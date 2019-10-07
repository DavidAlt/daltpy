# This version implements 
#   basic UI for adding records
#   moves view settings to view constructor
#   custom sorting proxy model so that numbers are sorted properly
# There is VERY little data validation/error checking, especially when
# casting to int

import operator
import sys
from PySide2.QtCore import Qt, QAbstractTableModel, QModelIndex, QSortFilterProxyModel
from PySide2 import QtWidgets
from PySide2.QtWidgets import QApplication, QWidget, QTableView, QVBoxLayout, QHBoxLayout, QAbstractItemView, QItemDelegate, QFrame, QLineEdit, QPushButton

# LOGGING
import logging
logging.basicConfig(level=logging.CRITICAL, format='%(levelname)-9s: %(name)s : %(funcName)s() : %(message)s')
log = logging.getLogger('models')
log.setLevel(logging.DEBUG)


class MyDelegate(QItemDelegate):
    ''' This class creates an in-place editor in the table view
        that won't delete the original value automatically. 
    '''
    def createEditor(self, parent, option, index):
        if index.isValid():
            return super(MyDelegate, self).createEditor(parent, option, index)
        return None

    def setEditorData(self, editor, index):
        if index.isValid():
            # Gets display text if edit data hasn't been set
            text = index.data(Qt.EditRole) or index.data(Qt.DisplayRole)
            editor.setText(text)


class MySortingProxyModel(QSortFilterProxyModel):
    def lessThan(self, left, right):
        col = left.column()
        data_left = left.data()
        data_right = right.data()

        if col in range(1,4): # x, z, y coordinate columns
            data_left = int(data_left)
            data_right = int(data_right)
        
        return data_left < data_right


class MyTableModel(QAbstractTableModel):
    def __init__(self, parent, my_data, header, *args):
        QAbstractTableModel.__init__(self, parent, *args)
        self.my_data = my_data
        self.header = header

    def rowCount(self, parent):
        return len(self.my_data)

    def columnCount(self, parent):
        return len(self.my_data[0])

    def data(self, index, role=Qt.DisplayRole):
        ''' Determines how data is displayed in the table. '''
        if not index.isValid():
            return None        
        if role == Qt.DisplayRole:
            return str(self.my_data[index.row()][index.column()])

    def headerData(self, section, orientation, role=Qt.DisplayRole):
        '''Determines how header data is displayed in the table'''
        # Column headers
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            return self.header[section]
        # Row headers    
        if orientation == Qt.Vertical and role == Qt.DisplayRole:
            return section
        return None

    def setData(self, index, value, role=Qt.EditRole):
        ''' Required for updating the model when the view is edited. '''
        if role != Qt.EditRole:
            return False

        if index.isValid():
            row = index.row() #self.my_data[index.row()]
            col = index.column()
            # If you have multiple data types, detect column and cast them
            if col in range(1, 4): # (x/z/y coordinate)
                try:
                    self.my_data[row][col] = int(value)
                    log.info(f'{value} is a valid integer.')
                except: # don't change the value
                    log.warning(f'{value} is not a valid integer')
            else:
                self.my_data[row][col] = value
            
            self.dataChanged.emit(index, index)
            return True


    def insertRows(self, row_position, new_data, row_count=1, parent=QModelIndex(), ):
        """ Inserts an empty row into the model. 
            row_position: if 0, rows are prepended to any existing rows
            row_count: # of rows to insert
            parent: if parent has no children, inserts a single column with {row_count} rows
        """
        # parent index, start position, end position for new rows
        self.beginInsertRows(parent, row_position, row_position + row_count - 1)

        for row in range(row_count):
            self.my_data.insert(row_position + row, new_data)

        self.endInsertRows()
        return True


    def removeRows(self, row_position, row_count=1, parent=QModelIndex()):
        """ Remove a row from the model. """
        log.info(f'position: {type(row_position)}, count: {type(row_count)}, parent: {type(parent)}')
        self.beginRemoveRows(parent, row_position, row_position + row_count - 1)

        del self.my_data[row_position:row_position+row_count]

        self.endRemoveRows()
        return True


    def flags(self, index):
        # Should return current flags plus the following three:
        return Qt.ItemIsEnabled | Qt.ItemIsSelectable | Qt.ItemIsEditable
        '''if not index.isValid():
            return Qt.ItemIsEnabled
        return Qt.ItemFlags(QAbstractTableModel.flags(self, index) | Qt.ItemIsEditable)'''


class MyTableView(QTableView):
    def __init__(self):
        super().__init__()
        
        # Setup the delegate (in-place editor when double-clicking)
        delegate = MyDelegate()
        self.setItemDelegate(delegate)
        
        # Hide unwanted headers and gridlines
        #self.verticalHeader().hide() # row labels
        #self.horizontalHeader().hide() # column labels
        self.setShowGrid(False) # hide gridlines
        
        # Select a single row at a time
        self.setSelectionBehavior(QTableView.SelectRows)
        self.setSelectionMode(QTableView.SingleSelection)
        
        # Enable sorting
        self.setSortingEnabled(True)

        # Drag and drop reordering using header labels
        self.verticalHeader().setSectionsMovable(True)
        self.verticalHeader().setDragEnabled(True)
        self.verticalHeader().setDragDropMode(QAbstractItemView.InternalMove)
        #self.horizontalHeader().setSectionsMovable(True)
        #self.horizontalHeader().setDragEnabled(True)
        #self.horizontalHeader().setDragDropMode(QAbstractItemView.InternalMove)

        # Column sizing
        self.horizontalHeader().setStretchLastSection(True) # last column stretches


    def resize_cols(self):
        self.resizeColumnsToContents() # set column width to fit contents
        


class TestApp(QWidget):
    def __init__(self, data_list, header, *args):
        QWidget.__init__(self, *args)

        # setGeometry(x_pos, y_pos, width, height)
        self.setGeometry(300, 200, 570, 450)
        self.setWindowTitle('Click on column title to sort')
        
        # Setup the models and view
        self.tmodel = MyTableModel(self, data_list, header) # actual model
        self.pmodel = MySortingProxyModel() # proxy model for sorting
        self.pmodel.setSourceModel(self.tmodel) # assign actual model to the proxy
        
        self.tview = MyTableView()
        self.tview.setModel(self.pmodel) # assign the proxy to the view
        self.tview.resizeColumnsToContents() # set col widths based on model data
        self.tview.model().dataChanged.connect(self.tview.resize_cols) # resize cols when data changes

        # Setup the entry fields
        entry_frame = QFrame(self)
        entry_layout = QHBoxLayout(entry_frame)
        name_edit = QLineEdit(entry_frame)
        x_edit = QLineEdit(entry_frame)
        z_edit = QLineEdit(entry_frame)
        y_edit = QLineEdit(entry_frame)
        type_edit = QLineEdit(entry_frame)
        biome_edit = QLineEdit(entry_frame)
        notes_edit = QLineEdit(entry_frame)
        add_btn = QPushButton('Add')
        del_btn = QPushButton('Remove')
        
        self.entry_fields = []
        self.entry_fields.append(name_edit)
        self.entry_fields.append(x_edit)
        self.entry_fields.append(z_edit)
        self.entry_fields.append(y_edit)
        self.entry_fields.append(type_edit)
        self.entry_fields.append(biome_edit)
        self.entry_fields.append(notes_edit)

        add_btn.clicked.connect(self.on_add_clicked)
        del_btn.clicked.connect(self.on_del_clicked)
        
        entry_layout.addWidget(name_edit)
        entry_layout.addWidget(x_edit)
        entry_layout.addWidget(z_edit)
        entry_layout.addWidget(y_edit)
        entry_layout.addWidget(type_edit)
        entry_layout.addWidget(biome_edit)
        entry_layout.addWidget(notes_edit)
        entry_layout.addWidget(add_btn)
        entry_layout.addWidget(del_btn)
        
        # Setup the main layout
        layout = QVBoxLayout(self)
        layout.addWidget(entry_frame)
        layout.addWidget(self.tview)
        self.setLayout(layout)

    def on_add_clicked(self):
        field_values = []
        idx = 0
        for edit in self.entry_fields:
            if idx in range(1,4):
                try:
                    field_values.append(int(edit.text()))
                except:
                    field_values.append(edit.text())
            else:
                field_values.append(edit.text())
            idx += 1
        log.info(field_values)
        self.tmodel.insertRows(len(self.tmodel.my_data), field_values)


    def on_del_clicked(self):
        # get the selected row index in the VIEW and remove from the PROXY
        # if you remove from the model directly, it can't account for the
        # sorting properly and will remove the wrong row
        selected = self.tview.selectionModel().selectedRows()[0].row()
        self.pmodel.removeRows(selected, 1)


# Dummy data
header = ['Name', 'X', 'Z', 'Y', 'Type', 'Biome', 'Notes']

data_list = [
    ['Hometown', -50, 0, 50, 'Village', 'Plains', 'no notes'],
    ['Pyramid', -25, 10, 250, 'Temple', 'Desert', ''],
    ['Shrine', 40, -20, 800, 'Temple', 'Jungle', 'creepers']
]

if __name__ == '__main__':
    app = QApplication([])
    win = TestApp(data_list, header)
    win.show()
    sys.exit(app.exec_())