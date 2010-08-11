# -*- coding: utf-8 -*-
from amsn2.ui import base
from amsn2.core.views import AccountView, ImageView

from PyQt4.QtCore import *
from PyQt4.QtGui import *
try:
    from ui_login import Ui_Login
except ImportError, e:
    print " WARNING: To use the QT4 you need to run the generateFiles.sh, check the README"
    raise e
from styledwidget import StyledWidget


class LoginThrobber(StyledWidget):
    def __init__(self, parent):
        StyledWidget.__init__(self, parent)
        # Throbber
        self.plsWait = QLabel(self)
        self.plsWait.setText("<strong>Please wait...</strong>")
        self.plsWait.setAlignment(Qt.AlignCenter)
        self.status = QLabel(self)
        self.status.setText("")
        self.status.setAlignment(Qt.AlignCenter)
        self.throbber = QLabel(self)
        self.movie = QMovie(self)
        self.movie.setFileName("amsn2/gui/front_ends/qt4/throbber.gif")
        self.movie.start()
        self.throbber.setMovie(self.movie)
        # Layout, for horizontal centering
        self.hLayout = QHBoxLayout()
        self.hLayout.addStretch()
        self.hLayout.addWidget(self.throbber)
        self.hLayout.addStretch()
        # Layout, for vertical centering
        self.vLayout = QVBoxLayout()
        self.vLayout.addStretch()
        self.vLayout.addLayout(self.hLayout)
        self.vLayout.addWidget(self.plsWait)
        self.vLayout.addWidget(self.status)
        self.vLayout.addStretch()
        # Top level layout
        self.setLayout(self.vLayout)
        # Apply StyleSheet
        self.setStyleSheet("background: white;")

class aMSNLoginWindow(StyledWidget, base.aMSNLoginWindow):
    def __init__(self, amsn_core, parent):
        StyledWidget.__init__(self, parent)
        self._amsn_core = amsn_core
        self._parent = parent
        self._skin = amsn_core._skin_manager.skin
        self._theme_manager = self._amsn_core._theme_manager
        self._ui_manager = self._amsn_core._ui_manager
        self.ui = Ui_Login()
        self.ui.setupUi(self)
        self._parent = parent
        self.loginThrobber = None
        QObject.connect(self.ui.pushSignIn, SIGNAL("clicked()"), self.__login_clicked)
        QObject.connect(self.ui.linePassword, SIGNAL("returnPressed()"), self.__login_clicked)
        QObject.connect(self.ui.styleDesktop, SIGNAL("clicked()"), self.setTestStyle)
        QObject.connect(self.ui.styleRounded, SIGNAL("clicked()"), self.setTestStyle)
        QObject.connect(self.ui.styleWLM, SIGNAL("clicked()"), self.setTestStyle)
        QObject.connect(self.ui.checkRememberMe, SIGNAL("toggled(bool)"), self.__on_toggled_cb)
        QObject.connect(self.ui.checkRememberPass, SIGNAL("toggled(bool)"), self.__on_toggled_cb)
        QObject.connect(self.ui.checkSignInAuto, SIGNAL("toggled(bool)"), self.__on_toggled_cb)
        QObject.connect(self.ui.comboAccount, SIGNAL("currentIndexChanged(QString)"), self.__on_user_comboxEntry_changed)
        self.setTestStyle()

        # status list
        for key in self._amsn_core.p2s:
            name = self._amsn_core.p2s[key]
            _, path = self._theme_manager.get_statusicon("buddy_%s" % name)
            if (name == self._amsn_core.p2s['FLN']): continue
            self.ui.comboStatus.addItem(QIcon(path), str.capitalize(name), key)

    def __on_user_comboxEntry_changed(self, text):
        self.__switch_to_account(text)

    def setTestStyle(self):
        styleData = QFile()
        if self.ui.styleDesktop.isChecked() == True:
            styleData.setFileName("amsn2/ui/front_ends/qt4/style0.qss")
        elif self.ui.styleWLM.isChecked() == True:
            styleData.setFileName("amsn2/ui/front_ends/qt4/style1.qss")
        elif self.ui.styleRounded.isChecked() == True:
            styleData.setFileName("amsn2/ui/front_ends/qt4/style2.qss")
        if styleData.open(QIODevice.ReadOnly|QIODevice.Text):
            styleReader = QTextStream(styleData)
            self.setStyleSheet(styleReader.readAll())

    def show(self):
        if not self.loginThrobber:
            self._parent.fadeIn(self)

    def hide(self):
        pass

    def set_accounts(self, accountviews):
        self._account_views = accountviews

        for accv in self._account_views:
            self.ui.comboAccount.addItem(accv.email)

        if len(accountviews)>0 :
            # first in the list, default
            self.__switch_to_account(self._account_views[0].email)

            if self._account_views[0].autologin:
                self.signin()


    def __switch_to_account(self, email):

        accv = self._ui_manager.get_accountview_from_email(email)

        if accv is None:
            accv = AccountView(self._amsn_core, email)

        self.ui.comboAccount.setEditText(accv.email)

        if accv.password:
            self.ui.linePassword.clear()
            self.ui.linePassword.insert(accv.password)

        self.ui.checkRememberMe.setChecked(accv.save)
        self.ui.checkRememberPass.setChecked(accv.save_password)
        self.ui.checkSignInAuto.setChecked(accv.autologin)

    def __login_clicked(self):
        email = str(self.ui.comboAccount.currentText())
        accv = self._ui_manager.get_accountview_from_email(email)

        if accv is None:
            accv = AccountView(self._amsn_core, str(email))

        accv.password = self.ui.linePassword.text().toLatin1().data()
        accv.presence = str(self.ui.comboStatus.itemData(self.ui.comboStatus.currentIndex()).toString())

        accv.save = self.ui.checkRememberMe.isChecked()
        accv.save_password = self.ui.checkRememberPass.isChecked()
        accv.autologin = self.ui.checkSignInAuto.isChecked()
        print accv
        self._amsn_core.signin_to_account(self, accv)

    def signout(self):
        pass

    def signing_in(self):
        self.loginThrobber = LoginThrobber(self)
        self._parent.fadeIn(self.loginThrobber)

    def on_connecting(self, progress, message):
        self.loginThrobber.status.setText(str(message))

    def __on_toggled_cb(self, bool):
        email = str(self.ui.comboAccount.currentText())
        accv = self._ui_manager.get_accountview_from_email(email)

        if accv is None:
            accv = AccountView(self._amsn_core, email)

        sender = self.sender()
        #just like wlm :)
        if sender == self.ui.checkRememberMe:
            accv.save = bool
            if not bool:
                self.ui.checkRememberPass.setChecked(False)
                self.ui.checkSignInAuto.setChecked(False)
        elif sender == self.ui.checkRememberPass:
            accv.save_password = bool
            if bool:
                self.ui.checkRememberMe.setChecked(True)
            else:
                self.ui.checkSignInAuto.setChecked(False)
        elif sender == self.ui.checkSignInAuto:
            accv.autologin = bool
            if bool:
                self.ui.checkRememberMe.setChecked(True)
                self.ui.checkRememberPass.setChecked(True)

