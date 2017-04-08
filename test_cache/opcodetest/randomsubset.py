#coding=utf-8

import os, time
from random import *
import pandas as pd
import shutil 

rs = Random()
rs.seed(1)

trainlabels = pd.read_csv('trainLabels.csv')
fids = []
opd = pd.DataFrame()
for clabel in range (1,10): #从1到9
    mids = trainlabels[trainlabels.Class == clabel] #循环出9个族
    mids = mids.reset_index(drop=True) #重新对9个族排列id

    rchoice = [rs.randint(0,len(mids)-1) for i in range(500)]
    print rchoice   #每个族中随机抽取100个，包含重复，相当于样本等比
                    #如果要生成不重复的可以使用集合最后计算总个数
    
#     for i in rchoice:
#         fids.append(mids.loc[i].Id)
#         opd = opd.append(mids.loc[i])

    rids = [mids.loc[i].Id for i in rchoice] #rids值为对应选中的文件名称
    fids.extend(rids)
    opd = opd.append(mids.loc[rchoice]) #组合出新的csv作为训练子集
    

print len(fids)
opd = opd.reset_index(drop=True)
print opd
opd.to_csv('subtrainLabels.csv', encoding='utf-8', index=False)

sbase = '/home/zrx/code/malwaredata/train/'
# sbase = sbase.encode('cp936')
tbase = '/home/zrx/code/malwaredata/testtrain/'

for fid in fids:
	fnames = ['{0}.asm'.format(fid),'{0}.asm'.format(fid)]
	for fname in fnames:
		cspath = sbase + fname
		ctpath = tbase + fname
		shutil.copy(cspath,ctpath)
        print fname