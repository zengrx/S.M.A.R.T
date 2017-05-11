#coding=utf-8

from PyQt4 import QtGui, QtCore, Qt
import os, sys, time
sys.path.append("..")
from UILib.whitelist import Ui_Dialog
from globalset import FilePath

reload(sys)
sys.setdefaultencoding("utf-8")

class Dialog(QtGui.QDialog):

    def __init__(self, parent=None):
        QtGui.QWidget.__init__(self, parent)
        self.ui = Ui_Dialog()
        self.ui.setupUi(self)

        self.text = self.ui.textBrowser
        self.ok   = self.ui.PB_OK
        self.apy  = self.ui.PB_Apply
        self.name = FilePath.whitelist

        self.getWhiteListInfo()
        self.ok.clicked.connect(self.saveWhiteListChange)
        self.apy.clicked.connect(self.quitWhiteListSet)
        self.apy.clicked.connect(self.close)

    '''
    获取白名单内容
    '''
    def getWhiteListInfo(self):
        f = open(self.name, "r")
        f.readline()
        for line in f:
            msg = str(line).split('\n')[0]
            self.text.append(unicode(str(msg)))

    def saveWhiteListChange(self):
        try:
            ftmp = QtCore.QFile(self.name)
            ftmp.open(QtCore.QIODevice.WriteOnly)
            stream = QtCore.QTextStream(ftmp)
            slog = self.text.toPlainText()
            stream << slog
            self.ok.setEnabled(False)
        except IOError, e:
            print e.args[0]
            
    def quitWhiteListSet(self):
        f = open(self.name)
        f.readline()
        for line in f:
            FilePath.whitefile.append(str(line).split('\n')[0])
        self.ok.setEnabled(True)

if __name__ == "__main__":

    window = QtGui.QApplication(sys.argv)
    thiswindow = Dialog()
    thiswindow.show()

    sys.exit(window.exec_())