import airsim
import numpy as np
import math
import time
from scipy import linalg
import json



class AirSimSettings:
    def __init__(self, path):
        self.path = path
        self.defaultSettings = {"SeeDocsAt": "https://github.com/Microsoft/AirSim/blob/master/docs/settings.md",
                                "SettingsVersion": 1.2, "SimMode": "Multirotor"}

    def reset(self):
        with open(self.path, 'w', encoding='utf8')as fp:
            json.dump(self.defaultSettings, fp, ensure_ascii=False)

    def set(self, key, value):
        """
            See https://microsoft.github.io/AirSim/settings/ for details

              "SimMode": 'Car','Multirotor','ComputerVision'
              "ViewMode": 'FlyWithMe'(default),'GroundObserver','Fpv','Manual',SpringArmChase','NoDisplay'
        """
        with open(self.path, 'r', encoding='utf8')as fp:
            settings = json.load(fp)
            # print(settings)
            settings[key] = value
        with open(self.path, 'w', encoding='utf8')as fp:
            json.dump(settings, fp, ensure_ascii=False)

    def print(self):
        with open(self.path, 'r', encoding='utf8')as fp:
            json_file = json.load(fp)
            print(json_file)

    def set_wind(self, x=0, y=0, z=0):
        wind_speed = {"X": x, "Y": y, "Z": z}
        self.set('Wind', wind_speed)

    def set_camera_director(self, x, y, z, pitch, roll, yaw, follow_distance=-3):
        camera_director = {"FollowDistance": follow_distance, "X": x, "Y": y, "Z": z, "Pitch": pitch, "Roll": roll,
                           "Yaw": yaw}
        self.set('CameraDirector', camera_director)

    def set_origin_geopoint(self, latitude, longitude, altitude):
        origin_geopoint = {"Latitude": latitude, "Longitude": longitude, "Altitude": altitude}
        self.set('OriginGeopoint', origin_geopoint)

    # TODO
    def set_subwindows(self):
        """
        This setting determines what is shown in each of 3 subwindows which are visible when you press 1,2,3 keys.

        "SubWindows": [
                {"WindowID": 0, "CameraName": "0", "ImageType": 3, "VehicleName": "", "Visible": false, "External": false},
                {"WindowID": 1, "CameraName": "0", "ImageType": 5, "VehicleName": "", "Visible": false, "External": false},
                {"WindowID": 2, "CameraName": "0", "ImageType": 0, "VehicleName": "", "Visible": false, "External": false}
              ]
        """

    # TODO
    def set_external_camera(self):
        """
        This element allows specifying cameras which are separate from the cameras attached to the vehicle,
        such as a CCTV camera. These are fixed cameras, and don't move along with the vehicles.
        The key in the element is the name of the camera, and the value i.e. settings are the same as CameraDefaults described above.
        All the camera APIs work with external cameras, including capturing images, changing the pose, etc by passing the parameter external=True in the API call.

        "ExternalCameras": {
            "FixedCamera1": {
                // same elements as in CameraDefaults above
            },
            "FixedCamera2": {
                // same elements as in CameraDefaults above
            }
          }
        """

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

    # TODO
    def set_recording(self, record_interval, record_on_move, folder, enabled, cameras):
        """
        The recording feature allows you to record data such as position, orientation, velocity along with the captured image at specified intervals.
        You can start recording by pressing red Record button on lower right or the R key.
        The data is stored in the Documents/AirSim folder (or the folder specified using Folder), in a time stamped subfolder for each recording session, as tab separated file.
        """
        recording = {"RecordInterval": record_interval, "RecordOnMove": record_on_move, "Folder": folder,
                     "Enabled": enabled, "Cameras": cameras}
        self.set('OriginGeopoint', recording)

    # TODO
    def set_camera_defaults(self, x, y, z, pitch, roll, yaw, capture_settings, noise_settings, gimbal, unreal_engine):
        """

        :param x:
        :param y:
        :param z:
        :param pitch:
        :param roll:
        :param yaw:
        :param capture_settings:
        :param noise_settings:
        :param gimbal:
        :param unreal_engine:

            "CameraDefaults": {
                "CaptureSettings": [
                  {
                    "ImageType": 0,
                    "Width": 256,
                    "Height": 144,
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
                "NoiseSettings": [
                  {
                    "Enabled": false,
                    "ImageType": 0,

                    "RandContrib": 0.2,
                    "RandSpeed": 100000.0,
                    "RandSize": 500.0,
                    "RandDensity": 2,

                    "HorzWaveContrib":0.03,
                    "HorzWaveStrength": 0.08,
                    "HorzWaveVertSize": 1.0,
                    "HorzWaveScreenSize": 1.0,

                    "HorzNoiseLinesContrib": 1.0,
                    "HorzNoiseLinesDensityY": 0.01,
                    "HorzNoiseLinesDensityXY": 0.5,

                    "HorzDistortionContrib": 1.0,
                    "HorzDistortionStrength": 0.002
                  }
                ],
                "Gimbal": {
                  "Stabilization": 0,
                  "Pitch": NaN, "Roll": NaN, "Yaw": NaN
                },
                "X": NaN, "Y": NaN, "Z": NaN,
                "Pitch": NaN, "Roll": NaN, "Yaw": NaN,
                "UnrealEngine": {
                  "PixelFormatOverride": [
                    {
                      "ImageType": 0,
                      "PixelFormat": 0
                    }
                  ]
                }
              }
        """
        camera_defaults = {"X": x, "Y": y, "Z": z, "Pitch": pitch, "Roll": roll, "Yaw": yaw,
                           "CaptureSettings": capture_settings, "NoiseSettings": noise_settings, "Gimbal": gimbal,
                           "UnrealEngine": unreal_engine}
        self.set("CameraDefaults", camera_defaults)

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


if __name__ == '__main__':
    PATH = 'C:/Users/huyutong2020/Documents/AirSim/settings.json'
    settings = AirSimSettings(PATH)
    settings.reset()
    settings.set_wind(1, 2, 3)
    settings.print()
