# -*- coding: utf-8 -*-

from PyQt4 import QtCore, QtGui
import time, sys, os
import magic

reload(sys)
sys.setdefaultencoding( "utf-8" )

class checkFileThread(QtCore.QThread):
    finishSignal = QtCore.pyqtSignal(int, str)

    def __init__(self, filename, parent=None):
        super(checkFileThread, self).__init__(parent)
        self.filename = filename

    def run(self):
        filename = str(self.filename).decode('utf-8')
        print filename 
        file_magic = magic.Magic(magic_file="D:\Python27\magic.mgc")
        self.filetype = file_magic.from_file(filename.encode('cp936')) #for windows encode
        self.finishSignal.emit(1, self.filetype)
        for n in file_info(filename.encode('cp936')):
            print "\t", n
            self.finishSignal.emit(2, n.decode('cp936'))

#继承 QThread 类
class checkPEThread(QtCore.QThread):
    finishSignal = QtCore.pyqtSignal(int, list)
    #构造函数里增加形参
    def __init__(self, filetype, filename, parent=None):
        super(checkPEThread, self).__init__(parent)
        self.filetype = filetype
        self.filename = filename
        self.seclist  = []

    #重写 run() 函数，在里面干大事。
    def run(self):
        #大事
        tmp = "PE32"
        if tmp in self.filetype:
            pe = PEScanner(filename=self.filename)
            print(colors.BOLD + colors.YELLOW + "File Details: " + colors.RESET)
            msglist = []
            for n in pe.file_info():
                #print "\t", n
                msglist.append(n)
            self.finishSignal.emit(1, msglist)
            self.seclist = pe.sections_analysis()
            self.finishSignal.emit(2, self.seclist)
            pe.check_file_header()
            check_date_result = pe.check_date()
            if check_date_result:
                print check_date_result

            check_imports_result = pe.check_imports()
            if check_imports_result:
                print( 
                    colors.BOLD + colors.YELLOW + "This file contains a list of Windows functions commonly used by malware.\nFor more information use the Microsoft documentation.\n" + colors.RESET)

                for n in check_imports_result:
                    n = n.split("^")
                    print "\t" + colors.LIGHT_RED + n[0] + colors.RESET + " - " + n[1]

        #大事干完了，发送一个信号告诉主线程窗口
        #self.finishSignal.emit('done.')

class anotherThread(QtCore.QThread):
    anotherSignal = QtCore.pyqtSignal(str)
    
    def __init__(self, stime, parent=None):
        super(anotherThread, self).__init__(parent)
        self.stime = stime

    def run(self):
        time.sleep(self.stime)
        self.anotherSignal.emit('message')