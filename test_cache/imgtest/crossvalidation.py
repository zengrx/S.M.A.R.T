import random
from sklearn.cross_validation import StratifiedKFold
from sklearn.utils import shuffle
import sklearn
import numpy

X = numpy.load('img_features.npy')
y = numpy.load('img_labels.npy')

n_samples, n_features = X.shape 
p = range(n_samples) # an index array, 0:n_samples
random.seed(random.random())
random.shuffle(p) # the index array is now shuffled

X, y = X[p], y[p] # both the arrays are now shuffled

kfold = 10 # no. of folds (better to have this at the start of the code)

skf = StratifiedKFold(y,kfold)#,indices='true')
# skf = sklearn.model_selection.StratifiedKFold(y, kfold, indices='true')

# Stratified KFold: This first divides the data into k folds. Then it also makes sure that the distribution of the data in each fold follows the original input distribution 
# Note: in future versions of scikit.learn, this module will be fused with kfold

skfind = [None]*len(skf) # indices
cnt=0
for train_index in skf:
    skfind[cnt] = train_index
    cnt = cnt + 1


# Supervised Classification with k-fold Cross Validation
import os, glob
from sklearn.metrics import confusion_matrix
from sklearn.neighbors import KNeighborsClassifier

os.chdir('F:\\malimg_paper_dataset_imgs') # the parent folder with sub-folders

list_fams = os.listdir(os.getcwd()) # vector of strings with family names
print list_fams

no_imgs = [] # No. of samples per family

for i in range(len(list_fams)):
    os.chdir(list_fams[i])
    len1 = len(glob.glob('*.png')) # assuming the images are stored as 'png'
    no_imgs.append(len1)
    os.chdir('..')

conf_mat = numpy.zeros((len(no_imgs),len(no_imgs))) # Initializing the Confusion Matrix

n_neighbors = 1; # better to have this at the start of the code

# 10-fold Cross Validation

for i in range(kfold):
    train_indices = skfind[i][0]
    test_indices = skfind[i][1]
    clf = []
    clf = KNeighborsClassifier(n_neighbors,weights='distance') 
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
    print "---------------", y_test-y_predict, "--------------"
    conf_mat = conf_mat + cm 
 

conf_mat = conf_mat.T # since rows and  cols are interchanged
avg_acc = numpy.trace(conf_mat)/sum(no_imgs)
conf_mat_norm = conf_mat/no_imgs # Normalizing the confusion matrix

import matplotlib.pyplot as plt
# plt.imshow(conf_mat_norm, interpolation='nearest')
# plt.title('confusion matrix')
# plt.show()
# plt.savefig('confusion_matrix.png')

conf_mat2 = numpy.around(conf_mat_norm,decimals=2) # rounding to display in figure
plt.imshow(conf_mat2,interpolation='nearest')
for x in xrange(len(list_fams)):
    for y in xrange(len(list_fams)):
        plt.annotate(str(conf_mat2[x][y]),xy=(y,x),ha='center',va='center')

plt.xticks(range(len(list_fams)),list_fams,rotation=90,fontsize=11)
plt.yticks(range(len(list_fams)),list_fams,fontsize=11)
plt.title('Confusion matrix')
plt.colorbar()
plt.show()
# plt.savefig('../confusion_matrix.png')