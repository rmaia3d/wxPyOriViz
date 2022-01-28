import numpy as np


def RotationX(theta):
    return np.array([[1, 0, 0],
                     [0, np.cos(theta), np.sin(theta)],
                     [0, -np.sin(theta), np.cos(theta)]])


def RotationY(theta):
    return np.array([[np.cos(theta), 0, -np.sin(theta)],
                     [0, 1, 0],
                     [np.sin(theta), 0, np.cos(theta)]])


def RotationZ(theta):
    return np.array([[np.cos(theta), np.sin(theta), 0],
                     [-np.sin(theta), np.cos(theta), 0],
                     [0, 0, 1]])


def DCMfromEulerXYZ(attitude_xyz):
    Rx = RotationX(attitude_xyz[0])
    Ry = RotationY(attitude_xyz[1])
    Rz = RotationZ(attitude_xyz[2])
    R = np.matmul(Rx, np.matmul(Ry, Rz))
    return R


def QuaternionFromEulerXYZ(attitude_xyz):
    c1 = np.cos(0.5 * attitude_xyz[0])
    s1 = np.sin(0.5 * attitude_xyz[0])
    c2 = np.cos(0.5 * attitude_xyz[1])
    s2 = np.sin(0.5 * attitude_xyz[1])
    c3 = np.cos(0.5 * attitude_xyz[2])
    s3 = np.sin(0.5 * attitude_xyz[2])

    q0 = (c1 * c2 * c3) + (s1 * s2 * s3)
    q1 = (s1 * c2 * c3) - (c1 * s2 * s3)
    q2 = (c1 * s2 * c3) + (s1 * c2 * s3)
    q3 = (c1 * c2 * s3) - (s1 * s2 * c3)

    return np.array([q0, q1, q2, q3])


def EulerXYZfromQuaternion(quat):
    q0 = quat[0]
    q1 = quat[1]
    q2 = quat[2]
    q3 = quat[3]

    r11 = (q0 * q0) + (q1 * q1) - (q2 * q2) - (q3 * q3)
    r12 = 2.0 * ((q1 * q2) + (q0 * q3))
    r13 = 2.0 * ((q1 * q3) - (q0 * q2))
    r23 = 2.0 * ((q2 * q3) + (q0 * q1))
    r33 = (q0 * q0) - (q1 * q1) - (q2 * q2) + (q3 * q3)

    phi = np.arctan2(r23, r33)
    theta = -np.arcsin(r13)
    psi = np.arctan2(r12, r11)

    return np.array([phi, theta, psi])


def QuaternionNorm(quat):
    q0 = quat[0]
    q1 = quat[1]
    q2 = quat[2]
    q3 = quat[3]
    return np.sqrt((q0 * q0) + (q1 * q1) + (q2 * q2) + (q3 * q3))


def QuaternionNormalise(quat):
    norm = QuaternionNorm(quat)
    return quat / norm


def Rad_to_Deg(rad):
    return np.array(rad) * (180.0 / np.pi)


def Deg_to_Rad(deg):
    return np.array(deg) * (np.pi / 180.0)


def QuatToDCM(quat):
    q0 = quat[0]
    q1 = quat[1]
    q2 = quat[2]
    q3 = quat[3]

    q0_2 = q0 * q0
    q1_2 = q1 * q1
    q2_2 = q2 * q2
    q3_2 = q3 * q3

    q1q2 = q1 * q2
    q0q3 = q0 * q3
    q1q3 = q1 * q3
    q0q2 = q0 * q2
    q2q3 = q2 * q3
    q0q1 = q0 * q1

    m11 = q0_2 + q1_2 - q2_2 - q3_2
    m12 = 2.0 * (q1q2 + q0q3)
    m13 = 2.0 * (q1q3 - q0q2)
    m21 = 2.0 * (q1q2 - q0q3)
    m22 = q0_2 - q1_2 + q2_2 - q3_2
    m23 = 2.0 * (q2q3 + q0q1)
    m31 = 2.0 * (q1q3 + q0q2)
    m32 = 2.0 * (q2q3 - q0q1)
    m33 = q0_2 - q1_2 - q2_2 + q3_2

    return np.array([[m11, m12, m13],
                     [m21, m22, m23],
                     [m31, m32, m33]])


def QuaternionRates(quat, omega_body):
    q0 = quat[0]
    q1 = quat[1]
    q2 = quat[2]
    q3 = quat[3]
    w = np.array([[-q1, -q2, -q3],
                  [q0, q3, -q2],
                  [-q3, q0, q1],
                  [q2, -q1, q0]])
    return 0.5 * np.matmul(w, omega_body)


def EulerAngleRatesXYZ(attitude, omega_body):
    phi = attitude[0]
    theta = attitude[1]
    E = np.array([[1, np.tan(theta) * np.sin(phi), np.tan(theta) * np.cos(phi)],
                  [0, np.cos(phi), -np.sin(phi)],
                  [0, np.sin(phi) / np.cos(theta), np.cos(phi) / np.cos(theta)]])
    return np.matmul(E, omega_body)


def EulerIntegration(X, Xdot, dt):
    return X + (Xdot * dt)


def EulerFromQuaternion(quat):
    w = quat[0]
    x = quat[1]
    y = quat[2]
    z = quat[3]

    t0 = 2.0 * (w * x + y * z)
    t1 = 1.0 - 2.0 * (x * x + y * y)
    roll_x = np.arctan2(t0, t1)

    t2 = 2.0 * (w * y - z * x)
    t2 = 1.0 if t2 > 1.0 else t2
    t2 = -1.0 if t2 < -1.0 else t2
    pitch_y = np.arcsin(t2)

    t3 = 2.0 * (w * z + x * y)
    t4 = 1.0 - 2.0 * (y * y + z * z)
    yaw_z = np.arctan2(t3, t4)

    return (roll_x, pitch_y, yaw_z)
