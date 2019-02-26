import sys
from PySide2.QtWidgets import QApplication, QPushButton
from PySide2.QtCore import Slot

@Slot()
def on_btn_click():
    print('Button clicked')
    #print(sender())
    #print(self.ui.plainTextEdit.toPlainText())
    #print(self.my_text.toPlainText())

if __name__ == '__main__':
    
    app = QApplication([]) # can use sys.argv in place of [] for command line arguments
    
    button = QPushButton('Click me')
    button.clicked.connect(on_btn_click)
    button.show()
    

    sys.exit(app.exec_()) # run the app until closed