import sys
from PySide2.QtWidgets import QApplication
from PySide2.QtQuick import QQuickView
from PySide2.QtCore import QUrl


if __name__ == '__main__':
    
    app = QApplication([]) # can use sys.argv in place of [] for command line arguments
    view = QQuickView()
    url = QUrl('basic_qml.qml')
    
    view.setSource(url)
    view.setResizeMode(QQuickView.SizeRootObjectToView) # makes the view scale w/ the window
    view.show()

    sys.exit(app.exec_()) # run the app until closed