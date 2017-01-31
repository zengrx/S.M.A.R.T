#coding=utf-8
import os

def iterateFIles(dir):
    assert os.path.isdir(dir), "make sure this is a path"
    result = []
    i = 0
    for root, dirs, files in os.walk(dir, topdown=True):
        for fl in files:
            result.append(os.path.join(root, fl))
            i = i + 1
    #return result
    return i

print iterateFIles('E:\\git')
