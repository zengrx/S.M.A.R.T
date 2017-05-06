import random
from sklearn.cross_validation import StratifiedKFold
from sklearn.neighbors import BallTree
from sklearn import cross_validation
from sklearn.utils import shuffle
import sklearn
import numpy
import cPickle

X = numpy.load('img_features.npy')
y = numpy.load('img_labels.npy')
n = cPickle.load(open("img.p","rb"))

b = BallTree(X)

'''
Yuner.A
00a4dca141fa845ee1a946eca1dafb07
00a5fee307b3411835b6bbe4a46c76f1
04b398f3d60fac660fe8ad461c6c9616
Malex.gen!J
00a05020315b92d79e4dda579dc4ed80
03c49177d0998bebff40d596d0e0c0dc
0027dfbce8c3a5cfce6f7c70c24ead61
Rbot!gen
3b3b6c6cc254f167ed82c0d83563677b.exe
9c6bfde533d8f07e83a0d3e2003b57ba.exe
'''

from PIL import Image
import leargist
im = Image.open('/home/amber/Documents/smart_image/malimg_dataset/malimg_paper_dataset_imgs/Malex.gen!J/00a05020315b92d79e4dda579dc4ed80.png')
im1 = im.resize((64,64), Image.ANTIALIAS); # for faster computation
des = leargist.color_gist(im1); # 960 values
feature = des[0:320]; # since the image is grayscale, we need only first 320 values
# print feature
query_feature = feature.reshape(1, -1)
# print query_feature
print "--------------"
print X.shape
print X, y, n

dist,ind = b.query(query_feature,k=5)
# print dist, ind

# Supervised Classification with k-fold Cross Validation
import os, glob
from sklearn.metrics import confusion_matrix
from sklearn.neighbors import KNeighborsClassifier

n_neighbors = 5; # better to have this at the start of the code

knn = KNeighborsClassifier(n_neighbors,weights='distance')
knn.fit(X, y)
num = int(knn.predict(query_feature))
print num
print n[num]
print knn.predict_proba(query_feature)

from sklearn.ensemble import RandomForestClassifier as RF
srf = RF(n_estimators=50, n_jobs=-1)
srf.fit(X,y)
print srf.predict(query_feature)
print srf.predict_proba(query_feature)

from sklearn import svm
sv = svm.NuSVC(gamma=0.001)
sv.fit(X, y)
print sv.predict(query_feature)
print sv.predict_proba(query_feature)