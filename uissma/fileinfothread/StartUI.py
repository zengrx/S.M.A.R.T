# -*- coding: utf-8 -*-

from PyQt4 import QtGui, QtCore
from SSMA_UI import Ui_MainWindow
import sys, os
import shutil
from check_thread import checkFileThread, checkPEThread, anotherThread

class MainWindow(QtGui.QMainWindow):
    peemit = QtCore.pyqtSignal(str) #check pe file emit

    def __init__(self, parent=None):
        QtGui.QWidget.__init__(self, parent)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        
        self.widget   = self.ui.listWidget
        self.widget2  = self.ui.listWidget_2
        self.table    = self.ui.tableWidget
        self.filename = ""
        self.filetype = "PE32 executable (GUI) Intel 80386, for MS Windows"
        self.sysname  = "" #write a init function

        QtCore.QObject.connect(self.ui.pushButton, QtCore.SIGNAL("clicked()"), self.showBaseInfo)
        #test for one emit connect many functions
        self.peemit.connect(self.showPEFileInfo)
        self.peemit.connect(self.anotherThreadRecv)

    '''
    This function use for show file base infomation
    @ListWidget
    '''
    def showBaseInfo(self):
        #filename = QtGui.QFileDialog.getExistingDirectory(self, "sf", QtCore.QDir.currentPath()) #for path select
        self.filename = QtGui.QFileDialog.getOpenFileName(self, "select file", "./", "All Files (*)") #for file select
        if self.filename:
            self.cfThread = checkFileThread(self.filename)
            self.cfThread.finishSignal.connect(self.checkFileEnd)
            self.cfThread.start()
            self.widget.clear()
        else:
            self.showMessage("选择文件失败，请重试".decode('utf-8'))#("选择文件失败，请重试")
            #self.ui.textEdit.append(u"选择文件失败，请重试")

    def checkFileEnd(self, index, msg):
        if 1 == index:
            self.showMessage(u"文件类型：" + msg)
            tmp = "PE32"
            if tmp in msg:
                self.peemit.emit(self.filename)
        elif 2 == index:
            self.widget.addItem(msg)

    '''
    This function use for show pe file's detail message
    if recived file type is pe, then analize it.
    '''
    def showPEFileInfo(self, filename):
        print "emit worked"
        #新建对象，传入参数
        self.cpThread = checkPEThread(self.filetype, filename)
        #连接子进程的信号和槽函数
        self.cpThread.finishSignal.connect(self.checkPEEnd)
        #开始执行 run() 函数里的内容
        self.cpThread.start()

    def checkPEEnd(self, index, msg):
        print 'get from pe thread!'
        if 1 == index:
            self.widget2.addItems(msg)
        elif 2 == index:
            self.table.setRowCount(msg[0])
            for i in range (msg[0]):
                for j in range(5):
                    item = str(msg[i * 5 + j + 1])
                    self.table.setItem(i, j, QtGui.QTableWidgetItem(item))
            self.table.horizontalHeader().setResizeMode(QtGui.QHeaderView.Stretch) #自适应宽度
            print "updated tablewidget"

    '''
    test for table widget
    '''
    def anotherThreadRecv(self):
        print "another test"
        self.testThread = anotherThread(int(10))
        self.testThread.anotherSignal.connect(self.anotherShow)
        self.testThread.start()

    def anotherShow(self):
        print "show from anotherShow function" 
        
    '''
    User for update opeartion message
    '''
    def showMessage(self, msg, showtime = True):
        self.ui.textEdit.append(msg)

if __name__ == "__main__":

    
    app = QtGui.QApplication(sys.argv)
    myapp = MainWindow()
    
    myapp.show()
    
    #check internet
    #internet_connection = check_internet_connection()
    system = os.name
    if ("nt" == system):
        print "windows"
    if ("posix" == system):
        print "Linux/Unix"

    sys.exit(app.exec_())
