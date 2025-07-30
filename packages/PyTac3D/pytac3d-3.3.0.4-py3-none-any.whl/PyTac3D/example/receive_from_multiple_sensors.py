import PyTac3D
import time
import numpy as np

SN1 = 'AD2-0065L'
SN2 = 'AD2-0080R'

sensor = PyTac3D.Sensor(port=9988)
sensor.waitForFrame(SN1)
sensor.waitForFrame(SN2)

analyzer1 = PyTac3D.Analyzer(SN1)
analyzer2 = PyTac3D.Analyzer(SN2)

view1 = PyTac3D.SensorView(SN1, PyTac3D.Presets.Mesh_Color_1)
view1.setRotation(
    np.matrix( [[1,0,0],
                [0,1,0],
                [0,0,1],
                ], np.float64)
    )
view1.setTranslation([0,0,-15])
view1.enable_Mesh = True
view1.enable_Pointcloud = False
view1.enable_Contact = True
view1.enable_Displacements = False
view1.enable_Normals = False
view1.enable_Forces = True
view1.enable_Object = False
view1.enable_3D_ResForce = False
view1.enable_3D_ResMoment = False

view2 = PyTac3D.SensorView(SN2, PyTac3D.Presets.Mesh_Color_1)
view2.setRotation(
    np.matrix( [[1,0,0],
                [0,-1,0],
                [0,0,-1],
                ], np.float64)
    )
view2.setTranslation([0,0,15])
view2.enable_Mesh = True
view2.enable_Pointcloud = False
view2.enable_Contact = True
view2.enable_Displacements = False
view2.enable_Normals = False
view2.enable_Forces = True
view2.enable_Object = False
view2.enable_3D_ResForce = False
view2.enable_3D_ResMoment = False      

def buttonCallback_Restart():
    pass

def buttonCallback_Calibrate():
    sensor.calibrate(SN1)
    sensor.calibrate(SN2)
    
displayer = PyTac3D.Displayer(PyTac3D.Presets.Lights_1)
displayer.buttonCallback_Restart = buttonCallback_Restart
displayer.buttonCallback_Calibrate = buttonCallback_Calibrate
displayer.addView(view1)
displayer.addView(view2)

while displayer.isRunning():
    frame1 = sensor.getFrame(SN1)
    frame2 = sensor.getFrame(SN2)

    if frame1:
        analyzer1.detectContact(frame1)
        view1.put(frame1)

    if frame2:
        analyzer2.detectContact(frame2)
        view2.put(frame2)
    time.sleep(0.03)
