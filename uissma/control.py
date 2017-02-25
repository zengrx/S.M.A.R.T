# -*- coding: utf-8 -*-

from PyQt4 import QtCore, QtGui
import time, sys, os
import magic, hashlib
from yarathread.yaracheck import CheckPacker, CheckMalware

sys.path.append("../ssma_python2")
from src import colors
from src.check_file import PEScanner, file_info
from src.blacklisted_domain_ip import ransomware_and_malware_domain_check
from src.check import is_malware, is_file_packed, check_crypto, is_antidb_antivm, is_malicious_document
from src.check_file import PEScanner, file_info
from src.check_updates import check_internet_connection, download_yara_rules_git
from src.check_virustotal import virustotal
from src.file_strings import get_strings

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
        self.dir = str(cdir).decode('utf-8')

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
    fileSignal = QtCore.pyqtSignal(int, str, list)

    def __init__(self, filelist, parent=None):
        super(ScanFile, self).__init__(parent)
        self.filelist = filelist # 从UI线程传回来的文件名列表
        self.filename = '' # 文件名
        self.filetype = '' # 文件类型
        self.filesize = '' # 文件大小
        self.infos    = [] # baseinfo列表
        self.detect   = [] # 检测结论

    '''
    获取文件类型，日期，大小，md5等基本信息
    '''
    def getFileInfo(self, filename):
        info = []
        with open(filename, 'rb') as f:
            cfile = f.read()
            info.append(os.path.getsize(filename))
            file_magic = magic.Magic(magic_file="D:\Python27\magic.mgc")
            info.append(file_magic.from_file(filename))
            info.append(hashlib.md5(cfile).hexdigest())
        return info

    # 开始yara检测线程
    def startYaraThread(self, filename, filetype, index):
        # return
        filename = filename.encode('cp936')
        typepe   = 'PE32'
        if typepe in filetype:
            print "---------PE----------"
            # 链接checkpacker线程
            self.checkMalwThread = CheckMalware(filename)
            self.checkMalwThread.valueSignal.connect(self.recvYaraResult)
            self.checkPackThread = CheckPacker(filename, index)
            self.checkPackThread.valueSignal.connect(self.recvYaraResult)
            self.checkMalwThread.start()
            self.checkPackThread.start()
            self.checkMalwThread.wait()
            self.checkPackThread.wait()

    # 获取yara检测结果
    # 在该接收函数中应该处理汇总的信息
    def recvYaraResult(self, msg):
        print "get result from yarathread"
        return msg

    def run(self):
        import random
        for i in range(len(self.filelist)):
            self.filename = self.filelist[i]
            # time.sleep(random.uniform(0, 0.5)) # 模拟耗时
            # 添加获取文件基本信息函数后
            # 此处可以发送多个参数
            try:
                self.infos = self.getFileInfo(str(self.filename).encode('cp936'))
            except:
                print str(i) + " error"
            self.filetype = self.infos[1]
            self.filesize = self.infos[0]
            if int(self.filesize) < 100*1024*1024:
                self.detect = self.startYaraThread(self.filename, self.filetype, i)
            self.fileSignal.emit(i+1, self.filename, self.infos)
            