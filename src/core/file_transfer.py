"""
文件传输模块 - 成员四负责
功能：实现基于TCP协议的文件传输功能
"""

import os
import socket
import threading
from typing import Optional, Callable, Dict, Tuple
from PyQt5.QtCore import QObject, pyqtSignal, QMetaType

from ..common.config import *
from ..common.message_types import *
from ..common.utils import *


class FileTransfer(QObject):
    """
    文件传输类
    负责通过TCP协议可靠地传输文件
    
    PyQt5注意事项：
    不在信号中传递自定义对象，改用基本类型
    """
    
    # 定义信号 - PyQt5使用基本类型
    file_request_received = pyqtSignal(str, int, str, str)  # filename, filesize, sender_ip, sender_name
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

        # 记录等待用户确认的传输：key 为 (ip, filename)
        self._pending: Dict[Tuple[str, str], dict] = {}
        
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
            filename = os.path.basename(file_path)
            if not os.path.exists(file_path):
                print(f"文件不存在: {file_path}")
                self.transfer_completed.emit(filename, False)
                return

            filesize = os.path.getsize(file_path)
            if filesize > MAX_FILE_SIZE:
                print("文件过大")
                self.transfer_completed.emit(filename, False)
                return

            # 连接对方
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(5)
                s.connect((receiver.ip, receiver.tcp_port))

                info = FileTransferInfo(
                    filename=filename,
                    filesize=filesize,
                    sender=self.local_member,
                    receiver=receiver
                )
                header = serialize_message(info.to_dict())
                header_len = len(header).to_bytes(4, 'big')
                s.sendall(header_len + header)

                # 等待对方接受/拒绝
                resp = s.recv(1)
                if not resp or resp != b'1':
                    print("对方拒绝接收文件")
                    self.transfer_completed.emit(filename, False)
                    return

                sent = 0
                with open(file_path, 'rb') as f:
                    while True:
                        chunk = f.read(FILE_CHUNK_SIZE)
                        if not chunk:
                            break
                        s.sendall(chunk)
                        sent += len(chunk)
                        percent = int(sent * 100 / filesize) if filesize else 100
                        print(f"[文件传输] 发送进度: {filename} {percent}%")
                        self.transfer_progress.emit(filename, percent)

                print(f"[文件传输] 发送完成: {filename}")
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
            key = None
            client_socket.settimeout(5)
            # 读取头长度
            head_len_bytes = self._recv_exact(client_socket, 4)
            if not head_len_bytes:
                return
            head_len = int.from_bytes(head_len_bytes, 'big')
            header_bytes = self._recv_exact(client_socket, head_len)
            if not header_bytes:
                return
            header_dict = deserialize_message(header_bytes)
            if not header_dict:
                return
            file_info = FileTransferInfo.from_dict(header_dict)

            key = (addr[0], file_info.filename)
            decision_event = threading.Event()
            self._pending[key] = {
                'event': decision_event,
                'accepted': None,
                'socket': client_socket,
                'info': file_info,
                'save_path': None,
            }

            # 询问用户 - PyQt5: 发送基本类型而不是对象
            self.file_request_received.emit(
                file_info.filename,
                file_info.filesize,
                file_info.sender.ip,
                file_info.sender.username
            )

            # 等待用户选择，超时拒绝
            decision_event.wait(timeout=30)
            accepted = self._pending.get(key, {}).get('accepted')
            if not accepted:
                client_socket.sendall(b'0')
                return

            client_socket.sendall(b'1')

            chosen = self._pending.get(key, {}).get('save_path')
            save_path = chosen if chosen else self._prepare_save_path(file_info.filename)
            if save_path:
                folder = os.path.dirname(save_path)
                if folder and not os.path.exists(folder):
                    os.makedirs(folder, exist_ok=True)
            received = 0
            with open(save_path, 'wb') as f:
                while received < file_info.filesize:
                    chunk = client_socket.recv(FILE_CHUNK_SIZE)
                    if not chunk:
                        break
                    f.write(chunk)
                    received += len(chunk)
                    percent = int(received * 100 / file_info.filesize) if file_info.filesize else 100
                    print(f"[文件传输] 接收进度: {file_info.filename} {percent}%")
                    self.transfer_progress.emit(file_info.filename, percent)

            success = received == file_info.filesize
            print(f"[文件传输] 接收完成: {file_info.filename}, 成功={success}")
            self.transfer_completed.emit(file_info.filename, success)
        except Exception as e:
            print(f"接收文件失败: {e}")
            import traceback
            traceback.print_exc()
            # 即使失败也要发送完成信号
            try:
                if 'file_info' in locals():
                    self.transfer_completed.emit(file_info.filename, False)
            except:
                pass
        finally:
            try:
                if key and key in self._pending:
                    self._pending.pop(key, None)
                client_socket.close()
            except:
                pass
    
    def accept_file(self, file_info: FileTransferInfo, save_path: Optional[str] = None):
        """
        接受文件传输
        
        Args:
            file_info: 文件传输信息
            save_path: 保存路径（含文件名），可选
        """
        key = (file_info.sender.ip, file_info.filename)
        pending = self._pending.get(key)
        if pending:
            pending['accepted'] = True
            if save_path:
                pending['save_path'] = save_path
            pending['event'].set()
    
    def reject_file(self, file_info: FileTransferInfo):
        """
        拒绝文件传输
        
        Args:
            file_info: 文件传输信息
        """
        key = (file_info.sender.ip, file_info.filename)
        pending = self._pending.get(key)
        if pending:
            pending['accepted'] = False
            pending['event'].set()

    def _recv_exact(self, sock: socket.socket, size: int) -> Optional[bytes]:
        data = b''
        try:
            while len(data) < size:
                chunk = sock.recv(size - len(data))
                if not chunk:
                    return None
                data += chunk
            return data
        except Exception:
            return None

    def _prepare_save_path(self, filename: str) -> str:
        base = os.path.join(DOWNLOAD_DIR, filename)
        if not os.path.exists(base):
            return base
        name, ext = os.path.splitext(filename)
        idx = 1
        while True:
            candidate = os.path.join(DOWNLOAD_DIR, f"{name}_{idx}{ext}")
            if not os.path.exists(candidate):
                return candidate
            idx += 1

