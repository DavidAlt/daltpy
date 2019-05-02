# -*- coding: utf-8 -*-
# Author:  David Alt, 2/25/19
# Status:  in progress

import sys
from PySide2.QtWidgets import (QApplication, QMainWindow, QWidget, QPushButton, QLabel, QListView)
from PySide2.QtWidgets import QVBoxLayout, QHBoxLayout, QDesktopWidget
from PySide2.QtGui import QIcon
from PySide2.QtCore import QStringListModel
#from PySide2 import QDesktopWidget


class Shell(QMainWindow):

    def __init__(self):  # constructor
        super().__init__()  # call the parent's constructor

        # Create the main window content widget
        w = QWidget()
        
        # Setup the rest of the main window appearance
        self.setGeometry(300,300,1600,800)
        self.setWindowTitle('PySide2 Center the Main Window')
        self.setWindowIcon(QIcon('assets/icons/moon_64x64.png'))

        # Create and set the main layout
        layout = QVBoxLayout()
        w.setLayout(layout) # Set the layout of the main window content widget
        self.setCentralWidget(w)        

        self.center()
        self.show() # display the UI


    def center(self):
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

if __name__ == '__main__':

    # Required application object; sys.argv are command line arguments
    app = QApplication(sys.argv)
    shell = Shell() # create and show the main window

    sys.exit(app.exec_())
