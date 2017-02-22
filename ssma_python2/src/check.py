import os, sys
import yara

def is_file_packed(filename):
    if not os.path.exists("../ssma_python2/rules_compiled/Packers"):
        os.mkdir("../ssma_python2/rules_compiled/Packers")
    for n in os.listdir("../ssma_python2/rules/Packers"):
        rule = yara.compile("../ssma_python2/rules/Packers/" + n)
        rule.save("../ssma_python2/rules_compiled/Packers/" + n)
        rule = yara.load("../ssma_python2/rules_compiled/Packers/" + n)
        m = rule.match(filename)
        if m:
            return m


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
