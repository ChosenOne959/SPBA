from fileinput import close
from importlib.resources import path
import os
from wsgiref.validate import validator
from PyQt5.QtWidgets import QMainWindow, QMessageBox,QApplication
from PyQt5 import QtWidgets,QtCore,QtGui
from Setting_Path.Ui_Setting_path import Ui_MainWindow  
import re
from Work_Place.workWindow import MyworkWindow
import json

class MyMainWindow(QMainWindow,Ui_MainWindow): 
    def __init__(self,parent =None):
        super(MyMainWindow,self).__init__(parent)
        self.setupUi(self)
        self.set_myUI()
        
        

    def set_myUI(self):
        self.show()
        self.configurefile_path = './Setting_Path/configuration_file.json'
        self.path_data={'path':{}}
        self.UE4dir=''
        self.Matlab=''
        self.Airsim=''
        self.Vs=''
        self.set_path_file()
        self.pushButton.clicked.connect(lambda:self.open_app("UE4"))
        self.pushButton_2.clicked.connect(lambda:self.open_app("matlab"))
        self.pushButton_3.clicked.connect(lambda:self.open_app("vs"))
        self.toolButton.clicked.connect(self.open_file)
        self.pushButton_4.clicked.connect(self.showExitDialog)
        self.comboBox.currentIndexChanged.connect(self.lineEdit.clear)
        self.lineEdit.inputRejected.connect(lambda:showErrorDialog("path"))
        self.lineEdit.returnPressed.connect(self.comfirm_path)
        self.lineEdit.textEdited.connect(lambda:print("Editing"))
        self.actionworkplace.triggered.connect(self.showSubWin1)

    
    def set_path_file(self):
        if os.path.getsize(self.configurefile_path)==0:
            showErrorDialog("configure")
        else:
            with open(self.configurefile_path,'r') as cfile_path:
                self.path_data=json.load(cfile_path)
                try:
                    self.UE4dir=self.path_data['path']['UE4dir']
                except Exception as e:
                    print("UE3dir path has not been configured!")
                try:
                    self.Matlab=self.path_data['path']['Matlab']
                except Exception as e:
                    print("Matlab path has not been configured!")
                try:
                    self.Airsim=self.path_data['path']['Airsim']
                except Exception as e:
                    print("Airsim path has not been configured!")
                try:
                    self.Vs=self.path_data['path']['Vs']
                except Exception as e:
                    print("Vs path has not been configured!")
            
        
  
    def open_file(self):
        comboBox_name=self.comboBox.currentText()
        if comboBox_name=="Airsim":
            dpath=QtWidgets.QFileDialog.getExistingDirectory(self, "Open Folder", os.getcwd())
            dpath=dpath.replace('/','\\')
            self.lineEdit.setText(dpath)
        else:
            fpath=QtWidgets.QFileDialog.getOpenFileName(self,"Open file",os.getcwd(),'Exe files(*.exe)')
            fpath=str(fpath[0])
            fpath=fpath.replace('/','\\')
            self.lineEdit.setText(fpath)

    def showSubWin1(self):
        if self.Airsim=="":
            showErrorDialog("airsim")
            return
        self.mySubWin1 = MyworkWindow()
        self.mySubWin1.show() 

    def showExitDialog(self):
        msgBox = QMessageBox()
        msgBox.setIcon(QMessageBox.Question)
        msgBox.setText("Do you want to exit?")
        msgBox.setWindowTitle("Question")
        msgBox.setStandardButtons(QMessageBox.Yes|QMessageBox.No)
        return_value=msgBox.exec()
        msgBox.buttonClicked.connect(close)
        if return_value==QMessageBox.Yes:
            self.close()


    def comfirm_path(self):
        path=self.lineEdit.text()
        path=path.replace('\\','/')
        name=self.comboBox.currentText()
        if name == "Unreal":
            self.path_data['path']['UE4dir']=path
        elif name == "Matlab":
            self.path_data['path']['Matlab']=path
        elif name == "Airsim":
            self.path_data['path']['Airsim']=path
        else:
            self.path_data['path']['Vs']=path
        self.write_json_file()
        self.set_path_file()
        showSettingDialog("Setting completed!!!")
        
    
    def write_json_file(self):
            self.jsonfile=json.dumps(self.path_data,indent=4,separators=(',',':'))
            with open(self.configurefile_path,'w') as file:
                file.write(self.jsonfile)
            
    def open_app(self,name):
        print("start to launch the app")
        print("UE4:",self.UE4dir)
        if(name=='UE4'):
            try:
                if self.UE4dir!="":
                    os.startfile(self.UE4dir)
                    print("successed to open UE4")
                else:
                    self.showErrorDialog("start")
            except Exception as e:
                print("failed to open the UE4")
        if(name=='matlab'):
            try:
                if self.matlab!="":
                    os.startfile(self.Matlab)
                    print("successed to open matlab")
                else:
                    self.showErrorDialog("start")
            except Exception as e:
                print("failed to open the matlab")
        if(name=='vs'):
            try:
                if self.vs!="":
                    os.startfile(self.Vs)
                    print("successed to open vs")
                else:
                    self.showErrorDialog("start")
            except Exception as e:
                print("failed to open the vs")   

def showSettingDialog(message):
        msgBox = QMessageBox()
        msgBox.setIcon(QMessageBox.Information)
        msgBox.setText(message)
        msgBox.setWindowTitle("Message")
        msgBox.setStandardButtons(QMessageBox.Ok)
        msgBox.exec()
        msgBox.buttonClicked.connect(close)

def showWarningDialog():
    msgBox = QMessageBox()
    msgBox.setIcon(QMessageBox.Warning)
    msgBox.setText("path format error!")
    msgBox.setWindowTitle("Warning")
    msgBox.setStandardButtons(QMessageBox.Ok)
    msgBox.exec()
    msgBox.buttonClicked.connect(close)

def showErrorDialog(Dialog_type):
    msgBox = QMessageBox()
    msgBox.setIcon(QMessageBox.Critical)
    if Dialog_type=="path":
        msgBox.setText("Format Error,please check your path")
    if Dialog_type=="start":
        msgBox.setText("Failed to start the App,please check your path")
    if Dialog_type=="configure":
        msgBox.setText("The needed pathes have not been configured!")
    if Dialog_type=="airsim":
        msgBox.setText("Airsim path has not been configured!")
    msgBox.setWindowTitle("Error")
    msgBox.setStandardButtons(QMessageBox.Ok)
    msgBox.exec()
    msgBox.buttonClicked.connect(close)