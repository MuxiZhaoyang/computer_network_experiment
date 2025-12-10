"""
组员管理模块 - 成员五负责
功能：管理聊天组成员列表，处理成员的加入、离开和更新
"""

from typing import List, Optional
from PyQt6.QtCore import QObject, pyqtSignal

from ..common.config import *
from ..common.message_types import *
from ..common.utils import *


class MemberManager(QObject):
    """
    组员管理类
    负责维护和管理聊天组的成员列表
    """
    
    # 定义信号
    member_added = pyqtSignal(Member)  # 成员加入信号
    member_removed = pyqtSignal(Member)  # 成员离开信号
    member_list_updated = pyqtSignal(list)  # 成员列表更新信号
    
    def __init__(self, local_member: Member, message_dispatcher):
        """
        初始化组员管理模块
        
        Args:
            local_member: 本地用户信息
            message_dispatcher: 消息分发器实例
        """
        super().__init__()
        self.local_member = local_member
        self.dispatcher = message_dispatcher
        self.members: List[Member] = []
    
    def add_member(self, member: Member):
        """
        添加成员到列表
        
        Args:
            member: 要添加的成员
        """
        # TODO: 成员五实现
        # 1. 检查成员是否已存在
        # 2. 检查是否是本地用户
        # 3. 添加到members列表
        # 4. 触发member_added信号
        # 5. 触发member_list_updated信号
        pass
    
    def remove_member(self, member: Member):
        """
        从列表中移除成员
        
        Args:
            member: 要移除的成员
        """
        # TODO: 成员五实现
        # 1. 在members列表中查找成员
        # 2. 如果找到，从列表中移除
        # 3. 触发member_removed信号
        # 4. 触发member_list_updated信号
        pass
    
    def get_member_list(self) -> List[Member]:
        """
        获取当前成员列表
        
        Returns:
            List[Member]: 成员列表
        """
        return self.members.copy()
    
    def get_member_by_ip(self, ip: str, port: int) -> Optional[Member]:
        """
        根据IP和端口查找成员
        
        Args:
            ip: IP地址
            port: 端口号
            
        Returns:
            Optional[Member]: 找到的成员，未找到返回None
        """
        # TODO: 成员五实现
        # 遍历members列表查找匹配的成员
        pass
    
    def broadcast_join(self):
        """
        广播加入消息
        通知其他成员本地用户已加入
        """
        try:
            # TODO: 成员五实现
            # 1. 构造JOIN类型的ChatMessage
            # 2. 使用 self.dispatcher.broadcast_message() 广播
            
            # 示例代码：
            # message = ChatMessage(
            #     msg_type=MessageType.JOIN,
            #     sender=self.local_member,
            #     content="JOIN"
            # )
            # self.dispatcher.broadcast_message(message.to_dict())
            pass
        except Exception as e:
            print(f"广播加入消息失败: {e}")
    
    def broadcast_leave(self):
        """
        广播离开消息
        通知其他成员本地用户即将离开
        """
        try:
            # TODO: 成员五实现
            # 1. 构造LEAVE类型的ChatMessage
            # 2. 使用 self.dispatcher.broadcast_message() 广播
            
            # 示例代码：
            # message = ChatMessage(
            #     msg_type=MessageType.LEAVE,
            #     sender=self.local_member,
            #     content="LEAVE"
            # )
            # self.dispatcher.broadcast_message(message.to_dict())
            pass
        except Exception as e:
            print(f"广播离开消息失败: {e}")
    
    def handle_join_message(self, message: dict, addr: tuple):
        """
        处理成员加入消息（由MessageDispatcher分发过来）
        
        Args:
            message: 消息字典
            addr: 发送者地址
        """
        try:
            # TODO: 成员五实现
            # 1. 从message中提取sender信息
            # 2. 创建Member对象
            # 3. 调用add_member添加成员
            
            # 示例代码：
            # sender_data = message.get('sender')
            # member = Member.from_dict(sender_data)
            # self.add_member(member)
            pass
        except Exception as e:
            print(f"处理加入消息失败: {e}")
    
    def handle_leave_message(self, message: dict, addr: tuple):
        """
        处理成员离开消息（由MessageDispatcher分发过来）
        
        Args:
            message: 消息字典
            addr: 发送者地址
        """
        try:
            # TODO: 成员五实现
            # 1. 从message中提取sender信息
            # 2. 创建Member对象
            # 3. 调用remove_member移除成员
            
            # 示例代码：
            # sender_data = message.get('sender')
            # member = Member.from_dict(sender_data)
            # self.remove_member(member)
            pass
        except Exception as e:
            print(f"处理离开消息失败: {e}")
    
    def clear_members(self):
        """
        清空成员列表
        """
        self.members.clear()
        self.member_list_updated.emit([])

