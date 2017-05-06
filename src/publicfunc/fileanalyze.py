#coding=utf-8

import sys, os
import time
from PyQt4 import QtCore, QtGui
import hashlib
import numbers
import array
import math
import pefile
import magic
import sqlite3
import re
import urlparse
import Queue
import threading
sys.path.append("../")
from globalset import ImpAlert

'''
通用除法操作
可统一py2/3
'''
def commonDiv(a, b):
    if isinstance(a, numbers.Integral) and isinstance(b, numbers.Integral):
        return a // b
    else:
        return a / b

'''
计算数据信息熵
return熵值
'''
def dataEntropy(data):
    if 0 == len(data):
        return 0.0
    arr = array.array('L', [0] * 256)
    for i in data:
        arr[i if isinstance(i, int) else ord(i)] += 1
    entropy = 0
    for i in arr:
        if i:
            p_i = commonDiv(float(i), len(data))
            entropy -= p_i * math.log(p_i, 2)
    return entropy

'''
获取文件详细信息
infoo:原始数据 返回MD5 SHA1 SHA256 Size Type
infof:格式化   返回Name Path ...
'''
def getFileInfo(filename):
    infoo = [] # origin data
    infof = [] # format data
    if os.path.exists(filename):
        with open(filename, 'rb') as f:
            cfile = f.read()
            # 分割文件名与路径
            p, f  = os.path.split(str(filename))#.decode('cp936'))
            # name   =
            infof.append("Name:\t{}".format(f))
            # path   =
            infof.append("Path:\t{}".format(p))
            # md5    =
            infoo.append(hashlib.md5(cfile).hexdigest())
            infof.append("MD5:\t{}".format(hashlib.md5(cfile).hexdigest()))
            # sha1   = 
            infoo.append(hashlib.sha1(cfile).hexdigest())
            infof.append("SHA1:\t{}".format(hashlib.sha1(cfile).hexdigest()))
            # sha256 = 
            infoo.append(hashlib.sha256(cfile).hexdigest())
            infof.append("SHA256:\t{}".format(hashlib.sha256(cfile).hexdigest()))
            # fsize  = 
            infoo.append(os.path.getsize(filename))
            infof.append("Size:\t{} Bytes".format(os.path.getsize(filename)))
            
            # file_magic = magic.Magic(magic_file="../libs/magic.mgc")
            # ftype  = 
            infoo.append(magic.from_file(filename))
            infof.append("Type:\t{}".format(magic.from_file(filename)))
        return infoo, infof
    else:
        print "file " + filename + "not exist!"
        return ["error"], ["error"]
        
class GetFileString:
    def __init__(self, filename):
        self.filename = filename
        self.chars    = b"A-Za-z0-9!\"#$%&'()*+,-./:;<=>?@[\\]^_`{|}~ "
        self.short_t  = 4
        self.regexp   = '[{}]{{{},}}'.format(self.chars.decode(), self.short_t).encode()
        self.pattern  = re.compile(self.regexp)

        with open(self.filename, 'rb') as f:
            fbytes = self.fileProcess(f)
            fstr   = []
            for n in fbytes:
                fstr.append(n.decode())
        self.result = (self.checkIPAddr(fstr), self.checkWebsit(fstr), self.checkEmail(fstr))
        
    def fileProcess(self, filename):
        data = filename.read()
        return self.pattern.findall(data)

    def getResult(self):
        return self.result

    def checkIPAddr(self, strlist):
        ippattern = re.compile(r'((([01]?[0-9]?[0-9]|2[0-4][0-9]|25[0-5])[ (\[]?(\.|dot)[ )\]]?){3}([01]?[0-9]?[0-9]|2[0-4][0-9]|25[0-5]))')
        f = filter(ippattern.match, strlist)
        return list(f)

    def checkWebsit(self, strlist):
        websit = []
        for n in strlist:
            try:
                netloc = urlparse.urlparse(n.split()[0]).netloc
                if netloc and "." in netloc and not netloc.startswith(".") and not netloc.endswith("."):
                    websit.append(netloc)
            except:
                pass
        websit = list(set(websit))
        return websit

    def checkEmail(self, strlist):
        email = re.compile(r'(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)')
        f = filter(email.match, strlist)
        return list(f)

class PEFileAnalize:
    def __init__(self, filename):
        self.filename = filename
        self.pe = pefile.PE(self.filename)
        with open(self.filename, 'rb') as alzfile:
            self.totalentropy = dataEntropy(alzfile.read())

    '''
    检查文件编译时间
    '''
    def checkFileDate(self):
        pedate = self.pe.FILE_HEADER.TimeDateStamp
        filedate = int(time.ctime(pedate).split()[-1])
        return filedate

    '''
    查看运行平台
    '''
    def checkMachine(self):
        machine = self.pe.FILE_HEADER.Machine
        if 0x14c == machine:
            return 32
        elif 0x8664 == machine:
            return 64
        else:
            return -1

    '''
    检查文件入口点
    '''
    def checkEntryPoint(self):
        return hex(self.pe.OPTIONAL_HEADER.AddressOfEntryPoint)

    '''
    检查文件导入表内容
    返回导入表{键-值}:{dll-API}
    '''
    def checkFileImports(self):
        ret1 = [] # api信息
        ret2 = [] # alert信息
        ret3 = {} # {dll-API}信息
        if not hasattr(self.pe, 'DIRECTORY_ENTRY_IMPORT'):
            return ret1
        for lib in self.pe.DIRECTORY_ENTRY_IMPORT:
            for imp in lib.imports:
                ret1.append(imp.name)
            ret3[lib.dll] = ret1
        return ret3

    '''
    检查pe文件节信息
    '''
    def checkFileSections(self):
        # 立两个flag
        entropyflag  = False
        datasizeflag = False
        # 储存变量的list
        virtualSize  = []
        pefileinfos  = []
        # 获取文件节个数
        numofsection = self.pe.FILE_HEADER.NumberOfSections
        pefileinfos.append(numofsection)
        for section in self.pe.sections:
            entropy = section.get_entropy()
            pefileinfos.append(section.Name.strip(b"\x00").decode(errors='ignore'))
            pefileinfos.append(hex(section.VirtualAddress))
            pefileinfos.append(section.Misc_VirtualSize)
            pefileinfos.append(section.SizeOfRawData)
            pefileinfos.append(str(entropy))
        return pefileinfos

    def checkFileHeader(self):
        debugflag      = False # 包含调试信息
        suspiciousflag = False # 可疑标志
        if self.pe.FILE_HEADER.PointerToSymbolTable > 0:
            debugflag = True
            
        flags = [("BYTES_REVERSED_LO", self.pe.FILE_HEADER.IMAGE_FILE_BYTES_REVERSED_LO,
                  "Little endian: LSB precedes MSB in memory, deprecated and should be zero."),
                 ("BYTES_REVERSED_HI", self.pe.FILE_HEADER.IMAGE_FILE_BYTES_REVERSED_HI,
                  "Big endian: MSB precedes LSB in memory, deprecated and should be zero."),
                 ("RELOCS_STRIPPED", self.pe.FILE_HEADER.IMAGE_FILE_RELOCS_STRIPPED,
                  "This indicates that the file does not contain base relocations and must therefore be loaded at its preferred base address.\nFlag has the effect of disabling Address Space Layout Randomization(ASPR) for the process.")]
        if any(tr[1] for tr in flags):
            sussuspiciousflag = True
            for n in flags:
                if n[1]:
                    print n[0] + "flag is set - {}".format(n[2])

class DefaultAnalyze(QtCore.QThread):
    numberSignal = QtCore.pyqtSignal(int, str)
    valueSignal  = QtCore.pyqtSignal(int, str)

    def __init__(self, filename, md5, index, parent=None):
        super(DefaultAnalyze, self).__init__(parent)
        self.filename  = filename
        self.md5       = md5
        self.peAnalize = PEFileAnalize(self.filename)

    # PE文件分析测试函数
    def test(self):
        peAnalize = PEFileAnalize(self.filename)
        # peAnalize.checkEntryPoint()
        peAnalize.checkFileDate()
        # peAnalize.checkFileHeader()
        peAnalize.checkFileImports()
        peAnalize.checkFileSections()
    
    def func1(self, q):
        result1 = self.peAnalize.checkFileDate()
        result2 = self.peAnalize.checkEntryPoint()
        result3 = self.peAnalize.checkMachine()
        q.put((1, result1, result2, result3))

    def func2(self, q):
        result = self.peAnalize.checkFileImports()
        q.put((2, result))

    def func3(self, q):
        result = self.peAnalize.checkFileSections()
        q.put((3, result))

    # python threading模块测试函数
    # 三个子函数时比顺序执行平均快3秒 
    def PEThreadControl(self, q):
        tlist = []
        t1 = threading.Thread(target=self.func1, args=(q,))
        tlist.append(t1)
        t2 = threading.Thread(target=self.func2, args=(q,))
        tlist.append(t2)
        t3 = threading.Thread(target=self.func3, args=(q,))
        tlist.append(t3)
        for i in tlist:
            i.start()
        for i in tlist:
            i.join()

    '''
    写入PE文件信息
    md5:文件md5值，作为数据库外键
    queue:PE分析线程队列
    return数据库执行结果
    -1:数据库连接失败
    -2:更新数据失败
     1:数据库更新成功
    '''
    def write2PEInfoDB(self, md5, queue):
        try:
            sqlconn = sqlite3.connect('../db/fileinfo.db')
        except sqlite3.Error, e:
            print "sqlite connect failed", "\n", e.args[0]
            return -1
        sqlcursor = sqlconn.cursor()
        try:            
            print "insert a new pe file info"
            sqlcursor.execute("insert into pe_info (md5) values(?)", (md5,))
            while(not queue.empty()):
                info = queue.get()
                if 1 == info[0]:
                    # print info[1], info[2]
                    sqlcursor.execute("update pe_info set cpltime=?, entrypnt=?, petype=? where md5=?", (info[1], info[2], info[3], md5))
                elif 2 == info[0]:
                    # print info[1]
                    sqlcursor.execute("update pe_info set impinfo=? where md5=?", (str(info[1]), md5))
                else:
                    # print info[1]
                    sqlcursor.execute("update pe_info set setinfo=? where md5=?", (str(info[1]), md5))
            sqlconn.commit()
            sqlconn.close()
            return 1
        except sqlite3.Error, e:
            print "error when read db data", "\n", e.args[0]
            return -2

    def run(self):
        print "run function in defaultanalyze class"
        # self.test()
        que = Queue.Queue()
        self.PEThreadControl(que)
        ret = self.write2PEInfoDB(self.md5, que)
        self.valueSignal.emit(ret, self.md5)