import numpy as np
from vispy import app, gloo
from vispy.util.transforms import perspective, rotate


def deg_to_rad(deg):
    return deg * (np.pi / 180.0)


def lookAt(eye, target, up=[0, 0, 1]):
    """Computes matrix to put eye looking at target point."""
    eye = np.asarray(eye).astype(np.float32)
    target = np.asarray(target).astype(np.float32)
    up = np.asarray(up).astype(np.float32)

    vforward = eye - target
    vforward /= np.linalg.norm(vforward)
    vright = np.cross(up, vforward)
    vright /= np.linalg.norm(vright)
    vup = np.cross(vforward, vright)

    view = np.r_[vright, -np.dot(vright, eye),
                 vup, -np.dot(vup, eye),
                 vforward, -np.dot(vforward, eye),
                 [0, 0, 0, 1]].reshape(4, 4, order='F')

    return view


def getView(azimuth, elevation, distance, target=[0, 0, 0]):
    """Computes view matrix based on angle, distance and target."""
    x = distance * np.sin(elevation) * np.sin(azimuth)
    y = distance * np.sin(-elevation) * np.cos(azimuth)
    z = distance * np.cos(elevation)
    return lookAt([x, y, z], target)


class ChevronIndicator:
    VERT_SHADER = """
    // Uniforms
    // ------------------------------------
    uniform   mat4 u_model;
    uniform   mat4 u_view;
    uniform   mat4 u_projection;
    uniform   vec4 u_color;

    // Attributes
    // ------------------------------------
    attribute vec3 a_position;

    // Varying
    // ------------------------------------
    varying vec4 v_color;

    void main()
    {
        v_color = u_color;
        gl_Position = u_projection * u_view * u_model * vec4(a_position,1.0);
    }
    """

    FRAG_SHADER = """
    // Varying
    // ------------------------------------
    varying vec4 v_color;

    void main()
    {
        gl_FragColor = v_color;
    }
    """

    def __init__(self, scr_dim: tuple):
        view_azimuth = -(3 * np.pi / 4)
        view_elevation = np.pi / 3
        self.view = getView(view_azimuth, view_elevation, 3)

        self.model = np.eye(4, dtype=np.float32)

        self.projection = perspective(40.0, scr_dim[0] / scr_dim[1], 2.0, 10.0)

        self.phi = 0    # Roll
        self.theta = 0  # Pitch
        self.psi = 0    # Yaw

        self.program = gloo.Program(self.VERT_SHADER, self.FRAG_SHADER)
        self.program['a_position'] = gloo.VertexBuffer(self.get_verts())
        self.program['u_projection'] = self.projection
        self.program['u_model'] = self.model
        self.program['u_view'] = self.view
        self.program['u_color'] = 0, 0, 0, 1

        self.draw_floor_refs = True
        self.build_floor_verts()
        self.floor_program = gloo.Program(self.VERT_SHADER, self.FRAG_SHADER)
        self.floor_program['a_position'] = None
        self.floor_program['u_projection'] = self.projection
        self.floor_program['u_model'] = self.model
        self.floor_program['u_view'] = self.view
        self.floor_program['u_color'] = 0.8, 0.8, 0.8, 1

    def get_verts(self):
        verts_y = np.array([(0, -0.4, 0), (0, 0.6, 0), (0.4, -0.7, 0),
                            (0, -0.4, 0), (-0.4, -0.7, 0), (0, 0.6, 0),
                            (0, 0.1, 0), (0, -0.5, 0.15), (0, -0.4, 0)]).astype(np.float32)

        verts = np.array([(0, -0.4, 0), (0, 0.6, 0), (0.4, -0.7, 0),
                          (0, -0.4, 0), (-0.4, -0.7, 0), (0, 0.6, 0),
                          (0, 0.1, 0), (0, -0.5, 0.15), (0, -0.4, 0)]).astype(np.float32)

        angle = deg_to_rad(-90)
        rot_z = np.array([[np.cos(angle), -np.sin(angle), 0],
                          [np.sin(angle), np.cos(angle), 0],
                          [0, 0, 1]])

        return np.array([np.matmul(rot_z, v) for v in verts]).astype(np.float32)

    def build_floor_verts(self):
        scale_fact = 0.75
        self.verts_xz = scale_fact * np.array(
            [(-1, 0, -1), (1, 0, -1), (1, 0, 1), (-1, 0, 1), (-1, 0, -1)]).astype(np.float32)

        self.verts_xy = scale_fact * np.array(
            [(-1, 1, 0), (1, 1, 0), (1, -1, 0), (-1, -1, 0), (-1, 1, 0)]).astype(np.float32)

        self.verts_yz = scale_fact * np.array(
            [(0, 1, -1), (0, 1, 1), (0, -1, 1), (0, -1, -1), (0, 1, -1)]).astype(np.float32)

    def update_screen_size(self, new_size: tuple):
        self.projection = perspective(
            40.0, new_size[0] / new_size[1], 2.0, 10.0)
        self.program['u_projection'] = self.projection
        self.floor_program['u_projection'] = self.projection

    # Angles should be passed in degrees
    def set_ypr_angles(self, ypr: tuple):
        self.phi = -ypr[2]
        self.theta = -ypr[1]
        self.psi = -ypr[0]

        self.model = np.dot(rotate(self.phi, (1, 0, 0)), np.dot(rotate(self.theta, (0, 1, 0)),
                                                                rotate(self.psi, (0, 0, 1))))

        self.program['u_model'] = self.model

    def set_dcm_rot(self, dcm):
        mat44 = np.array([[dcm[0][0], dcm[0][1], dcm[0][2], 0],
                          [dcm[1][0], dcm[1][1], dcm[1][2], 0],
                          [dcm[2][0], dcm[2][1], dcm[2][2], 0],
                          [0, 0, 0, 1]])
        self.model = mat44
        self.program['u_model'] = self.model

    def set_draw_floor_refs(self, draw: bool):
        self.draw_floor_refs = draw

    def run_shaders(self):
        self.program.draw('line_strip')

        if self.draw_floor_refs:
            self.floor_program['a_position'] = gloo.VertexBuffer(self.verts_yz)
            self.floor_program.draw('line_strip')

            self.floor_program['a_position'] = gloo.VertexBuffer(self.verts_xy)
            self.floor_program.draw('line_strip')

            self.floor_program['a_position'] = gloo.VertexBuffer(self.verts_xz)
            self.floor_program.draw('line_strip')


class ChevronCanvas(app.Canvas):
    def __init__(self, *args, **kwargs):
        self.print_callback = None
        scr_size = (800, 600)
        app.Canvas.__init__(self, *args, **kwargs)

        self.chevron = ChevronIndicator(scr_size)

        gloo.set_viewport(0, 0, scr_size[0], scr_size[1])

        gloo.set_clear_color('white')
        gloo.set_state('opaque')

        self.timer = app.Timer('auto', connect=self.on_timer)

        self.show()

        # self.phi = 0
        # self.theta = 0
        # self.psi = 0

    def set_data_obj(self, data_obj):
        self.data_obj = data_obj

    def on_timer(self, event):
        # self.phi += 0.0
        # self.theta += 1.0
        # self.psi += 1.0

        # ypr_tpl = (self.psi, self.theta, self.phi)
        self.data_obj.iterate_data()

        self.chevron.set_ypr_angles(self.data_obj.get_latest_ypr())
        # self.chevron.set_dcm_rot(self.data_obj.get_dcm())

        if self.print_callback is not None:
            self.print_callback(self.data_obj.get_latest_ypr())

        self.update()

    def update_dcm(self, dcm):
        self.chevron.set_dcm_rot(dcm)

        self.update()

    def set_ref_planes(self, draw: bool):
        self.chevron.set_draw_floor_refs(draw)
        self.update()

    def on_key_press(self, event):
        if event.text == 'p' or event.text == 'P':
            if self.timer.running:
                self.timer.stop()
            else:
                self.timer.start()
        elif event.text == 'r' or event.text == 'R':
            # i_data.reset_data()
            self.chevron.set_ypr_angles((0, 0, 0))

        self.update()

    def on_resize(self, event):
        gloo.set_viewport(0, 0, event.physical_size[0], event.physical_size[1])
        self.chevron.update_screen_size(
            (event.physical_size[0], event.physical_size[1]))

    def on_draw(self, event):
        gloo.context.set_current_canvas(self)
        gloo.clear()
        gloo.set_state(blend=True, depth_test=True)

        self.chevron.run_shaders()

    def stop_timer(self):
        self.timer.stop()
