import symbol
from turtle import color, pensize, width
from Ui_Data_display import Ui_Display_Win
from Ui_Data_display import Ui_Display_Win
from PyQt5.QtWidgets import QApplication,QGraphicsView, QGraphicsScene, QGraphicsPixmapItem
from PyQt5 import QtWidgets,QtCore
from PyQt5.QtGui import QPixmap,QImage
from PyQt5.QtCore import QTimer
from pyqtgraph import PlotWidget
import pandas as pd
import numpy as np
import cv2
import os
class MyDisplayWindow(QtWidgets.QWidget,Ui_Display_Win): 
    def __init__(self,parent=None):
        super(MyDisplayWindow,self).__init__(parent)
        self.setupUi(self)
        self.timeCount=0
        self.countSum=0
        self.Image_Data_Name=""
        new_file=self.Latest_File()
        self.Image_path=new_file+'/images/'  
        self.Data_path=new_file+'/airsim_rec.txt'  
        self.init_timer()

    def init_timer(self):
        self.graph_interval=QTimer(self)
        self.graph_interval.timeout.connect(self.Time_Out)
        self.time_interval=100
        self.init_Image_Display()
        self.init_Position_Display()
        self.init_Sensor_Display()
        self.init_Acceleration_Dispaly()
        self.graph_interval.start(self.time_interval)
        
    def init_Position_Display(self):
        self.Pos_X=self.Data_split("POS_X")
        self.X=[]
        self.X_x=[]
        self.Pos_Y=self.Data_split("POS_Y")
        self.Y=[]
        self.Y_x=[]
        self.Pos_Z=self.Data_split("POS_Z")
        self.Z=[]
        self.Z_x=[]
    
    def init_Image_Display(self):
        self.Image_Data_Name=self.Data_split("ImageFile")
        self.name1=self.Image_Name_Split()
        self.countSum=len(self.Image_Data_Name)
        self.xaxis=np.linspace(1,self.countSum,self.countSum)*100
    
    def init_Sensor_Display(self):
        self.La=self.Data_split("Latitude")
        self.Lo=self.Data_split("Longitude")
        self.Al=self.Data_split("Altitude")
        self.Pr=self.Data_split("Pressure")
        self.La_temp=[]
        self.Lo_temp=[]
        self.Al_temp=[]
        self.Pr_temp=[]
    
    def init_Acceleration_Dispaly(self):
        self.acc_x=self.Data_split("AccX")
        self.acc_y=self.Data_split("AccY")
        self.acc_z=self.Data_split("AccZ")
        self.acc_x_temp=[]
        self.acc_y_temp=[]
        self.acc_z_temp=[]

    def Time_Out(self):
        if self.timeCount<self.countSum:
            self.Position_Display_Clear()
            self.Sensor_Display_Clear()
            self.Acceleration_Display_Clear()
            Scene_path=self.Image_path+str(self.name1[0][self.timeCount])
            Depth_path=self.Image_path+str(self.name1[1][self.timeCount])
            Segment_path=self.Image_path+str(self.name1[2][self.timeCount])
            self.X.append(float(self.Pos_X[self.timeCount]))
            self.X_x.append(float(self.xaxis[self.timeCount]))
            self.Y.append(float(self.Pos_Y[self.timeCount]))
            self.Z.append(float(self.Pos_Z[self.timeCount]))
            self.La_temp.append(float(self.La[self.timeCount]))
            self.Lo_temp.append(float(self.Lo[self.timeCount]))
            self.Al_temp.append(float(self.Al[self.timeCount]))
            self.Pr_temp.append(float(self.Pr[self.timeCount]))
            self.acc_x_temp.append(float(self.acc_x[self.timeCount]))
            self.acc_y_temp.append(float(self.acc_y[self.timeCount]))
            self.acc_z_temp.append(float(self.acc_z[self.timeCount]))
            self.timeCount=self.timeCount+1
            self.showGraphic(Scene_path,"Scene")
            self.showGraphic(Depth_path,"Depth")
            self.showGraphic(Segment_path,"Segment")
            self.Position_Display(self.X,self.Y,self.Z,self.X_x)
            self.Sensor_Display(Latitude=self.La_temp,Longitude=self.Lo_temp,Altitude=self.Al_temp,Pressure=self.Pr_temp,axis=self.X_x)
            self.Acceleration_Display(self.acc_x_temp,self.acc_y_temp,self.acc_z_temp,self.X_x)
            
        else:
            self.graph_interval.stop()
    
    def Latest_File(self):
        path="C:/Users/asus/Documents/AirSim/"
        lists=os.listdir(path)
        lists.sort(key=lambda x:os.path.getmtime((path+"\\"+x)))
        if lists[-1]=="settings.json":
            file_new = os.path.join(path, lists[-2])
        else:
            file_new = os.path.join(path, lists[-1])
        return file_new


    def Data_split(self,dataname):
        data=pd.read_csv(self.Data_path,sep='\t',header=None)
        for i in range(len(data.iloc[0,:])):
            if data[i][0] == dataname:
                return np.array(data.iloc[1:,i])
    
    def Image_Name_Split(self):
        name1=[]
        name2=[]
        name3=[]
        for name in self.Image_Data_Name:
            name_str=str(name)
            name_str=name_str.split(';')
            name1.append(name_str[0])
            name2.append(name_str[1])
            name3.append(name_str[2])
        return name1,name2,name3
    
    def showGraphic(self,path,type):
        img=cv2.imread(path)
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
        if type=='Scene':
            self.Scene_view.setScene(scene)
            self.Scene_view.show()
        elif type=='Depth':
            self.Depth_view.setScene(scene)
            self.Depth_view.show()
        else:
            self.Segment_view.setScene(scene)
            self.Segment_view.show()
    
    def Position_Display(self,X,Y,Z,axis):
        self.Position.addLegend()
        self.Position.plot(axis,X,pen=(1,3),name="POS_X")
        self.Position.plot(axis,Y,pen=(2,3),name="POS_Y")
        self.Position.plot(axis,Z,pen=(3,3),name="POS_Z")
        #self.Position.setBackground('w')
        self.Position.setLabel('bottom',"time/ms")
        self.Position.setLabel('left',"Position")
    def Position_Display_Clear(self):
        self.Position.clear()

    def Sensor_Display(self,Latitude=None,Longitude=None,Altitude=None,Pressure=None,axis=None):
        try:
            if axis!=None:
                if Latitude!=None:
                    self.Latitude.addLegend()
                    self.Latitude.plot(axis,Latitude,name='Latitude',pen='#9400D3')
                    self.Latitude.setLabel('left','Latitude')
                    self.Latitude.setLabel('bottom','time/ms')
                if Longitude!=None:
                    self.Longitutde.addLegend()
                    self.Longitutde.plot(axis,Longitude,name='Longitude',pen='#CD5555')
                    self.Longitutde.setLabel('left','Longitude')
                    self.Longitutde.setLabel('bottom','time/ms')
                if Altitude!=None:
                    self.Altitude.addLegend()
                    self.Altitude.plot(axis,Altitude,name='Altitude',pen='#20B2AA')
                    self.Altitude.setLabel('left','Altitude')
                    self.Altitude.setLabel('bottom','time/ms')
                if Pressure!=None:
                    self.Pressure.addLegend()
                    self.Pressure.plot(axis,Pressure,name='Pressure',pen='#FFD700')
                    self.Pressure.setLabel('left','Pressure')
                    self.Pressure.setLabel('bottom','time/ms')
        except Exception as e:
            print("error:",e)

    def Sensor_Display_Clear(self):
        self.Latitude.clear()
        self.Longitutde.clear()
        self.Altitude.clear()
        self.Pressure.clear()
        
    def Acceleration_Display(self,acx,acy,acz,axis):
        self.acceleration.addLegend()
        self.acceleration.plot(axis,acx,pen=(1,3),name="Acc_X")
        self.acceleration.plot(axis,acy,pen=(2,3),name="Acc_Y")
        self.acceleration.plot(axis,acz,pen=(3,3),name="Acc_Z")
        #self.Position.setBackground('w')
        self.acceleration.setLabel('bottom',"time/ms")
        self.acceleration.setLabel('left',"Acceleration")
    
    def Acceleration_Display_Clear(self):
        self.acceleration.clear()
        

