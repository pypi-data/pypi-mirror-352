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

# 为tp_id对应序列号的处理模块设置新的网络配置：
# 当处理模块的网络地址存在冲突（如多个处理模块出厂默认IP地址均为192.168.2.100，但又需要连接在用一个局域网内）
# 或处理模块的IP地址与本地计算机网卡的IP地址不处于同一网段时需要进行此设置
new_ip = "192.168.2.100"
new_netmask = "255.255.255.0"
new_gateway = "192.168.2.1"
tac3d_manager.set_config_ip(tp_id, new_ip, new_netmask, new_gateway)

# 更给处理模块的网络配置后需要让处理模块重启网络接口
tac3d_manager.interface_restart(tp_id)
# 重新获取IP地址和其他网络配置
ip, netmask, gateway = tac3d_manager.get_run_ip(tp_id)
