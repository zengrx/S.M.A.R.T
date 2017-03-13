#coding=utf-8

import os, sys
import yara

def is_file_packed(filename):
    i = 0 # 统计数量
    result = [] # 保存结果
    # 没有编译过yara规则时
    if not os.path.exists("../ssma_python2/rules_compiled/Packers"):
        os.mkdir("../ssma_python2/rules_compiled/Packers")
        for n in os.listdir("../ssma_python2/rules/Packers"):
            try:
                rule = yara.compile("../ssma_python2/rules/Packers/" + n)
                rule.save("../ssma_python2/rules_compiled/Packers/" + n)
                rule = yara.load("../ssma_python2/rules_compiled/Packers/" + n)
                m = rule.match(filename)
                if m:
                    i += 1
                    return m # m为装有match规则的list
            except:
                print "internal error"
    # 已经生成了yara规则的二进制文件
    else:
        print "use compiled file"
        for n in os.listdir("../ssma_python2/rules_compiled/Packers/"):
            try:
                rule = yara.load("../ssma_python2/rules_compiled/Packers/" + n)
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
    if not os.path.exists("../ssma_python2/rules_compiled/Crypto"):
        os.mkdir("../ssma_python2/rules_compiled/Crypto")
        for n in os.listdir("../ssma_python2/rules/Crypto"):
            rule = yara.compile("../ssma_python2/rules/Crypto/" + n)
            rule.save("../ssma_python2/rules_compiled/Crypto/" + n)
            rule = yara.load("../ssma_python2/rules_compiled/Crypto/" + n)
            m = rule.match(filename)
            if m:
                return m
    else:
        for n in os.listdir("../ssma_python2/rules_compiled/Crypto"):
            rule = yara.load("../ssma_python2/rules_compiled/Crypto/" + n)
            m = rule.match(filename)
            if m:
                return m


def is_malware(filename):
    if not os.path.exists("../ssma_python2/rules_compiled/malware"):
        os.mkdir("../ssma_python2/rules_compiled/malware")
        for n in os.listdir("../ssma_python2/rules/malware/"):
            if not os.path.isdir("../ssma_python2/" + n):
                try:
                    rule = yara.compile("../ssma_python2/rules/malware/" + n)
                    rule.save("../ssma_python2/rules_compiled/malware/" + n)
                    rule = yara.load("../ssma_python2/rules_compiled/malware/" + n)
                    m = rule.match(filename)
                    if m:
                        return m
                except:
                    pass  # internal fatal error or warning
            else:
                pass
    else:
        print "use compiled file"
        for n in os.listdir("../ssma_python2/rules_compiled/malware/"):
            try:
                rule = yara.load("../ssma_python2/rules_compiled/malware/" + n)
                m = rule.match(filename)
                if m:
                    return m
            except:
                print "yara internal error"
