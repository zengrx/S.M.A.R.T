#coding=utf-8

import sys, os
import yara
from PyQt4 import QtCore, QtGui
import sqlite3
# import updateclamav

'''
由clamav数据库更新规则
预计放置在菜单栏中
'''
class UpdateClamav(QtCore.QThread):
    
    def __init__(self, parent=None):
        super(UpdateClamav, self).__init__(parent)

    '''
    更新数据库
    数据库组成为base+daily
    '''
    def updateDatabase(self):
        pass

    '''
    更新clamav特征
    包含PE\Shell\Html
    去除了对于OSX系mail等特征
    '''
    def updateSignatures(self):
        pass

'''
使用clamav规则检测
'''
class CheckClamav(QtCore.QThread):
    numberSignal = QtCore.pyqtSignal(int, str)
    valueSignal  = QtCore.pyqtSignal(list)

    def __init__(self, filename, parent=None):
        super(CheckClamav, self).__init__(parent)
        self.filename = filename

    def hitClamavRule(self):
        if os.path.exists("./checkrulethread/clamav/clamav_compiled.yar"):
            rule = yara.load("./checkrulethread/clamav/clamav_compiled.yar")
            m = rule.match(self.filename)
            if m:
                print m
        elif os.path.exists("./checkrulethread/clamav/clamav.yara"):
            print "generate rule from clamav2yara"
            rule = yara.compile("./checkrulethread/clamav/clamav.yara")
            rule.save("./checkrulethread/clamav/clamav_compiled.yar")
            rule = yara.load("./checkrulethread/clamav/clamav_compiled.yar")
            m = rule.match(self.filename)
            if m:
                print m
        else:
            print "generate yara rule failed"
        
    def run(self):
        self.hitClamavRule()