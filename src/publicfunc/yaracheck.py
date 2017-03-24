#coding=utf-8

import sys, os
import yara
from PyQt4 import QtCore, QtGui
import sqlite3

reload(sys)
sys.setdefaultencoding( "utf-8" )

def is_file_packed(filename):
    i = 0 # 统计数量
    result = [] # 保存结果
    # 没有编译过yara规则时
    if not os.path.exists("rules_compiled/Packers"):
        os.mkdir("rules_compiled/Packers")
        for n in os.listdir("rules/Packers"):
            try:
                rule = yara.compile("rules/Packers/" + n)
                rule.save("rules_compiled/Packers/" + n)
                rule = yara.load("rules_compiled/Packers/" + n)
                m = rule.match(filename)
                if m:
                    i += 1
                    return m # m为装有match规则的list
            except:
                print "internal error"
    # 已经生成了yara规则的二进制文件
    else:
        print "use compiled file"
        for n in os.listdir("rules_compiled/Packers/"):
            try:
                rule = yara.load("rules_compiled/Packers/" + n)
                m = rule.match(filename)
                if m:
                    i += 1
                    return m
            except:
                print "yara internal error"


def is_malicious_document(filename):
    if not os.path.exists("rules_compiled/Malicious_Documents"):
        os.mkdir("rules_compiled/Malicious_Documents")
    for n in os.listdir("rules/Malicious_Documents"):
        rule = yara.compile("rules/Malicious_Documents/" + n)
        rule.save("rules_compiled/Malicious_Documents/" + n)
        rule = yara.load("rules_compiled/Malicious_Documents/" + n)
        m = rule.match(filename)
        if m:
            return m


def is_antidb_antivm(filename):
    if not os.path.exists("rules_compiled/Antidebug_AntiVM"):
        os.mkdir("rules_compiled/Antidebug_AntiVM")
        for n in os.listdir("rules/Antidebug_AntiVM"):
            rule = yara.compile("rules/Antidebug_AntiVM/" + n)
            rule.save("rules_compiled/Antidebug_AntiVM/" + n)
            rule = yara.load("rules_compiled/Antidebug_AntiVM/" + n)
            m = rule.match(filename)
            if m:
                return m
    else:
        for n in os.listdir("rules_compiled/Antidebug_AntiVM"):
            rule = yara.load("rules_compiled/Antidebug_AntiVM/" + n)
            m = rule.match(filename)
            if m:
                return m


def check_crypto(filename):
    if not os.path.exists("rules_compiled/Crypto"):
        os.mkdir("rules_compiled/Crypto")
        for n in os.listdir("rules/Crypto"):
            rule = yara.compile("rules/Crypto/" + n)
            rule.save("rules_compiled/Crypto/" + n)
            rule = yara.load("rules_compiled/Crypto/" + n)
            m = rule.match(filename)
            if m:
                return m
    else:
        for n in os.listdir("rules_compiled/Crypto"):
            rule = yara.load("rules_compiled/Crypto/" + n)
            m = rule.match(filename)
            if m:
                return m


def is_malware(filename):
    if not os.path.exists("rules_compiled/malware"):
        os.mkdir("rules_compiled/malware")
        for n in os.listdir("rules/malware/"):
            if not os.path.isdir(n):
                try:
                    rule = yara.compile("rules/malware/" + n)
                    rule.save("rules_compiled/malware/" + n)
                    rule = yara.load("rules_compiled/malware/" + n)
                    m = rule.match(filename)
                    if m:
                        return m
                except:
                    pass  # internal fatal error or warning
            else:
                pass
    else:
        print "use compiled file"
        for n in os.listdir("rules_compiled/malware/"):
            try:
                rule = yara.load("rules_compiled/malware/" + n)
                m = rule.match(filename)
                if m:
                    return m
            except:
                print "yara internal error"

class CheckPacker(QtCore.QThread):
    numberSignal = QtCore.pyqtSignal(int, str)
    valueSignal  = QtCore.pyqtSignal(list)

    def __init__(self, filename, index, parent=None):
        super(CheckPacker, self).__init__(parent)
        self.filename = filename
        self.index    = index
    
    def run(self):
        print self.index
        pkdresult = is_file_packed(self.filename)
        result = []
        if pkdresult:
            print "get pkdresult!"
            for n in pkdresult:
                # 能输出描述则输出描述
                # 否则直接输出规则名
                try:
                    print "{} - {}".format(n, n.meta['description'])
                except:
                    print n
                # 最终直接输出评估结果，数据库里存详细内容
            # self.valueSignal.emit(pkdresult)

            # 搞事情--数据库
            # try:
		    #     sqlite_conn = sqlite3.connect("E:\\git\\MalwareScan_local\\db\\yarainfo.db")
            # except sqlite3.Error, e:
            #     print "sqlite connect failed", "\n", e.args[0]	
            # sqlite_cursor = sqlite_conn.cursor()
            # sqlite_cursor.execute("insert into yara_result (id, name, yararule) values(?, ?, ?)", (self.index, self.filename, str(pkdresult)))
            # sqlite_conn.commit()
            # sqlite_conn.close()
            # print "write data success"
        else:
            print "no match"

class CheckMalware(QtCore.QThread):
    numberSignal = QtCore.pyqtSignal(int, str)
    valueSignal  = QtCore.pyqtSignal(list)

    def __init__(self, filename, parent=None):
        super(CheckMalware, self).__init__(parent)
        self.filename = filename
    
    def run(self):
        malresult = is_malware(self.filename)
        result = []
        if malresult:
            print "get malresult!"
            for n in malresult:
                try:
                    print "{} - {}".format(n, n.meta['description'])
                except:
                    print n
            # self.valueSignal.emit(malresult)
        else:
            print "no match"

class CheckCrypto(QtCore.QThread):
    numberSignal = QtCore.pyqtSignal(int, str)
    valueSignal  = QtCore.pyqtSignal(list)

    def __init__(self, filename, parent=None):
        super(CheckCrypto, self).__init__(parent)
        self.filename = filename

    def run(self):
        cptresult = check_crypto(self.filename)
        result = []
        if cptresult:
            print "get crypto!"
            for n in cptresult:
                try:
                    print "{} - {}".format(n, n.meta['description'])
                except:
                    print n
        else:
            print "no match"