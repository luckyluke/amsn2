"""TODO:
    * Let the aMSNContactListWidget be selectable to choose contacts to add to a
    conversation... each contact should have a checkbox on front of it
    * Drag contacts through groups
    * Drag groups
    ...
"""

from amsn2.ui import base

class aMSNContactListWindow(base.aMSNContactListWindow):
    """ This interface represents the main Contact List Window
        self._clwidget is an aMSNContactListWidget
    """

    def __init__(self, amsn_core, parent):
        self._main = parent
        self._clwidget = aMSNContactListWidget(amsn_core,self)
        self._main.cl_window = self

    def __del__(self):
        self._main.cl_window = None

    def show(self):
        """ Show the contact list window """
        self._main.cl_window = self
        self._main.send("showContactListWindow")

    def hide(self):
        """ Hide the contact list window """
        self._main.login_window = None
        self._main.send("hideContactListWindow")

    def set_title(self, text):
        """ This will allow the core to change the current window's title
        @text : a string
        """
        self._main.send("setContactListTitle", text)

    def set_menu(self, menu):
        """ This will allow the core to change the current window's main menu
        @menu : a MenuView
        """
        self._main.send("setMenu")

    def my_info_updated(self, view):
        """ This will allow the core to change pieces of information about
        ourself, such as DP, nick, psm, the current media being played,...
        @view: the contactView of the ourself (contains DP, nick, psm,
        currentMedia,...)"""
        self._main.send("myInfoUpdated", str(view.nick))

    def get_contactlist_widget(self):
        return self._clwidget

class aMSNContactListWidget(base.aMSNContactListWidget):
    """ This interface implements the contact list of the UI """
    def __init__(self, amsn_core, parent):
        self._main = parent._main
        self.contacts = {}
        self.groups = {}

    def contact_clicked(self, uid):
        try:
            self.contacts[uid].on_click(uid)
        except Exception, inst:
            print inst
        return True

    def show(self):
        """ Show the contact list widget """
        self._main.send("showContactListWidget")

    def hide(self):
        """ Hide the contact list widget """
        self._main.send("hideContactListWidget")

    def contactlist_updated(self, clView):
        """ This method will be called when the core wants to notify
        the contact list of the groups that it contains, and where they
        should be drawn a group should be drawn.
        It will be called initially to feed the contact list with the groups
        that the CL should contain.
        It will also be called to remove any group that needs to be removed.
        @cl : a ContactListView containing the list of groups contained in
        the contact list which will contain the list of ContactViews
        for all the contacts to show in the group."""
        self._main.send("contactListUpdated", clView.group_ids)

    def group_updated(self, groupView):
        """ This method will be called to notify the contact list
        that a group has been updated.
        The contact list should update its icon and name
        but also its content (the ContactViews). The order of the contacts
        may be changed, in which case the UI should update itself accordingly.
        A contact can also be added or removed from a group using this method
        """
        self.groups[groupView.uid]=groupView
        self._main.send("groupUpdated",
                        groupView.uid,
                        str(groupView.name),
                        sorted(groupView.contact_ids))

    def contact_updated(self, contactView):
        """ This method will be called to notify the contact list
        that a contact has been updated.
        The contact can be in any group drawn and his icon,
        name or DP should be updated accordingly.
        The position of the contact will not be changed by a call
        to this function. If the position was changed, a groupUpdated
        call will be made with the new order of the contacts
        in the affects groups.
        """
        self.contacts[contactView.uid]=contactView
        self._main.send("contactUpdated", contactView.uid, str(contactView.name))

