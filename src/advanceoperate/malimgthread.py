#coding=utf-8

from PyQt4 import QtCore
import os, glob, numpy, sys
from PIL import Image
from sklearn.cross_validation import StratifiedKFold
from sklearn.metrics import confusion_matrix
from sklearn.neighbors import KNeighborsClassifier
from sklearn.neighbors import BallTree
from sklearn import cross_validation
from sklearn.utils import shuffle
import sklearn
import leargist
import cPickle
import random

import sys
reload(sys)
sys.setdefaultencoding( "utf-8" )

class ValidationResult(QtCore.QThread):
    finishSignal = QtCore.pyqtSignal(list)

    def __init__(self, filename, parent=None):
        super(ValidationResult, self).__init__(parent)
        self.filename = str(filename)#.encode('cp936')
    
    def run(self):
        pass

class MalwareImageClass(QtCore.QThread):
    malwarSignal = QtCore.pyqtSignal(int, list)
    concluSignal = QtCore.pyqtSignal(int, list)


    def __init__(self, filename, parent=None):
        super(MalwareImageClass, self).__init__(parent)
        self.filename = str(filename)#.encode('cp936')
        self.feature = ''

    '''
    获取训练结果
    特征,标签,文件名称及相应的序号
    '''
    def getClassifyLabel(self):
        X = numpy.load("./datafiles/img_features.npy") # 特征
        y = numpy.load("./datafiles/img_labels.npy") # 标签
        n = cPickle.load(open("./datafiles/img.p","rb")) # 标号
        l = cPickle.load(open("./datafiles/imglabel.p", "rb")) # [家族号, 家族中序号, 文件名, 总序号]
        return X, y, n ,l

    '''
    对图片进行分类
    train@训练集特征
    label@训练集标签
    '''
    def classifyImage(self, feature_X, label_y, number):
        im = Image.open(self.filename)
        im1 = im.resize((64,64), Image.ANTIALIAS); # 转换为64x64
        des = leargist.color_gist(im1); # 960 values
        feature = des[0:320]; # 生成灰阶图，只需要前320内容
        query_feature = feature.reshape(1, -1)
        self.feature = query_feature
        # 获取特征和标签
        X = feature_X
        y = label_y
        n = number
        n_neighbors = 5; # better to have this at the start of the code
        knn = KNeighborsClassifier(n_neighbors, weights='distance')
        knn.fit(X, y)
        num = int(knn.predict(query_feature))
        classname = n[num]
        proba = knn.predict_proba(query_feature)
        msg = [num, classname, proba]
        self.malwarSignal.emit(1, msg)

    '''
    balltrees寻找数据集中最相近的样本
    返回距离值及样本标签号
    '''
    def findMostSimilarImg(self, feature_X, serial):
        X = feature_X
        b = BallTree(X)
        # 5个最相近的样本
        dist, ind = b.query(self.feature, k=3)
        print dist, ind
        ind = ind[0]
        # print ind
        l = serial
        imgs = []
        for rank in ind:
            # print rank
            for name in l:
                if rank == name[3]:
                    # print name
                    imgs.append(name[2])
        self.concluSignal.emit(2, imgs)

    def run(self):
        X, y, n ,l = self.getClassifyLabel()
        self.classifyImage(X, y, n)
        self.findMostSimilarImg(X, l)
