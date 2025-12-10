"""
示例测试文件
用于测试各个模块的功能
"""

import sys
import os

# 添加src目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from common.message_types import Member, ChatMessage, MessageType
from common.utils import get_local_ip, serialize_message, deserialize_message


def test_member_creation():
    """测试创建成员对象"""
    member = Member(
        username="TestUser",
        ip="192.168.1.100",
        udp_port=8888,
        tcp_port=8889
    )
    assert member.username == "TestUser"
    assert member.ip == "192.168.1.100"
    print("✓ 成员创建测试通过")


def test_member_serialization():
    """测试成员序列化和反序列化"""
    member = Member(
        username="TestUser",
        ip="192.168.1.100",
        udp_port=8888,
        tcp_port=8889
    )
    
    # 转换为字典
    member_dict = member.to_dict()
    assert isinstance(member_dict, dict)
    
    # 从字典创建
    member2 = Member.from_dict(member_dict)
    assert member == member2
    print("✓ 成员序列化测试通过")


def test_message_serialization():
    """测试消息序列化"""
    sender = Member("User1", "192.168.1.100", 8888, 8889)
    message = ChatMessage(
        msg_type=MessageType.P2P_MESSAGE,
        sender=sender,
        content="Hello"
    )
    
    # 序列化
    message_dict = message.to_dict()
    data = serialize_message(message_dict)
    assert isinstance(data, bytes)
    
    # 反序列化
    received_dict = deserialize_message(data)
    assert received_dict is not None
    assert received_dict['content'] == "Hello"
    print("✓ 消息序列化测试通过")


def test_get_local_ip():
    """测试获取本地IP"""
    ip = get_local_ip()
    assert isinstance(ip, str)
    assert len(ip.split('.')) == 4
    print(f"✓ 获取本地IP测试通过: {ip}")


if __name__ == '__main__':
    print("开始运行测试...\n")
    test_member_creation()
    test_member_serialization()
    test_message_serialization()
    test_get_local_ip()
    print("\n所有测试通过！")

