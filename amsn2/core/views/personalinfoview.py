from stringview import *
from imageview import *

class PersonalInfoView(object):
    def __init__(self, personalinfo_manager):
        self._personalinfo_manager = personalinfo_manager

        self._nickname = StringView()
        self._psm = StringView()
        self._current_media  = StringView()
        self._image = ImageView()
        self._presence = 'offline'

        # TODO: get more info, how to manage webcams and mail
        self._webcam = None
        self._mail_unread = None

    def changeDP(self):
        self._personalinfo_manager._on_DP_change_request()

    def get_nick(self):
        return self._nickname
    def set_nick(self, nick):
        self._personalinfo_manager._on_nick_changed(nick)
    nick = property(get_nick, set_nick)

    def get_psm(self):
        return self._psm
    def set_psm(self, psm):
        self._personalinfo_manager._on_PSM_changed(psm)
    psm = property(get_psm, set_psm)

    def get_dp(self):
        return self._image
    def set_dp(self, dp_msnobj):
        self._personalinfo_manager._on_DP_changed(dp_msnobj)
    dp = property(get_dp, set_dp)

    def get_current_media(self):
        return self._current_media
    def set_current_media(self, artist, song):
        self._personalinfo_manager._on_CM_changed((artist, song))
    current_media = property(get_current_media, set_current_media)

    def get_presence(self):
        return self._presence
    def set_presence(self, presence):
        self._personalinfo_manager._on_presence_changed(presence)
    presence = property(get_presence, set_presence)

