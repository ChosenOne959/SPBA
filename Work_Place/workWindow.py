from hashlib import new
from Ui_workplace import Ui_Form
import sys
from PyQt5.QtWidgets import QApplication,QGraphicsView, QGraphicsScene, QGraphicsPixmapItem
from PyQt5 import QtWidgets
from PyQt5.QtGui import QPixmap,QImage
import cv2
class MyworkWindow(QtWidgets.QWidget,Ui_Form): #这里也要记得改
    def __init__(self,parent=None):
        super(MyworkWindow,self).__init__(parent)
        self.setupUi(self)
        self.set_myUI()
        self.showGraphic()
    
    def showGraphic(self):
        path='C:/Users/asus/Desktop/unreal.jpg'
        img=cv2.imread(path)
        img=cv2.cvtColor(img,cv2.COLOR_BGR2RGB)
        x=img.shape[1]
        y=img.shape[0]
        ratio=float(y/x)
        newx=180
        newy=int(newx*ratio)
        img=cv2.resize(img,(newx,newy))
        frame=QImage(img,newx,newy,QImage.Format_RGB888)
        pix=QPixmap.fromImage(frame)
        self.item=QGraphicsPixmapItem(pix)
        self.scene=QGraphicsScene()
        self.scene.addItem(self.item)
        self.DroneModel.setScene(self.scene)
        self.DroneModel.show()




    def set_myUI(self):
        print("start")
        self.commandLinkButton.clicked.connect(self.close)

    def mainWindow(self):
        self.close()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    myWin = MyworkWindow()
    myWin.show()
    sys.exit(app.exec_())    