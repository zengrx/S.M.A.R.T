import yara
import os
import sys
 
def getRules(path):
    filepath = {}
    for index,file in enumerate(os.listdir(path)):
        rupath = os.path.join(path, file)
        key = "rule"+str(index)
        filepath[key] = rupath
    yararule = yara.compile(filepaths=filepath)
    return yararule
 
def scan(rule, path):
    for file in os.listdir(path):
        mapath = os.path.join(path, file)
        fp = open(mapath, 'rb')
        matches = rule.match(data=fp.read())
        if len(matches)>0:
            print file,matches
 
if __name__ == '__main__':
    rulepath = sys.argv[1]
    malpath = sys.argv[2]
    yararule = getRules(rulepath)
scan(yararule, malpath)