from views import *
import os
import tempfile
import papyon
import logging

logger = logging.getLogger('amsn2.cl-manager')

class aMSNContactListManager:
    def __init__(self, core):
        """
        @type core: aMSNCore
        """

        self._core = core
        self._em = core._event_manager
        self._contacts = {} #Dictionary where every contact_uid has an associated aMSNContact
        self._groups = {}
        self._clv = None
        self._papyon_addressbook = None

    #TODO: sorting contacts & groups
    #TODO: simplify management of groups

    ''' normal changes of a contact '''

    def on_contact_changed(self, papyon_contact):
        """ Called when a contact changes either its presence, nick, psm or current media."""

        #1st/ update the aMSNContact object
        c = self.get_contact(papyon_contact.id, papyon_contact)
        c.fill(papyon_contact)
        #2nd/ update the ContactView
        cv = ContactView(self._core, c)
        self._em.emit(self._em.events.CONTACTVIEW_UPDATED, cv)

        ##3rd/ update the GroupView
        #for gid in c.groups:
        #    group = self.get_group(gid)
        #    gv = GroupView(self._core, gid, group.name, group.contacts)
        #    self._em.emit(self._em.events.GROUPVIEW_UPDATED, gv)

        #TODO: if contacts are sorted by presence, remove contact
        # from the offline/online group depending on the change
        groups = self.get_groups(c.uid)
        for g in groups:
            g.fill()
            self.on_amsn_group_changed(g)

    def on_group_changed(self, papyon_group):
        """ Called when a group changes its members or is renamed """
        # if grouping by papyon groups
        g = self.get_group(papyon_group.id)
        g.fill(papyon_group)
        self.on_amsn_group_changed(g)

    def on_amsn_group_changed(self, amsn_group):
        gv = GroupView(self._core, amsn_group)
        self._em.emit(self._em.events.GROUPVIEW_UPDATED, gv)

    def on_contact_DP_changed(self, papyon_contact):
        """ Called when a contact changes its Display Picture. """

        #Request the DP...
        c = self.get_contact(papyon_contact.id, papyon_contact)
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
                                                                (self.on_DP_downloaded,
                                                                 papyon_contact.id),
                                                                 peer = papyon_contact)

    def on_DP_downloaded(self, msn_object, uid):
        #1st/ update the aMSNContact object
        try:
            c = self.get_contact(uid)
        except ValueError:
            return
        fn = self._core._backend_manager.get_file_location_DP(c.account, uid,
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

    def add_contact(self):
        def cb(email, invite_msg='', groups=[]):
            logger.info('Adding WLM contact %s' %email)
            if email:
                def failed(error_code):
                    self._core._ui_manager.showError('Failed to remove the contact %s'
                                                      %email)
                    logger.error('Failed to remove contact %s error code %s' %(email, error_code))

                def done(papyon_contact):
                    # FIXME: this rely on the fact that papyon first emit
                    # the signal "contact-added", then calls this callback
                    # see AddressBook.__common_callback in papyon/service/AddressBook.py

                    # here groups is the list of group ids
                    self.add_contact_to_groups(papyon_contact.id, groups)

                self._papyon_addressbook.add_messenger_contact(email, self._core._account.view.email,
                                                               invite_msg, failed_cb=(failed,),
                                                               done_cb=(done,))

        groupviews = [GroupView(self._core, g) for g in self._groups.values()]
        self._core._ui_manager.load_contact_input_window(cb, groupviews)

    def remove_contact(self):
        def contact_cb(account):
            if account:
                try:
                    papyon_contact = self._papyon_addressbook.\
                                          contacts.search_by('account', account)[0]
                except IndexError:
                    self._core._ui_manager.show_error('You don\'t have the %s contact!'
                                                      %account)
                    logger.error('Failed to remove non-existing contact %s' %account)
                    return

                self.remove_contact_Uid(papyon_contact.id)

        contactviews = [ContactView(self._core, c) for c in self._contacts.values()]
        self._core._ui_manager.load_contact_delete_window(contact_cb, contactviews)

    def remove_contact_Uid(self, uid):
        papyon_contact = self._papyon_addressbook.contacts.search_by('id', uid)[0]
        def cb_ok():
            def failed(error_code):
                logger.error('Failed to remove %s error_code: %s' %(papyon_contact.account, error_code))
                self._core._ui_manager.show_error('Failed to remove the contact %s'
                                                  %papyon_contact.account)

            logger.info('Removing %s' %papyon_contact.account)
            self._papyon_addressbook.delete_contact(papyon_contact, failed_cb=(failed,))

        self._core._ui_manager.show_dialog('Are you sure you want to remove the contact %s?'
                                          % papyon_contact.account,
                                          (('OK', cb_ok), ('Cancel', lambda : '')))

    def block_contact(self, cid):
        pass

    def unblock_contact(self, cid):
        pass

    def allow_contact(self, cid):
        pass

    def disallow_contact(self, cid):
        pass

    def accept_contact_invitation(self):
        pass

    def decline_contact_invitation(self):
        pass

    def add_group(self):
        def cb(name, contacts=[]):
            def failed(error_code):
                logger.error('Failed to remove %s error code %s' %(name, error_code))
                self._core._ui_manager.show_error('Failed to add the group %s'
                                                  %name)

            def done(papyon_group):
                # FIXME: this rely on the fact that papyon first emit
                # the signal "group-added", then calls this callback
                # see AddressBook.__common_callback in papyon/service/AddressBook.py
                for contact in contacts:
                    cids = [cid for cid in self._contacts.keys()\
                            if self.get_contact(cid).account==contact]

                    self.add_contact_to_groups(cids[0], [papyon_group.id])

            self._papyon_addressbook.add_group(name, done_cb=(done,),
                                               failed_cb=(failed,))

        contactviews = [ContactView(self._core, c) for c in self._contacts.values()]
        self._core._ui_manager.load_group_input_window(cb, contactviews)

    def remove_group(self):
        def cb(group_name):
            if group_name:
                group = [g for g in self._groups.values() if g.name==group_name]
                if group:
                    self.remove_group_gid(group[0].id)

        groupviews = [GroupView(self._core, g) for g in self._groups.values()]
        self._core._ui_manager.load_group_delete_window(cb, groupviews)

    def remove_group_gid(self, gid):
        papyon_group = [g for g in self._papyon_addressbook.groups if g.id==gid][0]
        def failed(error_code):
            logger.error('Failed to remove group %s error code %s'
                                            %(papyon_group.name, error_code))
            self._core._ui_manager.show_error('Failed to remove the group %s'
                                              %self.get_group(gid).name)

        self._papyon_addressbook.delete_group(papyon_group, failed_cb=(failed,))

    def rename_group_gid(self, gid, new_name):
        group = self.get_group(gid)
        def failed(error_code):
            logger.error('Failed to rename %s to %s error code %s'
                                            %(group.name, new_name, error_code))
            self._core._ui_manager.show_error('Failed to rename the group %s'
                                              %self.get_group(gid).name)

        logger.info('Renaming group %s to %s' %(group.name, new_name))
        self._papyon_addressbook.rename_group(group, new_name, failed_cb=(failed,))

    def add_contact_to_groups(self, cid, gids):
        def failed(error_code):
            account = self.get_contact(cid).account
            groups = [self.get_group(gid) for gid in gids]
            logger.error('Failed to add %s to the groups %s, error code %s'
                                      %(account, ' '.join(groups), error_code))
            self._core._ui_manager.show_error('Failed to add %s to the groups'
                                                                    %(account))
        #TODO: contact may exist in multiple networks
        for gid in gids:
            groups = [g for g in self._papyon_addressbook.groups if g.id==gid]
            contacts = self._papyon_addressbook.contacts.search_by('id', cid)
            self._papyon_addressbook.add_contact_to_group(groups[0],
                                                          contacts[0],
                                                          failed_cb=(failed,))

    def remove_contact_from_groups(self, cid, gids):
        def failed(error_code):
            account = self.get_contact(cid).account
            groups = [self.get_group(gid).name for gid in gids]
            logger.error('Failed to add %s to the groups %s, error code %s'
                                      %(account, ' '.join(groups), error_code))
            self._core._ui_manager.show_error('Failed to remove %s to the groups'
                                                                    %(account))
        #TODO: contact may exist in multiple networks
        for gid in gids:
            groups = [g for g in self._papyon_addressbook.groups if g.id==gid]
            contacts = self._papyon_addressbook.contacts.search_by('id', cid)
            self._papyon_addressbook.delete_contact_from_group(groups[0],
                                                          contacts[0],
                                                          failed_cb=(failed,))

    ''' callbacks for the user's actions '''

    def on_contact_added(self, contact):
        logger.info('Contact %s added' %contact.account)
        c = self.get_contact(contact.id, contact)
        gids = [ g.id for g in self.get_groups(contact.id)]
        self._add_contact_to_groups(contact.id, gids)
        self._core._ui_manager.show_notification("Contact %s added!" % contact.account)

    def on_contact_removed(self, contact):
        logger.info('Contact %s removed' %contact.account)
        self._remove_contact_from_groups(contact.id)
        del self._contacts[contact.id]
        self._core._ui_manager.show_notification("Contact %s removed!" % contact.account)

    def on_contact_blocked(self, papyon_contact):
        pass

    def on_contact_unblocked(self, papyon_contact):
        pass

    def on_group_added(self, papyon_group):
        logger.info('Group %s added' %papyon_group.name)
        self.update_groups()

    def on_group_deleted(self, papyon_group):
        logger.info('Group %s deleted' %papyon_group.name)
        amsn_group = self.get_group(papyon_group.id)
        self.update_groups()
        for cid in amsn_group.contacts:
            c = self.get_contact(cid)
            cv = ContactView(self._core, c)
            self._em.emit(self._em.events.CONTACTVIEW_UPDATED, cv)

    def on_group_renamed(self, papyon_group):
        logger.info('Group %s renamed' %papyon_group.name)

    def on_group_contact_added(self, papyon_group, papyon_contact):
        logger.info('Contact %s added to group %s' %(papyon_contact.account,
                                                     papyon_group.name))
        self._add_contact_to_groups(papyon_contact.id, [papyon_group.id])

    def on_group_contact_deleted(self, papyon_group, papyon_contact):
        logger.info('Contact %s deleted from group %s'
                                  %(papyon_contact.account, papyon_group.name))
        #amsn_group = self.get_group(papyon_group.id)
        #amsn_group.contacts.remove(papyon_contact.id)
        ###gv = GroupView(self._core, amsn_group)
        ###self._em.emit(self._em.events.GROUPVIEW_UPDATED, gv)
        #self.update_groups()
        self._remove_contact_from_groups(papyon_contact.id, [papyon_group.id])

    ''' additional methods '''

    # used when a contact is deleted, moved or change status to offline
    def _remove_contact_from_groups(self, cid, gids=None):
        if gids:
            groups = [self.get_group(gid) for gid in gids]
        else:
            groups = self.get_groups(cid)
        for g in groups:
            g.contacts.remove(cid)
            g.fill()

        self.update_groups()

        # if a contact has to be removed from all the groups, has been deleted
        if gids:
            c = self.get_contact(cid)
            for gid in gids: c.groups.remove(gid)
            cv = ContactView(self._core, c)
            self._em.emit(self._em.events.CONTACTVIEW_UPDATED, cv)

    def _add_contact_to_groups(self, cid, gids):
        for gid in gids:
            g = self.get_group(gid)
            g.fill()
            #gv = GroupView(self._core, g)
            #self._em.emit(self._em.events.GROUPVIEW_UPDATED, gv)

        self.update_groups()

        c = self.get_contact(cid)
        for gid in gids: c.groups.add(gid)
        cv = ContactView(self._core, c)
        self._em.emit(self._em.events.CONTACTVIEW_UPDATED, cv)

    def on_CL_downloaded(self, address_book):
        self._papyon_addressbook = address_book
        self._clv = ContactListView()

        self.update_groups()
        self.update_contacts()

    def update_groups(self):
        logger.debug('Updating aMSN2 groups')
        grpviews = []

        # if grouping by user groups:
        # update the list of existing groups
        new_groups = [g for g in self._papyon_addressbook.groups if g.id not in self._groups.keys()]
        gids = [g.id for g in self._papyon_addressbook.groups]
        old_groups = [self.get_group(gid) for gid in self._groups.keys() if gid not in gids]
        for group in new_groups:
            g = self.get_group(group.id, group)
            self._clv.group_ids.append(group.id)

        for group in old_groups:
            self._clv.group_ids.remove(group.id)
            del self._groups[group.id]

        # and check if the NoGroup is needed
        contacts_nogroup = [c for c in self._papyon_addressbook.contacts if len(c.groups) == 0]
        if contacts_nogroup:
            nogroup = self.get_group(0)
            self._clv.group_ids.append(nogroup.id)

        # TODO: group in other ways (presence, no-grouping...)

        # create the groupviews
        for gid in self._clv.group_ids:
            g = self.get_group(gid)
            gv = GroupView(self._core, g)
            grpviews.append(gv)

        # and update them to the ui
        self._em.emit(self._em.events.CLVIEW_UPDATED, self._clv)
        for g in grpviews:
            self._em.emit(self._em.events.GROUPVIEW_UPDATED, g)

    def update_contacts(self):
        logger.debug('Updating aMSN2 contacts')
        cviews = []
        for contact in self._papyon_addressbook.contacts:
            c = self.get_contact(contact.id, contact)
            cv = ContactView(self._core, c)
            cviews.append(cv)

        #Emit the events
        for c in cviews:
            self._em.emit(self._em.events.CONTACTVIEW_UPDATED, c)

    def get_contact(self, uid, papyon_contact=None):
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

    # TODO: create aMSNPresenceGroup, ... depending on the gid type
    def get_group(self, gid, papyon_group = None):
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
                g = aMSNPapyonGroup(self._core, papyon_group)
                g.fill()
                # is AMSNGROUP_UPDATED necessary?
            elif gid == 0:
                g = aMSNPapyonGroup(self._core, None)
                g.fill()
            else:
                raise ValueError

            self._groups[gid] = g
            return g

    def get_groups(self, uid):
        # propagate a ValueError
        return [self.get_group(gid) for gid in self.get_contact(uid).groups]


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
        self.nickname.append_text(papyon_contact.display_name)
        self.personal_message.reset()
        self.personal_message.append_text(papyon_contact.personal_message)
        self.current_media.reset()
        self.current_media.append_text(papyon_contact.current_media)
        self.status.reset()
        self.status.append_text(self._core.p2s[papyon_contact.presence])

        #DP:
        if papyon_contact.msn_object:
            fn = self._core._backend_manager.get_file_location_DP(
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

class aMSNBaseGroup():
    """ Base class that represent a group of amsn2contacts """
    def __init__(self, core):
        self._contacts_storage = core._contactlist_manager._papyon_addressbook.contacts
        self.contacts = set()
        self.contacts_online = set()
        self.id = None
        self.name = ''
        #self.papyon_group = papyon_group
        #self.fill(papyon_group)

    def fill(self):
        raise NotImplementedError

class aMSNPapyonGroup(aMSNBaseGroup):
    """ Group which holds the contacts according to the group assigned in the WLM network """
    def __init__(self, core, papyon_group):
        aMSNBaseGroup.__init__(self, core)
        self.papyon_group = papyon_group

    def fill(self):
        # obtain all the contacts in the group
        if self.papyon_group:
            self.name = self.papyon_group.name
            self.id = self.papyon_group.id
            contacts = self._contacts_storage.search_by_groups(self.papyon_group)
        else:
            self.name = 'NoGroup'
            self.id = 0
            contacts = self._contacts_storage.search_by_memberships(papyon.Membership.FORWARD)
            contacts = [c for c in contacts if len(c.groups) == 0]

        self.contacts = set([ c.id for c in contacts])
        self.contacts_online = set([c.id for c in contacts if c.presence != papyon.Presence.OFFLINE])

class aMSNPreseceGroup(aMSNBaseGroup):
    """ Group which holds the contacts according to their status """
    def __init__(self, core):
        aMSNBaseGroup.__init__(self, core)

