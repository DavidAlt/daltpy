import sys
from PySide2.QtWidgets import (QApplication, QMainWindow, QWidget, QGridLayout, 
    QLineEdit, QPushButton, QLabel)
from PySide2.QtWidgets import QVBoxLayout
from PySide2.QtGui import QIcon


class Shell(QMainWindow):

    def __init__(self):  # constructor
        super().__init__()  # call the parent's constructor

        # Create the main window content widget
        w = QWidget()
        
        # Setup the rest of the main window appearance
        self.setGeometry(300,300,640,480)
        self.setWindowTitle('PySide2 Experiments')
        self.setWindowIcon(QIcon('assets/icons/moon_64x64.png'))

        # Create and set the layout
        layout = QVBoxLayout()
        w.setLayout(layout) # Set the layout of the main window content widget
        self.setCentralWidget(w)        

        # Create and add components to the layout
        self.edit = QLineEdit('Write your name:')
        layout.addWidget(self.edit)

        self.button = QPushButton('Show greeting')
        layout.addWidget(self.button)
        self.button.clicked.connect(self.greetings)

        self.label = QLabel()
        layout.addWidget(self.label)

        layout.addStretch(1) # expand the remaining space

        self.show() # display the UI

    def greetings(self):
        print(f'Hello {self.edit.text()}!')
        self.label.setText(self.edit.text())


if __name__ == '__main__':

    # Required application object; sys.argv are command line arguments
    app = QApplication(sys.argv)
    shell = Shell() # create and show the main window

    sys.exit(app.exec_())
