import airsim
import numpy as np
import math
import time

# 输入：期望的位置、速度、加速度
# 输出：力和力矩
def Geometric_control(p_des, v_des, a_des, yaw_des, p_now, v_now, R_now, omega_now, m):
    kp = 2
    kv = 2
    kR = 0.4
    komega = 0.08
    e_p = p_now - p_des
    e_v = v_now - v_des
    g = 9.81
    e3 = np.array([[0], [0], [1]])
    # 求合力 f
    acc = -kp*e_p -kv*e_v - m*g*e3 + m*a_des   # 3x1
    f = -np.dot((acc).T, np.dot(R_now, e3))
    # 求期望的旋转矩阵 R_des
    proj_xb = np.array([math.cos(yaw_des), math.sin(yaw_des), 0])
    acc = acc.reshape(3)
    z_b = - acc / np.linalg.norm(acc)
    y_b = np.cross(z_b, proj_xb)
    y_b = y_b / np.linalg.norm(y_b)
    x_b = np.cross(y_b, z_b)
    x_b = x_b / np.linalg.norm(x_b)
    R_des = np.hstack([np.hstack([x_b.reshape([3, 1]), y_b.reshape([3, 1])]), z_b.reshape([3, 1])])
    # 求合力矩 M
    e_R_tem = np.dot(R_des.T, R_now) - np.dot(R_now.T, R_des)/2
    e_R = np.array([[e_R_tem[2, 1]], [e_R_tem[0, 2]], [e_R_tem[1, 0]]])
    M = -kR * e_R - komega * omega_now
    return f[0, 0], M

# 力和力矩到电机控制的转换
def fM2u(f, M):
    mat = np.array([[4.179446268,       4.179446268,        4.179446268,        4.179446268],
                    [-0.6723341164784,  0.6723341164784,    0.6723341164784,    -0.6723341164784],
                    [0.6723341164784,   -0.6723341164784,   0.6723341164784,    -0.6723341164784],
                    [0.055562,          0.055562,           -0.055562,          -0.055562]])
    fM = np.vstack([f, M])
    u = np.dot(np.linalg.inv(mat), fM)
    u1 = u[0, 0]
    u2 = u[1, 0]
    u3 = u[2, 0]
    u4 = u[3, 0]
    return u1, u2, u3, u4

# 欧拉角到旋转矩阵的转换
def angle2R(roll, pitch, yaw):
    sphi = math.sin(roll)
    cphi = math.cos(roll)
    stheta = math.sin(pitch)
    ctheta = math.cos(pitch)
    spsi = math.sin(yaw)
    cpsi = math.cos(yaw)
    R = np.array([[ctheta*cpsi, sphi*stheta*cpsi-cphi*spsi, cphi*stheta*cpsi+sphi*spsi],
                  [ctheta*spsi, sphi*stheta*spsi+cphi*cpsi, cphi*stheta*spsi-sphi*cpsi],
                  [-stheta,     sphi*ctheta,                cphi*ctheta]])
    return R

# 生成8字形轨迹
def traj_8_create():
    v = 2           # 速度
    dt = 0.02       # 时间间隔
    h = -3          # 高度
    l = v * dt      # 步长：每个周期的长度
    a = 10/math.sqrt(2)  # 方程的参数

    p_traj = np.array([[0], [0], [h]])
    v_traj = np.array([[0], [2], [0]])
    a_traj = np.array([[0], [0], [0]])
    # x in [0, 20]
    l_tem = 0
    x_old = 0
    y_old = 0
    for i in range(1, 100000):  # x4
        x = 0.0002 * i
        p = np.array([1, 0, 2*((x-10)**2) + 2*(a**2), 0, ((x-10)**4) - 2*(a**2)*((x-10)**2)])
        roots = np.roots(p)
        y_list = np.real(roots[abs(np.imag(roots)) < 0.0001])    # 只取实数根,升序
        y_list.sort()
        if x < 10:
            y = y_list[-1]
        else:
            y = y_list[0]
        l_tem += np.linalg.norm(np.array([x-x_old, y-y_old]))
        x_old = x
        y_old = y
        if l_tem >= l:
            p_traj = np.hstack([p_traj, np.array([[x], [y], [h]])])
            l_tem = l_tem - l
    # x in [20, 0]
    for i in range(100000):    # x4
        x = 20 - 0.0002 * i
        p = np.array(
            [1, 0, 2 * ((x - 10) ** 2) + 2 * (a ** 2), 0, ((x - 10) ** 4) - 2 * (a ** 2) * ((x - 10) ** 2)])
        roots = np.roots(p)
        y_list = np.real(roots[abs(np.imag(roots)) < 0.0001])  # 只取实数根,升序
        y_list.sort()
        if x > 10:
            y = y_list[-1]
        else:
            y = y_list[0]
        l_tem += np.linalg.norm(np.array([x - x_old, y - y_old]))
        x_old = x
        y_old = y
        if l_tem >= l:
            p_traj = np.hstack([p_traj, np.array([[x], [y], [h]])])
            l_tem = l_tem - l
    # 求速度、加速度
    for i in range(1, len(p_traj[0, :])):
        g_v = p_traj[:, i:i+1] - p_traj[:, i-1:i]
        g_v = v * g_v/np.linalg.norm(g_v)
        v_traj = np.hstack([v_traj, g_v])
        g_a = g_v - v_traj[:, i-1:i]
        g_a = g_a/dt
        a_traj = np.hstack([a_traj, g_a])

    return p_traj, v_traj, a_traj

# 程序开始
client = airsim.MultirotorClient()
client.enableApiControl(True)
client.takeoffAsync().join()
p_traj, v_traj, a_traj = traj_8_create()

m = 1
total_n = 1000
for i in range(total_n):
    state = client.getMultirotorState()
    pos_now = np.array([[state.kinematics_estimated.position.x_val],
                        [state.kinematics_estimated.position.y_val],
                        [state.kinematics_estimated.position.z_val]])
    vel_now = np.array([[state.kinematics_estimated.linear_velocity.x_val],
                        [state.kinematics_estimated.linear_velocity.y_val],
                        [state.kinematics_estimated.linear_velocity.z_val]])
    acc_now = np.array([[state.kinematics_estimated.linear_acceleration.x_val],
                        [state.kinematics_estimated.linear_acceleration.y_val],
                        [state.kinematics_estimated.linear_acceleration.z_val]])
    omega_now = np.array([[state.kinematics_estimated.angular_velocity.x_val],
                          [state.kinematics_estimated.angular_velocity.y_val],
                          [state.kinematics_estimated.angular_velocity.z_val]])
    pitch_now, roll_now, yaw_now = airsim.to_eularian_angles(state.kinematics_estimated.orientation)
    R_now = angle2R(roll_now, pitch_now, yaw_now)
    f, M = Geometric_control(p_traj[:, i:i+1], v_traj[:, i:i+1], a_traj[:, i:i+1], 0, pos_now, vel_now, R_now, omega_now, m)
    u1, u2, u3, u4 = fM2u(f, M)
    client.moveByMotorPWMsAsync(u1, u2, u3, u4, 0.05)
    time.sleep(0.02)
    client.landAsync()