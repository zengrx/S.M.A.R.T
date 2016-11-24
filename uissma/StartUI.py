#coding=utf-8

from PyQt4 import QtGui, QtCore
import sys
from SSMA_UI import Ui_MainWindow

class MainWindow(QtGui.QMainWindow):
    def __init__(self, parent=None):
	QtGui.QWidget.__init__(self, parent)
	self.ui = Ui_MainWindow()
    	self.ui.setupUi(self)



if __name__ == "__main__":

    
    app = QtGui.QApplication(sys.argv)
    myapp = MainWindow()
    
    myapp.show()
    
    sys.exit(app.exec_())
