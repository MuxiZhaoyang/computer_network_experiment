"""
消息类型定义模块
定义所有消息类型和数据结构
"""

from enum import Enum
from dataclasses import dataclass
from typing import Optional


class MessageType(Enum):
    """消息类型枚举"""
    DISCOVERY = "DISCOVERY"  # 发现请求
    DISCOVERY_RESPONSE = "DISCOVERY_RESPONSE"  # 发现响应
    JOIN = "JOIN"  # 加入通知
    LEAVE = "LEAVE"  # 离开通知
    REFRESH = "REFRESH"  # 刷新请求
    P2P_MESSAGE = "P2P_MESSAGE"  # 一对一消息
    BROADCAST_MESSAGE = "BROADCAST_MESSAGE"  # 广播消息
    FILE_REQUEST = "FILE_REQUEST"  # 文件传输请求
    FILE_ACCEPT = "FILE_ACCEPT"  # 接受文件传输
    FILE_REJECT = "FILE_REJECT"  # 拒绝文件传输


@dataclass
class Member:
    """组员信息数据类"""
    username: str  # 用户名
    ip: str  # IP地址
    udp_port: int  # UDP端口
    tcp_port: int  # TCP端口
    
    def __eq__(self, other):
        """判断两个成员是否相同"""
        if not isinstance(other, Member):
            return False
        return self.ip == other.ip and self.udp_port == other.udp_port
    
    def __hash__(self):
        """用于set和dict"""
        return hash((self.ip, self.udp_port))
    
    def to_dict(self):
        """转换为字典"""
        return {
            'username': self.username,
            'ip': self.ip,
            'udp_port': self.udp_port,
            'tcp_port': self.tcp_port
        }
    
    @classmethod
    def from_dict(cls, data):
        """从字典创建实例"""
        return cls(
            username=data['username'],
            ip=data['ip'],
            udp_port=data['udp_port'],
            tcp_port=data['tcp_port']
        )


@dataclass
class ChatMessage:
    """聊天消息数据类"""
    msg_type: MessageType  # 消息类型
    sender: Member  # 发送者
    content: str  # 消息内容
    receiver: Optional[Member] = None  # 接收者（一对一消息使用）
    
    def to_dict(self):
        """转换为字典"""
        data = {
            'msg_type': self.msg_type.value,
            'sender': self.sender.to_dict(),
            'content': self.content
        }
        if self.receiver:
            data['receiver'] = self.receiver.to_dict()
        return data
    
    @classmethod
    def from_dict(cls, data):
        """从字典创建实例"""
        return cls(
            msg_type=MessageType(data['msg_type']),
            sender=Member.from_dict(data['sender']),
            content=data['content'],
            receiver=Member.from_dict(data['receiver']) if 'receiver' in data else None
        )


@dataclass
class FileTransferInfo:
    """文件传输信息数据类"""
    filename: str  # 文件名
    filesize: int  # 文件大小
    sender: Member  # 发送者
    receiver: Member  # 接收者
    
    def to_dict(self):
        """转换为字典"""
        return {
            'filename': self.filename,
            'filesize': self.filesize,
            'sender': self.sender.to_dict(),
            'receiver': self.receiver.to_dict()
        }
    
    @classmethod
    def from_dict(cls, data):
        """从字典创建实例"""
        return cls(
            filename=data['filename'],
            filesize=data['filesize'],
            sender=Member.from_dict(data['sender']),
            receiver=Member.from_dict(data['receiver'])
        )

