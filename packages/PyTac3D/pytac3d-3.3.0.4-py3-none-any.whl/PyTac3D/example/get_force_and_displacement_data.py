import PyTac3D
import time
import numpy as np
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
        view.put(frame)

        
    # 获得传感器SN码，可用于区分触觉信息来源于哪个触觉传感器
    # get the SN code, which can be used to distinguish which Tac3D sensor the tactile information comes from
    SN = frame['SN']
    print()
    print('Sensor SN:', SN)
    
    # 获得帧序号
    # get the frame index
    frameIndex = frame['index']
    print('Frame index:', frameIndex)
    
    # 获得时间戳
    # get the timestamp
    sendTimestamp = frame['sendTimestamp']
    recvTimestamp = frame['recvTimestamp']

    # 使用frame.get函数通过数据名称"3D_Positions"获得numpy.array类型的三维形貌数据
    # 矩阵的3列分别为x,y,z方向的分量
    # 矩阵的每行对应一个测量点
    # Use the frame.get function to obtain the 3D shape in the numpy.array type through the data name "3D_Positions"
    # The three columns of the matrix are the components in the x, y, and z directions, respectively
    # Each row of the matrix corresponds to a sensing point
    P = frame.get('3D_Positions')
    print('shape of P:', P.shape)

    # 使用frame.get函数通过数据名称"3D_Normals"获得numpy.array类型的表面法线数据
    # 矩阵的3列分别为x,y,z方向的分量
    # 矩阵的每行对应一个测量点
    # Use the frame.get function to obtain the surface normal in the numpy.array type through the data name "3D_Normals"
    # The three columns of the matrix are the components in the x, y, and z directions, respectively
    # Each row of the matrix corresponds to a sensing point
    N = frame.get('3D_Normals')
    print('shape of N:', N.shape)

    # 使用frame.get函数通过数据名称"3D_Displacements"获得numpy.array类型的三维变形场数据
    # 矩阵的3列分别为x,y,z方向的分量
    # 矩阵的每行对应一个测量点
    # Use the frame.get function to obtain the displacement field in the numpy.array type through the data name "3D_Displacements"
    # The three columns of the matrix are the components in the x, y, and z directions, respectively
    # Each row of the matrix corresponds to a sensing point
    D = frame.get('3D_Displacements')
    print('shape of D:', D.shape)

    # 使用frame.get函数通过数据名称"3D_Forces"获得numpy.array类型的三维分布力数据
    # 矩阵的3列分别为x,y,z方向的分量
    # 矩阵的每行对应一个测量点
    # Use the frame.get function to obtain the distributed force in the numpy.array type through the data name "3D_Forces"
    # The three columns of the matrix are the components in the x, y, and z directions, respectively
    # Each row of the matrix corresponds to a sensing point
    F = frame.get('3D_Forces')
    print('shape of F:', F.shape)

    # 使用frame.get函数通过数据名称"3D_ResultantForce"获得numpy.array类型的三维合力的数据指针
    # 矩阵的3列分别为x,y,z方向的分量
    # Use the frame.get function to obtain the resultant force in the numpy.array type through the data name "3D_ResultantForce"
    # The three columns of the matrix are the components in the x, y, and z directions, respectively
    Fr = frame.get('3D_ResultantForce')
    print('shape of Fr:', Fr.shape)

    # 使用frame.get函数通过数据名称"3D_ResultantMoment"获得numpy.array类型的三维合力的数据指针
    # 矩阵的3列分别为x,y,z方向的分量
    # Use the frame.get function to obtain the resultant moment in the numpy.array type through the data name "3D_ResultantMoment"
    # The three columns of the matrix are the components in the x, y, and z directions, respectively
    Mr = frame.get('3D_ResultantMoment')
    print('shape of Mr:', Mr.shape)

    time.sleep(dt)

