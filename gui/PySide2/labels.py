import sys
from PySide2.QtWidgets import QApplication, QLabel


if __name__ == '__main__':
    
    # Required application object; sys.argv are command line arguments
    app = QApplication(sys.argv)
    
    # build the gui
    #label = QLabel('Hello World') # plain text
    #label = QLabel("<font color=red size=40>Hello World!</font>") # html
    label = QLabel('<a href="https://web-satx02.mail.mil/owa" target="_blank">Defense Enterprise Email</a>') # link copyable but not clickable
    
    label.show()
    
    sys.exit(app.exec_()) # run the app until closed