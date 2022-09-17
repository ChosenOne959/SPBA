import airsim
import numpy as np
import math
import time
from scipy import linalg

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


def plot(p_traj, color_rgba=None, is_persistent=True):

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







if __name__ == '__main__':

    p_traj, v_traj, a_traj = test_traj_creat()

    plot_last_pos = [airsim.Vector3r(0, 0, -5)]

    client = airsim.MultirotorClient()  # connect to the AirSim simulator
    client.enableApiControl(True)  # 获取控制权
    client.armDisarm(True)  # 解锁
    client.takeoffAsync().join()  # 起飞
    client.moveToZAsync(-5, 1).join()  # 上升到5米高度

    plot(p_traj)    # 画出规划路径

    moveOnPath_LQR(client, p_traj, v_traj, a_traj)

    client.landAsync().join()
    client.armDisarm(False)  # 上锁
    client.enableApiControl(False)  # 释放控制权

