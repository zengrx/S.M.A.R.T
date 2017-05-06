#coding=utf-8

from PyQt4 import QtGui, QtCore, Qt
import sys, os, time
sys.path.append("..")
from UILib.opcode import Ui_Dialog
from advanceoperate.opcodethread import OpcodeNgram

reload(sys)
sys.setdefaultencoding("utf-8")

class Dialog(QtGui.QDialog):

    def __init__(self, parent=None):
        QtGui.QWidget.__init__(self, parent)
        self.ui = Ui_Dialog()
        self.ui.setupUi(self)

        self.table = self.ui.tableWidget
        self.prges = self.ui.progressBar
        
        self.filename = ''

    def getFileName(self, filename):
        self.filename = filename
        self.opngram  = OpcodeNgram(self.filename)
        self.opngram.opcodeSignal.connect(self.updateTableWdiget)
        self.opngram.concluSignal.connect(self.showClassifyResult)
        # 清空widget内容
        self.table.setRowCount(0)
        self.table.clearContents()
        # 还原label内容
        self.ui.label.setText(u"随机森林训练结论: ")
        self.ui.label_2.setText(u"弱分类器概率分布: ")
        self.ui.label_3.clear()
        # 进度条
        self.prges.setMaximum(0)
        self.prges.setValue(0)
        self.opngram.start()

    def updateTableWdiget(self, msg):
        self.table.horizontalHeader().setResizeMode(QtGui.QHeaderView.Stretch) #自适应宽度
        rowcoun = self.table.rowCount()
        self.table.insertRow(rowcoun)
        opcode = QtGui.QTableWidgetItem(str(msg[0]))
        freque = QtGui.QTableWidgetItem(str(msg[1]))
        opcode.setTextAlignment(Qt.Qt.AlignCenter)
        freque.setTextAlignment(Qt.Qt.AlignCenter)
        self.table.setItem(rowcoun, 0, opcode)
        self.table.setItem(rowcoun, 1, freque)

    def showClassifyResult(self, msg):
        self.prges.setMaximum(1)
        self.prges.setValue(1)
        print msg[0], msg[1]
        str1 = str(self.ui.label.text()) + "该文件属于训练集标签" + str(msg[0][0]).split('L')[0]
        m = 'class:   '
        n = ''
        ii = 1
        for i in msg[1]:
            tmp1 = str(ii) + ", "
            m += tmp1
            # 取小点后两位
            tmp2 = str(round(float(i), 2))  + "  "
            n += tmp2
            ii += 1
        self.ui.label.setText(unicode(str1))
        # self.ui.label_2.setText(unicode(m))
        self.ui.label_3.setText(unicode(n))

if __name__ == "__main__":

    window = QtGui.QApplication(sys.argv)
    thiswindow = Dialog()
    thiswindow.show()

    sys.exit(window.exec_())