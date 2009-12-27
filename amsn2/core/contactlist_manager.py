from views import *
import os
import tempfile
import papyon


class aMSNContactListManager:
    def __init__(self, core):
        """
        @type core: aMSNCore
        """

        self._core = core
        self._em = core._event_manager
        self._contacts = {} #Dictionary where every contact_uid has an associated aMSNContact
        self._groups = {}
        self._papyon_addressbook = None

    #TODO: sorting contacts & groups

    ''' normal changes of a contact '''

    def onContactChanged(self, papyon_contact):
        """ Called when a contact changes either its presence, nick, psm or current media."""

        #1st/ update the aMSNContact object
        c = self.getContact(papyon_contact.id, papyon_contact)
        c.fill(papyon_contact)
        #2nd/ update the ContactView
        cv = ContactView(self._core, c)
        self._em.emit(self._em.events.CONTACTVIEW_UPDATED, cv)

        #TODO: update the group view
        groups = self.getGroups(c.uid)
        for g in groups:
            g.fill()
            self.onAmsnGroupChanged(g)

    def onGroupChanged(self, papyon_group):
        g = self.getGroup(papyon_group.id)
        g.fill(papyon_group)
        self.onAmsnGroupChanged(g)

    def onAmsnGroupChanged(self, amsn_group):
        gv = GroupView(self._core, amsn_group)
        self._em.emit(self._em.events.GROUPVIEW_UPDATED, gv)

    def onContactDPChanged(self, papyon_contact):
        """ Called when a contact changes its Display Picture. """

        #Request the DP...
        c = self.getContact(papyon_contact.id, papyon_contact)
        if ("Theme", "dp_nopic") in c.dp.imgs:
            c.dp.load("Theme", "dp_loading")
        elif papyon_contact.msn_object is None:
            c.dp.load("Theme", "dp_nopic")
            self._em.emit(self._em.events.AMSNCONTACT_UPDATED, c)
            cv = ContactView(self._core, c)
            self._em.emit(self._em.events.CONTACTVIEW_UPDATED, cv)
            return

        if (papyon_contact.presence is not papyon.Presence.OFFLINE and
            papyon_contact.msn_object):
            self._core._account.client.msn_object_store.request(papyon_contact.msn_object,
                                                                (self.onDPdownloaded,
                                                                 papyon_contact.id))

    def onDPdownloaded(self, msn_object, uid):
        #1st/ update the aMSNContact object
        try:
            c = self.getContact(uid)
        except ValueError:
            return
        fn = self._core._backend_manager.getFileLocationDP(c.account, uid,
                                                           msn_object._data_sha)
        try:
            f = open(fn, 'w+b', 0700)
            try:
                f.write(msn_object._data.read())
            finally:
                f.close()
        except IOError:
            return
        c.dp.load("Filename", fn)
        self._em.emit(self._em.events.AMSNCONTACT_UPDATED, c)
        #2nd/ update the ContactView
        cv = ContactView(self._core, c)
        self._em.emit(self._em.events.CONTACTVIEW_UPDATED, cv)

    ''' changes to the address book '''

    def addContact(self):
        def cb(email, invite_msg):
            if email:
                self._papyon_addressbook.add_messenger_contact(email, self._core._account.view.email,
                                                               invite_msg)
        self._core._ui_manager.loadContactInputWindow(cb)

    def removeContact(self):
        def contactCB(account):
            if account:
                try:
                    papyon_contact = self._papyon_addressbook.\
                                          contacts.search_by('account', account)[0]
                except IndexError:
                    self._core._ui_manager.showError('You don\'t have the %s contact!', account)
                    return

                self.removeContactUid(papyon_contact.id)

        self._core._ui_manager.loadContactDeleteWindow(contactCB)

    def removeContactUid(self, uid):
        papyon_contact = self._papyon_addressbook.contacts.search_by('id', uid)[0]
        def cb_ok():
            self._papyon_addressbook.delete_contact(papyon_contact)

        self._core._ui_manager.showDialog('Are you sure you want to remove the contact %s?'
                                          % papyon_contact.account,
                                          (('OK', cb_ok), ('Cancel', lambda : '')))

    def blockContact(self, cid):
        pass

    def unblockContact(self, cid):
        pass

    def allowContact(self, cid):
        pass

    def disallowContact(self, cid):
        pass

    def acceptContactInvitation(self):
        pass

    def declineContactInvitation(self):
        pass

    def addGroup(self, name, contacts_ids):
        def failed(group):
            self._core._ui_manager.showError('Failed to add the group %s', group)

        self._papyon_addressbook.add_group(self, name, failed_cb=failed):

    def removeGroup(self, gid):
        group = self.getGroup(gid)
        def failed(group):
            self._core._ui_manager.showError('Failed to remove the group %s', group.name)

        self._papyon_addressbook.delete_group(self, group, failed_cb=failed)

    def renameGroup(self, gid, new_name):
        group = self.getGroup(gid)
        def failed(group):
            self._core._ui_manager.showError('Failed to rename the group %s', group.name)

        self._papyon_addressbook.rename_group(self, group, new_name, failed_cb=failed)

    def addContactToGroups(self, cid, gids):
        pass

    def removeContactFromGroups(self, cid, gids):
        pass

    ''' callbacks for the user's actions '''

    def onContactAdded(self, contact):
        c = self.getContact(contact.id, contact)
        gids = [ g.id for g in self.getGroups(contact.id)]
        self._addContactToGroups(contact.id, gids)
        self._core._ui_manager.showNotification("Contact %s added!" % contact.account)

    def onContactRemoved(self, contact):
        self._removeContactFromGroups(contact.id)
        del self._contacts[contact.id]
        self._core._ui_manager.showNotification("Contact %s removed!" % contact.account)

    def onContactBlocked(self, papyon_contact):
        pass

    def onContactUnblocked(self, papyon_contact):
        pass

    def onGroupAdded(self, papyon_group):
        pass

    def onGroupDeleted(self, papyon_group):
        pass

    def onGroupRenamed(self, papyon_group):
        pass

    def onGroupContactAdded(self, papyon_group, papyon_contact):
        pass

    def onGroupContactDeleted(self, papyon_group, papyon_contact):
        pass

    ''' additional methods '''

    # used when a contact is deleted, moved or change status to offline
    def _removeContactFromGroups(self, cid):
        groups = self.getGroups(cid)
        for g in groups:
            g.contacts.remove(cid)
            gv = GroupView(self._core, g)
            self._em.emit(self._em.events.GROUPVIEW_UPDATED, gv)

    def _addContactToGroups(self, cid, gids):
        for gid in gids:
            g = self.getGroup(gid)
            g.contacts.add(cid)
            gv = GroupView(self._core, g)
            self._em.emit(self._em.events.GROUPVIEW_UPDATED, gv)

        c = self.getContact(cid)
        cv = ContactView(self._core, c)
        self._em.emit(self._em.events.CONTACTVIEW_UPDATED, cv)

    # can this be reused to rebuild the contactlist when we want to group the contacts in another way?
    # maybe adding a createGroups method?
    def onCLDownloaded(self, address_book):
        self._papyon_addressbook = address_book
        grpviews = []
        cviews = []
        clv = ContactListView()

        for group in address_book.groups:
            g = self.getGroup(group.id, group)
            gv = GroupView(self._core, g)
            grpviews.append(gv)
            clv.group_ids.append(group.id)

        no_group = False
        for contact in address_book.contacts:
            c = self.getContact(contact.id, contact)
            cv = ContactView(self._core, c)
            cviews.append(cv)
            if len(contact.groups) == 0:
                no_group =True

        if no_group:
            g = self.getGroup(0, None)
            gv = GroupView(self._core, g)
            grpviews.append(gv)
            clv.group_ids.append(0)

        #Emit the events
        self._em.emit(self._em.events.CLVIEW_UPDATED, clv)
        for g in grpviews:
            self._em.emit(self._em.events.GROUPVIEW_UPDATED, g)
        for c in cviews:
            self._em.emit(self._em.events.CONTACTVIEW_UPDATED, c)

    def getContact(self, uid, papyon_contact=None):
        """
        @param uid: uid of the contact
        @type uid: str
        @param papyon_contact:
        @type papyon_contact:
        @return: aMSNContact of that contact
        @rtype: aMSNContact
        """
        #TODO: should raise UnknownContact or sthg like that
        try:
            return self._contacts[uid]
        except KeyError:
            if papyon_contact is not None:
                c = aMSNContact(self._core, papyon_contact)
                self._contacts[uid] = c
                self._em.emit(self._em.events.AMSNCONTACT_UPDATED, c)
                return c
            else:
                raise ValueError

    def getGroup(self, gid, papyon_group = None, cids=[]):
        """
        @param gid: uid of the group
        @type gid: str
        @param papyon_group:
        @type papyon_group:
        @return: aMSNGroup of that group
        @rtype: aMSNGroup
        """
        try:
            return self._groups[gid]
        except KeyError:
            if papyon_group:
                g = aMSNGroup(self._core, papyon_group)
                # is AMSNGROUP_UPDATED necessary?
            elif gid == 0:
                g = aMSNGroup(self._core)
            else:
                raise ValueError

            self._groups[gid] = g
            return g

    def getGroups(self, uid):
        # propagate a ValueError
        return [self.getGroup(gid) for gid in self.getContact(uid).groups]


""" A few things used to describe a contact
    They are stored in that structure so that there's no need to create them
    everytime
"""
class aMSNContact():
    def __init__(self, core, papyon_contact=None):
        """
        @type core: aMSNCore
        @param papyon_contact:
        @type papyon_contact: papyon.profile.Contact
        """
        self._core = core

        self.account  = ''
        self.groups = set()
        self.dp = ImageView()
        self.icon = ImageView()
        self.emblem = ImageView()
        self.nickname = StringView()
        self.status = StringView()
        self.personal_message = StringView()
        self.current_media = StringView()
        if papyon_contact:
            if papyon_contact.msn_object is None:
                self.dp.load("Theme", "dp_nopic")
            else:
                self.dp.load("Theme", "dp_loading")
            self.fill(papyon_contact)

        else:
            self.dp.load("Theme", "dp_nopic")
            self.uid = None

    def fill(self, papyon_contact):
        """
        Fills the aMSNContact structure.

        @type papyon_contact: papyon.profile.Contact
        """

        self.uid = papyon_contact.id
        self.account = papyon_contact.account
        self.icon.load("Theme","buddy_" + self._core.p2s[papyon_contact.presence])
        self.emblem.load("Theme", "emblem_" + self._core.p2s[papyon_contact.presence])
        #TODO: PARSE ONLY ONCE
        self.nickname.reset()
        self.nickname.appendText(papyon_contact.display_name)
        self.personal_message.reset()
        self.personal_message.appendText(papyon_contact.personal_message)
        self.current_media.reset()
        self.current_media.appendText(papyon_contact.current_media)
        self.status.reset()
        self.status.appendText(self._core.p2s[papyon_contact.presence])

        #DP:
        if papyon_contact.msn_object:
            fn = self._core._backend_manager.getFileLocationDP(
                    papyon_contact.account,
                    papyon_contact.id,
                    papyon_contact.msn_object._data_sha)
            if os.path.exists(fn):
                self.dp.load("Filename", fn)
            else:
                #TODO: request?
                pass
        # ro, can be changed indirectly with addressbook's actions
        self.memberships = papyon_contact.memberships
        self.contact_type = papyon_contact.contact_type
        for g in papyon_contact.groups:
            self.groups.add(g.id)
        if len(self.groups) == 0:
            self.groups.add(0)
        # ro
        self.capabilities = papyon_contact.client_capabilities
        self.infos = papyon_contact.infos.copy()
        #for the moment, we store the papyon_contact object, but we shouldn't have to

        #TODO: getPapyonContact(self, core...) or _papyon_contact?
        self._papyon_contact = papyon_contact

class aMSNGroup():
    def __init__(self, core, papyon_group=None):
        self._contacts_storage = core._contactlist_manager._papyon_addressbook.contacts
        self.contacts = set()
        self.contacts_online = set()
        self.papyon_group = papyon_group
        self.fill(papyon_group)

    def fill(self, papyon_group=None):
        if self.papyon_group:
            papyon_group = self.papyon_group

        # obtain all the contacts in the group
        if papyon_group:
            self.name = papyon_group.name
            self.id = papyon_group.id
            contacts = self._contacts_storage.search_by_groups(papyon_group)
        else:
            self.name = 'NoGroup'
            self.id = 0
            contacts = self._contacts_storage.search_by_memberships(papyon.Membership.FORWARD)
            contacts = [c for c in contacts if len(c.groups) == 0]

        self.contacts = set([ c.id for c in contacts])
        self.contacts_online = set([c.id for c in contacts if c.presence != papyon.Presence.OFFLINE])

