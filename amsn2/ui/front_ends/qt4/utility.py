
from amsn2.ui import base
from amsn2.core import views
from PyQt4.QtCore import *
from PyQt4.QtGui import *

class aMSNErrorWindow(base.aMSNErrorWindow, QMessageBox):
    def __init__(self, error_text, parent = None):
        QMessageBox.__init__(self, QMessageBox.Critical, "aMSN Error", error_text, QMessageBox.Ok, parent)
        self.exec_()


class aMSNNotificationWindow(base.aMSNNotificationWindow, QMessageBox):
    def __init__(self, notification_text, parent = None):
        QMessageBox.__init__(self, QMessageBox.Information, "aMSN Notification", notification_text, QMessageBox.Ok, parent)
        self.exec_()


class aMSNDialogWindow(base.aMSNDialogWindow, QMessageBox):
    def __init__(self, message, actions, parent = None):
        QMessageBox.__init__(self, QMessageBox.Information, "aMSN Dialog", message, QMessageBox.NoButton, parent)

        for action in actions:
            name, callback = action
            button = QPushButton(name)
            QObject.connect(button, SIGNAL("clicked()"), callback)
            self.addButton(button, QMessageBox.AcceptRole)
        self.exec_()


class aMSNContactInputWindow(base.aMSNContactInputWindow, QDialog):
    def __init__(self, message, callback, groups, parent = None):
        QDialog.__init__(self, parent)
        self.setWindowTitle("aMSN Contact Input")
        self._callback = callback
        self.adress = self # Workaround to make the window not disapear as it is poped

        self.vboxlayout = QVBoxLayout()
        label = QLabel(message[0])
        self.vboxlayout.addWidget(label)
        self._name = QLineEdit()
        self.vboxlayout.addWidget(self._name)

        # TODO: build list of existing groups
        label2 = QLabel(message[1])
        self.vboxlayout.addWidget(label2)
        self._message = QLineEdit()
        self.vboxlayout.addWidget(self._message)

        self.buttonbox = QDialogButtonBox()
        self.buttonOk = QPushButton("Ok", self)
        QObject.connect(self.buttonOk, SIGNAL("clicked()"), self.onOk)
        self.buttonbox.addButton(self.buttonOk,QDialogButtonBox.ActionRole)
        self.buttonCancel = QPushButton("Cancel", self)
        QObject.connect(self.buttonCancel, SIGNAL("clicked()"), self.onCancel)
        self.buttonbox.addButton(self.buttonCancel,QDialogButtonBox.ActionRole)
        self.vboxlayout.addWidget(self.buttonbox)

        self.setLayout(self.vboxlayout)

        self.show()

    def onOk(self):
        name = str(self._name.text())
        msg = str(self._message.text())
        self._callback(name, msg)
        self.done(0)
        self.deleteLater()

    def onCancel(self):
        self.done(0)
        self.deleteLater()


class aMSNGroupInputWindow(base.aMSNGroupInputWindow, QDialog): 
    def __init__(self, message, callback, contacts, parent = None):
        QDialog.__init__(self, parent)
        self.setWindowTitle("aMSN Group Input")
        self._callback = callback
        self.adress = self # Workaround to make the window not disapear as it is poped

        self.vboxlayout = QVBoxLayout()
        label = QLabel(message[0])
        self.vboxlayout.addWidget(label)
        self._name = QLineEdit()
        self.vboxlayout.addWidget(self._name)

        # TODO: build list of existing contacts
        label2 = QLabel(message[1]) # Done like the GTK implementation but i really don't get what these second label and lineEdit are for ...
        self.vboxlayout.addWidget(label2)
        self._message = QLineEdit()
        self.vboxlayout.addWidget(self._message)

        self.buttonbox = QDialogButtonBox()
        self.buttonOk = QPushButton(self, "Ok")
        QObject.connect(buttonOk, SIGNAL("clicked()"), self.onOk)
        self.buttonbox.addButton(self.buttonOk)
        self.buttonCancel = QPushButton(self, "Cancel")
        QObject.connect(buttonCancel, SIGNAL("clicked()"), self.onCancel)
        self.buttonbox.addButton(self.buttonCancel)
        self.vboxlayout.addWidget(self.buttonbox)

        self.addLayout(vboxlayout)

        self.show()

    def onOk(self):
        name = str(self._name.text())
        self._callback(name)
        self.done(0)
        self.deleteLater()

    def onCancel(self):
        self.done(0)
        self.deleteLater()

class aMSNContactDeleteWindow(base.aMSNContactDeleteWindow, QInputDialog): 
    def __init__(self, message, callback, contacts, parent = None):
        QInputDialog.__init__(self, parent)
        self._callback = callback
        self.adress = self # Workaround to make the window not disapear as it is poped
        self.setWindowTitle("aMSN Contact Input")
        self.setInputMode(QInputDialog.TextInput)
        self.setLabelText(message)
        QObject.connect(self, SIGNAL("accepted()"), self.onOk)
        QObject.connect(self, SIGNAL("rejected()"), self.onCancel)

        self.show()

    def onOk(self):
        self._callback(str(self.textValue()))
        self.done(-1)
        self.deleteLater()

    def onCancel(self):
        self.done(-1)
        self.deleteLater()

class aMSNGroupDeleteWindow(base.aMSNGroupDeleteWindow, QInputDialog): 
    def __init__(self, message, callback, contacts, parent = None):
        QInputDialog.__init__(self, parent)
        self._callback = callback
        self.adress = self # Workaround to make the window not disapear as it is poped
        self.setWindowTitle("aMSN Group Input")
        self.setInputMode(QInputDialog.TextInput)
        self.setLabelText(message)
        QObject.connect(self, SIGNAL("accepted()"), self.onOk)
        QObject.connect(self, SIGNAL("rejected()"), self.onCancel)

        self.show()

    def onOk(self):
        self._callback(str(self.textValue()))
        self.done(-1)
        self.deleteLater()

    def onCancel(self):
        self.done(-1)  
        self.deleteLater()