#coding=utf-8

from PyQt4 import QtCore
from sklearn.ensemble import RandomForestClassifier as RF
from sklearn import cross_validation
from collections import *
import pandas as pd
import numpy as np
import re, os

import sys
reload(sys)
sys.setdefaultencoding( "utf-8" )

class CrossValidation(QtCore.QThread):
    finishSignal = QtCore.pyqtSignal(str)

    def __init__(self, parent=None):
        super(CrossValidation, self).__init__(parent)
        # self.filename = str(filename)#.encode('cp936')

    def getCrossVadLabel(self):
        subtrainLabel = pd.read_csv("./datafiles/subtrainLabels.csv")
        subtrainfeature = pd.read_csv("./datafiles/3gramfeature.csv")
        subtrain = pd.merge(subtrainLabel, subtrainfeature, on='Id')
        labels = subtrain.Class
        subtrain.drop(["Class","Id"], axis=1, inplace=True)
        # print subtrain
        subtrain = subtrain.as_matrix()
        print "..."
        return labels, subtrain

    def calculateCrossVad(self, labels, subtrain):
        X_train, X_test, y_train, y_test = cross_validation.train_test_split(subtrain,labels,test_size=0.1)
        # print X_test, y_test
        srf = RF(n_estimators=500, n_jobs=-1)
        srf.fit(X_train,y_train)
        score = srf.score(X_test,y_test)
        return score

    def run(self):
        lab, train = self.getCrossVadLabel()
        scr = str(self.calculateCrossVad(lab, train))
        self.finishSignal.emit(scr)

class OpcodeNgram(QtCore.QThread):
    opcodeSignal = QtCore.pyqtSignal(list)
    concluSignal = QtCore.pyqtSignal(list)

    def __init__(self, filename, parent=None):
        super(OpcodeNgram, self).__init__(parent)
        self.filename = str(filename)#.encode('cp936')
        self.trainlabel = None # 训练子集标签
        self.trainfeatu = None # 训练子集特征
    
    '''
    获取训练分类标签信息
    操作码频数合并训练特征
    '''
    def getClassifyLabel(self, t3gram):
        self.trainfeatu = pd.read_csv("./datafiles/3gramfeature.csv")
        self.trainlabel = pd.read_csv('./datafiles/subtrainLabels.csv')
        # 取csv文件的第一行中除去id列，并转化为list
        features = self.trainfeatu.columns.tolist()[1:]
        newdata = {}
        for feature in features:
            feature = tuple(eval(feature)) # 转""数据为元组
            if feature in t3gram.keys():
                # print "get"
                newdata[feature] = t3gram[feature] # 传递统计数值
            else:
                newdata[feature] = 0
        newdata = sorted(newdata.items()) # 以特征元组规定顺序排序
        return newdata

    '''
    获取汇编代码中的操作码序列
    '''
    def getOpcodeSequence(self, filename):
        opcode_seq = []
        p = re.compile(r'\s([a-fA-F0-9]{2}\s)+\s+([a-z]+)') # 需要再匹配一个制表符
        with open(filename) as f:
            for line in f:
                if line.startswith(".text"): # or line.startswith(".code") or line.startswith("CODE"): # 指定解析代码行
                    m = re.findall(p,line)
                    if m:
                        # print m # 结果匹配opcode及前一个制表符16进制数据
                        # eg:[('FF\t', 'jmp')]
                        opc = m[0][1]
                        if opc != "align":
                            opcode_seq.append(opc)
        return opcode_seq

    '''
    N元语法化汇编操作码序列
    @ops:操作码
    @n:n元化参数
    操作码序列为元组形式
    返回组合后counter的字典
    '''
    def getOpcodeNgram(self, ops, n=3):
        opngramlist = [tuple(ops[i:i+n]) for i in range(len(ops)-n)]
        opngram = Counter(opngramlist)
        return opngram

    '''
    矩阵化操作码序列
    @opngram:{操作码序列-频数}字典
    '''
    def opSequece2Matrix(self, opngram):
        finallist = []
        for i in opngram:
            finallist.append(i[1])
        print len(finallist)
        dd = np.array(finallist).reshape(1, -1)
        return dd

    def randomForestClassify(self, matrix):
        subtrainLabel = self.trainlabel
        subtrainfeature = self.trainfeatu
        subtrain = pd.merge(subtrainLabel, subtrainfeature, on='Id')
        labels = subtrain.Class
        subtrain.drop(["Class","Id"], axis=1, inplace=True)
        # print subtrain
        subtrain = subtrain.as_matrix()
        print "..."
        # X_train, X_test, y_train, y_test = cross_validation.train_test_split(subtrain,labels,test_size=0.1)
        srf = RF(n_estimators=500, n_jobs=-1)
        # srf.fit(X_train,y_train)
        # print srf.score(X_test,y_test)
        srf.fit(subtrain, labels)
        print srf.predict(matrix)
        predict = srf.predict(matrix).tolist()
        print srf.predict_proba(matrix)
        proba = srf.predict_proba(matrix).tolist()[0]
        return [predict, proba]
        print srf.predict_log_proba(matrix)

    def run(self):
        tops = self.getOpcodeSequence(self.filename)
        t3gram = self.getOpcodeNgram(tops)
        for op in t3gram:
            if t3gram[op] > 5:
                va = [op, t3gram[op]]
                self.opcodeSignal.emit(va)
        data = self.getClassifyLabel(t3gram)
        matrix = self.opSequece2Matrix(data)
        ret = self.randomForestClassify(matrix)
        self.concluSignal.emit(list(ret))