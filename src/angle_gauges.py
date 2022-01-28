import numpy as np
from vispy import gloo
from vispy import app


def deg_to_rad(deg):
    return deg * (np.pi / 180.0)


class AngleGauge:
    # Class that draws a circle with a line indicating a passed angle
    # For orientation visualizations

    CIRCLE_V_SHADER = """
    uniform float radius;
    uniform float radius_frac;
    uniform vec2 scr_dim;
    uniform vec2 draw_dim;
    uniform vec2 center_offset;
    attribute vec2 a_position2d;
    void main (void) {
        float offset_x_fact = center_offset.x / (scr_dim.x / 2.f);
        float offset_y_fact = center_offset.y / (scr_dim.y / 2.f);

        vec2 screen_fact;
        screen_fact.x = draw_dim.x / scr_dim.x;
        screen_fact.y = draw_dim.y / scr_dim.y;        

        float pos_x, pos_y;
        if(radius_frac < 0.01) {
            // Fixed radius in pixels
            pos_x = ((radius / draw_dim.x) * a_position2d.x * screen_fact.x) + offset_x_fact;
            pos_y = ((radius / draw_dim.y) * a_position2d.y * screen_fact.y) + offset_y_fact;
        }
        else {
            // Radius as fraction of total window
            float r_frac_x, r_frac_y;            
            if(draw_dim.x > draw_dim.y) {
                r_frac_x = radius_frac * (draw_dim.y / draw_dim.x);
                r_frac_y = radius_frac;
            }
            else {
                r_frac_x = radius_frac;
                r_frac_y = radius_frac * (draw_dim.x / draw_dim.y);
            }
            pos_x = (r_frac_x * a_position2d.x * screen_fact.x) + offset_x_fact;
            pos_y = (r_frac_y * a_position2d.y * screen_fact.y) + offset_y_fact;
        }
        gl_Position = vec4(pos_x, pos_y, 0.0, 1.0);
    }
    """

    ANGLE_LINE_V_SHADER = """
    uniform float radius_frac;
    uniform vec2 scr_dim;
    uniform vec2 draw_dim;
    uniform vec2 center_offset;
    uniform float line_angle;
    attribute vec2 a_position2d;
    void main (void) {
        // Convert to screen relative coordinates
        float offset_x_fact = center_offset.x / (scr_dim.x / 2.f);
        float offset_y_fact = center_offset.y / (scr_dim.y / 2.f);

        vec2 screen_fact;
        screen_fact.x = draw_dim.x / scr_dim.x;
        screen_fact.y = draw_dim.y / scr_dim.y;        

        float pos_x, pos_y;
        
        // Radius as fraction of total window
        float r_frac_x, r_frac_y;            
        if(draw_dim.x > draw_dim.y) {
            r_frac_x = radius_frac * (draw_dim.y / draw_dim.x);
            r_frac_y = radius_frac;
        }
        else {
            r_frac_x = radius_frac;
            r_frac_y = radius_frac * (draw_dim.x / draw_dim.y);
        }
        
        // Create a rotation matrix (note that line_angle must be passed in radians)
        mat2 rot_matrix = mat2(cos(line_angle), -sin(line_angle),
                               sin(line_angle), cos(line_angle));
        
        // Rotate the points
        vec2 rotated_pos2d = (rot_matrix * a_position2d);

        pos_x = (r_frac_x * rotated_pos2d.x * screen_fact.x) + offset_x_fact;
        pos_y = (r_frac_y * rotated_pos2d.y * screen_fact.y) + offset_y_fact;
    
        gl_Position = vec4(pos_x, pos_y, 0.0, 1.0);
    }
    """

    FRAG_SHADER = """
    void main()
    {
        gl_FragColor = vec4(0,0,0,1);
    }
    """

    def __init__(self, draw_area_dim: tuple, total_screen_dim: tuple, center_offset=(0, 0)):
        self.circle_xy = []
        self.build_circle()

        self.circle_program = gloo.Program(
            self.CIRCLE_V_SHADER, self.FRAG_SHADER)

        self.radius_frac = 0.9

        self.circle_program['a_position2d'] = gloo.VertexBuffer(
            np.array(self.circle_xy).astype(np.float32))
        self.circle_program['radius_frac'] = self.radius_frac
        self.circle_program['radius'] = 0.0

        self.circle_program['scr_dim'] = np.array([total_screen_dim])
        self.circle_program['draw_dim'] = np.array([draw_area_dim])
        self.circle_program['center_offset'] = np.array([center_offset])

        self.ref_line1_xy = []
        self.ref_line2_xy = []
        self.symmetrical_ref_line = False
        # Offset for "resting point" angle (in degrees) (0 = horizontal pointing right, -90 = vertical pointing up)
        self.ref_line_angle_offset = 0
        self.build_ref_line()

        self.line_program = gloo.Program(
            self.ANGLE_LINE_V_SHADER, self.FRAG_SHADER)

        self.line_program['radius_frac'] = self.radius_frac
        self.line_program['scr_dim'] = np.array([total_screen_dim])
        self.line_program['draw_dim'] = np.array([draw_area_dim])
        self.line_program['center_offset'] = np.array([center_offset])

        self.line_program['a_position2d'] = gloo.VertexBuffer(
            np.array(self.ref_line1_xy).astype(np.float32))
        self.line_program['line_angle'] = deg_to_rad(90)

    def build_circle(self, angle_step=1.0):
        step = deg_to_rad(angle_step)
        angle = 0.0
        while (angle < deg_to_rad(360.0)):
            x = np.cos(angle)
            y = np.sin(angle)
            self.circle_xy.append((x, y))
            angle += step

    def build_ref_line(self):
        arrow_tip1 = (1 - 0.1, 0.1)
        arrow_tip2 = (1 - 0.1, -0.1)
        origin = (0, 0)
        line_tip = (1, 0)
        line_tip2 = (-1, 0)

        self.ref_line1_xy = [origin, line_tip,
                             arrow_tip1, line_tip, arrow_tip2]

        if self.symmetrical_ref_line:
            arrow_tip1_symm = (-1 + 0.1, 0.1)
            arrow_tip2_symm = (-1 + 0.1, -0.1)
            self.ref_line2_xy = [origin, (0, 0.15), origin, line_tip2,
                                 arrow_tip1_symm, line_tip2, arrow_tip2_symm]
        else:
            self.ref_line2_xy = [origin, line_tip2]

    def resize(self, new_draw_area: tuple, new_total_screen: tuple, new_offsets: tuple):
        self.circle_program['scr_dim'] = np.array([new_total_screen])
        self.circle_program['draw_dim'] = np.array([new_draw_area])
        self.circle_program['center_offset'] = np.array([new_offsets])

        self.line_program['scr_dim'] = np.array([new_total_screen])
        self.line_program['draw_dim'] = np.array([new_draw_area])
        self.line_program['center_offset'] = np.array([new_offsets])

    def run_shaders(self):
        self.circle_program.draw('line_strip')

        self.line_program['a_position2d'] = gloo.VertexBuffer(
            np.array(self.ref_line1_xy).astype(np.float32))
        self.line_program.draw('line_strip')

        self.line_program['a_position2d'] = gloo.VertexBuffer(
            np.array(self.ref_line2_xy).astype(np.float32))
        self.line_program.draw('line_strip')

    def set_ref_line_symmetry(self, symmetric: bool):
        self.symmetrical_ref_line = symmetric
        self.ref_line1_xy = []
        self.ref_line2_xy = []
        self.build_ref_line()

    def set_line_angle(self, line_angle):
        self.line_program['line_angle'] = deg_to_rad(
            line_angle + self.ref_line_angle_offset)

    def set_line_angle_offset(self, offset_angle):
        self.ref_line_angle_offset = offset_angle


class GaugeCanvas(app.Canvas):
    def __init__(self, *args, **kwargs):
        if 'size' in kwargs.keys():
            canvas_size = kwargs['size']
        else:
            canvas_size = (1200, 400)

        app.Canvas.__init__(self, *args, **kwargs)

        self.data_obj = None

        self.angle_gauge1 = AngleGauge((400, 400), canvas_size, (-400, 0))
        self.angle_gauge2 = AngleGauge((400, 400), canvas_size, (0, 0))
        self.angle_gauge3 = AngleGauge((400, 400), canvas_size, (400, 0))

        self.angle_gauge1.set_line_angle_offset(-90)
        self.angle_gauge2.set_line_angle_offset(-180)

        self.angle_gauge3.set_ref_line_symmetry(True)
        self.angle_gauge3.set_line_angle_offset(0)

        gloo.set_viewport(0, 0, canvas_size[0], canvas_size[1])

        self.context.set_clear_color('silver')
        self.context.set_state('translucent')

        self.timer = app.Timer('auto', connect=self.on_timer)
        # self.timer.start()
        self.angle1 = 0
        self.angle2 = 0
        self.angle3 = 0

        self.show()

    def update_gauges_sizes(self, new_screen_size: tuple):
        total_x = new_screen_size[0]
        total_y = new_screen_size[1]
        gauge_wid = total_x // 3
        gauge1_x_offs = -gauge_wid
        gauge2_x_offs = 0
        gauge3_x_offs = gauge_wid

        self.angle_gauge1.resize((gauge_wid, total_y),
                                 (total_x, total_y), (gauge1_x_offs, 0))

        self.angle_gauge2.resize((gauge_wid, total_y),
                                 (total_x, total_y), (gauge2_x_offs, 0))

        self.angle_gauge3.resize((gauge_wid, total_y),
                                 (total_x, total_y), (gauge3_x_offs, 0))

    def on_key_press(self, event):
        if event.text == 'p' or event.text == 'P':
            if self.timer.running:
                self.timer.stop()
            else:
                self.timer.start()
        elif event.text == 'r' or event.text == 'R':
            self.update_angles((0, 0, 0))

            self.data_obj.reset_data()

            self.update()

    def on_timer(self, event):
        if self.data_obj is None:
            return  # Do nothing

        self.data_obj.iterate_data()

        angles_tpl = self.data_obj.get_latest_ypr()

        # self.angle1 += 1
        # self.angle2 += 0.5
        # self.angle3 += 3

        self.update_angles(angles_tpl)

        # if self.angle1 > 360:
        #     self.angle1 = 0
        # if self.angle2 > 360:
        #     self.angle2 = 0
        # if self.angle3 > 360:
        #     self.angle3 = 0

        self.update()

    def set_data_obj(self, data_obj):
        self.data_obj = data_obj

    def update_angles(self, ypr_tpl):
        self.angle1 = ypr_tpl[0]
        self.angle2 = ypr_tpl[1]
        self.angle3 = -ypr_tpl[2]

        self.angle_gauge1.set_line_angle(self.angle1)
        self.angle_gauge2.set_line_angle(self.angle2)
        self.angle_gauge3.set_line_angle(self.angle3)

        self.update()

    def on_resize(self, event):
        new_canvas_size = event.physical_size
        gloo.set_viewport(0, 0, new_canvas_size[0], new_canvas_size[1])
        self.update_gauges_sizes(new_canvas_size)

    def on_draw(self, event):
        gloo.context.set_current_canvas(self)
        self.context.clear()
        self.angle_gauge1.run_shaders()
        self.angle_gauge2.run_shaders()
        self.angle_gauge3.run_shaders()
