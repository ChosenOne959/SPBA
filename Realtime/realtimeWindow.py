from Realtime.Ui_realtime import Ui_Realtime
from PyQt5 import QtWidgets
import os
import cv2
from PyQt5.QtGui import QPixmap,QImage
from PyQt5.QtWidgets import QGraphicsScene, QGraphicsPixmapItem
from PyQt5.QtCore import QTimer 
import airsim
import SPBA_API as SPBA

class MyRealtime(QtWidgets.QWidget,Ui_Realtime):
    def __init__(self,parent=None):
        super(MyRealtime,self).__init__(parent)
        self.setupUi(self)
        self.init_airsim()
        self.init_timer()
        
        
    def init_airsim(self): 
        self.client_camera = SPBA.Multirotor()

    def release_airsim(self):
        del self.client_camera
        self.graph_interval.stop()

    def start_takeImage(self):
        """
        start_takeImage : obtain the image catched by the five cameras attached with the multirotor
        """
        list = self.client_camera.GroundTruth.CameraImages
        for i in range(len(list)):
            self.showGraphic(i,list[i])

    def init_timer(self):
        self.graph_interval=QTimer(self)
        self.graph_interval.timeout.connect(self.Time_Out)
        self.time_interval=40
        self.graph_interval.start(self.time_interval)
       
    
    def Time_Out(self):
        self.start_takeImage()
  
    
    def showGraphic(self,name,img):
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