# -*- coding: utf-8 -*-
# Author:  David Alt, 3/4/19
# Status:  unfinished

import sys
from PySide2.QtUiTools import QUiLoader
from PySide2.QtWidgets import QApplication, QMainWindow, QFileDialog
from PySide2.QtGui import QIcon
from PySide2.QtCore import QStringListModel

class Window(QMainWindow):
    def __init__(self):
        super().__init__()

        # load the ui file
        self.ui = QUiLoader().load('listview_manip.ui')

        # connect signals/slots
        self.ui.load_btn.clicked.connect(self.on_load_btn_click)

        # you can access form objects directly ...
        # self.ui.<name_of_object>.<some_method>()

        # or search for them ...
        # self.found_object = self.ui.findChild(QPlainTextEdit, 'plainTextEdit')

        # or setup shorter references
        #self.my_text = self.ui.plainTextEdit

        # Test data in a model
        self.users = ['User 1', 'User 2', 'User 3']
        self.lv_model = QStringListModel()
        self.lv_model.setStringList(self.users)

        # 

        # Attach the model and selection events
        self.ui.file_view.setModel(self.lv_model)
        self.ui.file_view.selectionModel().selectionChanged.connect(self.item_selected)


    def item_selected(self):
        index = self.ui.file_view.currentIndex() # returns the primary QModelIndex
        self.ui.test_lbl.setText(index.data())
    
    
    def on_load_btn_click(self):
        print('click!')
        file_name = self.load_file()
        self.ui.test_lbl.setText(file_name)


    def load_file(self):
        file_name = QFileDialog.getOpenFileName(self)
            #tr('Open AHLTA template'), '', tr('AHLTA template (*.txt)'))
        return file_name


if __name__ == "__main__":
    app = QApplication(sys.argv)

    main_window = Window()
    main_window.ui.show() # you have to show ui, not the window itself

    sys.exit(app.exec_())