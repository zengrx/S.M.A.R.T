#coding=utf-8

from PyQt4 import QtGui, QtCore, Qt
import sys, os
from PIL import Image
sys.path.append("..")
from UILib.author import Ui_Dialog

class Dialog(QtGui.QDialog):

    def __init__(self, parent=None):
        QtGui.QWidget.__init__(self, parent)
        self.ui = Ui_Dialog()
        self.ui.setupUi(self)

        self.setImg()

    def setImg(self):
        img = str(".\UILib\icons\pk.png")
        # print im
        msg = ''
        image = QtGui.QImage()
        if image.load(img):
            self.ui.label.setPixmap(QtGui.QPixmap.fromImage(image))
            self.ui.label_2.setText(u"  bugreport@ ")
            self.ui.label_3.setText(u"  zengrx1995@gmail.com; zengrx1995@163.com; zengrx1995@outlook.com")
        

if __name__ == "__main__":

    window = QtGui.QApplication(sys.argv)
    thiswindow = Dialog()
    thiswindow.show()

    sys.exit(window.exec_())