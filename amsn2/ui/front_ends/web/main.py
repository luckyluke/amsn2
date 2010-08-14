
from amsn2.ui import base
from bend import Backend

import optparse
import os

class aMSNMainWindow(base.aMSNMainWindow, Backend):
    def __init__(self, core):
        self._core = core
        parser = optparse.OptionParser(
            usage="usage: %prog [global_options] -f web [-- options]")
        parser.add_option("-H", "--host", dest="host",
                          default="127.0.0.1", help="The address to listen on")
        parser.add_option("-P", "--port", dest="port",
                          default=8080, help="The port to listen on")
        (self._options, self._args) = parser.parse_args(self._core.extra_args)
        Backend.__init__(self, core)

    def show(self):
        self.send("showMainWindow")

    def hide(self):
        self.send("hideMainWindow")

    def set_title(self, title):
        self.send("setMainWindowTitle", title)

    def set_menu(self,menu):
        print "TODO: aMSNMainWindow.setMenu"
