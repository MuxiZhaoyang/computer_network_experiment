"""
消息分发器模块
功能：统一管理UDP socket，接收并分发消息到相应模块
这个模块由成员一和成员七共同完成
"""

import socket
import threading
from typing import Optional, Dict, Callable
from PyQt5.QtCore import QObject, pyqtSignal

from ..common.config import *
from ..common.message_types import *
from ..common.utils import *


class MessageDispatcher(QObject):
    """
    消息分发器类
    负责创建UDP socket，接收所有消息并分发到相应的处理模块
    """
    
    # 定义信号 - 根据消息类型分发
    discovery_message = pyqtSignal(dict, tuple)      # 发现消息 (message, addr)
    p2p_message = pyqtSignal(dict, tuple)            # 一对一消息
    broadcast_message = pyqtSignal(dict, tuple)      # 广播消息
    join_message = pyqtSignal(dict, tuple)           # 加入消息
    leave_message = pyqtSignal(dict, tuple)          # 离开消息
    refresh_message = pyqtSignal(dict, tuple)        # 刷新消息
    
    def __init__(self, local_member: Member):
        """
        初始化消息分发器
        
        Args:
            local_member: 本地用户信息
        """
        super().__init__()
        self.local_member = local_member
        self.udp_socket: Optional[socket.socket] = None
        self.is_running = False
        self.listen_thread: Optional[threading.Thread] = None
    
    def start(self):
        """
        启动消息分发服务
        创建UDP socket并开始监听
        """
        try:
            # 创建UDP socket
            self.udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            
            # 设置socket选项 - 允许广播
            self.udp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
            # 允许地址重用
            self.udp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            
            # 绑定到所有网络接口的指定端口
            self.udp_socket.bind(('0.0.0.0', DEFAULT_UDP_PORT))
            
            # 设置为非阻塞模式，避免close时卡住
            self.udp_socket.settimeout(1.0)
            
            # 启动监听线程
            self.is_running = True
            self.listen_thread = threading.Thread(target=self._listen_loop, daemon=True)
            self.listen_thread.start()
            
            print(f"[分发器] 启动成功，监听端口 {DEFAULT_UDP_PORT}")
            print(f"[分发器] 本地IP: {self.local_member.ip}")
            print(f"[分发器] 广播地址: {BROADCAST_ADDRESS}")
            
        except Exception as e:
            print(f"[分发器] 启动失败: {e}")
            import traceback
            traceback.print_exc()
    
    def stop(self):
        """
        停止消息分发服务
        """
        self.is_running = False
        if self.udp_socket:
            self.udp_socket.close()
        if self.listen_thread:
            self.listen_thread.join(timeout=2)
        print("消息分发器已停止")
    
    def get_socket(self) -> Optional[socket.socket]:
        """
        获取UDP socket供其他模块发送消息使用
        
        Returns:
            socket.socket: UDP socket对象
        """
        return self.udp_socket
    
    def send_message(self, message_dict: dict, target_ip: str, target_port: int) -> bool:
        """
        发送UDP消息（供所有模块使用的统一发送接口）
        
        Args:
            message_dict: 消息字典
            target_ip: 目标IP
            target_port: 目标端口
            
        Returns:
            bool: 是否发送成功
        """
        try:
            if not self.udp_socket:
                print("UDP socket未初始化")
                return False
            
            data = serialize_message(message_dict)
            self.udp_socket.sendto(data, (target_ip, target_port))
            return True
        except Exception as e:
            print(f"发送消息失败: {e}")
            return False
    
    def send_broadcast(self, message_dict: dict) -> bool:
        """
        广播UDP消息（方法名改为send_broadcast避免与信号冲突）
        
        Args:
            message_dict: 消息字典
            
        Returns:
            bool: 是否发送成功
        """
        result = self.send_message(message_dict, BROADCAST_ADDRESS, DEFAULT_UDP_PORT)
        if result:
            msg_type = message_dict.get('msg_type', 'UNKNOWN')
            print(f"[分发器] 广播发送成功: {msg_type}")
        return result
    
    def _listen_loop(self):
        """
        监听循环（在独立线程中运行）
        接收所有UDP消息并根据类型分发
        """
        print("[分发器] 监听线程已启动")
        while self.is_running:
            try:
                # 接收数据
                data, addr = self.udp_socket.recvfrom(BUFFER_SIZE)
                
                print(f"[分发器] 收到消息，来自 {addr[0]}:{addr[1]}")
                
                # 反序列化消息
                message = deserialize_message(data)
                if not message:
                    print(f"[分发器] 消息反序列化失败")
                    continue
                
                # 获取消息类型和发送者信息
                msg_type = message.get('msg_type')
                sender_data = message.get('sender', {})
                sender_ip = sender_data.get('ip', 'unknown')
                sender_name = sender_data.get('username', 'unknown')
                
                print(f"[分发器] 消息类型: {msg_type}, 发送者: {sender_name}({sender_ip})")
                
                # 检查是否是自己发送的消息（通过发送者信息判断）
                if sender_ip == self.local_member.ip and sender_data.get('udp_port') == self.local_member.udp_port:
                    print(f"[分发器] 忽略自己的消息")
                    continue
                
                # 根据消息类型分发到相应的信号
                if msg_type == MessageType.DISCOVERY.value:
                    print(f"[分发器] 分发发现请求")
                    self.discovery_message.emit(message, addr)
                elif msg_type == MessageType.DISCOVERY_RESPONSE.value:
                    print(f"[分发器] 分发发现响应")
                    self.discovery_message.emit(message, addr)
                elif msg_type == MessageType.P2P_MESSAGE.value:
                    print(f"[分发器] 分发P2P消息")
                    self.p2p_message.emit(message, addr)
                elif msg_type == MessageType.BROADCAST_MESSAGE.value:
                    print(f"[分发器] 分发广播消息")
                    self.broadcast_message.emit(message, addr)
                elif msg_type == MessageType.JOIN.value:
                    print(f"[分发器] 分发加入消息")
                    self.join_message.emit(message, addr)
                elif msg_type == MessageType.LEAVE.value:
                    print(f"[分发器] 分发离开消息")
                    self.leave_message.emit(message, addr)
                elif msg_type == MessageType.REFRESH.value:
                    print(f"[分发器] 分发刷新消息")
                    self.refresh_message.emit(message, addr)
                else:
                    print(f"[分发器] 未知消息类型: {msg_type}")
                    
            except socket.timeout:
                # 超时是正常的，继续循环
                continue
            except Exception as e:
                if self.is_running:
                    print(f"[分发器] 接收消息出错: {e}")
                    import traceback
                    traceback.print_exc()
        
        print("[分发器] 监听循环已退出")

