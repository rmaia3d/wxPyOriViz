# wxPyOriViz
 A vispy + wxPython 3D orientation visualization tool

 I wrote this tool as a helper in developing attitude and orientation tracking algorithms from IMU data (i.e., body rates). It does simple first order integration of the body rates and calculates the global (inertial) frame orientation and using vispy, uses OpenGL to plot Euler angle gauges (from left to right, yaw, pitch and row) and a general 3D scene with a wireframe chevron shape filling in for a plane or whatever other object orientation is being simulated/visualized.

 The GUI is based on wxPython (wxWidgets python wrapper).

 # Dependencies
 
 - Python 3.6 and up
 - Vispy
 - Numpy
 - wxPython

 You can use pip to install of these dependencies if needed
 ```
 pip install vispy
 pip install numpy
 pip install wxPython
 ```

 # Setup and running

 Ensure all *.py files from the /src folder are in the same folder and just run the main.py file. If you have all the dependencies properly installed, the app should just run and present you with this interface:

 ![ss1]

 # Misc notes

This is a initial and rather rough version, no guarantees of proper functionality are given. Use at your own risk.
I have tried to comment the code in the most critical sections, but there's no extensive commenting/documentation available.

This is mostly an experimental tool for my own projects, and I'm sharing the code here so maybe it can help as an insight or example implementation to other people needing a similar tool. Also works as an example how to integrate a vispy canvas (multiple canvas, actually) into a wxPython GUI framework.

The code for has been ran in Windows 10, MacOS 10.15 and Linux Ubuntu 20.04.

 [ss1]: https://github.com/rmaia3d/wxPyOriViz/blob/master/images/screen1.png


