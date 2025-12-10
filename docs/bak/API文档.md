# API 文档

## 公共模块（common）

### config.py - 配置参数

```python
# 网络配置
DEFAULT_UDP_PORT = 8888          # UDP通信端口
DEFAULT_TCP_PORT = 8889          # TCP文件传输端口
BROADCAST_ADDRESS = '255.255.255.255'  # 广播地址
BUFFER_SIZE = 4096               # 接收缓冲区大小
FILE_CHUNK_SIZE = 8192           # 文件传输块大小

# 消息关键字
DISCOVERY_KEYWORD = "CHAT_DISCOVER"  # 发现组员关键字
JOIN_KEYWORD = "CHAT_JOIN"           # 加入组关键字
LEAVE_KEYWORD = "CHAT_LEAVE"         # 离开组关键字
REFRESH_KEYWORD = "CHAT_REFRESH"     # 刷新请求关键字

# 超时设置
SOCKET_TIMEOUT = 5               # socket超时时间（秒）
DISCOVERY_TIMEOUT = 3            # 发现组员超时时间（秒）

# 界面配置
WINDOW_TITLE = "简易即时通信工具"
WINDOW_WIDTH = 1000
WINDOW_HEIGHT = 700
```

### message_types.py - 数据类型

#### MessageType（枚举）

消息类型枚举：

```python
class MessageType(Enum):
    DISCOVERY = "DISCOVERY"                    # 发现请求
    DISCOVERY_RESPONSE = "DISCOVERY_RESPONSE"  # 发现响应
    JOIN = "JOIN"                              # 加入通知
    LEAVE = "LEAVE"                            # 离开通知
    REFRESH = "REFRESH"                        # 刷新请求
    P2P_MESSAGE = "P2P_MESSAGE"                # 一对一消息
    BROADCAST_MESSAGE = "BROADCAST_MESSAGE"    # 广播消息
    FILE_REQUEST = "FILE_REQUEST"              # 文件传输请求
    FILE_ACCEPT = "FILE_ACCEPT"                # 接受文件传输
    FILE_REJECT = "FILE_REJECT"                # 拒绝文件传输
```

#### Member（数据类）

成员信息：

```python
@dataclass
class Member:
    username: str   # 用户名
    ip: str        # IP地址
    udp_port: int  # UDP端口
    tcp_port: int  # TCP端口
    
    def to_dict() -> dict           # 转换为字典
    def from_dict(data) -> Member   # 从字典创建
```

#### ChatMessage（数据类）

聊天消息：

```python
@dataclass
class ChatMessage:
    msg_type: MessageType       # 消息类型
    sender: Member             # 发送者
    content: str               # 消息内容
    receiver: Optional[Member] # 接收者（一对一消息使用）
    
    def to_dict() -> dict                # 转换为字典
    def from_dict(data) -> ChatMessage   # 从字典创建
```

#### FileTransferInfo（数据类）

文件传输信息：

```python
@dataclass
class FileTransferInfo:
    filename: str   # 文件名
    filesize: int   # 文件大小
    sender: Member  # 发送者
    receiver: Member # 接收者
    
    def to_dict() -> dict                      # 转换为字典
    def from_dict(data) -> FileTransferInfo    # 从字典创建
```

### utils.py - 工具函数

```python
def get_local_ip() -> str
    """获取本机IP地址"""

def serialize_message(message_dict: dict) -> bytes
    """序列化消息为字节流"""

def deserialize_message(data: bytes) -> Optional[dict]
    """反序列化字节流为消息字典"""

def format_file_size(size: int) -> str
    """格式化文件大小显示"""

def validate_ip(ip: str) -> bool
    """验证IP地址格式"""

def validate_port(port: int) -> bool
    """验证端口号"""
```

---

## 核心模块（core）

### NetworkDiscovery - 网络发现

**信号**：
- `member_discovered(Member)`: 发现新成员时触发

**方法**：

```python
def __init__(local_member: Member)
    """初始化网络发现模块"""

def start()
    """启动网络发现服务"""

def stop()
    """停止网络发现服务"""

def send_discovery_broadcast()
    """发送发现广播消息"""
```

### MessageP2P - 一对一消息

**信号**：
- `message_received(ChatMessage)`: 接收到消息时触发

**方法**：

```python
def __init__(local_member: Member)
    """初始化一对一消息模块"""

def set_socket(sock: socket.socket)
    """设置UDP socket"""

def send_p2p_message(receiver: Member, content: str) -> bool
    """发送一对一消息"""

def handle_received_message(data: bytes, addr)
    """处理接收到的消息"""
```

### MessageBroadcast - 广播消息

**信号**：
- `broadcast_received(ChatMessage)`: 接收到广播消息时触发

**方法**：

```python
def __init__(local_member: Member)
    """初始化广播消息模块"""

def set_socket(sock: socket.socket)
    """设置UDP socket"""

def update_member_list(members: List[Member])
    """更新成员列表"""

def send_broadcast_message(content: str) -> bool
    """发送广播消息"""

def handle_broadcast_message(data: bytes, addr)
    """处理接收到的广播消息"""
```

### FileTransfer - 文件传输

**信号**：
- `file_request_received(FileTransferInfo)`: 收到文件传输请求
- `transfer_progress(str, int)`: 传输进度更新（文件名，百分比）
- `transfer_completed(str, bool)`: 传输完成（文件名，是否成功）

**方法**：

```python
def __init__(local_member: Member)
    """初始化文件传输模块"""

def start()
    """启动文件传输服务"""

def stop()
    """停止文件传输服务"""

def send_file(file_path: str, receiver: Member)
    """发送文件"""

def accept_file(file_info: FileTransferInfo)
    """接受文件传输"""

def reject_file(file_info: FileTransferInfo)
    """拒绝文件传输"""
```

### MemberManager - 组员管理

**信号**：
- `member_added(Member)`: 成员加入时触发
- `member_removed(Member)`: 成员离开时触发
- `member_list_updated(list)`: 成员列表更新时触发

**方法**：

```python
def __init__(local_member: Member)
    """初始化组员管理模块"""

def set_socket(sock: socket.socket)
    """设置UDP socket"""

def add_member(member: Member)
    """添加成员"""

def remove_member(member: Member)
    """移除成员"""

def get_member_list() -> List[Member]
    """获取成员列表"""

def get_member_by_ip(ip: str, port: int) -> Optional[Member]
    """根据IP和端口查找成员"""

def broadcast_join()
    """广播加入消息"""

def broadcast_leave()
    """广播离开消息"""

def handle_join_message(message: dict)
    """处理加入消息"""

def handle_leave_message(message: dict)
    """处理离开消息"""

def clear_members()
    """清空成员列表"""
```

### MemberRefresh - 成员刷新

**信号**：
- `refresh_started()`: 刷新开始时触发
- `refresh_completed(int)`: 刷新完成时触发（发现的成员数）

**方法**：

```python
def __init__(local_member: Member)
    """初始化成员刷新模块"""

def set_socket(sock: socket.socket)
    """设置UDP socket"""

def refresh_members()
    """手动刷新成员列表"""

def handle_refresh_request(sender_addr)
    """处理刷新请求"""

def handle_refresh_response(message: dict)
    """处理刷新响应"""
```

---

## UI模块（ui）

### MainWindow - 主窗口

**属性**：
```python
self.local_member: Member                    # 本地用户信息
self.network_discovery: NetworkDiscovery     # 网络发现模块
self.message_p2p: MessageP2P                 # 一对一消息模块
self.message_broadcast: MessageBroadcast     # 广播消息模块
self.file_transfer: FileTransfer             # 文件传输模块
self.member_manager: MemberManager           # 组员管理模块
self.member_refresh: MemberRefresh           # 成员刷新模块
```

**方法**：

```python
def __init__()
    """初始化主窗口"""

def init_ui()
    """初始化用户界面"""

def init_modules()
    """初始化核心功能模块"""

def connect_signals()
    """连接信号和槽"""

# 事件处理
def on_refresh_members()        # 刷新成员列表
def on_send_message()           # 发送消息
def on_broadcast_message()      # 广播消息
def on_send_file()              # 发送文件
def on_member_double_clicked()  # 成员双击

# 信号槽函数
def on_member_discovered(member: Member)           # 发现新成员
def on_message_received(message: ChatMessage)      # 接收消息
def on_broadcast_received(message: ChatMessage)    # 接收广播
def on_file_request(file_info: FileTransferInfo)   # 文件请求
def on_transfer_progress(filename: str, percentage: int)  # 传输进度
def on_member_list_updated(members: list)          # 成员列表更新

# 辅助函数
def append_chat_message(sender: str, content: str, is_broadcast: bool)
    """在聊天窗口添加消息"""

def show_about()
    """显示关于对话框"""

def closeEvent(event)
    """窗口关闭事件"""
```

---

## 消息格式示例

### 发现请求消息

```json
{
    "msg_type": "DISCOVERY",
    "sender": {
        "username": "User1",
        "ip": "192.168.1.100",
        "udp_port": 8888,
        "tcp_port": 8889
    },
    "content": "CHAT_DISCOVER"
}
```

### 一对一消息

```json
{
    "msg_type": "P2P_MESSAGE",
    "sender": {
        "username": "User1",
        "ip": "192.168.1.100",
        "udp_port": 8888,
        "tcp_port": 8889
    },
    "receiver": {
        "username": "User2",
        "ip": "192.168.1.101",
        "udp_port": 8888,
        "tcp_port": 8889
    },
    "content": "Hello, User2!"
}
```

### 广播消息

```json
{
    "msg_type": "BROADCAST_MESSAGE",
    "sender": {
        "username": "User1",
        "ip": "192.168.1.100",
        "udp_port": 8888,
        "tcp_port": 8889
    },
    "content": "Hello, everyone!"
}
```

