from amsn2.core.views import StringView, MenuItemView
from PyQt4.QtCore import *
from PyQt4.QtGui import *


def create_menu_items_from_view(menu, items):
    # TODO: images & radio groups, for now only basic representation
    for item in items:
        if item.type is MenuItemView.COMMAND:
            it = QAction(item.label, menu)
            QObject.connect(it, SIGNAL("triggered()"), item.command)
            menu.addAction(it)
        elif item.type is MenuItemView.CASCADE_MENU:
            men = QMenu(item.label, menu)
            create_menu_items_from_view(men, item.items)
            menu.addMenu(men)
        elif item.type is MenuItemView.SEPARATOR:
            menu.addSeparator()
        elif item.type is MenuItemView.CHECKBUTTON:
            it = QAction(item.label, menu)
            it.setCheckable(True)
            if item.checkbox: #TODO : isn't it checkbox_value instead of checkbox ? By the way the MenuItemView constructor doesn't store the checkbox_value passed to it
                it.setChecked(True)
            QObject.connect(it, SIGNAL("triggered()"), item.command)
            menu.addAction(it)
        elif item.type is MenuItemView.RADIOBUTTON:
            it = QAction(item.label, menu)
            it.setCheckable(True)
            if item.checkbox: 
                it.setChecked(True)
            QObject.connect(it, SIGNAL("triggered()"), item.command)
        elif item.type is MenuItemView.RADIOBUTTONGROUP:
            group = QActionGroup(menu)
            create_menu_items_from_view(group, item.items)
            menu.addActions(group)
