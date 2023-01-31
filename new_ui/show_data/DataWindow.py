from new_ui.show_data.Ui_Data_Window import Ui_DataWindow
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QMainWindow, QMessageBox
from PyQt5.QtCore import QTimer
import airsim
import cv2
from PyQt5.QtWidgets import QApplication, QGraphicsView, QMessageBox, QGraphicsScene, QGraphicsPixmapItem
from PyQt5.QtGui import QPixmap, QImage
import os
import SPBA_API
import threading
from SPBA_API import Multirotor
from new_ui.controller.keyboard_controler import keyboard_control




class DataWindow(QMainWindow, Ui_DataWindow):
    """
    MysensorWindow : show the sensor data and world camera scene.But,there is caton problem at present.Maybe it can be solved by delayed time processing--
                     catch hundreds of images befor show the window and upgrade the images in the cache constantly.

    """

    def __init__(self, SharedData, parent=None):
        self.SharedData = SharedData
        super(DataWindow, self).__init__(parent)
        self.setupUi(self)
        self.Multirotor = Multirotor(self.SharedData)
        self.set_myUI()

        # self.init_airsim()
        self.init_timer()

    def set_myUI(self):
        self.route_button.clicked.connect(self.route)
        self.KeyboardCtrl_start.clicked.connect(self.keyboard_controler)

    def keyboard_controler(self):
        keyboard_thread = threading.Thread(target=self.Multirotor.FlightControl.keyboard_control)
        keyboard_thread.start()

    def route(self):
        if self.route_choose.currentText() == '0形路径':
            self.Multirotor.LQR_fly('0')
        elif self.route_choose.currentText() == '8形路径':
            self.Multirotor.LQR_fly('8')

    def init_timer(self):
        self.sensor_data_interval = QTimer(self)
        self.sensor_data_interval.timeout.connect(self.time_out)
        self.time_interval = 40
        self.sensor_data_interval.start(self.time_interval)
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

    def release_airsim(self):
        del self.Multirotor
        self.sensor_data_interval.stop()

    def time_out(self):
        self.Multirotor.GroundTruth.update()
        self.show_all_data()

    def time_count(self):

        if len(self.time_axis) == 0:
            self.time_axis.append(self.time_interval / 1000)
        else:
            self.time_axis.append(self.time_axis[-1] + self.time_interval / 1000)

    def data_clear(self):
        """
        data_clear : the datas have to be cleared before show them again
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

    def show_all_data(self):
        self.data_clear()
        imu_data = self.Multirotor.GroundTruth.ImuData
        barometer_data = self.Multirotor.GroundTruth.BarometerData
        magnetometer_data = self.Multirotor.GroundTruth.MagnetometerData
        gps_data = self.Multirotor.GroundTruth.GpsData
        kinematics_data = self.Multirotor.GroundTruth.KinematicsState
        environment_data = self.Multirotor.GroundTruth.EnvironmentState
        front_center_img = main_view_img = self.Multirotor.GroundTruth.CameraImages[0]
        front_left_img = self.Multirotor.GroundTruth.CameraImages[1]
        front_right_img = self.Multirotor.GroundTruth.CameraImages[2]
        bottom_center_img = self.Multirotor.GroundTruth.CameraImages[3]
        back_center_img = self.Multirotor.GroundTruth.CameraImages[4]
        user_defined_img = self.Multirotor.GroundTruth.CameraImages[5]
        self.time_count()
        self.plot_data("imu", imu_data)
        self.plot_data("barometer", barometer_data)
        self.plot_data("gps", gps_data)
        self.plot_data("magnetometer", magnetometer_data)
        self.plot_data("kinematics", kinematics_data)
        self.plot_data("environment", environment_data)


        self.showGraphic(self.user_defined_view, main_view_img)

        # self.showGraphic(self.front_center_view, front_center_img)
        self.showGraphic(self.front_left_view, front_left_img)
        self.showGraphic(self.front_right_view, front_right_img)
        self.showGraphic(self.bottom_center_view, bottom_center_img)
        self.showGraphic(self.back_center_view, back_center_img)

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

    def plot_data(self, datatype, data):

        if datatype == "imu":
            self.imu_data_angular_velocity_x_val.append(float(data.angular_velocity.x_val))
            self.imu_data_angular_velocity_y_val.append(float(data.angular_velocity.y_val))
            self.imu_data_angular_velocity_z_val.append(float(data.angular_velocity.z_val))

            self.imu_angular_plot.addLegend()
            self.imu_angular_plot.plot(self.time_axis, self.imu_data_angular_velocity_x_val, pen="#9400D3", name="X")
            self.imu_angular_plot.plot(self.time_axis, self.imu_data_angular_velocity_y_val, pen="#CD5555", name="Y")
            self.imu_angular_plot.plot(self.time_axis, self.imu_data_angular_velocity_z_val, pen="#20B2AA", name="Z")
            self.imu_angular_plot.setLabel('bottom', "time/s")
            self.imu_angular_plot.setLabel('left', "Angular_Velocity")

            self.imu_data_linear_acceleration_x_val.append(float(data.linear_acceleration.x_val))
            self.imu_data_linear_acceleration_y_val.append(float(data.linear_acceleration.y_val))
            self.imu_data_linear_acceleration_z_val.append(float(data.linear_acceleration.z_val))

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
            self.environment_pressure_plot.addLegend()
            self.environment_pressure_plot.plot(self.time_axis, self.environment_data_pressure, pen='#9400D3',
                                              name="Pressure")
            self.environment_pressure_plot.setLabel('bottom', 'time/s')
            self.environment_pressure_plot.setLabel('left', "Environment_Pressure")

            self.environment_data_air_density.append(float(data.air_density))
            self.environment_air_density_plot.addLegend()
            self.environment_air_density_plot.plot(self.time_axis, self.environment_data_air_density, pen='#9400D3',
                                                name="air_density")
            self.environment_air_density_plot.setLabel('bottom', 'time/s')
            self.environment_air_density_plot.setLabel('left', "Environment_Air_Density")

            self.environment_gravity_x_val.append(data.gravity.x_val)
            self.environment_gravity_y_val.append(data.gravity.y_val)
            self.environment_gravity_z_val.append(data.gravity.z_val)
            self.environment_gravity_plot.addLegend()
            self.environment_gravity_plot.plot(self.time_axis, self.environment_gravity_x_val, pen='#1E90FF',
                                   name="X")
            self.environment_gravity_plot.plot(self.time_axis, self.environment_gravity_y_val, pen='#DAA520',
                                   name="Y")
            self.environment_gravity_plot.plot(self.time_axis, self.environment_gravity_z_val, pen='#A52A2A',
                                   name="Z")
            self.environment_gravity_plot.setLabel('bottom', 'time/s')
            self.environment_gravity_plot.setLabel('left', "Environment_Gravity")

            
            self.environment_data_temperature.append(float(data.temperature))
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
            self.release_airsim()


        else:
            event.ignore()














