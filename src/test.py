import sys, os
from globalset import FilePath

reload(sys)
sys.setdefaultencoding("utf-8")

f = open(FilePath.whitelist, "r")
f.readline()
for line in f:
    print line