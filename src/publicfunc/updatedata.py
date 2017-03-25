#coding=utf-8

from PyQt4 import QtCore
import os, sys
import git

class UpdateData(QtCore.QObject):

    def __init__(self, parent=None):
        QtCore.QObject.__init__(self)

    '''
    从github下载/更新yara数据库
    '''
    def cloneYaraData(self):
        if not os.path.exists("rules"):
            os.mkdir("rules")
        if not os.path.exists("rules_compiled"):
            os.mkdir("rules_compiled")
        if not os.listdir("rules"):
            print "Downloading Yara-rules..."
            git.Git().clone("https://github.com/Yara-Rules/rules")
            return
        else:
            print "exists yara data"
        # else: # 更新yara数据库
        #     update = QtGui.QMessageBox()
        #     recv = update.question(u"q", u"r", update.Yes, update.No)
        #     if recv == update.yes:
        #         if os.path.exists("rules"):
        #             shutil.rmtree("rules")
        #         if os.path.exists("rules_compiled"):
        #             shutil.rmtree("rules_compiled")
        #             os.mkdir("rules_compiled")
        #         download_yara_rules_git()
        #     else:
        #         print "donot update"
        #         pass