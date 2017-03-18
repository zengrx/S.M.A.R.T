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
        self.apikey = "632d8d808a60dba0ac32496f6c41073fff34e7ec6b33723136c7ca1861cd5ae6"

        self.table = self.ui.tableWidget

        # 按键信号槽
        self.ui.PB_Upload.clicked.connect(self.uploadFile)
        self.ui.PB_2Queue.clicked.connect(self.addFile2Queue)

    def getFilename(self, filename):
        print "get filename from main ui"
        self.filename = filename

    '''
    点击上传文件按钮事件
    连接uploadfile中的线程函数
    '''
    def uploadFile(self, filename):
        self.ui.PB_Upload.setEnabled(False)
        self.uploadthread = UploadFile(self.filename, self.apikey)
        self.uploadthread.finfishSignal.connect(self.recvAnalyzeResult)
        self.uploadthread.start()
    
    '''
    接收分析结果函数
    接收一个元组内容
    '''
    def recvAnalyzeResult(self, index, msg):
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
            self.ui.LE_DeteRate.setText(linetext)
            self.ui.PB_Upload.setEnabled(True)
        elif virus_check[0] == "permalink":
            if virus_check[1]:
                print "your file has been analysising"

    def addFile2Queue(self, filename):
        pass


if __name__ == "__main__":

    window = QtGui.QApplication(sys.argv)
    thiswindow = Dialog()
    thiswindow.show()

    sys.exit(window.exec_())