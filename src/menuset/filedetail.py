#coding=utf-8

from PyQt4 import QtGui, QtCore, Qt
import sys, os, time
sys.path.append("..")
from UILib.detail import Ui_Dialog
from advanceoperate.detailthread import FileDetail, PEFileInfo
from globalset import ImpAlert

reload(sys)
sys.setdefaultencoding("utf-8")

class Dialog(QtGui.QDialog):
    # detailSignal = QtCore.pyqtSignal(str)

    def __init__(self, parent=None):
        QtGui.QWidget.__init__(self, parent)
        self.ui = Ui_Dialog()
        self.ui.setupUi(self)

        self.widget   = self.ui.listWidget
        self.tree     = self.ui.treeWidget
        self.table    = self.ui.tableWidget
        self.filename = ""
        self.md5      = ""
        self.filetype = ""

    def getFileName(self, filename, md5):
        self.filename = filename
        self.md5      = md5
        self.detail   = FileDetail(self.filename) # 基本信息
        self.peinfo   = PEFileInfo(self.filename, self.md5) # PE信息
        self.detail.finishSignal.connect(self.showBaseInfo)
        self.detail.start()

    def showBaseInfo(self, msg):
        self.widget.clear() # 清空list内容
        self.table.clearContents() # 清空table内容保留列名
        self.tree.clear()
        for n in msg:
            if "PE32" in n or "executable" in n:
                self.peinfo.importSignal.connect(self.showImpImfo) # 连接显示导入表widget
                self.peinfo.sectionSignal.connect(self.showSetInfo) # 连接显示节信息widget
                self.peinfo.start()
            n = unicode(n)
            self.widget.addItem(n)

    def showAdvInfo(self, msg):
        print "aadfasf"

    '''
    显示PE import信息
    未处理dll名None情况
    已处理API名None情况
    '''
    def showImpImfo(self, msg):
        self.tree.setColumnCount(2)
        self.tree.setHeaderLabels([u"Name", u"Description"])
        alt = ImpAlert().alerts # 取glob内容
        att = [] # 需要注意的API列表->转集合
        rootindex = len(msg.keys())
        for i in range(rootindex):
            dll = QtGui.QTreeWidgetItem(self.tree)
            keyname = msg.keys()[i]
            dll.setText(0, keyname)
            childindex = len(msg[keyname])
            for j in range(childindex):
                if None == msg[keyname][j]:
                    continue
                child = QtGui.QTreeWidgetItem(dll)
                child.setText(0, msg[keyname][j])
                if any(map(msg[keyname][j].startswith, alt.keys())):
                    att.append(msg[keyname][j])
                    child.setForeground(0, Qt.Qt.red)
                    for a in alt:
                        if msg[keyname][j].startswith(a):
                            child.setText(1, alt.get(a))
        alert = QtGui.QTreeWidgetItem(self.tree)
        alert.setText(0, "Suspicious API")
        alert.setForeground(0, Qt.Qt.red)
        att = list(set(att))
        for i in range(len(att)):
            child = QtGui.QTreeWidgetItem(alert)
            child.setText(0, att[i])
            child.setForeground(0, Qt.Qt.red)
                
    '''
    在tablewidget中显示PE节信息
    '''
    def showSetInfo(self, msg):
        # 认可的节名称
        goodsection = ['.data', '.text', '.code', '.reloc', '.idata', '.edata', '.rdata', '.bss', '.rsrc']
        self.table.setRowCount(msg[0])
        for i in range(msg[0]):
            for j in range(5):
                item = str(msg[i * 5 + j + 1])
                self.table.setItem(i, j, QtGui.QTableWidgetItem(item))
        self.table.horizontalHeader().setResizeMode(QtGui.QHeaderView.Stretch) #自适应宽度
        for i in range(msg[0]):
            secname = self.table.item(i, 0)
            if secname.text() not in goodsection:
                secname.setTextColor(Qt.Qt.red)
            entrpoy = self.table.item(i, 4)
            if float(entrpoy.text()) < 1 or float(entrpoy.text()) > 7:
                entrpoy.setTextColor(Qt.Qt.red)
            rawsize = self.table.item(i, 3)
            if 0 == int(rawsize.text()):
                rawsize.setTextColor(Qt.Qt.red)
        print "updated tablewidget"


if __name__ == "__main__":

    window = QtGui.QApplication(sys.argv)
    thiswindow = Dialog()
    thiswindow.show()

    sys.exit(window.exec_())