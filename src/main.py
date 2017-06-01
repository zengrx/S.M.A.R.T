# -*- coding: utf-8 -*-

'''
    S.M.A.R.T.
    Static Malware Analysis and Report Tool
    author: Zeng RuoXing

'''

from PyQt4 import QtGui, QtCore, Qt
from UILib.main import Ui_MainWindow
import time, sys, os, shutil
from datetime import datetime
from control import CheckFolder, ScanFile
from menuset.setting import Dialog as SetDialog
from menuset.validation import Dialog as mlvdDialog
from menuset.editwhitelist import Dialog as WtLDialog
from menuset.authorinfo import Dialog as AuthorInfo
from menuset.filedetail import Dialog as DetailDialog
from menuset.ngramopcode import Dialog as OpcodeDialog
from menuset.malimgclassify import Dialog as MalimgDialog
from menuset.uploadfile import Dialog as UploadDialog
from globalset import FlagSet, FilePath, StaticValue
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
        self.cbrpe   = self.ui.CBRulePE     # PE分析
        self.cbrcryp = self.ui.CBRuleCrypto # 检查加密
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

        # 扫描选项下拉菜单
        self.cbbox = self.ui.comboBox

        # 初始按键不可用
        self.ui.PB_Start.setEnabled(False)
        self.ui.PB_End.setEnabled(False)
        self.ui.PB_SelectHistory.setEnabled(False)

        # tab2信息显示textEdit
        self.text = self.ui.textEdit
        self.ui.PB_ClearLog.clicked.connect(self.clearAnalysisLog)
        self.ui.PB_KeepLog.clicked.connect(self.saveAnalysisLog)
        
        # tab3日历widget
        self.calender = self.ui.calendarWidget
        self.calender.clicked.connect(self.getCalenderDate)
        self.table2 = self.ui.tableWidget_2
        self.historydb = ''
        self.ui.PB_SelectHistory.clicked.connect(lambda: self.queryDBOperate(2))

        # 设置tablewdiget属性
        # 自动适配header宽度，效果不好后期改适配最后一列
        # setStretchLastSection已在ui文件中设置 
        # 设置不可编辑 设置每次选中一行 设置可多选
        # 设置id列不显示
        self.table = self.ui.tableWidget
        # self.table.horizontalHeader().setResizeMode(QtGui.QHeaderView.Stretch)
        # self.table.horizontalHeader().setStretchLastSection(True)
        self.table.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)
        self.table.setContextMenuPolicy(Qt.Qt.CustomContextMenu)
        self.table.setSelectionMode(QtGui.QAbstractItemView.ExtendedSelection)
        self.table.setColumnHidden(8, True)

        # tablewidget信号槽--排序
        self.table.horizontalHeader().sectionClicked.connect(self.tableHeaderEvent)
        
        # 右键菜单信号槽
        self.table.customContextMenuRequested.connect(self.generateMenu)

        # 菜单栏控件-索引字典
        self.menubardict = {
            self.ui.AC_Check   : 0, # 检查配置 
            self.ui.AC_Setting : 1, # 软件设置
            self.ui.AC_CheckML : 2, # 机器学习
            self.ui.AC_EditWL  : 3, # 名单设置
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
        self.ui.AC_CheckML.triggered.connect(lambda: self.menuBarOperate(2))
        self.ui.AC_EditWL.triggered.connect(lambda: self.menuBarOperate(3))
        self.ui.AC_Info.triggered.connect(lambda: self.menuBarOperate(4))
        self.ui.AC_About.triggered.connect(lambda: self.menuBarOperate(5))
        self.ui.AC_Author.triggered.connect(lambda: self.menuBarOperate(6))
        
        self.scanflag = 0  # 扫描策略flag
        self.folder   = '' # 选取文件夹路径
        self.files    = [] # 最终选取的文件名列表
        self.depth    = -1
        self.dirsnum  = 0
        self.filenum  = 0
        self.table    = self.ui.tableWidget
        self.rowindex = 0
        self.rulelist = ['2', '3', '4', '5', '6']
        self.typelist = ['7', '8', '9', '10', '11', '12']
        self.rule     = [] # 发送至control的扫描规则
        self.type     = [] # 发送至control的文件类型
        self.flist    = [] # uploadfile判断更新滑动窗口
        self.enter    = -1 # 回车更新数据库id

        # 其他窗口对象实例
        self.setdialog    = SetDialog() # 设置
        self.mlvddialog   = mlvdDialog()   # 机器学习验证
        self.wtldialog    = WtLDialog()    # 白名单
        self.authorinfo   = AuthorInfo() # 作者
        self.detailDialog = DetailDialog() # 文件信息
        self.opcodeDialog = OpcodeDialog() # 操作码n元语法分类
        self.malimgDialog = MalimgDialog() # 二进制文件图像分类
        self.uploadDialog = UploadDialog() # 文件上传

        # 按钮事件信号槽
        QtCore.QObject.connect(self.ui.PB_SelectFolder, QtCore.SIGNAL("clicked()"), self.selectFolder)
        QtCore.QObject.connect(self.ui.PB_Start, QtCore.SIGNAL("clicked()"), self.startScan)
        QtCore.QObject.connect(self.ui.PB_Clear, QtCore.SIGNAL("clicked()"), self.clearTableWidget)
        self.ui.PB_End.clicked.connect(self.stopScan)
        self.ui.PB_Recover.clicked.connect(lambda: self.queryDBOperate(0))
        self.ui.PB_Select.clicked.connect(lambda: self.queryDBOperate(1))
        self.ui.PB_Store.clicked.connect(self.store2DataBaseByDate)

        self.fuzzy = self.ui.lineEditSelect # 模糊查询lineEdit
        
        # checkbox信号槽
        # 使用lambda表达式自定义参数
        self.cbrall.clicked.connect(lambda: self.checkBoxEvent(0))
        self.cbtall.clicked.connect(lambda: self.checkBoxEvent(1))
        self.cbrpe.clicked.connect(lambda: self.checkBoxEvent(2))
        self.cbrcryp.clicked.connect(lambda: self.checkBoxEvent(3)) 
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
        advmsg = "文件扩展名：" + str(StaticValue.adextension)
        self.ui.lineEditAdvSet.setText(unicode(advmsg))
        if 0 == self.cbbox.currentIndex():
            self.scanflag = 0
            self.folder = QtGui.QFileDialog.getExistingDirectory(self, u"选择文件夹", "e:\\")#QtCore.QDir.currentPath())
            if self.folder:
                showmsg = u"选择：" + self.folder
                self.ui.statusbar.showMessage(showmsg)
                self.ui.lineEditScanStart.setText(self.folder)
            else:
                self.ui.lineEditScanStart.setText('')
                self.ui.statusbar.showMessage(u"操作取消")
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
                self.ui.lineEditScanStart.setText('')
                self.ui.statusbar.showMessage(u"操作取消")
        else:
            pass
        # 选择完成后激活开始按键
        if self.ui.lineEditScanStart.text() == '':
                self.ui.PB_Start.setEnabled(False)
                return
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
        FlagSet.scandoneflag = 0 # 恢复完成标识
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
            self.depth = self.ui.spinBox.value()
            print "start: " + str(self.folder).decode('utf-8')
            if self.folder != '':
                # send folder filetype, scanrule and folder depth to fliter
                self.folderThread = CheckFolder(self.folder, self.type, self.rule, self.depth)
                # two signals connect one slot
                self.folderThread.numberSignal.connect(self.recvInitSingal)
                self.folderThread.folderSignal.connect(self.showFileAnalyzLog)
                #执行run方法
                self.folderThread.start()
        elif 1 == self.scanflag: # 选择文件
            if self.files:
                self.filenum = len(self.files)
                # 直接连接control中的scanfile线程
                self.filesThread = ScanFile(self.files, self.rule)
                self.filesThread.fileSignal.connect(self.updateScanInfo) # 连到更新函数中
                self.filesThread.smsgSignal.connect(self.updateStatusBar)
                self.filesThread.flogSignal.connect(self.showFileAnalyzLog)
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
                FlagSet.scandoneflag = 1
                self.ui.PB_Start.setEnabled(True)
                self.ui.PB_Clear.setEnabled(True)
                self.ui.PB_End.setEnabled(False)
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
            self.scanThread.flogSignal.connect(self.showFileAnalyzLog)
            self.scanThread.start()

    '''
    可对应添加scanfile信号发射的参数
    @msg:文件绝对路径，将分割为文件名+路径
    @文件类型
    @文件日期
    @文件大小
    @文件MD5
    '''
    def updateScanInfo(self, num, msg):
        self.updateStatusBar(num, msg)
        # 更新tablewidget
        self.rowindex = FlagSet.scansqlcount
        i = self.rowindex
        # print i
        self.table.setRowCount(i)
        # 或者用insertRow
        sqlcursor = self.readFromDB(i)
        fid   = str(sqlcursor[0])
        fsize = str(sqlcursor[2])
        ftype = str(sqlcursor[3])
        ftime = self.convertTime(sqlcursor[4])
        fMD5  = str(sqlcursor[5])
        mark  = str(sqlcursor[7]).decode('utf-8')
        p, f  = os.path.split(str(sqlcursor[1]).decode('utf-8')) # 分割文件路径与文件名
        self.table.setItem(i - 1, 0, QtGui.QTableWidgetItem(f))
        self.table.setItem(i - 1, 1, QtGui.QTableWidgetItem(p))
        sizeitem = QtGui.QTableWidgetItem(fsize+"  ")
        # 设置单元内容对齐方式
        if int(fsize) > 100*1024*1024:
            sizeitem.setTextColor(Qt.Qt.red)
        sizeitem.setTextAlignment(Qt.Qt.AlignRight|Qt.Qt.AlignVCenter)
        self.table.setItem(i - 1, 2, sizeitem)
        self.table.setItem(i - 1, 3, QtGui.QTableWidgetItem(ftype))
        detection = self.convertSocre2Rank(sqlcursor[6])
        self.table.setItem(i - 1, 4, detection)
        self.table.setItem(i - 1, 5, QtGui.QTableWidgetItem(mark))
        self.table.setItem(i - 1, 6, ftime)
        self.table.setItem(i - 1, 7, QtGui.QTableWidgetItem(fMD5))
        self.table.setItem(i - 1, 8, QtGui.QTableWidgetItem(fid))

    '''
    更新重新扫描返回事件
    '''
    def updateRescanInfo(self, num, msg):
        self.updateStatusBar(int(msg), msg)
        # 更改tablewidget内容
        infos = self.readFromDB(num + 1)
        print infos
        line = -1
        for i in range(self.table.rowCount()):
            if int(self.table.item(i, 8).text()) == num:
                line = i
        if -1 == line:
            print "sql id error"
            return
        detection = self.convertSocre2Rank(infos[6])
        dtime     = self.convertTime(infos[4])
        mark      = str(infos[7]).decode('utf-8')
        self.table.setItem(line, 4, detection)
        self.table.setItem(line, 5, QtGui.QTableWidgetItem(mark))
        self.table.setItem(line, 6, dtime)

    '''
    读取数据库信息
    更新tablewidget显示
    '''
    def readFromDB(self, index):
        i = index
        try:
            sqlconn = sqlite3.connect("../db/fileinfo.db")
        except sqlite3.Error, e:
            print "sqlite connect failed" , "\n", e.args[0]
        sqlcursor = sqlconn.cursor()
        sqlcursor.execute("select * from base_info where id =?", (int(i-1),))
        sqlconn.commit()
        sqlcursor = sqlcursor.fetchone()
        sqlconn.close()
        return sqlcursor

    '''
    更新进度条函数
    '''
    def updateStatusBar(self, num, msg):
        if -1 == num: # 显示yara规则库的检查信息
            self.ui.statusbar.showMessage(msg)
            self.ui.progressBar.setMaximum(0)
            self.ui.progressBar.setValue(0)
            return # 没有return进度条不会左右移动
        showmsg = 'recv result from file: ' + msg
        self.ui.statusbar.showMessage(showmsg)
        # 更新进度条 最大值和当前值放在一起
        self.ui.progressBar.setMaximum(int(self.filenum))
        self.ui.progressBar.setValue(num)
        if int(self.filenum) == num:
            self.ui.statusbar.showMessage(u"扫描结束")
            FlagSet.scandoneflag = 1
            self.ui.PB_Start.setEnabled(True)
            self.ui.PB_Clear.setEnabled(True)
            self.ui.PB_End.setEnabled(False)

    def updateTableMsg(self):
        pass

    '''
    数据库模糊查询
    @flag:查询标记 1-执行查询 0-恢复内容 2-历史记录查询
    '''
    def queryDBOperate(self, flag):
        print flag
        # 构造模糊查询条件
        # 默认赋值tab1内容
        sql = unicode("'%" + str(self.fuzzy.text()) + "%'")
        condition = unicode(self.ui.comboBox_2.currentText())
        dbname = "../db/fileinfo.db"
        if 2 == flag:
            sql = unicode("'%" + str(self.ui.LE_FuzzyHistory.text()) + "%'")
            condition = condition = unicode(self.ui.comboBox_3.currentText())
            dbname = self.historydb
        try:
            sqlconn = sqlite3.connect(dbname)
        except sqlite3.Error, e:
            print "sqlite connect failed" , "\n", e.args[0]
        sqlcursor = sqlconn.cursor()
        if 0 == flag:
            sqlcursor.execute("select * from base_info where md5 not NULL")
        elif 1 == flag or 2 == flag:        
            sqlcursor.execute("select * from base_info where " + condition + " like " + sql)
        else:
            print "database query flag error"
            return
        sqlconn.commit()
        i = 0
        for raw in sqlcursor:
            i += 1
            if 2 == flag:
                self.updateFromHistoryDB(i, raw)
                continue
            self.updateFromDBInit(i, raw)
        sqlconn.close()

    '''
    初始化时从数据库中读取内容并更新
    msg:数据库查询返回元组
    '''
    def updateFromDBInit(self, index, msg):
        info  = msg
        # index = info[0] + 1 # index标记
        self.table.setRowCount(index)
        p, f  = os.path.split(str(info[1]).decode('utf-8'))
        fid   = str(info[0])
        size  = str(info[2])
        ftype = str(info[3])
        ftime = float(info[4])
        md5   = str(info[5])
        score = int(info[6])
        mark  = str(info[7]).decode('utf-8')
        index -= 1
        dtime = self.convertTime(ftime)
        # self.table.setItem(index - 1, 0, QtGui.QTableWidgetItem(f))
        self.table.setItem(index, 0, QtGui.QTableWidgetItem(f))
        self.table.setItem(index, 1, QtGui.QTableWidgetItem(p))
        sizeitem = QtGui.QTableWidgetItem(size+"  ")
        if int(size) > 100*1024*1024:
            sizeitem.setTextColor(Qt.Qt.red)
        detection = self.convertSocre2Rank(score)
        self.table.setItem(index, 4, detection)
        sizeitem.setTextAlignment(Qt.Qt.AlignRight|Qt.Qt.AlignVCenter)
        self.table.setItem(index, 5, QtGui.QTableWidgetItem(mark))
        self.table.setItem(index, 2, QtGui.QTableWidgetItem(sizeitem))
        self.table.setItem(index, 3, QtGui.QTableWidgetItem(ftype))
        self.table.setItem(index, 6, dtime)
        self.table.setItem(index, 7, QtGui.QTableWidgetItem(md5))
        self.table.setItem(index, 8, QtGui.QTableWidgetItem(fid))

    '''
    转换score数值与评判结果
    '''
    def convertSocre2Rank(self, score):
        if score >= 15:
            detection = QtGui.QTableWidgetItem(u"危险 - " + str(score))
            detection.setTextColor(Qt.Qt.red)
        if score >= 10 and score < 15:
            detection = QtGui.QTableWidgetItem(u"可疑 - " + str(score))
            detection.setTextColor(Qt.Qt.darkRed)
        if score >= 5 and score < 10:
            detection = QtGui.QTableWidgetItem(u"常规 - " + str(score))
            detection.setTextColor(Qt.Qt.darkYellow)
        if score < 5 and score >=0:
            detection = QtGui.QTableWidgetItem(u"安全 - " + str(score))
            detection.setTextColor(Qt.Qt.green)
        if score < 0:
            detection = QtGui.QTableWidgetItem(u" 不支持类型 ")
            detection.setTextColor(Qt.Qt.blue)
        detection.setTextAlignment(Qt.Qt.AlignCenter)
        return detection

    '''
    转换时间函数
    '''
    def convertTime(self, intime):
        nowtime   = time.time()
        localtime = time.localtime(intime)
        midnight  = nowtime - nowtime % 86400 + time.timezone
        if intime < midnight:
            outtime = time.strftime(' %Y-%m-%d ', localtime)
        else:
            outtime = time.strftime('%H:%M:%S', localtime)
        outtime = QtGui.QTableWidgetItem(outtime)
        outtime.setTextAlignment(Qt.Qt.AlignCenter)
        return outtime

    '''
    checkbox事件
    @flag: 标记全选与其他
    '''
    def checkBoxEvent(self, flag):
        ruleslist = [self.cbrpe, self.cbrcryp, self.cbrpack, self.cbrself, self.cbrwl]
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
        if self.cbrpe.isChecked():
            policy.append("2")
        if self.cbrcryp.isChecked():
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
            icon.addPixmap(QtGui.QPixmap("./UILib/icons/setting_icon.ico"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
            dialog.setWindowIcon(icon)
            dialog.show()
        if 2 == index:
            dialog = self.mlvddialog
            dialog.show()
        if 3 == index:
            dialog = self.wtldialog
            dialog.setWindowFlags(Qt.Qt.WindowStaysOnTopHint)
            # icon = QtGui.QIcon()
            # icon.addPixmap(QtGui.QPixmap(".\\UILib\\icons\\setting_icon.ico"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
            # dialog.setWindowIcon(icon)
            dialog.show()
        if 6 == index:
            dialog = self.authorinfo
            icon = QtGui.QIcon()
            icon.addPixmap(QtGui.QPixmap("./UILib/icons/pk.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
            dialog.setWindowIcon(icon)
            dialog.show()
        
    '''
    右键菜单生成函数
    仍需完善策略
    '''
    def generateMenu(self, pos):
        # 未选中元素时无法使用右键菜单
        print pos # 原始坐标
        row_num = [] # 右键操作列索引列表
        rid_num = [] # 右键id索引列表
        for i in self.table.selectionModel().selection().indexes():
            row_num.append(i.row())
            rid_num.append(int(self.table.item(i.row(), 8).text()))
        row_num = list(set(row_num))
        rid_num = list(set(rid_num))
        # print row_num
        # print len(row_num)
        # 未选中任何一行
        if len(row_num) < 1:
            return
        # 选中多行
        elif len(row_num) > 1:
            print u"多选"
            mumenu  = QtGui.QMenu()
            muitem1 = mumenu.addAction(QtGui.QIcon("./UILib/icons/drescan_icon.png"), u"重新扫描")
            if 0 == FlagSet.scandoneflag:
                muitem1.setEnabled(False)
            maction = mumenu.exec_(self.table.mapToGlobal(pos))
            if maction == muitem1:
                print "get clicked"
                self.filenum = len(row_num)
                rescanfiles  = ("rescan", rid_num)
                print rescanfiles
                # 直接连接control中的scanfile线程
                self.rule, useless = self.prevScanPrepare()
                self.filesThread = ScanFile(rescanfiles, self.rule)
                self.filesThread.fileSignal.connect(self.updateRescanInfo) # 连到更行重新函数中
                self.filesThread.smsgSignal.connect(self.updateStatusBar)
                self.filesThread.flogSignal.connect(self.showFileAnalyzLog)
                self.filesThread.start()
        # 选中一行
        else:
            row_num = row_num[0]
            menu = QtGui.QMenu()
            item1 = menu.addAction(QtGui.QIcon("./UILib/icons/detail_icon.png"), u"详细信息") # (u"详细信息")
            item2 = menu.addAction(QtGui.QIcon("./UILib/icons/drescan_icon.png"), u"重新扫描")
            advmenu = menu.addMenu(QtGui.QIcon("./UILib/icons/robot_icon.png"), u"机器学习")
            item3 = advmenu.addAction(QtGui.QIcon("./UILib/icons/img_icon.png"), u"二进制图像")
            item4 = advmenu.addAction(QtGui.QIcon("./UILib/icons/code_icon.png"), u"操作码分类")
            item5 = menu.addAction(QtGui.QIcon("./UILib/icons/mark_icon.png"), u"文件位置")
            item6 = menu.addAction(QtGui.QIcon("./UILib/icons/user_icon.png"), u"用户标记")
            item7 = menu.addAction(QtGui.QIcon("./UILib/icons/upload_icon.png"), u"上传样本")
            fname = self.table.item(row_num, 0).text()
            fpath = self.table.item(row_num, 1).text()
            ffull = os.path.join(str(fpath), str(fname)) # 文件绝对路径
            fmd5  = self.table.item(row_num, 7).text()
            if 0 == FlagSet.scandoneflag:
                item2.setEnabled(False)
                item6.setEnabled(False)
            # if 'PE32' not in self.table.item(row_num, 3).text() and 'executable' not in self.table.item(row_num, 3).text():
            # 更改为png图片及可执行文件都触发
            ext = os.path.splitext(str(fname))[1]
            t_type = self.table.item(row_num, 3).text()
            if 'PE32' not in t_type and 'MS-DOS' not in t_type and 'png' not in ext:
                item3.setEnabled(False)
            if not str(self.table.item(row_num, 0).text()).endswith('.asm'):
                item4.setEnabled(False)
            action = menu.exec_(self.table.mapToGlobal(pos))
            if action == item1:
                # print u'您选了选项一，当前行文字内容是：', self.table.item(row_num, 0).text()
                print ffull
                filedetail = self.detailDialog
                filedetail.getFileName(ffull, fmd5)
                filedetail.setWindowFlags(Qt.Qt.WindowStaysOnTopHint)
                icon = QtGui.QIcon()
                icon.addPixmap(QtGui.QPixmap("./UILib/icons/detail_icon.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
                filedetail.setWindowIcon(icon)
                filedetail.show()
            elif action == item2:
                self.filenum = 1
                rescan = []
                reid = int(self.table.item(row_num, 8).text())
                rescan.append(reid)
                rescanfiles = ("rescan", rescan)
                print rescanfiles
                # 直接连接control中的scanfile线程
                self.rule, useless = self.prevScanPrepare()
                self.filesThread = ScanFile(rescanfiles, self.rule)
                self.filesThread.fileSignal.connect(self.updateRescanInfo) # 连到更行重新函数中
                self.filesThread.smsgSignal.connect(self.updateStatusBar)
                self.filesThread.flogSignal.connect(self.showFileAnalyzLog)
                self.filesThread.start()
            elif action == item3:
                print "going to greate a pe image"
                malimgclass = self.malimgDialog
                malimgclass.getFileName(ffull)
                malimgclass.setWindowFlags(Qt.Qt.WindowStaysOnTopHint)
                icon = QtGui.QIcon()
                icon.addPixmap(QtGui.QPixmap("./UILib/icons/img_icon.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
                malimgclass.setWindowIcon(icon)
                malimgclass.show()
            elif action == item4:
                print "going to analysis asm file"
                opcodeclass = self.opcodeDialog
                opcodeclass.getFileName(ffull)
                opcodeclass.setWindowFlags(Qt.Qt.WindowStaysOnTopHint)
                icon = QtGui.QIcon()
                icon.addPixmap(QtGui.QPixmap("./UILib/icons/code_icon.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
                opcodeclass.setWindowIcon(icon)
                opcodeclass.show()
            elif action == item5:
                print u"打开文件所在位置"
                fname = self.table.item(row_num, 0).text()
                fpath = self.table.item(row_num, 1).text()
                # ffull = os.path.join(str(fpath).encode('cp936'), str(fname).encode('cp936'))
                # 仅打开文件夹
                # os.startfile(fpath)
                # 打开文件-慎重
                # os.startfile(ffull)
                # 打开文件夹并定位到文件
                print str(ffull).encode('cp936')
                estr = 'explorer /select,' + str(ffull).encode('cp936')
                print os.system(estr)
            elif action == item6:
                # 设置item可编辑
                self.table.editItem(self.table.item(row_num, 5))
                self.enter = row_num
                self.ui.statusbar.showMessage(u"修改后按回车更新标记内容")
            elif action == item7:
                # 在没有数据库的情况下
                # 如果前后两次打开同一个文件，那么不清空内容
                # 否则执行clear方法
                flist = self.flist # 文件名列表
                flist.append(fmd5)
                print flist
                dialog = self.uploadDialog
                dialog.getFilename(ffull)
                if len(flist) == 2:
                    if flist[0] != flist[1]:
                        dialog.clearFileData()
                    del flist[0]
                print flist
                dialog.setWindowFlags(Qt.Qt.WindowStaysOnTopHint)
                icon = QtGui.QIcon()
                icon.addPixmap(QtGui.QPixmap("./UILib/icons/upload_icon.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
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
            self.table.sortByColumn(index)
        elif 1 == index:
            print u"按文件路径排序"
            self.table.sortByColumn(index)
        elif 2 == index:
            print u"按文件大小排序，单位Bytes"
            sortflag = self.table.horizontalHeader().sortIndicatorOrder()
            print sortflag
            self.sortByFileSize(sortflag)
        elif 3 == index:
            print u"按文件类型排序"
            self.table.sortByColumn(index)
        elif 4 == index:
            print u"按扫描结果排序"
            self.table.sortByColumn(index)
        elif 5 == index:
            print u"按标记排序"
            self.table.sortByColumn(index)
        elif 6 == index:
            print u"按分析日期排序"
            self.table.sortByColumn(index)
        elif 7 == index:
            print u"按MD5值排序"
            self.table.sortByColumn(index)
        else:
            self.table.horizontalHeader().setSortIndicatorShown(False)
            pass

    '''
    tablewidget表头点击事件
    文件大小排序数据库操作
    '''
    def sortByFileSize(self, flag):
        try:
            sqlconn = sqlite3.connect("../db/fileinfo.db")
        except sqlite3.Error, e:
            print "sqlite connect failed" , "\n", e.args[0]
        sqlcursor = sqlconn.cursor()
        if 0 == flag:
            sqlcursor.execute("select * from base_info where md5 not NULL order by size")
        elif 1 == flag:
            sqlcursor.execute("select * from base_info where md5 not NULL order by size desc")
        else:
            print "sort flag error, quit..."
            sqlconn.close()
            return
        sqlconn.commit()
        i = 0
        for raw in sqlcursor:
            i += 1
            self.updateFromDBInit(i, raw)
        sqlconn.close()

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
    保存tab页内容至历史数据库
    '''
    def store2DataBaseByDate(self):
        tday = datetime.today()
        y = str(tday.year)
        m = str(tday.month)
        d = str(tday.day)
        src = "../db/fileinfo.db"
        dst = "../db/history/" + y + m + d + ".db"
        print src, dst
        shutil.copy(src, dst)
        if os.path.isfile(dst):
            self.ui.statusbar.showMessage(u"本页内容已保存至" + dst)

    #------------------------------tab2-----------------------------
    '''
    文件分析日志显示
    @flag:标记-暂未使用
    @msg:接收内容
    '''
    def showFileAnalyzLog(self, flag, msg):
        nowtime = time.localtime(time.time())
        nowtime = time.strftime('%Y-%m-%d %H:%M:%S', nowtime)
        nowtime = "[" + nowtime + "]  "
        self.text.append(nowtime + msg)

    '''
    清除历史分析
    '''
    def clearAnalysisLog(self):
        self.text.clear()
        self.showFileAnalyzLog(4, " clear all information")

    '''
    保存分析结果
    使用qtextstream流写入文件
    '''
    def saveAnalysisLog(self):
        tday = datetime.today()
        y = str(tday.year)
        m = str(tday.month)
        d = str(tday.day)
        H = str(tday.hour)
        M = str(tday.minute)
        S = str(tday.second)
        name = "../log/{}-{}-{}_{}-{}-{}.analy".format(y, m, d, H, M, S)
        try:
            ftmp = QtCore.QFile(name)
            ftmp.open(QtCore.QIODevice.WriteOnly)
            stream = QtCore.QTextStream(ftmp)
            slog = self.text.toPlainText()
            stream << slog
            self.ui.statusbar.showMessage(u"扫描报告保存成功")
        except IOError, e:
            print e.args[0]

    #------------------------------tab3-----------------------------
    '''
    显示分析历史信息
    获取日历控件响应
    '''
    def getCalenderDate(self):
        qdate = self.calender.selectedDate()
        y = str(qdate.year())
        m = str(qdate.month())
        d = str(qdate.day())
        flogs = "{}年{}月{}日文件分析记录".format(y, m, d)
        fname = "../db/history/" + y + m + d + ".db"
        self.historydb = fname
        if not os.path.isfile(fname):
            self.ui.statusbar.showMessage(u"无此日分析历史记录")
            self.ui.PB_SelectHistory.setEnabled(False)
            self.table2.setRowCount(0)
            self.table2.clearContents()
            return
        self.ui.PB_SelectHistory.setEnabled(True)
        try:
            sqlconn = sqlite3.connect(fname)
        except sqlite3.Error, e:
            print "sqlite connect failed" , "\n", e.args[0]
        self.ui.statusbar.showMessage(unicode(flogs))
        sqlcursor = sqlconn.cursor()
        sqlcursor.execute("select * from base_info where md5 not NULL")
        sqlconn.commit()
        i = 0
        for raw in sqlcursor:
            i += 1
            self.updateFromHistoryDB(i, raw)
        sqlconn.close()

    '''
    显示历史分析数据库内容
    @index:table索引
    @msg:查询记录
    '''
    def updateFromHistoryDB(self, index, msg):
        info  = msg
        # index = info[0] + 1 # index标记
        self.table2.setRowCount(index)
        p, f  = os.path.split(str(info[1]).decode('utf-8'))
        size  = str(info[2])
        ftype = str(info[3])
        ftime = float(info[4])
        md5   = str(info[5])
        score = int(info[6])
        mark  = str(info[7]).decode('utf-8')
        index -= 1
        dtime = self.convertTime(ftime)
        # self.table.setItem(index - 1, 0, QtGui.QTableWidgetItem(f))
        self.table2.setItem(index, 0, QtGui.QTableWidgetItem(f))
        self.table2.setItem(index, 1, QtGui.QTableWidgetItem(p))
        sizeitem = QtGui.QTableWidgetItem(size+"  ")
        if int(size) > 100*1024*1024:
            sizeitem.setTextColor(Qt.Qt.red)
        detection = self.convertSocre2Rank(score)
        self.table2.setItem(index, 4, detection)
        sizeitem.setTextAlignment(Qt.Qt.AlignRight|Qt.Qt.AlignVCenter)
        self.table2.setItem(index, 5, QtGui.QTableWidgetItem(mark))
        self.table2.setItem(index, 2, QtGui.QTableWidgetItem(sizeitem))
        self.table2.setItem(index, 3, QtGui.QTableWidgetItem(ftype))
        self.table2.setItem(index, 6, dtime)
        self.table2.setItem(index, 7, QtGui.QTableWidgetItem(md5))

    #------------------------------event-----------------------------
    '''
    重写键盘响应事件
    '''
    def keyPressEvent(self, event):
        if QtCore.Qt.Key_Enter and self.enter > -1:
            mark = unicode(self.table.item(self.enter, 5).text())
            tid  = int(self.table.item(self.enter, 8).text())
            # print mark, tid
            try:
                sqlconn = sqlite3.connect("../db/fileinfo.db")
            except sqlite3.Error, e:
                print "sqlite connect failed" , "\n", e.args[0]
            sqlcursor = sqlconn.cursor()
            sqlcursor.execute("update base_info set mark=? where id=?", (mark, tid))
            sqlconn.commit()
        self.enter = -1
        self.ui.statusbar.showMessage(u"用户标记已更新")

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
            # 下次开启窗口读取数据库count并传给sqlconunt
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
        i = 0
        for raw in sqlcursor:
            i += 1
            self.updateFromDBInit(i, raw)
        sqlconn.close()
        print self.table.rowCount()
        FlagSet.scansqlcount = self.table.rowCount() # 为打开窗口不清数据做准备
        # 加载白名单
        f = open(FilePath.whitelist, "r")
        f.readline()
        for line in f:
            FilePath.whitefile.append(str(line).split('\n')[0])


if __name__ == "__main__":

    app = QtGui.QApplication(sys.argv)
    myapp = MainWindow()
    icon = QtGui.QIcon()
    icon.addPixmap(QtGui.QPixmap("./UILib/icons/main_icon.ico"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
    myapp.setWindowIcon(icon)
    myapp.show()

    sys.exit(app.exec_())