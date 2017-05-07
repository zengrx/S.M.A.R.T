#coding=utf-8

from PyQt4 import QtGui, QtCore, Qt
import os, sys, time
import numpy, scipy, array
from PIL import Image
sys.path.append("..")
from UILib.malimg import Ui_Dialog
from advanceoperate.malimgthread import MalwareImageClass

reload(sys)
sys.setdefaultencoding("utf-8")

class Dialog(QtGui.QDialog):

    def __init__(self, parent=None):
        QtGui.QWidget.__init__(self, parent)
        self.ui = Ui_Dialog()
        self.ui.setupUi(self)

        self.imglb = self.ui.LB_Malimg

        self.filename = ''
        self.classname = ''

    def getFileName(self, filename):
        self.filename = str(filename)#.encode('cp936')
        print self.filename
        ext = os.path.splitext(self.filename)[1]
        if 'png' in ext:
            imgname = self.filename
        elif 'exe' in ext:
            self.convertBin2Img(self.filename)
            imgname = "./cache/aaaaa.png"
        self.postImageFile(imgname)
        self.malimg = MalwareImageClass(imgname)
        self.malimg.malwarSignal.connect(self.showClassifyResult)
        self.malimg.concluSignal.connect(self.showClassifyResult)
        self.malimg.start()
        # self.convertBin2Img(self.filename)

    def postImageFile(self, filename):
        img = str(filename)
        image = QtGui.QImage()
        if image.load(img):
            # 设置图像适配
            self.imglb.setScaledContents(True)
            self.imglb.setPixmap(QtGui.QPixmap.fromImage(image))
        else:
            print u"导入图像失败"

    def convertBin2Img(self, filename):
        f = open(filename,'rb')
        ln = os.path.getsize(filename) # length of file in bytes
        width = 256
        rem = ln % width

        a = array.array("B") # uint8 array
        a.fromfile(f,ln - rem)
        f.close()

        g = numpy.reshape(a,(len(a)/width,width))
        g = numpy.uint8(g)
        scipy.misc.imsave('./cache/aaaaa.png', g) # save the image
        print "save img"

    def showClassifyResult(self, flag, msg):
        self.ui.label_4.setText(u"图像1")
        self.ui.label_5.setText(u"图像2")
        self.ui.label_6.setText(u"图像3")
        print msg
        rootpath = '/home/amber/Documents/smart_image/malimg_dataset/malimg_paper_dataset_imgs/'
        if 1 == flag:
            self.ui.label.setText(unicode(msg[0]))
            self.ui.label_2.setText(unicode(msg[1]))
            self.classname = str(msg[1])
        if 2 == flag:
            img1 = os.path.join(rootpath, self.classname, msg[0])
            img2 = os.path.join(rootpath, self.classname, msg[1])
            img3 = os.path.join(rootpath, self.classname, msg[2])
            # print img1, img2, img3

            image = QtGui.QImage()
            if image.load(img1):
                # image.scaled(64, 64)
                # 设置图像适配
                self.ui.label_4.setScaledContents(True)
                self.ui.label_4.setPixmap(QtGui.QPixmap.fromImage(image))
            else:
                print u"导入图像失败"
            if image.load(img2):
                # image.scaled(64, 64)
                # 设置图像适配
                self.ui.label_5.setScaledContents(True)
                self.ui.label_5.setPixmap(QtGui.QPixmap.fromImage(image))
            else:
                print u"导入图像失败"
            if image.load(img3):
                # image.scaled(64, 64)
                # 设置图像适配
                self.ui.label_6.setScaledContents(True)
                self.ui.label_6.setPixmap(QtGui.QPixmap.fromImage(image))
            else:
                print u"导入图像失败"