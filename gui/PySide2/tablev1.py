import operator
import sys
from PySide2.QtCore import Qt, QAbstractTableModel, QModelIndex, QSortFilterProxyModel
from PySide2.QtWidgets import QApplication, QWidget, QTableView, QVBoxLayout, QAbstractItemView, QItemDelegate

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


'''class ProxyModel(QSortFilterProxyModel):
    def filterAccepts'''


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





    def sort(self, col, order):
        '''Sorts table by given column number col'''
        self.layoutAboutToBeChanged.emit()
        self.my_data = sorted(self.my_data, key=operator.itemgetter(col))
        if order == Qt.DescendingOrder:
            self.my_data.reverse()
        self.layoutChanged.emit()


    def flags(self, index):
        # Should return current flags plus the following three:
        return Qt.ItemIsEnabled | Qt.ItemIsSelectable | Qt.ItemIsEditable
        '''if not index.isValid():
            return Qt.ItemIsEnabled
        return Qt.ItemFlags(QAbstractTableModel.flags(self, index) | Qt.ItemIsEditable)'''


    def dropMimeData(self, data, action, row, col, parent):
        # Always move the entire row, and don't allow column shifting
        return super().dropMimeData(data, action, row, 0, parent)


class TestApp(QWidget):
    def __init__(self, data_list, header, *args):
        QWidget.__init__(self, *args)

        # setGeometry(x_pos, y_pos, width, height)
        self.setGeometry(300, 200, 570, 450)
        self.setWindowTitle('Click on column title to sort')
        
        # Setup the model and view
        '''tmodel = MyTableModel(self, data_list, header)
        tview = QTableView()
        tview.setModel(tmodel)
        delegate = MyDelegate()
        tview.setItemDelegate(delegate)'''
        
        # Setup the proxy model for sorting and filtering
        tmodel = MyTableModel(self, data_list, header)
        pmodel = QSortFilterProxyModel()
        pmodel.setSourceModel(tmodel)
        
        tview = QTableView()
        tview.setModel(pmodel)
        delegate = MyDelegate()
        tview.setItemDelegate(delegate)
        
        # TableView properties
        tview.resizeColumnsToContents() # set column width to fit contents
        tview.setShowGrid(False) # hide gridlines
        #tview.verticalHeader().hide() # row labels
        #tview.horizontalHeader().hide() # column labels
        
        # Select a single row at a time
        tview.setSelectionBehavior(QTableView.SelectRows)
        tview.setSelectionMode(QTableView.SingleSelection)
        
        # Enable sorting
        tview.setSortingEnabled(True)

        # Drag and drop reordering using header labels
        '''tview.verticalHeader().setSectionsMovable(True)
        tview.verticalHeader().setDragEnabled(True)
        tview.verticalHeader().setDragDropMode(QAbstractItemView.InternalMove)

        tview.horizontalHeader().setSectionsMovable(True)
        tview.horizontalHeader().setDragEnabled(True)
        tview.horizontalHeader().setDragDropMode(QAbstractItemView.InternalMove)'''

        # Drag and drop reordering using rows
        tview.setDragEnabled(True)
        tview.setAcceptDrops(True)
        tview.setDragDropMode(QTableView.InternalMove)
        tview.setDragDropOverwriteMode(False)


        layout = QVBoxLayout(self)
        layout.addWidget(tview)
        self.setLayout(layout)


# the solvent data ...
header = ['Place', 'X', 'Z', 'Y', 'Type', 'Biome', 'Notes']

# use numbers for numeric data to sort properly
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