#coding=utf-8

from PyQt4 import QtGui, QtCore, Qt
import sys, os, time
sys.path.append("..")
from UILib.setting import Ui_Dialog

reload(sys)
sys.setdefaultencoding("utf-8")

class Dialog(QtGui.QDialog):

    def __init__(self, parent=None):
        QtGui.QWidget.__init__(self, parent)
        self.ui = Ui_Dialog()
        self.ui.setupUi(self)

if __name__ == "__main__":

    window = QtGui.QApplication(sys.argv)
    thiswindow = Dialog()
    thiswindow.show()

    sys.exit(window.exec_())