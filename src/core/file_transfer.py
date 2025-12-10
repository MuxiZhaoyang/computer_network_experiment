"""
文件传输模块 - 成员四负责
功能：实现基于TCP协议的文件传输功能
"""

import os
import socket
import threading
from typing import Optional, Callable
from PyQt6.QtCore import QObject, pyqtSignal

from ..common.config import *
from ..common.message_types import *
from ..common.utils import *


class FileTransfer(QObject):
    """
    文件传输类
    负责通过TCP协议可靠地传输文件
    """
    
    # 定义信号
    file_request_received = pyqtSignal(FileTransferInfo)  # 收到文件传输请求
    transfer_progress = pyqtSignal(str, int)  # 传输进度 (filename, percentage)
    transfer_completed = pyqtSignal(str, bool)  # 传输完成 (filename, success)
    
    def __init__(self, local_member: Member):
        """
        初始化文件传输模块
        
        Args:
            local_member: 本地用户信息
        """
        super().__init__()
        self.local_member = local_member
        self.tcp_socket: Optional[socket.socket] = None
        self.is_running = False
        self.listen_thread: Optional[threading.Thread] = None
        
        # 确保下载目录存在
        if not os.path.exists(DOWNLOAD_DIR):
            os.makedirs(DOWNLOAD_DIR)
    
    def start(self):
        """
        启动文件传输服务
        创建TCP socket并开始监听连接
        """
        try:
            # TODO: 成员四实现
            # 1. 创建TCP socket
            # 2. 绑定到指定端口
            # 3. 开始监听
            # 4. 启动接受连接的线程
            pass
        except Exception as e:
            print(f"启动文件传输服务失败: {e}")
    
    def stop(self):
        """
        停止文件传输服务
        """
        # TODO: 成员四实现
        # 1. 设置停止标志
        # 2. 关闭socket
        # 3. 等待线程结束
        pass
    
    def send_file(self, file_path: str, receiver: Member):
        """
        发送文件给指定成员
        
        Args:
            file_path: 要发送的文件路径
            receiver: 接收者信息
        """
        # TODO: 成员四实现
        # 在新线程中执行，避免阻塞UI
        thread = threading.Thread(
            target=self._send_file_thread,
            args=(file_path, receiver)
        )
        thread.daemon = True
        thread.start()
    
    def _send_file_thread(self, file_path: str, receiver: Member):
        """
        发送文件的线程函数
        
        Args:
            file_path: 文件路径
            receiver: 接收者
        """
        try:
            # TODO: 成员四实现
            # 1. 获取文件信息（文件名、大小）
            # 2. 连接到接收方的TCP端口
            # 3. 发送文件信息
            # 4. 等待接收方响应（接受/拒绝）
            # 5. 如果接受，分块读取并发送文件
            # 6. 更新进度（触发transfer_progress信号）
            # 7. 发送完成后触发transfer_completed信号
            pass
        except Exception as e:
            print(f"发送文件失败: {e}")
            self.transfer_completed.emit(os.path.basename(file_path), False)
    
    def _listen_loop(self):
        """
        监听TCP连接的循环
        """
        while self.is_running:
            try:
                # TODO: 成员四实现
                # 1. 接受新的连接
                # 2. 为每个连接创建新线程处理
                pass
            except Exception as e:
                if self.is_running:
                    print(f"接受连接出错: {e}")
    
    def _handle_client(self, client_socket: socket.socket, addr):
        """
        处理客户端连接（接收文件）
        
        Args:
            client_socket: 客户端socket
            addr: 客户端地址
        """
        try:
            # TODO: 成员四实现
            # 1. 接收文件信息
            # 2. 创建FileTransferInfo对象
            # 3. 触发file_request_received信号（让用户确认）
            # 4. 根据用户响应发送接受/拒绝
            # 5. 如果接受，接收文件数据并保存
            # 6. 更新进度
            # 7. 完成后触发transfer_completed信号
            pass
        except Exception as e:
            print(f"接收文件失败: {e}")
        finally:
            client_socket.close()
    
    def accept_file(self, file_info: FileTransferInfo):
        """
        接受文件传输
        
        Args:
            file_info: 文件传输信息
        """
        # TODO: 成员四实现
        # 发送接受响应
        pass
    
    def reject_file(self, file_info: FileTransferInfo):
        """
        拒绝文件传输
        
        Args:
            file_info: 文件传输信息
        """
        # TODO: 成员四实现
        # 发送拒绝响应
        pass

