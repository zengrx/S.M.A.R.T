#coding=utf-8

from PyQt4 import QtGui, QtCore, Qt
import os, sys, time
import numpy, scipy, array
from PIL import Image
sys.path.append("..")
from UILib.malimg import Ui_Dialog

reload(sys)
sys.setdefaultencoding("utf-8")

class Dialog(QtGui.QDialog):

    def __init__(self, parent=None):
        QtGui.QWidget.__init__(self, parent)
        self.ui = Ui_Dialog()
        self.ui.setupUi(self)

        self.imglb = self.ui.LB_Malimg

        self.filename = ''

    def getFileName(self, filename):
        self.filename = str(filename)#.encode('cp936')
        # self.test()
        self.convertBin2Img(self.filename)

    def test(self):
        img = str(".\\cache\\aaaaa.png")
        image = QtGui.QImage()
        if image.load(img):
            # image.scaled(64, 64)
            # 设置图像适配
            self.imglb.setScaledContents(True)
            self.imglb.setPixmap(QtGui.QPixmap.fromImage(image))
        else:
            print u"导入图像失败"

    def convertBin2Img(self, filename):
        f = open(filename,'rb')
        ln = os.path.getsize(filename) # length of file in bytes
        width = 512
        rem = ln % width

        a = array.array("B") # uint8 array
        a.fromfile(f,ln - rem)
        f.close()

        g = numpy.reshape(a,(len(a)/width,width))
        g = numpy.uint8(g)
        scipy.misc.imsave('.\\cache\\aaaaa.png', g) # save the image
        print "save img"
        self.test()