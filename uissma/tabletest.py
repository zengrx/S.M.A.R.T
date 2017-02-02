# -*- coding: utf-8 -*-

from PyQt4 import QtCore, QtGui
import time, sys, os

reload(sys)
sys.setdefaultencoding( "utf-8" )

'''
扫描init线程
'''
class CheckFolder(QtCore.QThread):
    numberSignal = QtCore.pyqtSignal(int, str)
    valueSignal  = QtCore.pyqtSignal(int, list)

    def __init__(self, cdir, parent=None):
        super(CheckFolder, self).__init__(parent)
        self.dir = str(cdir)

    #重写的run方法
    def run(self):
        #self.dir = os.path.join(str(self.folder).decode('utf-8'))
        print self.dir
        assert os.path.isdir(self.dir), "make sure this is a path"
        result = [] # test print all files
        i = 0 # number of files
        j = 0 # number of dirs
        for root, dirs, files in os.walk(self.dir, topdown=True):
            for di in dirs:
                j = j + 1
                # print os.path.join(root, di)
            
            for fl in files:
                result.append(os.path.join(root, fl))
                # time.sleep(3)
                # self.numberSignal.emit(3, str(fl))
                i = i + 1
                # print os.path.join(root, fl)

        print "(origin)dirs: ",  j
        print "(origin)files: ", i
        # 发送初始化信息
        self.numberSignal.emit(1, str(j))  # dirs
        self.numberSignal.emit(2, str(i))  # files
        self.valueSignal.emit(3, result) # filename

'''
扫描操作线程
'''
class ScanFile(QtCore.QThread):
    fileSignal = QtCore.pyqtSignal(int, str)

    def __init__(self, filelist, parent=None):
        super(ScanFile, self).__init__(parent)
        self.filelist = filelist
        self.filename = ''

    def run(self):
        import random
        for i in range(len(self.filelist)):
            self.filename = self.filelist[i]
            time.sleep(random.uniform(0, 3)) # 模拟耗时
            self.fileSignal.emit(i+1, self.filename)