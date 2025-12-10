"""
网络发现模块 - 成员一负责
功能：通过UDP广播实现客户端间的组员发现与加入
"""

from typing import Optional
from PyQt6.QtCore import QObject, pyqtSignal

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
            # TODO: 成员一实现
            # 1. 构造ChatMessage对象，类型为DISCOVERY
            # 2. 转换为字典：message.to_dict()
            # 3. 使用 self.dispatcher.broadcast_message(message_dict) 发送
            
            # 示例代码：
            # message = ChatMessage(
            #     msg_type=MessageType.DISCOVERY,
            #     sender=self.local_member,
            #     content=DISCOVERY_KEYWORD
            # )
            # self.dispatcher.broadcast_message(message.to_dict())
            pass
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
            # TODO: 成员一实现
            # 1. 构造DISCOVERY_RESPONSE类型的响应消息
            # 2. 使用 self.dispatcher.send_message() 发送给请求者
            
            # 示例代码：
            # response = ChatMessage(
            #     msg_type=MessageType.DISCOVERY_RESPONSE,
            #     sender=self.local_member,
            #     content="RESPONSE"
            # )
            # self.dispatcher.send_message(response.to_dict(), addr[0], addr[1])
            pass
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
            # TODO: 成员一实现
            # 1. 从message中提取sender信息
            # 2. 创建Member对象
            # 3. 触发member_discovered信号
            
            # 示例代码：
            # sender_data = message.get('sender')
            # member = Member.from_dict(sender_data)
            # self.member_discovered.emit(member)
            pass
        except Exception as e:
            print(f"处理发现响应失败: {e}")

