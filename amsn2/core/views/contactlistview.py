from stringview import *
from imageview import *
from menuview import *

class ContactListView:
    def __init__(self):
        self.group_ids = []

    def __repr__(self):
        return "<ContactListView {group_ids=%s}>" \
                % (repr(self.group_ids),)


class GroupView:
    def __init__(self, core, amsn_group):
        self.uid = amsn_group.id
        self.contact_ids = set(amsn_group.contacts)
        self.icon = ImageView() # TODO: expanded/collapsed icon
        self.name = StringView() # TODO: default color from skin/settings

        self.name.append_text(amsn_group.name) #TODO: parse for smileys
        active = len(amsn_group.contacts_online)

        #self.name.append_text(name) #TODO: parse for smileys
        #active = 0
        #for cid in contact_ids:
        #    contact = core._contactlist_manager.get_contact(cid)
        #    if str(contact.status) != core.p2s['FLN']:
        #        active = active + 1

        total = len(self.contact_ids)
        self.name.append_text("(" + str(active) + "/" + str(total) + ")")

        self.on_click = None #TODO: collapse, expand
        self.on_double_click = None
        self.on_right_click_popup_menu = GroupPopupMenu(core, amsn_group)
        self.tooltip = None
        self.context_menu = None


    #TODO: @roproperty: context_menu, tooltip

    def __repr__(self):
        return "<GroupView {uid='%s', name='%s', contact_ids=%s}>" \
                % (self.uid, self.name, repr(self.contact_ids))

""" a view of a contact on the contact list """
class ContactView:
    def __init__(self, core, amsn_contact):
        """
        @type core: aMSNCore
        @type amsn_contact: aMSNContact
        """

        self.uid = amsn_contact.uid

        self.account = amsn_contact.account
        #self.contact = amsn_contact # Usefull at least if we want to reload the ContactPopupMenu

        self.icon = amsn_contact.icon
        #TODO: apply emblem on dp
        self.dp = amsn_contact.dp.clone()
        self.dp.append_imageview(amsn_contact.emblem)
        self.name = StringView() # TODO : default colors
        self.name.open_tag("nickname")
        self.name.append_stringview(amsn_contact.nickname) # TODO parse
        self.name.close_tag("nickname")
        self.name.append_text(" ")
        self.name.open_tag("status")
        self.name.append_text("(")
        self.name.append_stringview(amsn_contact.status)
        self.name.append_text(")")
        self.name.close_tag("status")
        self.name.append_text(" ")
        self.name.open_tag("psm")
        self.name.set_italic()
        self.name.append_stringview(amsn_contact.personal_message)
        self.name.unset_italic()
        self.name.close_tag("psm")

        def start_conversation_cb(c_uid):
            core._conversation_manager.new_conversation([c_uid])
        self.on_click = start_conversation_cb
        self.on_double_click = None
        self.on_right_click_popup_menu = ContactPopupMenu(core, amsn_contact)
        self.tooltip = None
        self.context_menu = None

    #TODO: @roproperty: context_menu, tooltip

    def __repr__(self):
        return "<ContactView {uid='%s', name='%s'}>" % (self.uid, self.name)

class ContactPopupMenu(MenuView):
    def __init__(self, core, amsn_contact):
        MenuView.__init__(self)
        self._cm = core._contactlist_manager
        self._uid = amsn_contact.uid

        remove = MenuItemView(MenuItemView.COMMAND,
                              label="Remove %s" % amsn_contact.account,
                              command= lambda:
                              self._cm.remove_contact_Uid(amsn_contact.uid))
        self.add_item(remove)

    def create_var_items(self):
        amsn_contact = self._cm.get_contact(self._uid)

        copy_to_group = MenuItemView(MenuItemView.CASCADE_MENU, label="Copy to group")
        move_to_group = MenuItemView(MenuItemView.CASCADE_MENU, label="Move to group")
        for gid in self._cm._groups.keys():
            if gid in amsn_contact.groups or gid == 0: continue
            amsn_group = self._cm.get_group(gid)

            def add_to_g(gid):
                return lambda: self._cm.add_contact_to_groups(amsn_contact.uid, (gid,))

            def move_to_g(gid):
                # TODO: the contactmenu should know which group the view belongs to..
                def do_move():
                    #self._cm.remove_contact_from_groups(self._uid, )
                    add_to_g(gid)()
                return do_move

            group_entry = MenuItemView(MenuItemView.COMMAND, label=amsn_group.name,
                                       command=add_to_g(gid))
            copy_to_group.add_item(group_entry)

            group_entry = MenuItemView(MenuItemView.COMMAND, label=amsn_group.name,
                                       command=move_to_g(gid))
            move_to_group.add_item(group_entry)

        remove_from_group = MenuItemView(MenuItemView.CASCADE_MENU, label="Remove from group")
        for gid in amsn_contact.groups:
            if gid == 0:
                remove_from_group.disabled = True
                continue

            amsn_group = self._cm.get_group(gid)
            def remove_from_g(gid):
                return lambda: self._cm.remove_contact_from_groups(amsn_contact.uid, (gid,))

            group_entry = MenuItemView(MenuItemView.COMMAND, label=amsn_group.name,
                                       command=remove_from_g(gid))
            remove_from_group.add_item(group_entry)

        self._var_items = [copy_to_group, move_to_group, remove_from_group]


class GroupPopupMenu(MenuView):
    def __init__(self, core, amsn_group):
        MenuView.__init__(self)
        add_group = MenuItemView(MenuItemView.COMMAND,
                                 label="Add group",
                                 command= lambda:
                                 core._contactlist_manager.add_group())

        self.add_item(add_group)
        if amsn_group.id != 0:
            remove = MenuItemView(MenuItemView.COMMAND,
                                  label="Remove group",
                                  command= lambda:
                                  core._contactlist_manager.remove_group_gid(amsn_group.id))

            self.add_item(remove)

