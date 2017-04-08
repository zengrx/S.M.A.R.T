#coding=utf-8

from sklearn.ensemble import RandomForestClassifier as RF
from sklearn import cross_validation
from sklearn.metrics import confusion_matrix
from collections import *
import re
from collections import *
import os
import pandas as pd
import numpy as np

def getOpcodeSequence(filename):
    opcode_seq = []
    p = re.compile(r'\s([a-fA-F0-9]{2}\s)+\s*([a-z]+)')
    with open(filename) as f:
        for line in f:
            if line.startswith(".text"):
                m = re.findall(p,line)
                if m:
                    opc = m[0][1]
                    if opc != "align":
                        opcode_seq.append(opc)
    return opcode_seq

def train_opcode_lm(ops, order=4):
    lm = defaultdict(Counter)
    prefix = ["~"] * order
    prefix.extend(ops)
    data = prefix
    for i in xrange(len(data)-order):
        history, char = tuple(data[i:i+order]), data[i+order]
        lm[history][char]+=1
    def normalize(counter):
        s = float(sum(counter.values()))
        return [(c,cnt/s) for c,cnt in counter.iteritems()]
    outlm = {hist:chars for hist, chars in lm.iteritems()}
    return outlm

def getOpcodeNgram(ops, n=3):
    opngramlist = [tuple(ops[i:i+n]) for i in range(len(ops)-n)]
    opngram = Counter(opngramlist)
    return opngram

basepath = '/home/zrx/code/malwaredata/testtrain/'
map3gram = defaultdict(Counter)
subtrain = pd.read_csv('subtrainLabels.csv')
count = 1
for sid in subtrain.Id:
    print "counting the 3-gram of the {0} file...".format(str(count))
    count += 1
    filename = basepath + sid + ".asm"
    ops = getOpcodeSequence(filename)
    op3gram = getOpcodeNgram(ops)
    map3gram[sid] = op3gram

cc = Counter([])
for d in map3gram.values():
    cc += d
selectedfeatures = {}
tc = 0
print "select features..."
# 选取大于出现次数500的作为特征
for k,v in cc.iteritems():
    if v >= 500:
        selectedfeatures[k] = v
        print k,v
        tc += 1
dataframelist = []
print selectedfeatures
for fid,op3gram in map3gram.iteritems():
    standard = {}
    standard["Id"] = fid
    for feature in selectedfeatures:
        if feature in op3gram:
            standard[feature] = op3gram[feature]
        else:
            standard[feature] = 0
    dataframelist.append(standard)
    print "-----------standard----------"
    print standard
    
df = pd.DataFrame(dataframelist)
print "csv"
# print df
df.to_csv("3gramfeature.csv",index=False)

filepath = '/home/zrx/code/malwaredata/train/IkzqRMZW71YALpX6VtCf.asm'
tops = getOpcodeSequence(filepath)
t3gram = getOpcodeNgram(tops)
testdata = {}
for feature in selectedfeatures:
    if feature in t3gram:
        print feature
        testdata[feature] = t3gram[feature] # 传递统计数值
    else:
        testdata[feature] = 0
# testdata = pd.DataFrame(testdata)
print testdata.values()
dd = np.array(testdata.values(), dtype = int).reshape((1,-1))
print dd

subtrainLabel = pd.read_csv('subtrainLabels.csv')
subtrainfeature = pd.read_csv("3gramfeature.csv")
subtrain = pd.merge(subtrainLabel,subtrainfeature,on='Id')
labels = subtrain.Class
subtrain.drop(["Class","Id"], axis=1, inplace=True)
subtrain = subtrain.as_matrix()

X_train, X_test, y_train, y_test = cross_validation.train_test_split(subtrain,labels,test_size=0.3)
srf = RF(n_estimators=500, n_jobs=-1)
# srf.fit(X_train,y_train)
srf.fit(subtrain, labels)
# print srf.score(X_test, y_test)
print srf.predict_proba(dd)
print srf.predict(dd)