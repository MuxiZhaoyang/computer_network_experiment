"""
手动刷新组员列表模块 - 成员六负责
功能：实现手动刷新功能，通过广播重新查找并更新组员列表
"""

import socket
from typing import Optional
from PyQt6.QtCore import QObject, pyqtSignal

from ..common.config import *
from ..common.message_types import *
from ..common.utils import *


class MemberRefresh(QObject):
    """
    成员刷新类
    负责手动刷新组员列表
    """
    
    # 定义信号
    refresh_started = pyqtSignal()  # 刷新开始信号
    refresh_completed = pyqtSignal(int)  # 刷新完成信号 (发现的成员数量)
    
    def __init__(self, local_member: Member, message_dispatcher):
        """
        初始化成员刷新模块
        
        Args:
            local_member: 本地用户信息
            message_dispatcher: 消息分发器实例
        """
        super().__init__()
        self.local_member = local_member
        self.dispatcher = message_dispatcher
        self.is_refreshing = False
    
    def refresh_members(self):
        """
        手动刷新成员列表
        发送刷新广播请求
        """
        if self.is_refreshing:
            print("正在刷新中，请稍候...")
            return
        
        try:
            self.is_refreshing = True
            self.refresh_started.emit()
            message = ChatMessage(
                msg_type=MessageType.REFRESH,
                sender=self.local_member,
                content=REFRESH_KEYWORD
            )
            self.dispatcher.broadcast_udp(message.to_dict())
            # 简化处理：立即允许再次刷新
            self.is_refreshing = False
        except Exception as e:
            print(f"刷新成员列表失败: {e}")
            self.is_refreshing = False
    
    def handle_refresh_message(self, message: dict, addr: tuple):
        """
        处理刷新相关消息（由MessageDispatcher分发过来）
        
        Args:
            message: 消息字典
            addr: 发送者地址
        """
        try:
            msg_type = message.get('msg_type')
            if msg_type != MessageType.REFRESH.value:
                return
            # 收到刷新请求，回一个发现响应，便于对方更新列表
            response = ChatMessage(
                msg_type=MessageType.DISCOVERY_RESPONSE,
                sender=self.local_member,
                content="REFRESH_RESPONSE"
            )
            self.dispatcher.send_message(response.to_dict(), addr[0], addr[1])
        except Exception as e:
            print(f"处理刷新消息失败: {e}")

