"""
文件传输模块 - 完整实现版本
基于TCP协议的可靠文件传输
"""

import os
import socket
import threading
import struct
import json
from typing import Optional
from PyQt5.QtCore import QObject, pyqtSignal

from ..common.config import *
from ..common.message_types import *
from ..common.utils import *


class FileTransfer(QObject):
    """文件传输类 - 完整版本"""
    
    # 定义信号
    file_request_received = pyqtSignal(FileTransferInfo)  # 收到文件传输请求
    transfer_progress = pyqtSignal(str, int)  # 传输进度 (filename, percentage)
    transfer_completed = pyqtSignal(str, bool)  # 传输完成 (filename, success)
    
    def __init__(self, local_member: Member):
        super().__init__()
        self.local_member = local_member
        self.tcp_socket: Optional[socket.socket] = None
        self.is_running = False
        self.listen_thread: Optional[threading.Thread] = None
        self.pending_transfers = {}  # 待处理的传输请求
        
        # 确保下载目录存在
        if not os.path.exists(DOWNLOAD_DIR):
            os.makedirs(DOWNLOAD_DIR)
            print(f"[文件] 创建下载目录: {DOWNLOAD_DIR}")
    
    def start(self):
        """启动TCP文件传输服务"""
        try:
            # 创建TCP socket
            self.tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.tcp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            
            # 绑定端口
            self.tcp_socket.bind(('', self.local_member.tcp_port))
            
            # 开始监听
            self.tcp_socket.listen(5)
            self.tcp_socket.settimeout(1.0)
            
            # 启动监听线程
            self.is_running = True
            self.listen_thread = threading.Thread(target=self._listen_loop, daemon=True)
            self.listen_thread.start()
            
            print(f"[文件] TCP服务启动成功，监听端口 {self.local_member.tcp_port}")
            
        except Exception as e:
            print(f"启动文件传输服务失败: {e}")
    
    def stop(self):
        """停止文件传输服务"""
        self.is_running = False
        if self.tcp_socket:
            self.tcp_socket.close()
        if self.listen_thread:
            self.listen_thread.join(timeout=2)
        print("[文件] TCP服务已停止")
    
    def send_file(self, file_path: str, receiver: Member):
        """
        发送文件
        
        Args:
            file_path: 文件路径
            receiver: 接收者
        """
        # 在新线程中执行，避免阻塞UI
        thread = threading.Thread(
            target=self._send_file_thread,
            args=(file_path, receiver),
            daemon=True
        )
        thread.start()
    
    def _send_file_thread(self, file_path: str, receiver: Member):
        """发送文件的线程函数"""
        filename = os.path.basename(file_path)
        
        try:
            # 检查文件
            if not os.path.exists(file_path):
                print(f"[文件] 文件不存在: {file_path}")
                self.transfer_completed.emit(filename, False)
                return
            
            filesize = os.path.getsize(file_path)
            if filesize > MAX_FILE_SIZE:
                print(f"[文件] 文件过大: {format_file_size(filesize)}")
                self.transfer_completed.emit(filename, False)
                return
            
            print(f"[文件] 开始发送: {filename} ({format_file_size(filesize)}) 到 {receiver.username}")
            
            # 连接到接收方
            client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client_socket.settimeout(10)
            client_socket.connect((receiver.ip, receiver.tcp_port))
            
            # 发送文件信息
            file_info = {
                'filename': filename,
                'filesize': filesize,
                'sender': self.local_member.to_dict()
            }
            info_data = json.dumps(file_info).encode('utf-8')
            info_length = len(info_data)
            
            # 发送信息长度（4字节）+ 信息内容
            client_socket.send(struct.pack('!I', info_length))
            client_socket.send(info_data)
            
            # 等待接收方响应
            response = client_socket.recv(1024).decode('utf-8')
            if response != 'ACCEPT':
                print(f"[文件] 接收方拒绝: {response}")
                client_socket.close()
                self.transfer_completed.emit(filename, False)
                return
            
            print(f"[文件] 接收方已接受，开始传输...")
            
            # 发送文件内容
            sent_bytes = 0
            with open(file_path, 'rb') as f:
                while sent_bytes < filesize:
                    # 读取数据块
                    chunk = f.read(FILE_CHUNK_SIZE)
                    if not chunk:
                        break
                    
                    # 发送数据
                    client_socket.send(chunk)
                    sent_bytes += len(chunk)
                    
                    # 更新进度
                    percentage = int((sent_bytes / filesize) * 100)
                    self.transfer_progress.emit(filename, percentage)
            
            client_socket.close()
            print(f"[文件] 发送完成: {filename}")
            self.transfer_completed.emit(filename, True)
            
        except Exception as e:
            print(f"[文件] 发送失败: {e}")
            self.transfer_completed.emit(filename, False)
    
    def _listen_loop(self):
        """监听TCP连接的循环"""
        while self.is_running:
            try:
                # 接受新连接
                client_socket, addr = self.tcp_socket.accept()
                
                # 为每个连接创建新线程处理
                thread = threading.Thread(
                    target=self._handle_client,
                    args=(client_socket, addr),
                    daemon=True
                )
                thread.start()
                
            except socket.timeout:
                continue
            except Exception as e:
                if self.is_running:
                    print(f"[文件] 接受连接出错: {e}")
    
    def _handle_client(self, client_socket: socket.socket, addr):
        """处理客户端连接（接收文件）"""
        try:
            print(f"[文件] 接受连接，来自 {addr[0]}")
            
            # 接收文件信息长度
            length_data = client_socket.recv(4)
            if len(length_data) < 4:
                client_socket.close()
                return
            
            info_length = struct.unpack('!I', length_data)[0]
            
            # 接收文件信息
            info_data = b''
            while len(info_data) < info_length:
                chunk = client_socket.recv(min(info_length - len(info_data), 4096))
                if not chunk:
                    break
                info_data += chunk
            
            file_info = json.loads(info_data.decode('utf-8'))
            filename = file_info['filename']
            filesize = file_info['filesize']
            sender_data = file_info['sender']
            sender = Member.from_dict(sender_data)
            
            print(f"[文件] 收到文件请求: {filename} ({format_file_size(filesize)}) 来自 {sender.username}")
            
            # 创建FileTransferInfo并触发信号（让UI询问用户）
            transfer_info = FileTransferInfo(
                filename=filename,
                filesize=filesize,
                sender=sender,
                receiver=self.local_member
            )
            
            # 保存到待处理列表
            transfer_key = f"{addr[0]}_{filename}"
            self.pending_transfers[transfer_key] = {
                'socket': client_socket,
                'info': transfer_info,
                'accepted': False
            }
            
            # 触发信号（UI会调用accept_file或reject_file）
            self.file_request_received.emit(transfer_info)
            
            # 等待用户响应（最多30秒）
            import time
            timeout = 30
            waited = 0
            while waited < timeout:
                if transfer_key in self.pending_transfers:
                    if self.pending_transfers[transfer_key].get('accepted') is not None:
                        break
                else:
                    return  # 已被处理
                time.sleep(0.5)
                waited += 0.5
            
            # 检查是否接受
            if transfer_key not in self.pending_transfers:
                return
            
            transfer_data = self.pending_transfers[transfer_key]
            if not transfer_data.get('accepted', False):
                client_socket.send(b'REJECT')
                client_socket.close()
                del self.pending_transfers[transfer_key]
                print(f"[文件] 已拒绝: {filename}")
                return
            
            # 发送接受响应
            client_socket.send(b'ACCEPT')
            print(f"[文件] 已接受，开始接收...")
            
            # 接收文件内容
            save_path = os.path.join(DOWNLOAD_DIR, filename)
            received_bytes = 0
            
            with open(save_path, 'wb') as f:
                while received_bytes < filesize:
                    # 接收数据块
                    remaining = filesize - received_bytes
                    chunk_size = min(FILE_CHUNK_SIZE, remaining)
                    chunk = client_socket.recv(chunk_size)
                    
                    if not chunk:
                        break
                    
                    f.write(chunk)
                    received_bytes += len(chunk)
                    
                    # 更新进度
                    percentage = int((received_bytes / filesize) * 100)
                    self.transfer_progress.emit(filename, percentage)
            
            client_socket.close()
            del self.pending_transfers[transfer_key]
            
            if received_bytes == filesize:
                print(f"[文件] 接收完成: {filename} 保存到 {save_path}")
                self.transfer_completed.emit(filename, True)
            else:
                print(f"[文件] 接收不完整: {received_bytes}/{filesize}")
                self.transfer_completed.emit(filename, False)
                
        except Exception as e:
            print(f"[文件] 接收文件失败: {e}")
            try:
                client_socket.close()
            except:
                pass
    
    def accept_file(self, file_info: FileTransferInfo):
        """接受文件传输"""
        transfer_key = f"{file_info.sender.ip}_{file_info.filename}"
        if transfer_key in self.pending_transfers:
            self.pending_transfers[transfer_key]['accepted'] = True
            print(f"[文件] 用户接受: {file_info.filename}")
    
    def reject_file(self, file_info: FileTransferInfo):
        """拒绝文件传输"""
        transfer_key = f"{file_info.sender.ip}_{file_info.filename}"
        if transfer_key in self.pending_transfers:
            self.pending_transfers[transfer_key]['accepted'] = False
            print(f"[文件] 用户拒绝: {file_info.filename}")



