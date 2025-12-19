"""
手动刷新模块 - 完整实现
"""

from PyQt5.QtCore import QObject, pyqtSignal, QTimer

from ..common.config import *
from ..common.message_types import *
from ..common.utils import *


class MemberRefresh(QObject):
    """成员刷新类"""
    
    refresh_started = pyqtSignal()
    refresh_completed = pyqtSignal(int)
    
    def __init__(self, local_member: Member, message_dispatcher):
        super().__init__()
        self.local_member = local_member
        self.dispatcher = message_dispatcher
        self.is_refreshing = False
        self.discovered_count = 0
    
    def refresh_members(self):
        """手动刷新成员列表"""
        if self.is_refreshing:
            print("正在刷新中，请稍候...")
            return
        
        try:
            self.is_refreshing = True
            self.discovered_count = 0
            self.refresh_started.emit()
            print("[刷新] 开始刷新成员列表")
            
            # 发送刷新请求（使用DISCOVERY消息）
            message = ChatMessage(
                msg_type=MessageType.REFRESH,
                sender=self.local_member,
                content=REFRESH_KEYWORD
            )
            self.dispatcher.broadcast_message(message.to_dict())
            
            # 3秒后触发完成
            QTimer.singleShot(3000, self._on_refresh_timeout)
            
        except Exception as e:
            print(f"刷新成员列表失败: {e}")
            self.is_refreshing = False
    
    def _on_refresh_timeout(self):
        """刷新超时"""
        print(f"[刷新] 刷新完成，发现 {self.discovered_count} 个成员")
        self.is_refreshing = False
        self.refresh_completed.emit(self.discovered_count)
    
    def handle_refresh_message(self, message: dict, addr: tuple):
        """处理刷新消息"""
        try:
            msg_type = message.get('msg_type')
            
            if msg_type == MessageType.REFRESH.value:
                # 收到刷新请求，返回本地信息
                response = ChatMessage(
                    msg_type=MessageType.DISCOVERY_RESPONSE,
                    sender=self.local_member,
                    content="REFRESH_RESPONSE"
                )
                self.dispatcher.send_message(response.to_dict(), addr[0], addr[1])
                print(f"[刷新] 响应刷新请求，来自 {addr[0]}")
                
            elif msg_type == MessageType.DISCOVERY_RESPONSE.value:
                # 收到刷新响应
                if self.is_refreshing:
                    self.discovered_count += 1
                    
        except Exception as e:
            print(f"处理刷新消息失败: {e}")



