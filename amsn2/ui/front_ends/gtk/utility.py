
from amsn2.ui import base
from amsn2.core import views

import gtk
import logging
import pango

logger = logging.getLogger('amsn2.gtk.utility')

class aMSNErrorWindow(base.aMSNErrorWindow, gtk.Dialog):
    def __init__(self, error_text):
        gtk.Dialog.__init__(self, None, None, gtk.DIALOG_NO_SEPARATOR,
                            (gtk.STOCK_OK, gtk.RESPONSE_ACCEPT))
        label = gtk.Label(error_text)
        self.get_content_area().set_spacing(5)
        self.get_content_area().pack_start(label)
        label.show()
        self.connect("response", self.on_response)
        self.show()

    def on_response(self, dialog, id):
        self.destroy()

    def show(self):
        self.show_all()

    def set_title(self, title):
        gtk.Dialog.set_title(self, title)

class aMSNNotificationWindow(base.aMSNNotificationWindow, gtk.Dialog):
    def __init__(self, notification_text):
        gtk.Dialog.__init__(self, None, None, gtk.DIALOG_NO_SEPARATOR,
                            (gtk.STOCK_OK, gtk.RESPONSE_ACCEPT))
        label = gtk.Label(notification_text)
        self.get_content_area().set_spacing(5)
        self.get_content_area().pack_start(label)
        label.show()
        self.connect("response", self.on_response)
        self.show()

    def on_response(self, dialog, id):
        self.destroy()

    def show(self):
        self.show_all()

    def set_title(self, title):
        gtk.Dialog.set_title(self, title)

class aMSNDialogWindow(base.aMSNDialogWindow, gtk.Dialog):
    def __init__(self, message, actions):
        gtk.Dialog.__init__(self, None, None, gtk.DIALOG_NO_SEPARATOR, None)

        label = gtk.Label(message)
        ca = self.get_content_area()
        ca.pack_start(label)

        id = -1
        self._cbs = {}
        for act in actions:
            name, cb = act
            self.add_button(name, id)
            self._cbs[id] = cb
            id = id - 1

        self.connect("response", self.on_response)
        label.show()
        self.show()

    def on_response(self, dialog, id):
        try:
            self._cbs[id]()
        except KeyError:
            logger.warning("Unknown dialog choice, id %s" % id)
        self.destroy()

    def show(self):
        self.show_all()

    def set_title(self, title):
        gtk.Dialog.set_title(self, title)

class aMSNContactInputWindow(base.aMSNContactInputWindow, gtk.Dialog):
    def __init__(self, message, callback, groups):
        gtk.Dialog.__init__(self, None, None, gtk.DIALOG_NO_SEPARATOR,
                            (gtk.STOCK_OK, gtk.RESPONSE_ACCEPT,
                             gtk.STOCK_CANCEL, gtk.RESPONSE_REJECT))
        self._callback = callback

        label = gtk.Label(message[0])
        self._name = gtk.Entry()
        label2 = gtk.Label(message[1])
        self._message = gtk.Entry()

        gstore = gtk.ListStore(str, object, bool)
        gstore.connect("row-changed", self._row_selected)
        for gw in groups:
            if gw.uid != 0:
                gstore.append([gw.name, gw, None])

        name = gtk.CellRendererText()
        name.set_property('ellipsize-set',True)
        name.set_property('ellipsize', pango.ELLIPSIZE_END)
        toggle = gtk.CellRendererToggle()
        toggle.set_property('activatable', True)
        toggle.connect('toggled', self._toggled, gstore)
        column = gtk.TreeViewColumn()
        column.set_expand(True)
        column.pack_start(name, True)
        column.add_attribute(name, "text", 0)
        column.pack_end(toggle, False)
        column.add_attribute(toggle, "active", 2)
        self.g_treeview = gtk.TreeView(model=gstore)
        self.g_treeview.set_headers_visible(False)
        self.g_treeview.append_column(column)

        scrollwindow = gtk.ScrolledWindow()
        scrollwindow.set_shadow_type(gtk.SHADOW_ETCHED_IN)
        scrollwindow.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)	
        scrollwindow.add(self.g_treeview)

        ca = self.get_content_area()
        ca.set_spacing(5)
        inputbox = gtk.VBox()
        cbox = gtk.HBox()
        msgbox = gtk.HBox()
        cbox.pack_start(label, False)
        cbox.pack_start(self._name, True)
        msgbox.pack_start(label2, False)
        msgbox.pack_start(self._message, True)
        inputbox.pack_start(cbox, False)
        inputbox.pack_start(msgbox, False)
        ca.pack_start(inputbox, False)
        ca.pack_start(scrollwindow, True)

        self.connect("response", self.on_response)

    def _row_selected(self, dialog, row, boh):
        pass

    def _toggled(self, cell, path, model):
        model[path][2] = not model[path][2]

    def on_response(self, dialog, id):
        if id == gtk.RESPONSE_ACCEPT:
            name = self._name.get_text()
            msg = self._message.get_text()
            groups = [g[1].uid for g in self.g_treeview.get_model() if g[2]]
            self._callback(name, msg, groups)
        elif id == gtk.RESPONSE_REJECT:
            pass
        self.destroy()

    def show(self):
        self.show_all()

    def set_title(self, title):
        gtk.Dialog.set_title(self, title)

class aMSNGroupInputWindow(base.aMSNGroupInputWindow, gtk.Dialog): 
    def __init__(self, message, callback, contacts):
        gtk.Dialog.__init__(self, None, None, gtk.DIALOG_NO_SEPARATOR,
                            (gtk.STOCK_OK, gtk.RESPONSE_ACCEPT,
                             gtk.STOCK_CANCEL, gtk.RESPONSE_REJECT))
        self._callback = callback
        self.set_default_size(250, 300)

        label = gtk.Label(message[0])
        #label1 = gtk.Label(message[1])
        self._name = gtk.Entry()

        cstore = gtk.ListStore(str, object, bool)
        cstore.connect("row-changed", self._row_selected)
        for cw in contacts:
            cstore.append([cw.name, cw, None])

        name = gtk.CellRendererText()
        name.set_property('ellipsize-set',True)
        name.set_property('ellipsize', pango.ELLIPSIZE_END)
        toggle = gtk.CellRendererToggle()
        toggle.set_property('activatable', True)
        toggle.connect('toggled', self._toggled, cstore)
        column = gtk.TreeViewColumn()
        column.set_expand(True)
        column.pack_start(name, True)
        column.add_attribute(name, "text", 0)
        column.pack_end(toggle, False)
        column.add_attribute(toggle, "active", 2)
        self.c_treeview = gtk.TreeView(model=cstore)
        self.c_treeview.set_headers_visible(False)
        self.c_treeview.append_column(column)

        scrollwindow = gtk.ScrolledWindow()
        scrollwindow.set_shadow_type(gtk.SHADOW_ETCHED_IN)
        scrollwindow.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)	
        scrollwindow.add(self.c_treeview)

        ca = self.get_content_area()
        ca.set_spacing(5)
        namebox = gtk.HBox()
        namebox.pack_start(label, False)
        namebox.pack_start(self._name, True)
        ca.pack_start(namebox, False)
        #ca.pack_start(label1, False)
        ca.pack_start(scrollwindow, True)

        self.connect("response", self.on_response)

    def _row_selected(self, dialog, row, boh):
        pass

    def _toggled(self, cell, path, model):
        model[path][2] = not model[path][2]

    def on_response(self, dialog, id):
        if id == gtk.RESPONSE_ACCEPT:
            name = self._name.get_text()
            contacts = [c[1].account for c in self.c_treeview.get_model() if c[2]]
            self._callback(name, contacts)
        elif id == gtk.RESPONSE_REJECT:
            pass
        self.destroy()

    def show(self):
        self.show_all()

    def set_title(self, title):
        gtk.Dialog.set_title(self, title)

class aMSNContactDeleteWindow(base.aMSNContactDeleteWindow, gtk.Dialog): 
    def __init__(self, message, callback, contacts):
        gtk.Dialog.__init__(self, None, None, gtk.DIALOG_NO_SEPARATOR,
                            (gtk.STOCK_OK, gtk.RESPONSE_ACCEPT,
                             gtk.STOCK_CANCEL, gtk.RESPONSE_REJECT))
        self._callback = callback

        label = gtk.Label(message[0])
        self._name = gtk.Entry()
        ca = self.get_content_area()
        ca.set_spacing(5)
        ca.pack_start(label)
        ca.pack_start(self._name)

        self.connect("response", self.on_response)
        label.show()
        self._name.show()
        self.show()

    def on_response(self, dialog, id):
        if id == gtk.RESPONSE_ACCEPT:
            name = self._name.get_text()
            self._callback(name)
        elif id == gtk.RESPONSE_REJECT:
            pass
        self.destroy()

    def show(self):
        self.show_all()

    def set_title(self, title):
        gtk.Dialog.set_title(self, title)

class aMSNGroupDeleteWindow(base.aMSNGroupDeleteWindow, gtk.Dialog): 
    def __init__(self, message, callback, groups):
        gtk.Dialog.__init__(self, None, None, gtk.DIALOG_NO_SEPARATOR,
                            (gtk.STOCK_OK, gtk.RESPONSE_ACCEPT,
                             gtk.STOCK_CANCEL, gtk.RESPONSE_REJECT))
        self._callback = callback

        label = gtk.Label(message[0])
        self._name = gtk.Entry()
        ca = self.get_content_area()
        ca.set_spacing(5)
        ca.pack_start(label)
        ca.pack_start(self._name)

        self.connect("response", self.on_response)
        label.show()
        self._name.show()
        self.show()

    def on_response(self, dialog, id):
        if id == gtk.RESPONSE_ACCEPT:
            name = self._name.get_text()
            self._callback(name)
        elif id == gtk.RESPONSE_REJECT:
            pass
        self.destroy()

    def show(self):
        self.show_all()

    def set_title(self, title):
        gtk.Dialog.set_title(self, title)

