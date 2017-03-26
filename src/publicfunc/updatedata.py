#coding=utf-8

from PyQt4 import QtCore
import os, sys, shutil
# import git

class UpdateData(QtCore.QObject):

    def __init__(self, parent=None):
        QtCore.QObject.__init__(self)

    '''
    从github下载yara规则库库
    '''
    def cloneYaraData(self):
        if not os.path.exists("rules"):
            os.mkdir("rules")
        if not os.path.exists("rules_compiled"):
            os.mkdir("rules_compiled")
        if not os.listdir("rules"):
            print "Downloading Yara-rules..."
            # git.Git().clone("https://github.com/Yara-Rules/rules")
            return
        else:
            print "exists yara data"

    '''
    更新yara更新库
    '''
    def updateYaraData(self):
        print u"更新规则库"
        import time
        time.sleep(10)
        return
        if os.path.exists("rules"):
            shutil.rmtree("rules")
        if os.path.exists("rules_compiled"):
            shutil.rmtree("rules_compiled")
        os.mkdir("rules_compiled")
        self.cloneYaraData()