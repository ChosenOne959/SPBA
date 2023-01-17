import subprocess
from Work_Place.Ui_workplace import Ui_Work_Win
import sys
from PyQt5.QtWidgets import QApplication, QGraphicsView, QMessageBox, QGraphicsScene, QGraphicsPixmapItem
from PyQt5 import QtWidgets, QtCore
from PyQt5.QtGui import QPixmap, QImage
from PyQt5.QtCore import QTimer
import cv2
import os
import time
import pandas as pd
import numpy as np
import re
import json
import threading
from Work_Place.keyboard_controler import keyboard_control
from new_ui.settings.Ui_Setting_Window import Ui_SettingWindow
from SPBA_API import SettingClient
from PyQt5.QtWidgets import QMainWindow, QMessageBox
from new_ui.show_data.DataWindow import DataWindow
from new_ui.controller.ControlWindow import ControlWindow


class SettingWindow(QMainWindow, Ui_SettingWindow):
    def __init__(self, SharedData, parent=None):
        self.SharedData = SharedData
        super(SettingWindow, self).__init__(parent)
        self.setupUi(self)
        self.set_myUI()

        self.SettingClient = SettingClient(self.SharedData)
        self.AirSimSettings = self.SettingClient.AirSimSettings
        self.AirSimParameters = self.SettingClient.AirSimParameters
        self.RPC_client = self.SharedData.resources['RPC_client']
        self.airsim_settings_config()

        self.param_data = SharedData.param_data
        self.show_params()


    def set_myUI(self):
        """
        set_myUI : set basic signal slots
        """
        self.backButton.clicked.connect(self.back)
        self.fowardButton.clicked.connect(self.forward)
        self.Thrust_SpinBox.valueChanged.connect(lambda: self.alter('Rotor_params', "Thrust", self.Thrust_SpinBox.value()))
        self.Torque_SpinBox.valueChanged.connect(lambda: self.alter('Rotor_params', "Torque", self.Torque_SpinBox.value()))
        self.Air_SpinBox.valueChanged.connect(lambda: self.alter('Rotor_params', "Air", self.Air_SpinBox.value()))
        self.Revolutions_SpinBox.valueChanged.connect(lambda: self.alter('Rotor_params', "Revolutions", self.Revolutions_SpinBox.value()))

        # more parameters will be added later
        # self.Diameter_SpinBox.valueChanged.connect(lambda: self.alter("Diameter"))
        # self.Height_SpinBox.valueChanged.connect(lambda: self.alter("Height"))
        # self.MaxThrust_SpinBox.valueChanged.connect(lambda: self.alter("MaxThrust"))
        # self.MaxTorque_SpinBox.valueChanged.connect(lambda: self.alter("MaxTorque"))

    def airsim_settings_config(self):
        """
        need path of settings.json
        better input in Setting_Path window
        still requires some work todo
        :return:
        """
        settings = self.AirSimSettings
        settings.reset()
        capture_settings = settings.capture_settings(image_type=0, width=788, height=520, fov_degrees=90,
                                                     auto_exposure_speed=100, auto_exposure_bias=0,
                                                     auto_exposure_max_brightness=0.64,
                                                     auto_exposure_min_brightness=0.03,
                                                     motion_blur_amount=0, target_gamma=1.0, projection_mode="",
                                                     ortho_width=5.12)
        gimbal = settings.gimbal(stabilization=0)
        camera_settings = settings.camera_settings(x=-2, y=0, z=-2, pitch=-45, roll=0, yaw=0,
                                                   capture_settings=capture_settings, gimbal=gimbal)
        cameras = settings.cameras_add("Mycamera", camera_settings)
        vehicle_settings = settings.vehicle_settings(cameras=cameras)
        vehicles = settings.vehicles_add("SimpleFlight", vehicle_settings)
        settings.set_vehicles(vehicles)

    def start_simulator(self):
        self.RPC_client.start_simulator()

    def forward(self):
        self.start_simulator()
        time.sleep(3)

        # first initiate ControlWindow, then DataWindow
        self.SettingClient.AirSimParameters.set_params()
        self.ControlWindow = ControlWindow(self.SharedData)
        self.SharedData.append_window(self.ControlWindow)
        self.DataWindow = DataWindow(self.SharedData)
        self.SharedData.append_window(self.DataWindow)
        self.DataWindow.show()
        self.ControlWindow.show()
        self.close()

    def back(self):
        # print(self.SharedData.WindowSeries.pop())
        # self.close()
        self.destroy()
        self.SharedData.WindowSeries.pop()
        self.SharedData.WindowSeries[0].show()
        # !!!need to destroy the this window object( including memory & thread)
        # I have no idea how to do it

    def show_params(self):
        self.Thrust_SpinBox.setProperty("value", self.param_data['Rotor_params']['Thrust']['Value'])
        self.Torque_SpinBox.setProperty("value", self.param_data['Rotor_params']['Torque']['Value'])
        self.Air_SpinBox.setProperty("value", self.param_data['Rotor_params']['Air']['Value'])
        self.Revolutions_SpinBox.setProperty("value", self.param_data['Rotor_params']['Revolutions']['Value'])

    def alter(self, param_kind: str, name: str, value: float):
        """
        alter : when user adjust the params through the SpinBox,the corresponding file will be modified
        further : the file will be changed.this module need to be combined with the init_body,init_kineatic method

        Args:
            name: the names of the params,which have been changed by user
        """
        # self.SettingClient.AirSimParameters.set_param(param_kind, name, value)
        self.param_data[param_kind][name]['Value'] = value  # shortcut

