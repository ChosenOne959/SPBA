from fileinput import close
import os
from PyQt5.QtWidgets import QMainWindow, QMessageBox
from PyQt5 import QtWidgets
from new_ui.login.Ui_Login import Ui_login
from new_ui.settings.SettingWindow import SettingWindow
import json
from SPBA_API import SharedData

class LoginWindow(QMainWindow, Ui_login):
    def __init__(self, parent=None):
        super(LoginWindow, self).__init__(parent)
        self.SharedData = SharedData()
        self.SharedData.append_window(self)
        self.setupUi(self)
        self.set_myUI()

    def set_myUI(self):
        """
        set_myUI : set basic signal slots and initialize app path
        """
        self.show()
        self.set_localhost(False)
        self.remote_button.setChecked(True)

        self.read_configuration_file()

        self.path_button.clicked.connect(self.open_file)
        self.software_choose.currentIndexChanged.connect(self.path_edit.clear)
        self.path_edit.inputRejected.connect(lambda: showErrorDialog("path"))
        self.path_edit.returnPressed.connect(self.comfirm_path)
        self.path_edit.textEdited.connect(lambda: print("Editing"))
        self.local_button.clicked.connect(lambda: self.set_localhost(True))
        self.remote_button.clicked.connect(lambda: self.set_localhost(False))
        self.login_button.clicked.connect(lambda: self.login())

    def set_localhost(self, flag):
        self.SharedData.is_localhost = flag
        if flag:
            self.username_edit.setEnabled(False)
            self.password_edit.setEnabled(False)
            self.remeber_password_checkbox.setEnabled(False)
            self.path_edit.setEnabled(True)
            self.path_button.setEnabled(True)
            self.software_choose.setEnabled(True)
        else:
            self.username_edit.setEnabled(True)
            self.password_edit.setEnabled(True)
            self.remeber_password_checkbox.setEnabled(True)
            self.path_edit.setEnabled(False)
            self.path_button.setEnabled(False)
            self.software_choose.setEnabled(False)


    def read_configuration_file(self):
        """
        set_path_file : read the configurefile and assign the corresponding value
        """
        if os.path.getsize(self.SharedData.configurefile_path) == 0:
            showErrorDialog("configure")
        else:
            with open(self.SharedData.configurefile_path, 'r') as cfile_path:
                self.SharedData.configure_data = json.load(cfile_path)
                if 'path' not in self.SharedData.configure_data:
                    self.SharedData.configure_data['path'] = {}

    def open_file(self):
        """
        open_file : show the file selection window when the tool button is clicked
                    when airsim comboBox is selected,the target will be restricted to folder
                    otherwise the target will be executable files
        """
        comboBox_name = self.software_choose.currentText()
        if comboBox_name == "Airsim":
            dpath = QtWidgets.QFileDialog.getExistingDirectory(self, "Open Folder", os.getcwd())
            dpath = dpath.replace('/', '\\')
            self.path_edit.setText(dpath)
        elif comboBox_name == "AirSimSettings":
            fpath = QtWidgets.QFileDialog.getOpenFileName(self, "Open file", os.getcwd(), 'Json files(*.json)')
            fpath = str(fpath[0])
            fpath = fpath.replace('/', '\\')
            self.path_edit.setText(fpath)
        else:
            fpath = QtWidgets.QFileDialog.getOpenFileName(self, "Open file", os.getcwd(), 'Exe files(*.exe)')
            fpath = str(fpath[0])
            fpath = fpath.replace('/', '\\')
            self.path_edit.setText(fpath)

    # check path/password and go to next window
    def login(self):
        if self.SharedData.is_localhost:
            if not self.check_path_is_set():
                return
            self.write_configuration_file()
        self.show_SettingWindow()

    def check_path_is_set(self):
        if 'UE4dir' not in self.SharedData.configure_data['path']:
            showErrorDialog("UE4dir")
        elif 'Airsim' not in self.SharedData.configure_data['path']:
            showErrorDialog("Airsim")
        elif 'AirSimSettings' not in self.SharedData.configure_data['path']:
            showErrorDialog("AirSimSettings")
        elif self.SharedData.configure_data['path']['UE4dir'] == "":
            showErrorDialog("UE4dir")
        elif self.SharedData.configure_data['path']['Airsim'] == "":
            showErrorDialog("Airsim")
        elif self.SharedData.configure_data['path']['AirSimSettings'] == "":
            showErrorDialog("AirSimSettings")
        else:
            return True
        return False

    def show_SettingWindow(self):
        settingWindow = SettingWindow(self.SharedData)
        self.SharedData.append_window(settingWindow)
        settingWindow.show()
        self.destroy()

    # def showExitDialog(self):
    #     """
    #     showExitDialog : showExitDialog show the question dialog when the "exit" button is clicked
    #     """
    #     msgBox = QMessageBox()
    #     msgBox.setIcon(QMessageBox.Question)
    #     msgBox.setText("Do you want to exit?")
    #     msgBox.setWindowTitle("Question")
    #     msgBox.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
    #     return_value = msgBox.exec()
    #     msgBox.buttonClicked.connect(close)
    #     if return_value == QMessageBox.Yes:
    #         self.close()

    def comfirm_path(self):
        """
        comfirm_path : read the uses's setting contain by lineEdit component
        """
        path = self.path_edit.text()
        path = path.replace('\\', '/')
        name = self.software_choose.currentText()
        if name == "Unreal":
            self.SharedData.configure_data['path']['UE4dir'] = path
        elif name == "Airsim":
            self.SharedData.configure_data['path']['Airsim'] = path
            self.SharedData.configure_data['path']['Rotor_params'] = path + "/AirLib/include/vehicles/multirotor/RotorParams.hpp"
            # some other paths
        elif name == "AirSimSettings":
            self.SharedData.configure_data['path']['AirSimSettings'] = path
        showSettingDialog("Setting completed!!!")

    def write_configuration_file(self):
        """
        write_json_file : modify the configuration file according to user's setting
        """
        jsonfile = json.dumps(self.SharedData.configure_data, indent=4, separators=(',', ':'))
        with open(self.SharedData.configurefile_path, 'w') as file:
            file.write(jsonfile)


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
    if Dialog_type == "path":
        msgBox.setText("Format Error,please check your path")
    if Dialog_type == "start":
        msgBox.setText("Failed to start the App,please check your path")
    if Dialog_type == "configure":
        msgBox.setText("The needed pathes have not been configured!")
    if Dialog_type == "Airsim":
        msgBox.setText("Airsim path has not been configured!")
    if Dialog_type == "UE4dir":
        msgBox.setText("UE4dir path has not been configured!")
    if Dialog_type == "AirSimSettings":
        msgBox.setText("AirSimSettings path has not been configured!")
    msgBox.setWindowTitle("Error")
    msgBox.setStandardButtons(QMessageBox.Ok)
    msgBox.exec()
    msgBox.buttonClicked.connect(close)


