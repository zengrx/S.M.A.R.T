# -*- coding: utf-8 -*-

from PyQt4 import QtCore, QtGui
import time, sys, os

reload(sys)
sys.setdefaultencoding( "utf-8" )

'''
假设每个文件查询时间为10秒，设置分离主线程和查询线程的框架
'''
class checkFolder(QtCore.QThread):
    numberSignal = QtCore.pyqtSignal(int, str)
    valueSignal  = QtCore.pyqtSignal(int, list)

    def __init__(self, cdir, parent=None):
        super(checkFolder, self).__init__(parent)
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
                self.numberSignal.emit(3, str(fl))
                i = i + 1
                # print os.path.join(root, fl)

        print "(origin)dirs: ",  j
        print "(origin)files: ", i
        self.numberSignal.emit(1, str(j))  # dirs
        self.numberSignal.emit(2, str(i))  # files
        # self.valueSignal.emit(3, result) # filename