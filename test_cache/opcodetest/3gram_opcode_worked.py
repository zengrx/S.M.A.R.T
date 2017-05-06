#coding=utf-8

from sklearn.ensemble import RandomForestClassifier as RF
from sklearn import cross_validation
from sklearn.metrics import confusion_matrix
from collections import *
import pandas as pd
import numpy as np
import re, os

import sys
reload(sys)
sys.setdefaultencoding( "utf-8" )

def getOpcodeSequence(filename):
    opcode_seq = []
    p = re.compile(r'\s([a-fA-F0-9]{2}\s)+\s+([a-z]+)') # 需要再匹配一个制表符
    with open(filename) as f:
        for line in f:
            if line.startswith(".text"): # 指定解析代码行
                m = re.findall(p,line)
                if m:
                    # print m # 结果匹配opcode及前一个制表符16进制数据
                    # eg:[('FF\t', 'jmp')]
                    opc = m[0][1]
                    #  and opc != "a" and opc != "db" and opc != "dword" and opc != "unicode" and opc != "dd" and opc != "word"
                    if opc != "align":
                        opcode_seq.append(opc)
    return opcode_seq

def getOpcodeNgram(ops, n=3):
    opngramlist = [tuple(ops[i:i+n]) for i in range(len(ops)-n)]
    opngram = Counter(opngramlist)
    return opngram

subtrainfeature = pd.read_csv("3gramfeature.csv")
# 取csv文件的第一行中除去id列，并转化为list
features = subtrainfeature.columns.tolist()[1:]
# print features

'''
9
iouyxgUJX7pjI1LBTSDF
IGX67kgpuNz8JD4Ciwd2
gGfFjZ8Xab24eQ6zADN1
ETH8lrLD7Yx05Wu16hcK
8
ESMo7G9RVnYNgB3fHdpP
EMaDXLFSlr9TyW68JNOz
56KhNHUTXZpryYaGqoj4
5102w8Hp4TRkWbIUXSgZ
7
EZ7FwiO2p4DCrH6SJYBT
ewsfhA3Dunp49SFNMoVR
DpNvYX1qedHLiQnRhF98
28U1hRkQ6Yl57493ZdXD
6
k9H1WjlnQPASt0mg25hB
K51kg4QuOW3zMeft7lXU
IZWuOMidGxg1HYNP9fJr
f0jhPJ2913c56yY4mwEi
5
e2r6IncxE1LQOKFGgphj
cIojVJGQOtrL0S1ApeDY
4UTMdcZkxzLvwygO8EuK
1KB3Z7gd5aN4Xmx8W0sf
'''

filepath = 'G:\\工程及其他\\train\\cIojVJGQOtrL0S1ApeDY.asm'
tops = getOpcodeSequence(filepath.encode('cp936'))
t3gram = getOpcodeNgram(tops)
# print t3gram
testdata = {}
for feature in features:
    # print feature
    # print t3gram[feature]
    feature = tuple(eval(feature)) # 转""数据为元组
    if feature in t3gram.keys():
        # print "get"
        testdata[feature] = t3gram[feature] # 传递统计数值
    else:
        testdata[feature] = 0
testdata = sorted(testdata.items()) # 以特征元组规定顺序排序
print testdata
# testdata = pd.DataFrame(testdata)
finallist = []
for i in testdata:
    finallist.append(i[1])
print len(finallist)
dd = np.array(finallist).reshape(1, -1)
print dd

subtrainLabel = pd.read_csv('subtrainLabels.csv')
subtrainfeature = pd.read_csv("3gramfeature.csv")
subtrain = pd.merge(subtrainLabel,subtrainfeature,on='Id')
labels = subtrain.Class
subtrain.drop(["Class","Id"], axis=1, inplace=True)
# print subtrain
subtrain = subtrain.as_matrix()
print "..."

X_train, X_test, y_train, y_test = cross_validation.train_test_split(subtrain,labels,test_size=0.1)
# print X_test, y_test
srf = RF(n_estimators=500, n_jobs=-1)
srf.fit(X_train,y_train)
print srf.score(X_test,y_test)
srf.fit(subtrain, labels)
print srf.predict(dd)
print srf.predict_proba(dd)
# print srf.predict_log_proba(dd)

