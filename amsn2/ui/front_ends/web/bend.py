import os
import socket
import errno
import logging
import urlparse
import re
import gobject
import cgi

from constants import BASEPATH
from tinyhttpserver import TinyHTTPServer

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
        self._socket.setblocking(0)
        self._socket.bind(("127.0.0.1", 8080))
        self._socket.listen(1)
        self._workers = []
        self._rules = (
            (re.compile('/$'), self.get_index, None),
            (re.compile('/static/(.*)'), self.get_static_file, None),
            (re.compile('/out$'), self.out, self.out),
            (re.compile('/signin'), None, self.post_signin),
            (re.compile('/contactClicked'), None, self.post_contact_clicked),
            (re.compile('/sendMsg'), None, self.post_send_msg),
        )

        gobject.io_add_watch(self._socket, gobject.IO_IN, self.on_accept)
        self._q = ""

    def on_accept(self, s, c):
        w = s.accept()
        t = TinyHTTPServer(self, *w, rules = self._rules)
        self._workers.append(t)
        return True

    def emit_event(self, event, *args, **kwargs):
        """
        if event in self.listeners.keys():
            for func in self.listeners[event]:
                try:
                    func(*args, **kwargs)
                except:
                    pass
        """

    def out(self, w, uri, headers, body = None):
        if len(self._q):
            print ">>> %s" % (self._q,)
        w._200(self._q)
        self._q = ""

    def _args2JS(self, *args):
        call = ""
        for value in args:
            t = type(value).__name__
            if (t == 'tuple' or t == 'list'):
                call += '['+ self._args2JS(*value)+']'
            elif (t == 'str'):
                call += "'" + str(value).encode('string_escape') + "',"
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
        w.send_file(BASEPATH + "/static/amsn2.html")

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
        if (body and 'Content-Type' in headers
        and headers['Content-Type'].startswith('application/x-www-form-urlencoded')):
            args = cgi.parse_qs(body)
            print "<<< %s" %(args,)
            self.login_window.signin(args['username'][0], args['password'][0])
            w.write("HTTP/1.1 200 OK\r\n\r\n")
            w.close()
            return
        w._400()

    def post_contact_clicked(self, w, uri, headers, body = None):
        print "Contact Clicked"
        if (body and 'Content-Type' in headers
        and headers['Content-Type'].startswith('application/x-www-form-urlencoded')):
            args = cgi.parse_qs(body)
            print "<<< %s" %(args,)
            w.write("HTTP/1.1 200 OK\r\n\r\n")
            w.close()
            return
        w._400()

    def post_send_msg(self, w, uri, headers, body = None):
        print "Send Msg"
        if (body and 'Content-Type' in headers
        and headers['Content-Type'].startswith('application/x-www-form-urlencoded')):
            args = cgi.parse_qs(body)
            print "<<< %s" %(args,)
            w.write("HTTP/1.1 200 OK\r\n\r\n")
            w.close()
            return
        w._400()
