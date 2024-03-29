from typing import Any

import msgpackrpc.error
import keyboard

from new_ui.RPC import RPC_client as RPC_client
from new_ui.RPC import RPC_server as RPC_server

import airsim
import numpy as np
import math
import time
from scipy import linalg
import json
import threading
import cv2
import re

nan = float("nan")
remote_host = '202.120.37.157'

# used to control all the windows and transmit data between windows
class SharedData:
    def __init__(self):
        self.WindowSeries = []   # a stack to store windows
        self.is_localhost = True
        self.configurefile_path = './configuration_file.json'
        self.configure_data = {'path': {}}
        self.resources = {}
        self.Vehicle_Type = 0     #0 represents Multirotor type
        self.param_data = self.init_param_data()
        self.lock = threading.Lock()    # 控制airsimAPI资源访问的锁
        

    @staticmethod
    def init_param_data():
        param_data = {'Rotor_params': {'Thrust': {'Name': 'C_T'}, 'Torque': {'Name': 'C_P'}, 'Air': {'Name': 'air_density'}, 'Revolutions': {'Name': 'max_rpm'}}}
        for parameter, value in param_data['Rotor_params'].items():
            value['DataType'] = 'real_T'
        return param_data


    def add_resources(self, Name: str, client):
        self.resources[Name] = client

    def append_window(self, Window):
        self.WindowSeries.append(Window)
        return self

    def Vehicle_Type_Change(self,Type = 0):
        self.Vehicle_Type =Type


class SettingClient:
    def __init__(self, SharedData):
        self.SharedData = SharedData
        self.RPC_client = RPC_client.RPC_client(self.SharedData)
        self.AirSimSettings = AirSimSettings(self.SharedData)
        self.AirSimParameters = AirSimParameters(self.SharedData)
        self.SharedData.add_resources('SettingClient', self)


# used by client
class AirSimParameters:
    def __init__(self, SharedData):
        self.SharedData = SharedData
        self.RPC_client = self.SharedData.resources['RPC_client']
        self.param_data = self.SharedData.param_data
        self.get_params()

    def print_params(self):
        print(self.param_data)

    def get_params(self):
        """
        get params from server
        :return: params from server
        """
        self.param_data.update(self.RPC_client.get_params())

    def set_param(self, param_kind: str, param: str, value: float):
        """
        set a param, note that the change won't commit until calling set_params()
        :param param_kind:
        :param param:
        :param value:
        :return:
        """
        self.param_data[param_kind][param]['Value'] = value

    def set_params(self):
        """
        after params settings, call this function to update changes to the server
        :return:
        """
        self.RPC_client.set_params()


class AirSimSettings:
    def __init__(self, SharedData):
        self.defaultSettings = {"SeeDocsAt": "https://github.com/Microsoft/AirSim/blob/master/docs/settings.md",
                                "SettingsVersion": 1.2, "SimMode": "Multirotor"}
        self.SharedData = SharedData
        self.RPC_client = self.SharedData.resources['RPC_client']
        self.settings = self.RPC_client.json_load("settings")
        self.SharedData.add_resources('AirSimSettings', self)
        

    def __del__(self):
        # better kill the thread
        pass

    def reset(self):
        """
        Set to default settings
        """
        self.settings = self.defaultSettings
        self.RPC_client.json_dump('settings', self.settings)

    def set(self, key, value):
        """
            See https://microsoft.github.io/AirSim/settings/ for more options

            Most useful choices:
              "SimMode": 'Car','Multirotor','ComputerVision'
              "ViewMode": ""(default),'FlyWithMe'(drone default),'GroundObserver','Fpv','Manual',SpringArmChase'(car default),'NoDisplay'
        """
        self.settings[key] = value
        self.settings = self.remove_empty_key(self.settings)
        # print('s_settings = ', self.settings)
        self.RPC_client.json_dump('settings', self.settings)
        # str = json.dumps(settings, allow_nan=True)
        # fp.write(str)

    def print(self):
        print(self.settings)
        # with open(self.path, 'r', encoding='utf8')as fp:
            # json_file = json.load(fp)
            # print(json_file)
            # print(fp.read())

    def remove_empty_key(self, info):
        def isinstance(a, b):
            return type(a) is b

        if isinstance(info, dict):
            info_re = dict()
            for key, value in info.items():
                if isinstance(value, dict) or isinstance(value, list):
                    re = self.remove_empty_key(value)
                    if len(re):
                        info_re[key] = re
                elif value not in ['', {}, [], 'null', nan]:
                    info_re[key] = value
            return info_re
        elif isinstance(info, list):
            info_re = list()
            for value in info:
                if isinstance(value, dict) or isinstance(value, list):
                    re = self.remove_empty_key(value)
                    if len(re):
                        info_re.append(re)
                elif value not in ['', {}, [], 'null', nan]:
                    info_re.append(value)
            return info_re
        else:
            print('输入非列表/字典')

    def set_wind(self, x=0, y=0, z=0):
        """
        This setting specifies the wind speed in World frame, in NED direction.
        NED: x(North), y(East), z(Down)
        """
        wind_speed = {"X": x, "Y": y, "Z": z}
        self.set('Wind', wind_speed)

    def set_vehicle_type(self,vehicle_type = "Multirotor"):
        """
        set_vehicle_type set the type of simulation model

        Args:
            vehicle_type: _description_. Defaults to "Multirotor".
        """
        self.set('SimMode',vehicle_type)
        

    def set_camera_director(self, follow_distance=-3, x=nan, y=nan, z=nan, pitch=nan, roll=nan, yaw=nan):
        """
        Position is in NED coordinates in SI units with origin set to Player Start location in Unreal environment.
        NED: x(North), y(East), z(Down)
        """
        camera_director = {"FollowDistance": follow_distance, "X": x, "Y": y, "Z": z, "Pitch": pitch, "Roll": roll,
                           "Yaw": yaw}
        self.set('CameraDirector', camera_director)

    def set_origin_geopoint(self, latitude=47.641468, longitude=-122.140165, altitude=122):
        origin_geopoint = {"Latitude": latitude, "Longitude": longitude, "Altitude": altitude}
        self.set('OriginGeopoint', origin_geopoint)

    def set_subwindows(self, *subwindow):
        """
        This setting determines what is shown in each of 3 subwindows which are visible when you press 1,2,3 keys.

        :param subwindow: (use subwindow object)
        :return:
        """
        subwindows_list = []
        for i in subwindow:
            subwindows_list.append(i)
        self.set('SubWindows', subwindows_list)

    def set_camera_defaults(self, x=nan, y=nan, z=nan, pitch=nan, roll=nan, yaw=nan, capture_settings=[],
                            noise_settings=[], gimbal={}, unreal_engine={}):
        """
        The CameraDefaults element at root level specifies defaults used for all cameras.
        These defaults can be overridden for individual camera in Cameras element inside Vehicles as described later.

        :param x:
        :param y:
        :param z:
        :param pitch:
        :param roll:
        :param yaw:
        :param capture_settings:(input capture_settings object)
        :param noise_settings:(input noise_settings object)
        :param gimbal:(input noise_settings object)
        :param unreal_engine:(input unreal_engine object)
        """
        camera_defaults = self.camera_settings(x, y, z, pitch, roll, yaw, capture_settings, noise_settings, gimbal, unreal_engine)
        self.set("CameraDefaults", camera_defaults)

    def set_external_camera(self, camera_settings_1={}, camera_settings_2={}):
        """
        This element allows specifying cameras which are separate from the cameras attached to the vehicle,
        such as a CCTV camera. These are fixed cameras, and don't move along with the vehicles.
        The key in the element is the name of the camera.
        All the camera APIs work with external cameras, including capturing images, changing the pose, etc by passing the parameter external=True in the API call.

        :param camera_settings_1:(input camera_settings object)
        :param camera_settings_2:(input camera_settings object)
        """
        external_cameras = {}
        if not camera_settings_1:
            external_cameras["FixedCamera1"] = camera_settings_1
        if not camera_settings_2:
            external_cameras["FixedCamera2"] = camera_settings_2
        if not external_cameras:
            self.set("ExternalCameras", external_cameras)

    # TODO
    def set_pawn_path(self):
        """
        This allows you to specify your own vehicle pawn blueprints, for example, you can replace the default car in AirSim with your own car
        See https://microsoft.github.io/AirSim/settings/ for more information

        "PawnPaths": {
                "BareboneCar": {"PawnBP": "Class'/AirSim/VehicleAdv/Vehicle/VehicleAdvPawn.VehicleAdvPawn_C'"},
                "DefaultCar": {"PawnBP": "Class'/AirSim/VehicleAdv/SUV/SuvCarPawn.SuvCarPawn_C'"},
                "DefaultQuadrotor": {"PawnBP": "Class'/AirSim/Blueprints/BP_FlyingPawn.BP_FlyingPawn_C'"},
                "DefaultComputerVision": {"PawnBP": "Class'/AirSim/Blueprints/BP_ComputerVisionPawn.BP_ComputerVisionPawn_C'"}
              },
        """
        pass

    def set_recording(self, folder="", record_interval=0.05,
                      recording_cameras=[{"CameraName": "0", "ImageType": 0, "PixelsAsFloat": False,  "VehicleName": "", "Compress": True}],
                      record_on_move=False, enabled=False):
        """
        The recording feature allows you to record data such as position, orientation, velocity along with the captured image at specified intervals.
        You can start recording by pressing red Record button on lower right or the R key.
        The data is stored in the Documents/AirSim folder (or the folder specified using Folder),
        in a time stamped subfolder for each recording session, as tab separated file.

        :param record_interval: Specifies minimal interval in seconds between capturing two images.
        :param record_on_move: specifies that do not record frame if there was vehicle's position or orientation hasn't changed.
        :param folder: Where to store your recording data
        :param enabled: Whether Recording should start from the beginning itself,
        setting to true will start recording automatically when the simulation starts. By default, it's set to false
        :param recording_cameras: (input cameras object) By default scene image from camera 0 is recorded as compressed png format.
        :return:
        """
        recording = {"RecordInterval": record_interval, "RecordOnMove": record_on_move, "Folder": folder,
                     "Enabled": enabled, "Cameras": recording_cameras}
        self.set("Recording", recording)

    def set_cameras(self, cameras={}):
        """
        :param cameras: input cameras object
        :return:
        """
        self.set("Cameras", cameras)

    def set_vehicles(self, vehicles):
        """
        Each simulation mode will go through the list of vehicles specified in this setting and create the ones that has "AutoCreate": true.
        Each vehicle specified in this setting has key which becomes the name of the vehicle.
        If "Vehicles" element is missing then this list is populated with default car named "PhysXCar" and default multirotor named "SimpleFlight"

        "Vehicles": {
                "SimpleFlight": {
                  "VehicleType": "SimpleFlight",
                  "DefaultVehicleState": "Armed",
                  "AutoCreate": true,
                  "PawnPath": "",
                  "EnableCollisionPassthrogh": false,
                  "EnableCollisions": true,
                  "AllowAPIAlways": true,
                  "EnableTrace": false,
                  "RC": {
                    "RemoteControlID": 0,
                    "AllowAPIWhenDisconnected": false
                  },
                  "Cameras": {
                    //same elements as CameraDefaults above, key as name
                  },
                  "X": NaN, "Y": NaN, "Z": NaN,
                  "Pitch": NaN, "Roll": NaN, "Yaw": NaN
                },
                "PhysXCar": {
                  "VehicleType": "PhysXCar",
                  "DefaultVehicleState": "",
                  "AutoCreate": true,
                  "PawnPath": "",
                  "EnableCollisionPassthrogh": false,
                  "EnableCollisions": true,
                  "RC": {
                    "RemoteControlID": -1
                  },
                  "Cameras": {
                    "MyCamera1": {
                      //same elements as elements inside CameraDefaults above
                    },
                    "MyCamera2": {
                      //same elements as elements inside CameraDefaults above
                    },
                  },
                  "X": NaN, "Y": NaN, "Z": NaN,
                  "Pitch": NaN, "Roll": NaN, "Yaw": NaN
                }
              },
        """
        self.set("Vehicles", vehicles)

    @staticmethod
    def vehicles_add(vehicle_name="SimpleFlight", vehicle_settings={}, vehicles={}):
        vehicles[vehicle_name] = vehicle_settings
        return vehicles

    @staticmethod
    def vehicle_settings(vehicle_type='SimpleFlight', default_vehicle_state='Armed', auto_create=True, pawn_path='',
                         enable_collision_pass_through=False, enable_collisions=True, allow_api_always=True,
                         enable_trace=False, RC={}, cameras={}, x=nan, y=nan, z=nan, pitch=nan, roll=nan, yaw=nan):
        vehicle_settings = {"VehicleType": vehicle_type, "DefaultVehicleState": default_vehicle_state,
                            "AutoCreate": auto_create, "PawnPath": pawn_path,
                            "EnableCollisionPassThrough": enable_collision_pass_through,
                            "EnableCollisions": enable_collisions, "AllowAPIAlways": allow_api_always,
                            "EnableTrace": enable_trace, "RC": RC, "Cameras": cameras, "X": x, "Y": y, "Z": z,
                            "Pitch": pitch, "Roll": roll, "Yaw": yaw}
        return vehicle_settings

    @staticmethod
    def recording_camera(camera_name: str, image_type: int, vehicle_name: str, compress=True, pixels_as_float=False):
        """
        this element controls which cameras are used to capture images.
        By default scene image from camera 0 is recorded as compressed png format.

        :param camera_name:
        :param image_type:(enum class)
                Available ImageType Values:
                  Scene = 0,
                  DepthPlanar = 1,
                  DepthPerspective = 2,
                  DepthVis = 3,
                  DisparityNormalized = 4,
                  Segmentation = 5,
                  SurfaceNormals = 6,
                  Infrared = 7,
                  OpticalFlow = 8,
                  OpticalFlowVis = 9
        :param pixels_as_float:
        :param vehicle_name:
        :param compress:
        :return:camera object
        """
        camera = {"CameraName": camera_name, "ImageType": image_type, "PixelsAsFloat": pixels_as_float,
                   "VehicleName": vehicle_name, "compress": compress}
        return camera

    @staticmethod
    def recording_cameras(*camera):
        """
        :param camera: use recording_camera objects(you can input at most 3 camera object as params)
        :return: recording_cameras object
        """
        cameras_list = []
        for i in camera:
            cameras_list.append(i)
        return cameras_list

    @staticmethod
    def cameras_add(camera_name: str, camera_settings={}, cameras={}):
        """
        add camera to an existing cameras object, if no cameras object input, create a new one
        :param camera_name:
        :param camera_settings:
        :param cameras: input existing cameras object
        :return:
        """
        cameras[camera_name] = camera_settings
        return cameras

    @staticmethod
    def camera_settings(x=nan, y=nan, z=nan, pitch=nan, roll=nan, yaw=nan, capture_settings=[], noise_settings=[],
                        gimbal={}, unreal_engine={}):
        """
        :param x:
        :param y:
        :param z:
        :param pitch:
        :param roll:
        :param yaw:
        :param capture_settings:(input capture_settings object)
        :param noise_settings:(input noise_settings object)
        :param gimbal:(input noise_settings object)
        :param unreal_engine:(input unreal_engine object)
        """
        # if not capture_settings:
        #     capture_settings = AirSimSettings.capture_settings()
        # if not noise_settings:
        #     noise_settings = AirSimSettings.noise_settings()
        # if not gimbal:
        #     gimbal = AirSimSettings.gimbal()
        # if not unreal_engine:
        #     unreal_engine = AirSimSettings.unreal_engine()

        camera_settings = {"X": x, "Y": y, "Z": z, "Pitch": pitch, "Roll": roll, "Yaw": yaw,
                           "CaptureSettings": capture_settings, "NoiseSettings": noise_settings, "Gimbal": gimbal,
                           "UnrealEngine": unreal_engine}
        return camera_settings

    @staticmethod
    def subwindow(window_id: int, image_type: int, camera_name="0", visible=True, external=False, vehicle_name=''):
        """
        This setting determines what is shown in each of 3 subwindows which are visible when you press 1,2,3 keys.

        :param window_id:0,1,2
        :param camera_name: any available camera on the vehicle or external camera
        :param image_type:(enum class)
            Scene = 0,
            DepthPlanar = 1,
            DepthPerspective = 2,
            DepthVis = 3,
            DisparityNormalized = 4,
            Segmentation = 5,
            SurfaceNormals = 6,
            Infrared = 7,
            OpticalFlow = 8,
            OpticalFlowVis = 9
        :param vehicle_name: String allows you to specify the vehicle to use the camera from,
                            used when multiple vehicles are specified in the settings。
                            Leave it empty if there is only one vehicle
        :param external: Set it to true if the camera is an external camera. If true, then the VehicleName parameter is ignored
        :param visible: Determine if the subwindow is visible
        :return:
        """
        subwindow = {"WindowsID": window_id, "CameraName": camera_name, "ImageType": image_type,
                     "Visible": visible}
        if vehicle_name != '':
            subwindow["VehicleName"] = vehicle_name
        if external:
            subwindow["External"] = external
        return subwindow

    @staticmethod
    def capture_settings(image_type=0, width=891, height=391, fov_degrees=90, auto_exposure_speed=100,
                         auto_exposure_bias=0, auto_exposure_max_brightness=0.64, auto_exposure_min_brightness=0.03,
                         motion_blur_amount=0, target_gamma=1.0, projection_mode="", ortho_width=5.12):
        """
        :param auto_exposure_speed: Decides how fast eye adaptation works. We set to generally high value such as 100 to avoid artifacts（假像） in image capture.
        :param projection_mode: Decides the projection used by the capture camera
                                projection_mode = "perspective"(default),"orthographic"（正射投影？需要建议百度一下）
        :param ortho_width: Determines width of projected area captured in meters.(only work at orthographic mode)
        """
        capture_settings_dict = {"ImageType": image_type, "Width": width, "Height":height, "FOV_Degrees": fov_degrees,
                                 "AutoExposureSpeed": auto_exposure_speed, "AutoExposureBias": auto_exposure_bias,
                                 "AutoExposureMaxBrightness": auto_exposure_max_brightness,
                                 "AutoExposureMinBrightness": auto_exposure_min_brightness,
                                 "MotionBlurAmount": motion_blur_amount, "TargetGamma": target_gamma,
                                 "ProjectionMode": projection_mode, "OrhoWidth": ortho_width}
        capture_settings = [capture_settings_dict]
        return capture_settings

    @staticmethod
    def noise_settings(enabled=False, image_type=0, rand_contrib=0.2, rand_speed=100000.0, rand_size=500.0,
                       rand_density=2, horz_wave_contrib=0.03, horz_wave_strength=0.08, horz_wave_vert_size=1.0,
                       horz_wave_screen_size=1.0, horz_noise_lines_contrib=1.0, horz_noise_lines_density_y=0.01,
                       horz_noise_lines_density_xy=0.5, horz_distortion_contrib=1.0, horz_distortion_strength=0.002
                       ):
        """
        Random noise
        :param rand_contrib: This determines blend ratio of noise pixel with image pixel, 0 means no noise and 1 means only noise
        :param rand_speed: （随机干扰的变化速度）This determines how fast noise fluctuates, 1 means no fluctuation and higher values like 1E6 means full fluctuation.
        :param rand_size:  （随机干扰的粒度）This determines how coarse noise is, 1 means every pixel has its own noise while higher value means more than 1 pixels share same noise value.
        :param rand_density: （随机干扰的像素点数）This determines how many pixels out of total will have noise, 1 means all pixels while higher value means lesser number of pixels (exponentially)

        Horizontal bump distortion(This adds horizontal bumps / flickering / ghosting effect)
        :param horz_wave_contrib: This determines blend ratio of noise pixel with image pixel, 0 means no noise and 1 means only noise
        :param horz_wave_strength: This determines overall strength of the effect
        :param horz_wave_vert_size: This determines how many vertical pixels would be effected by the effect
        :param horz_wave_screen_size: This determines how much of the screen is effected by the effect

        Horizontal noise lines(This adds regions of noise on horizontal lines)
        :param horz_noise_lines_contrib: This determines blend ratio of noise pixel with image pixel, 0 means no noise and 1 means only noise
        :param horz_noise_lines_density_y: This determines how many pixels in horizontal line gets affected
        :param horz_noise_lines_density_xy: This determines how many lines on screen gets affected

        Horizontal line distortion(This adds fluctuations on horizontal line)
        :param horz_distortion_contrib: This determines blend ratio of noise pixel with image pixel, 0 means no noise and 1 means only noise
        :param horz_distortion_strength: This determines how large is the distortion
        """
        noise_settings_dict = {"Enabled": enabled, "ImageType": image_type, "RandContrib": rand_contrib,
                               "RandSpeed": rand_speed, "RandSize": rand_size, "RandDensity": rand_density,
                               "HorzWaveContrib": horz_wave_contrib, "HorzWaveStrength": horz_wave_strength,
                               "HorzWaveVertSize": horz_wave_vert_size, "HorzWaveScreenSize": horz_wave_screen_size,
                               "HorzNoiseLinesContrib": horz_noise_lines_contrib,
                               "HorzNoiseLinesDensityY": horz_noise_lines_density_y,
                               "HorzNoiseLinesDensityXY": horz_noise_lines_density_xy,
                               "HorzDistortionContrib": horz_distortion_contrib,
                               "HorzDistortionStrength": horz_distortion_strength}
        noise_settings = [noise_settings_dict]
        return noise_settings

    @staticmethod
    def gimbal(pitch=nan, roll=nan, yaw=nan, stabilization=0):
        """
        The Gimbal element allows to freeze camera orientation for pitch, roll and/or yaw
        :param stabilization: defaulted to 0 meaning no gimbal (camera orientation changes with body orientation on all axis)
                            The value of 1 means full stabilization.
        :param yaw: When any of the angles(pitch, roll, yaw) is omitted from json or set to NaN, that angle is not stabilized
        """
        gimbal = {"Pitch": pitch, "Roll": roll, "Yaw": yaw, "Stabilization": stabilization}
        return gimbal

    # TODO
    @staticmethod
    def unreal_engine():
        """
        This element contains settings specific to the Unreal Engine
        """
        unreal_engine = {
            "PixelFormatOverride": [
                {
                    "ImageType": 0,
                    "PixelFormat": 0
                }
            ]
        }
        return unreal_engine

    @staticmethod
    def image_type(image_type: str):
        if image_type == 'Scene':
            return 0
        elif image_type == 'DepthPlanar':
            return 1
        elif image_type == 'DepthPerspective':
            return 2
        elif image_type == 'DepthVis':
            return 3
        elif image_type == 'DisparityNormalized':
            return 4
        elif image_type == 'Segmentation':
            return 5
        elif image_type == 'SurfaceNormals':
            return 6
        elif image_type == 'Infrared':
            return 7
        elif image_type == 'OpticalFlow':
            return 8
        elif image_type == 'OpticalFlowVis':
            return 9
        else:
            print("not a valid Image Type")
            return 0


class GroundTruthEstimation(threading.Thread):
    def __init__(self, SharedData):
        threading.Thread.__init__(self)
        self.SharedData = SharedData
        self.client = SharedData.resources['client']
        self.dt = 0.5,     # period for running GroundTruth Estimation thread
        self.CameraImages = []
        self.ImuData = {}
        self.BarometerData = {}
        self.MagnetometerData = {}
        self.GpsData = {}
        self.KinematicsState = {}
        self.EnvironmentState = {}
        self.RotorStates = {}
        self.EstimationData = {}

    # 目前不使用创建新线程的方式以固定时间self.dt更新，而是在窗口中的QTimer中顺带调用update()更新
    def run(self):    # 把要执行的代码写到run函数里面 调用start创建线程来运行run函数
        print("Starting GroundTruthEstimation")
        while True:
            self.update()
            time.sleep(self.dt[0])

    def update(self):
        # data update
        with self.SharedData.lock:
            self.update_sensor_data()
            self.KinematicsState = self.client.simGetGroundTruthKinematics()
            self.EnvironmentState = self.client.simGetGroundTruthEnvironment()
            #self.RotorStates = self.client.getRotorStates()
            self.update_image()
        print("At time ", time.time(), "Simulator Data Updated!")
        # estimate
        self.update_estimation()
        
    def Kinematics_update(self):
        with self.SharedData.lock:
            self.KinematicsState = self.client.simGetGroundTruthKinematics()

    def set_sample_time(self, dt):
        self.dt = dt

    def update_sensor_data(self):
        self.ImuData = self.client.getImuData()
        self.BarometerData = self.client.getBarometerData()
        self.MagnetometerData = self.client.getMagnetometerData()
        self.GpsData = self.client.getGpsData()

    def update_image(self):
        image_list = self.client.simGetImages([airsim.ImageRequest('0',airsim.ImageType.Scene),
                                               airsim.ImageRequest('1',airsim.ImageType.Scene),
                                               airsim.ImageRequest('2',airsim.ImageType.Scene),
                                               airsim.ImageRequest('3',airsim.ImageType.Scene),
                                               airsim.ImageRequest('4',airsim.ImageType.Scene),
                                               airsim.ImageRequest("user_defined",airsim.ImageType.Scene)
                                               ])
        if not image_list:
            print("no image received")
        for i in range(len(image_list)):
            # 将图片字节码bytes转换成一维的numpy数组到缓存中
            img_buffer_numpy = np.frombuffer(image_list[i].image_data_uint8, dtype=np.uint8)
            img = cv2.imdecode(img_buffer_numpy, 1)  # 从指定的内存缓存中读取一维numpy数据，并把数据转换(解码)成图像矩阵格式
            img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            if len(self.CameraImages) <= i:
                # insert() takes too much time
                self.CameraImages.insert(i, img)
            else:
                self.CameraImages[i] = img

    def update_estimation(self):
        pass

    def get_estimation(self):
        pass

    def log(self):
        pass


class Control:
    def __init__(self, SharedData):
        self.SharedData = SharedData
        # 下面这一段是整段程序第一次调用airsimAPI，需要反复尝试，直到仿真环境开启连接成功
        while True:
            try:
                if (SharedData.is_localhost):
                    if SharedData.Vehicle_Type == 0:
                        self.client = airsim.MultirotorClient()
                    elif SharedData.Vehicle_Type == 1:
                        self.client = airsim.CarClient()
                else:
                    self.client = airsim.MultirotorClient(ip=remote_host)
                SharedData.add_resources('client', self.client)

                print("check whether simulator has started")
                self.client.enableApiControl(True)  # 获取控制权
                print("simulator has started, ready to go!")
            except :
                print("simulator hasn't started, retrying...")
            else:
                break
        self.client.armDisarm(True)  # 解锁

        self.GroundTruth = GroundTruthEstimation(self.SharedData)
        # self.GroundTruth.start()

    # some of the APIs here are actually airsim APIs defined in client.py
    # basic control
    def takeoffAsync(self):
        with self.SharedData.lock:
            self.client.takeoffAsync()
    
    def landAsync(self):
        with self.SharedData.lock:
            self.client.landAsync()

    # low level
    def moveByMotorPWMsAsync(self, front_right_pwm, rear_left_pwm, front_left_pwm, rear_right_pwm, duration, vehicle_name =''):
        with self.SharedData.lock:
            return self.client.moveByMotorPWMsAsync(front_right_pwm, rear_left_pwm, front_left_pwm, rear_right_pwm, duration, vehicle_name)

    def moveByRollPitchYawZAsync(self, roll, pitch, yaw, z, duration, vehicle_name=''):
        with self.SharedData.lock:
            self.client.moveByRollPitchYawZAsync(roll, pitch, yaw, z, duration, vehicle_name)

    def moveByRollPitchYawrateThrottleAsync(self, roll, pitch, yaw_rate, throttle, duration, vehicle_name=''):
        with self.SharedData.lock:
            self.client.moveByRollPitchYawrateThrottleAsync(roll, pitch, yaw_rate, throttle, duration, vehicle_name)

    def moveByRollPitchYawrateZAsync(self, roll, pitch, yaw_rate, z, duration, vehicle_name=''):
        with self.SharedData.lock:
            self.client.moveByRollPitchYawrateZAsync(roll, pitch, yaw_rate, z, duration, vehicle_name)


    # high level
    def moveByVelocityBodyFrameAsync(self, vx, vy, vz, duration, drivetrain=airsim.DrivetrainType.MaxDegreeOfFreedom, 
                                     yaw_mode=airsim.YawMode(), vehicle_name=''):
        with self.SharedData.lock:
            self.client.moveByVelocityBodyFrameAsync(vx, vy, vz, duration, drivetrain, yaw_mode, vehicle_name)

    # controller gains
    def setAngleRateControllerGains(self, angle_rate_gains, vehicle_name=''):
        with self.SharedData.lock:
            self.client.setAngleRateControllerGains(angle_rate_gains, vehicle_name)

    def setAngleLevelControllerGains(self, angle_level_gains, vehicle_name=''):
        with self.SharedData.lock:
            self.client.setAngleLevelControllerGains(angle_level_gains, vehicle_name)

    def setVelocityControllerGains(self, velocity_gains, vehicle_name=''):
        with self.SharedData.lock:
            self.client.setVelocityControllerGains(velocity_gains, vehicle_name)

    def setPositionControllerGains(self, position_gains, vehicle_name=''):
        with self.SharedData.lock:
            self.client.setPositionControllerGains(position_gains, vehicle_name)

    # tracking
    def moveOnPathAsync(self, path, velocity, lookahead=-1, adaptive_lookahead=1, vehicle_name=''):
        timeout_sec = 3e+38
        drivetrain = airsim.DrivetrainType.MaxDegreeOfFreedom
        yaw_mode = airsim.YawMode()
        # 在with语句块中有 return 时会在return发生以后再调用lock.release()
        with self.SharedData.lock:
            return self.client.moveOnPathAsync(path, velocity, timeout_sec, drivetrain, yaw_mode,
            lookahead, adaptive_lookahead, vehicle_name)

    def moveOnPath_LQR(self, p_traj, v_traj, a_traj):
        # 解算离散LQR的反馈矩阵

        def DLQR(A, B, Q, R):
            S = np.matrix(linalg.solve_discrete_are(A, B, Q, R))
            K = np.matrix(linalg.inv(B.T * S * B + R) * (B.T * S * A))
            return K

        # 四旋翼加速度控制
        def move_by_acceleration_horizontal(self, ax_cmd, ay_cmd, z_cmd, duration=1):
            print("At time ", time.time(), "LQR_fly sending command")
            # 读取自身yaw角度
            self.GroundTruth.Kinematics_update()
            state = self.GroundTruth.KinematicsState
            angles = airsim.to_eularian_angles(state.orientation)
            yaw_my = angles[2]
            g = 9.8  # 重力加速度
            sin_yaw = math.sin(yaw_my)
            cos_yaw = math.cos(yaw_my)
            A_psi = np.array([[sin_yaw, cos_yaw], [-cos_yaw, sin_yaw]])
            A_psi_inverse = np.linalg.inv(A_psi)
            angle_h_cmd = 1 / g * np.dot(A_psi_inverse, np.array([[-ax_cmd], [-ay_cmd]]))
            a_x_cmd = math.atan(angle_h_cmd[0, 0])
            a_y_cmd = -math.atan(angle_h_cmd[1, 0])
            self.moveByRollPitchYawZAsync(a_x_cmd, a_y_cmd, 0, z_cmd, duration)
            return

        # configuration
        dt = 0.5
        A = np.array([[1, 0, dt, 0],
                      [0, 1, 0, dt],
                      [0, 0, 1, 0],
                      [0, 0, 0, 1]])
        B = np.array([[0, 0],
                      [0, 0],
                      [dt, 0],
                      [0, dt]])
        Q = np.diag([2, 2, 2, 2])
        R = np.diag([.1, .1])
        K = DLQR(A, B, Q, R)

        plot_last_pos = [airsim.Vector3r(0, 0, -5)]

        start_time = time.time()
        for t in range(1600):
            if time.time()-start_time >10:
                break
            # 读取当前的位置和速度
            self.GroundTruth.Kinematics_update()
            UAV_state = self.GroundTruth.KinematicsState
            pos_now = np.array([[UAV_state.position.x_val], [UAV_state.position.y_val], [UAV_state.position.z_val]])
            vel_now = np.array(
                [[UAV_state.linear_velocity.x_val], [UAV_state.linear_velocity.y_val],
                 [UAV_state.linear_velocity.z_val]])
            state_now = np.vstack((pos_now[0:2], vel_now[0:2]))
            # 目标状态
            state_des = np.vstack((p_traj[:, t:t + 1], v_traj[:, t:t + 1]))
            # LQR轨迹跟踪
            a = -np.dot(K, state_now - state_des) + a_traj[:, t:t + 1]
            # 四旋翼加速度控制
            move_by_acceleration_horizontal(self, a[0, 0], a[1, 0], -5)
            # 画图
            plot_v_start = [airsim.Vector3r(pos_now[0, 0], pos_now[1, 0], pos_now[2, 0])]
            plot_v_end = pos_now + vel_now
            plot_v_end = [airsim.Vector3r(plot_v_end[0, 0], plot_v_end[1, 0], plot_v_end[2, 0])]
            with self.SharedData.lock:
                self.client.simPlotArrows(plot_v_start, plot_v_end, arrow_size=8.0, color_rgba=[0.0, 0.0, 1.0, 1.0])
                self.client.simPlotLineList(plot_last_pos + plot_v_start, color_rgba=[1.0, 0.0, 0.0, 1.0], is_persistent=True)
            plot_last_pos = plot_v_start
            time.sleep(dt)

    def custom_tracking(self, **kwargs):
        pass
    
    # keyboard_control
    def keyboard_control(self):
        print("keyboard_control start!")
        velocity = 3
        duration = 1
        ratio = 3
        velocity_shift = velocity * ratio
        vehicle_name = ""
        """
        take off and land
        """
        keyboard.add_hotkey('t', lambda: self.takeoffAsync())
        keyboard.add_hotkey('l', lambda: self.landAsync())
        """
        up--forward
        down--back
        LEFT--turn left
        RIGHT--turn right
        a--raise height
        d--lower height
        """
        keyboard.add_hotkey('LEFT',
                            lambda: self.moveByVelocityBodyFrameAsync(0, -velocity, 0, duration=duration,
                                                                               vehicle_name=vehicle_name))
        keyboard.add_hotkey('RIGHT',
                            lambda: self.moveByVelocityBodyFrameAsync(0, velocity, 0, duration=duration,
                                                                               vehicle_name=vehicle_name))
        keyboard.add_hotkey('up', lambda: self.moveByVelocityBodyFrameAsync(velocity, 0, 0, duration=duration,
                                                                                     vehicle_name=vehicle_name))
        keyboard.add_hotkey('down',
                            lambda: self.moveByVelocityBodyFrameAsync(-velocity, 0, 0, duration=duration,
                                                                               vehicle_name=vehicle_name))
        keyboard.add_hotkey('a', lambda: self.moveByVelocityBodyFrameAsync(0, 0, -velocity, duration=duration,
                                                                                    vehicle_name=vehicle_name))
        keyboard.add_hotkey('d', lambda: self.moveByVelocityBodyFrameAsync(0, 0, velocity, duration=duration,
                                                                                    vehicle_name=vehicle_name))

        keyboard.add_hotkey('up+LEFT', lambda: self.moveByVelocityBodyFrameAsync(velocity, -velocity, 0,
                                                                                          duration=duration,
                                                                                          vehicle_name=vehicle_name))
        keyboard.add_hotkey('up+RIGHT',
                            lambda: self.moveByVelocityBodyFrameAsync(velocity, velocity, 0, duration=duration,
                                                                               vehicle_name=vehicle_name))
        keyboard.add_hotkey('up+a', lambda: self.moveByVelocityBodyFrameAsync(velocity, 0, -velocity,
                                                                                       duration=duration,
                                                                                       vehicle_name=vehicle_name))
        keyboard.add_hotkey('up+d',
                            lambda: self.moveByVelocityBodyFrameAsync(velocity, 0, velocity, duration=duration,
                                                                               vehicle_name=vehicle_name))

        keyboard.add_hotkey('down+LEFT', lambda: self.moveByVelocityBodyFrameAsync(-velocity, -velocity, 0,
                                                                                            duration=duration,
                                                                                            vehicle_name=vehicle_name))
        keyboard.add_hotkey('down+RIGHT', lambda: self.moveByVelocityBodyFrameAsync(-velocity, velocity, 0,
                                                                                             duration=duration,
                                                                                             vehicle_name=vehicle_name))
        keyboard.add_hotkey('down+a', lambda: self.moveByVelocityBodyFrameAsync(-velocity, 0, -velocity,
                                                                                         duration=duration,
                                                                                         vehicle_name=vehicle_name))
        keyboard.add_hotkey('down+d', lambda: self.moveByVelocityBodyFrameAsync(-velocity, 0, velocity,
                                                                                         duration=duration,
                                                                                         vehicle_name=vehicle_name))

        keyboard.add_hotkey('a+RIGHT', lambda: self.moveByVelocityBodyFrameAsync(0, velocity, -velocity,
                                                                                          duration=duration,
                                                                                          vehicle_name=vehicle_name))
        keyboard.add_hotkey('a+LEFT', lambda: self.moveByVelocityBodyFrameAsync(0, -velocity, -velocity,
                                                                                         duration=duration,
                                                                                         vehicle_name=vehicle_name))

        keyboard.add_hotkey('d+RIGHT',
                            lambda: self.moveByVelocityBodyFrameAsync(0, velocity, velocity, duration=duration,
                                                                               vehicle_name=vehicle_name))
        keyboard.add_hotkey('d+LEFT', lambda: self.moveByVelocityBodyFrameAsync(0, -velocity, velocity,
                                                                                         duration=duration,
                                                                                         vehicle_name=vehicle_name))

        """
         left shift--increase the veloctiy
        """
        keyboard.add_hotkey('LEFT+left shift',
                            lambda: self.moveByVelocityBodyFrameAsync(0, -velocity_shift, 0, duration=duration,
                                                                               vehicle_name=vehicle_name))
        keyboard.add_hotkey('RIGHT+left shift',
                            lambda: self.moveByVelocityBodyFrameAsync(0, velocity_shift, 0, duration=duration,
                                                                               vehicle_name=vehicle_name))
        keyboard.add_hotkey('up+left shift',
                            lambda: self.moveByVelocityBodyFrameAsync(velocity_shift, 0, 0, duration=duration,
                                                                               vehicle_name=vehicle_name))
        keyboard.add_hotkey('down+left shift',
                            lambda: self.moveByVelocityBodyFrameAsync(-velocity_shift, 0, 0, duration=duration,
                                                                               vehicle_name=vehicle_name))
        keyboard.add_hotkey('a+left shift',
                            lambda: self.moveByVelocityBodyFrameAsync(0, 0, -velocity_shift, duration=duration,
                                                                               vehicle_name=vehicle_name))
        keyboard.add_hotkey('d+left shift',
                            lambda: self.moveByVelocityBodyFrameAsync(0, 0, velocity_shift, duration=duration,
                                                                               vehicle_name=vehicle_name))

        keyboard.add_hotkey('left shift+up+LEFT',
                            lambda: self.moveByVelocityBodyFrameAsync(velocity_shift, -velocity_shift, 0,
                                                                               duration=duration,
                                                                               vehicle_name=vehicle_name))
        keyboard.add_hotkey('left shift+up+RIGHT',
                            lambda: self.moveByVelocityBodyFrameAsync(velocity_shift, velocity_shift, 0,
                                                                               duration=duration,
                                                                               vehicle_name=vehicle_name))
        keyboard.add_hotkey('left shift+up+a',
                            lambda: self.moveByVelocityBodyFrameAsync(velocity_shift, 0, -velocity_shift,
                                                                               duration=duration,
                                                                               vehicle_name=vehicle_name))
        keyboard.add_hotkey('left shift+up+d',
                            lambda: self.moveByVelocityBodyFrameAsync(velocity_shift, 0, velocity_shift,
                                                                               duration=duration,
                                                                               vehicle_name=vehicle_name))

        keyboard.add_hotkey('left shift+down+LEFT',
                            lambda: self.moveByVelocityBodyFrameAsync(-velocity_shift, -velocity_shift, 0,
                                                                               duration=duration,
                                                                               vehicle_name=vehicle_name))
        keyboard.add_hotkey('left shift+down+RIGHT',
                            lambda: self.moveByVelocityBodyFrameAsync(-velocity_shift, velocity_shift, 0,
                                                                               duration=duration,
                                                                               vehicle_name=vehicle_name))
        keyboard.add_hotkey('left shift+down+a',
                            lambda: self.moveByVelocityBodyFrameAsync(-velocity_shift, 0, -velocity_shift,
                                                                               duration=duration,
                                                                               vehicle_name=vehicle_name))
        keyboard.add_hotkey('left shift+down+d',
                            lambda: self.moveByVelocityBodyFrameAsync(-velocity_shift, 0, velocity_shift,
                                                                               duration=duration,
                                                                               vehicle_name=vehicle_name))

        keyboard.add_hotkey('left shift+a+RIGHT',
                            lambda: self.moveByVelocityBodyFrameAsync(0, velocity_shift, -velocity_shift,
                                                                               duration=duration,
                                                                               vehicle_name=vehicle_name))
        keyboard.add_hotkey('left shift+a+LEFT',
                            lambda: self.moveByVelocityBodyFrameAsync(0, -velocity_shift, -velocity_shift,
                                                                               duration=duration,
                                                                               vehicle_name=vehicle_name))

        keyboard.add_hotkey('left shift+d+RIGHT',
                            lambda: self.moveByVelocityBodyFrameAsync(0, velocity_shift, velocity_shift,
                                                                               duration=duration,
                                                                               vehicle_name=vehicle_name))
        keyboard.add_hotkey('left shift+d+LEFT',
                            lambda: self.moveByVelocityBodyFrameAsync(0, -velocity_shift, velocity_shift,
                                                                               duration=duration,
                                                                               vehicle_name=vehicle_name))
        keyboard.wait('q')
        keyboard.clear_all_hotkeys()
        print("keyboard_control end!")



class Multirotor:
    """
    use this class to call all flight-related APIs
    note that Multirotor instance should only be created once (because each instance opens a thread for GroundTruthEstimation)
    """
    def __init__(self, SharedData):
        self.SharedData = SharedData
        self.is_localhost = SharedData.is_localhost
        self.FlightControl = Control(self.SharedData)
        self.GroundTruth = self.FlightControl.GroundTruth
        SharedData.add_resources('Multirotor', self)
        self.client = SharedData.resources['client']

    def __del__(self):
        self.client.reset()
        self.client.armDisarm(False)
        self.client.enableApiControl(False)

    # create trajectory
    @staticmethod
    def LQR_8_traj():
        p_traj = np.zeros([2, 1600])
        v_traj = np.zeros([2, 1600])
        a_traj = np.zeros([2, 1600])

        for i in range(400):
            theta = math.pi - math.pi / 400 * i
            p_traj[0, i] = 5 * math.cos(theta) + 5
            p_traj[1, i] = 5 * math.sin(theta)
            v_traj[0, i] = 1.9635 * math.cos(theta - math.pi / 2)
            v_traj[1, i] = 1.9635 * math.sin(theta - math.pi / 2)
            a_traj[0, i] = -0.7712 * math.cos(theta)
            a_traj[1, i] = -0.7712 * math.sin(theta)
        for i in range(400):
            theta = math.pi + math.pi / 400 * i
            p_traj[0, i + 400] = 5 * math.cos(theta) + 15
            p_traj[1, i + 400] = 5 * math.sin(theta)
            v_traj[0, i + 400] = 1.9635 * math.cos(theta + math.pi / 2)
            v_traj[1, i + 400] = 1.9635 * math.sin(theta + math.pi / 2)
            a_traj[0, i + 400] = -0.7712 * math.cos(theta)
            a_traj[1, i + 400] = -0.7712 * math.sin(theta)
        for i in range(400):
            theta = math.pi / 400 * i
            p_traj[0, i + 800] = 5 * math.cos(theta) + 15
            p_traj[1, i + 800] = 5 * math.sin(theta)
            v_traj[0, i + 800] = 1.9635 * math.cos(theta + math.pi / 2)
            v_traj[1, i + 800] = 1.9635 * math.sin(theta + math.pi / 2)
            a_traj[0, i + 800] = -0.7712 * math.cos(theta)
            a_traj[1, i + 800] = -0.7712 * math.sin(theta)
        for i in range(400):
            theta = 2 * math.pi - math.pi / 400 * i
            p_traj[0, i + 1200] = 5 * math.cos(theta) + 5
            p_traj[1, i + 1200] = 5 * math.sin(theta)
            v_traj[0, i + 1200] = 1.9635 * math.cos(theta - math.pi / 2)
            v_traj[1, i + 1200] = 1.9635 * math.sin(theta - math.pi / 2)
            a_traj[0, i + 1200] = -0.7712 * math.cos(theta)
            a_traj[1, i + 1200] = -0.7712 * math.sin(theta)
        return p_traj, v_traj, a_traj

    @staticmethod
    def LQR_0_traj():
        p_traj = np.zeros([2, 1600])
        v_traj = np.zeros([2, 1600])
        a_traj = np.zeros([2, 1600])

        for i in range(1600):
            theta = math.pi - math.pi / 400 * i
            p_traj[0, i] = 5 * math.cos(theta) + 5
            p_traj[1, i] = 5 * math.sin(theta)
            v_traj[0, i] = 1.9635 * math.cos(theta - math.pi / 2)
            v_traj[1, i] = 1.9635 * math.sin(theta - math.pi / 2)
            a_traj[0, i] = -0.7712 * math.cos(theta)
            a_traj[1, i] = -0.7712 * math.sin(theta)
        return p_traj, v_traj, a_traj

    @staticmethod
    def custom_traj():
        pass

    # others
    def plot(self, path, color_rgba=None, is_persistent=True):
        if color_rgba is None:
            color_rgba = [0.0, 1.0, 0.0, 1.0]
        plot_traj = [airsim.Vector3r(path[0, 0], path[1, 0], -5)]

        for i in range(1600):
            plot_traj += [airsim.Vector3r(path[0, i], path[1, i], -5)]
        with self.SharedData.lock:
            self.client.simPlotLineList(plot_traj, color_rgba=color_rgba, is_persistent=is_persistent)

    def LQR_fly(self, traj_name):
        print("LQR_fly started")
        print("LQR_fly: waiting until takeoff")
        with self.SharedData.lock:
            self.client.takeoffAsync() # 起飞
            self.client.moveToZAsync(-5, 1)  # 上升到5米高度

        print("LQR_fly: generating path")
        if traj_name == '0':
            path = self.LQR_0_traj()
        elif traj_name == '8':
            path = self.LQR_8_traj()

        print("LQR_fly: plotting path")
        self.plot(path[0])  # 画出规划路径

        print("LQR_fly: starting LQR control")
        self.FlightControl.moveOnPath_LQR(path[0], path[1], path[2])

        with self.SharedData.lock:
            self.client.landAsync()
            self.client.armDisarm(False)  # 上锁

        print("LQR_fly finished")


class Car:
    def __init__(self, SharedData):
        self.SharedData = SharedData
        self.is_localhost = SharedData.is_localhost
        self.FlightControl = Control(self.SharedData)
        self.GroundTruth = self.FlightControl.GroundTruth
        SharedData.add_resources('Car', self)
        self.client = SharedData.resources['client']

    def __del__(self):
        self.client.reset()
        self.client.armDisarm(False)
        self.client.enableApiControl(False)


# def init():
#     client = airsim.MultirotorClient()  # connect to the AirSim simulator
#     client.enableApiControl(True)  # 获取控制权
#     client.armDisarm(True)  # 解锁
#     client.takeoffAsync().join()  # 起飞


# list=[]
#         for i in range(len(self.responses)):
#                 file_name="photo_"+str(i)+".png"
#                 list.append(file_name)
#                 airsim.write_file(file_name,self.responses[i].image_data_uint8)
#         for i in range(len(list)):
#             self.showGraphic(i,list[i])

if __name__ == '__main__':
    # settings = AirSimSettings(is_localhost=False)
    # settings.reset()
    # capture_settings = settings.capture_settings(image_type=0, width=788, height=520, fov_degrees=90,
    #                                              auto_exposure_speed=100, auto_exposure_bias=0,
    #                                              auto_exposure_max_brightness=0.64, auto_exposure_min_brightness=0.03,
    #                                              motion_blur_amount=0, target_gamma=1.0, projection_mode="",
    #                                              ortho_width=5.12)
    # gimbal = settings.gimbal(stabilization=0)
    # camera_settings = settings.camera_settings(x=-2, y=0, z=-2, pitch=-45, roll=0, yaw=0,
    #                                            capture_settings=capture_settings, gimbal=gimbal)
    # cameras = settings.cameras_add("Mycamera", camera_settings)
    # vehicle_settings = settings.vehicle_settings(cameras=cameras)
    # vehicles = settings.vehicles_add(vehicle_settings=vehicle_settings)
    # settings.set_vehicles(vehicles)
    # # settings.set_cameras(cameras)
    # print('setting finished')
    # drone = Multirotor(is_localhost=False)

    parameters = AirSimParameters()
    parameters.print_dict()

    # client = airsim.MultirotorClient(ip=remote_host)
    # client.enableApiControl(True)
    # client.armDisarm(True)
    # client.takeoffAsync()
    # print(client.getImuData().time_stamp)
    # print(client.getImuData().time_stamp)
    # client.simGetImages([airsim.ImageRequest('0', airsim.ImageType.Scene),
    #                      airsim.ImageRequest('1', airsim.ImageType.Scene),
    #                      airsim.ImageRequest('2', airsim.ImageType.Scene),
    #                      airsim.ImageRequest('3', airsim.ImageType.Scene),
    #                      airsim.ImageRequest('4', airsim.ImageType.Scene),
    #                      airsim.ImageRequest("Mycamera", airsim.ImageType.Scene)
    #                      ])

    # while(True):
    #     if len(drone.GroundTruth.CameraImages)!=0:
    #         break
    #     else:
    #         print("no image")
    #         time.sleep(0.5)
    # data = drone.GroundTruth.CameraImages[0]
    # cv2.imshow('dd', data)
    # cv2.waitKey(0)
    # cv2.destroyAllWindows()

    # drone = airsim.MultirotorClient(ip=remote_host)
    # drone.enableApiControl(True)
    # drone.armDisarm(True)
    # drone.takeoffAsync()