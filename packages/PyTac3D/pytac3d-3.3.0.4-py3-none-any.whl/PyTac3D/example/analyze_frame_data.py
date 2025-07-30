import PyTac3D
import time
import numpy as np
import cv2
import os

path = os.path.join(os.path.split(PyTac3D.__file__)[0], 'data/example_1')
SN = 'AD2-0065L'

loader = PyTac3D.DataLoader(path, SN, skip=0)

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
view.enable_Object = True
view.enable_3D_ResForce = False
view.enable_3D_ResMoment = False

def buttonCallback_Restart():
    global restartFlag
    restartFlag = True

def buttonCallback_Calibrate():
    pass

displayer = PyTac3D.Displayer(PyTac3D.Presets.Lights_1)
displayer.buttonCallback_Restart = buttonCallback_Restart
displayer.buttonCallback_Calibrate = buttonCallback_Calibrate
displayer.addView(view)

dt = 0.03
restartFlag = True
cv2.namedWindow('force', 0)
cv2.namedWindow('displacements', 0)
cv2.namedWindow('resample_force', 0)
while displayer.isRunning():
    if restartFlag:
        loader.reset()
        frame, t, endFlag = loader.get()
        startTime = time.time() - t
        restartFlag = False

    currentTime = time.time() - startTime

    # 获取数据，时间对齐
    while not endFlag and t < currentTime:
        frame, t, endFlag = loader.get()

    # 到达最后一帧时，重新开始
    if endFlag:
        restartFlag = True

    if frame:
        print()
        print('Frame index:', frame['index'])

        # 接触检测
        print('  ==Before detectContact==')
        print('    ContactRegion:', type(frame.get('ContactRegion')))
        print('    ContactRegions:', type(frame.get('ContactRegions')))
        
        analyzer.detectContact(frame)
        print('  ==After detectContact==')
        print('    ContactRegion:', type(frame.get('ContactRegion')))
        print('    ContactRegions:', type(frame.get('ContactRegions')))

        # 形状检测
        print('  ==Before detectObjects==')
        regions = frame.get('ContactRegions')
        for region in regions:    
            print('    object:', type(region.get('object')))

        analyzer.detectObjects(frame)
        print('  ==After detectObjects==')
        regions = frame.get('ContactRegions')
        for region in regions:    
            print('    object:', region.get('object'))

        # nx3矩阵的xyz坐标形式的数据转换为3通道Mat
        Dmat = analyzer.points2matrix(frame['3D_Displacements'])
        Fmat = analyzer.points2matrix(frame['3D_Forces'])

        cv2.imshow('force', Fmat * 10.0 + 0.5)
        cv2.imshow('displacements', Dmat * 1.0 + 0.5)

        # nx3矩阵的xyz坐标形式的数据，先按40x40重采样，再转换为3通道Mat
        resampleShape = (40, 40) 
        F_resample = analyzer.resample(frame['3D_Forces'], shape_out=resampleShape)
        Fmat_resample = analyzer.points2matrix(F_resample, shape=resampleShape)
        cv2.imshow('resample_force', Fmat_resample * 10.0 + 0.5)

        cv2.waitKey(int(dt*1000))
        view.put(frame)
    else:
        time.sleep(dt)

