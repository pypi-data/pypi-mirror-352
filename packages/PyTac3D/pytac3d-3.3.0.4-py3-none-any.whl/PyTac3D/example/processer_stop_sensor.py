import PyTac3D

# GUI工具：https://gitee.com/sxhzzlw/tac3d-utils

# Tac3DClient的主要功能是与处理模块（Tac3D Processor）通信
# 更改处理模块的参数设置，启动或停止处理模块上连接的传感器

# 初始化Tac3d_Manager
# 此处传入的IP地址为本地计算机与处理模块连接的网卡的IP地址
# 此IP地址需要手动设置为静态IP
tac3d_manager = PyTac3D.Manager("192.168.2.1")

# 获取可连接的处理模块列表
# tp_num为检测到的可用的处理模块的数量
# tp_list为检测到的可用的处理模块的序列号的列表
# 当计算机和多个处理模块连接在同一个交换机上时，可同时检测到多个处理模块
tp_num, tp_list = tac3d_manager.get_tp_id()

# 从列表中取出检测到的第一个处理模块的序列号
tp_id = tp_list[0]

# 获取处理模块的网络配置信息
# 包括IP地址、子网掩码和网关
ip, netmask, gateway = tac3d_manager.get_run_ip(tp_id)
        
# 通过指定IP地址，与指定的处理模块建立TCP连接，以执行有关Tac3D传感器的操作
tac3d_manager.connect_server(ip)

# 获取配置文件中已导入的配置列表
# cfg_num为处理模块中已导入的配置文件数量
# cfg_list为处理模块中已导入的配置文件名称的列表
# sn_list为处理模块中已导入的配置文件对应的传感器SN的列表
# 通常情况下cfg_list与sn_list的内容是相同的
cfg_num, cfg_list, sn_list = tac3d_manager.get_config()

# 检查处理模块上Tac3D传感器主程序是否正在运行
print(tac3d_manager.stat_tac3d(cfg_list[0]))

###########################################################
# 以下代码功能为中止Tac3D主程序、导出日志并关闭处理模块电源
###########################################################


# 中止处理模块上指定SN的Tac3D传感器主程序
tac3d_manager.stop_tac3d(cfg_list[0])

# 从处理模块中提取指定SN的Tac3D传感器主程序运行日志，在传感器启动或运行异常时，请向技术人员提供此日志以排查故障原因
tac3d_manager.get_log(sn_list[0], sn_list[0] + "_log.zip")

# 断开与处理模块的连接，此操作只会断开Tac3d_Manager与处理模块的TCP连接，不会停止Tac3D主程序的运行
tac3d_manager.disconnect_server()

# 关闭指定的处理模块（需要按电源键才能再次开机）
# tac3d_manager.system_shutdown(tp_id)
