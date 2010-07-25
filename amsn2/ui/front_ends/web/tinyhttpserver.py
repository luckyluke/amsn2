import os
import socket
import errno
import logging
import urlparse
import re
import gobject
from constants import READ_CHUNK_SIZE
import traceback

class TinyHTTPServer(object):
    def __init__(self, backend, socket, peer, rules):
        self._backend = backend
        self._socket = socket
        self._socket.setblocking(0)
        self._peer = peer

        self._rbuf = ""
        self._wbuf = ""
        self._read = 0
        self._written = 0

        self._read_delimiter = "\r\n\r\n"
        self._bytes_to_read = 0
        self._rcb = self.on_headers

        self._is_alive = True

        self._rules = rules

        self._in_id = gobject.io_add_watch(socket.fileno(),
                             gobject.IO_IN | gobject.IO_PRI,
                             self.on_read)
        self._out_id = gobject.io_add_watch(self._socket.fileno(),
                             gobject.IO_OUT,
                             self.on_write)
        self._err_id = gobject.io_add_watch(self._socket.fileno(),
                             gobject.IO_ERR,
                             self.on_error)
        self._hup_id = gobject.io_add_watch(self._socket.fileno(),
                             gobject.IO_HUP,
                             self.on_hang_up)


    def close(self):
        if self._is_alive:
            self._is_alive = False
            gobject.source_remove(self._in_id)
            gobject.source_remove(self._out_id)
            gobject.source_remove(self._err_id)
            gobject.source_remove(self._hup_id)
            self._socket.close()
            self._socket = None

    def write(self, data):
        if self._is_alive:
            self._wbuf += data
            self.on_write(self._socket, gobject.IO_IN)

    def on_headers(self, headers):
        eol = headers.find("\r\n")
        start_line = headers[:eol]
        self._method, uri, self._version = start_line.split(" ")
        self._headers = {}
        for line in headers[eol:].splitlines():
            if line:
                name, value = line.split(":", 1)
                self._headers[name] = value.strip()
        #print "method=%s, uri=%s, version=%s" % (self._method, uri, self._version)
        if not self._version.startswith("HTTP/"):
            self.close()
            return
        self._uri = (scheme, netloc, path, query, fragment) = urlparse.urlsplit(uri)
        if self._method == "GET":
            for (r, get_cb, _) in self._rules:
                if r.match(path) and get_cb:
                    try:
                        get_cb(self, self._uri, self._headers)
                    except Exception as e:
                        traceback.print_exc()
                        self._500()
                    finally:
                        return
            self._404()
        elif self._method == "POST":
            if "Content-Length" in self._headers:
                r = int(self._headers["Content-Length"])
                if r > 0:
                    self._read_delimiter = None
                    self._rcb = self.on_body
                    self._bytes_to_read = r
                else:
                    self._400()
            else:
                self._400()
        else:
            #TODO: head, put, delete, trace, options, connect, patch
            self._501()


    def on_body(self, body):
        if self._method == "POST":
            path = self._uri[2]
            for (r, _, post_cb) in self._rules:
                if r.match(path) and post_cb:
                    try:
                        post_cb(self, self._uri, self._headers, body)
                    except Exception as e:
                        traceback.print_exc()
                        self._500()
                    finally:
                        return
            self._404()
        else:
            self._501()

    def on_read(self, s, c):
        try:
            chunk = self._socket.recv(READ_CHUNK_SIZE)
        except socket.error, e:
            if e[0] in (errno.EWOULDBLOCK, errno.EAGAIN):
                return self._is_alive
            else:
                logging.warning("Read error on %d: %s",
                                self._socket.fileno(), e)
                self.close()
                return self._is_alive
        if not chunk:
            self.close()
            return self._is_alive

        self._rbuf += chunk
        self._read += len(chunk)
        if self._read >= 16777216:
            logging.error("Reached maximum read buffer size")
            self.close()
            return self._is_alive

        if self._read_delimiter:
            pos = self._rbuf.find(self._read_delimiter)
            if pos != -1:
                pos += len(self._read_delimiter)
                r = self._rbuf[:pos]
                self._rbuf = self._rbuf[pos:]
                self._rcb(r)
                self._read -= pos
        if self._bytes_to_read > 0 and self._read >= self._bytes_to_read:
            r = self._rbuf[:self._bytes_to_read]
            self._rbuf = self._rbuf[self._bytes_to_read:]
            self._rcb(r)
            self._read -= self._bytes_to_read
            self._bytes_to_read = 0
        return self._is_alive

    def on_write(self, s, c):
        while self._wbuf:
            try:
                b = self._socket.send(self._wbuf)
                self._wbuf = self._wbuf[b:]
            except socket.error, e:
                if e[0] in (errno.EWOULDBLOCK, errno.EAGAIN):
                    break
                else:
                    logging.warning("Write error on %d: %s",
                                    self._socket.fileno(), e)
                    self.close()
                    return self._is_alive
        return self._is_alive

    def on_error(self, s, c):
        self.close()
        return self._is_alive

    def on_hang_up(self, s, c):
        self.close()
        return self._is_alive

    def send_file(self, path):
        f = open(path, "r")
        r = f.read()
        f.close()
        self.write("HTTP/1.1 200 OK\r\nContent-Length: %d\r\n\r\n%s"
                   % (len(r), r))
        self.close()

    def _200(self, body = None):
        if body:
            self.write("HTTP/1.1 200 OK\r\nContent-Length: %d\r\n\r\n%s"
                       % (len(body), body))
        else:
            self.write("HTTP/1.1 200 OK\r\nContent-Length: 0\r\n\r\n")
        self.close()

    """
    400 Bad Request
    The request contains bad syntax or cannot be fulfilled
    """
    def _400(self, body = None):
        path = self._uri[2]
        self.write("HTTP/1.1 400\r\n\r\n")
        self.close()

    """
    404 Not Found
    The requested resource could not be found but may be available again in the future. Subsequent requests by the client are permissible.
    """
    def _404(self, body = None):
        path = self._uri[2]
        self.write("HTTP/1.1 404\r\n\r\n")
        self.close()

    """
    500 Internal Server Error
    A generic error message, given when no more specific message is suitable.
    """
    def _500(self, body = None):
        path = self._uri[2]
        self.write("HTTP/1.1 500\r\n\r\n")
        self.close()

    """
    501 Not Implemented
    The server either does not recognise the request method, or it lacks the ability to fulfill the request.
    """
    def _501(self, body = None):
        path = self._uri[2]
        self.write("HTTP/1.1 501\r\n\r\n")
        self.close()

