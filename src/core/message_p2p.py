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
            # TODO: 成员二实现
            # 1. 构造ChatMessage对象，类型为P2P_MESSAGE
            # 2. 设置sender为self.local_member，receiver为参数receiver
            # 3. 转换为字典：message.to_dict()
            # 4. 使用 self.dispatcher.send_message() 发送到目标
            # 5. 返回发送结果
            
            # 示例代码：
            # message = ChatMessage(
            #     msg_type=MessageType.P2P_MESSAGE,
            #     sender=self.local_member,
            #     receiver=receiver,
            #     content=content
            # )
            # return self.dispatcher.send_message(
            #     message.to_dict(),
            #     receiver.ip,
            #     receiver.udp_port
            # )
            pass
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
            # TODO: 成员二实现
            # 1. 从字典创建ChatMessage对象
            # 2. 检查receiver是否是本地用户（可选）
            # 3. 触发message_received信号
            
            # 示例代码：
            # chat_message = ChatMessage.from_dict(message)
            # self.message_received.emit(chat_message)
            pass
        except Exception as e:
            print(f"处理P2P消息失败: {e}")

