"""
广播消息模块测试脚本
严格按照《理想实现结果清单.md》和《详细测试方法指南.md》进行测试
"""

import sys
import os
import unittest
from unittest.mock import MagicMock

# 添加项目根目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.common.message_types import Member, ChatMessage, MessageType
from src.core.message_broadcast import MessageBroadcast

class TestMessageBroadcast(unittest.TestCase):
    def setUp(self):
        # 创建模拟的本地成员
        self.local_member = Member(
            username="TestUser",
            ip="127.0.0.1",
            udp_port=8888,
            tcp_port=8889
        )
        
        # 创建模拟的消息分发器
        self.mock_dispatcher = MagicMock()
        self.mock_dispatcher.broadcast_message.return_value = True
        
        # 创建广播模块实例
        self.broadcast = MessageBroadcast(self.local_member, self.mock_dispatcher)
        
    def test_verification_flow_from_docs(self):
        """
        对应《理想实现结果清单.md》中的验证方法：
        1. 设置成员列表
        2. 发送广播
        """
        print("\n=== 测试场景：标准广播流程 ===")
        
        # 1. 设置成员列表 (模拟3个成员，对应文档要求)
        member1 = Member("User1", "192.168.1.2", 8888, 8889)
        member2 = Member("User2", "192.168.1.3", 8888, 8889)
        member3 = Member("User3", "192.168.1.4", 8888, 8889)
        members = [member1, member2, member3]
        
        self.broadcast.update_member_list(members)
        
        # 验证成员列表长度
        self.assertEqual(len(self.broadcast.member_list), 3)
        print(f"✓ 成员列表更新验证通过 (当前成员数: {len(self.broadcast.member_list)})")

        # 2. 发送广播
        content = "Test broadcast message"
        result = self.broadcast.send_broadcast_message(content)
        
        # 验证结果
        self.assertTrue(result)
        
        # 验证调用了dispatcher的广播接口
        # 根据架构设计，使用UDP广播地址(255.255.255.255)发送，确保"不遗漏任何成员"
        self.mock_dispatcher.broadcast_message.assert_called_once()
        
        # 验证发送的消息结构
        args = self.mock_dispatcher.broadcast_message.call_args[0]
        msg_dict = args[0]
        
        self.assertEqual(msg_dict['msg_type'], MessageType.BROADCAST_MESSAGE.value)
        self.assertEqual(msg_dict['content'], content)
        self.assertEqual(msg_dict['sender']['username'], self.local_member.username)
        print("✓ 发送广播消息验证通过 (消息类型正确，内容正确)")

    def test_receive_broadcast_from_others(self):
        """
        测试接收来自其他成员的广播消息
        对应文档：能够接收处理广播消息，触发broadcast_received信号
        """
        print("\n=== 测试场景：接收广播消息 ===")
        
        # 模拟来自不同成员的消息
        senders = [
            Member("UserA", "192.168.1.10", 8888, 8889),
            Member("UserB", "192.168.1.11", 8888, 8889)
        ]
        
        # 使用Mock监听信号
        mock_slot = MagicMock()
        self.broadcast.broadcast_received.connect(mock_slot)
        
        for i, sender in enumerate(senders):
            content = f"Message from {sender.username}"
            message = ChatMessage(
                msg_type=MessageType.BROADCAST_MESSAGE,
                sender=sender,
                content=content
            )
            
            # 模拟收到消息
            self.broadcast.handle_message(message.to_dict(), (sender.ip, sender.udp_port))
            
            # 验证信号触发
            self.assertEqual(mock_slot.call_count, i + 1)
            received_msg = mock_slot.call_args[0][0]
            
            self.assertEqual(received_msg.sender.username, sender.username)
            self.assertEqual(received_msg.content, content)
            print(f"✓ 成功接收来自 {sender.username} 的广播消息")

if __name__ == '__main__':
    unittest.main()
