<<<<<<< HEAD
import subprocess
from Ui_workplace import Ui_Work_Win
import sys
from PyQt5.QtWidgets import QApplication,QGraphicsView, QGraphicsScene, QGraphicsPixmapItem
from PyQt5 import QtWidgets,QtCore
from PyQt5.QtGui import QPixmap,QImage
from PyQt5.QtCore import QTimer
import cv2
import os
import time
import pandas as pd
import numpy as np
import re
from Data_display import MyDisplayWindow
class MyworkWindow(QtWidgets.QWidget,Ui_Work_Win): 
    def __init__(self,parent=None):
        super(MyworkWindow,self).__init__(parent)
        self.setupUi(self)
        self.Rotor_params_path="D:/Airsim/AirSim/AirLib/include/vehicles/multirotor/RotorParams.hpp"
        self.set_myUI()
        self.init_Rotor_params()
        self.init_Body_params()
        self.init_kineatic()
        

    def set_myUI(self):
        self.commandLinkButton.clicked.connect(self.close)
        self.pushButton.clicked.connect(self.runCode)
        self.pushButton_2.clicked.connect(self.textBrowser.clear)
        self.pushButton_3.clicked.connect(self.Show_Display_Window)
        self.Thrust_SpinBox.valueChanged.connect(lambda:self.alter("Thrust"))
        self.Torque_SpinBox.valueChanged.connect(lambda:self.alter("Torque"))
        self.Air_SpinBox.valueChanged.connect(lambda:self.alter("Air"))
        self.Revolutions_SpinBox.valueChanged.connect(lambda:self.alter("Revolutions"))
        self.Diameter_SpinBox.valueChanged.connect(lambda:self.alter("Diameter"))
        self.Height_SpinBox.valueChanged.connect(lambda:self.alter("Height"))
        self.MaxThrust_SpinBox.valueChanged.connect(lambda:self.alter("MaxThrust"))
        self.MaxTorque_SpinBox.valueChanged.connect(lambda:self.alter("MaxTorque"))
        
    def init_Rotor_params(self):
        with open(self.Rotor_params_path,"r+") as file:
            for line in file:
                Thrust_str="".join(re.findall(r'real_T C_T = (.*?)f',line))
                Torque_str="".join(re.findall(r'real_T C_P = (.*?)f',line))
                Air_str="".join(re.findall(r'real_T air_density = (.*?)f',line))
                Revolutions_str="".join(re.findall(r'real_T max_rpm = (.*?)f',line))
                Diameter_str="".join(re.findall(r'real_T propeller_diameter = (.*?)f',line))
                Height_str="".join(re.findall(r'real_T propeller_height = (.*?)f',line))
                MaxThrust_str="".join(re.findall(r'real_T max_thrust = (.*?)f',line))
                MaxTorque_str="".join(re.findall(r'real_T torque = (.*?)f',line))
                if Thrust_str!="":
                    self.Thrust_old_str="real_T C_T = "+Thrust_str
                    self.Thrust_SpinBox.setProperty("value", float(Thrust_str))
                if Torque_str!="":
                    self.Torque_old_str="real_T C_P = "+Torque_str
                    self.Torque_SpinBox.setProperty("value", float(Torque_str))
                if Air_str!="":
                    self.Air_old_str="real_T air_density = "+Air_str
                    self.Air_SpinBox.setProperty("value", float(Air_str))
                if Revolutions_str!="":
                    self.Revolutions_old_str="real_T max_rpm = "+Revolutions_str
                    self.Revolutions_SpinBox.setProperty("value", float(Revolutions_str))
                if Diameter_str!="":
                    self.Diameter_old_str="real_T propeller_diameter = "+Diameter_str
                    self.Diameter_SpinBox.setProperty("value", float(Diameter_str))
                if Height_str!="":
                    self.Height_old_str="real_T propeller_height = "+Height_str
                    self.Height_SpinBox.setProperty("value",float(Height_str))
                if MaxThrust_str!="":
                    self.MaxThrust_old_str="real_T max_thrust = "+MaxThrust_str
                    self.MaxThrust_SpinBox.setProperty("value",float(MaxThrust_str))
                if MaxTorque_str!="":
                    self.MaxTorque_old_str="real_T torque = "+MaxTorque_str
                    self.MaxTorque_SpinBox.setProperty("value",float(MaxTorque_str))

    def init_Body_params(self):
        body=None
    
    def init_kineatic(self):
        kineatic=None
    
    def Show_Display_Window(self):
        self.Display_Win=MyDisplayWindow()
        self.Display_Win.show()
    

    def showGraphic(self,path):
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

    def runCode(self):
        run_time=time.localtime()
        run_date="<"+str(run_time.tm_year)+"/"+str(run_time.tm_mon)+"/"+str(run_time.tm_mday)+">"
        run_clock=str(run_time.tm_hour)+":"+str(run_time.tm_min).rjust(2,'0')
        self.textBrowser.append(run_date)
        self.textBrowser.append(run_clock)
        flag=0
        code=self.textEdit.toPlainText()
        file_path="D:/Uav_hardware_in_the_loop_simulation_platform/qtProect/codefile.py "
        with open(file_path,'w+') as codefile:
            codefile.write(code)
        try:
            subprocess.check_call("python codefile.py 2>error.txt ",shell=True)
        except Exception as e:
            flag=1
            with open("error.txt",'r') as mes:
                for i in mes:
                    self.textBrowser.append(i) 
        if flag==1:
            flag=0
        else:
            self.textBrowser.append("compiled successfully!!")
            self.pushButton_3.setEnabled(True)

        os.remove("error.txt")
        os.remove("codefile.py")

    def alter(self,name):
        init_flag=0
        if self.tabWidget.currentIndex()==0:
            file="D:/Airsim/AirSim/AirLib/include/vehicles/multirotor/RotorParams.hpp"
        if self.tabWidget.currentIndex()==1:
            file="D:/Airsim/AirSim/AirLib/include/vehicles/multirotor/RotorParams.hpp"
            init_flag=1
        if self.tabWidget.currentIndex()==2:
            file="D:/Airsim/AirSim/AirLib/include/vehicles/multirotor/RotorParams.hpp"
            init_flag=2
        
        if name == "Thrust":
            new_str="real_T C_T = "+str(self.Thrust_SpinBox.value())
            old_str=self.Thrust_old_str
        if name == "Torque":
            new_str="real_T C_P = "+str(self.Torque_SpinBox.value())
            old_str=self.Torque_old_str
        if name == "Air":
            new_str="real_T air_density = "+str(self.Air_SpinBox.value())
            old_str=self.Air_old_str
        if name == "Revolutions":
            new_str="real_T max_rpm = "+str(self.Revolutions_SpinBox.value())
            old_str=self.Revolutions_old_str
        if name == "Diameter":
            new_str="real_T propeller_diameter = "+str(self.Diameter_SpinBox.value())
            old_str=self.Diameter_old_str
        if name == "Height":
            new_str="real_T propeller_height = "+str(self.Height_SpinBox.value())
            old_str=self.Height_old_str
        if name == "MaxThrust":
            new_str="real_T max_thrust = "+str(self.MaxThrust_SpinBox.value())
            old_str=self.MaxThrust_old_str
        if name == "MaxTorque":
            new_str="real_T torque = "+str(self.MaxTorque_SpinBox.value())
            old_str=self.MaxTorque_old_str
        with open(file, "r+", encoding="utf-8") as f1:
            lines=[]
            for line in f1:
                if old_str in line:
                    line = line.replace(old_str, new_str)
                lines.append(line)
        
        with open(file, "w+", encoding="utf-8") as f1:
            for line in lines:
                f1.write(line)

        if init_flag==0:
            self.init_Rotor_params()
        elif init_flag==1:
            self.init_Body_params()
        else:
            self.init_kineatic()

    def mainWindow(self):
        self.close()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    myWin = MyworkWindow()
    myWin.show()
=======
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
>>>>>>> 42db3926bd934d42ba8ee1511fbce63ae75061af
    sys.exit(app.exec_())    