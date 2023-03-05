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
        self.forwardButton.clicked.connect(self.forward)

        self.user_defined_camera_checkBox.clicked.connect(lambda: self.user_defined_enable())
        self.user_noise_checkBox.clicked.connect(lambda: self.noise_settings_enable('user', self.user_noise_checkBox.isChecked()))
        self.user_gimbal_checkBox.clicked.connect(lambda: self.gimbal_settings_enable('user', self.user_gimbal_checkBox.isChecked()))
        self.default_noise_checkBox.clicked.connect(lambda: self.noise_settings_enable('default', self.default_noise_checkBox.isChecked()))
        self.default_gimbal_checkBox.clicked.connect(lambda: self.gimbal_settings_enable('default', self.default_gimbal_checkBox.isChecked()))
        self.user_defined_enable()
        self.noise_settings_enable('default', self.default_noise_checkBox.isChecked())
        self.gimbal_settings_enable('default', self.default_gimbal_checkBox.isChecked())
        self.record_path_edit.setEnabled(False)
        if not self.SharedData.is_localhost:
            self.record_path_button.setEnabled(False)
        self.record_path_button.clicked.connect(self.open_file)


        self.Thrust_SpinBox.valueChanged.connect(lambda: self.alter('Rotor_params', "Thrust", self.Thrust_SpinBox.value()))
        self.Torque_SpinBox.valueChanged.connect(lambda: self.alter('Rotor_params', "Torque", self.Torque_SpinBox.value()))
        self.Air_SpinBox.valueChanged.connect(lambda: self.alter('Rotor_params', "Air", self.Air_SpinBox.value()))
        self.Revolutions_SpinBox.valueChanged.connect(lambda: self.alter('Rotor_params', "Revolutions", self.Revolutions_SpinBox.value()))

        # more parameters will be added later
        # self.Diameter_SpinBox.valueChanged.connect(lambda: self.alter("Diameter"))
        # self.Height_SpinBox.valueChanged.connect(lambda: self.alter("Height"))
        # self.MaxThrust_SpinBox.valueChanged.connect(lambda: self.alter("MaxThrust"))
        # self.MaxTorque_SpinBox.valueChanged.connect(lambda: self.alter("MaxTorque"))

    # def airsim_settings_config(self):
    #     """
    #     need path of settings.json
    #     better input in Setting_Path window
    #     still requires some work todo
    #     :return:
    #     """
    #     settings = self.AirSimSettings
    #     settings.reset()
    #     capture_settings = settings.capture_settings(image_type=0, width=788, height=520, fov_degrees=90,
    #                                                  auto_exposure_speed=100, auto_exposure_bias=0,
    #                                                  auto_exposure_max_brightness=0.64,
    #                                                  auto_exposure_min_brightness=0.03,
    #                                                  motion_blur_amount=0, target_gamma=1.0, projection_mode="",
    #                                                  ortho_width=5.12)
    #     gimbal = settings.gimbal(stabilization=0)
    #     camera_settings = settings.camera_settings(x=-2, y=0, z=-2, pitch=-45, roll=0, yaw=0,
    #                                                capture_settings=capture_settings, gimbal=gimbal)
    #     cameras = settings.cameras_add("Mycamera", camera_settings)
    #     vehicle_settings = settings.vehicle_settings(cameras=cameras)
    #     vehicles = settings.vehicles_add("SimpleFlight", vehicle_settings)
    #     settings.set_vehicles(vehicles)

    def airsim_settings_config(self):
        """
        need path of settings.json
        better input in Setting_Path window
        still requires some work todo
        :return:
        """
        settings = self.AirSimSettings
        settings.reset()
        settings.set_wind(self.wind_north_SpinBox.value(), self.wind_east_SpinBox.value(), self.wind_down_SpinBox.value())
        settings.set_origin_geopoint(self.born_latitude_SpinBox.value(), self.born_longitude_SpinBox.value(), self.born_altitude_SpinBox.value())

        projection_mode = ""
        if self.default_project_mode_choose.currentText() == '透视投影':
            projection_mode = 'perspective'
        elif self.default_project_mode_choose.currentText() == '正射投影':
            projection_mode = 'orthographic'
        capture_settings = settings.capture_settings(image_type=settings.image_type(self.default_image_type_choose.currentText()),
                                                     width=self.default_width_SpinBox.value(),
                                                     height=self.default_height_SpinBox.value(),
                                                     fov_degrees=self.default_fov_degrees_SpinBox.value(),
                                                     auto_exposure_speed=self.default_auto_exposure_speed_SpinBox.value(),
                                                     auto_exposure_bias=self.default_auto_exposure_bias_SpinBox.value(),
                                                     auto_exposure_max_brightness=self.default_auto_exposure_max_brightness_SpinBox.value(),
                                                     auto_exposure_min_brightness=self.default_auto_exposure_min_brightness_SpinBox.value(),
                                                     motion_blur_amount=self.default_motion_blur_amount_SpinBox.value(),
                                                     target_gamma=self.default_target_gamma_SpinBox.value(),
                                                     projection_mode=projection_mode,
                                                     ortho_width=self.default_ortho_width_SpinBox.value())

        noise_settings = []
        if self.default_noise_checkBox.isChecked():
            noise_settings = settings.noise_settings(enabled=True,
                                                     image_type=settings.image_type(self.default_noise_image_type_choose.currentText()),
                                                     rand_contrib=self.default_rand_contrib_SpinBox.value(),
                                                     rand_size=self.default_rand_size_SpinBox.value(),
                                                     rand_speed=self.default_rand_speed_SpinBox.value(),
                                                     rand_density=self.default_rand_density_SpinBox.value(),
                                                     horz_noise_lines_contrib=self.default_horz_noise_lines_contrib_SpinBox.value(),
                                                     horz_noise_lines_density_y=self.default_horz_noise_lines_density_y_SpinBox.value(),
                                                     horz_noise_lines_density_xy=self.default_horz_noise_lines_density_xy_SpinBox.value(),
                                                     horz_wave_contrib=self.default_horz_wave_contrib_SpinBox.value(),
                                                     horz_wave_strength=self.default_horz_wave_strength_SpinBox.value(),
                                                     horz_wave_vert_size=self.default_horz_wave_vert_size_SpinBox.value(),
                                                     horz_wave_screen_size=self.default_horz_wave_screen_size_SpinBox.value(),
                                                     horz_distortion_contrib=self.default_horz_distortion_contrib_SpinBox.value(),
                                                     horz_distortion_strength=self.default_horz_distortion_strength_SpinBox.value())
        gimbal = {}
        if self.default_gimbal_checkBox.isChecked():
            gimbal = settings.gimbal(pitch=self.default_pitch_SpinBox.value(),
                                     roll=self.default_roll_SpinBox.value(),
                                     yaw=self.default_yaw_SpinBox.value(),
                                     stabilization=1)
        settings.set_camera_defaults(capture_settings=capture_settings, noise_settings=noise_settings, gimbal=gimbal)

        if self.user_defined_camera_checkBox.isChecked():
            projection_mode = ""
            if self.user_project_mode_choose.currentText() == '透视投影':
                projection_mode = 'perspective'
            elif self.user_project_mode_choose.currentText() == '正射投影':
                projection_mode = 'orthographic'
            capture_settings = settings.capture_settings(
                image_type=settings.image_type(self.user_image_type_choose.currentText()),
                width=self.user_width_SpinBox.value(),
                height=self.user_height_SpinBox.value(),
                fov_degrees=self.user_fov_degrees_SpinBox.value(),
                auto_exposure_speed=self.user_auto_exposure_speed_SpinBox.value(),
                auto_exposure_bias=self.user_auto_exposure_bias_SpinBox.value(),
                auto_exposure_max_brightness=self.user_auto_exposure_max_brightness_SpinBox.value(),
                auto_exposure_min_brightness=self.user_auto_exposure_min_brightness_SpinBox.value(),
                motion_blur_amount=self.user_motion_blur_amount_SpinBox.value(),
                target_gamma=self.user_target_gamma_SpinBox.value(),
                projection_mode=projection_mode,
                ortho_width=self.user_ortho_width_SpinBox.value())
            noise_settings = []
            if self.user_noise_checkBox.isChecked():
                noise_settings = settings.noise_settings(enabled=True,
                                                         image_type=settings.image_type(
                                                             self.user_noise_image_type_choose.currentText()),
                                                         rand_contrib=self.user_rand_contrib_SpinBox.value(),
                                                         rand_size=self.user_rand_size_SpinBox.value(),
                                                         rand_speed=self.user_rand_speed_SpinBox.value(),
                                                         rand_density=self.user_rand_density_SpinBox.value(),
                                                         horz_noise_lines_contrib=self.user_horz_noise_lines_contrib_SpinBox.value(),
                                                         horz_noise_lines_density_y=self.user_horz_noise_lines_density_y_SpinBox.value(),
                                                         horz_noise_lines_density_xy=self.user_horz_noise_lines_density_xy_SpinBox.value(),
                                                         horz_wave_contrib=self.user_horz_wave_contrib_SpinBox.value(),
                                                         horz_wave_strength=self.user_horz_wave_strength_SpinBox.value(),
                                                         horz_wave_vert_size=self.user_horz_wave_vert_size_SpinBox.value(),
                                                         horz_wave_screen_size=self.user_horz_wave_screen_size_SpinBox.value(),
                                                         horz_distortion_contrib=self.user_horz_distortion_contrib_SpinBox.value(),
                                                         horz_distortion_strength=self.user_horz_distortion_strength_SpinBox.value())
            gimbal = {}
            if self.user_gimbal_checkBox.isChecked():
                gimbal = settings.gimbal(pitch=self.user_pitch_SpinBox.value(),
                                         roll=self.user_roll_SpinBox.value(),
                                         yaw=self.user_yaw_SpinBox.value(),
                                         stabilization=1)
            camera_settings = settings.camera_settings(x=self.user_x_SpinBox.value(), y=self.user_y_SpinBox.value(), 
                                                       z=self.user_z_SpinBox.value(), pitch=self.user_born_pitch_SpinBox.value(),
                                                       roll=self.user_born_roll_SpinBox.value(),
                                                       yaw=self.user_born_yaw_SpinBox.value(),
                                                       capture_settings=capture_settings, noise_settings=noise_settings, 
                                                       gimbal=gimbal)
            cameras = settings.cameras_add("user_defined", camera_settings)
            vehicle_settings = settings.vehicle_settings(cameras=cameras)
            vehicles = settings.vehicles_add(vehicle_settings=vehicle_settings)
            settings.set_vehicles(vehicles)
        else:
            capture_settings = settings.capture_settings(image_type=0, width=788, height=520, fov_degrees=90,
                                                             auto_exposure_speed=100, auto_exposure_bias=0,
                                                             auto_exposure_max_brightness=0.64,
                                                             auto_exposure_min_brightness=0.03,
                                                             motion_blur_amount=0, target_gamma=1.0, projection_mode="",
                                                             ortho_width=5.12)
            gimbal = settings.gimbal(stabilization=0)
            camera_settings = settings.camera_settings(x=-2, y=0, z=-2, pitch=-45, roll=0, yaw=0,
                                                       capture_settings=capture_settings, gimbal=gimbal)
            cameras = settings.cameras_add("user_defined", camera_settings)
            vehicle_settings = settings.vehicle_settings(cameras=cameras)
            vehicles = settings.vehicles_add(vehicle_settings=vehicle_settings)
            settings.set_vehicles(vehicles)

        recording_cameras = []
        if self.record_fl_camera_checkBox.isChecked():
            recording_camera = settings.recording_camera(camera_name='1', image_type=0, vehicle_name="SimpleFlight",
                                                         compress=self.record_fl_camera_compress_checkBox.isChecked())
            recording_cameras.append(recording_camera)
        if self.record_fr_camera_checkBox.isChecked():
            recording_camera = settings.recording_camera(camera_name='2', image_type=0, vehicle_name="SimpleFlight",
                                                         compress=self.record_fr_camera_compress_checkBox.isChecked())
            recording_cameras.append(recording_camera)
        if self.record_back_camera_checkBox.isChecked():
            recording_camera = settings.recording_camera(camera_name='3', image_type=0, vehicle_name="SimpleFlight",
                                                         compress=self.record_back_camera_compress_checkBox.isChecked())
            recording_cameras.append(recording_camera)
        if self.record_buttom_center_camera_checkBox.isChecked():
            recording_camera = settings.recording_camera(camera_name='4', image_type=0, vehicle_name="SimpleFlight",
                                                         compress=self.record_buttom_center_camera_compress_checkBox.isChecked())
            recording_cameras.append(recording_camera)
        if self.SharedData.is_localhost:
            folder = self.record_path_edit.text()
        else:
            folder = ""
        if len(recording_cameras) > 3:
            QMessageBox.warning(self, "提示(采样相机设置）", "最多选择三个相机用于记录，已选择的相机中只有前三个相机会生效", QMessageBox.Ok)
        while len(recording_cameras) > 3:
            recording_cameras.pop()
        settings.set_recording(folder=folder, record_interval=self.record_interval_SpinBox.value(),
                               recording_cameras=recording_cameras, record_on_move=self.record_on_move_checkBox.isChecked(),
                               enabled=self.record_enabled_checkBox.isChecked())

    def start_simulator(self):
        self.RPC_client.start_simulator()

    def forward(self):
        self.SettingClient.AirSimParameters.set_params()
        self.airsim_settings_config()

        self.start_simulator()

        # first initiate ControlWindow, then DataWindow
        # self.ControlWindow = ControlWindow(self.SharedData)
        # self.SharedData.append_window(self.ControlWindow)
        self.DataWindow = DataWindow(self.SharedData)
        self.SharedData.append_window(self.DataWindow)
        self.DataWindow.show()
        # self.ControlWindow.show()
        self.close()

    def back(self):
        # print(self.SharedData.WindowSeries.pop())
        # self.close()
        self.SharedData.WindowSeries.pop()
        self.destroy()
        self.SharedData.WindowSeries[0].show()
        # !!!need to destroy the window object( including memory & thread)
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

    def user_defined_enable(self):
        user_enable = self.user_defined_camera_checkBox.isChecked()

        self.user_x_SpinBox.setEnabled(user_enable)
        self.user_y_SpinBox.setEnabled(user_enable)
        self.user_z_SpinBox.setEnabled(user_enable)
        self.user_born_yaw_SpinBox.setEnabled(user_enable)
        self.user_born_pitch_SpinBox.setEnabled(user_enable)
        self.user_born_roll_SpinBox.setEnabled(user_enable)
        self.user_image_type_choose.setEnabled(user_enable)
        self.user_project_mode_choose.setEnabled(user_enable)
        self.user_width_SpinBox.setEnabled(user_enable)
        self.user_height_SpinBox.setEnabled(user_enable)
        self.user_fov_degrees_SpinBox.setEnabled(user_enable)
        self.user_auto_exposure_speed_SpinBox.setEnabled(user_enable)
        self.user_auto_exposure_bias_SpinBox.setEnabled(user_enable)
        self.user_auto_exposure_max_brightness_SpinBox.setEnabled(user_enable)
        self.user_auto_exposure_min_brightness_SpinBox.setEnabled(user_enable)
        self.user_motion_blur_amount_SpinBox.setEnabled(user_enable)
        self.user_target_gamma_SpinBox.setEnabled(user_enable)
        self.user_ortho_width_SpinBox.setEnabled(user_enable)
        self.user_noise_checkBox.setEnabled(user_enable)
        self.user_gimbal_checkBox.setEnabled(user_enable)
        if user_enable:
            self.noise_settings_enable('user', self.user_noise_checkBox.isChecked())
            self.gimbal_settings_enable('user', self.user_gimbal_checkBox.isChecked())
        else:
            self.noise_settings_enable('user', False)
            self.gimbal_settings_enable('user', False)

    def noise_settings_enable(self, position: str, enabled):
        if position == 'default':
            self.default_noise_image_type_choose.setEnabled(enabled)
            self.default_rand_size_SpinBox.setEnabled(enabled)
            self.default_rand_speed_SpinBox.setEnabled(enabled)
            self.default_rand_contrib_SpinBox.setEnabled(enabled)
            self.default_rand_density_SpinBox.setEnabled(enabled)
            self.default_horz_noise_lines_contrib_SpinBox.setEnabled(enabled)
            self.default_horz_noise_lines_density_y_SpinBox.setEnabled(enabled)
            self.default_horz_noise_lines_density_xy_SpinBox.setEnabled(enabled)
            self.default_horz_wave_contrib_SpinBox.setEnabled(enabled)
            self.default_horz_wave_strength_SpinBox.setEnabled(enabled)
            self.default_horz_wave_vert_size_SpinBox.setEnabled(enabled)
            self.default_horz_wave_screen_size_SpinBox.setEnabled(enabled)
            self.default_horz_distortion_contrib_SpinBox.setEnabled(enabled)
            self.default_horz_distortion_strength_SpinBox.setEnabled(enabled)
        elif position == 'user':
            self.user_image_type_choose.setEnabled(enabled)
            self.user_rand_size_SpinBox.setEnabled(enabled)
            self.user_rand_speed_SpinBox.setEnabled(enabled)
            self.user_rand_contrib_SpinBox.setEnabled(enabled)
            self.user_rand_density_SpinBox.setEnabled(enabled)
            self.user_horz_noise_lines_contrib_SpinBox.setEnabled(enabled)
            self.user_horz_noise_lines_density_y_SpinBox.setEnabled(enabled)
            self.user_horz_noise_lines_density_xy_SpinBox.setEnabled(enabled)
            self.user_horz_wave_contrib_SpinBox.setEnabled(enabled)
            self.user_horz_wave_strength_SpinBox.setEnabled(enabled)
            self.user_horz_wave_vert_size_SpinBox.setEnabled(enabled)
            self.user_horz_wave_screen_size_SpinBox.setEnabled(enabled)
            self.user_horz_distortion_contrib_SpinBox.setEnabled(enabled)
            self.user_horz_distortion_strength_SpinBox.setEnabled(enabled)

    def gimbal_settings_enable(self, position: str, enabled):
        if position == 'default':
            self.default_pitch_SpinBox.setEnabled(enabled)
            self.default_roll_SpinBox.setEnabled(enabled)
            self.default_yaw_SpinBox.setEnabled(enabled)
        elif position == 'user':
            self.user_pitch_SpinBox.setEnabled(enabled)
            self.user_roll_SpinBox.setEnabled(enabled)
            self.user_yaw_SpinBox.setEnabled(enabled)

    def open_file(self):
        """
        open_file : show the file selection window when the tool button is clicked
                    when airsim comboBox is selected,the target will be restricted to folder
                    otherwise the target will be executable files
        """
        dpath = QtWidgets.QFileDialog.getExistingDirectory(self, "Open Folder", os.getcwd())
        # dpath = dpath.replace('/', '\\')
        self.record_path_edit.setText(dpath)


            


