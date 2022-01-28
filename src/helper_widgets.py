import wx


class QuatDisplay(wx.Panel):
    def __init__(self, parent, id):
        wx.Panel.__init__(self, parent, id)
        self.lbl_w = wx.StaticText(self, -1, "W")
        self.lbl_x = wx.StaticText(self, -1, "X")
        self.lbl_y = wx.StaticText(self, -1, "Y")
        self.lbl_z = wx.StaticText(self, -1, "Z")
        self.txt_w = wx.TextCtrl(self, wx.ID_ANY, "0.000000", size=(70, 20))
        self.txt_x = wx.TextCtrl(self, wx.ID_ANY, "0.000000", size=(70, 20))
        self.txt_y = wx.TextCtrl(self, wx.ID_ANY, "0.000000", size=(70, 20))
        self.txt_z = wx.TextCtrl(self, wx.ID_ANY, "0.000000", size=(70, 20))

        self.m_sizer = wx.StaticBoxSizer(
            wx.HORIZONTAL, self, "Quaternion elements")
        self.m_sizer.Add(self.lbl_w, 0, wx.CENTER | wx.ALL, 2)
        self.m_sizer.Add(self.txt_w, 0, wx.CENTER | wx.ALL, 2)
        self.m_sizer.AddSpacer(10)
        self.m_sizer.Add(self.lbl_x, 0, wx.CENTER | wx.ALL, 2)
        self.m_sizer.Add(self.txt_x, 0, wx.CENTER | wx.ALL, 2)
        self.m_sizer.AddSpacer(10)
        self.m_sizer.Add(self.lbl_y, 0, wx.CENTER | wx.ALL, 2)
        self.m_sizer.Add(self.txt_y, 0, wx.CENTER | wx.ALL, 2)
        self.m_sizer.AddSpacer(10)
        self.m_sizer.Add(self.lbl_z, 0, wx.CENTER | wx.ALL, 2)
        self.m_sizer.Add(self.txt_z, 0, wx.CENTER | wx.ALL, 2)

        self.SetSizerAndFit(self.m_sizer)

    def set_quat(self, quat):
        w = "{:6f}".format(quat[0])
        x = "{:6f}".format(quat[1])
        y = "{:6f}".format(quat[2])
        z = "{:6f}".format(quat[3])

        self.txt_w.SetValue(w)
        self.txt_x.SetValue(x)
        self.txt_y.SetValue(y)
        self.txt_z.SetValue(z)


class RateSliders(wx.Panel):
    def __init__(self, parent, id, data_obj):
        wx.Panel.__init__(self, parent, id)

        self.data_obj = data_obj

        self.lbl_x = wx.StaticText(self, -1, "Roll (X)")
        self.lbl_y = wx.StaticText(self, -1, "Pitch (Y)")
        self.lbl_z = wx.StaticText(self, -1, "Yaw (Z))")

        self.txt_x = wx.TextCtrl(
            self, wx.ID_ANY, "0.0", size=(50, 20), style=wx.TE_PROCESS_ENTER)
        self.txt_y = wx.TextCtrl(
            self, wx.ID_ANY, "0.0", size=(50, 20), style=wx.TE_PROCESS_ENTER)
        self.txt_z = wx.TextCtrl(
            self, wx.ID_ANY, "0.0", size=(50, 20), style=wx.TE_PROCESS_ENTER)

        self.slider_x = wx.Slider(
            self, wx.ID_ANY, 0, 0, 360, size=(30, 300), style=wx.SL_VERTICAL | wx.SL_INVERSE)
        self.slider_y = wx.Slider(
            self, wx.ID_ANY, 0, 0, 360, size=(30, 300), style=wx.SL_VERTICAL | wx.SL_INVERSE)
        self.slider_z = wx.Slider(
            self, wx.ID_ANY, 0, 0, 360, size=(30, 300), style=wx.SL_VERTICAL | wx.SL_INVERSE)

        self.btn_plus_x = wx.ToggleButton(self, -1, "+", size=(30, 30))
        self.btn_minus_x = wx.ToggleButton(self, -1, "-", size=(30, 30))

        self.btn_plus_y = wx.ToggleButton(self, -1, "+", size=(30, 30))
        self.btn_minus_y = wx.ToggleButton(self, -1, "-", size=(30, 30))

        self.btn_plus_z = wx.ToggleButton(self, -1, "+", size=(30, 30))
        self.btn_minus_z = wx.ToggleButton(self, -1, "-", size=(30, 30))

        self.Bind(wx.EVT_TOGGLEBUTTON, self.on_btn_plus_x, self.btn_plus_x)
        self.Bind(wx.EVT_TOGGLEBUTTON, self.on_btn_plus_y, self.btn_plus_y)
        self.Bind(wx.EVT_TOGGLEBUTTON, self.on_btn_plus_z, self.btn_plus_z)

        self.Bind(wx.EVT_TOGGLEBUTTON, self.on_btn_minus_x, self.btn_minus_x)
        self.Bind(wx.EVT_TOGGLEBUTTON, self.on_btn_minus_y, self.btn_minus_y)
        self.Bind(wx.EVT_TOGGLEBUTTON, self.on_btn_minus_z, self.btn_minus_z)

        self.Bind(wx.EVT_TEXT_ENTER, self.on_txt_enter, self.txt_x)
        self.Bind(wx.EVT_TEXT_ENTER, self.on_txt_enter, self.txt_y)
        self.Bind(wx.EVT_TEXT_ENTER, self.on_txt_enter, self.txt_z)

        self.Bind(wx.EVT_SCROLL_THUMBTRACK,
                  self.on_slider_track, self.slider_x)
        self.Bind(wx.EVT_SCROLL_THUMBTRACK,
                  self.on_slider_track, self.slider_y)
        self.Bind(wx.EVT_SCROLL_THUMBTRACK,
                  self.on_slider_track, self.slider_z)

        self.m_sizer = wx.StaticBoxSizer(
            wx.HORIZONTAL, self, "Body rates (deg/s)")
        self.x_sizer = wx.BoxSizer(wx.VERTICAL)
        self.y_sizer = wx.BoxSizer(wx.VERTICAL)
        self.z_sizer = wx.BoxSizer(wx.VERTICAL)

        self.x_sizer.Add(self.lbl_x, 0, wx.CENTER | wx.ALL, 2)
        self.x_sizer.Add(self.txt_x, 0, wx.CENTER | wx.ALL, 2)
        self.x_sizer.Add(self.slider_x, 0, wx.CENTER | wx.ALL, 2)
        self.x_sizer.AddSpacer(10)
        self.x_sizer.Add(self.btn_plus_x, 0, wx.CENTER | wx.ALL, 0)
        self.x_sizer.Add(self.btn_minus_x, 0, wx.CENTER | wx.ALL, 0)

        self.y_sizer.Add(self.lbl_y, 0, wx.CENTER | wx.ALL, 2)
        self.y_sizer.Add(self.txt_y, 0, wx.CENTER | wx.ALL, 2)
        self.y_sizer.Add(self.slider_y, 0, wx.CENTER | wx.ALL, 2)
        self.y_sizer.AddSpacer(10)
        self.y_sizer.Add(self.btn_plus_y, 0, wx.CENTER | wx.ALL, 0)
        self.y_sizer.Add(self.btn_minus_y, 0, wx.CENTER | wx.ALL, 0)

        self.z_sizer.Add(self.lbl_z, 0, wx.CENTER | wx.ALL, 2)
        self.z_sizer.Add(self.txt_z, 0, wx.CENTER | wx.ALL, 2)
        self.z_sizer.Add(self.slider_z, 0, wx.CENTER | wx.ALL, 2)
        self.z_sizer.AddSpacer(10)
        self.z_sizer.Add(self.btn_plus_z, 0, wx.CENTER | wx.ALL, 0)
        self.z_sizer.Add(self.btn_minus_z, 0, wx.CENTER | wx.ALL, 0)

        self.m_sizer.Add(self.z_sizer, 0, wx.CENTER | wx.ALL, 2)
        self.m_sizer.AddSpacer(25)
        self.m_sizer.Add(self.y_sizer, 0, wx.CENTER | wx.ALL, 2)
        self.m_sizer.AddSpacer(25)
        self.m_sizer.Add(self.x_sizer, 0, wx.CENTER | wx.ALL, 2)

        self.init_state()

        self.SetSizerAndFit(self.m_sizer)

    def init_state(self):
        self.txt_x.SetValue('0.0')
        self.txt_y.SetValue('0.0')
        self.txt_z.SetValue('90.0')

        self.slider_z.SetValue(90)

        self.btn_plus_x.SetValue(True)
        self.btn_minus_x.SetValue(False)

        self.btn_plus_y.SetValue(True)
        self.btn_minus_y.SetValue(False)

        self.btn_plus_z.SetValue(True)
        self.btn_minus_z.SetValue(False)

        self.set_rates()

    def set_rates(self):
        # Set based on values in TextCtrls
        rates_tpl = (float(self.txt_x.GetValue()),
                     float(self.txt_y.GetValue()),
                     float(self.txt_z.GetValue()))

        self.data_obj.set_body_rates(rates_tpl)

    def on_txt_enter(self, event):
        a = self.txt_x.GetValue()
        self.slider_x.SetValue(int(float(self.txt_x.GetValue())))
        self.slider_y.SetValue(int(float(self.txt_y.GetValue())))
        self.slider_z.SetValue(int(float(self.txt_z.GetValue())))

        self.set_rates()

    def on_slider_track(self, event):
        x_val = self.slider_x.GetValue()
        y_val = self.slider_y.GetValue()
        z_val = self.slider_z.GetValue()

        x_sign = 1 if self.btn_plus_x.GetValue() else -1
        y_sign = 1 if self.btn_plus_y.GetValue() else -1
        z_sign = 1 if self.btn_plus_z.GetValue() else -1

        self.txt_x.SetValue(str(x_val * x_sign))
        self.txt_y.SetValue(str(y_val * y_sign))
        self.txt_z.SetValue(str(z_val * z_sign))

        self.set_rates()

    def on_btn_plus_x(self, event):
        if self.btn_plus_x.GetValue():
            self.btn_minus_x.SetValue(False)
            if float(self.txt_x.GetValue()) < 0.0:
                new_val = float(self.txt_x.GetValue()) * -1.0
                self.txt_x.SetValue("{:.2f}".format(new_val))
                self.set_rates()

    def on_btn_plus_y(self, event):
        if self.btn_plus_y.GetValue():
            self.btn_minus_y.SetValue(False)
            if float(self.txt_y.GetValue()) < 0.0:
                new_val = float(self.txt_y.GetValue()) * -1.0
                self.txt_y.SetValue("{:.2f}".format(new_val))
                self.set_rates()

    def on_btn_plus_z(self, event):
        if self.btn_plus_z.GetValue():
            self.btn_minus_z.SetValue(False)
            if float(self.txt_z.GetValue()) < 0.0:
                new_val = float(self.txt_z.GetValue()) * -1.0
                self.txt_z.SetValue("{:.2f}".format(new_val))
                self.set_rates()

    def on_btn_minus_x(self, event):
        if self.btn_minus_x.GetValue():
            self.btn_plus_x.SetValue(False)
            if float(self.txt_x.GetValue()) > 0.0:
                new_val = float(self.txt_x.GetValue()) * -1.0
                self.txt_x.SetValue("{:.2f}".format(new_val))
                self.set_rates()

    def on_btn_minus_y(self, event):
        if self.btn_minus_y.GetValue():
            self.btn_plus_y.SetValue(False)
            if float(self.txt_y.GetValue()) > 0.0:
                new_val = float(self.txt_y.GetValue()) * -1.0
                self.txt_y.SetValue("{:.2f}".format(new_val))
                self.set_rates()

    def on_btn_minus_z(self, event):
        if self.btn_minus_z.GetValue():
            self.btn_plus_z.SetValue(False)
            if float(self.txt_z.GetValue()) > 0.0:
                new_val = float(self.txt_z.GetValue()) * -1.0
                self.txt_z.SetValue("{:.2f}".format(new_val))
                self.set_rates()
