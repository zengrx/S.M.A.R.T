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

    def __init__(self, parent=None):
        super(ValidationResult, self).__init__(parent)

    def getClassifyLabel(self):
        X = numpy.load("./datafiles/img_features.npy") # 特征
        y = numpy.load("./datafiles/img_labels.npy") # 标签
        n = cPickle.load(open("./datafiles/img.p","rb")) # 标号
        l = cPickle.load(open("./datafiles/imglabel.p", "rb")) # [家族号, 家族中序号, 文件名, 总序号]
        return X, y, n ,l

    '''
    准备绘制矩阵的数据
    @X:特征矩阵
    @y:标签
    @n:所有样本家族名称
    @l:对应家族个数
    '''
    def prepareData2Matrix(self, X, y, n, l):
        n_samples, useless = X.shape 
        p = range(n_samples)
        random.seed(random.random())
        random.shuffle(p)
        X, y = X[p], y[p] # 打乱数组
        kfold = 10 # 10重
        skf = StratifiedKFold(y,kfold)
        skfind = [None] * len(skf)
        cnt = 0
        for train_index in skf:
            skfind[cnt] = train_index
            cnt += 1
        list_fams = n
        cache = []
        no_imgs = []
        for l_list in l:
            if 0 == l_list[1]:
                # print l[l_list[3] - 1]
                # print l_list
                cache.append(l[l_list[3] - 1][1] + 1)
        no_imgs = cache[1:len(cache)]
        no_imgs.append(cache[0])
        # print no_imgs # 输出所有家族包含文件个数
        conf_mat = numpy.zeros((len(no_imgs), len(no_imgs))) # 初始化矩阵
        n_neighbors = 5
        # 10-fold Cross Validation
        for i in range(kfold):
            train_indices = skfind[i][0]
            test_indices = skfind[i][1]
            clf = []
            clf = KNeighborsClassifier(n_neighbors, weights='distance') 
            X_train = X[train_indices]
            y_train = y[train_indices]
            X_test = X[test_indices]
            y_test = y[test_indices]
            # Training
            import time
            tic = time.time()
            clf.fit(X_train,y_train) 
            toc = time.time()
            print "training time= ", toc-tic # roughly 2.5 secs
            # Testing
            y_predict = []
            tic = time.time()
            y_predict = clf.predict(X_test) # output is labels and not indices
            toc = time.time()
            print "testing time = ", toc-tic # roughly 0.3 secs
            # Compute confusion matrix
            cm = []
            cm = confusion_matrix(y_test,y_predict)
            conf_mat = conf_mat + cm
        return conf_mat, no_imgs, list_fams
    
    def run(self):
        print "start draw"
        X, y, n, l = self.getClassifyLabel()
        cm, nimg, listf = self.prepareData2Matrix(X, y, n, l)
        msg = [cm, nimg, listf]
        self.finishSignal.emit(msg)

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
