from typing import Any

import airsim
import numpy as np
import math
import time
from scipy import linalg
import json

nan = float("nan")


class AirSimSettings:
    def __init__(self, path):
        self.path = path
        self.defaultSettings = {"SeeDocsAt": "https://github.com/Microsoft/AirSim/blob/master/docs/settings.md",
                                "SettingsVersion": 1.2, "SimMode": "Multirotor"}

    def reset(self):
        """
        Set to default settings
        """
        with open(self.path, 'w', encoding='utf8')as fp:
            json.dump(self.defaultSettings, fp, ensure_ascii=False)

    def set(self, key, value):
        """
            See https://microsoft.github.io/AirSim/settings/ for more options

            Most useful choices:
              "SimMode": 'Car','Multirotor','ComputerVision'
              "ViewMode": ""(default),'FlyWithMe'(drone default),'GroundObserver','Fpv','Manual',SpringArmChase'(car default),'NoDisplay'
        """
        with open(self.path, 'r', encoding='utf8')as fp:
            settings = json.load(fp)
            settings[key] = value
            settings = self.remove_empty_key(settings)
            # print('s_settings = ', settings)
        with open(self.path, 'w', encoding='utf8')as fp:
            json.dump(settings, fp, ensure_ascii=False, allow_nan=True)
            print(settings)
            # str = json.dumps(settings, allow_nan=True)
            # fp.write(str)

    def print(self):
        with open(self.path, 'r', encoding='utf8')as fp:
            # json_file = json.load(fp)
            # print(json_file)
            print(fp.read())

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
                      cameras=[{"CameraName": "0", "ImageType": 0, "PixelsAsFloat": False,  "VehicleName": "", "Compress": True}],
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
        :param cameras: (input cameras object) By default scene image from camera 0 is recorded as compressed png format.
        :return:
        """
        recording = {"RecordInterval": record_interval, "RecordOnMove": record_on_move, "Folder": folder,
                     "Enabled": enabled, "Cameras": cameras}
        self.set("Recording", recording)

    # TODO
    def set_vehicles(self):
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
        pass

    @staticmethod
    def camera(camera_name: str, image_type: int, vehicle_name: str, compress=True, pixels_as_float=False):
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
    def cameras(*camera):
        """
        :param camera: use camera object(you can input at most 3 camera object as params)
        :return: cameras object
        """
        cameras_list = []
        for i in camera:
            cameras_list.append(i)
        return cameras_list

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
        if not capture_settings:
            capture_settings = AirSimSettings.capture_settings()
        if not noise_settings:
            noise_settings = AirSimSettings.noise_settings()
        if not gimbal:
            gimbal = AirSimSettings.gimbal()
        if not unreal_engine:
            unreal_engine = AirSimSettings.unreal_engine()

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
    def capture_settings(image_type=0, width=256, height=144, fov_degrees=90, auto_exposure_speed=100,
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







def test_traj_creat():
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


def plot(client, p_traj, color_rgba=None, is_persistent=True):
    if color_rgba is None:
        color_rgba = [0.0, 1.0, 0.0, 1.0]
    plot_traj = [airsim.Vector3r(p_traj[0, 0], p_traj[1, 0], -5)]

    for i in range(1600):
        plot_traj += [airsim.Vector3r(p_traj[0, i], p_traj[1, i], -5)]
    client.simPlotLineList(plot_traj, color_rgba=color_rgba, is_persistent=is_persistent)


def moveOnPath_LQR(client, p_traj, v_traj, a_traj):
    # 解算离散LQR的反馈矩阵

    def DLQR(A, B, Q, R):
        S = np.matrix(linalg.solve_discrete_are(A, B, Q, R))
        K = np.matrix(linalg.inv(B.T * S * B + R) * (B.T * S * A))
        return K

    # 四旋翼加速度控制
    def move_by_acceleration_horizontal(client, ax_cmd, ay_cmd, z_cmd, duration=1):
        # 读取自身yaw角度
        state = client.simGetGroundTruthKinematics()
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
        client.moveByRollPitchYawZAsync(a_x_cmd, a_y_cmd, 0, z_cmd, duration)
        return

    # configuration
    dt = 0.02
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

    for t in range(1600):
        # 读取当前的位置和速度
        UAV_state = client.simGetGroundTruthKinematics()
        pos_now = np.array([[UAV_state.position.x_val], [UAV_state.position.y_val], [UAV_state.position.z_val]])
        vel_now = np.array(
            [[UAV_state.linear_velocity.x_val], [UAV_state.linear_velocity.y_val], [UAV_state.linear_velocity.z_val]])
        state_now = np.vstack((pos_now[0:2], vel_now[0:2]))
        # 目标状态
        state_des = np.vstack((p_traj[:, t:t + 1], v_traj[:, t:t + 1]))
        # LQR轨迹跟踪
        a = -np.dot(K, state_now - state_des) + a_traj[:, t:t + 1]
        # 四旋翼加速度控制
        move_by_acceleration_horizontal(client, a[0, 0], a[1, 0], -5)
        # 画图
        plot_v_start = [airsim.Vector3r(pos_now[0, 0], pos_now[1, 0], pos_now[2, 0])]
        plot_v_end = pos_now + vel_now
        plot_v_end = [airsim.Vector3r(plot_v_end[0, 0], plot_v_end[1, 0], plot_v_end[2, 0])]
        client.simPlotArrows(plot_v_start, plot_v_end, arrow_size=8.0, color_rgba=[0.0, 0.0, 1.0, 1.0])
        client.simPlotLineList(plot_last_pos + plot_v_start, color_rgba=[1.0, 0.0, 0.0, 1.0], is_persistent=True)
        plot_last_pos = plot_v_start
        time.sleep(dt)


def LQR_fly_test():
    p_traj, v_traj, a_traj = test_traj_creat()

    client = airsim.MultirotorClient()  # connect to the AirSim simulator
    client.enableApiControl(True)  # 获取控制权
    client.armDisarm(True)  # 解锁
    client.takeoffAsync().join()  # 起飞
    client.moveToZAsync(-5, 1).join()  # 上升到5米高度

    plot(client, p_traj)  # 画出规划路径

    moveOnPath_LQR(client, p_traj, v_traj, a_traj)

    client.landAsync().join()
    client.armDisarm(False)  # 上锁
    client.enableApiControl(False)  # 释放控制权

def init():
    client = airsim.MultirotorClient()  # connect to the AirSim simulator
    client.enableApiControl(True)  # 获取控制权
    client.armDisarm(True)  # 解锁
    client.takeoffAsync().join()  # 起飞


if __name__ == '__main__':
    PATH = 'C:/Users/huyutong2020/Documents/AirSim/settings.json'
    settings = AirSimSettings(PATH)
    settings.reset()

