from Realtime.Ui_realtime import Ui_Realtime
from PyQt5 import QtWidgets
import os
import cv2
from PyQt5.QtGui import QPixmap,QImage
from PyQt5.QtWidgets import QGraphicsScene, QGraphicsPixmapItem
from PyQt5.QtCore import QTimer 
import airsim
class MyRealtime(QtWidgets.QWidget,Ui_Realtime):
    def __init__(self,parent=None):
        super(MyRealtime,self).__init__(parent)
        self.setupUi(self)
        self.init_airsim()
        self.init_timer()
        
        
    def init_airsim(self): 
        self.client_camera = airsim.MultirotorClient()
        self.client_camera.confirmConnection()
        self.client_camera.enableApiControl(True)
        self.client_camera.armDisarm(True)
    
    def release_airsim(self):
        self.client_camera.reset()
        self.client_camera.armDisarm(False)
        self.client_camera.enableApiControl(False)
        self.graph_interval.stop()

    def start_takeImage(self):
        """
        start_takeImage : obtain the image catched by the five cameras attached with the multirotor
        """
        list=[]
        self.responses = self.client_camera.simGetImages([airsim.ImageRequest(0,airsim.ImageType.Scene),airsim.ImageRequest(1,airsim.ImageType.Scene),airsim.ImageRequest(2,airsim.ImageType.Scene),airsim.ImageRequest(3,airsim.ImageType.Scene),airsim.ImageRequest(4,airsim.ImageType.Scene)])
        for i in range(len(self.responses)):
                file_name="photo_"+str(i)+".png"
                list.append(file_name)
                airsim.write_file(file_name,self.responses[i].image_data_uint8)
        for i in range(len(list)):
            self.showGraphic(i,list[i])

    def init_timer(self):
        self.graph_interval=QTimer(self)
        self.graph_interval.timeout.connect(self.Time_Out)
        self.time_interval=40
        self.graph_interval.start(self.time_interval)
       
    
    def Time_Out(self):
        self.start_takeImage()
        for i in range(len(self.responses)):
            os.remove("photo_"+str(i)+".png")
  
    
    def showGraphic(self,name,filename):
        img=cv2.imread(filename)
        img=cv2.cvtColor(img,cv2.COLOR_BGR2RGB)
        x=img.shape[1]
        y=img.shape[0]
        ratio=float(y/x)
        newx=360
        newy=int(newx*ratio)
        img=cv2.resize(img,(newx,newy))
        frame=QImage(img,newx,newy,QImage.Format_RGB888)
        pix=QPixmap.fromImage(frame)
        item=QGraphicsPixmapItem(pix)
        scene=QGraphicsScene()
        scene.addItem(item)
        if name==0:
            self.front_left.setScene(scene)
            self.front_left.show()
        elif name==1:
            self.front_right.setScene(scene)
            self.front_right.show()
        elif name==2:
            self.front_center.setScene(scene)
            self.front_center.show()
        elif name==3:
            self.bottom_center.setScene(scene)
            self.bottom_center.show()
        else:
            self.back_center.setScene(scene)
            self.back_center.show()

    def closeEvent(self, event):
            reply = QtWidgets.QMessageBox.question(self,
                                                'Attention',
                                                "you do want to exit ?",
                                                QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No,
                                                QtWidgets.QMessageBox.No)
            if reply == QtWidgets.QMessageBox.Yes:
                event.accept()
                self.release_airsim()
                

            else:
                event.ignore()