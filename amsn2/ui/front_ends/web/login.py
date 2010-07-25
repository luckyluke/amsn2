from papyon import Presence
from amsn2.ui import base

class aMSNLoginWindow(base.aMSNLoginWindow):
    def __init__(self, core, main):
        self._main = main
        self._core = core
        self._account_views = []

    def __del__(self):
        self._main.login_window = None

    def show(self):
        self._main.login_window = self

    def hide(self):
        self._main.login_window = None

    def set_accounts(self, accountviews):
        self._account_views = accountviews

    def signin(self, u, p, *args, **kwargs):
        accv = self._core._ui_manager.get_accountview_from_email(u)
        accv.password = p

        accv.presence = Presence.ONLINE

        accv.save = False
        accv.save_password = False
        accv.autologin = False

        self._core.signin_to_account(self, accv)

    def signing_in(self):
        self._main.send("signingIn")

    def on_connecting(self, progress, msg):
        self._main.send("onConnecting", msg)
