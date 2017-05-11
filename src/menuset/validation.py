#coding=utf-8

from PyQt4 import QtGui, QtCore, Qt
import matplotlib; matplotlib.use('Qt4Agg')
import matplotlib.pyplot as plt
import os, sys, time
import numpy
sys.path.append("..")
from UILib.machinelearn import Ui_Dialog
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas # matplotlib对PyQt4的支持
from matplotlib.figure import Figure
from advanceoperate.malimgthread import ValidationResult

reload(sys)
sys.setdefaultencoding("utf-8")

class Dialog(QtGui.QDialog):

    def __init__(self, parent=None):
        QtGui.QWidget.__init__(self, parent)
        self.ui = Ui_Dialog()
        self.ui.setupUi(self)

        self.frame = self.ui.frame
        self._createFigures()
        self._createLayouts()
        # self.ui.PB_ConfMatrix.clicked.connect(self.test)
        self.ui.PB_ConfMatrix.clicked.connect(self.test2)

    def test2(self):
        self.vali = ValidationResult()
        self.vali.finishSignal.connect(self.getValidationResult)
        self.vali.start()

    def getValidationResult(self, msg):
        self.drawConfusionMatrix(msg[0], msg[1], msg[2])

    def drawConfusionMatrix(self, conf_mat, no_imgs, list_fams):
        conf_mat = conf_mat.T # since rows and  cols are interchanged
        avg_acc = numpy.trace(conf_mat) / sum(no_imgs)
        conf_mat_norm = conf_mat / no_imgs # Normalizing the confusion matrix

        conf_mat2 = numpy.around(conf_mat_norm,decimals=2) # rounding to display in figure
        self._ax.imshow(conf_mat2, interpolation='nearest')
        for x in xrange(len(list_fams)):
            for y in xrange(len(list_fams)):
                self._ax.annotate(str(conf_mat2[x][y]), xy=(y,x), ha='center', va='center', fontsize=7)

        self._ax.set_xticks([])
        # self._ax.set_yticks([])
        self._ax.set_yticks(range(len(list_fams)))
        self._ax.set_yticklabels(list_fams, fontsize=7)
        self._ax.grid(True)
        self._canvas.draw()

    def _createFigures(self):
        self._fig = Figure(figsize=(8, 6), dpi=100, tight_layout=False) 
        self._fig.set_facecolor("#F5F5F5") # 背景色
        self._fig.subplots_adjust(left=0, top=1, right=1, bottom=0) # Margins
        self._canvas = FigureCanvas(self._fig) # 画布
        self._ax = self._fig.add_subplot(111) # 增加subplot
        # self._ax.hold(True)

    def _createLayouts(self):
        layout = QtGui.QHBoxLayout(self.frame)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self._canvas) # Add Matplotlib