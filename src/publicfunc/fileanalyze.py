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
    with open(filename, 'rb') as f:
        cfile = f.read()
        # 分割文件名与路径
        p, f  = os.path.split(str(filename).decode('cp936'))
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
        
        file_magic = magic.Magic(magic_file="../libs/magic.mgc")
        # ftype  = 
        infoo.append(file_magic.from_file(filename))
        infof.append("Type:\t{}".format(file_magic.from_file(filename)))
    return infoo, infof

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
        nowdate = int(time.gmtime(time.time())[0])
        # 怀疑的编译时间
        if filedate > nowdate or filedate < 1995:
            return filedate

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
        # for n in ret1:
        #     if n:
        #         n = n.decode()
        #         if any(map(n.startswith, self.alerts.keys())):
        #             for a in self.alerts:
        #                 if n.startswith(a):
        #                     ret2.append("{}^{}".format(n, self.alerts.get(a)))
        # return ret2
        # -------------
        # self.alerts use ImpAlert.alerts now
        # -------------

    '''
    检查pe文件节信息
    '''
    def checkFileSections(self):
        # 立两个flag
        entropyflag  = False
        datasizeflag = False
        # 储存变量的list
        virtualSize  = []
        sectionName  = []
        pefileinfos  = []
        # 认可的节名称
        goodsection  = ['.data', '.text', '.code', '.reloc', '.idata', '.edata', '.rdata', '.bss', '.rsrc']
        # 获取文件节个数
        numofsection = self.pe.FILE_HEADER.NumberOfSections
        if numofsection < 1 or numofsection > 9:
            print "suspicious number os sections"
        else:
            print "number of sections: ", numofsection
        pefileinfos.append(numofsection)
        for section in self.pe.sections:
            secname = section.Name.strip(b"\x00").decode(errors='ignore')
            sectionName.append(secname)
            entropy = section.get_entropy()
            subentropyflag = False
            if entropy < 1 or entropy > 7:
                entropyflag = True
                subentropyflag = True
            try:
                if section.Misc_VirtualSize / section.SizeOfRawData > 10:
                    virtualSize.append((secname, section.Misc_VirtualSize))
            except:
                if section.SizeOfRawData == 0 and section.Misc_VirtualSize > 0:
                    datasizeflag = True
                    virtualSize.append((section.Name.strip(b"\x00").decode(errors='ignore'), section.Misc_VirtualSize))
            pefileinfos.append(section.Name.strip(b"\x00").decode(errors='ignore'))
            pefileinfos.append(hex(section.VirtualAddress))
            pefileinfos.append(section.Misc_VirtualSize)
            pefileinfos.append(section.SizeOfRawData)
            pefileinfos.append(str(entropy))

        if virtualSize:
            for n, m in virtualSize:
                print 'SUSPICIOUS size of the section "{}" when stored in memory - {}'.format(n, m)
        if entropyflag:
            print "very high or very low entropy means that file or section is compressed or encrypted since truly data is not common."
        if datasizeflag:
            print "suspicious size of the raw data: 0"
        badsections = [bad for bad in sectionName if bad not in goodsection]
        if badsections:
            print "suspicious section names:"
            for n in badsections:
                print n,
            print ""
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
    valueSignal  = QtCore.pyqtSignal(list)

    def __init__(self, filename, index, parent=None):
        super(DefaultAnalyze, self).__init__(parent)
        self.filename = filename

    def test(self):
        peAnalize = PEFileAnalize(self.filename)
        print peAnalize.checkEntryPoint()
        # print peAnalize.checkFileDate()
        # print peAnalize.checkFileHeader()
        print peAnalize.checkFileImports()
        # print peAnalize.checkFileSections()

    def run(self):
        print "run function in defaultanalyze class"
        self.test()