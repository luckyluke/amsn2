
from amsn2.ui import base
from bend import Backend
import os

class aMSNMainWindow(base.aMSNMainWindow, Backend):
    def __init__(self, amsn_core):
        Backend.__init__(self, amsn_core)
        self._amsn_core = amsn_core

    def show(self):
        self.send("showMainWindow")
        self._amsn_core.idler_add(self.__on_show)

    def hide(self):
        self.send("hideMainWindow")

    def set_title(self,title):
        self.send("setMainWindowTitle", title)

    def set_menu(self,menu):
        print "aMSNMainWindow.setMenu"

    def __on_show(self):
        self._amsn_core.main_window_shown()
