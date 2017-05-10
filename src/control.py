# -*- coding: utf-8 -*-

from PyQt4 import QtCore, QtGui
import time, sys, os
import magic, hashlib
from publicfunc.yaracheck import CheckPacker, CheckMalware, CheckCrypto, CheckWebshell, Checkcustom
from publicfunc.clamav.clamav import CheckClamav
from publicfunc.fileanalyze import getFileInfo, DefaultAnalyze, GetFileString
from publicfunc.updatedata import UpdateData
from globalset import FlagSet, ImpAlert, YaraAlert, StaticValue, FilePath
import sqlite3

reload(sys)
sys.setdefaultencoding( "utf-8" )

'''
扫描init线程
'''
class CheckFolder(QtCore.QThread):
    numberSignal = QtCore.pyqtSignal(int, str)
    folderSignal = QtCore.pyqtSignal(int, str)

    def __init__(self, cdir, ctype, crule, cdepth, parent=None):
        super(CheckFolder, self).__init__(parent)
        self.dir      = str(cdir).decode('utf-8')
        self.type     = ctype
        self.rule     = crule
        self.depth    = cdepth
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
            typevalue.append("executable")
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
            fmagic = magic.from_file(str(filename))#.encode('cp936'))
        except:
            print "maigc error {}".format(str(filename))#.encode('cp936'))
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
    
    '''
    匹配白名单
    有匹配时返回1
    '''
    def matchWhiteList(self, filename):
        tmpf = ''
        for af in FilePath.whitefile:
            tmpf = str(af)#.decode('cp936')
            if tmpf == str(filename) and '6' in self.rule:
                print "hit", tmpf
                self.folderSignal.emit(1, "match a withlist file: " + unicode(tmpf))
                return 1

    def writeInit2DB(self, filename, index, sqlconn):
        i = index
        self.filename = filename
        sqlcursor = sqlconn.cursor()
        sfilename = self.filename # 解决windows下使用sqlite编码问题
        sqlcursor.execute("insert into base_info (id, name) values(?, ?)", (int(i), sfilename))
            
    #重写的run方法
    def run(self):
        #self.dir = os.path.join(str(self.folder).decode('utf-8'))
        # print self.dir, self.type
        sendm = "entrance folder:" + unicode(self.dir) + "\t" + "file type:" + str(self.type)
        self.folderSignal.emit(1, sendm)
        assert os.path.isdir(self.dir), "make sure this is a path"
        result = [] # test print all files
        i = 0 # number of files
        j = 0 # number of dirs
        sqlindex = FlagSet.scansqlcount # 数据库索引基址+本次插入索引
        try:
            sqlconn = sqlite3.connect("../db/fileinfo.db")
        except sqlite3.Error, e:
            print "sqlite connect failed" , "\n", e.args[0]
        # print self.depth
        sendm = "scan depth:" + str(self.depth)
        self.folderSignal.emit(1, sendm)
        d = str(self.dir).count('/')
        for root, dirs, files in os.walk(self.dir, topdown=True):
            if 0 == FlagSet.scanstopflag:
                # print "stopflag"
                sendm = "user has stoped initialization, quit..."
                self.folderSignal.emit(1, sendm)
                break
            # print root
            s = str(root).count('/')
            layer = s - d
            # print layer
            sendm = root + "  -->layers: " + str(layer)
            self.folderSignal.emit(1, sendm)
            if layer <= self.depth or -1 == self.depth:
                for di in dirs:
                    j = j + 1
                    # print os.path.join(root, di)
                for fl in files:
                    # print os.path.join(root, fl)
                    self.filename = os.path.join(root, fl)
                    wflag = self.matchWhiteList(self.filename)
                    if self.chooseFileType(self.filename) > 0 and not wflag:
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
        self.folderSignal.emit(1, "folder check initialization over")

'''
扫描操作线程
'''
class ScanFile(QtCore.QThread):
    fileSignal = QtCore.pyqtSignal(int, str)
    smsgSignal = QtCore.pyqtSignal(int, str)
    flogSignal = QtCore.pyqtSignal(int, str)

    def __init__(self, filelist, scanrule, parent=None):
        super(ScanFile, self).__init__(parent)
        self.filelist = filelist # 从UI线程传回的文件名列表-文件个数
        self.scanrule = scanrule # 从UI线程传回的扫描规则策略
        self.filename = '' # 文件名
        self.md5      = '' # 文件md5
        self.filetype = '' # 文件类型
        self.filesize = '' # 文件大小
        self.infos    = [] # baseinfo列表
        self.detect   = [] # 检测结论
        self.score    = 0  # 评分
        self.sendmsg  = '' # 分析text内容
        # flags
        self.pealflag = 0
        self.crypflag = 0
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
        except sqlite3.Error, e :
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
    def write2DataBase(self, index, info, score, alstime):
        i = index - 1
        try:
            sqlconn = sqlite3.connect("../db/fileinfo.db")
            # sqlconn.text_factory = str
        except sqlite3.Error, e:
            print "sqlite connect failed" , "\n", e.args[0]
        sqlcursor = sqlconn.cursor()
        try:
            sqlcursor.execute("update base_info set size=? ,type=? ,md5=?, score=?, mark=?, time=? where id=?", (info[3], info[4], info[0], score, "none", alstime, i))
            sqlconn.commit()
            sqlconn.close()
        except sqlite3.Error, e:
            print "sql exec err" , "\n", e.args[0]

    '''
    重新扫描时更新数据库内容
    主要更新扫描结果
    '''
    def update4DataBse(self, index, score, alstime):
        i = index
        try:
            sqlconn = sqlite3.connect("../db/fileinfo.db")
        except sqlite3.Error, e:
            print "sqlite connect failed" , "\n", e.args[0]
        sqlcursor = sqlconn.cursor()
        try:
            sqlcursor.execute("update base_info set score=?, time=? where id=?", (score, alstime, i))
            sqlconn.commit()
            sqlconn.close()
        except sqlite3.Error, e:
            print "sql exec err" , "\n", e.args[0]

    '''
    应用main中设置的规则进行扫描调度
    默认用系统自带分析 不加载其他规则如yara或反病毒数据库
    '''
    def chooseScanRule(self, rules):
        print rules
        if not any(set(rules)):
            print u"使用内置规则"
        if '2' in rules:
            print u"使用PE分析"
            self.pealflag = 1
        if '3' in rules:
            print u"使用检查加密"
            self.crypflag = 1
        if '4' in rules:
            print u"使用文件查壳"
            self.Packflag = 1
        if '5' in rules:
            print u"使用自定义规则"
            self.selfflag = 1
        if '6' in rules:
            print u"启用白名单"
            self.whitflag = 1

    '''
    使用内置方法检查
    '''
    def startDefaultThread(self, filename, filetype, md5, index):
        filename = filename#.encode('cp936')
        typepe = 'executable'
        if typepe in filetype:
            sqlcursor = self.readPEinfoDB(md5)
            if sqlcursor:
                print "pe_info exist"
                entrypnt = sqlcursor[1]
                setinfo  = sqlcursor[2]
                impinfo  = sqlcursor[3]
                cpltime  = sqlcursor[4]
                self.score = self.PEDetectionResult(entrypnt, setinfo, impinfo, cpltime)
            else:
                # 需要拆分为三个左右的线程
                # 线程级别安全操作 
                # 使用Queue在threading处理数据库操作 
                self.checkdefault = DefaultAnalyze(filename, md5, index)
                self.checkdefault.valueSignal.connect(self.recvDefaultResult)
                self.checkdefault.start()
                self.checkdefault.wait()

    '''
    从pe_info表中读取信息
    '''
    def readPEinfoDB(self, md5):
        try:
            sqlconn = sqlite3.connect('../db/fileinfo.db')
        except sqlite3.Error, e:
            print "sqlite connect failed", "\n", e.args[0]
        sqlcursor = sqlconn.cursor()
        sqlcursor.execute("select * from pe_info where md5=?", (md5,))
        sqlconn.commit()
        sqlcursor = sqlcursor.fetchone()
        return sqlcursor

    '''
    接收线程返回的内容
    '''
    def recvDefaultResult(self, msg, md5):
        print "get default result"
        if 1 == msg:
            sqlcursor = self.readPEinfoDB(str(md5))
            entrypnt  = sqlcursor[1]
            setinfo   = sqlcursor[2]
            impinfo   = sqlcursor[3]
            cpltime   = sqlcursor[4]
            self.score = self.PEDetectionResult(entrypnt, setinfo, impinfo, cpltime)
        # elif -1 == msg: else:
        else:
            return

    '''
    PE分析结果汇总
    '''
    def PEDetectionResult(self, entrypnt, setinfo, impinfo, cpltime):
        dtk = 0
        fillm = "\t\t"
        sendm = ''
        nowdate = int(time.gmtime(time.time())[0])
        # 可疑的编译时间
        if cpltime > nowdate or cpltime < 1995:
            dtk += 1
            sendm = sendm + fillm + "---------suspicious cpltime----------" + "\n\t\t" + str(cpltime) + "\n"
        # 可疑的API
        alt = ImpAlert().alerts # 取alob内容
        att = [] # 文件中存在的可疑API列表
        impinfo = dict(eval(impinfo)) # unicode转dict
        apis = list(set(impinfo.values()[0])) # 文件使用所有API列表
        tmp = ""
        for i in apis:
            if i: # 除去none
                if any(map(i.startswith, alt.keys())):
                    for a in alt:
                        if i.startswith(a):
                             tmp += "\t\t{} : {}\n".format(i, alt.get(a))
                    dtk += 1
        sendm = sendm + fillm + "-----------suspicious api------------" + "\n" + tmp + "\n"
        # 可疑的PE节信息
        setinfo = list(eval(setinfo)) # unicode转list
        # 认可的节名称
        goodsection  = ['.data', '.text', '.code', '.reloc', '.idata', '.edata', '.rdata', '.bss', '.rsrc']
        numofsection = setinfo[0]
        if numofsection < 1 or numofsection > 9:
            dtk += 1
            sendm = sendm + fillm + "------suspicious section number------" + "\n\t\t" + str(numofsection) + "\n"
        sectionname = [] # 可疑的节名称
        rawsize0    = [] # 可疑的0长度节
        ssetsize    = [] # 可疑的节长度
        sentropy    = [] # 可疑的节熵
        for i in range(numofsection):
            secname     = str(setinfo[i * 5 + 1])
            virtualsize = int(setinfo[i * 5 + 3])
            rawsize     = int(setinfo[i * 5 + 4])
            entropy     = float(setinfo[i * 5 + 5])
            sectionname.append(secname)
            if 0 == rawsize and virtualsize > 0:
                dtk += 1
                rawsize0.append(secname)
            if 0 != rawsize and virtualsize / rawsize > 10:
                dtk += 1
                ssetsize.append(secname)
            if entropy < 1 or entropy > 7:
                dtk += 1
                sentropy.append(secname)
        if len(rawsize0):
            sendm = sendm + fillm + "--------suspicious rawsize 0---------" + "\n\t\t" + str(rawsize0) + "\n"
        if len(ssetsize):
            sendm = sendm + fillm + "------suspicious size section--------" + "\n\t\t" + str(ssetsize) + "\n"
        if len(sentropy):
            sendm = sendm + fillm + "---------suspicious entropy----------" + "\n\t\t" + str(sentropy) + "\n"
        badsections = [bad for bad in sectionname if bad not in goodsection]
        if len(badsections):
            sendm = sendm + fillm + "------suspicious section name--------" + "\n\t\t" + str(badsections) + "\n"
        dtk += len(badsections)
        # self.flogSignal.emit(2, sendm)
        self.sendmsg += sendm
        return dtk

    '''
    检查yara规则库
    '''
    def checkYaraExists(self):
        if not os.listdir("rules"):
            self.smsgSignal.emit(-1, u"未检测到Yara规则库，正在下载...")
            # U = UpdateData()
            # U.cloneYaraData()
        else:
            self.smsgSignal.emit(-1, u"Yara规则库存在，准备分析文件")

    # 开始yara检测线程
    def startYaraThread(self, filename, filetype, md5, index):
        # return
        filename = filename#.encode('cp936')
        typepe   = 'executable' # PE文件
        typesh   = 'text' # 文本&脚本文件
        # 开始可疑字符检查
        strcheck = GetFileString(filename)
        r = strcheck.getResult()
        # 解析返回元组
        self.analyzeSusString(r)
        sqlcursor = self.readYaraResultDB(md5)
        if sqlcursor:
            print "yara_result exist"
            return
        if typepe in filetype:
            print "---------PE----------"
            # PE文件检测malware特征,antidbg特征
            self.checkMalwThread = CheckMalware(filename, md5)
            self.checkMalwThread.valueSignal.connect(self.recvYaraResult)
            self.checkMalwThread.start()
            self.checkMalwThread.wait()
        # elif typesh in filetype: # 文本类型检测webshell特征
        else:
            print "---------SH----------"
            self.checkShelThread = CheckWebshell(filename, md5)
            self.checkShelThread.valueSignal.connect(self.recvYaraResult)
            self.checkShelThread.start()
            self.checkShelThread.wait()
    
    '''
    获取yara数据库信息
    1.插入默认yara检测数据时使用
    2.run方法汇总时使用
    '''
    def readYaraResultDB(self, md5):
        try:
            sqlconn = sqlite3.connect("../db/detected.db")
        except sqlite3.Error, e:
            print "sqlite connect failed", "\n", e.args[0]
        sqlcursor = sqlconn.cursor()
        sqlcursor.execute("select * from yara_result where md5=?", (md5,))
        sqlconn.commit()
        sqlcursor = sqlcursor.fetchone()
        return sqlcursor

    # 获取yara检测结果
    # 在该接收函数中应该处理汇总的信息
    def recvYaraResult(self, msg):
        print "get result from yarathread"
        print msg

    '''
    解析可疑字符返回内容
    r[0]:ip地址
    r[1]:网址
    r[2]:邮箱
    '''
    def analyzeSusString(self, result):
        ipaddr = list(set(result[0]))
        websit = list(set(result[1]))
        email  = list(set(result[2]))
        self.sendmsg = self.filename + " File Analysis Result:\n"
        sendm = ''
        # print result
        if len(ipaddr):
            sendm += "\t\t--------suspicious ip address--------\n"
            for i in ipaddr:
                sendm += "\t\t{}\n".format(str(i))
        if len(websit):
            sendm += "\t\t----------suspicious websit----------\n"
            for i in websit:
                sendm += "\t\t{}\n".format(str(i))
        if len(email):
            sendm += "\t\t-------suspicious email address------\n"
            for i in email:
                sendm += "\t\t{}\n".format(str(i))
        self.sendmsg += sendm
        # self.flogSignal.emit(3, sendm)

    '''
    使用clamav数据库规则检测
    主要用于对已知病毒文件检测
    '''
    def startClamThread(self, filename, index):
        print "use clamav signature"
        filename = filename#.encode('cp936')
        self.checkClamThread = CheckClamav(filename)
        self.checkClamThread.valueSignal.connect(self.recvClamResult)
        self.checkClamThread.start()
        self.checkClamThread.wait()

    def recvClamResult(self, msg):
        pass

    def startPackThread(self, filename, index, md5):
        sqlcursor = self.readYaraResultDB(md5)
        if sqlcursor[2]:
            print "packed result exist"
            return
        print "start check pack"
        filename = filename#.encode('cp936')
        self.checkPackThread = CheckPacker(filename, index, md5)
        self.checkPackThread.valueSignal.connect(self.recvYaraResult)
        self.checkPackThread.start()
        self.checkPackThread.wait()

    def startCrypThread(self, filename, index, md5):
        sqlcursor = self.readYaraResultDB(md5)
        if sqlcursor[3]:
            print "crypto result exist"
            return
        print "start check crypto"
        filename = filename#.encode('cp936')
        self.checkCrypThread = CheckCrypto(filename, md5)
        self.checkCrypThread.valueSignal.connect(self.recvYaraResult)
        self.checkCrypThread.start()
        self.checkCrypThread.wait()

    def startCustThread(self, filename, index, md5):
        filename = filename#.encode('cp936')
        self.checkCustThread = Checkcustom(filename, md5)
        self.checkCustThread.valueSignal.connect(self.recvYaraResult)
        self.checkCustThread.start()
        self.checkCustThread.wait()

    '''
    yara分析结果汇总
    '''
    def yaraDetectionResult(self, result):
        yarscore = 0
        string = [] # 结果概述
        print result
        if result[1] == "null":
            print "not malware or antidbg, not webshell, not documentmal"
        else:
            if dict(eval(result[1])).has_key("malware"):
                yarscore += len(set(YaraAlert.malalerts.keys()) & set(dict(eval(result[1]))["malware"]))
            if dict(eval(result[1])).has_key("antidbg"):
                yarscore += len(set(YaraAlert.atialerts.keys()) & set(dict(eval(result[1]))["antidbg"]))
            print dict(eval(result[1]))
        if result[2]:
            yarscore += len(set(YaraAlert.pkdalerts.keys()) & set(dict(eval(result[2]))["packed"]))
            if 'IsPacked' in result[2]:
                yarscore += 5
            if 'HasModified_DOS_Message' in result[2]:
                yarscore += 15
            print dict(eval(result[2]))
        if result[3]:
            yarscore += len(set(YaraAlert.cptalerts.keys()) & set(dict(eval(result[3]))["crypto"]))
            print dict(eval(result[3]))
        return yarscore

    '''
    汇总分析结果
    '''
    def collectAnalyzResult(self):
        pass

    '''
    文件分析总控
    判断执行何种分析功能
    '''
    def analysisControl(self, index):
        i = index
        # 默认规则换成yara
        # PE-Malware+antidbg
        # SH-Webshell  
        self.startYaraThread(self.filename, self.filetype, self.md5, i)
        # 分析pe文件--影响self.score值
        if 1 == self.pealflag:
            self.startDefaultThread(self.filename, self.filetype, self.md5, i)
        # 检查是否存在可疑的加密记号
        if 1 == self.crypflag:
            self.startCrypThread(self.filename, i, self.md5)
        # 检查可能加壳记号
        if 1 == self.Packflag:
            self.startPackThread(self.filename, i, self.md5)
        if 1 == self.selfflag:
            print "going to use custom rule"
            self.startCustThread(self.filename, i, self.md5)
        yararst = self.readYaraResultDB(self.md5)
        yarscore = self.yaraDetectionResult(yararst)
        return yarscore
        # print yararst

    def run(self):
        # import random
        self.chooseScanRule(self.scanrule)
        self.checkYaraExists()
        # 判断来自文件夹or文件选择
        # 文件选择发送list信号
        if isinstance(self.filelist, tuple):
            print "datebase update"
            # print self.filelist
            for i in range(len(self.filelist[1])):
                time.sleep(0.2)
                # print self.filelist[1][i]
                try:
                    sqlconn = sqlite3.connect("../db/fileinfo.db")
                except sqlite3.Error, e:
                    print "sqlite connect failed" , "\n", e.args[0]
                sqlcursor = sqlconn.cursor()
                sqlcursor.execute("select * from base_info where id=?", (self.filelist[1][i],))
                sqlconn.commit()
                sqlcursor = sqlcursor.fetchone()
                sqlconn.close()
                self.filename = sqlcursor[1]
                self.md5      = sqlcursor[5]
                self.filetype = sqlcursor[3]
                self.filesize = sqlcursor[2]
                print "----------------", "\n", self.filename
                # file size should less than 100M
                # file type should be supported
                typeflag = 0
                for t in StaticValue.typesupport:
                    if t in self.filetype:
                        typeflag = 1
                        break
                if int(self.filesize) < 100*1024*1024 and typeflag:
                    s = self.analysisControl(i)
                else:
                    self.sendmsg = "unsupport type"
                    s = -1
                self.update4DataBse(self.filelist[1][i], s, time.time())
                self.fileSignal.emit(self.filelist[1][i], str(i + 1))
                self.flogSignal.emit(2, self.sendmsg)
            return
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
                sqlcursor.execute("insert into base_info (id, name) values(?, ?)", (int(sqlindex), sfilename))
                sqlindex += 1
            sqlconn.commit()
            sqlconn.close()
            self.filelist = len(self.filelist)
        for i in range(self.filelist):
            time.sleep(0.2)
            # print i, FlagSet.scansqlcount
            FlagSet.scansqlcount = FlagSet.scansqlcount + 1
            self.filename = self.readFromDataBase(FlagSet.scansqlcount)
            self.infos, useless = getFileInfo(str(self.filename))#.encode('cp936'))
            if "error" == self.infos[0]:
                print u"可能扫描到临时生成的文件"
                continue
            self.md5      = self.infos[0]
            self.filetype = self.infos[4]
            self.filesize = self.infos[3]
            # file size should less than 100M
            # file type should be supported
            typeflag = 0
            for t in StaticValue.typesupport:
                if t in self.filetype:
                    typeflag = 1
                    break    
            if int(self.filesize) < 100*1024*1024 and typeflag:
                self.score = self.analysisControl(i)
            else:
                self.sendmsg = "unsupport type"
                self.score = -1
            self.write2DataBase(FlagSet.scansqlcount, self.infos, self.score, time.time())
            # print FlagSet.scanstopflag
            if 0 == FlagSet.scanstopflag:
                # 发送filelist长度在ui线程中标记结束
                self.fileSignal.emit(self.filelist, self.filename)
                self.flogSignal.emit(2, self.sendmsg)
                break
            self.fileSignal.emit(i+1, self.filename)
            self.flogSignal.emit(2, self.sendmsg)