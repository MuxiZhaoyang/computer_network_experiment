"""
一对一消息模块 - 成员二负责
功能：实现客户端之间一对一即时消息的发送和接收
"""

from PyQt6.QtCore import QObject, pyqtSignal

from ..common.config import *
from ..common.message_types import *
from ..common.utils import *


class MessageP2P(QObject):
    """
    一对一消息类
    负责点对点消息的发送和接收
    
    注意：消息接收由MessageDispatcher分发，此模块只负责处理
    """
    
    # 定义信号
    message_received = pyqtSignal(ChatMessage)  # 接收到消息信号
    
    def __init__(self, local_member: Member, message_dispatcher):
        """
        初始化一对一消息模块
        
        Args:
            local_member: 本地用户信息
            message_dispatcher: 消息分发器实例
        """
        super().__init__()
        self.local_member = local_member
        self.dispatcher = message_dispatcher
    
    def send_p2p_message(self, receiver: Member, content: str) -> bool:
        """
        发送一对一消息
        
        Args:
            receiver: 接收者信息
            content: 消息内容
            
        Returns:
            bool: 发送是否成功
        """
        try:
            message = ChatMessage(
                msg_type=MessageType.P2P_MESSAGE,
                sender=self.local_member,
                receiver=receiver,
                content=content
            )
            return self.dispatcher.send_message(
                message.to_dict(),
                receiver.ip,
                receiver.udp_port
            )
        except Exception as e:
            print(f"发送一对一消息失败: {e}")
            return False
    
    def handle_message(self, message: dict, addr: tuple):
        """
        处理接收到的P2P消息（由MessageDispatcher分发过来）
        
        Args:
            message: 消息字典
            addr: 发送者地址
        """
        try:
            chat_message = ChatMessage.from_dict(message)
            self.message_received.emit(chat_message)
        except Exception as e:
            print(f"处理P2P消息失败: {e}")

