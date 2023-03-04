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
        """
        set_myUI : set basic signal slots and initialize app path 
        """
        self.show()
        self.configurefile_path = './Setting_Path/configuration_file.json'
        self.path_data = {'path':{}}
        self.UE4dir = ''
        self.Matlab = ''
        self.Airsim = ''
        self.Recording = ''
        self.Setting = ''
        self.Vs = ''
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
        self.actionworkplace.triggered.connect(self.show_Work_window)
    
    def set_path_file(self):
        """
        set_path_file : read the configurefile and assign the corresponding value 
        """
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
                    self.Recording=self.path_data['path']['Recording store']
                except Exception as e:
                    print("Recording store path has not been configured!")
                try:
                    self.Vs=self.path_data['path']['Vs']
                except Exception as e:
                    print("Vs path has not been configured!")
            
        
  
    def open_file(self):
        """
        open_file : show the file selection window when the tool button is clicked 
                    when airsim comboBox is selected,the target will be restricted to folder
                    otherwise the target will be executable files
        """
        comboBox_name=self.comboBox.currentText()
        if comboBox_name=="Airsim" or comboBox_name == "Recording store":
            dpath=QtWidgets.QFileDialog.getExistingDirectory(self, "Open Folder", os.getcwd())
            dpath=dpath.replace('/','\\')
            self.lineEdit.setText(dpath)
        else:
            fpath=QtWidgets.QFileDialog.getOpenFileName(self,"Open file",os.getcwd(),'Exe files(*.exe)')
            fpath=str(fpath[0])
            fpath=fpath.replace('/','\\')
            self.lineEdit.setText(fpath)

    def show_Work_window(self):
        """
        show_Work_window : 
        show Work window when "workplace" is stimulated if airsim' path haven't been set,show the error
        """
        if self.Airsim=="":
            showErrorDialog("airsim")
            return
        self.workWindow = MyworkWindow()
        self.workWindow.show() 

    def showExitDialog(self):
        """
        showExitDialog : showExitDialog show the question dialog when the "exit" button is clicked
        """
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
        """
        comfirm_path : read the uses's setting contain by lineEdit component
        """
        path=self.lineEdit.text()
        path=path.replace('\\','/')
        name=self.comboBox.currentText()
        if name == "Unreal":
            self.path_data['path']['UE4dir']=path
        elif name == "Matlab":
            self.path_data['path']['Matlab']=path
        elif name == "Airsim":
            self.path_data['path']['Airsim']=path
        elif name == "Recording store":
            self.path_data['path']['Recording store']=path
        else:
            self.path_data['path']['Vs']=path
        self.write_json_file()
        self.set_path_file()
        showSettingDialog("Setting completed!!!")
        
    
    def write_json_file(self):
        """
        write_json_file : modify the configuration file according to user's setting
        """
        self.jsonfile=json.dumps(self.path_data,indent=4,separators=(',',':'))
        with open(self.configurefile_path,'w') as file:
            file.write(self.jsonfile)
            
    def open_app(self,name):
        """
        open_app : start the corresponding app when the button is clicked

        Args:
            name: app name
        """
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

    def closeEvent(self, event):
        """
        closeEvent : override the close function so that the question dialog after the close Icon was clicked

        Args:
            event: default param
        """
        reply = QtWidgets.QMessageBox.question(self,
                                               'Attention',
                                               "you do want to exit ?",
                                               QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No,
                                               QtWidgets.QMessageBox.No)
        if reply == QtWidgets.QMessageBox.Yes:
            event.accept()

        else:
            event.ignore() 

def showSettingDialog(message):
    """
    showSettingDialog : show setting dialog when the setting is done

    Args:
        message: what you want to deliver to user 
    """
    
    msgBox = QMessageBox()
    msgBox.setIcon(QMessageBox.Information)
    msgBox.setText(message)
    msgBox.setWindowTitle("Message")
    msgBox.setStandardButtons(QMessageBox.Ok)
    msgBox.exec()
    msgBox.buttonClicked.connect(close)

def showWarningDialog():
    """
    showWarningDialog : show warning dialog when the path format dosen't match the regular expression
    """
    msgBox = QMessageBox()
    msgBox.setIcon(QMessageBox.Warning)
    msgBox.setText("path format error!")
    msgBox.setWindowTitle("Warning")
    msgBox.setStandardButtons(QMessageBox.Ok)
    msgBox.exec()
    msgBox.buttonClicked.connect(close)

def showErrorDialog(Dialog_type):
    """
    showErrorDialog : show error dialog

    Args:
        Dialog_type: dialog type
    """
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


