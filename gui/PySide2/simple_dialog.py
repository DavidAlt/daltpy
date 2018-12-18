import sys
from PySide2.QtWidgets import QApplication, QDialog, QLineEdit, QPushButton
from PySide2.QtWidgets import QVBoxLayout


class Form(QDialog):

    def __init__(self, parent=None):
        super(Form, self).__init__(parent)
        self.setWindowTitle('Simple Dialog')

        # setup widgets
        self.edit = QLineEdit('Write your name:')
        self.button = QPushButton('Show greeting')
        self.button.clicked.connect(self.greetings)

        # setup layout
        layout = QVBoxLayout()
        layout.addWidget(self.edit)
        layout.addWidget(self.button)
        self.setLayout(layout)


    def greetings(self):
        print(f'Hello {self.edit.text()}!')
    

if __name__ == '__main__':
    
    app = QApplication([]) # can use sys.argv in place of [] for command line arguments
    
    form = Form()
    form.show()

    sys.exit(app.exec_()) # run the app until closed