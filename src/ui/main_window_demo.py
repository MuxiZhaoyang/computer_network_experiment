"""
主窗口 - Demo简化版本
快速可用的聊天界面
"""

import sys
from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QTextEdit, QLineEdit, QPushButton, QListWidget,
    QLabel, QMessageBox, QInputDialog, QSplitter,
    QGroupBox
)
from PyQt5.QtCore import Qt

from ..common.config import *
from ..common.message_types import *
from ..common.utils import *
from ..core import *


class MainWindow(QMainWindow):
    """主窗口类 - Demo版本"""
    
    def __init__(self):
        super().__init__()
        self.local_member = None
        self.init_ui()
        self.init_modules()
        self.connect_signals()
    
    def init_ui(self):
        """初始化界面"""
        self.setWindowTitle(WINDOW_TITLE)
        self.setGeometry(100, 100, WINDOW_WIDTH, WINDOW_HEIGHT)
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)
        
        # 左侧：成员列表
        left_panel = self.create_member_panel()
        
        # 右侧：聊天区域
        right_panel = self.create_chat_panel()
        
        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.addWidget(left_panel)
        splitter.addWidget(right_panel)
        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 3)
        
        main_layout.addWidget(splitter)
        self.statusBar().showMessage('准备就绪')
    
    def create_member_panel(self) -> QWidget:
        """创建成员列表面板"""
        panel = QWidget()
        layout = QVBoxLayout(panel)
        
        # 用户信息
        user_group = QGroupBox("用户信息")
        user_layout = QVBoxLayout()
        self.label_username = QLabel("用户名：未设置")
        self.label_ip = QLabel(f"IP：{get_local_ip()}")
        user_layout.addWidget(self.label_username)
        user_layout.addWidget(self.label_ip)
        user_group.setLayout(user_layout)
        layout.addWidget(user_group)
        
        # 成员列表
        member_group = QGroupBox("在线成员")
        member_layout = QVBoxLayout()
        
        self.btn_refresh = QPushButton("🔄 刷新成员列表")
        self.btn_refresh.clicked.connect(self.on_refresh_members)
        member_layout.addWidget(self.btn_refresh)
        
        self.list_members = QListWidget()
        member_layout.addWidget(self.list_members)
        
        member_group.setLayout(member_layout)
        layout.addWidget(member_group)
        
        return panel
    
    def create_chat_panel(self) -> QWidget:
        """创建聊天面板"""
        panel = QWidget()
        layout = QVBoxLayout(panel)
        
        self.text_chat = QTextEdit()
        self.text_chat.setReadOnly(True)
        layout.addWidget(self.text_chat)
        
        input_layout = QHBoxLayout()
        
        self.input_message = QLineEdit()
        self.input_message.setPlaceholderText("输入消息...")
        self.input_message.returnPressed.connect(self.on_send_message)
        input_layout.addWidget(self.input_message)
        
        self.btn_send = QPushButton("发送")
        self.btn_send.clicked.connect(self.on_send_message)
        input_layout.addWidget(self.btn_send)
        
        self.btn_broadcast = QPushButton("广播")
        self.btn_broadcast.clicked.connect(self.on_broadcast_message)
        input_layout.addWidget(self.btn_broadcast)
        
        layout.addLayout(input_layout)
        
        return panel
    
    def init_modules(self):
        """初始化核心模块"""
        # 获取用户名
        username, ok = QInputDialog.getText(
            self, '设置用户名', '请输入您的用户名：',
            text=f'User_{get_local_ip().split(".")[-1]}'
        )
        
        if not ok or not username:
            QMessageBox.warning(self, '警告', '必须设置用户名！')
            sys.exit(0)
        
        # 创建本地成员对象
        local_ip = get_local_ip()
        self.local_member = Member(
            username=username,
            ip=local_ip,
            udp_port=DEFAULT_UDP_PORT,
            tcp_port=DEFAULT_TCP_PORT
        )
        
        # 更新UI
        self.label_username.setText(f"用户名：{username}")
        self.label_ip.setText(f"IP：{local_ip}")
        
        # 创建消息分发器
        self.message_dispatcher = MessageDispatcher(self.local_member)
        self.message_dispatcher.start()
        
        # 创建各功能模块
        self.network_discovery = NetworkDiscovery(self.local_member, self.message_dispatcher)
        self.message_p2p = MessageP2P(self.local_member, self.message_dispatcher)
        self.message_broadcast = MessageBroadcast(self.local_member, self.message_dispatcher)
        self.member_manager = MemberManager(self.local_member, self.message_dispatcher)
        self.member_refresh = MemberRefresh(self.local_member, self.message_dispatcher)
        
        print(f"[系统] 用户 {username} 已启动")
    
    def connect_signals(self):
        """连接信号和槽"""
        # Dispatcher → 各模块
        self.message_dispatcher.discovery_message.connect(
            self.network_discovery.handle_message)
        self.message_dispatcher.p2p_message.connect(
            self.message_p2p.handle_message)
        self.message_dispatcher.broadcast_message.connect(
            self.message_broadcast.handle_message)
        self.message_dispatcher.join_message.connect(
            self.member_manager.handle_join_message)
        self.message_dispatcher.leave_message.connect(
            self.member_manager.handle_leave_message)
        self.message_dispatcher.refresh_message.connect(
            self.member_refresh.handle_refresh_message)
        
        # 各模块 → UI
        self.network_discovery.member_discovered.connect(
            self.on_member_discovered)
        self.message_p2p.message_received.connect(
            self.on_message_received)
        self.message_broadcast.broadcast_received.connect(
            self.on_broadcast_received)
        self.member_manager.member_list_updated.connect(
            self.on_member_list_updated)
        
        # 成员列表同步
        self.member_manager.member_list_updated.connect(
            self.message_broadcast.update_member_list)
        
        # 发送初始广播
        self.network_discovery.send_discovery_broadcast()
        print("[系统] 已发送初始发现广播")
    
    def on_refresh_members(self):
        """刷新成员列表"""
        self.member_refresh.refresh_members()
        self.statusBar().showMessage('正在刷新...', 3000)
    
    def on_send_message(self):
        """发送一对一消息"""
        content = self.input_message.text().strip()
        if not content:
            return
        
        selected_items = self.list_members.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, '提示', '请先选择接收者！')
            return
        
        # 获取选中的成员
        member_index = self.list_members.row(selected_items[0])
        members = self.member_manager.get_member_list()
        if member_index < len(members):
            receiver = members[member_index]
            
            # 发送消息
            if self.message_p2p.send_p2p_message(receiver, content):
                self.append_chat_message(
                    f"我 → {receiver.username}", content, False)
                self.input_message.clear()
            else:
                self.statusBar().showMessage('发送失败', 3000)
    
    def on_broadcast_message(self):
        """发送广播消息"""
        content = self.input_message.text().strip()
        if not content:
            return
        
        if self.message_broadcast.send_broadcast_message(content):
            self.append_chat_message("我（广播）", content, True)
            self.input_message.clear()
        else:
            self.statusBar().showMessage('广播失败', 3000)
    
    def on_member_discovered(self, member: Member):
        """发现新成员"""
        self.member_manager.add_member(member)
    
    def on_message_received(self, message: ChatMessage):
        """接收到消息"""
        sender_name = message.sender.username
        self.append_chat_message(sender_name, message.content, False)
    
    def on_broadcast_received(self, message: ChatMessage):
        """接收到广播"""
        sender_name = message.sender.username
        self.append_chat_message(f"{sender_name}（广播）", message.content, True)
    
    def on_member_list_updated(self, members: list):
        """成员列表更新"""
        self.list_members.clear()
        for member in members:
            self.list_members.addItem(f"{member.username} ({member.ip})")
        
        count = len(members)
        self.statusBar().showMessage(f'在线成员：{count}人')
    
    def append_chat_message(self, sender: str, content: str, is_broadcast: bool):
        """添加聊天消息"""
        msg_type = "[广播]" if is_broadcast else "[消息]"
        self.text_chat.append(f"{msg_type} {sender}: {content}")
    
    def closeEvent(self, event):
        """关闭事件"""
        reply = QMessageBox.question(
            self, '确认退出', '确定要退出吗？',
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            # 清理资源
            if hasattr(self, 'member_manager'):
                self.member_manager.broadcast_leave()
            if hasattr(self, 'message_dispatcher'):
                self.message_dispatcher.stop()
            event.accept()
        else:
            event.ignore()


