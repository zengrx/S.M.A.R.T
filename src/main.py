# -*- coding: utf-8 -*-

'''
    S.M.A.R.T.
    Static Malware Analysis and Report Tool
    author: Zeng RuoXing

'''

from PyQt4 import QtGui, QtCore, Qt
from UILib.MS_MainWindow import Ui_MainWindow
import sys, os, shutil
from control import CheckFolder, ScanFile
from menuset.setting import Dialog as SetDialog
from menuset.authorinfo import Dialog as AuthorInfo
from menuset.filedetail import Dialog as DetailDialog
from menuset.uploadfile import Dialog as UploadDialog
from globalset import FlagSet
import sqlite3

reload(sys)
sys.setdefaultencoding( "utf-8" )

class MainWindow(QtGui.QMainWindow):
    # scanemit = QtCore.pyqtSignal(str)
    # anailzemit = QtCore.pyqtSignal(str) # 开始分析文件信号

    def __init__(self, parent=None):
        QtGui.QWidget.__init__(self, parent)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        
        # checkBox对象
        # 扫描规则部分
        self.cbrall  = self.ui.CBRuleAll    # 规则全选
        self.cbryara = self.ui.CBRuleYara   # yara规则
        self.cbrclam = self.ui.CBRuleClamav # clamav
        self.cbrpack = self.ui.CBRulePack   # 文件查壳
        self.cbrself = self.ui.CBRuleSelf   # 自定义规则
        self.cbrwl   = self.ui.CBRuleWL     # 白名单
        # 文件类型部分
        self.cbtall  = self.ui.CBTypeAll    # 类型全选
        self.cbtpe   = self.ui.CBTypePE     # PE类型
        self.cbtofs  = self.ui.CBTypeOffice # office类型
        self.cbtsh   = self.ui.CBTypeShell  # 脚本类型
        self.cbtzip  = self.ui.CBTypeZip    # 压缩包
        self.cbtmda  = self.ui.CBTypeMedia  # 多媒体
        self.cbtasm  = self.ui.CBTypeAsm    # asm文件

        # 下拉菜单
        self.cbbox = self.ui.comboBox

        # 初始按键不可用
        self.ui.PB_Start.setEnabled(False)
        self.ui.PB_End.setEnabled(False)

        # 设置tablewdiget属性
        # 自动适配header宽度，效果不好后期改适配最后一列
        # setStretchLastSection已在ui文件中设置 
        # 设置不可编辑 设置每次选中一行
        self.table = self.ui.tableWidget
        # self.table.horizontalHeader().setResizeMode(QtGui.QHeaderView.Stretch)
        # self.table.horizontalHeader().setStretchLastSection(True)
        self.table.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)
        self.table.setContextMenuPolicy(Qt.Qt.CustomContextMenu)

        # tablewidget信号槽--排序
        self.table.horizontalHeader().sectionClicked.connect(self.tableHeaderEvent)
         
        # 右键菜单信号槽
        self.table.customContextMenuRequested.connect(self.generateMenu)

        # 菜单栏控件-索引字典
        self.menubardict = {
            self.ui.AC_Check   : 0, # 检查配置 
            self.ui.AC_Setting : 1, # 软件设置
            self.ui.AC_Loadcfg : 2, # 读取配置
            self.ui.AC_OutLog  : 3, # 导出日志
            self.ui.AC_Info    : 4, # 版本信息
            self.ui.AC_About   : 5, # 关于软件
            self.ui.AC_Author  : 6  # 联系作者
        }

        # 菜单栏信号槽
        # for key, value in self.menubardict.items():
        #     print key, value
        #     key.triggered.connect(lambda: self.menuBarOperate(value))
        self.ui.AC_Check.triggered.connect(lambda: self.menuBarOperate(0))
        self.ui.AC_Setting.triggered.connect(lambda: self.menuBarOperate(1))
        self.ui.AC_Loadcfg.triggered.connect(lambda: self.menuBarOperate(2))
        self.ui.AC_OutLog.triggered.connect(lambda: self.menuBarOperate(3))
        self.ui.AC_Info.triggered.connect(lambda: self.menuBarOperate(4))
        self.ui.AC_About.triggered.connect(lambda: self.menuBarOperate(5))
        self.ui.AC_Author.triggered.connect(lambda: self.menuBarOperate(6))
        
        self.scanflag = 0  # 扫描策略flag
        self.folder   = '' # 选取文件夹路径
        self.files    = [] # 最终选取的文件名列表
        # self.dir      = ''
        self.dirsnum  = 0
        self.filenum  = 0
        self.table    = self.ui.tableWidget
        self.rowindex = 0
        self.rulelist = ['2', '3', '4', '5', '6']
        self.typelist = ['7', '8', '9', '10', '11', '12']
        self.rule     = [] # 发送至control的扫描规则
        self.type     = [] # 发送至control的文件类型
        self.flist    = [] # uploadfile判断更新滑动窗口

        # 其他窗口对象实例
        self.setdialog    = SetDialog() # 设置
        self.authorinfo   = AuthorInfo()
        self.detailDialog = DetailDialog()
        self.uploadDialog = UploadDialog()

        # 按钮事件信号槽
        QtCore.QObject.connect(self.ui.PB_SelectFolder, QtCore.SIGNAL("clicked()"), self.selectFolder)
        QtCore.QObject.connect(self.ui.PB_Start, QtCore.SIGNAL("clicked()"), self.startScan)
        QtCore.QObject.connect(self.ui.PB_Clear, QtCore.SIGNAL("clicked()"), self.clearTableWidget)
        self.ui.PB_End.clicked.connect(self.stopScan)
        
        # checkbox信号槽
        # 使用lambda表达式自定义参数
        self.cbrall.clicked.connect(lambda: self.checkBoxEvent(0))
        self.cbtall.clicked.connect(lambda: self.checkBoxEvent(1))
        self.cbryara.clicked.connect(lambda: self.checkBoxEvent(2))
        self.cbrclam.clicked.connect(lambda: self.checkBoxEvent(3)) 
        self.cbrpack.clicked.connect(lambda: self.checkBoxEvent(4))
        self.cbrself.clicked.connect(lambda: self.checkBoxEvent(5))
        self.cbrwl.clicked.connect(lambda: self.checkBoxEvent(6))
        self.cbtpe.clicked.connect(lambda: self.checkBoxEvent(7))
        self.cbtofs.clicked.connect(lambda: self.checkBoxEvent(8))
        self.cbtsh.clicked.connect(lambda: self.checkBoxEvent(9))
        self.cbtzip.clicked.connect(lambda: self.checkBoxEvent(10))
        self.cbtmda.clicked.connect(lambda: self.checkBoxEvent(11))
        self.cbtasm.clicked.connect(lambda: self.checkBoxEvent(12))

        # 连接线程操作的信号槽
        # self.scanemit.connect(self.recvInitSingal)
        # self.anailzemit.connect(self.updateScanInfo)

    '''
    选择文件按钮事件响应函数
    设置扫描文件或扫描文件夹
    # 假设以扫描类型作为开始扫描动作测试
    # 需要实现在功能函数线程中而非UI线程
    '''
    def selectFolder(self):
        if 0 == self.cbbox.currentIndex():
            self.scanflag = 0
            self.folder = QtGui.QFileDialog.getExistingDirectory(self, u"选择文件夹", "e:\\")#QtCore.QDir.currentPath())
            if self.folder == '':
                self.ui.statusbar.showMessage(u"操作取消")
            else:
                showmsg = u"选择：" + self.folder
                self.ui.statusbar.showMessage(showmsg)
                self.ui.lineEditScanStart.setText(self.folder)
        elif 1 == self.cbbox.currentIndex():
            self.scanflag = 1
            # 清空列表
            self.files[:] = []
            getlist = list(QtGui.QFileDialog.getOpenFileNames(self, u"选择文件", "e:\\"))
            if getlist:
                for i in getlist:
                    i = str(i).decode('utf-8')
                    self.files.append(i)
                showmsg = u"已选择待扫描文件"
                self.ui.statusbar.showMessage(showmsg)
                self.ui.lineEditScanStart.setText(showmsg)
            else:
                self.ui.statusbar.showMessage(u"操作取消")
        else:
            pass
        # 选择完成后激活开始按键
        self.ui.PB_Start.setEnabled(True)
            
    '''
    扫描器起始
    调度扫描文件夹与扫描文件
    扫描文件时不受filetype选择影响
    需要添加类似的调度函数
    '''
    def startScan(self):
        self.ui.PB_Start.setEnabled(False)
        self.ui.PB_Clear.setEnabled(False)
        self.ui.PB_End.setEnabled(True)
        self.ui.progressBar.reset()
        self.ui.statusbar.showMessage(u"正在初始化...")
        FlagSet.scanstopflag = 1 # 恢复停止标识
        FlagSet.scansqlcount = self.table.rowCount()
        try:
            sqlconn = sqlite3.connect("../db/fileinfo.db")
        except sqlite3.Error, e:
            print "sqlite connect failed" , "\n", e.args[0]
        sqlcursor = sqlconn.cursor()
        sqlcursor.execute("delete from base_info where md5 is NULL")#> ?", str(self.table.rowCount()),) <-warring
        sqlconn.commit()
        sqlconn.close()
        print "delete no value data over"
        # 设置左右滑动效果
        # 进度条最大最小值都为0
        self.ui.progressBar.setMaximum(0)
        self.ui.progressBar.setValue(0)
        # 应用扫描策略
        self.rule, self.type = self.prevScanPrepare()
        if 0 == self.scanflag: # 选择文件夹
            print "start: " + str(self.folder).decode('utf-8')
            if self.folder != '':
                # send folder and filetype to fliter
                self.folderThread = CheckFolder(self.folder, self.type)
                # two signals connect one slot
                self.folderThread.numberSignal.connect(self.recvInitSingal)
                #执行run方法
                self.folderThread.start()
        elif 1 == self.scanflag: # 选择文件
            if self.files:
                self.filenum = len(self.files)
                # 直接连接control中的scanfile线程
                self.filesThread = ScanFile(self.files, self.rule)
                self.filesThread.fileSignal.connect(self.updateScanInfo) # 连到更新函数中
                self.filesThread.smsgSignal.connect(self.updateStatusBar)
                self.filesThread.start()
        else:
            pass

    def stopScan(self):
        print "stopscan"
        self.ui.PB_Start.setEnabled(True)
        self.ui.PB_Clear.setEnabled(True)
        self.ui.PB_End.setEnabled(False)
        self.ui.statusbar.showMessage(u"手动结束扫描，等待线程退出")
        FlagSet.scanstopflag = 0
        # if 0 == self.ui.progressBar.maximum():
        #     print u"在初始化时结束扫描"
        #     # 删除没有初始化没有显示的数据
        #     # 与update分开是为了同步线程对数据库的操作 
        #     try:
        #         sqlconn = sqlite3.connect("../db/fileinfo.db")
        #     except sqlite3.Error, e:
        #         print "sqlite connect failed" , "\n", e.args[0]
        #     sqlcursor = sqlconn.cursor()
        #     sqlcursor.execute("delete from base_info where id>=?", str(self.table.rowCount()),) #<-warring
        #     sqlconn.commit()
        #     sqlconn.close()
        #     print "delete no value data over"
    
    '''
    扫描前准备函数
    负责获取所有设置并统一设置调度
    返回调度结果rule[]与type[]
    '''
    def prevScanPrepare(self):
        policy = self.getScanPolicy()
        if not any(set(policy) & set(self.typelist)):
            self.ui.statusbar.showMessage(u"请至少选择一种类型文件")
        # if "set([])" == str(set(policy) & set(self.rulelist)):
        #     self.ui.statusbar.showMessage(u"不使用拓展规则")
        rulepolicy = list(set(policy) & set(self.rulelist))
        typepolicy = list(set(policy) & set(self.typelist))
        return rulepolicy, typepolicy

    '''
    接收startScan连接的子进程checkFolder返回内容
    @index:区分信息索引
    1-子文件夹个数
    2-文件个数
    3-文件名列表
    @msg:具体内容
    '''
    def recvInitSingal(self, index, msg):
        if 1 == index:
            self.dirsnum = msg
            print "folders number is: " + self.dirsnum
        if 2 == index:
            self.filenum = msg
            print "files number is: " + self.filenum
        if 3 == index:
            scanlist = msg
            if 0 == int(self.filenum):
                self.ui.statusbar.showMessage(u"未检索到符合条件的文件，扫描结束")
                self.ui.progressBar.setMaximum(1)
                self.ui.progressBar.setValue(1)
                return
            if 0 == FlagSet.scanstopflag:
                self.ui.statusbar.showMessage(u"扫描初始化已停止")
                self.ui.progressBar.setMaximum(1)
                self.ui.progressBar.setValue(1)
                return
            # 扫描线程准备工作 第一版 发列表
            # 下一版可以考虑不发文件名list
            # 3月2日更新配合多文件选择使用，暂不修改
            # 3月27日更改为读写数据库
            self.scanThread = ScanFile(int(self.filenum), self.rule)
            self.scanThread.fileSignal.connect(self.updateScanInfo) # 连到更新函数中
            self.scanThread.smsgSignal.connect(self.updateStatusBar)
            self.scanThread.start()

    '''
    暂时将statusbar和tablewidget信息集中在这里
    验证后再分离功能
    可对应添加scanfile信号发射的参数
    @msg:文件绝对路径，将分割为文件名+路径
    @文件类型
    @文件日期
    @文件大小
    @文件MD5
    '''
    def updateScanInfo(self, num, msg):
        showmsg = 'recv result from file: ' + msg
        self.ui.statusbar.showMessage(showmsg)
        # 更新进度条 最大值和当前值放在一起
        self.ui.progressBar.setMaximum(int(self.filenum))
        self.ui.progressBar.setValue(num)
        if int(self.filenum) == num:
            self.ui.statusbar.showMessage(u"扫描结束")
        # 更新tablewidget
        self.rowindex = FlagSet.scansqlcount
        i = self.rowindex
        # print i
        self.table.setRowCount(i)
        # 或者用insertRow
        try:
            sqlconn = sqlite3.connect("../db/fileinfo.db")
        except sqlite3.Error, e:
            print "sqlite connect failed" , "\n", e.args[0]
        sqlcursor = sqlconn.cursor()
        sqlcursor.execute("select * from base_info where id =?", (int(i-1),))
        sqlconn.commit()
        sqlcursor = sqlcursor.fetchone()
        sqlconn.close()
        fsize = str(sqlcursor[3])
        ftype = str(sqlcursor[4])
        fMD5  = str(sqlcursor[5])
        p, f  = os.path.split(str(sqlcursor[1]).decode('utf-8')) # 分割文件路径与文件名
        self.table.setItem(i - 1, 0, QtGui.QTableWidgetItem(f))
        self.table.setItem(i - 1, 1, QtGui.QTableWidgetItem(p))
        sizeitem = QtGui.QTableWidgetItem(fsize+"  ")
        # 设置单元内容对齐方式
        sizeitem.setTextAlignment(Qt.Qt.AlignRight|Qt.Qt.AlignVCenter)
        self.table.setItem(i - 1, 2, sizeitem)
        self.table.setItem(i - 1, 3, QtGui.QTableWidgetItem(ftype))
        self.table.setItem(i - 1, 7, QtGui.QTableWidgetItem(fMD5))

    def updateStatusBar(self, msg):
        print unicode(msg) + " recv from updatedata class"
        self.ui.statusbar.showMessage(msg)       

    def updateTableMsg(self):
        pass

    '''
    初始化时从数据库中读取内容并更新
    msg:数据库查询返回元组
    '''
    def updateFromDBInit(self, msg):
        info  = msg
        index = info[0] + 1 # index标记
        self.table.setRowCount(index)
        p, f  = os.path.split(str(info[1]).decode('utf-8'))
        size  = str(info[3])
        ftype = str(info[4])
        md5   = str(info[5])
        index -= 1
        # self.table.setItem(index - 1, 0, QtGui.QTableWidgetItem(f))
        self.table.setItem(index, 0, QtGui.QTableWidgetItem(f))
        self.table.setItem(index, 1, QtGui.QTableWidgetItem(p))
        sizeitem = QtGui.QTableWidgetItem(size+"  ")
        sizeitem.setTextAlignment(Qt.Qt.AlignRight|Qt.Qt.AlignVCenter)
        self.table.setItem(index, 2, QtGui.QTableWidgetItem(sizeitem))
        self.table.setItem(index, 3, QtGui.QTableWidgetItem(ftype))
        self.table.setItem(index, 7, QtGui.QTableWidgetItem(md5))

    '''
    checkbox事件
    @flag: 标记全选与其他
    '''
    def checkBoxEvent(self, flag):
        ruleslist = [self.cbryara, self.cbrclam, self.cbrpack, self.cbrself, self.cbrwl]
        typeslist = [self.cbtpe, self.cbtofs, self.cbtsh, self.cbtzip, self.cbtmda, self.cbtasm]
        if flag == 0: # 对应rule全选操作
            if self.cbrall.isChecked():
                print "all rules selected"
                for i in ruleslist:
                    i.setCheckState(Qt.Qt.Checked)
            else:
                for i in ruleslist:
                    i.setCheckState(Qt.Qt.Unchecked)
        elif flag == 1: # 对应type全选操作
            if self.cbtall.isChecked():
                print "all type selected"
                for i in typeslist:
                    i.setCheckState(Qt.Qt.Checked)
            else:
                for i in typeslist:
                    i.setCheckState(Qt.Qt.Unchecked)
        else:
            if self.cbrall.isChecked() or self.cbtall.isChecked():
                if flag < 7:
                    self.cbrall.setCheckState(Qt.Qt.Unchecked)
                else:
                    self.cbtall.setCheckState(Qt.Qt.Unchecked)
        policy = self.getScanPolicy()
        if set(self.rulelist).issubset(set(policy)):
            self.cbrall.setCheckState(Qt.Qt.Checked)
        if set(self.typelist).issubset(set(policy)):
            self.cbtall.setCheckState(Qt.Qt.Checked)
    
    '''
    获取数据库设置及扫描文件类型策略
    判断checkbox勾选情况
    默认使用内置规则检测pe文件
    return policy列表
    '''
    def getScanPolicy(self):
        policy = []
        if self.cbrall.isChecked():
            policy.append("0")
        if self.cbtall.isChecked():
            policy.append("1")
        if self.cbryara.isChecked():
            policy.append("2")
        if self.cbrclam.isChecked():
            policy.append("3")
        if self.cbrpack.isChecked():
            policy.append("4")
        if self.cbrself.isChecked():
            policy.append("5")
        if self.cbrwl.isChecked():
            policy.append("6")
        if self.cbtpe.isChecked():
            policy.append("7")
        if self.cbtofs.isChecked():
            policy.append("8")
        if self.cbtsh.isChecked():
            policy.append("9")
        if self.cbtzip.isChecked():
            policy.append("10")
        if self.cbtmda.isChecked():
            policy.append("11")
        if self.cbtasm.isChecked():
            policy.append("12")
        return policy

    '''
    菜单栏点击事件响应函数
    '''
    def menuBarOperate(self, index):
        print index
        if 1 == index:
            dialog = self.setdialog
            dialog.setWindowFlags(Qt.Qt.WindowStaysOnTopHint)
            icon = QtGui.QIcon()
            icon.addPixmap(QtGui.QPixmap(".\UILib\icons\setting_icon.ico"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
            dialog.setWindowIcon(icon)
            dialog.show()
        if 6 == index:
            dialog = self.authorinfo
            icon = QtGui.QIcon()
            icon.addPixmap(QtGui.QPixmap(".\UILib\icons\pk.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
            dialog.setWindowIcon(icon)
            dialog.show()
        
    '''
    右键菜单生成函数
    仍需完善策略
    '''
    def generateMenu(self, pos):
        # 未选中元素时无法使用右键菜单
        # currentrow = self.table.currentRow()
        # print currentrow
        # if currentrow < 0:
        #     return
        print pos
        row_num = -1 # 右键操作列索引
        for i in self.table.selectionModel().selection().indexes():
            row_num = i.row()
        print row_num
        if row_num < 0:
            return
        menu = QtGui.QMenu()
        item1 = menu.addAction(QtGui.QIcon(".\UILib\icons\detail_icon.png"), u"详细信息") # (u"详细信息")
        item2 = menu.addAction(QtGui.QIcon(".\UILib\icons\Fanalyz_icon.png"), u"文件分析")
        item3 = menu.addAction(QtGui.QIcon(".\UILib\icons\img_icon.png"), u"二进制图像")
        item4 = menu.addAction(QtGui.QIcon(".\UILib\icons\delete_icon.png"), u"删除文件")
        item5 = menu.addAction(QtGui.QIcon(".\UILib\icons\locate_icon.png"), u"打开文件位置")
        markmenu = menu.addMenu(QtGui.QIcon(".\UILib\icons\usermark_icon.png"), u"用户标记")
        item6 = markmenu.addAction(u"分析完成")
        item7 = markmenu.addAction(u"仍需分析")
        item8 = markmenu.addAction(u"3")
        item9 = menu.addAction(QtGui.QIcon(".\UILib\icons\upload_icon.png"), u"上传样本")
        action = menu.exec_(self.table.mapToGlobal(pos))
        fname = self.table.item(row_num, 0).text()
        fpath = self.table.item(row_num, 1).text()
        ffull = os.path.join(str(fpath), str(fname)) # 文件绝对路径
        fmd5  = self.table.item(row_num, 7).text()
        flist = self.flist # 文件名列表
        flist.append(fmd5)
        print flist
        if action == item1:
            print u'您选了选项一，当前行文字内容是：',self.table.item(row_num,0).text()
            print ffull
            filedetail = self.detailDialog
            filedetail.getFileName(ffull)
            filedetail.setWindowFlags(Qt.Qt.WindowStaysOnTopHint)
            icon = QtGui.QIcon()
            icon.addPixmap(QtGui.QPixmap(".\UILib\icons\detail_icon.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
            filedetail.setWindowIcon(icon)
            filedetail.show()
            
        elif action == item2:
            print u'您选了选项二，当前行文字内容是：',self.table.item(row_num,0).text()

        elif action == item3:
            print u'您选了选项三，当前行文字内容是：',self.table.item(row_num,0).text()
        
        elif action == item5:
            print u"打开文件所在位置"
            fname = self.table.item(row_num, 0).text()
            fpath = self.table.item(row_num, 1).text()
            ffull = os.path.join(str(fpath), str(fname))
            # 仅打开文件夹
            # os.startfile(fpath)
            # 打开文件-慎重
            # os.startfile(ffull)
            # 打开文件夹并定位到文件
            estr = 'explorer /select,' + str(ffull)
            os.system(estr)

        elif action == item9:
            # 在没有数据库的情况下
            # 如果前后两次打开同一个文件，那么不清空内容
            # 否则执行clear方法
            dialog = self.uploadDialog
            dialog.getFilename(ffull)
            if len(flist) == 2:
                if flist[0] != flist[1]:
                    dialog.clearFileData()
                del flist[0]
            print flist
            dialog.setWindowFlags(Qt.Qt.WindowStaysOnTopHint)
            icon = QtGui.QIcon()
            icon.addPixmap(QtGui.QPixmap(".\UILib\icons\upload_icon.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
            dialog.setWindowIcon(icon)
            dialog.show()

        else:
            return

    '''
    表头点击事件
    index:表头section索引值
    '''
    def tableHeaderEvent(self, index):
        if 0 == FlagSet.scansqlcount:
            return
        self.table.horizontalHeader().setSortIndicatorShown(True)
        if 0 == index:
            print u"按文件名排序"
            self.table.sortByColumn(0)
        elif 1 == index:
            print u"按文件路径排序"
            self.table.sortByColumn(1)
        elif 2 == index:
            print u"按文件大小排序，单位Bytes"
            # 使用sort方法时将以qstirng方式排序
        elif 3 == index:
            print u"按文件类型排序"
            self.table.sortByColumn(3)
        elif 4 == index:
            print u"按扫描结果排序"

        elif 5 == index:
            print u"按用户标记排序"

        elif 6 == index:
            print u"按分析日期排序"

        else:
            print "MD5"
            self.table.horizontalHeader().setSortIndicatorShown(False)
            pass

    '''
    清空tablewidget内容
    '''
    def clearTableWidget(self):
        print self.table.rowCount()
        print "clear tablewidget"
        self.table.setRowCount(0)
        self.table.clearContents()
        self.rowindex = 0 # 让新元素从第一行开始
        self.ui.progressBar.setValue(0) # 进度条回0
        self.ui.statusbar.showMessage(u"已清空显示列表内容")
        try:
            sqlconn = sqlite3.connect("../db/fileinfo.db")
        except sqlite3.Error, e:
            print "sqlite connect failed" , "\n", e.args[0]
        sqlcursor = sqlconn.cursor()
        sqlcursor.execute("delete from base_info where id >= 0")
        sqlconn.commit()
        sqlconn.close()
        FlagSet.scansqlcount = 0 # 将全局计数flag置0
        self.table.horizontalHeader().setSortIndicatorShown(False)

    '''
    重写窗口关闭事件
    '''
    def closeEvent(self, event):
        # 无数据时直接退出
        if 0 == FlagSet.scansqlcount:
            return
        quitbtn = QtGui.QMessageBox()
        # quitbtn.setButtonText(quitbtn.Yes, u"llaalf")
        recv = quitbtn.question(self, u"退出", u"是否保存当前信息", \
                                                        quitbtn.Yes, \
                                                        quitbtn.No, \
                                                        quitbtn.Cancel )
        if recv == quitbtn.No:
            try:
                sqlconn = sqlite3.connect("../db/fileinfo.db")
            except sqlite3.Error, e:
                print "sqlite connect failed" , "\n", e.args[0]
            sqlcursor = sqlconn.cursor()
            sqlcursor.execute("delete from base_info where id >= 0")
            sqlconn.commit()
            sqlconn.close()
        elif recv == quitbtn.Yes:
            print "saved"
            pass
            # 再保存一下scansqlcount计数
        else:
            event.ignore()

    '''
    窗口打开事件
    '''
    def showEvent(self, event):
        try:
            sqlconn = sqlite3.connect("../db/fileinfo.db")
        except sqlite3.Error, e:
            print "sqlite connect failed" , "\n", e.args[0]
        sqlcursor = sqlconn.cursor()
        sqlcursor.execute("select * from base_info where md5 not NULL")
        sqlconn.commit()
        for raw in sqlcursor:
            self.updateFromDBInit(raw)
        sqlconn.close()
        print self.table.rowCount()
        FlagSet.scansqlcount = self.table.rowCount() # 为打开窗口不清数据做准备


if __name__ == "__main__":

    app = QtGui.QApplication(sys.argv)
    myapp = MainWindow()
    icon = QtGui.QIcon()
    icon.addPixmap(QtGui.QPixmap(".\UILib\icons\main_icon.ico"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
    myapp.setWindowIcon(icon)
    myapp.show()

    sys.exit(app.exec_())