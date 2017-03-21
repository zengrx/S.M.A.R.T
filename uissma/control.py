# -*- coding: utf-8 -*-

from PyQt4 import QtCore, QtGui
import time, sys, os
import magic, hashlib
from checkrulethread.yaracheck import CheckPacker, CheckMalware, CheckCrypto
from checkrulethread.clamav.clamav import CheckClamav
from checkrulethread.fileanalyze import DefaultAnalyze
from gobalset import FlagSet

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

    def __init__(self, cdir, ctype, parent=None):
        super(CheckFolder, self).__init__(parent)
        self.dir      = str(cdir).decode('utf-8')
        self.type     = ctype
        self.filename = ""

    '''
    选择main中传入的文件类型或后缀
    filename: 文件绝对路径
    返回
    need all types of file to create the typevalue list
    '''
    def chooseFileType(self, filename):
        # typedict = {
        #     7: "pe32", 8: "", 9: "text", 10: "archive data", 11: "", 12: "data"
        # }
        typevalue = [] # 储存文件类型字符串
        if '7' in self.type: # PE文件
            typevalue.append("PE32")
        if '8' in self.type: # office/pdf文档等
            typevalue.append("Microsoft")
            typevalue.append("Document File")
            typevalue.append("PDF")
        if '9' in self.type: # 脚本/文本文件
            typevalue.append("text")
            typevalue.append("script")
            typevalue.append("html")
        if '10' in self.type: # 压缩包
            typevalue.append("achive data")
            typevalue.append("gzip")
        if '11' in self.type: # 多媒体文件
            typevalue.append("Media")
            typevalue.append("Matroska")
            typevalue.append("Audio")
            typevalue.append("image")
            typevalue.append("MPEG")
        if '12' in self.type: # .asm后缀
            typevalue.append(".asm")
        file_magic = magic.Magic(magic_file="D:\Python27\magic.mgc")
        fmagic = file_magic.from_file(str(filename).encode('cp936'))
        extension = os.path.splitext(filename)[1]
        # 匹配文件类型或后缀名
        flag = 0
        # 全选情况
        if set(self.type) == set(['7', '8', '9', '10', '11', '12']):
            return 1
        for x in typevalue:
            if x in fmagic or x in extension:
                flag += 1
        return flag
            
    #重写的run方法
    def run(self):
        #self.dir = os.path.join(str(self.folder).decode('utf-8'))
        print self.dir, self.type
        assert os.path.isdir(self.dir), "make sure this is a path"
        result = [] # test print all files
        i = 0 # number of files
        j = 0 # number of dirs
        for root, dirs, files in os.walk(self.dir, topdown=True):
            if 0 == FlagSet.scanstopflag:
                print "stopflag"
                break
            for di in dirs:
                j = j + 1
                # print os.path.join(root, di)
            
            for fl in files:
                # print os.path.join(root, fl)
                self.filename = os.path.join(root, fl)
                if self.chooseFileType(self.filename) > 0:
                    result.append(self.filename)
                    # time.sleep(3)
                    # self.numberSignal.emit(3, str(fl))
                    i = i + 1

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

    def __init__(self, filelist, scanrule, parent=None):
        super(ScanFile, self).__init__(parent)
        self.filelist = filelist # 从UI线程传回的文件名列表
        self.scanrule = scanrule # 从UI线程传回的扫描规则策略
        self.filename = '' # 文件名
        self.filetype = '' # 文件类型
        self.filesize = '' # 文件大小
        self.infos    = [] # baseinfo列表
        self.detect   = [] # 检测结论
        # flags
        self.yaraflag = 0
        self.clamflag = 0
        self.Packflag = 0
        self.selfflag = 0
        self.whitflag = 0

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

    '''
    应用main中设置的规则进行扫描调度
    默认用系统自带分析 不加载其他规则如yara或反病毒数据库
    '''
    def chooseScanRule(self, rules):
        print rules
        if not any(set(rules)):
            print u"使用内置规则"
        if '2' in rules:
            print u"使用yara规则"
            self.yaraflag = 1
        if '3' in rules:
            print u"使用clamav"
            self.clamflag = 1
        if '4' in rules:
            print u"使用文件查壳"
            self.Packflag = 1
        if '5' in rules:
            print u"使用自定义规则"
            self.selfflag = 1
        if '6' in rules:
            print u"启用白名单"
            self.whitflag = 1

    def startDefaultThread(self, filename, filetype, index):
        filename = filename.encode('cp936')
        typepe = 'PE32'
        if typepe in filetype:
            self.checkdefault = DefaultAnalyze(filename, index)
            self.checkdefault.valueSignal.connect(self.recvDefaultResult)
            self.checkdefault.start()
            self.checkdefault.wait()

    def recvDefaultResult(self):
        print "get default result"

    # 开始yara检测线程
    def startYaraThread(self, filename, filetype, index):
        # return
        filename = filename.encode('cp936')
        typepe   = 'PE32' # PE文件
        typesh   = 'text' # 文本&脚本文件
        if typepe in filetype:
            print "---------PE----------"
            # 链接checkpacker线程
            self.checkMalwThread = CheckMalware(filename)
            self.checkMalwThread.valueSignal.connect(self.recvYaraResult)
            self.checkMalwThread.start()
            self.checkMalwThread.wait()
        if typesh in filetype: # 检测加密特征
            print "---------SH----------"
            self.checkCrypThread = CheckCrypto(filename)
            self.checkCrypThread.valueSignal.connect(self.recvYaraResult)
            self.checkCrypThread.start()
            self.checkCrypThread.wait()

    # 获取yara检测结果
    # 在该接收函数中应该处理汇总的信息
    def recvYaraResult(self, msg):
        print "get result from yarathread"
        return msg

    '''
    使用clamav数据库规则检测
    主要用于对已知病毒文件检测
    '''
    def startClamThread(self, filename, index):
        print "use clamav signature"
        filename = filename.encode('cp936')
        self.checkClamThread = CheckClamav(filename)
        self.checkClamThread.valueSignal.connect(self.recvClamResult)
        self.checkClamThread.start()
        self.checkClamThread.wait()

    def recvClamResult(self, msg):
        pass

    def startPackThread(self, filename, index):
        print "start check pack"
        filename = filename.encode('cp936')
        self.checkPackThread = CheckPacker(filename, index)
        self.checkPackThread.valueSignal.connect(self.recvYaraResult)
        self.checkPackThread.start()
        self.checkPackThread.wait()

    def run(self):
        # import random
        self.chooseScanRule(self.scanrule)
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
            # file size should less than 100M
            if int(self.filesize) < 100*1024*1024:
                # use default function
                # self.dection = self.startDefaultThread(self.filename, self.filetype, i)
                # use yara rule
                if 1 == self.yaraflag:
                    self.detect = self.startYaraThread(self.filename, self.filetype, i)
                # 直接使用生成的clamav全部规则
                # 后期计划拆分针对不同类型文件的规则
                if 1 == self.clamflag: 
                    self.detect = self.startClamThread(self.filename, i)
                if 1 == self.Packflag:
                    self.detect = self.startPackThread(self.filename, i)
            print FlagSet.scanstopflag
            if 0 == FlagSet.scanstopflag:
                self.fileSignal.emit(len(self.filelist), self.filename, self.infos)
                break
            self.fileSignal.emit(i+1, self.filename, self.infos)
            