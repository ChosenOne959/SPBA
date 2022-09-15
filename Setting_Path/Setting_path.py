from fileinput import close
from importlib.resources import path
import sys
import os
from wsgiref.validate import validator
from PyQt5.QtWidgets import QMainWindow, QMessageBox,QApplication
from PyQt5 import QtWidgets,QtCore,QtGui
from Ui_Setting_path import Ui_MainWindow  #导入你写的界面类
import re
from workWindow import MyworkWindow

class MyMainWindow(QMainWindow,Ui_MainWindow): #这里也要记得改
    def __init__(self,parent =None):
        super(MyMainWindow,self).__init__(parent)
        self.setupUi(self)
        self.set_myUI()
        self.mySubWin1 = MyworkWindow()
        self.UE4dir=""
        self.matlab=""
        self.vs=""
        

    def set_myUI(self):
        print("start")
        self.show()
        self.pushButton.clicked.connect(lambda:self.open_app("UE4"))
        self.pushButton_2.clicked.connect(lambda:self.open_app("matlab"))
        self.pushButton_3.clicked.connect(lambda:self.open_app("vs"))
        self.toolButton.clicked.connect(self.open_file)
        self.pushButton_4.clicked.connect(self.showExitDialog)
        self.comboBox.currentIndexChanged.connect(self.lineEdit.clear)
        self.lineEdit.inputRejected.connect(self.showErrorDialog)
        self.actionworkplace.triggered.connect(self.showSubWin1)

    def open_file(self):
        QtWidgets.QFileDialog.getExistingDirectory(self, "选取文件夹", os.getcwd())
        dpath=os.getcwd()
        self.lineEdit.setText(dpath)
    
    def showSubWin1(self):
        #self.hide()
        self.mySubWin1.show() 

    def showSettingDialog(self):
        msgBox = QMessageBox()
        msgBox.setIcon(QMessageBox.Information)
        msgBox.setText("Setting completed!!!")
        msgBox.setWindowTitle("Message")
        msgBox.setStandardButtons(QMessageBox.Ok)
        msgBox.exec()
        msgBox.buttonClicked.connect(close)

    def showWarningDialog(self):
        msgBox = QMessageBox()
        msgBox.setIcon(QMessageBox.Warning)
        msgBox.setText("path format error!")
        msgBox.setWindowTitle("Warning")
        msgBox.setStandardButtons(QMessageBox.Ok)
        msgBox.exec()
        msgBox.buttonClicked.connect(close)
    
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
    
    def showErrorDialog(self):
        msgBox = QMessageBox()
        msgBox.setIcon(QMessageBox.Critical)
        msgBox.setText("Format Error,please check your path")
        msgBox.setWindowTitle("Error")
        msgBox.setStandardButtons(QMessageBox.Ok)
        msgBox.exec()
        msgBox.buttonClicked.connect(close)
        
    def comfirm_path(self):
        path=self.lineEdit.text()
        name=self.comboBox.currentText()
        if name == "Unreal":
            self.UE4dir=path
        elif name == "Matalb":
            self.matalb=path
        else:
            self.vs=path
        self.showSettingDialog()
        

    def pushButton_print(self):

        print("test successful!!")

    def open_app(self,name):
        print("start to launch the app")
        print("UE4:",self.UE4dir)
        if(name=='UE4'):
            try:
                os.startfile(self.UE4dir)
                print("successed to open UE4")
            except Exception as e:
                print("failed to open the UE4")
        if(name=='matlab'):
            try:
                os.startfile(self.matlab)
                print("successed to open matlab")
            except Exception as e:
                print("failed to open the matlab")
        if(name=='vs'):
            try:
                os.startfile(self.vs)
                print("successed to open vs")
            except Exception as e:
                print("failed to open the vs")       