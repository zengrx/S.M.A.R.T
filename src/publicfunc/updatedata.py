#coding=utf-8

import os, sys
import git

'''
从github下载/更新yara数据库
'''
def cloneYaraData():
    if not os.path.exists("rules"):
        os.mkdir("rules")
    if not os.path.exists("rules_compiled"):
        os.mkdir("rules_compiled")
    if not os.listdir("rules"):
        print "Downloading Yara-rules..."
        # emit开始下载
        git.Git().clone("https://github.com/Yara-Rules/rules")
        # emit一个下载完成给UI线程
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