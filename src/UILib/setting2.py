# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'setting2.ui'
#
# Created by: PyQt4 UI code generator 4.12
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

try:
    _encoding = QtGui.QApplication.UnicodeUTF8
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig)

class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName(_fromUtf8("Dialog"))
        Dialog.resize(421, 270)
        self.verticalLayout_2 = QtGui.QVBoxLayout(Dialog)
        self.verticalLayout_2.setObjectName(_fromUtf8("verticalLayout_2"))
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.listWidget = QtGui.QListWidget(Dialog)
        self.listWidget.setObjectName(_fromUtf8("listWidget"))
        item = QtGui.QListWidgetItem()
        self.listWidget.addItem(item)
        item = QtGui.QListWidgetItem()
        self.listWidget.addItem(item)
        item = QtGui.QListWidgetItem()
        self.listWidget.addItem(item)
        self.horizontalLayout.addWidget(self.listWidget)
        self.stackedWidget = QtGui.QStackedWidget(Dialog)
        self.stackedWidget.setObjectName(_fromUtf8("stackedWidget"))
        self.page = QtGui.QWidget()
        self.page.setObjectName(_fromUtf8("page"))
        self.label = QtGui.QLabel(self.page)
        self.label.setGeometry(QtCore.QRect(20, 20, 61, 16))
        self.label.setObjectName(_fromUtf8("label"))
        self.stackedWidget.addWidget(self.page)
        self.page_2 = QtGui.QWidget()
        self.page_2.setObjectName(_fromUtf8("page_2"))
        self.label_2 = QtGui.QLabel(self.page_2)
        self.label_2.setGeometry(QtCore.QRect(10, 23, 71, 21))
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.lineEdit = QtGui.QLineEdit(self.page_2)
        self.lineEdit.setGeometry(QtCore.QRect(80, 24, 221, 20))
        self.lineEdit.setObjectName(_fromUtf8("lineEdit"))
        self.label_3 = QtGui.QLabel(self.page_2)
        self.label_3.setGeometry(QtCore.QRect(10, 70, 71, 21))
        self.label_3.setObjectName(_fromUtf8("label_3"))
        self.stackedWidget.addWidget(self.page_2)
        self.page_3 = QtGui.QWidget()
        self.page_3.setObjectName(_fromUtf8("page_3"))
        self.label_4 = QtGui.QLabel(self.page_3)
        self.label_4.setGeometry(QtCore.QRect(10, 20, 111, 21))
        self.label_4.setObjectName(_fromUtf8("label_4"))
        self.label_5 = QtGui.QLabel(self.page_3)
        self.label_5.setGeometry(QtCore.QRect(10, 90, 111, 21))
        self.label_5.setObjectName(_fromUtf8("label_5"))
        self.label_6 = QtGui.QLabel(self.page_3)
        self.label_6.setGeometry(QtCore.QRect(10, 172, 121, 21))
        self.label_6.setObjectName(_fromUtf8("label_6"))
        self.LE_VTPub = QtGui.QLineEdit(self.page_3)
        self.LE_VTPub.setGeometry(QtCore.QRect(10, 41, 301, 20))
        self.LE_VTPub.setObjectName(_fromUtf8("LE_VTPub"))
        self.LE_FileExt = QtGui.QLineEdit(self.page_3)
        self.LE_FileExt.setGeometry(QtCore.QRect(10, 111, 301, 20))
        self.LE_FileExt.setObjectName(_fromUtf8("LE_FileExt"))
        self.lineEdit_4 = QtGui.QLineEdit(self.page_3)
        self.lineEdit_4.setGeometry(QtCore.QRect(132, 173, 50, 20))
        self.lineEdit_4.setObjectName(_fromUtf8("lineEdit_4"))
        self.stackedWidget.addWidget(self.page_3)
        self.horizontalLayout.addWidget(self.stackedWidget)
        self.horizontalLayout.setStretch(0, 1)
        self.horizontalLayout.setStretch(1, 10)
        self.verticalLayout_2.addLayout(self.horizontalLayout)
        self.horizontalLayout_2 = QtGui.QHBoxLayout()
        self.horizontalLayout_2.setObjectName(_fromUtf8("horizontalLayout_2"))
        spacerItem = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout_2.addItem(spacerItem)
        self.PB_Apply = QtGui.QPushButton(Dialog)
        self.PB_Apply.setObjectName(_fromUtf8("PB_Apply"))
        self.horizontalLayout_2.addWidget(self.PB_Apply)
        self.PB_Yes = QtGui.QPushButton(Dialog)
        self.PB_Yes.setObjectName(_fromUtf8("PB_Yes"))
        self.horizontalLayout_2.addWidget(self.PB_Yes)
        self.PB_Cancel = QtGui.QPushButton(Dialog)
        self.PB_Cancel.setObjectName(_fromUtf8("PB_Cancel"))
        self.horizontalLayout_2.addWidget(self.PB_Cancel)
        self.verticalLayout_2.addLayout(self.horizontalLayout_2)
        self.verticalLayout_2.setStretch(0, 6)

        self.retranslateUi(Dialog)
        self.stackedWidget.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        Dialog.setWindowTitle(_translate("Dialog", "软件设置", None))
        __sortingEnabled = self.listWidget.isSortingEnabled()
        self.listWidget.setSortingEnabled(False)
        item = self.listWidget.item(0)
        item.setText(_translate("Dialog", "基本设置", None))
        item = self.listWidget.item(1)
        item.setText(_translate("Dialog", "网络设置", None))
        item = self.listWidget.item(2)
        item.setText(_translate("Dialog", "高级设置", None))
        self.listWidget.setSortingEnabled(__sortingEnabled)
        self.label.setText(_translate("Dialog", "目录结构", None))
        self.label_2.setText(_translate("Dialog", "主网地址：", None))
        self.label_3.setText(_translate("Dialog", "主网地址：", None))
        self.label_4.setText(_translate("Dialog", "VirusTotal公钥：", None))
        self.label_5.setText(_translate("Dialog", "文件后缀名设置：", None))
        self.label_6.setText(_translate("Dialog", "Magic Mime设置：", None))
        self.lineEdit_4.setText(_translate("Dialog", "True", None))
        self.PB_Apply.setText(_translate("Dialog", "应  用", None))
        self.PB_Yes.setText(_translate("Dialog", "确  定", None))
        self.PB_Cancel.setText(_translate("Dialog", "取  消", None))


if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    Dialog = QtGui.QDialog()
    ui = Ui_Dialog()
    ui.setupUi(Dialog)
    Dialog.show()
    sys.exit(app.exec_())

