import PyTac3D
import time
import numpy as np
import copy
import os

path = os.path.join(os.path.split(PyTac3D.__file__)[0], 'data/example_1')
SN1 = 'AD2-0065L'
SN2 = SN1 + '-smooth'

loader1 = PyTac3D.DataLoader(path, SN1, skip=0)

analyzer1 = PyTac3D.Analyzer(SN1)

view1 = PyTac3D.SensorView(SN1, PyTac3D.Presets.Mesh_Color_1)
view1.setRotation(
    np.matrix( [[1,0,0],
                [0,1,0],
                [0,0,1],
                ], np.float64)
    )
view1.setTranslation([-15, 0, -10])
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
                [0,1,0],
                [0,0,1],
                ], np.float64)
    )
view2.setTranslation([15, 0,-10])
view2.enable_Mesh = True
view2.enable_Pointcloud = False
view2.enable_Contact = True
view2.enable_Displacements = False
view2.enable_Normals = False
view2.enable_Forces = True
view2.enable_Object = False
view2.enable_3D_ResForce = False
view2.enable_3D_ResMoment = False

config = view2.getConfig()
config['mesh_upsample'] = 3
view2.setConfig(config)

def buttonCallback_Restart():
    global restartFlag
    restartFlag = True

def buttonCallback_Calibrate():
    pass

displayer = PyTac3D.Displayer(PyTac3D.Presets.Lights_1)
displayer.buttonCallback_Restart = buttonCallback_Restart
displayer.buttonCallback_Calibrate = buttonCallback_Calibrate
displayer.addView(view1)
displayer.addView(view2)

dt = 0.03
restartFlag = True

while displayer.isRunning():
    if restartFlag:
        loader1.reset()
        frame1, t1, endFlag1 = loader1.get()
        startTime = time.time() - t1
        restartFlag = False

    currentTime = time.time() - startTime

    # 获取数据，时间对齐
    while not endFlag1 and t1 < currentTime:
        frame1, t1, endFlag1 = loader1.get()

    
    # 到达最后一帧时，重新开始
    if endFlag1:
        restartFlag = True

    if frame1:
        analyzer1.detectContact(frame1)
        view1.put(frame1)

        frame2 = copy.deepcopy(frame1)
        frame2["SN"] = SN2
        view2.put(frame2)

    time.sleep(dt)

