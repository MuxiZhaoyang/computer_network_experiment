"""
组员管理模块 - 完整实现版本
"""

from typing import List, Optional
from PyQt5.QtCore import QObject, pyqtSignal

from ..common.config import *
from ..common.message_types import *
from ..common.utils import *


class MemberManager(QObject):
    """组员管理类"""
    
    member_added = pyqtSignal(Member)
    member_removed = pyqtSignal(Member)
    member_list_updated = pyqtSignal(list)
    
    def __init__(self, local_member: Member, message_dispatcher):
        super().__init__()
        self.local_member = local_member
        self.dispatcher = message_dispatcher
        self.members: List[Member] = []
    
    def add_member(self, member: Member):
        """添加成员"""
        # 检查是否是本地用户
        if member.ip == self.local_member.ip and member.udp_port == self.local_member.udp_port:
            return
        
        # 检查是否已存在
        for existing_member in self.members:
            if existing_member.ip == member.ip and existing_member.udp_port == member.udp_port:
                return
        
        self.members.append(member)
        print(f"[管理] 添加成员: {member.username} ({member.ip})")
        self.member_added.emit(member)
        self.member_list_updated.emit(self.members.copy())
    
    def remove_member(self, member: Member):
        """移除成员"""
        for existing_member in self.members:
            if existing_member.ip == member.ip and existing_member.udp_port == member.udp_port:
                self.members.remove(existing_member)
                print(f"[管理] 移除成员: {member.username}")
                self.member_removed.emit(member)
                self.member_list_updated.emit(self.members.copy())
                break
    
    def get_member_list(self) -> List[Member]:
        """获取成员列表"""
        return self.members.copy()
    
    def get_member_by_ip(self, ip: str, port: int) -> Optional[Member]:
        """根据IP查找成员"""
        for member in self.members:
            if member.ip == ip and member.udp_port == port:
                return member
        return None
    
    def broadcast_join(self):
        """广播加入"""
        try:
            message = ChatMessage(
                msg_type=MessageType.JOIN,
                sender=self.local_member,
                content="JOIN"
            )
            self.dispatcher.broadcast_message(message.to_dict())
            print("[管理] 广播加入消息")
        except Exception as e:
            print(f"广播加入消息失败: {e}")
    
    def broadcast_leave(self):
        """广播离开"""
        try:
            message = ChatMessage(
                msg_type=MessageType.LEAVE,
                sender=self.local_member,
                content="LEAVE"
            )
            self.dispatcher.broadcast_message(message.to_dict())
            print("[管理] 广播离开消息")
        except Exception as e:
            print(f"广播离开消息失败: {e}")
    
    def handle_join_message(self, message: dict, addr: tuple):
        """处理加入消息"""
        try:
            sender_data = message.get('sender')
            if sender_data:
                member = Member.from_dict(sender_data)
                self.add_member(member)
        except Exception as e:
            print(f"处理加入消息失败: {e}")
    
    def handle_leave_message(self, message: dict, addr: tuple):
        """处理离开消息"""
        try:
            sender_data = message.get('sender')
            if sender_data:
                member = Member.from_dict(sender_data)
                self.remove_member(member)
        except Exception as e:
            print(f"处理离开消息失败: {e}")
    
    def clear_members(self):
        """清空成员列表"""
        self.members.clear()
        self.member_list_updated.emit([])


