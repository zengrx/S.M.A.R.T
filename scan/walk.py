#coding=utf-8
import os

def iterateFIles(dir):
    assert os.path.isdir(dir), "make sure this is a path"
    result = []
    for root, dirs, files in os.walk(dir, topdown=True):
        for fl in files:
            result.append(os.path.join(root, fl))

    return result

print iterateFIles('../../')