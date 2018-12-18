# This uses basic_ui.ui generated in QtDesigner, which has a 
#   pushButton and plainTextEdit

import sys
from PySide2.QtUiTools import QUiLoader
from PySide2.QtWidgets import QApplication, QMainWindow


class Window(QMainWindow):
    def __init__(self):
        super().__init__()

        # load the ui file
        self.ui = QUiLoader().load('basic_ui.ui')

        # connect signals/slots
        self.ui.pushButton.clicked.connect(self.on_btn_click)

        # you can access form objects directly ...
        # self.ui.<name_of_object>.<some_method>()

        # or search for them ...
        # self.found_object = self.ui.findChild(QPlainTextEdit, 'plainTextEdit')

        # or setup shorter references
        self.my_text = self.ui.plainTextEdit
        

    def on_btn_click(self):
        print('click!')
        print(self.ui.plainTextEdit.toPlainText())
        print(self.my_text.toPlainText())


if __name__ == "__main__":
    app = QApplication(sys.argv)

    main_window = Window()

    main_window.ui.show() # you have to show ui, not the window itself

    sys.exit(app.exec_())