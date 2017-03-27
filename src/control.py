# -*- coding: utf-8 -*-

from PyQt4 import QtCore, QtGui
import time, sys, os
import magic, hashlib
from publicfunc.yaracheck import CheckPacker, CheckMalware, CheckCrypto
from publicfunc.clamav.clamav import CheckClamav
from publicfunc.fileanalyze import getFileInfo, DefaultAnalyze
from publicfunc.updatedata import UpdateData
from globalset import FlagSet
import sqlite3

reload(sys)
sys.setdefaultencoding( "utf-8" )

'''
扫描init线程
'''
class CheckFolder(QtCore.QThread):
    numberSignal = QtCore.pyqtSignal(int, str)

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
        # file_magic = magic.Magic(magic_file="../libs/magic.mgc")
        try:
            fmagic = magic.from_file(str(filename))
        except:
            print "maigc error {}".format(str(filename))
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
    
    def writeInit2DB(self, filename, index, sqlconn):
        i = index
        self.filename = filename
        sqlcursor = sqlconn.cursor()
        sfilename = self.filename # 解决windows下使用sqlite编码问题
        sqlcursor.execute("insert into base_info (id, name, path) values(?, ?, ?)", (int(i), sfilename, "lalal"))
            
    #重写的run方法
    def run(self):
        #self.dir = os.path.join(str(self.folder).decode('utf-8'))
        print self.dir, self.type
        assert os.path.isdir(self.dir), "make sure this is a path"
        result = [] # test print all files
        i = 0 # number of files
        j = 0 # number of dirs
        sqlindex = FlagSet.scansqlcount # 数据库索引基址+本次插入索引
        try:
            sqlconn = sqlite3.connect("../db/fileinfo.db")
        except sqlite3.Error, e:
            print "sqlite connect failed" , "\n", e.args[0]        
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
                    self.writeInit2DB(self.filename, sqlindex, sqlconn)
                    sqlindex +=  1
                    i += 1
        sqlconn.commit()
        sqlconn.close()
        print "(origin)dirs: ",  j
        print "(origin)files: ", i
        # 发送初始化信息
        self.numberSignal.emit(1, str(j))  # dirs
        self.numberSignal.emit(2, str(i))  # files
        self.numberSignal.emit(3, "start analysis")  # start analysis signal

'''
扫描操作线程
'''
class ScanFile(QtCore.QThread):
    fileSignal = QtCore.pyqtSignal(int, str)
    smsgSignal = QtCore.pyqtSignal(str)

    def __init__(self, filelist, scanrule, parent=None):
        super(ScanFile, self).__init__(parent)
        self.filelist = filelist # 从UI线程传回的文件名列表-文件个数
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
    获取文件名信息
    '''
    def readFromDataBase(self, index):
        i = index - 1
        try:
            sqlcoon = sqlite3.connect("../db/fileinfo.db")
        except sqlite3.Error,e :
            print "sqlite connect failed" , "\n", e.args[0]
        sqlcursor = sqlcoon.cursor()
        try:
            sqlcursor.execute("select name from base_info where id =?", (int(i),))
            sqlcoon.commit()
            sqlcursor = sqlcursor.fetchone()
            sqlcoon.close()
            return sqlcursor[0]
        except:
            print "error when read db data"

    '''
    写入文件类型，日期，大小，md5等基本信息
    '''
    def write2DataBase(self, index, filename):
        i = index - 1
        info, useless = getFileInfo(filename)
        try:
            sqlconn = sqlite3.connect("../db/fileinfo.db")
            sqlconn.text_factory = str
        except sqlite3.Error, e:
            print "sqlite connect failed" , "\n", e.args[0]
        sqlcursor = sqlconn.cursor()
        try:
            sfilename = filename # 解决windows下使用sqlite编码问题
            sqlcursor.execute("update base_info set size=? ,typt=? ,md5=? where id=?", (info[3], info[4], info[0], i))
            sqlconn.commit()
            sqlconn.close()
        except:
            print "sql exec err"
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
        filename = filename
        typepe = 'PE32'
        if typepe in filetype:
            self.checkdefault = DefaultAnalyze(filename, index)
            self.checkdefault.valueSignal.connect(self.recvDefaultResult)
            self.checkdefault.start()
            self.checkdefault.wait()

    def recvDefaultResult(self):
        print "get default result"

    '''
    检查yara规则库
    '''
    def checkYaraExists(self):
        self.smsgSignal.emit(u"未检测到Yara规则库，正在下载...")
        U = UpdateData()
        U.cloneYaraData()

    # 开始yara检测线程
    def startYaraThread(self, filename, filetype, index):
        # return
        filename = filename
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
        filename = filename
        self.checkClamThread = CheckClamav(filename)
        self.checkClamThread.valueSignal.connect(self.recvClamResult)
        self.checkClamThread.start()
        self.checkClamThread.wait()

    def recvClamResult(self, msg):
        pass

    def startPackThread(self, filename, index):
        print "start check pack"
        filename = filename
        self.checkPackThread = CheckPacker(filename, index)
        self.checkPackThread.valueSignal.connect(self.recvYaraResult)
        self.checkPackThread.start()
        self.checkPackThread.wait()

    def run(self):
        # import random
        self.chooseScanRule(self.scanrule)
        if 1 == self.yaraflag:
            self.checkYaraExists()
        # 判断来自文件夹or文件选择
        # 文件选择发送list信号
        if isinstance(self.filelist, list):
            print "it's a list"
            sqlindex = FlagSet.scansqlcount
            try:
                sqlconn = sqlite3.connect("../db/fileinfo.db")
            except sqlite3.Error, e:
                print "sqlite connect failed" , "\n", e.args[0]
            for i in range(len(self.filelist)):
                self.filename = self.filelist[i]
                print self.filename
                sqlcursor = sqlconn.cursor()
                sfilename = self.filename # 解决windows下使用sqlite编码问题
                sqlcursor.execute("insert into base_info (id, name, path) values(?, ?, ?)", (int(sqlindex), sfilename, "lalal"))
                sqlindex += 1
            sqlconn.commit()
            sqlconn.close()
            self.filelist = len(self.filelist)
        for i in range(self.filelist):
            # self.filename = self.filelist[i]
            # time.sleep(random.uniform(0, 0.5)) # 模拟耗时
            # 添加获取文件基本信息函数后
            # 此处可以发送多个参数
            # print i, FlagSet.scansqlcount
            FlagSet.scansqlcount = FlagSet.scansqlcount + 1
            try:
                self.filename = self.readFromDataBase(FlagSet.scansqlcount)
                self.infos = self.write2DataBase(FlagSet.scansqlcount, str(self.filename))
            except:
                print str(i) + " error when db operate"
            self.filetype = self.infos[4]
            self.filesize = self.infos[3]
            # file size should less than 100M
            if int(self.filesize) < 100*1024*1024:
                # use default function
                self.dection = self.startDefaultThread(self.filename, self.filetype, i)
                # use yara rule
                if 1 == self.yaraflag:
                    self.detect = self.startYaraThread(self.filename, self.filetype, i)
                # 直接使用生成的clamav全部规则
                # 后期计划拆分针对不同类型文件的规则
                if 1 == self.clamflag: 
                    self.detect = self.startClamThread(self.filename, i)
                if 1 == self.Packflag:
                    self.detect = self.startPackThread(self.filename, i)
            # print FlagSet.scanstopflag
            if 0 == FlagSet.scanstopflag:
                self.fileSignal.emit(self.filelist, self.filename)
                break
            self.fileSignal.emit(i+1, self.filename)
            
