#coding=utf-8

import sys, os
import scipy.misc
import array
import numpy

def getBinFiles(rootdir):
    for root, dirs, files in os.walk(rootdir, topdown=True):
        for fi in files:
            path = os.path.join(root, fi)
            print fi, path
            convertBin2Img(path, 2048, fi)

def convertBin2Img(filename, width, n):
    f = open(filename, 'rb')
    ln = os.path.getsize(filename)
    rem = ln % width
    a = array.array("B")
    a.fromfile(f, ln - rem)
    f.close()
    g = numpy.reshape(a, (len(a) / width, width))
    g = numpy.uint8(g)
    imgname = './wanacry/' + n + '.png'
    print imgname
    scipy.misc.imsave(imgname, g)

if __name__ == "__main__":
    f = '/home/amber/code/samples/GameSetup.exe'
    w = 256
    # convertBin2Img(f, w)
    getBinFiles('/home/amber/code/samples/wannacry_switchkill')