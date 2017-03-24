# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'setting.ui'
#
# Created by: PyQt4 UI code generator 4.11.4
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
        Dialog.resize(480, 600)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(Dialog.sizePolicy().hasHeightForWidth())
        Dialog.setSizePolicy(sizePolicy)
        Dialog.setMinimumSize(QtCore.QSize(480, 600))
        Dialog.setMaximumSize(QtCore.QSize(480, 600))
        self.verticalLayout = QtGui.QVBoxLayout(Dialog)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.toolBox = QtGui.QToolBox(Dialog)
        self.toolBox.setObjectName(_fromUtf8("toolBox"))
        self.PG_Base = QtGui.QWidget()
        self.PG_Base.setGeometry(QtCore.QRect(0, 0, 462, 499))
        self.PG_Base.setToolTip(_fromUtf8(""))
        self.PG_Base.setObjectName(_fromUtf8("PG_Base"))
        self.verticalLayout_2 = QtGui.QVBoxLayout(self.PG_Base)
        self.verticalLayout_2.setObjectName(_fromUtf8("verticalLayout_2"))
        self.groupBox = QtGui.QGroupBox(self.PG_Base)
        self.groupBox.setObjectName(_fromUtf8("groupBox"))
        self.verticalLayout_2.addWidget(self.groupBox)
        self.groupBox_2 = QtGui.QGroupBox(self.PG_Base)
        self.groupBox_2.setObjectName(_fromUtf8("groupBox_2"))
        self.verticalLayout_2.addWidget(self.groupBox_2)
        self.groupBox_3 = QtGui.QGroupBox(self.PG_Base)
        self.groupBox_3.setObjectName(_fromUtf8("groupBox_3"))
        self.verticalLayout_2.addWidget(self.groupBox_3)
        self.toolBox.addItem(self.PG_Base, _fromUtf8(""))
        self.PG_Advence = QtGui.QWidget()
        self.PG_Advence.setGeometry(QtCore.QRect(0, 0, 462, 499))
        self.PG_Advence.setObjectName(_fromUtf8("PG_Advence"))
        self.verticalLayout_3 = QtGui.QVBoxLayout(self.PG_Advence)
        self.verticalLayout_3.setObjectName(_fromUtf8("verticalLayout_3"))
        self.groupBox_4 = QtGui.QGroupBox(self.PG_Advence)
        self.groupBox_4.setObjectName(_fromUtf8("groupBox_4"))
        self.verticalLayout_3.addWidget(self.groupBox_4)
        self.groupBox_5 = QtGui.QGroupBox(self.PG_Advence)
        self.groupBox_5.setObjectName(_fromUtf8("groupBox_5"))
        self.verticalLayout_3.addWidget(self.groupBox_5)
        self.toolBox.addItem(self.PG_Advence, _fromUtf8(""))
        self.verticalLayout.addWidget(self.toolBox)
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        spacerItem = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem)
        self.PB_Confirm = QtGui.QPushButton(Dialog)
        self.PB_Confirm.setObjectName(_fromUtf8("PB_Confirm"))
        self.horizontalLayout.addWidget(self.PB_Confirm)
        self.PB_Cancel = QtGui.QPushButton(Dialog)
        self.PB_Cancel.setObjectName(_fromUtf8("PB_Cancel"))
        self.horizontalLayout.addWidget(self.PB_Cancel)
        self.PB_Apply = QtGui.QPushButton(Dialog)
        self.PB_Apply.setObjectName(_fromUtf8("PB_Apply"))
        self.horizontalLayout.addWidget(self.PB_Apply)
        self.verticalLayout.addLayout(self.horizontalLayout)

        self.retranslateUi(Dialog)
        self.toolBox.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        Dialog.setWindowTitle(_translate("Dialog", "设置", None))
        self.groupBox.setTitle(_translate("Dialog", "网络设置", None))
        self.groupBox_2.setTitle(_translate("Dialog", "上传设置", None))
        self.groupBox_3.setTitle(_translate("Dialog", "更新数据库", None))
        self.toolBox.setItemText(self.toolBox.indexOf(self.PG_Base), _translate("Dialog", "基本设置", None))
        self.groupBox_4.setTitle(_translate("Dialog", "扫描规则", None))
        self.groupBox_5.setTitle(_translate("Dialog", "GroupBox", None))
        self.toolBox.setItemText(self.toolBox.indexOf(self.PG_Advence), _translate("Dialog", "高级设置", None))
        self.PB_Confirm.setText(_translate("Dialog", "确  定", None))
        self.PB_Cancel.setText(_translate("Dialog", "取  消", None))
        self.PB_Apply.setToolTip(_translate("Dialog", " 应用更改", None))
        self.PB_Apply.setText(_translate("Dialog", "应  用", None))


if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    Dialog = QtGui.QDialog()
    ui = Ui_Dialog()
    ui.setupUi(Dialog)
    Dialog.show()
    sys.exit(app.exec_())

