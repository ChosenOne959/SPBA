import keyboard

from new_ui.show_data.Ui_showdata_v2 import Ui_DataWindow
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QMainWindow, QMessageBox
from PyQt5.QtCore import QTimer
import airsim
import cv2
from PyQt5.QtWidgets import QApplication, QGraphicsView, QMessageBox, QGraphicsScene, QGraphicsPixmapItem
from PyQt5.QtGui import QPixmap, QImage
import os
import new_ui.SPBA_API as SPBA_API
import threading
from new_ui.SPBA_API import Multirotor
from new_ui.SPBA_API import Car
from new_ui.SPBA_API import SettingClient
from new_ui.controller.keyboard_controler import keyboard_control
import threading
import time
import subprocess



class DataWindow(QMainWindow, Ui_DataWindow):
    """
    MysensorWindow : show the sensor data and world camera scene.But,there is caton problem at present.Maybe it can be solved by delayed time processing--
                     catch hundreds of images befor show the window and upgrade the images in the cache constantly.

    """

    def __init__(self, SharedData, parent=None):
        self.SharedData = SharedData
        super(DataWindow, self).__init__(parent)
        self.setupUi(self)
        self.Classification()
        self.set_myUI()
        self.control_busy = False
        self.record_flag = False
        self.replay_flag = False
        self.replay_count = 0
        self.record_length = 0

        # self.init_airsim()
        self.init_timer()

    def Classification(self):
        if self.SharedData.Vehicle_Type == 0 :
            self.Client = Multirotor(self.SharedData)
        elif self.SharedData.Vehicle_Type ==1 :
            self.Client = Car(self.SharedData)

    def set_myUI(self):
        self.route_button.clicked.connect(self.route)
        self.KeyboardCtrl_start.clicked.connect(self.keyboard_controler)
        self.control_up.clicked.connect(lambda: self.controller_panel('up'))
        self.control_down.clicked.connect(lambda: self.controller_panel('down'))
        self.control_forward.clicked.connect(lambda: self.controller_panel('forward'))
        self.control_backward.clicked.connect(lambda: self.controller_panel('backward'))
        self.control_turnL.clicked.connect(lambda: self.controller_panel('turnL'))
        self.control_turnR.clicked.connect(lambda: self.controller_panel('turnR'))
        self.KeyboardCtrl_stop.clicked.connect(lambda: self.end_KeyboardCtrl())
        self.record_button.clicked.connect(lambda: self.record())
        self.replay_button.clicked.connect(lambda: self.replay(True))
        self.replay_stop_button.clicked.connect(lambda: self.replay(False))
        self.replay_button.setDisabled(True)
        self.replay_stop_button.setDisabled(True)
        self.code_run_start.clicked.connect(lambda: self.running())
        self.code_run_start.clicked.connect(lambda: self.stopCode())

    def end_KeyboardCtrl(self):
        print("press and release q")
        keyboard.press_and_release('q')

    def time_out(self):
        if self.replay_flag:
            self.replay_count += 1
        else:
            self.Client.GroundTruth.update()
            if self.record_flag:
                self.record_length += 1
        self.show_all_data()
        print("replay:", self.replay_count, "\trecord:", self.record_length, "\n")

    def show_all_data(self):
        self.plot_clear()
        if not self.replay_flag:
            imu_data = self.Client.GroundTruth.ImuData
            barometer_data = self.Client.GroundTruth.BarometerData
            magnetometer_data = self.Client.GroundTruth.MagnetometerData
            gps_data = self.Client.GroundTruth.GpsData
            kinematics_data = self.Client.GroundTruth.KinematicsState
            environment_data = self.Client.GroundTruth.EnvironmentState
            front_center_img = main_view_img = self.Client.GroundTruth.CameraImages[0]
            front_left_img = self.Client.GroundTruth.CameraImages[1]
            front_right_img = self.Client.GroundTruth.CameraImages[2]
            bottom_center_img = self.Client.GroundTruth.CameraImages[3]
            back_center_img = self.Client.GroundTruth.CameraImages[4]
            user_defined_img = self.Client.GroundTruth.CameraImages[5]

            self.time_count()
            self.plot_data("imu", imu_data)
            self.plot_data("barometer", barometer_data)
            self.plot_data("gps", gps_data)
            self.plot_data("magnetometer", magnetometer_data)
            self.plot_data("kinematics", kinematics_data)
            self.plot_data("environment", environment_data)
            #self.showGraphic(self.user_defined_view, user_defined_img)
            self.showGraphic_user(user_defined_img)
            # self.showGraphic(self.front_center_view, front_center_img)
            self.showGraphic(self.front_left_view, front_left_img)
            self.showGraphic(self.front_right_view, front_right_img)
            self.showGraphic(self.bottom_center_view, bottom_center_img)
            self.showGraphic(self.back_center_view, back_center_img)
            if self.record_flag:
                self.record_images['front_center'].append(front_center_img)
                self.record_images['front_left'].append(front_left_img)
                self.record_images['front_right'].append(front_right_img)
                self.record_images['bottom_center'].append(bottom_center_img)
                self.record_images['back_center'].append(back_center_img)
                #self.record_images['user_defined'].append(user_defined_img)
        else:
            self.time_count()
            self.plot_record_data()
            self.showGraphic(self.user_defined_view, self.record_images['user_defined'][self.replay_count])
            
            # self.showGraphic(self.front_center_view, self.record_images['front_center'][self.replay_count])
            self.showGraphic(self.front_left_view, self.record_images['front_left'][self.replay_count])
            self.showGraphic(self.front_right_view, self.record_images['front_right'][self.replay_count])
            self.showGraphic(self.bottom_center_view, self.record_images['bottom_center'][self.replay_count])
            self.showGraphic(self.back_center_view, self.record_images['back_center'][self.replay_count])
            if self.replay_count >= self.record_length-1:
                self.replay(False)

    def record(self):
        self.record_flag = not self.record_flag
        if self.record_flag:
            self.replay_button.setDisabled(True)
            self.replay_stop_button.setDisabled(True)
            self.record_data_clear()
            self.output_edit.setText("Recording...")
        else:
            self.replay_button.setDisabled(False)
            self.replay_stop_button.setDisabled(False)
            self.output_edit.setText("Recording finished, now that you can replay")


    def replay(self, flag):
        self.replay_flag = flag
        if flag:
            self.replay_count = 0
            self.record_button.setDisabled(True)
            self.output_edit.setText("Replaying...")
            self.controller_setDisabled(True)
        else:
            self.record_button.setDisabled(False)
            self.output_edit.setText("Replaying finished")
            self.controller_setDisabled(False)
        self.display_data_clear()

    def keyboard_controler(self):
        self.output_edit.setText("Keyboard Controller:"
                                 "t: take off; l: land"
                                 "a: up; d: down"
                                 "up arrow: forward; down arrow: backward"
                                 "left arrow: left; right arrow: right"
                                 "left shift: speed up"
                                 "q: quit")
        self.keyboard_thread = threading.Thread(target=self.keyboard_control_thread)
        self.keyboard_thread.start()
        print("finish")

    def keyboard_control_thread(self):
        self.controller_setDisabled(True)
        self.KeyboardCtrl_stop.setDisabled(False)
        self.Client.FlightControl.keyboard_control()
        self.controller_setDisabled(False)

    def route_thread(self, para):
        print("Routing")
        self.controller_setDisabled(True)
        self.Client.LQR_fly(para)
        self.controller_setDisabled(False)
        print("Routing finished")

    def route(self):
        if self.route_choose.currentText() == '0形路径':
            route_thread = threading.Thread(target=self.route_thread, args='0')
        elif self.route_choose.currentText() == '8形路径':
            route_thread = threading.Thread(target=self.route_thread, args='8')
        route_thread.start()

    def init_timer(self):
        self.sensor_data_interval = QTimer(self)
        self.sensor_data_interval.timeout.connect(self.time_out)
        self.time_interval = 40
        self.sensor_data_interval.start(self.time_interval)
        self.display_data_clear()

    def end_task(self):
        # del self.Client
        # self.sensor_data_interval.stop()
        self.SharedData.resources["RPC_client"].kill_task(True, "UE4Editor.exe")
        self.SharedData.resources["RPC_client"].kill_task(False, "Python.exe")

    def running(self):
        runcode_thread = threading.Thread(target=self.runCode)
        runcode_thread.start()

    def runCode(self):
        """
        runCode : when the "run" button is clicked,complete showing realtime window,showing the timestamp,
                    compile the code and display the compile information.
                    If the unreal project is not ready,this process will report an error.
        """
        self.controller_setDisabled(True)
        run_time = time.localtime()
        run_date = "<" + str(run_time.tm_year) + "/" + str(run_time.tm_mon) + "/" + str(run_time.tm_mday) + ">"
        run_clock = str(run_time.tm_hour) + ":" + str(run_time.tm_min).rjust(2, '0')
        self.output_edit.append(run_date)
        self.output_edit.append(run_clock)
        flag = 0
        code = self.code_edit.toPlainText()
        file_path = "codefile.py "
        with open(file_path, 'w+') as codefile:
            codefile.write(code)
            print("write codefile")
        try:
            subprocess.check_call("python codefile.py 2>error.txt ", shell=True)
            '''
            in order to catch the compile information ,need to control the child thread and wait it 
            '''
        except Exception as e:
            flag = 1
            with open("error.txt", 'r') as mes:
                '''
                when the error appears,the error information will be writen into the error file and show its contain on the textBrower
                '''
                for i in mes:
                    self.output_edit.append(i)
        if flag == 1:
            flag = 0
            print("an error occurred")
        else:
            print("compiled successfully!!")
            self.output_edit.append("compiled successfully!!")
        os.remove("error.txt")
        #os.remove("codefile.py")
        self.controller_setDisabled(False)

    def stopCode(self):
        pass

    def controller_setDisabled(self, flag=True):
        print("set controller disabled: ", flag)
        self.route_button.setDisabled(flag)
        self.KeyboardCtrl_start.setDisabled(flag)
        self.KeyboardCtrl_stop.setDisabled(flag)
        self.code_run_stop.setDisabled(flag)
        self.code_run_start.setDisabled(flag)
        self.control_up.setDisabled(flag)
        self.control_down.setDisabled(flag)
        self.control_forward.setDisabled(flag)
        self.control_backward.setDisabled(flag)
        self.control_turnL.setDisabled(flag)
        self.control_turnR.setDisabled(flag)

    def controller_panel(self, button):
        velocity = 3
        duration = 1
        yaw_rate = 0.3  # in radian per second
        vehicle_name = ""

        if button == 'forward':
            self.Client.FlightControl.moveByVelocityBodyFrameAsync(velocity, 0, 0, duration=duration,vehicle_name=vehicle_name)
        elif button == 'backward':
            self.Client.FlightControl.moveByVelocityBodyFrameAsync(-velocity, 0, 0, duration=duration,vehicle_name=vehicle_name)
        elif button == 'up':
            self.Client.FlightControl.moveByVelocityBodyFrameAsync(0, 0, -velocity, duration=duration,vehicle_name=vehicle_name)
        elif button == 'down':
            self.Client.FlightControl.moveByVelocityBodyFrameAsync(0, 0, velocity, duration=duration,vehicle_name=vehicle_name)
        elif button == 'turnL':
            self.Client.FlightControl.moveByRollPitchYawrateZAsync(0, 0, yaw_rate, 0, duration=duration, vehicle_name=vehicle_name)
        elif button == 'turnR':
            self.Client.FlightControl.moveByRollPitchYawrateZAsync(0, 0, -yaw_rate, 0, duration=duration, vehicle_name=vehicle_name)

    def time_count(self):
        if len(self.time_axis) == 0:
            self.time_axis.append(self.time_interval / 1000)
        else:
            self.time_axis.append(self.time_axis[-1] + self.time_interval / 1000)

    def plot_clear(self):
        """
        plot_clear : the datas have to be cleared before show them again
        """
        self.imu_angular_plot.clear()
        self.imu_linear_plot.clear()
        self.imu_orientation_plot.clear()
        self.barometer_altitude_plot.clear()
        self.barometer_pressure_plot.clear()
        self.barometer_qnh_plot.clear()
        self.gps_altitude_plot.clear()
        self.gps_longitude_plot.clear()
        self.gps_latitude_plot.clear()
        self.gps_velocity_plot.clear()
        self.magnetometer.clear()
        self.kinematics_position_plot.clear()
        self.kinematics_linear_velocity_plot.clear()
        self.kinematics_linear_acceleration_plot.clear()
        self.kinematics_orientation_plot.clear()
        self.kinematics_angular_velocity_plot.clear()
        self.kinematics_angular_acceleration_plot.clear()
        self.environment_pressure_plot.clear()
        self.environment_air_density_plot.clear()
        self.environment_gravity_plot.clear()
        self.environment_temperature_plot.clear()

    def display_data_clear(self):
        self.time_axis = []
        self.imu_data_orientation_x_val = []
        self.imu_data_orientation_y_val = []
        self.imu_data_orientation_z_val = []
        self.imu_data_orientation_w_val = []
        self.imu_data_angular_velocity_x_val = []
        self.imu_data_angular_velocity_y_val = []
        self.imu_data_angular_velocity_z_val = []
        self.imu_data_linear_acceleration_x_val = []
        self.imu_data_linear_acceleration_y_val = []
        self.imu_data_linear_acceleration_z_val = []
        self.barometer_data_pressure = []
        self.barometer_data_altitude = []
        self.barometer_data_qnh = []
        self.gps_data_geo_latitude = []
        self.gps_data_geo_longitude = []
        self.gps_data_geo_altitude = []
        self.gps_data_velocity_x_val = []
        self.gps_data_velocity_y_val = []
        self.gps_data_velocity_z_val = []
        self.magnetometer_data_magnetic_field_body_x_val = []
        self.magnetometer_data_magnetic_field_body_y_val = []
        self.magnetometer_data_magnetic_field_body_z_val = []
        self.environment_data_pressure = []
        self.environment_data_air_density = []
        self.environment_gravity_x_val = []
        self.environment_gravity_y_val = []
        self.environment_gravity_z_val = []
        self.environment_data_temperature = []
        self.kinematics_position_x_val = []
        self.kinematics_position_y_val = []
        self.kinematics_position_z_val = []
        self.kinematics_orientation_x_val = []
        self.kinematics_orientation_y_val = []
        self.kinematics_orientation_z_val = []
        self.kinematics_linear_velocity_x_val = []
        self.kinematics_linear_velocity_y_val = []
        self.kinematics_linear_velocity_z_val = []
        self.kinematics_linear_acceleration_x_val = []
        self.kinematics_linear_acceleration_y_val = []
        self.kinematics_linear_acceleration_z_val = []
        self.kinematics_angular_velocity_x_val = []
        self.kinematics_angular_velocity_y_val = []
        self.kinematics_angular_velocity_z_val = []
        self.kinematics_angular_acceleration_x_val = []
        self.kinematics_angular_acceleration_y_val = []
        self.kinematics_angular_acceleration_z_val = []

    def record_data_clear(self):
        self.record_length = 0
        self.record_images = {'user_defined': [], 'front_left': [], 'front_right': [], 'bottom_center': [],
                              'front_center': [], 'back_center': []}
        self.record_imu_data_orientation_x_val = []
        self.record_imu_data_orientation_y_val = []
        self.record_imu_data_orientation_z_val = []
        self.record_imu_data_orientation_w_val = []
        self.record_imu_data_angular_velocity_x_val = []
        self.record_imu_data_angular_velocity_y_val = []
        self.record_imu_data_angular_velocity_z_val = []
        self.record_imu_data_linear_acceleration_x_val = []
        self.record_imu_data_linear_acceleration_y_val = []
        self.record_imu_data_linear_acceleration_z_val = []
        self.record_barometer_data_pressure = []
        self.record_barometer_data_altitude = []
        self.record_barometer_data_qnh = []
        self.record_gps_data_geo_latitude = []
        self.record_gps_data_geo_longitude = []
        self.record_gps_data_geo_altitude = []
        self.record_gps_data_velocity_x_val = []
        self.record_gps_data_velocity_y_val = []
        self.record_gps_data_velocity_z_val = []
        self.record_magnetometer_data_magnetic_field_body_x_val = []
        self.record_magnetometer_data_magnetic_field_body_y_val = []
        self.record_magnetometer_data_magnetic_field_body_z_val = []
        self.record_environment_data_pressure = []
        self.record_environment_data_air_density = []
        self.record_environment_gravity_x_val = []
        self.record_environment_gravity_y_val = []
        self.record_environment_gravity_z_val = []
        self.record_environment_data_temperature = []
        self.record_kinematics_position_x_val = []
        self.record_kinematics_position_y_val = []
        self.record_kinematics_position_z_val = []
        self.record_kinematics_orientation_x_val = []
        self.record_kinematics_orientation_y_val = []
        self.record_kinematics_orientation_z_val = []
        self.record_kinematics_linear_velocity_x_val = []
        self.record_kinematics_linear_velocity_y_val = []
        self.record_kinematics_linear_velocity_z_val = []
        self.record_kinematics_linear_acceleration_x_val = []
        self.record_kinematics_linear_acceleration_y_val = []
        self.record_kinematics_linear_acceleration_z_val = []
        self.record_kinematics_angular_velocity_x_val = []
        self.record_kinematics_angular_velocity_y_val = []
        self.record_kinematics_angular_velocity_z_val = []
        self.record_kinematics_angular_acceleration_x_val = []
        self.record_kinematics_angular_acceleration_y_val = []
        self.record_kinematics_angular_acceleration_z_val = []

    def plot_record_data(self):
        # imu
        self.imu_data_angular_velocity_x_val.append(self.record_imu_data_angular_velocity_x_val[self.replay_count])
        self.imu_data_angular_velocity_y_val.append(self.record_imu_data_angular_velocity_y_val[self.replay_count])
        self.imu_data_angular_velocity_z_val.append(self.record_imu_data_angular_velocity_z_val[self.replay_count])
        self.imu_angular_plot.addLegend()
        self.imu_angular_plot.plot(self.time_axis, self.imu_data_angular_velocity_x_val, pen="#9400D3", name="X")
        self.imu_angular_plot.plot(self.time_axis, self.imu_data_angular_velocity_y_val, pen="#CD5555", name="Y")
        self.imu_angular_plot.plot(self.time_axis, self.imu_data_angular_velocity_z_val, pen="#20B2AA", name="Z")
        self.imu_angular_plot.setLabel('bottom', "time/s")
        self.imu_angular_plot.setLabel('left', "Angular_Velocity")

        self.imu_data_linear_acceleration_x_val.append(self.record_imu_data_linear_acceleration_x_val[self.replay_count])
        self.imu_data_linear_acceleration_y_val.append(self.record_imu_data_linear_acceleration_y_val[self.replay_count])
        self.imu_data_linear_acceleration_z_val.append(self.record_imu_data_linear_acceleration_z_val[self.replay_count])
        self.imu_linear_plot.addLegend()
        self.imu_linear_plot.plot(self.time_axis, self.imu_data_linear_acceleration_x_val, pen="#9400D3", name="X")
        self.imu_linear_plot.plot(self.time_axis, self.imu_data_linear_acceleration_y_val, pen="#CD5555", name="Y")
        self.imu_linear_plot.plot(self.time_axis, self.imu_data_linear_acceleration_z_val, pen="#20B2AA", name="Z")
        self.imu_linear_plot.setLabel('bottom', "time/s")
        self.imu_linear_plot.setLabel('left', "Linear_Acceleration")

        self.imu_data_orientation_x_val.append(self.record_imu_data_orientation_x_val[self.replay_count])
        self.imu_data_orientation_y_val.append(self.record_imu_data_orientation_y_val[self.replay_count])
        self.imu_data_orientation_z_val.append(self.record_imu_data_orientation_z_val[self.replay_count])
        self.imu_data_orientation_w_val.append(self.record_imu_data_orientation_w_val[self.replay_count])
        self.imu_orientation_plot.addLegend()
        self.imu_orientation_plot.plot(self.time_axis, self.imu_data_orientation_x_val, pen="#9400D3", name="X")
        self.imu_orientation_plot.plot(self.time_axis, self.imu_data_orientation_y_val, pen="#CD5555", name="Y")
        self.imu_orientation_plot.plot(self.time_axis, self.imu_data_orientation_z_val, pen="#20B2AA", name="Z")
        self.imu_orientation_plot.plot(self.time_axis, self.imu_data_orientation_w_val, pen="red", name="O_W")
        self.imu_orientation_plot.setLabel('bottom', "time/s")
        self.imu_orientation_plot.setLabel('left', "Orientation")

        # barometer
        self.barometer_data_pressure.append(self.record_barometer_data_pressure[self.replay_count])
        self.barometer_data_altitude.append(self.record_barometer_data_altitude[self.replay_count])
        self.barometer_data_qnh.append(self.record_barometer_data_qnh[self.replay_count])
        self.barometer_pressure_plot.addLegend()
        self.barometer_pressure_plot.plot(self.time_axis, self.barometer_data_pressure, pen='#9400D3',
                                          name="Pressure")
        self.barometer_pressure_plot.setLabel('bottom', 'time/s')
        self.barometer_pressure_plot.setLabel('left', "Barometer_Pressure")
        self.barometer_altitude_plot.addLegend()
        self.barometer_altitude_plot.plot(self.time_axis, self.barometer_data_altitude, pen='#9400D3',
                                          name="Altitude")
        self.barometer_altitude_plot.setLabel('bottom', 'time/s')
        self.barometer_altitude_plot.setLabel('left', "Barometer_Altitude")
        self.barometer_qnh_plot.addLegend()
        self.barometer_qnh_plot.plot(self.time_axis, self.barometer_data_qnh, pen='#9400D3',
                                     name="Qnh")
        self.barometer_qnh_plot.setLabel('bottom', 'time/s')
        self.barometer_qnh_plot.setLabel('left', "Barometer_Qnh")

        # gps
        self.gps_data_geo_latitude.append(self.record_gps_data_geo_latitude[self.replay_count])
        self.gps_data_geo_longitude.append(self.record_gps_data_geo_longitude[self.replay_count])
        self.gps_data_geo_altitude.append (self.record_gps_data_geo_altitude[self.replay_count])
        self.gps_data_velocity_x_val.append(self.record_gps_data_velocity_x_val[self.replay_count])
        self.gps_data_velocity_y_val.append(self.record_gps_data_velocity_y_val[self.replay_count])
        self.gps_data_velocity_z_val.append(self.record_gps_data_velocity_z_val[self.replay_count])
        self.gps_altitude_plot.addLegend()
        self.gps_altitude_plot.plot(self.time_axis, self.gps_data_geo_altitude, pen='#4169E1', name="altitude")
        self.gps_altitude_plot.setLabel('bottom', 'time/s')
        self.gps_altitude_plot.setLabel('left', "Gps_Altitude")
        self.gps_longitude_plot.addLegend()
        self.gps_longitude_plot.plot(self.time_axis, self.gps_data_geo_longitude, pen='#4169E1', name="longitude")
        self.gps_longitude_plot.setLabel('bottom', 'time/s')
        self.gps_longitude_plot.setLabel('left', "Gps_Longitude")
        self.gps_latitude_plot.addLegend()
        self.gps_latitude_plot.plot(self.time_axis, self.gps_data_geo_latitude, pen='#4169E1', name="latitude")
        self.gps_latitude_plot.setLabel('bottom', 'time/s')
        self.gps_latitude_plot.setLabel('left', "Gps_Latitude")
        self.gps_velocity_plot.addLegend()
        self.gps_velocity_plot.plot(self.time_axis, self.gps_data_velocity_x_val, pen="#9400D3", name="X")
        self.gps_velocity_plot.plot(self.time_axis, self.gps_data_velocity_y_val, pen="#CD5555", name="Y")
        self.gps_velocity_plot.plot(self.time_axis, self.gps_data_velocity_z_val, pen="#20B2AA", name="Z")
        self.gps_velocity_plot.setLabel('bottom', 'time/s')
        self.gps_velocity_plot.setLabel('left', "Gps_Velocity")

        # magnetometer
        self.magnetometer_data_magnetic_field_body_x_val.append(self.record_magnetometer_data_magnetic_field_body_x_val[self.replay_count])
        self.magnetometer_data_magnetic_field_body_y_val.append(self.record_magnetometer_data_magnetic_field_body_y_val[self.replay_count])
        self.magnetometer_data_magnetic_field_body_z_val.append(self.record_magnetometer_data_magnetic_field_body_z_val[self.replay_count])
        self.magnetometer.addLegend()
        self.magnetometer.plot(self.time_axis, self.magnetometer_data_magnetic_field_body_x_val, pen='#1E90FF',
                               name="X")
        self.magnetometer.plot(self.time_axis, self.magnetometer_data_magnetic_field_body_y_val, pen='#DAA520',
                               name="Y")
        self.magnetometer.plot(self.time_axis, self.magnetometer_data_magnetic_field_body_z_val, pen='#A52A2A',
                               name="Z")
        self.magnetometer.setLabel('bottom', 'time/s')
        self.magnetometer.setLabel('left', "Magnetic_Field_Body")

        # kinematics
        self.kinematics_position_x_val.append(self.record_kinematics_position_x_val[self.replay_count])
        self.kinematics_position_y_val.append(self.record_kinematics_position_y_val[self.replay_count])
        self.kinematics_position_z_val.append(self.record_kinematics_position_z_val[self.replay_count])
        self.kinematics_position_plot.addLegend()
        self.kinematics_position_plot.plot(self.time_axis, self.kinematics_position_x_val, pen='#1E90FF',
                                           name="X")
        self.kinematics_position_plot.plot(self.time_axis, self.kinematics_position_y_val, pen='#DAA520',
                                           name="Y")
        self.kinematics_position_plot.plot(self.time_axis, self.kinematics_position_z_val, pen='#A52A2A',
                                           name="Z")
        self.kinematics_position_plot.setLabel('bottom', 'time/s')
        self.kinematics_position_plot.setLabel('left', "Position")

        self.kinematics_orientation_x_val.append(self.record_kinematics_orientation_x_val[self.replay_count])
        self.kinematics_orientation_y_val.append(self.record_kinematics_orientation_y_val[self.replay_count])
        self.kinematics_orientation_z_val.append(self.record_kinematics_orientation_z_val[self.replay_count])
        self.kinematics_orientation_plot.addLegend()
        self.kinematics_orientation_plot.plot(self.time_axis, self.kinematics_orientation_x_val, pen='#1E90FF',
                                              name="X")
        self.kinematics_orientation_plot.plot(self.time_axis, self.kinematics_orientation_y_val, pen='#DAA520',
                                              name="Y")
        self.kinematics_orientation_plot.plot(self.time_axis, self.kinematics_orientation_z_val, pen='#A52A2A',
                                              name="Z")
        self.kinematics_orientation_plot.setLabel('bottom', 'time/s')
        self.kinematics_orientation_plot.setLabel('left', "Orientation")

        self.kinematics_linear_velocity_x_val.append(self.record_kinematics_linear_velocity_x_val[self.replay_count])
        self.kinematics_linear_velocity_y_val.append(self.record_kinematics_linear_velocity_y_val[self.replay_count])
        self.kinematics_linear_velocity_z_val.append(self.record_kinematics_linear_velocity_z_val[self.replay_count])
        self.kinematics_linear_velocity_plot.addLegend()
        self.kinematics_linear_velocity_plot.plot(self.time_axis, self.kinematics_linear_velocity_x_val,
                                                  pen='#1E90FF',
                                                  name="X")
        self.kinematics_linear_velocity_plot.plot(self.time_axis, self.kinematics_linear_velocity_y_val,
                                                  pen='#DAA520',
                                                  name="Y")
        self.kinematics_linear_velocity_plot.plot(self.time_axis, self.kinematics_linear_velocity_z_val,
                                                  pen='#A52A2A',
                                                  name="Z")
        self.kinematics_linear_velocity_plot.setLabel('bottom', 'time/s')
        self.kinematics_linear_velocity_plot.setLabel('left', "Linear_Velocity")

        self.kinematics_linear_acceleration_x_val.append(self.record_kinematics_linear_acceleration_x_val[self.replay_count])
        self.kinematics_linear_acceleration_y_val.append(self.record_kinematics_linear_acceleration_y_val[self.replay_count])
        self.kinematics_linear_acceleration_z_val.append(self.record_kinematics_linear_acceleration_z_val[self.replay_count])
        self.kinematics_linear_acceleration_plot.addLegend()
        self.kinematics_linear_acceleration_plot.plot(self.time_axis, self.kinematics_linear_acceleration_x_val,
                                                      pen='#1E90FF',
                                                      name="X")
        self.kinematics_linear_acceleration_plot.plot(self.time_axis, self.kinematics_linear_acceleration_y_val,
                                                      pen='#DAA520',
                                                      name="Y")
        self.kinematics_linear_acceleration_plot.plot(self.time_axis, self.kinematics_linear_acceleration_z_val,
                                                      pen='#A52A2A',
                                                      name="Z")
        self.kinematics_linear_acceleration_plot.setLabel('bottom', 'time/s')
        self.kinematics_linear_acceleration_plot.setLabel('left', "Linear_Acceleration")

        self.kinematics_angular_velocity_x_val.append(self.record_kinematics_angular_velocity_x_val[self.replay_count])
        self.kinematics_angular_velocity_y_val.append(self.record_kinematics_angular_velocity_y_val[self.replay_count])
        self.kinematics_angular_velocity_z_val.append(self.record_kinematics_angular_velocity_z_val[self.replay_count])
        self.kinematics_angular_velocity_plot.addLegend()
        self.kinematics_angular_velocity_plot.plot(self.time_axis, self.kinematics_angular_velocity_x_val,
                                                   pen='#1E90FF',
                                                   name="X")
        self.kinematics_angular_velocity_plot.plot(self.time_axis, self.kinematics_angular_velocity_y_val,
                                                   pen='#DAA520',
                                                   name="Y")
        self.kinematics_angular_velocity_plot.plot(self.time_axis, self.kinematics_angular_velocity_z_val,
                                                   pen='#A52A2A',
                                                   name="Z")
        self.kinematics_angular_velocity_plot.setLabel('bottom', 'time/s')
        self.kinematics_angular_velocity_plot.setLabel('left', "Angular_Velocity")

        self.kinematics_angular_acceleration_x_val.append(self.record_kinematics_angular_acceleration_x_val[self.replay_count])
        self.kinematics_angular_acceleration_y_val.append(self.record_kinematics_angular_acceleration_y_val[self.replay_count])
        self.kinematics_angular_acceleration_z_val.append(self.record_kinematics_angular_acceleration_z_val[self.replay_count])
        self.kinematics_angular_acceleration_plot.addLegend()
        self.kinematics_angular_acceleration_plot.plot(self.time_axis, self.kinematics_angular_acceleration_x_val,
                                                       pen='#1E90FF',
                                                       name="X")
        self.kinematics_angular_acceleration_plot.plot(self.time_axis, self.kinematics_angular_acceleration_y_val,
                                                       pen='#DAA520',
                                                       name="Y")
        self.kinematics_angular_acceleration_plot.plot(self.time_axis, self.kinematics_angular_acceleration_z_val,
                                                       pen='#A52A2A',
                                                       name="Z")
        self.kinematics_angular_acceleration_plot.setLabel('bottom', 'time/s')
        self.kinematics_angular_acceleration_plot.setLabel('left', "Angular_Acceleration")


        # environment
        self.environment_data_pressure.append(self.record_environment_data_pressure[self.replay_count])
        self.environment_data_air_density.append(self.record_environment_data_air_density[self.replay_count])
        self.environment_gravity_x_val.append(self.record_environment_gravity_x_val[self.replay_count])
        self.environment_gravity_y_val.append(self.record_environment_gravity_y_val[self.replay_count])
        self.environment_gravity_z_val.append(self.record_environment_gravity_z_val[self.replay_count])
        self.environment_data_temperature.append(self.record_environment_data_temperature[self.replay_count])
        self.environment_pressure_plot.addLegend()
        self.environment_pressure_plot.plot(self.time_axis, self.environment_data_pressure, pen='#9400D3',
                                            name="Pressure")
        self.environment_pressure_plot.setLabel('bottom', 'time/s')
        self.environment_pressure_plot.setLabel('left', "Environment_Pressure")
        self.environment_air_density_plot.addLegend()
        self.environment_air_density_plot.plot(self.time_axis, self.environment_data_air_density, pen='#9400D3',
                                               name="air_density")
        self.environment_air_density_plot.setLabel('bottom', 'time/s')
        self.environment_air_density_plot.setLabel('left', "Environment_Air_Density")
        self.environment_gravity_plot.addLegend()
        self.environment_gravity_plot.plot(self.time_axis, self.environment_gravity_x_val, pen='#1E90FF',
                                           name="X")
        self.environment_gravity_plot.plot(self.time_axis, self.environment_gravity_y_val, pen='#DAA520',
                                           name="Y")
        self.environment_gravity_plot.plot(self.time_axis, self.environment_gravity_z_val, pen='#A52A2A',
                                           name="Z")
        self.environment_gravity_plot.setLabel('bottom', 'time/s')
        self.environment_gravity_plot.setLabel('left', "Environment_Gravity")
        self.environment_temperature_plot.addLegend()
        self.environment_temperature_plot.plot(self.time_axis, self.environment_data_temperature, pen='#9400D3',
                                               name="temperature")
        self.environment_temperature_plot.setLabel('bottom', 'time/s')
        self.environment_temperature_plot.setLabel('left', "Environment_Temperature")

    def showGraphic(self, window, img):
        x = img.shape[1]
        y = img.shape[0]
        ratio = float(y / x)
        width = window.width()-10
        height = window.height()-10
        if(float(height / width) > ratio):
            newx = width
            newy = int(newx * ratio)
        else:
            newy = height
            newx = int(newy / ratio)
        img = cv2.resize(img, (newx, newy))
        frame = QImage(img, newx, newy, QImage.Format_RGB888)
        pix = QPixmap.fromImage(frame)
        item = QGraphicsPixmapItem(pix)
        scene = QGraphicsScene()
        scene.addItem(item)
        window.setScene(scene)
        window.show()
    
    def showGraphic_user(self,img):
        x=img.shape[1]
        y=img.shape[0]
        ratio=float(y/x)
        newx=680
        newy=int(newx*ratio)
        img=cv2.resize(img,(newx,newy))
        frame=QImage(img,newx,newy,QImage.Format_RGB888)
        pix=QPixmap.fromImage(frame)
        item=QGraphicsPixmapItem(pix)
        scene=QGraphicsScene()
        scene.addItem(item)
        self.user_defined_view.setScene(scene)
        self.user_defined_view.show()


    def plot_data(self, datatype, data):

        if datatype == "imu":
            self.imu_data_angular_velocity_x_val.append(float(data.angular_velocity.x_val))
            self.imu_data_angular_velocity_y_val.append(float(data.angular_velocity.y_val))
            self.imu_data_angular_velocity_z_val.append(float(data.angular_velocity.z_val))
            if self.record_flag:
                self.record_imu_data_angular_velocity_x_val.append(float(data.angular_velocity.x_val))
                self.record_imu_data_angular_velocity_y_val.append(float(data.angular_velocity.y_val))
                self.record_imu_data_angular_velocity_z_val.append(float(data.angular_velocity.z_val))

            self.imu_angular_plot.addLegend()
            self.imu_angular_plot.plot(self.time_axis, self.imu_data_angular_velocity_x_val, pen="#9400D3", name="X")
            self.imu_angular_plot.plot(self.time_axis, self.imu_data_angular_velocity_y_val, pen="#CD5555", name="Y")
            self.imu_angular_plot.plot(self.time_axis, self.imu_data_angular_velocity_z_val, pen="#20B2AA", name="Z")
            self.imu_angular_plot.setLabel('bottom', "time/s")
            self.imu_angular_plot.setLabel('left', "Angular_Velocity")

            self.imu_data_linear_acceleration_x_val.append(float(data.linear_acceleration.x_val))
            self.imu_data_linear_acceleration_y_val.append(float(data.linear_acceleration.y_val))
            self.imu_data_linear_acceleration_z_val.append(float(data.linear_acceleration.z_val))
            if self.record_flag:
                self.record_imu_data_linear_acceleration_x_val.append(float(data.linear_acceleration.x_val))
                self.record_imu_data_linear_acceleration_y_val.append(float(data.linear_acceleration.y_val))
                self.record_imu_data_linear_acceleration_z_val.append(float(data.linear_acceleration.z_val))

            self.imu_linear_plot.addLegend()
            self.imu_linear_plot.plot(self.time_axis, self.imu_data_linear_acceleration_x_val, pen="#9400D3", name="X")
            self.imu_linear_plot.plot(self.time_axis, self.imu_data_linear_acceleration_y_val, pen="#CD5555", name="Y")
            self.imu_linear_plot.plot(self.time_axis, self.imu_data_linear_acceleration_z_val, pen="#20B2AA", name="Z")
            self.imu_linear_plot.setLabel('bottom', "time/s")
            self.imu_linear_plot.setLabel('left', "Linear_Acceleration")

            self.imu_data_orientation_x_val.append(float(data.orientation.x_val))
            self.imu_data_orientation_y_val.append(float(data.orientation.y_val))
            self.imu_data_orientation_z_val.append(float(data.orientation.z_val))
            self.imu_data_orientation_w_val.append(float(data.orientation.w_val))
            if self.record_flag:
                self.record_imu_data_orientation_x_val.append(float(data.orientation.x_val))
                self.record_imu_data_orientation_y_val.append(float(data.orientation.y_val))
                self.record_imu_data_orientation_z_val.append(float(data.orientation.z_val))
                self.record_imu_data_orientation_w_val.append(float(data.orientation.w_val))

            self.imu_orientation_plot.addLegend()
            self.imu_orientation_plot.plot(self.time_axis, self.imu_data_orientation_x_val, pen="#9400D3", name="X")
            self.imu_orientation_plot.plot(self.time_axis, self.imu_data_orientation_y_val, pen="#CD5555", name="Y")
            self.imu_orientation_plot.plot(self.time_axis, self.imu_data_orientation_z_val, pen="#20B2AA", name="Z")
            self.imu_orientation_plot.plot(self.time_axis, self.imu_data_orientation_w_val, pen="red", name="O_W")
            self.imu_orientation_plot.setLabel('bottom', "time/s")
            self.imu_orientation_plot.setLabel('left', "Orientation")

        elif datatype == "barometer":
            self.barometer_data_pressure.append(float(data.pressure))
            self.barometer_data_altitude.append(float(data.altitude))
            self.barometer_data_qnh.append(float(data.qnh))
            if self.record_flag:
                self.record_barometer_data_pressure.append(float(data.pressure))
                self.record_barometer_data_altitude.append(float(data.altitude))
                self.record_barometer_data_qnh.append(float(data.qnh))

            self.barometer_pressure_plot.addLegend()
            self.barometer_pressure_plot.plot(self.time_axis, self.barometer_data_pressure, pen='#9400D3',
                                              name="Pressure")
            self.barometer_pressure_plot.setLabel('bottom', 'time/s')
            self.barometer_pressure_plot.setLabel('left', "Barometer_Pressure")

            self.barometer_altitude_plot.addLegend()
            self.barometer_altitude_plot.plot(self.time_axis, self.barometer_data_altitude, pen='#9400D3',
                                              name="Altitude")
            self.barometer_altitude_plot.setLabel('bottom', 'time/s')
            self.barometer_altitude_plot.setLabel('left', "Barometer_Altitude")

            self.barometer_qnh_plot.addLegend()
            self.barometer_qnh_plot.plot(self.time_axis, self.barometer_data_qnh, pen='#9400D3',
                                              name="Qnh")
            self.barometer_qnh_plot.setLabel('bottom', 'time/s')
            self.barometer_qnh_plot.setLabel('left', "Barometer_Qnh")

        elif datatype == "gps":
            self.gps_data_geo_latitude.append(data.gnss.geo_point.latitude)
            self.gps_data_geo_longitude.append(data.gnss.geo_point.longitude)
            self.gps_data_geo_altitude.append(data.gnss.geo_point.altitude)
            self.gps_data_velocity_x_val.append(data.gnss.velocity.x_val)
            self.gps_data_velocity_y_val.append(data.gnss.velocity.y_val)
            self.gps_data_velocity_z_val.append(data.gnss.velocity.z_val)
            if self.record_flag:
                self.record_gps_data_geo_latitude.append(data.gnss.geo_point.latitude)
                self.record_gps_data_geo_longitude.append(data.gnss.geo_point.longitude)
                self.record_gps_data_geo_altitude.append(data.gnss.geo_point.altitude)
                self.record_gps_data_velocity_x_val.append(data.gnss.velocity.x_val)
                self.record_gps_data_velocity_y_val.append(data.gnss.velocity.y_val)
                self.record_gps_data_velocity_z_val.append(data.gnss.velocity.z_val)

            self.gps_altitude_plot.addLegend()
            self.gps_altitude_plot.plot(self.time_axis, self.gps_data_geo_altitude, pen='#4169E1', name="altitude")
            self.gps_altitude_plot.setLabel('bottom', 'time/s')
            self.gps_altitude_plot.setLabel('left', "Gps_Altitude")

            self.gps_longitude_plot.addLegend()
            self.gps_longitude_plot.plot(self.time_axis, self.gps_data_geo_longitude, pen='#4169E1', name="longitude")
            self.gps_longitude_plot.setLabel('bottom', 'time/s')
            self.gps_longitude_plot.setLabel('left', "Gps_Longitude")

            self.gps_latitude_plot.addLegend()
            self.gps_latitude_plot.plot(self.time_axis, self.gps_data_geo_latitude, pen='#4169E1', name="latitude")
            self.gps_latitude_plot.setLabel('bottom', 'time/s')
            self.gps_latitude_plot.setLabel('left', "Gps_Latitude")

            self.gps_velocity_plot.addLegend()
            self.gps_velocity_plot.plot(self.time_axis, self.gps_data_velocity_x_val, pen="#9400D3", name="X")
            self.gps_velocity_plot.plot(self.time_axis, self.gps_data_velocity_y_val, pen="#CD5555", name="Y")
            self.gps_velocity_plot.plot(self.time_axis, self.gps_data_velocity_z_val, pen="#20B2AA", name="Z")
            self.gps_velocity_plot.setLabel('bottom', 'time/s')
            self.gps_velocity_plot.setLabel('left', "Gps_Velocity")

        elif datatype == "magnetometer":
            self.magnetometer_data_magnetic_field_body_x_val.append(data.magnetic_field_body.x_val)
            self.magnetometer_data_magnetic_field_body_y_val.append(data.magnetic_field_body.y_val)
            self.magnetometer_data_magnetic_field_body_z_val.append(data.magnetic_field_body.z_val)
            if self.record_flag:
                self.record_magnetometer_data_magnetic_field_body_x_val.append(data.magnetic_field_body.x_val)
                self.record_magnetometer_data_magnetic_field_body_y_val.append(data.magnetic_field_body.y_val)
                self.record_magnetometer_data_magnetic_field_body_z_val.append(data.magnetic_field_body.z_val)

            self.magnetometer.addLegend()
            self.magnetometer.plot(self.time_axis, self.magnetometer_data_magnetic_field_body_x_val, pen='#1E90FF',
                                   name="X")
            self.magnetometer.plot(self.time_axis, self.magnetometer_data_magnetic_field_body_y_val, pen='#DAA520',
                                   name="Y")
            self.magnetometer.plot(self.time_axis, self.magnetometer_data_magnetic_field_body_z_val, pen='#A52A2A',
                                   name="Z")
            self.magnetometer.setLabel('bottom', 'time/s')
            self.magnetometer.setLabel('left', "Magnetic_Field_Body")

        elif datatype == "kinematics":
            self.kinematics_position_x_val.append(data.position.x_val)
            self.kinematics_position_y_val.append(data.position.y_val)
            self.kinematics_position_z_val.append(data.position.z_val)
            if self.record_flag:
                self.record_kinematics_position_x_val.append(data.position.x_val)
                self.record_kinematics_position_y_val.append(data.position.y_val)
                self.record_kinematics_position_z_val.append(data.position.z_val)

            self.kinematics_position_plot.addLegend()
            self.kinematics_position_plot.plot(self.time_axis, self.kinematics_position_x_val, pen='#1E90FF',
                                   name="X")
            self.kinematics_position_plot.plot(self.time_axis, self.kinematics_position_y_val, pen='#DAA520',
                                   name="Y")
            self.kinematics_position_plot.plot(self.time_axis, self.kinematics_position_z_val, pen='#A52A2A',
                                   name="Z")
            self.kinematics_position_plot.setLabel('bottom', 'time/s')
            self.kinematics_position_plot.setLabel('left', "Position")

            self.kinematics_orientation_x_val.append(data.orientation.x_val)
            self.kinematics_orientation_y_val.append(data.orientation.y_val)
            self.kinematics_orientation_z_val.append(data.orientation.z_val)
            if self.record_flag:
                self.record_kinematics_orientation_x_val.append(data.orientation.x_val)
                self.record_kinematics_orientation_y_val.append(data.orientation.y_val)
                self.record_kinematics_orientation_z_val.append(data.orientation.z_val)

            self.kinematics_orientation_plot.addLegend()
            self.kinematics_orientation_plot.plot(self.time_axis, self.kinematics_orientation_x_val, pen='#1E90FF',
                                               name="X")
            self.kinematics_orientation_plot.plot(self.time_axis, self.kinematics_orientation_y_val, pen='#DAA520',
                                               name="Y")
            self.kinematics_orientation_plot.plot(self.time_axis, self.kinematics_orientation_z_val, pen='#A52A2A',
                                               name="Z")
            self.kinematics_orientation_plot.setLabel('bottom', 'time/s')
            self.kinematics_orientation_plot.setLabel('left', "Orientation")

            self.kinematics_linear_velocity_x_val.append(data.linear_velocity.x_val)
            self.kinematics_linear_velocity_y_val.append(data.linear_velocity.y_val)
            self.kinematics_linear_velocity_z_val.append(data.linear_velocity.z_val)
            if self.record_flag:
                self.record_kinematics_linear_velocity_x_val.append(data.linear_velocity.x_val)
                self.record_kinematics_linear_velocity_y_val.append(data.linear_velocity.y_val)
                self.record_kinematics_linear_velocity_z_val.append(data.linear_velocity.z_val)

            self.kinematics_linear_velocity_plot.addLegend()
            self.kinematics_linear_velocity_plot.plot(self.time_axis, self.kinematics_linear_velocity_x_val, pen='#1E90FF',
                                   name="X")
            self.kinematics_linear_velocity_plot.plot(self.time_axis, self.kinematics_linear_velocity_y_val, pen='#DAA520',
                                   name="Y")
            self.kinematics_linear_velocity_plot.plot(self.time_axis, self.kinematics_linear_velocity_z_val, pen='#A52A2A',
                                   name="Z")
            self.kinematics_linear_velocity_plot.setLabel('bottom', 'time/s')
            self.kinematics_linear_velocity_plot.setLabel('left', "Linear_Velocity")

            self.kinematics_linear_acceleration_x_val.append(data.linear_acceleration.x_val)
            self.kinematics_linear_acceleration_y_val.append(data.linear_acceleration.y_val)
            self.kinematics_linear_acceleration_z_val.append(data.linear_acceleration.z_val)
            if self.record_flag:
                self.record_kinematics_linear_acceleration_x_val.append(data.linear_acceleration.x_val)
                self.record_kinematics_linear_acceleration_y_val.append(data.linear_acceleration.y_val)
                self.record_kinematics_linear_acceleration_z_val.append(data.linear_acceleration.z_val)

            self.kinematics_linear_acceleration_plot.addLegend()
            self.kinematics_linear_acceleration_plot.plot(self.time_axis, self.kinematics_linear_acceleration_x_val, pen='#1E90FF',
                                   name="X")
            self.kinematics_linear_acceleration_plot.plot(self.time_axis, self.kinematics_linear_acceleration_y_val, pen='#DAA520',
                                   name="Y")
            self.kinematics_linear_acceleration_plot.plot(self.time_axis, self.kinematics_linear_acceleration_z_val, pen='#A52A2A',
                                   name="Z")
            self.kinematics_linear_acceleration_plot.setLabel('bottom', 'time/s')
            self.kinematics_linear_acceleration_plot.setLabel('left', "Linear_Acceleration")

            self.kinematics_angular_velocity_x_val.append(data.angular_velocity.x_val)
            self.kinematics_angular_velocity_y_val.append(data.angular_velocity.y_val)
            self.kinematics_angular_velocity_z_val.append(data.angular_velocity.z_val)
            if self.record_flag:
                self.record_kinematics_angular_velocity_x_val.append(data.angular_velocity.x_val)
                self.record_kinematics_angular_velocity_y_val.append(data.angular_velocity.y_val)
                self.record_kinematics_angular_velocity_z_val.append(data.angular_velocity.z_val)

            self.kinematics_angular_velocity_plot.addLegend()
            self.kinematics_angular_velocity_plot.plot(self.time_axis, self.kinematics_angular_velocity_x_val, pen='#1E90FF',
                                   name="X")
            self.kinematics_angular_velocity_plot.plot(self.time_axis, self.kinematics_angular_velocity_y_val, pen='#DAA520',
                                   name="Y")
            self.kinematics_angular_velocity_plot.plot(self.time_axis, self.kinematics_angular_velocity_z_val, pen='#A52A2A',
                                   name="Z")
            self.kinematics_angular_velocity_plot.setLabel('bottom', 'time/s')
            self.kinematics_angular_velocity_plot.setLabel('left', "Angular_Velocity")

            self.kinematics_angular_acceleration_x_val.append(data.angular_acceleration.x_val)
            self.kinematics_angular_acceleration_y_val.append(data.angular_acceleration.y_val)
            self.kinematics_angular_acceleration_z_val.append(data.angular_acceleration.z_val)
            if self.record_flag:
                self.record_kinematics_angular_acceleration_x_val.append(data.angular_acceleration.x_val)
                self.record_kinematics_angular_acceleration_y_val.append(data.angular_acceleration.y_val)
                self.record_kinematics_angular_acceleration_z_val.append(data.angular_acceleration.z_val)

            self.kinematics_angular_acceleration_plot.addLegend()
            self.kinematics_angular_acceleration_plot.plot(self.time_axis, self.kinematics_angular_acceleration_x_val, pen='#1E90FF',
                                   name="X")
            self.kinematics_angular_acceleration_plot.plot(self.time_axis, self.kinematics_angular_acceleration_y_val, pen='#DAA520',
                                   name="Y")
            self.kinematics_angular_acceleration_plot.plot(self.time_axis, self.kinematics_angular_acceleration_z_val, pen='#A52A2A',
                                   name="Z")
            self.kinematics_angular_acceleration_plot.setLabel('bottom', 'time/s')
            self.kinematics_angular_acceleration_plot.setLabel('left', "Angular_Acceleration")

        elif datatype == "environment":
            
            self.environment_data_pressure.append(float(data.air_pressure))
            self.environment_data_air_density.append(float(data.air_density))
            self.environment_gravity_x_val.append(data.gravity.x_val)
            self.environment_gravity_y_val.append(data.gravity.y_val)
            self.environment_gravity_z_val.append(data.gravity.z_val)
            self.environment_data_temperature.append(float(data.temperature))
            if self.record_flag:
                self.record_environment_data_pressure.append(float(data.air_pressure))
                self.record_environment_data_air_density.append(float(data.air_density))
                self.record_environment_gravity_x_val.append(data.gravity.x_val)
                self.record_environment_gravity_y_val.append(data.gravity.y_val)
                self.record_environment_gravity_z_val.append(data.gravity.z_val)
                self.record_environment_data_temperature.append(float(data.temperature))

            self.environment_pressure_plot.addLegend()
            self.environment_pressure_plot.plot(self.time_axis, self.environment_data_pressure, pen='#9400D3',
                                              name="Pressure")
            self.environment_pressure_plot.setLabel('bottom', 'time/s')
            self.environment_pressure_plot.setLabel('left', "Environment_Pressure")

            self.environment_air_density_plot.addLegend()
            self.environment_air_density_plot.plot(self.time_axis, self.environment_data_air_density, pen='#9400D3',
                                                name="air_density")
            self.environment_air_density_plot.setLabel('bottom', 'time/s')
            self.environment_air_density_plot.setLabel('left', "Environment_Air_Density")

            self.environment_gravity_plot.addLegend()
            self.environment_gravity_plot.plot(self.time_axis, self.environment_gravity_x_val, pen='#1E90FF',
                                   name="X")
            self.environment_gravity_plot.plot(self.time_axis, self.environment_gravity_y_val, pen='#DAA520',
                                   name="Y")
            self.environment_gravity_plot.plot(self.time_axis, self.environment_gravity_z_val, pen='#A52A2A',
                                   name="Z")
            self.environment_gravity_plot.setLabel('bottom', 'time/s')
            self.environment_gravity_plot.setLabel('left', "Environment_Gravity")

            
            self.environment_temperature_plot.addLegend()
            self.environment_temperature_plot.plot(self.time_axis, self.environment_data_temperature, pen='#9400D3',
                                                name="temperature")
            self.environment_temperature_plot.setLabel('bottom', 'time/s')
            self.environment_temperature_plot.setLabel('left', "Environment_Temperature")

    def closeEvent(self, event):
        """
        closeEvent _summary_

        Args:
            event: _description_
        """
        reply = QtWidgets.QMessageBox.question(self,
                                               'Attention',
                                               "you do want to exit ?",
                                               QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No,
                                               QtWidgets.QMessageBox.No)
        if reply == QtWidgets.QMessageBox.Yes:
            event.accept()
            self.end_task()


        else:
            event.ignore()














