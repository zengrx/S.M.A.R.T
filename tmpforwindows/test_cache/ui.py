from PyQt4.QtGui  import *  
from PyQt4.QtCore import *    
class MyDialog(QDialog):  
    def __init__(self, parent=None):  
        super(MyDialog, self).__init__(parent)  
        self.MyTable = QTableWidget(4,3)  
        self.MyTable.setHorizontalHeaderLabels(['test','test','test'])  
          
        newItem = QTableWidgetItem("aaa")  
        self.MyTable.setItem(0, 0, newItem)  
          
        newItem = QTableWidgetItem("10cm")  
        self.MyTable.setItem(0, 1, newItem)  
          
        newItem = QTableWidgetItem("60g")  
        self.MyTable.setItem(0, 2, newItem)   
        
        layout = QHBoxLayout()  
        layout.addWidget(self.MyTable)  
        self.setLayout(layout)      
          
          
if __name__ == '__main__':  
    import sys  
    app = QApplication(sys.argv)  
    myWindow = MyDialog()  
    myWindow.show()  
    sys.exit(app.exec_())   