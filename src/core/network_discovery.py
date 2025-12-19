"""
网络发现模块 - 成员一负责
功能：通过UDP广播实现客户端间的组员发现与加入
"""

from typing import Optional
from PyQt5.QtCore import QObject, pyqtSignal

from ..common.config import *
from ..common.message_types import *
from ..common.utils import *


class NetworkDiscovery(QObject):
    """
    网络发现类
    负责通过UDP广播发现局域网内的聊天组成员
    
    注意：此模块不再管理socket，由MessageDispatcher统一管理
    """
    
    # 定义信号
    member_discovered = pyqtSignal(Member)  # 发现新成员信号
    
    def __init__(self, local_member: Member, message_dispatcher):
        """
        初始化网络发现模块
        
        Args:
            local_member: 本地用户信息
            message_dispatcher: 消息分发器实例
        """
        super().__init__()
        self.local_member = local_member
        self.dispatcher = message_dispatcher
    
    
    def send_discovery_broadcast(self):
        """
        发送发现广播消息
        向局域网广播发现请求
        """
        try:
            message = ChatMessage(
                msg_type=MessageType.DISCOVERY,
                sender=self.local_member,
                content=DISCOVERY_KEYWORD
            )
            self.dispatcher.send_broadcast(message.to_dict())
            print(f"[发现] 发送发现广播")
        except Exception as e:
            print(f"发送发现广播失败: {e}")
    
    def handle_message(self, message: dict, addr: tuple):
        """
        处理接收到的发现相关消息（由MessageDispatcher分发过来）
        
        Args:
            message: 消息字典
            addr: 发送者地址 (ip, port)
        """
        try:
            # TODO: 成员一实现
            # 1. 判断消息类型
            # 2. 如果是DISCOVERY请求，调用_handle_discovery_request
            # 3. 如果是DISCOVERY_RESPONSE，调用_handle_discovery_response
            
            msg_type = message.get('msg_type')
            
            if msg_type == MessageType.DISCOVERY.value:
                self._handle_discovery_request(message, addr)
            elif msg_type == MessageType.DISCOVERY_RESPONSE.value:
                self._handle_discovery_response(message, addr)
                
        except Exception as e:
            print(f"处理发现消息出错: {e}")
    
    def _handle_discovery_request(self, message: dict, addr: tuple):
        """
        处理发现请求
        
        Args:
            message: 消息字典
            addr: 发送者地址
        """
        try:
            print(f"[发现] 收到发现请求，来自 {addr[0]}")
            response = ChatMessage(
                msg_type=MessageType.DISCOVERY_RESPONSE,
                sender=self.local_member,
                content="RESPONSE"
            )
            self.dispatcher.send_message(response.to_dict(), addr[0], addr[1])
            print(f"[发现] 已响应发现请求")
        except Exception as e:
            print(f"处理发现请求失败: {e}")
    
    def _handle_discovery_response(self, message: dict, addr: tuple):
        """
        处理发现响应
        
        Args:
            message: 消息字典
            addr: 发送者地址
        """
        try:
            sender_data = message.get('sender')
            if sender_data:
                member = Member.from_dict(sender_data)
                print(f"[发现] 发现成员: {member.username} ({member.ip})")
                self.member_discovered.emit(member)
        except Exception as e:
            print(f"处理发现响应失败: {e}")

