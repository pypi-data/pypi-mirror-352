import PyTac3D
import time
import numpy as np
import os

path = os.path.join(os.path.split(PyTac3D.__file__)[0], 'data/example_2')
SN1 = 'HDL1-GWH0021'
SN2 = 'HDL1-GWH0022'

loader1 = PyTac3D.DataLoader(path, SN1, skip=0)
loader2 = PyTac3D.DataLoader(path, SN2, skip=0)

analyzer1 = PyTac3D.Analyzer(SN1)
analyzer2 = PyTac3D.Analyzer(SN2)

view1 = PyTac3D.SensorView(SN1, PyTac3D.Presets.Mesh_Color_1)
view1.setRotation(
    np.matrix( [[1,0,0],
                [0,1,0],
                [0,0,1],
                ], np.float64)
    )
view1.setTranslation([0,0,-15.5])
view1.enable_Mesh = True
view1.enable_Pointcloud = False
view1.enable_Contact = True
view1.enable_Displacements = False
view1.enable_Normals = False
view1.enable_Forces = True
view1.enable_Object = True
view1.enable_3D_ResForce = False
view1.enable_3D_ResMoment = False

view2 = PyTac3D.SensorView(SN2, PyTac3D.Presets.Mesh_Color_1)
view2.setRotation(
    np.matrix( [[1,0,0],
                [0,-1,0],
                [0,0,-1],
                ], np.float64)
    )
view2.setTranslation([0,0,15.5])
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
        loader2.reset()
        frame1, t1, endFlag1 = loader1.get()
        frame2, t2, endFlag2 = loader2.get()
        startTime = time.time() - max(t1, t2)
        restartFlag = False

    currentTime = time.time() - startTime

    # 获取数据，时间对齐
    while not endFlag1 and t1 < currentTime:
        frame1, t1, endFlag1 = loader1.get()

    while not endFlag2 and t2 < currentTime:
        frame2, t2, endFlag2 = loader2.get()
    
    # 到达最后一帧时，重新开始
    if endFlag1 or endFlag2:
        restartFlag = True

    if frame1:
        analyzer1.detectObjects(frame1)
        view1.put(frame1)

    if frame2:
        analyzer2.detectContact(frame2)
        view2.put(frame2)

    time.sleep(dt)

