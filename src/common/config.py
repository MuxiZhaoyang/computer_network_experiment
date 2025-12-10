"""
配置文件模块
定义系统全局配置参数
"""

# 网络配置
DEFAULT_UDP_PORT = 8888  # UDP通信端口
DEFAULT_TCP_PORT = 8889  # TCP文件传输端口
BROADCAST_ADDRESS = '255.255.255.255'  # 广播地址
BUFFER_SIZE = 4096  # 接收缓冲区大小
FILE_CHUNK_SIZE = 8192  # 文件传输块大小

# 消息关键字
DISCOVERY_KEYWORD = "CHAT_DISCOVER"  # 发现组员关键字
JOIN_KEYWORD = "CHAT_JOIN"  # 加入组关键字
LEAVE_KEYWORD = "CHAT_LEAVE"  # 离开组关键字
REFRESH_KEYWORD = "CHAT_REFRESH"  # 刷新请求关键字

# 超时设置
SOCKET_TIMEOUT = 5  # socket超时时间（秒）
DISCOVERY_TIMEOUT = 3  # 发现组员超时时间（秒）

# 界面配置
WINDOW_TITLE = "简易即时通信工具"
WINDOW_WIDTH = 1000
WINDOW_HEIGHT = 700

# 文件传输配置
MAX_FILE_SIZE = 100 * 1024 * 1024  # 最大文件大小 100MB
DOWNLOAD_DIR = "downloads"  # 下载文件保存目录

