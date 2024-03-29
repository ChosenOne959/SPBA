from Realtime.Ui_realtime_sensorData import Ui_sensorData
from PyQt5 import QtWidgets
from PyQt5.QtCore import QTimer 
import airsim
import cv2
from PyQt5.QtWidgets import QApplication,QGraphicsView,QMessageBox, QGraphicsScene, QGraphicsPixmapItem
from PyQt5.QtGui import QPixmap,QImage
import os
import numpy as np
from Work_Place import global_value
import new_ui.SPBA_API as SPBA

class MysensorWindow(QtWidgets.QWidget,Ui_sensorData):
    """
    MysensorWindow : show the sensor data and world camera scene.But,there is caton problem at present.Maybe it can be solved by delayed time processing--
                     catch hundreds of images befor show the window and upgrade the images in the cache constantly.

    """
    def __init__(self,parent=None):
        super(MysensorWindow,self).__init__(parent)
        self.setupUi(self)
        self.init_airsim()
        self.init_timer()
    
    def init_timer(self):
        self.sensor_data_interval=QTimer(self)
        self.sensor_data_interval.timeout.connect(self.time_out)
        self.time_interval=20
        self.sensor_data_interval.start(self.time_interval)
        self.time_axis=[]
        self.imu_data_angular_velocity_x_val=[]
        self.imu_data_angular_velocity_y_val=[]
        self.imu_data_angular_velocity_z_val=[]
        self.imu_data_linear_acceleration_x_val=[]
        self.imu_data_linear_acceleration_y_val=[]
        self.imu_data_linear_acceleration_z_val=[]
        self.barometer_data_pressure=[]
        self.barometer_data_altitude=[]
        self.barometer_data_qnh=[]
        self.gps_data_geo_latitude=[]
        self.gps_data_geo_longitude=[]
        self.gps_data_geo_altitude=[]
        self.magnetometer_data_magnetic_field_body_x_val=[]
        self.magnetometer_data_magnetic_field_body_y_val=[]
        self.magnetometer_data_magnetic_field_body_z_val=[]

    

    
    def init_airsim(self):
        # note that self.drone should be the only instance of SPBA.Multirotor class
        self.drone = SPBA.Multirotor(is_localhost=global_value.is_localhost)
        # self.airsim_settings_config()
        self.recording_flag = 0;
        

    def release_airsim(self):
        del self.drone
        self.sensor_data_interval.stop()

    def time_out(self):
        self.data_clear()
        self.start_getSensor_data()
        self.recording_control()
       
    def recording_control(self):
        if self.radioButton.isChecked() == True and self.recording_flag == 0:
            self.drone.client.startRecording()
            self.recording_flag = 1;    
        elif self.recording_flag == 1 and self.radioButton.isChecked() == False:
            self.drone.client.stopRecording()
            self.recording_flag = 0;
        else:
            pass
        
    def time_count(self):

        if len(self.time_axis)==0:
            self.time_axis.append(self.time_interval/1000)
        else:
            self.time_axis.append(self.time_axis[-1]+self.time_interval/1000)

    def data_clear(self):
        """
        data_clear : the datas have to be cleared before show them again
        """
        self.imu_angular.clear()
        self.barometer.clear()
        self.imu_linear.clear()
        self.gps_geo.clear()
        self.magnetometer.clear()

    def airsim_settings_config(self):
        """
        need path of settings.json
        better input in Setting_Path window
        still requires some work todo
        :return:
        """
        PATH = 'C:/Users/huyutong2020/Documents/AirSim/settings.json'
        settings = SPBA.AirSimSettings(PATH)
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

    def start_getSensor_data(self):
        """
        start_getSensor_data : display the different kinds of data obtained by the sensor api.In order to display the scene in unreal
                               in realtime,a new camera need to be added in the arisim setting file:
        further : this content should can  be added by our SBPA app
                               *******************************
                                "Cameras": {
                                            "Mycamera": {
                                            "X": -2,
                                            "Y": 0,
                                            "Z": -2,
                                            "Pitch": -45,
                                            "Roll": 0,
                                            "Yaw": 0,
                                            
                                            "CaptureSettings": [
                                                {
                                                "ImageType": 0,
                                                "Width": 780,
                                                "Height": 520,
                                                "FOV_Degrees": 90,
                                                "AutoExposureSpeed": 100,
                                                "AutoExposureBias": 0,
                                                "AutoExposureMaxBrightness": 0.64,
                                                "AutoExposureMinBrightness": 0.03,
                                                "MotionBlurAmount": 0,
                                                "TargetGamma": 1.0,
                                                "ProjectionMode": "",
                                                "OrthoWidth": 5.12
                                                }
                                            ],
                                            "Gimbal": {
                                                "Stabilization": 0
                                            }
                                            }
                                            
                                        } 

                               ******************************* 

        """ 
        # imu_data=self.drone.GroundTruth.ImuData
        # barometer_data=self.drone.GroundTruth.BarometerData
        # magnetometer_data=self.drone.GroundTruth.MagnetometerData
        # gps_data=self.drone.GroundTruth.GpsData
        # img = self.drone.GroundTruth.CameraImages[5]
        # self.time_count()
        # self.plot_sensor_data("imu",imu_data)
        # self.plot_sensor_data("barometer",barometer_data)
        # self.plot_sensor_data("gps",gps_data)
        # self.plot_sensor_data("magnetometer",magnetometer_data)
        # self.showGraphic(img)
        imu_data=self.drone.client.getImuData()
        barometer_data=self.drone.client.getBarometerData()
        magnetometer_data=self.drone.client.getMagnetometerData()
        gps_data=self.drone.client.getGpsData()
        response = self.drone.client.simGetImages([airsim.ImageRequest('Mycamera', airsim.ImageType.Scene)])
        img_buffer_numpy = np.frombuffer(response[0].image_data_uint8, dtype=np.uint8)
        img = cv2.imdecode(img_buffer_numpy, 1)  # 从指定的内存缓存中读取一维numpy数据，并把数据转换(解码)成图像矩阵格式
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        self.time_count()
        self.plot_sensor_data("imu",imu_data)
        self.plot_sensor_data("barometer",barometer_data)
        self.plot_sensor_data("gps",gps_data)
        self.plot_sensor_data("magnetometer",magnetometer_data)
        self.showGraphic(img)

    
    # def showGraphic(self,img):
    #     x=img.shape[1]
    #     y=img.shape[0]
    #     ratio=float(y/x)
    #     newx=780
    #     newy=int(newx*ratio)
    #     img=cv2.resize(img,(newx,newy))
    #     frame=QImage(img,newx,newy,QImage.Format_RGB888)
    #     pix=QPixmap.fromImage(frame)
    #     item=QGraphicsPixmapItem(pix)
    #     scene=QGraphicsScene()
    #     scene.addItem(item)
    #     self.Main_View.setScene(scene)
    #     self.Main_View.show()

    def showGraphic(self,img):
        x=img.shape[1]
        y=img.shape[0]
        ratio=float(y/x)
        newx=780
        newy=int(newx*ratio)
        img=cv2.resize(img,(newx,newy))
        frame=QImage(img,newx,newy,QImage.Format_RGB888)
        pix=QPixmap.fromImage(frame)
        item=QGraphicsPixmapItem(pix)
        scene=QGraphicsScene()
        scene.addItem(item)
        self.Main_View.setScene(scene)
        self.Main_View.show()

    def plot_sensor_data(self,datatype,data):

        if datatype=="imu":
            
            self.imu_data_angular_velocity_x_val.append(float(data.angular_velocity.x_val))
            self.imu_data_angular_velocity_y_val.append(float(data.angular_velocity.y_val))
            self.imu_data_angular_velocity_z_val.append(float(data.angular_velocity.z_val))
            
            self.imu_angular.addLegend()
            self.imu_angular.plot(self.time_axis,self.imu_data_angular_velocity_x_val,pen="#9400D3",name="AV_X")
            self.imu_angular.plot(self.time_axis,self.imu_data_angular_velocity_y_val,pen="#CD5555",name="AV_Y")
            self.imu_angular.plot(self.time_axis,self.imu_data_angular_velocity_z_val,pen="#20B2AA",name="AV_Z")
            self.imu_angular.setLabel('bottom',"time/s")
            self.imu_angular.setLabel('left',"Angular_Velocity")

            self.imu_data_linear_acceleration_x_val.append(float(data.linear_acceleration.x_val))
            self.imu_data_linear_acceleration_y_val.append(float(data.linear_acceleration.y_val))
            self.imu_data_linear_acceleration_z_val.append(float(data.linear_acceleration.z_val))

            self.imu_linear.addLegend()
            self.imu_linear.plot(self.time_axis,self.imu_data_angular_velocity_x_val,pen="#9400D3",name="LA_X")
            self.imu_linear.plot(self.time_axis,self.imu_data_angular_velocity_y_val,pen="#CD5555",name="LA_Y")
            self.imu_linear.plot(self.time_axis,self.imu_data_angular_velocity_z_val,pen="#20B2AA",name="LA_Z")
            self.imu_linear.setLabel('bottom',"time/s")
            self.imu_linear.setLabel('left',"Linear_Acceleration")

        
        if datatype=="barometer":

            self.barometer_data_pressure.append(float(data.pressure))
            self.barometer_data_altitude.append(float(data.altitude))
            self.barometer_data_qnh.append(float(data.qnh))
            self.barometer.addLegend()
            self.barometer.plot(self.time_axis,self.barometer_data_pressure,pen='#9400D3',name="Pressure")
            self.barometer.plot(self.time_axis,self.barometer_data_altitude,pen='#DCDCDC',name="Altitude")
            self.barometer.plot(self.time_axis,self.barometer_data_qnh,pen='#FF4500',name="QNH")
            self.barometer.setLabel('bottom','time/s')
            self.barometer.setLabel('left',"Barometer")
        
        if datatype=="gps":

            self.gps_data_geo_latitude.append(data.gnss.geo_point.latitude)
            self.gps_data_geo_longitude.append(data.gnss.geo_point.longitude)
            self.gps_data_geo_altitude.append(data.gnss.geo_point.altitude)
            self.gps_geo.addLegend()
            self.gps_geo.plot(self.time_axis,self.gps_data_geo_altitude,pen='#4169E1',name="altitude")
            self.gps_geo.plot(self.time_axis,self.gps_data_geo_longitude,pen='#32CD32',name="longitude")
            self.gps_geo.plot(self.time_axis,self.gps_data_geo_latitude,pen='#FF4500',name="latitude")
            self.gps_geo.setLabel('bottom','time/s')
            self.gps_geo.setLabel('left',"Gps_Geo")
        
        if datatype=="magnetometer":

            self.magnetometer_data_magnetic_field_body_x_val.append(data.magnetic_field_body.x_val)
            self.magnetometer_data_magnetic_field_body_y_val.append(data.magnetic_field_body.y_val)
            self.magnetometer_data_magnetic_field_body_z_val.append(data.magnetic_field_body.z_val)
            self.magnetometer.addLegend()
            self.magnetometer.plot(self.time_axis,self.magnetometer_data_magnetic_field_body_x_val,pen='#1E90FF',name="MFB_X")
            self.magnetometer.plot(self.time_axis,self.magnetometer_data_magnetic_field_body_y_val,pen='#DAA520',name="MFB_Y")
            self.magnetometer.plot(self.time_axis,self.magnetometer_data_magnetic_field_body_z_val,pen='#A52A2A',name="MFB_Z")

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
            

            

        


            






