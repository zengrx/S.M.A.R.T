#coding=utf-8

from PyQt4 import QtGui, QtCore, Qt
import sys, os, time
sys.path.append("..")
from UILib.upload_file import Ui_Dialog
from advanceoperate.uploadthread import UploadFile, AddFileToQqueu

reload(sys)
sys.setdefaultencoding("utf-8")

class Dialog(QtGui.QDialog):

    def __init__(self, parent=None):
        QtGui.QWidget.__init__(self, parent)
        self.ui = Ui_Dialog()
        self.ui.setupUi(self)
        self.filename = ""
        self.apikey = "your apikey"

        self.table = self.ui.tableWidget
        
        # 按键信号槽
        self.ui.PB_Upload.clicked.connect(self.uploadFile)
        self.ui.PB_2Queue.clicked.connect(self.addFile2Queue)

    '''
    接收ui窗口传值
    '''
    def getFilename(self, filename):
        print "get filename from main ui"
        self.filename = filename

    '''
    点击上传文件按钮事件
    连接uploadfile中的线程函数
    '''
    def uploadFile(self, filename):
        self.clearFileData()
        self.ui.PB_Upload.setEnabled(False)
        self.uploadthread = UploadFile(self.filename, self.apikey)
        self.uploadthread.finishSignal.connect(self.recvAnalyzeResult)
        self.uploadthread.start()
    
    '''
    接收分析结果函数
    接收一个元组内容
    '''
    def recvAnalyzeResult(self, index, msg):
        if 1 == index:
            self.ui.label_4.setText(u"网络响应: " + str(msg[2]))
            self.ui.label_5.setText(u"返回代码: " + str(msg[3]))
            self.ui.PB_Upload.setEnabled(True)
            # self.ui.LE_HttpCode.setText(str(msg[2]))
            # self.ui.LE_SerCode.setText(str(msg[3]))
            if msg[0] == "scan_result":
                print "dddd"
                rowcount = len(msg[1])
                detecten = 0
                # for n in msg[1]:
                #     n = n.split("^")
                #     print "\t" + n[0] + "-" + n[1]
                self.table.setRowCount(rowcount)
                i = 0
                for n in msg[1]:
                    n = n.split("^")
                    engine = QtGui.QTableWidgetItem(n[0]) # 引擎
                    result = QtGui.QTableWidgetItem(n[1]) # 结果
                    self.table.setItem(i, 0, engine)
                    self.table.setItem(i, 1, result)
                    if str(n[1]) != " None":
                        detecten = detecten + 1
                        self.table.item(i, 1).setForeground(Qt.Qt.red)
                    else:
                        self.table.item(i, 1).setForeground(Qt.Qt.green)
                    i = i + 1
                linetext = str(detecten) + "/" + str(rowcount)
                # self.ui.LE_DeteRate.setText(linetext)
                self.ui.label.setText(u"检测率: " + linetext)
            elif msg[0] == "permalink":
                if msg[1]:
                    print "your file has been analysising"
                    self.ui.LE_URL.setText(str(msg[1][0]))
            elif msg[0] == "http_code":
                self.ui.LE_URL.setText(u"网络响应问题，请参考官方文档")
        if 2 == index:
            if msg[0] == "baseinfo":
                for n in msg[1]:
                    n = unicode(n)
                    self.ui.listWidget.addItem(n)
        if 3 == index:
            self.ui.PB_Upload.setEnabled(True)
            self.ui.LE_URL.setText(u"网络连接失败...")

    def addFile2Queue(self, filename):
        pass
    
    def clearFileData(self):
        print "clear table data"
        self.table.setRowCount(0)
        self.table.clearContents()
        self.ui.listWidget.clear()
        self.ui.LE_URL.clear()
        self.ui.label.setText(u"检测率: ")
        self.ui.label_4.setText(u"网络响应: ")
        self.ui.label_5.setText(u"返回代码: ")


if __name__ == "__main__":

    window = QtGui.QApplication(sys.argv)
    thiswindow = Dialog()
    thiswindow.show()

    sys.exit(window.exec_())