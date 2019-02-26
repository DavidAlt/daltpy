# -*- coding: utf-8 -*-
# Author:  David Alt, 2/25/19
# Status:  complete

import sys
from PySide2.QtWidgets import (QApplication, QMainWindow, QWidget, QPushButton, QLabel, QListView)
from PySide2.QtWidgets import QVBoxLayout
from PySide2.QtGui import QIcon
from PySide2.QtCore import QStringListModel


class Shell(QMainWindow):

    def __init__(self):  # constructor
        super().__init__()  # call the parent's constructor

        # Test data in a model
        self.users = ['User 1', 'User 2', 'User 3']
        self.lv_model = QStringListModel()
        self.lv_model.setStringList(self.users)

        # Create the main window content widget
        w = QWidget()
        
        # Setup the rest of the main window appearance
        self.setGeometry(300,300,640,480)
        self.setWindowTitle('PySide2 Listview Experiments')
        self.setWindowIcon(QIcon('assets/icons/moon_64x64.png'))

        # Create and set the main layout
        layout = QVBoxLayout()
        w.setLayout(layout) # Set the layout of the main window content widget
        self.setCentralWidget(w)        

        # Create and add components to the layout
        self.lv_label = QLabel('QListView with QStringListModel')
        layout.addWidget(self.lv_label)
        
        self.lv = QListView()
        self.lv.setSelectionMode(QListView.MultiSelection) # single selection is the default
        self.lv.setModel(self.lv_model)
        self.lv.selectionModel().selectionChanged.connect(self.item_selected)
        layout.addWidget(self.lv)
        
        self.button = QPushButton('Update model')
        self.button.clicked.connect(self.change_model)
        layout.addWidget(self.button)
                
        self.selected_label = QLabel('Selected item: none')
        layout.addWidget(self.selected_label)
        layout.addStretch(1)

        self.show() # display the UI

    def change_model(self):
        the_list = self.lv_model.stringList()
        the_list.append('Another User')
        self.lv_model.setStringList(the_list)

    def item_selected(self):
        # Get the current index (a QModelIndex object) from the QListView
        # From the index, get the data (a QVariant) that you can convert to a QString

        index = self.lv.currentIndex() # returns the primary QModelIndex
        indices = self.lv.selectedIndexes() # returns a list of QModelIndex

        selected_text = ''
        for i in indices:
            selected_text += i.data() + '\n' # use .data() to get the value from QModelIndex

        self.selected_label.setText(selected_text)

if __name__ == '__main__':

    # Required application object; sys.argv are command line arguments
    app = QApplication(sys.argv)
    shell = Shell() # create and show the main window

    sys.exit(app.exec_())
