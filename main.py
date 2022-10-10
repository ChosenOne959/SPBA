from Setting_Path.Setting_path import MyMainWindow
import sys
from PyQt5.QtWidgets import QApplication    
if __name__ == "__main__":
    app = QApplication(sys.argv)
    myWin = MyMainWindow()
    myWin.show()
    sys.exit(app.exec_())    