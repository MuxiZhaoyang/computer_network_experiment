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
            # 简化实现：仅初始化监听socket，确保不影响其他功能
            self.tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.tcp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.tcp_socket.bind(('', self.local_member.tcp_port))
            self.tcp_socket.listen(5)
            self.is_running = True
            self.listen_thread = threading.Thread(target=self._listen_loop, daemon=True)
            self.listen_thread.start()
        except Exception as e:
            print(f"启动文件传输服务失败: {e}")
    
    def stop(self):
        """
        停止文件传输服务
        """
        self.is_running = False
        if self.tcp_socket:
            try:
                self.tcp_socket.close()
            except Exception:
                pass
        if self.listen_thread:
            self.listen_thread.join(timeout=2)
    
    def send_file(self, file_path: str, receiver: Member):
        """
        发送文件给指定成员
        
        Args:
            file_path: 要发送的文件路径
            receiver: 接收者信息
        """
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
            # 未实现完整文件传输，此处仅占位防止崩溃
            filename = os.path.basename(file_path)
            if not os.path.exists(file_path):
                print(f"文件不存在: {file_path}")
                self.transfer_completed.emit(filename, False)
                return
            self.transfer_completed.emit(filename, False)
        except Exception as e:
            print(f"发送文件失败: {e}")
            self.transfer_completed.emit(os.path.basename(file_path), False)
    
    def _listen_loop(self):
        """
        监听TCP连接的循环
        """
        while self.is_running:
            try:
                client_socket, addr = self.tcp_socket.accept()
                handler = threading.Thread(
                    target=self._handle_client,
                    args=(client_socket, addr),
                    daemon=True
                )
                handler.start()
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
            # 简化：当前未实现完整文件接收，直接关闭
            client_socket.close()
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
        # 占位：未实现
        print("暂未实现文件接收确认")
    
    def reject_file(self, file_info: FileTransferInfo):
        """
        拒绝文件传输
        
        Args:
            file_info: 文件传输信息
        """
        print("已拒绝文件传输（未实现实际通信）")

