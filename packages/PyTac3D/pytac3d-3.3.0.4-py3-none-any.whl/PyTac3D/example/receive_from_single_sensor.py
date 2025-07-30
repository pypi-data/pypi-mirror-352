import PyTac3D
import time
import numpy as np

SN = 'AD2-0065L'

sensor = PyTac3D.Sensor(port=9988)
sensor.waitForFrame(SN)

analyzer = PyTac3D.Analyzer(SN)

view = PyTac3D.SensorView(SN, PyTac3D.Presets.Mesh_Color_1)
view.setRotation(
    np.matrix( [[1,0,0],
                [0,1,0],
                [0,0,1],
                ], np.float64)
    )
view.setTranslation([0,0,-10])
view.enable_Mesh = True
view.enable_Pointcloud = False
view.enable_Contact = True
view.enable_Displacements = False
view.enable_Normals = False
view.enable_Forces = True
view.enable_Object = False
view.enable_3D_ResForce = False
view.enable_3D_ResMoment = False

def buttonCallback_Restart():
    pass

def buttonCallback_Calibrate():
    sensor.calibrate(SN)

displayer = PyTac3D.Displayer(PyTac3D.Presets.Lights_1)
displayer.buttonCallback_Restart = buttonCallback_Restart
displayer.buttonCallback_Calibrate = buttonCallback_Calibrate
displayer.addView(view)

while displayer.isRunning():
    frame = sensor.getFrame(SN)
    if frame:
        analyzer.detectContact(frame)
        view.put(frame)
    time.sleep(0.03)
