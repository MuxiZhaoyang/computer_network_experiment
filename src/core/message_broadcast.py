"""
广播消息模块 - 成员三负责
功能：实现客户端间的广播消息功能
"""

from typing import List
from PyQt5.QtCore import QObject, pyqtSignal

from ..common.config import *
from ..common.message_types import *
from ..common.utils import *


class MessageBroadcast(QObject):
    """
    广播消息类
    负责向所有在线成员广播消息
    """
    
    # 定义信号
    broadcast_received = pyqtSignal(ChatMessage)  # 接收到广播消息信号
    
    def __init__(self, local_member: Member, message_dispatcher):
        """
        初始化广播消息模块
        
        Args:
            local_member: 本地用户信息
            message_dispatcher: 消息分发器实例
        """
        super().__init__()
        self.local_member = local_member
        self.dispatcher = message_dispatcher
        self.member_list: List[Member] = []
    
    def update_member_list(self, members: List[Member]):
        """
        更新成员列表
        
        Args:
            members: 成员列表
        """
        self.member_list = members
    
    def send_broadcast_message(self, content: str) -> bool:
        """
        发送广播消息到所有在线成员
        
        Args:
            content: 消息内容
            
        Returns:
            bool: 发送是否成功
        """
        try:
            message = ChatMessage(
                msg_type=MessageType.BROADCAST_MESSAGE,
                sender=self.local_member,
                content=content
            )
            message_dict = message.to_dict()
            success = True
            for member in self.member_list:
                if not self.dispatcher.send_message(
                    message_dict,
                    member.ip,
                    member.udp_port
                ):
                    success = False
            return success
        except Exception as e:
            print(f"发送广播消息失败: {e}")
            return False
    
    def handle_message(self, message: dict, addr: tuple):
        """
        处理接收到的广播消息（由MessageDispatcher分发过来）
        
        Args:
            message: 消息字典
            addr: 发送者地址
        """
        try:
            chat_message = ChatMessage.from_dict(message)
            self.broadcast_received.emit(chat_message)
        except Exception as e:
            print(f"处理广播消息失败: {e}")

