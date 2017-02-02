# -*- coding: utf-8 -*-

from PyQt4 import QtGui, QtCore
from MS_MainWindow import Ui_MainWindow
import sys, os, shutil
from tabletest import CheckFolder, ScanFile

reload(sys)
sys.setdefaultencoding( "utf-8" )

class MainWindow(QtGui.QMainWindow):
    scanemit = QtCore.pyqtSignal(str)
    anailzemit = QtCore.pyqtSignal(str) # 开始分析文件信号

    def __init__(self, parent=None):
        QtGui.QWidget.__init__(self, parent)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        
        self.table = self.ui.tableWidget
        self.table.horizontalHeader().setResizeMode(QtGui.QHeaderView.Stretch)

        self.folder   = ''
        self.dir      = ''
        self.dirsnum  = 0
        self.filenum  = 0
        self.table    = self.ui.tableWidget
        self.rowindex = 0

        QtCore.QObject.connect(self.ui.PB_SelectFolder, QtCore.SIGNAL("clicked()"), self.selectFolder)
        QtCore.QObject.connect(self.ui.PB_ScanType, QtCore.SIGNAL("clicked()"), self.startScan)
        self.scanemit.connect(self.recvInitSingal)
        self.anailzemit.connect(self.updateScanInfo)

    #假设以扫描类型作为开始扫描动作测试
    #需要实现在功能函数线程中而非UI线程
    def selectFolder(self):
        self.folder = QtGui.QFileDialog.getExistingDirectory(self, u"选择文件夹", "e:\\")#QtCore.QDir.currentPath())
        if self.folder == '':
            self.ui.statusbar.showMessage(u"操作取消")
        else:
            showmsg = u"选择：" + self.folder
            self.ui.statusbar.showMessage(showmsg)
            self.ui.lineEdit.setText(self.folder)

    def startScan(self):
        self.ui.statusbar.showMessage("init...")
        print "lll" + str(self.folder).decode('utf-8')
        if self.folder != '':
            self.folderThread = CheckFolder(self.folder)
            # two signals connect one slot
            self.folderThread.numberSignal.connect(self.recvInitSingal)
            self.folderThread.valueSignal.connect(self.recvInitSingal)
            #执行run方法
            self.folderThread.start()

    def recvInitSingal(self, index, msg):
        if 1 == index:
            self.dirsnum = msg
            print "folders number is: " + self.dirsnum
            self.ui.progressBar.setMaximum(int(self.filenum))
        if 2 == index:
            self.filenum = msg
            print "files number is: " + self.filenum
        if 3 == index:
            scanlist = msg
            # 扫描线程准备工作 第一版 发列表
            self.scanThread = ScanFile(scanlist)
            self.scanThread.fileSignal.connect(self.updateScanInfo) # 连到更新函数中
            self.scanThread.start()


            # for i in range(int(self.filenum)):
            #     filename = scanlist[i]
                

            # # 测试更新tablewdiget
            # if str(len(scanlist)) == self.filenum:
            #     print "ok"
            #     showmsg = "folders: " + self.dirsnum + ", files: " + self.filenum
            #     self.ui.statusbar.showMessage(showmsg)
            # print msg
            # # statusmsg = 'now scanning ' + msg + ' file'
            # # self.statusBar().showMessage(statusmsg)
            # self.rowindex = self.rowindex + 1
            # i = self.rowindex
            # # print i
            # self.table.setRowCount(i)
            # # 或者用insertRow
            # self.table.setItem(i - 1, 0, QtGui.QTableWidgetItem(msg))

    # 暂时将statusbar和tablewidget信息集中在这里
    # 验证后再分离功能
    def updateScanInfo(self, num, msg):
        showmsg = 'recv result from file: ' + msg
        self.ui.statusbar.showMessage(showmsg)
        # 更新进度条 最大值和当前值放在一起
        self.ui.progressBar.setMaximum(int(self.filenum))
        self.ui.progressBar.setValue(num)

        # 更新tablewidget
        self.rowindex = self.rowindex + 1
        i = self.rowindex
        # print i
        self.table.setRowCount(i)
        # 或者用insertRow
        p, f = os.path.split(str(msg)) # 分割文件路径与文件名
        self.table.setItem(i - 1, 0, QtGui.QTableWidgetItem(f))
        self.table.setItem(i - 1, 1, QtGui.QTableWidgetItem(p))

    def updateStatusBar(self):
        pass

    def updateTableMsg(self):
        pass


if __name__ == "__main__":

    app = QtGui.QApplication(sys.argv)
    myapp = MainWindow()
    myapp.show()

    sys.exit(app.exec_())