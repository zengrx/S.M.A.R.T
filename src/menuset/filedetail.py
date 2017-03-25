#coding=utf-8

from PyQt4 import QtGui, QtCore, Qt
import sys, os, time
sys.path.append("..")
from UILib.detail import Ui_Dialog
from advanceoperate.detailthread import FileDetail, PEFileInfo

reload(sys)
sys.setdefaultencoding("utf-8")

class Dialog(QtGui.QDialog):
    # detailSignal = QtCore.pyqtSignal(str)

    def __init__(self, parent=None):
        QtGui.QWidget.__init__(self, parent)
        self.ui = Ui_Dialog()
        self.ui.setupUi(self)

        self.widget   = self.ui.listWidget
        self.wdiget2  = self.ui.listWidget_2
        self.table    = self.ui.tableWidget
        self.filename = ""
        self.filetype = ""

    def getFileName(self, filename):
        self.filename = filename
        self.detail   = FileDetail(self.filename) # 基本信息
        self.section  = PEFileInfo(self.filename) # 节信息
        self.detail.finishSignal.connect(self.showBaseInfo)
        self.detail.start()

    def showBaseInfo(self, msg):
        self.widget.clear() # 清空list内容
        self.table.clearContents() # 清空table内容保留列名
        for n in msg:
            if "PE32" in n:
                self.section.finishSignal.connect(self.showSetInfo)
                self.section.start()
            self.widget.addItem(n)

    def showAdvInfo(self, msg):
        print "aadfasf"

    '''
    在tablewidget中显示PE节信息
    '''
    def showSetInfo(self, msg):
        self.table.setRowCount(msg[0])
        for i in range(msg[0]):
            for j in range(5):
                item = str(msg[i * 5 + j + 1])
                self.table.setItem(i, j, QtGui.QTableWidgetItem(item))
        self.table.horizontalHeader().setResizeMode(QtGui.QHeaderView.Stretch) #自适应宽度
        print "updated tablewidget"


if __name__ == "__main__":

    window = QtGui.QApplication(sys.argv)
    thiswindow = Dialog()
    thiswindow.show()

    sys.exit(window.exec_())