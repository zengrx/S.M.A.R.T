#coding=utf-8

from PyQt4 import QtGui, QtCore, Qt
import sys, os, time
sys.path.append("..")
from UILib.setting import Ui_Dialog
from publicfunc.updatedata import UpdateData
from globalset import FlagSet

reload(sys)
sys.setdefaultencoding("utf-8")

class Dialog(QtGui.QDialog):

    def __init__(self, parent=None):
        QtGui.QWidget.__init__(self, parent)
        self.ui = Ui_Dialog()
        self.ui.setupUi(self)

        self.ui.pushButton_2.clicked.connect(self.updateyara)

    def updateyara(self):
        update = QtGui.QMessageBox()
        recv = update.question(self, u"更新", u"更新规则库时会停止扫描，是否更新", update.Yes, update.No)
        if recv == update.Yes:
            FlagSet.scanstopflag = 0
            U = UpdateData()
            U.updateYaraData()

if __name__ == "__main__":

    window = QtGui.QApplication(sys.argv)
    thiswindow = Dialog()
    thiswindow.show()

    sys.exit(window.exec_())