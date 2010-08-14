# -*- coding: utf-8 -*-
from amsn2.ui import base
import image
from PyQt4.QtCore import *
from PyQt4.QtGui import *


class aMSNFileChooserWindow(base.aMSNFileChooserWindow):
    def __init__(self, filters, directory, callback, parent = None):

        filefilter = QString()

        if filters:
            first = True
            for name in filters.keys():
                if first == False:
                    filefilter = filefilter + ";;"
                filefilter = filefilter + name + " ("
                for ext in filters[name]:
                    filefilter = filefilter + ext + " "
                filefilter = filefilter + ")"
                first = False

        filename=QFileDialog.getOpenFileName(parent, "aMSN2 - Choose a file", "", filefilter)


        self.callback = callback
        if str(filename)=="":
            pass
        else:
            self.callback(filename)





class aMSNDPChooserWindow(base.aMSNDPChooserWindow, QDialog):
    def __init__(self, callback, backend_manager, parent = None):
        QDialog.__init__(self, parent)
        
        self.resize(550, 450)
        self.setWindowTitle("aMSN - Choose a Display Picture")
        self.callback = callback
        self.iconview = QListWidget()
        self.iconview.setViewMode(1)
        self.iconview.setResizeMode(1)
        self.iconview.setMovement(0)
        self.iconview.setIconSize(QSize(96,96))
        self.iconview.setWordWrap( True )
        self.iconview.setGridSize(QSize(106,121))
        QObject.connect(self.iconview, SIGNAL("itemDoubleClicked(QListWidgetItem)"), self._on_dp_dblclick)
        self.buttonOk= QPushButton("Ok")
        QObject.connect(self.buttonOk, SIGNAL("clicked()"), self._on_ok_clicked)
        self.buttonCancel = QPushButton("Cancel")
        QObject.connect(self.buttonCancel, SIGNAL("clicked()"), self.reject)
        self.buttonOpen = QPushButton("Open File")
        QObject.connect(self.buttonOpen, SIGNAL("clicked()"), self._open_file)
        self.vboxlayout = QVBoxLayout()
        self.hboxlayout = QHBoxLayout()
        self.vboxlayout.addWidget(self.buttonOk)
        self.vboxlayout.addWidget(self.buttonCancel)
        self.vboxlayout.addWidget(self.buttonOpen)
        self.vboxlayout.addStretch(1)
        self.hboxlayout.addWidget(self.iconview)
        self.hboxlayout.addLayout(self.vboxlayout)
        self.setLayout(self.hboxlayout)
        default_dps = []
        for dp in default_dps:
            self._update_dp_list(default_dps)
        self.exec_()

    def _open_file(self):
        filters = {'Image files':("*.png", "*.jpeg", "*.jpg", "*.gif", "*.bmp"),
                   'All files':('*.*')}
        self.filechooser = aMSNFileChooserWindow(filters, None, self._update_dp_list,self)


    def _dp_chosen(self, path):
        self.callback(str(path))    
        self.done(0)
        
        
    def _on_ok_clicked(self):
        item = self.iconview.currentItem()
        if item == None:
            return

        path = item.data(Qt.UserRole)
        path = path.toString()
        self._dp_chosen(path)
        

    def _on_dp_dblclick(self, item):
        path = item.data(Qt.UserRole)
        path = path.toString()
        self._dp_chosen(path)
        

    def _update_dp_list(self, dp_path):
        im = QPixmap(dp_path) #should pass the image to the core then get the rescaled pixmap from it
        im = im.scaled(96,96,0,1) #should also check if the given path really contains an image, or the core should ?
        name = QString(dp_path)
        name.remove(0, (name.lastIndexOf("/")+1))
        item = QListWidgetItem(QIcon(im), name)
        item.setData(Qt.UserRole, dp_path)
        self.iconview.addItem(item)