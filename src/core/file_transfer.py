"""
文件传输模块 - 成员四负责
功能：实现基于TCP协议的文件传输功能
"""

import os
import socket
import threading
import struct
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
        self.pending_transfers = {}
        self.pending_lock = threading.Lock()
        
        # 确保下载目录存在
        if not os.path.exists(DOWNLOAD_DIR):
            os.makedirs(DOWNLOAD_DIR)
    
    def start(self):
        """
        启动文件传输服务
        创建TCP socket并开始监听连接
        """
        try:
            if self.is_running:
                return
            self.tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.tcp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.tcp_socket.bind(('', DEFAULT_TCP_PORT))
            self.tcp_socket.listen(5)
            self.tcp_socket.settimeout(1.0)
            self.is_running = True
            self.listen_thread = threading.Thread(target=self._listen_loop, daemon=True)
            self.listen_thread.start()
            print(f"启动文件传输服务，监听端口 {DEFAULT_TCP_PORT}")
        except Exception as e:
            print(f"启动文件传输服务失败: {e}")
    
    def stop(self):
        """
        停止文件传输服务
        """
        self.is_running = False
        try:
            if self.tcp_socket:
                try:
                    self.tcp_socket.shutdown(socket.SHUT_RDWR)
                except Exception:
                    pass
                self.tcp_socket.close()
                self.tcp_socket = None
            if self.listen_thread and self.listen_thread.is_alive():
                self.listen_thread.join(timeout=2)
        finally:
            self.listen_thread = None
    
    def send_file(self, file_path: str, receiver: Member):
        """
        发送文件给指定成员
        
        Args:
            file_path: 要发送的文件路径
            receiver: 接收者信息
        """
        if not os.path.exists(file_path):
            print("文件不存在")
            self.transfer_completed.emit(os.path.basename(file_path), False)
            return
        filesize = os.path.getsize(file_path)
        if filesize > MAX_FILE_SIZE:
            print("文件过大，超过限制")
            self.transfer_completed.emit(os.path.basename(file_path), False)
            return
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
            filename = os.path.basename(file_path)
            filesize = os.path.getsize(file_path)
            file_info = FileTransferInfo(
                filename=filename,
                filesize=filesize,
                sender=self.local_member,
                receiver=receiver
            )
            
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_sock:
                client_sock.settimeout(SOCKET_TIMEOUT)
                client_sock.connect((receiver.ip, receiver.tcp_port))
                
                # 发送文件请求
                request_msg = {
                    'msg_type': MessageType.FILE_REQUEST.value,
                    'file_info': file_info.to_dict()
                }
                self._send_json(client_sock, request_msg)
                
                # 等待响应
                response = self._recv_json(client_sock)
                if not response or response.get('msg_type') == MessageType.FILE_REJECT.value:
                    print("对方拒绝接收文件或无响应")
                    self.transfer_completed.emit(filename, False)
                    return
                
                # 开始发送文件
                sent = 0
                last_percent = -1
                with open(file_path, 'rb') as f:
                    while True:
                        chunk = f.read(FILE_CHUNK_SIZE)
                        if not chunk:
                            break
                        client_sock.sendall(chunk)
                        sent += len(chunk)
                        percent = int(sent * 100 / filesize) if filesize > 0 else 100
                        if percent != last_percent:
                            self.transfer_progress.emit(filename, percent)
                            last_percent = percent
                self.transfer_completed.emit(filename, True)
        except Exception as e:
            print(f"发送文件失败: {e}")
            self.transfer_completed.emit(os.path.basename(file_path), False)
    
    def _listen_loop(self):
        """
        监听TCP连接的循环
        """
        while self.is_running:
            try:
                if not self.tcp_socket:
                    break
                client_socket, addr = self.tcp_socket.accept()
                handler_thread = threading.Thread(
                    target=self._handle_client,
                    args=(client_socket, addr),
                    daemon=True
                )
                handler_thread.start()
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
            request = self._recv_json(client_socket)
            if not request or request.get('msg_type') != MessageType.FILE_REQUEST.value:
                return
            file_info = FileTransferInfo.from_dict(request['file_info'])
            
            # 准备等待用户确认
            key = self._make_transfer_key(file_info)
            session = {
                'socket': client_socket,
                'info': file_info,
                'event': threading.Event(),
                'decision': None
            }
            with self.pending_lock:
                self.pending_transfers[key] = session
            self.file_request_received.emit(file_info)
            
            # 等待用户接受/拒绝，超时默认拒绝
            decided = session['event'].wait(timeout=30)
            decision = session['decision'] if decided else 'reject'
            
            if decision != 'accept':
                # 通知对方拒绝
                reject_msg = {'msg_type': MessageType.FILE_REJECT.value}
                self._send_json(client_socket, reject_msg)
                self.transfer_completed.emit(file_info.filename, False)
                return
            
            # 发送接受消息
            accept_msg = {'msg_type': MessageType.FILE_ACCEPT.value}
            self._send_json(client_socket, accept_msg)
            
            # 接收文件数据
            file_path = os.path.join(DOWNLOAD_DIR, file_info.filename)
            received = 0
            last_percent = -1
            with open(file_path, 'wb') as f:
                while received < file_info.filesize:
                    chunk = client_socket.recv(min(FILE_CHUNK_SIZE, file_info.filesize - received))
                    if not chunk:
                        break
                    f.write(chunk)
                    received += len(chunk)
                    percent = int(received * 100 / file_info.filesize) if file_info.filesize > 0 else 100
                    if percent != last_percent:
                        self.transfer_progress.emit(file_info.filename, percent)
                        last_percent = percent
            success = received == file_info.filesize
            self.transfer_completed.emit(file_info.filename, success)
        except Exception as e:
            print(f"接收文件失败: {e}")
        finally:
            with self.pending_lock:
                self.pending_transfers.pop(key, None) if 'key' in locals() else None
            client_socket.close()
    
    def accept_file(self, file_info: FileTransferInfo):
        """
        接受文件传输
        
        Args:
            file_info: 文件传输信息
        """
        key = self._make_transfer_key(file_info)
        with self.pending_lock:
            session = self.pending_transfers.get(key)
        if session:
            session['decision'] = 'accept'
            session['event'].set()
    
    def reject_file(self, file_info: FileTransferInfo):
        """
        拒绝文件传输
        
        Args:
            file_info: 文件传输信息
        """
        key = self._make_transfer_key(file_info)
        with self.pending_lock:
            session = self.pending_transfers.get(key)
        if session:
            session['decision'] = 'reject'
            session['event'].set()
    
    # ====== 内部工具函数 ======
    def _make_transfer_key(self, file_info: FileTransferInfo):
        return (file_info.sender.ip, file_info.sender.tcp_port, file_info.filename)
    
    def _recv_exact(self, sock: socket.socket, size: int) -> Optional[bytes]:
        data = b''
        while len(data) < size:
            chunk = sock.recv(size - len(data))
            if not chunk:
                return None
            data += chunk
        return data
    
    def _send_json(self, sock: socket.socket, message: dict):
        data = serialize_message(message)
        length = struct.pack('!I', len(data))
        sock.sendall(length + data)
    
    def _recv_json(self, sock: socket.socket) -> Optional[dict]:
        length_bytes = self._recv_exact(sock, 4)
        if not length_bytes:
            return None
        length = struct.unpack('!I', length_bytes)[0]
        body = self._recv_exact(sock, length)
        if not body:
            return None
        return deserialize_message(body)

