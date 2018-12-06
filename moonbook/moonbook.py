"""
moonbook shell
Author: David Alt (https://github.com/DavidAlt)
"""

import sys
from PyQt5.QtWidgets import (
    QWidget, QMainWindow, QApplication) 
from PyQt5.QtGui import QIcon

class Shell(QMainWindow):

    def __init__(self):  # constructor
        super().__init__()  # call the parent's constructor
        
   
        # Create the main window content widget
        w = QWidget()
        #w.setLayout(layout) # Set the layout of the main window content widget
        self.setCentralWidget(w)        
        
        # Setup the rest of the main window appearance
        self.setGeometry(300,300,640,480)
        self.setWindowTitle('moonbook')
        self.setWindowIcon(QIcon('assets/icons/moon_64x64.png'))

        self.show()


if __name__ == '__main__':
    
    # Required application object; sys.argv are command line arguments
    app = QApplication(sys.argv)
    shell = Shell() # create and show the main window
    
    sys.exit(app.exec_())
