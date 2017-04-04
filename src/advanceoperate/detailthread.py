#coding=utf-8

import sys, os
from PyQt4 import QtCore
sys.path.append("..")
from publicfunc.fileanalyze import PEFileAnalize, getFileInfo

class FileDetail(QtCore.QThread):
    finishSignal = QtCore.pyqtSignal(list)

    def __init__(self, filename, parent=None):
        super(FileDetail, self).__init__(parent)
        self.filename = str(filename).encode('cp936')

    def run(self):
        # 获取文件基本内容
        useless, baseinfo = getFileInfo(self.filename)
        self.finishSignal.emit(baseinfo)

class PEFileInfo(QtCore.QThread):
    sectionSignal = QtCore.pyqtSignal(list)
    importSignal  = QtCore.pyqtSignal(dict)

    def __init__(self, filename, parent=None):
        super(PEFileInfo, self).__init__(parent)
        self.filename = str(filename).encode('cp936')

    # 处理PE节
    def getSetInfo(self):
        pefile  = PEFileAnalize(self.filename)
        setinfo = pefile.checkFileSections()
        return setinfo
    
    # 处理导入表
    def getImpInfo(self):
        pefile  = PEFileAnalize(self.filename)
        impinfo = pefile.checkFileImports()
        return impinfo

    def run(self):
        print "pefile info from thread"
        # 处理PE节时速度较慢
        self.importSignal.emit(self.getImpInfo())
        self.sectionSignal.emit(self.getSetInfo())
