import wx
import numpy as np

from angle_gauges import GaugeCanvas
from chevron_viz import ChevronCanvas
from orientation import GenRatesData
from helper_widgets import QuatDisplay, RateSliders


class wxVP_Gauge(wx.Panel):
    def __init__(self, parent, ID, ini_size):
        wx.Panel.__init__(self, parent, ID, size=ini_size)

        self.canvas = GaugeCanvas(
            app="wx", parent=self, keys='interactive', size=ini_size)

        self.canvas.set_data_obj(i_data)

        self.Bind(wx.EVT_SIZE, self.OnSize)

    def ShowCanvas(self):
        self.canvas.show()

    def StopTimer(self):
        self.canvas.stop_timer()

    def OnSize(self, event):
        size_x = event.GetSize()[0]
        size_y = event.GetSize()[1]
        self.canvas.size = (size_x, size_y)


class wxVP_Chevron(wx.Panel):
    def __init__(self, parent, ID, ini_size, print_callback=None):
        wx.Panel.__init__(self, parent, ID, size=ini_size)

        self.canvas = ChevronCanvas(app="wx", parent=self, keys='interactive')

        self.canvas.set_data_obj(i_data)

        if print_callback is not None:
            self.canvas.print_callback = print_callback

        self.Bind(wx.EVT_SIZE, self.OnSize)

    def ShowCanvas(self):
        self.canvas.show()

    def StopTimer(self):
        self.canvas.stop_timer()

    def OnSize(self, event):
        size_x = event.GetSize()[0]
        size_y = event.GetSize()[1]
        self.canvas.size = (size_x, size_y)


class MainFrame(wx.Frame):
    def __init__(self):
        wx.Frame.__init__(self, None, -1, "Euler angles tracking - Vispy + wxWidgets",
                          wx.DefaultPosition, size=(1200, 1000))

        MenuBar = wx.MenuBar()
        file_menu = wx.Menu()
        file_menu.Append(wx.ID_EXIT, "&Quit")
        self.Bind(wx.EVT_MENU, self.on_quit, id=wx.ID_EXIT)
        self.Bind(wx.EVT_SHOW, self.on_show)
        MenuBar.Append(file_menu, "&File")
        self.SetMenuBar(MenuBar)

        self.main_panel = wx.Panel(self)

        self.chevron_canvas = wxVP_Chevron(self.main_panel, wx.ID_ANY,
                                           (800, 600), self.PrintAngles)

        self.gauge_canvas = wxVP_Gauge(self.main_panel, wx.ID_ANY, (1200, 400))

        self.slider_controls = RateSliders(self.main_panel, wx.ID_ANY, i_data)

        self.quat_display = QuatDisplay(self.main_panel, wx.ID_ANY)

        self.lbl_x_lbl = wx.StaticText(self.main_panel, -1, "Roll:")
        self.lbl_y_lbl = wx.StaticText(self.main_panel, -1, "Pitch:")
        self.lbl_z_lbl = wx.StaticText(self.main_panel, -1, "Yaw:")

        self.lbl_x_pos = wx.StaticText(
            self.main_panel, -1, "")
        self.lbl_y_pos = wx.StaticText(
            self.main_panel, -1, "")
        self.lbl_z_pos = wx.StaticText(
            self.main_panel, -1, "")

        self.lbl_x_pos.SetLabel("Test X")
        self.lbl_y_pos.SetLabel("Test Y")
        self.lbl_z_pos.SetLabel("Test Z")

        self.btn_quit = wx.Button(self.main_panel, -1, "Quit")
        self.btn_start_stop = wx.Button(self.main_panel, -1, "Start")
        self.btn_reset = wx.Button(self.main_panel, -1, "Reset")

        self.cb_angle_refs = wx.CheckBox(
            self.main_panel, wx.ID_ANY, "Show ref. planes")
        self.cb_angle_refs.SetValue(True)

        self.Bind(wx.EVT_BUTTON, self.on_quit, self.btn_quit)
        self.Bind(wx.EVT_BUTTON, self.on_btn_start, self.btn_start_stop)
        self.Bind(wx.EVT_BUTTON, self.on_btn_reset, self.btn_reset)

        self.Bind(wx.EVT_CHECKBOX, self.on_cb_angle_refs, self.cb_angle_refs)

        self.tick_timer = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self.on_tick_timer, self.tick_timer)
        self.tick_size = 1.0 / 60.0   # So we have roughly 60fps refresh
        self.timer_running = False

        self.main_sizer = wx.BoxSizer(wx.VERTICAL)
        self.hsizer1 = wx.BoxSizer(wx.HORIZONTAL)
        self.hsizer2 = wx.BoxSizer(wx.HORIZONTAL)

        self.hsizer1.Add(self.chevron_canvas, 1,
                         wx.CENTER | wx.EXPAND | wx. ALL, 2)
        self.hsizer1.Add(self.slider_controls, 0,
                         wx.CENTER | wx.EXPAND | wx.ALL, 2)

        self.hsizer2.Add(self.quat_display, 0, wx.CENTER | wx.ALL, 2)
        self.hsizer2.AddSpacer(10)
        self.hsizer2.Add(self.lbl_z_lbl, 0, wx.CENTER | wx.ALL, 2)
        self.hsizer2.Add(self.lbl_z_pos, 0, wx.CENTER | wx.ALL, 2)
        self.hsizer2.AddSpacer(5)
        self.hsizer2.Add(self.lbl_y_lbl, 0, wx.CENTER | wx.ALL, 2)
        self.hsizer2.Add(self.lbl_y_pos, 0, wx.CENTER | wx.ALL, 2)
        self.hsizer2.AddSpacer(5)
        self.hsizer2.Add(self.lbl_x_lbl, 0, wx.CENTER | wx.ALL, 2)
        self.hsizer2.Add(self.lbl_x_pos, 0, wx.CENTER | wx.ALL, 2)
        self.hsizer2.AddSpacer(20)
        self.hsizer2.Add(self.btn_start_stop, 0, wx.CENTER | wx.ALL, 2)
        self.hsizer2.AddSpacer(10)
        self.hsizer2.Add(self.btn_reset, 0, wx.CENTER | wx.ALL, 2)
        self.hsizer2.AddSpacer(40)
        self.hsizer2.Add(self.btn_quit, 0, wx.CENTER | wx.ALL, 2)
        self.hsizer2.AddSpacer(20)
        self.hsizer2.Add(self.cb_angle_refs, 0, wx.CENTER | wx.ALL, 2)

        self.main_sizer.Add(self.gauge_canvas, 1,
                            wx.CENTER | wx.EXPAND | wx.ALL, 2)
        self.main_sizer.Add(self.hsizer1, 1, wx.CENTER | wx.EXPAND | wx.ALL, 2)
        self.main_sizer.Add(self.hsizer2, 0, wx.CENTER | wx.ALL, 2)

        self.main_panel.SetSizer(self.main_sizer)
        self.main_panel.Fit()

    def OnMouse(self, event):
        self.lbl_x_pos.SetLabel(str(event.pos[0]))
        self.lbl_y_pos.SetLabel(str(event.pos[1]))

    def PrintAngles(self, angles):
        self.lbl_x_pos.SetLabel("{:.2f}".format(angles[2]))
        self.lbl_y_pos.SetLabel("{:.2f}".format(angles[1]))
        self.lbl_z_pos.SetLabel("{:.2f}".format(angles[0]))

    def on_tick_timer(self, event):
        i_data.iterate_data()

        # self.chevron_canvas.canvas.chevron.set_ypr_angles(
        #     i_data.get_latest_ypr())
        self.chevron_canvas.canvas.update_dcm(i_data.get_dcm())

        self.gauge_canvas.canvas.update_angles(i_data.get_latest_ypr())

        self.chevron_canvas.canvas.update()
        self.gauge_canvas.canvas.update()

        self.quat_display.set_quat(i_data.attitude_q)

        self.PrintAngles(i_data.get_latest_ypr())

    def on_btn_start(self, event):
        if self.timer_running:
            # Stop the timer
            self.tick_timer.Stop()
            self.timer_running = False
            self.btn_start_stop.SetLabel("Start")
        else:
            # Start the timer
            self.tick_timer.Start(self.tick_size * 1000)
            self.timer_running = True
            self.btn_start_stop.SetLabel("Stop")

    def on_btn_reset(self, event):
        zero_angles = (0, 0, 0)
        self.chevron_canvas.canvas.chevron.set_ypr_angles(zero_angles)
        self.gauge_canvas.canvas.update_angles(zero_angles)
        self.PrintAngles(zero_angles)

        i_data.reset_data()

        self.chevron_canvas.canvas.update()
        self.gauge_canvas.canvas.update()

    def on_cb_angle_refs(self, event):
        self.chevron_canvas.canvas.set_ref_planes(
            self.cb_angle_refs.GetValue())

    def on_quit(self, event):
        self.chevron_canvas.StopTimer()
        # self.gauge_canvas2.StopTimer()
        self.Close(True)

    def on_show(self, event):
        # self.canvas.show()
        event.Skip()


if __name__ == '__main__':
    i_data = GenRatesData()
    myapp = wx.App(0)
    frame = MainFrame()
    frame.Show(True)
    myapp.MainLoop()
