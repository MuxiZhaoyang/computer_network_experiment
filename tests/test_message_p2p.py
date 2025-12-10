"""
MessageP2P 模块单元测试
"""

import os
import sys

from PyQt6.QtCore import QCoreApplication

# 添加项目根目录到路径，再使用 src.* 形式导入
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.common.message_types import Member, ChatMessage, MessageType
from src.core.message_p2p import MessageP2P


def _ensure_qt_app():
    """确保存在QCoreApplication实例。"""
    app = QCoreApplication.instance()
    if app is None:
        QCoreApplication([])


def test_send_p2p_message():
    """验证发送时构造的消息内容和发送调用。"""
    _ensure_qt_app()

    sent_payload = {}

    class DummyDispatcher:
        def send_message(self, message_dict, ip, port):
            sent_payload["message"] = message_dict
            sent_payload["ip"] = ip
            sent_payload["port"] = port
            return True

    local = Member("Alice", "192.168.1.10", 8888, 8889)
    receiver = Member("Bob", "192.168.1.20", 9999, 10000)
    dispatcher = DummyDispatcher()

    p2p = MessageP2P(local, dispatcher)
    ok = p2p.send_p2p_message(receiver, "hello")

    assert ok is True
    assert sent_payload["ip"] == "192.168.1.20"
    assert sent_payload["port"] == 9999
    assert sent_payload["message"]["msg_type"] == MessageType.P2P_MESSAGE.value
    assert sent_payload["message"]["content"] == "hello"
    assert sent_payload["message"]["sender"]["username"] == "Alice"
    assert sent_payload["message"]["receiver"]["username"] == "Bob"


def test_handle_message_emit_signal():
    """验证收到消息后会发射message_received信号。"""
    _ensure_qt_app()

    received = []
    local = Member("Alice", "192.168.1.10", 8888, 8889)

    class DummyDispatcher:
        def send_message(self, *args, **kwargs):
            return True

    dispatcher = DummyDispatcher()
    p2p = MessageP2P(local, dispatcher)
    p2p.message_received.connect(lambda msg: received.append(msg))

    sender = Member("Bob", "192.168.1.20", 9999, 10000)
    chat = ChatMessage(
        msg_type=MessageType.P2P_MESSAGE,
        sender=sender,
        receiver=local,
        content="hi"
    )

    p2p.handle_message(chat.to_dict(), (sender.ip, sender.udp_port))

    assert len(received) == 1
    assert received[0].content == "hi"
    assert received[0].sender.username == "Bob"
    assert received[0].receiver.username == "Alice"


if __name__ == "__main__":
    _ensure_qt_app()
    test_send_p2p_message()
    test_handle_message_emit_signal()
    print("MessageP2P tests passed.")
