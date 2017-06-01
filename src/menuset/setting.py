#coding=utf-8

from PyQt4 import QtGui, QtCore, Qt
import sys, os, time
sys.path.append("..")
from UILib.setting2 import Ui_Dialog
from globalset import StaticValue

reload(sys)
sys.setdefaultencoding("utf-8")

class Dialog(QtGui.QDialog):

    def __init__(self, parent=None):
        QtGui.QWidget.__init__(self, parent)
        self.ui = Ui_Dialog()
        self.ui.setupUi(self)

        self.list  = self.ui.listWidget
        self.stack = self.ui.stackedWidget

        self.extension = []

        exts = Qt.QRegExp('[\da-zA-Z;]*')
        exts = Qt.QRegExpValidator(exts)
        # exts = Qt.QValidator('[\da-zA-Z;]*')
        self.ui.LE_FileExt.setValidator(exts)

        self.list.currentRowChanged.connect(self.stack.setCurrentIndex)
        self.stack.currentChanged.connect(self.fadeInWidget)
        self.ui.PB_Yes.clicked.connect(self.saveSetChange)
        self.ui.PB_Apply.clicked.connect(self.applySetChange)
        self.ui.PB_Cancel.clicked.connect(self.close)

    def fadeInWidget(self, index):
        self.faderWidget = FaderWidget(self.stack.widget(index))
        self.faderWidget.start()

    def saveSetChange(self):
        print u"save setting changes"
        print self.ui.LE_FileExt.text()
        extname = self.ui.LE_FileExt.text()
        ext = list(str(extname).split(';'))
        print ext
        while '' in ext:
            ext.remove('')
        StaticValue.adextension = ext

    def applySetChange(self):
        pass

'''
淡入淡出效果
'''
class FaderWidget(QtGui.QWidget):
    def __init__(self, parent=None):
        super(FaderWidget, self).__init__(parent)

        if parent:
            self.startColor = parent.palette().window().color()
        else:
            self.startColor = Qt.Qt.White

        self.currentAlpha = 0
        self.duration = 1000

        self.timer = QtCore.QTimer(self)  
        self.connect(self.timer, QtCore.SIGNAL("timeout()"), self.update)  
        self.setAttribute(Qt.Qt.WA_DeleteOnClose)
        self.resize(parent.size())
  
    def start(self):
        self.currentAlpha = 255
        self.timer.start(100)
        self.show()

    def paintEvent(self, event):
        semiTransparentColor = self.startColor  
        semiTransparentColor.setAlpha(self.currentAlpha)  
        painter = QtGui.QPainter(self)
        painter.fillRect(self.rect(), semiTransparentColor)
        self.currentAlpha -= (255*self.timer.interval() / self.duration)

        if self.currentAlpha <= 0:
            self.timer.stop()
            self.close()

if __name__ == "__main__":

    window = QtGui.QApplication(sys.argv)
    thiswindow = Dialog()
    thiswindow.show()

    sys.exit(window.exec_())
