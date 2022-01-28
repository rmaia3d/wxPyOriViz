import numpy as np

import attitude_math as amath


class GenRatesData:
    def __init__(self):
        self.init_data()

    def init_data(self):
        # Initial attitude in angles (roll, pitch, yaw)
        self.attitude0 = amath.Deg_to_Rad([0, 0, 0])

        # Initial body rates in degress/second (roll, pitch, yaw)
        self.omega_body = amath.Deg_to_Rad([0, 0, 90])

        self.attitude_q = amath.QuaternionFromEulerXYZ(self.attitude0)
        self.attitude_euler = self.attitude0

        self.dcm = amath.QuatToDCM(self.attitude_q)

        self.t = 0
        self.dt = 1 / 60        # Assuming 60fps refresh rate
        self.time = []
        self.phi_q = []
        self.theta_q = []
        self.psi_q = []
        self.phi_euler = []
        self.theta_euler = []
        self.psi_euler = []

    def iterate_data(self):
        world_rates = np.matmul(self.omega_body, self.dcm)
        q_dot = amath.QuaternionRates(self.attitude_q, world_rates)
        self.attitude_q = amath.EulerIntegration(
            self.attitude_q, q_dot, self.dt)
        self.attitude_q = amath.QuaternionNormalise(self.attitude_q)
        self.attitude_q_euler = amath.EulerXYZfromQuaternion(self.attitude_q)

        euler_dot = amath.EulerAngleRatesXYZ(
            self.attitude_euler, self.omega_body)
        self.attitude_euler = amath.EulerIntegration(
            self.attitude_euler, euler_dot, self.dt)

        self.time.append(self.t)
        self.phi_q.append(amath.Rad_to_Deg(self.attitude_q_euler[0]))
        self.theta_q.append(amath.Rad_to_Deg(self.attitude_q_euler[1]))
        self.psi_q.append(amath.Rad_to_Deg(self.attitude_q_euler[2]))
        self.phi_euler.append(amath.Rad_to_Deg(self.attitude_euler[0]))
        self.theta_euler.append(amath.Rad_to_Deg(self.attitude_euler[1]))
        self.psi_euler.append(amath.Rad_to_Deg(self.attitude_euler[2]))

        self.dcm = amath.QuatToDCM(self.attitude_q)
        self.t += self.dt

    def set_body_rates(self, rates_tpl):
        # Different signs so rates agree with OpenGL (vispy) conventions
        rates = [rates_tpl[0], -rates_tpl[1], -rates_tpl[2]]
        self.omega_body = amath.Deg_to_Rad(rates)   # In X, Y, Z format

    def get_latest_ypr(self):
        # Different signs so rates agree with OpenGL (vispy) conventions
        out_tpl = (-self.psi_q[-1],
                   -self.theta_q[-1],
                   -self.phi_q[-1])

        print(self.t, out_tpl)
        return out_tpl

    def get_dcm(self):
        # return amath.QuatToDCM(self.attitude_q)
        return self.dcm

    def reset_data(self):
        self.init_data()
