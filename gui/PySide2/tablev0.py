import sys
from PySide2 import QtWidgets, QtGui, QtCore
from PySide2.QtCore import (Qt, QAbstractTableModel, QModelIndex)
import logging

# LOGGING
logging.basicConfig(level=logging.CRITICAL, format='%(levelname)-9s: %(name)s : %(funcName)s() : %(message)s')
log = logging.getLogger('models')
log.setLevel(logging.DEBUG)

my_sites = [
    ['Hometown', -300, 68, -257, 'Village', 'Grass', 'mixed biomes'],
    ['Sandstonia', -765, 64, -236, 'Village', 'Desert', ''],
    ['Bilkage', -25, 44, -536, 'Cave', 'Swamp', 'A note']
]
# Hometown, -300, 68, -257, Village, Grass, 'mixed biomes'
# Sandstonia, -765, 64, -236, Village, Desert, ''

class MyModel(QtGui.QStandardItemModel):

    def dropMimeData(self, data, action, row, col, parent):
        """
        Always move the entire row, and don't allow column "shifting"
        """
        return super().dropMimeData(data, action, row, 0, parent)


class TableModel(QAbstractTableModel):
    # constants
    NAME = 0
    X = 1
    Z = 2
    Y = 3
    SITE_TYPE = 4
    BIOME = 5
    NOTES = 6

    def __init__(self, data_list=None, parent=None):
        super(TableModel, self).__init__(parent)

        if data_list is None:
            self.my_data = []
        else:
            self.my_data = data_list


    def rowCount(self, index=QModelIndex()):
        """ Returns the number of rows the model holds. """
        return len(self.my_data)


    def columnCount(self, index=QModelIndex()):
        """ Returns the number of columns the model holds. 
            'Name', 'X', 'Z', 'Y', 'Type', 'Biome', 'Notes' """
        return 7


    def data(self, index, role=Qt.DisplayRole):
        """ Depending on the index and role given, return data. If not 
            returning data, return None (PySide equivalent of QT's 
            "invalid QVariant").
        """
        if not index.isValid():
            return None

        if not 0 <= index.row() < len(self.my_data):
            return None

        if role == Qt.DisplayRole:
            # there should be able to slice this using column name rather than integer, but for now this works
            name = self.my_data[index.row()][TableModel.NAME]
            x_coord = self.my_data[index.row()][TableModel.X]
            z_coord = self.my_data[index.row()][TableModel.Z]
            y_coord = self.my_data[index.row()][TableModel.Y]
            site_type = self.my_data[index.row()][TableModel.SITE_TYPE]
            biome = self.my_data[index.row()][TableModel.BIOME]
            notes = self.my_data[index.row()][TableModel.NOTES]

            if index.column() == 0:
                return name
            elif index.column() == 1:
                return x_coord
            elif index.column() == 2:
                return z_coord
            elif index.column() == 3:
                return y_coord
            elif index.column() == 4:
                return site_type
            elif index.column() == 5:
                return biome
            elif index.column() == 6:
                return notes

        return None


    def headerData(self, section, orientation, role=Qt.DisplayRole):
        """ Set the headers to be displayed. """
        if role != Qt.DisplayRole:
            return None

        if orientation == Qt.Horizontal:
            if section == TableModel.NAME:
                return 'Name'
            elif section == TableModel.X:
                return 'X'
            elif section == TableModel.Z:
                return 'Z'
            elif section == TableModel.Y:
                return 'Y'
            elif section == TableModel.SITE_TYPE:
                return 'Type'
            elif section == TableModel.BIOME:
                return 'Biome'
            elif section == TableModel.NOTES:
                return 'Notes'
        
        return None


    def insertRows(self, position, rows=1, index=QModelIndex()):
        """ Insert a row into the model. """
        self.beginInsertRows(QModelIndex(), position, position + rows - 1)

        for row in range(rows):
            self.my_data.insert(position + row, {'name':'', 'x_coord':'', 'z_coord':'', 'y_coord':'', 'site_type':'', 'biome':'', 'notes':''})

        self.endInsertRows()
        return True


    def removeRows(self, position, rows=1, index=QModelIndex()):
        """ Remove a row from the model. """
        self.beginRemoveRows(QModelIndex(), position, position + rows - 1)

        del self.my_data[position:position+rows]

        self.endRemoveRows()
        return True


    def setData(self, index, value, role=Qt.EditRole):
        """ Adjust the data (set it to <value>) depending on the given 
            index and role. 
        """
        if role != Qt.EditRole:
            return False

        if index.isValid() and 0 <= index.row() < len(self.my_data):
            row = self.my_data[index.row()]
            if index.column() == TableModel.NAME:
                row[TableModel.NAME] = value
            elif index.column() == TableModel.X:
                row[TableModel.X] = value
            elif index.column() == TableModel.Z:
                row[TableModel.Z] = value
            elif index.column() == TableModel.Y:
                row[TableModel.Y] = value
            elif index.column() == TableModel.SITE_TYPE:
                row[TableModel.SITE_TYPE] = value
            elif index.column() == TableModel.BIOME:
                row[TableModel.BIOME] = value
            elif index.column() == TableModel.NOTES:
                row[TableModel.NOTES] = value
            else:
                return False
            
            self.dataChanged.emit(index, index)
            return True

        return False


    def flags(self, index):
        """ Set the item flags at the given index. Seems like we're 
            implementing this function just to see how it's done, as we 
            manually adjust each tableView to have NoEditTriggers.
        """
        if not index.isValid():
            return Qt.ItemIsEnabled
        return Qt.ItemFlags(QAbstractTableModel.flags(self, index) |
                            Qt.ItemIsEditable)    

    
    def dropMimeData(self, data, action, row, col, parent):
        """
        Always move the entire row, and don't allow column "shifting"
        """
        if(row == -1):
            row = self.rowCount()

        return super().dropMimeData(data, action, row, 0, parent)



class MyStyle(QtWidgets.QProxyStyle):

    def drawPrimitive(self, element, option, painter, widget=None):
        """
        Draw a line across the entire row rather than just the column
        we're hovering over.  This may not always work depending on global
        style - for instance I think it won't work on OSX.
        """
        if element == self.PE_IndicatorItemViewItemDrop and not option.rect.isNull():
            option_new = QtWidgets.QStyleOption(option)
            option_new.rect.setLeft(0)
            if widget:
                option_new.rect.setRight(widget.width())
            option = option_new
        super().drawPrimitive(element, option, painter, widget)



class MyTableView(QtWidgets.QTableView):

    def __init__(self, parent):
        super().__init__(parent)
        #self.verticalHeader().hide()
        #self.horizontalHeader().hide()
        self.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)
        
        # This is invalid syntax
        #self.horizontalHeader().setMaximumSectionSize(10))
        
        self.setSelectionBehavior(self.SelectRows)
        self.setSelectionMode(self.SingleSelection)
        self.setShowGrid(False)
        #self.setDefaultDropAction(self.MoveAction) #untested
        self.setDragDropMode(self.InternalMove)
        self.setDragDropOverwriteMode(False)

        # Set our custom style - this draws the drop indicator across the whole row
        self.setStyle(MyStyle())

        # Set our custom model - this prevents row "shifting"
        self.model = TableModel(my_sites)
        self.setModel(self.model)

        

class MyTableView2(QtWidgets.QTableView):

    def __init__(self, parent):
        super().__init__(parent)
        #self.verticalHeader().hide()
        #self.horizontalHeader().hide()
        self.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)
        
        # This is invalid syntax
        #self.horizontalHeader().setMaximumSectionSize(10))
        
        self.setSelectionBehavior(self.SelectRows)
        self.setSelectionMode(self.SingleSelection)
        self.setShowGrid(False)
        self.setDragDropMode(self.InternalMove)
        self.setDragDropOverwriteMode(False)

        # Set our custom style - this draws the drop indicator across the whole row
        self.setStyle(MyStyle())

        # Set our custom model - this prevents row "shifting"
        #self.model = TableModel(my_sites)
        self.model = MyModel()
        self.model.setHorizontalHeaderLabels(['Name', 'X', 'Z', 'Y', 'Type', 'Biome', 'Notes'])
        self.setModel(self.model)

        for item in my_sites:
            name = QtGui.QStandardItem(item[0])
            name.setDropEnabled(False)
            x = QtGui.QStandardItem(str(item[1]))
            x.setDropEnabled(False)
            z = QtGui.QStandardItem(str(item[2]))
            z.setDropEnabled(False)
            y = QtGui.QStandardItem(str(item[3]))
            y.setDropEnabled(False)
            site_type = QtGui.QStandardItem(item[4])
            site_type.setDropEnabled(False)
            biome = QtGui.QStandardItem(item[5])
            biome.setDropEnabled(False)
            notes = QtGui.QStandardItem(item[6])
            notes.setDropEnabled(False)

            self.model.appendRow([name, x, z, y, site_type, biome, notes])


class Testing(QtWidgets.QMainWindow):

    def __init__(self):
        super().__init__()

        # Main widget
        w = QtWidgets.QWidget()
        l = QtWidgets.QVBoxLayout()
        w.setLayout(l)
        self.setCentralWidget(w)

        
        # TableView
        l.addWidget(MyTableView(self))

        # spacer
        l.addWidget(QtWidgets.QLabel('middle'), 1)

        # TableView
        l.addWidget(MyTableView2(self))

        # A bit of window housekeeping
        self.resize(700, 400)
        self.setWindowTitle('Testing')
        self.show()

if __name__ == '__main__':

    app = QtWidgets.QApplication([])
    test = Testing()
    sys.exit(app.exec_())