#coding=utf-8

from PyQt4 import QtGui, QtCore
from SSMA_UI import Ui_MainWindow
import sys, os
import argparse
import magic
import shutil

sys.path.append("../ssma_python2")
from src import colors
from src.blacklisted_domain_ip import ransomware_and_malware_domain_check
from src.check import is_malware, is_file_packed, check_crypto, is_antidb_antivm, is_malicious_document
from src.check_file import PEScanner, file_info
from src.check_updates import check_internet_connection, download_yara_rules_git
from src.check_virustotal import virustotal
from src.file_strings import get_strings

class MainWindow(QtGui.QMainWindow):
    def __init__(self, parent=None):
        QtGui.QWidget.__init__(self, parent)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        QtCore.QObject.connect(self.ui.pushButton, QtCore.SIGNAL("clicked()"), self.testFunc)

    def testFunc(self):
        #filename = QtGui.QFileDialog.getExistingDirectory(self, "sf", QtCore.QDir.currentPath()) #for path select
        filename = QtGui.QFileDialog.getOpenFileName(self, "select file", "./", "All Files (*)") #for file select
        filename = str(filename)
        self.ui.lineEdit.setText(filename)
        self.showMessage(filename, False)
        #filename = os.path.realpath(filename)
        filetype = magic.from_file(filename, mime=True)
        self.showMessage(filetype, False)

    def showMessage(self, msg, showtime = True):
        self.ui.textEdit.append(msg)

if __name__ == "__main__":

    
    app = QtGui.QApplication(sys.argv)
    myapp = MainWindow()
    
    myapp.show()
    
    #check internet
    internet_connection = check_internet_connection()

    sys.exit(app.exec_())
