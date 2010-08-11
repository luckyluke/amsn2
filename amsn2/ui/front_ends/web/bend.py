import os
import socket
import errno
import logging
import re
import gobject
import sys

if sys.hexversion < 0x020600f0:
    from cgi import parse_qs
else:
    from urlparse import parse_qs

from constants import BASEPATH
from tinyhttpserver import TinyHTTPServer
from time import time

def uri_path_is_safe(path):
    if not BASEPATH and path[0] == '/':
        return False
    elif path[0:1] == '..':
        return False

    l = path.split('/')
    b = [d for d in l if d == '..']

    if len(b) >= len(l):
        return False

    return True


class Backend(object):
    """
    This is the main comunication module,
    all comunication to the JS frontend will be issued from here
    """
    def __init__(self, core):
        self._core = core
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._socket.setblocking(False)
        self._socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self._socket.bind((self._options.host, self._options.port))
        self._socket.listen(1)
        #self._workers = []
        self._rules = (
            (re.compile('/$'), self.get_index, None),
            (re.compile('/static/(.*)'), self.get_static_file, None),
            (re.compile('/out$'), self.out, self.out),
            (re.compile('/signin$'), None, self.post_signin),
            (re.compile('/contactClicked$'), None, self.post_contact_clicked),
            (re.compile('/sendMsg$'), None, self.post_send_msg),
            (re.compile('/closeCW$'), None, self.post_close_cw),
            (re.compile('/logout$'), None, self.post_logout),
            #TODO: set (nick,psm,status,dp), get (dp, dps),
            # add/remove group/contact
        )

        gobject.io_add_watch(self._socket, gobject.IO_IN, self.on_accept)
        self._q = ""

        self.login_window = None
        self.cl_window = None
        self.chat_windows = {}
        self.chat_widgets = {}

        self._logged_in = False
        self._last_poll = 0

        #TODO: on log out
        def cb():
            if self._logged_in:
                if time() - self._last_poll >= 30:
                    self._core.sign_out_of_account()
                    self._logged_in = False
            return True
        self._core._loop.timer_add(30000, cb)

    def on_accept(self, s, c):
        w = s.accept()
        t = TinyHTTPServer(self, *w, rules = self._rules)
        #self._workers.append(t)
        return True

    def out(self, w, uri, headers, body = None):
        if self._logged_in:
            if len(self._q):
                print ">>> %s" % (self._q,)
            self._last_poll = time()
            w.send_javascript(self._q)
            self._q = ""
        else:
            w.send_javascript("loggedOut();")

    def _args2JS(self, *args):
        call = ""
        for value in args:
            t = type(value).__name__
            if (t == 'tuple' or t == 'list'):
                call += '['+ self._args2JS(*value)+']'
            elif (t == 'unicode'):
                call += "'" + value.encode('unicode_escape') + "',"
            elif (t == 'str'):
                call += "'" + value.encode('string_escape') + "',"
            elif (t == 'int'):
                call += str(value) + ","
            else:
                print t
                call += "'" + str(value).encode('string_escape') + "',"
        return call.rstrip(",")


    def send(self, event, *args):
        # The backend sent a message to the JS client
        # select the JS function to call depending on the type of event
        if args:
            self._q += event + '(' + self._args2JS(*args) + ');'
        else:
            self._q += event + '();'

    def get_index(self, w, uri, headers, body = None):
        self._core.main_window_shown()
        w.send_file(BASEPATH + "/static/amsn2.html", {'Content-Type':
                                                      'text/html; charset=utf-8'})

    def get_static_file(self, w, uri, headers, body = None):
        path = uri[2]
        if uri_path_is_safe(path):
            w.send_file(BASEPATH + path)
        else:
            w._404()


    def post_signin(self, w, uri, headers, body = None):
        if self.login_window is None:
            w._400()
            return
        if (body and 'content-type' in headers
        and headers['content-type'].startswith('application/x-www-form-urlencoded')):
            args = parse_qs(body)
            print "<<< signin: %s" %(args,)
            self.login_window.signin(args['username'][0], args['password'][0])
            self._logged_in = True
            self._last_poll = time()
            w.write("HTTP/1.1 200 OK\r\n\r\n")
            w.close()
            return
        w._400()

    def post_contact_clicked(self, w, uri, headers, body = None):
        if self.cl_window is None:
            w._400()
            return
        if (body and 'content-type' in headers
        and headers['content-type'].startswith('application/x-www-form-urlencoded')):
            args = parse_qs(body)
            print "<<< contactClicked: %s" %(args,)
            self.cl_window.get_contactlist_widget().contact_clicked(args['uid'][0])
            w.write("HTTP/1.1 200 OK\r\n\r\n")
            w.close()
            return
        w._400()

    def post_send_msg(self, w, uri, headers, body = None):
        if (body and 'content-type' in headers
        and headers['content-type'].startswith('application/x-www-form-urlencoded')):
            args = parse_qs(body)
            print "<<< sendMsg: %s" %(args,)
            uid = args['uid'][0]
            if uid not in self.chat_widgets:
                w._400()
                return
            cw = self.chat_widgets[uid]
            cw.send_message(uid, args['msg'])
            w.write("HTTP/1.1 200 OK\r\n\r\n")
            w.close()
            return
        w._400()

    def post_close_cw(self, w, uri, headers, body = None):
        if (body and 'content-type' in headers
        and headers['content-type'].startswith('application/x-www-form-urlencoded')):
            args = parse_qs(body)
            print "<<< closeCW: %s" %(args,)
            uid = args['uid'][0]
            if uid not in self.chat_windows:
                w._400()
                return
            cw = self.chat_windows[uid]
            cw.close()
            w.write("HTTP/1.1 200 OK\r\n\r\n")
            w.close()
            return
        w._400()

    def post_logout(self, w, uri, headers, body = None):
        if self._core._account:
            self._core.sign_out_of_account()
            w.write("HTTP/1.1 200 OK\r\n\r\n")
            w.close()
            return
        w._400()
