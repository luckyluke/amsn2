import hashlib
import random
from amsn2.core.views import ContactView, StringView
from amsn2.ui import base

class aMSNChatWindow(base.aMSNChatWindow):
    """ This interface will represent a chat window of the UI
        It can have many aMSNChatWidgets"""
    def __init__(self, amsn_core):
        self._amsn_core = amsn_core
        self._uid = hashlib.md5(str(random.random())).hexdigest()
        self._main = amsn_core._core._main
        self._main.chat_windows[self._uid] = self
        self._main.send("newChatWindow", self._uid)
        self._chat_widgets = {}

    def __del__(self):
        self._main.chat_windows[self._uid] = None

    def add_chat_widget(self, chat_widget):
        """ add an aMSNChatWidget to the window """
        self._main.send("addChatWidget", self._uid, chat_widget._uid)
        self._chat_widgets[chat_widget._uid] = chat_widget

    def show(self):
        self._main.send("showChatWindow", self._uid)

    def hide(self):
        self._main.send("hideChatWindow", self._uid)

    def add(self):
        print "aMSNChatWindow.add"
        pass

    def move(self):
        print "aMSNChatWindow.move"
        pass

    def remove(self):
        print "aMSNChatWindow.remove"
        pass

    def attach(self):
        print "aMSNChatWindow.attach"
        pass

    def detach(self):
        print "aMSNChatWindow.detach"
        pass

    def close(self):
        for (uid, cw) in self._chat_widgets.items():
            cw._conversation.leave()

    def flash(self):
        print "aMSNChatWindow.flash"
        pass
    """TODO: move, remove, detach, attach (shouldn't we use add ?), close,
        flash..."""


class aMSNChatWidget(base.aMSNChatWidget):
    """ This interface will present a chat widget of the UI """
    def __init__(self, amsn_conversation, parent, contacts_uid):
        """ create the chat widget for the 'parent' window, but don't attach to
        it."""
        self._main = parent._main
        self._uid = hashlib.md5(str(random.random())).hexdigest()
        self._main.chat_widgets[self._uid] = self
        self._main.send("newChatWidget", self._uid)
        self._conversation = amsn_conversation

    def __del__(self):
        self._main.chat_widgets[self._uid] = None

    def send_message(self, uid, msg):
        if uid == self._uid:
            stmess = StringView()
            stmess.append_text('\n'.join(msg))
            self._conversation.send_message(stmess)
        return True



    def on_message_received(self, messageview, formatting):
        """ Called for incoming and outgoing messages
            message: a MessageView of the message"""
        self._main.send("onMessageReceivedChatWidget",
                        self._uid, unicode(messageview.to_stringview()))

    def nudge(self):
        self._main.send("nudgeChatWidget", self._uid)

    def on_user_typing(self, contact):
        pass
