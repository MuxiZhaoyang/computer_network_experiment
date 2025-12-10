"""
主窗口UI模块 - 成员七负责
功能：整合各个功能模块，设计用户界面
"""

import sys
from typing import Optional
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QTextEdit, QLineEdit, QPushButton, QListWidget,
    QLabel, QFileDialog, QMessageBox, QSplitter,
    QGroupBox, QProgressBar, QListWidgetItem
)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QAction

from ..common.config import *
from ..common.message_types import *
from ..common.utils import *
from ..core import *


class MainWindow(QMainWindow):
    """
    主窗口类
    负责整合所有功能模块并提供用户界面
    """
    
    def __init__(self):
        """
        初始化主窗口
        """
        super().__init__()
        
        # 本地用户信息
        self.local_member: Optional[Member] = None
        
        # 核心功能模块实例
        self.network_discovery: Optional[NetworkDiscovery] = None
        self.message_p2p: Optional[MessageP2P] = None
        self.message_broadcast: Optional[MessageBroadcast] = None
        self.file_transfer: Optional[FileTransfer] = None
        self.member_manager: Optional[MemberManager] = None
        self.member_refresh: Optional[MemberRefresh] = None
        
        # 初始化UI
        self.init_ui()
        
        # 初始化核心模块
        self.init_modules()
        
        # 连接信号和槽
        self.connect_signals()
    
    def init_ui(self):
        """
        初始化用户界面
        """
        # TODO: 成员七实现
        # 设置窗口属性
        self.setWindowTitle(WINDOW_TITLE)
        self.setGeometry(100, 100, WINDOW_WIDTH, WINDOW_HEIGHT)
        
        # 创建中心部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 创建主布局
        main_layout = QHBoxLayout(central_widget)
        
        # 左侧：成员列表区域
        left_panel = self.create_member_panel()
        
        # 右侧：聊天区域
        right_panel = self.create_chat_panel()
        
        # 使用分割器
        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.addWidget(left_panel)
        splitter.addWidget(right_panel)
        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 3)
        
        main_layout.addWidget(splitter)
        
        # 创建菜单栏
        self.create_menu_bar()
        
        # 创建状态栏
        self.statusBar().showMessage('准备就绪')
    
    def create_member_panel(self) -> QWidget:
        """
        创建成员列表面板
        
        Returns:
            QWidget: 成员面板
        """
        # TODO: 成员七实现
        panel = QWidget()
        layout = QVBoxLayout(panel)
        
        # 用户信息区域
        user_group = QGroupBox("用户信息")
        user_layout = QVBoxLayout()
        self.label_username = QLabel("用户名：未设置")
        self.label_ip = QLabel(f"IP：{get_local_ip()}")
        user_layout.addWidget(self.label_username)
        user_layout.addWidget(self.label_ip)
        user_group.setLayout(user_layout)
        layout.addWidget(user_group)
        
        # 成员列表区域
        member_group = QGroupBox("在线成员")
        member_layout = QVBoxLayout()
        
        # 刷新按钮
        self.btn_refresh = QPushButton("🔄 刷新成员列表")
        self.btn_refresh.clicked.connect(self.on_refresh_members)
        member_layout.addWidget(self.btn_refresh)
        
        # 成员列表
        self.list_members = QListWidget()
        self.list_members.itemDoubleClicked.connect(self.on_member_double_clicked)
        member_layout.addWidget(self.list_members)
        
        member_group.setLayout(member_layout)
        layout.addWidget(member_group)
        
        return panel
    
    def create_chat_panel(self) -> QWidget:
        """
        创建聊天面板
        
        Returns:
            QWidget: 聊天面板
        """
        # TODO: 成员七实现
        panel = QWidget()
        layout = QVBoxLayout(panel)
        
        # 聊天显示区域
        self.text_chat = QTextEdit()
        self.text_chat.setReadOnly(True)
        layout.addWidget(self.text_chat)
        
        # 输入区域
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
        
        self.btn_send_file = QPushButton("发送文件")
        self.btn_send_file.clicked.connect(self.on_send_file)
        input_layout.addWidget(self.btn_send_file)
        
        layout.addLayout(input_layout)
        
        # 文件传输进度条
        self.progress_file = QProgressBar()
        self.progress_file.setVisible(False)
        layout.addWidget(self.progress_file)
        
        return panel
    
    def create_menu_bar(self):
        """
        创建菜单栏
        """
        # TODO: 成员七实现
        menubar = self.menuBar()
        
        # 文件菜单
        file_menu = menubar.addMenu('文件')
        
        exit_action = QAction('退出', self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # 帮助菜单
        help_menu = menubar.addMenu('帮助')
        
        about_action = QAction('关于', self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
    
    def init_modules(self):
        """
        初始化核心功能模块
        """
        # TODO: 成员七实现
        # 参考 docs/架构优化后的成员任务.md 中的示例代码
        
        # 1. 获取用户名（可以弹出对话框输入）
        from ..main import get_username
        # username = get_username()  # 取消注释
        
        # 2. 创建本地成员对象
        # local_ip = get_local_ip()
        # self.local_member = Member(
        #     username=username,
        #     ip=local_ip,
        #     udp_port=DEFAULT_UDP_PORT,
        #     tcp_port=DEFAULT_TCP_PORT
        # )
        
        # 3. 创建消息分发器（最先创建）
        # self.message_dispatcher = MessageDispatcher(self.local_member)
        # self.message_dispatcher.start()
        
        # 4. 创建各个核心模块（传入dispatcher）
        # self.network_discovery = NetworkDiscovery(self.local_member, self.message_dispatcher)
        # self.message_p2p = MessageP2P(self.local_member, self.message_dispatcher)
        # self.message_broadcast = MessageBroadcast(self.local_member, self.message_dispatcher)
        # self.member_manager = MemberManager(self.local_member, self.message_dispatcher)
        # self.member_refresh = MemberRefresh(self.local_member, self.message_dispatcher)
        # self.file_transfer = FileTransfer(self.local_member)
        # self.file_transfer.start()
        
        pass
    
    def connect_signals(self):
        """
        连接信号和槽
        """
        # TODO: 成员七实现
        # 参考 docs/架构优化后的成员任务.md 中的示例代码
        
        # *** 第一步：连接dispatcher的信号到各模块的处理函数 ***
        # self.message_dispatcher.discovery_message.connect(
        #     self.network_discovery.handle_message)
        # self.message_dispatcher.p2p_message.connect(
        #     self.message_p2p.handle_message)
        # self.message_dispatcher.broadcast_message.connect(
        #     self.message_broadcast.handle_message)
        # self.message_dispatcher.join_message.connect(
        #     self.member_manager.handle_join_message)
        # self.message_dispatcher.leave_message.connect(
        #     self.member_manager.handle_leave_message)
        # self.message_dispatcher.refresh_message.connect(
        #     self.member_refresh.handle_refresh_message)
        
        # *** 第二步：连接各模块的信号到UI槽函数 ***
        # self.network_discovery.member_discovered.connect(self.on_member_discovered)
        # self.message_p2p.message_received.connect(self.on_message_received)
        # self.message_broadcast.broadcast_received.connect(self.on_broadcast_received)
        # self.file_transfer.file_request_received.connect(self.on_file_request)
        # self.file_transfer.transfer_progress.connect(self.on_transfer_progress)
        # self.member_manager.member_list_updated.connect(self.on_member_list_updated)
        
        # *** 第三步：成员列表同步到广播模块 ***
        # self.member_manager.member_list_updated.connect(
        #     self.message_broadcast.update_member_list)
        
        # *** 第四步：发送初始发现广播 ***
        # self.network_discovery.send_discovery_broadcast()
        
        pass
    
    # ========== 槽函数 ==========
    
    def on_refresh_members(self):
        """
        刷新成员列表按钮点击事件
        """
        # TODO: 成员七实现
        # 调用member_refresh.refresh_members()
        pass
    
    def on_send_message(self):
        """
        发送消息按钮点击事件
        """
        # TODO: 成员七实现
        # 1. 获取输入的消息
        # 2. 获取选中的成员
        # 3. 调用message_p2p.send_p2p_message()
        # 4. 在聊天窗口显示发送的消息
        # 5. 清空输入框
        pass
    
    def on_broadcast_message(self):
        """
        广播消息按钮点击事件
        """
        # TODO: 成员七实现
        # 1. 获取输入的消息
        # 2. 调用message_broadcast.send_broadcast_message()
        # 3. 在聊天窗口显示广播的消息
        # 4. 清空输入框
        pass
    
    def on_send_file(self):
        """
        发送文件按钮点击事件
        """
        # TODO: 成员七实现
        # 1. 获取选中的成员
        # 2. 打开文件选择对话框
        # 3. 调用file_transfer.send_file()
        pass
    
    def on_member_double_clicked(self, item: QListWidgetItem):
        """
        成员列表双击事件
        
        Args:
            item: 被双击的列表项
        """
        # TODO: 成员七实现
        # 可以实现双击成员打开私聊窗口等功能
        pass
    
    def on_member_discovered(self, member: Member):
        """
        发现新成员信号的槽函数
        
        Args:
            member: 发现的成员
        """
        # TODO: 成员七实现
        # 调用member_manager.add_member()
        pass
    
    def on_message_received(self, message: ChatMessage):
        """
        接收到消息信号的槽函数
        
        Args:
            message: 接收到的消息
        """
        # TODO: 成员七实现
        # 在聊天窗口显示接收到的消息
        pass
    
    def on_broadcast_received(self, message: ChatMessage):
        """
        接收到广播消息信号的槽函数
        
        Args:
            message: 广播消息
        """
        # TODO: 成员七实现
        # 在聊天窗口显示广播消息
        pass
    
    def on_file_request(self, file_info: FileTransferInfo):
        """
        收到文件传输请求信号的槽函数
        
        Args:
            file_info: 文件传输信息
        """
        # TODO: 成员七实现
        # 弹出对话框询问是否接受文件
        pass
    
    def on_transfer_progress(self, filename: str, percentage: int):
        """
        文件传输进度信号的槽函数
        
        Args:
            filename: 文件名
            percentage: 进度百分比
        """
        # TODO: 成员七实现
        # 更新进度条
        pass
    
    def on_member_list_updated(self, members: list):
        """
        成员列表更新信号的槽函数
        
        Args:
            members: 成员列表
        """
        # TODO: 成员七实现
        # 更新UI中的成员列表
        pass
    
    def append_chat_message(self, sender: str, content: str, is_broadcast: bool = False):
        """
        在聊天窗口添加消息
        
        Args:
            sender: 发送者
            content: 消息内容
            is_broadcast: 是否是广播消息
        """
        # TODO: 成员七实现
        msg_type = "[广播]" if is_broadcast else "[消息]"
        self.text_chat.append(f"{msg_type} {sender}: {content}")
    
    def show_about(self):
        """
        显示关于对话框
        """
        QMessageBox.about(
            self,
            "关于",
            f"{WINDOW_TITLE}\n\n"
            "一个简易的局域网即时通信工具\n"
            "支持UDP广播发现、P2P消息、广播消息和TCP文件传输\n\n"
            "技术栈：Python + PyQt6"
        )
    
    def closeEvent(self, event):
        """
        窗口关闭事件
        
        Args:
            event: 关闭事件
        """
        # TODO: 成员七实现
        # 1. 广播离开消息
        # 2. 停止所有服务
        # 3. 关闭socket
        # 4. 接受关闭事件
        reply = QMessageBox.question(
            self,
            '确认退出',
            '确定要退出吗？',
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            # 清理资源
            if self.member_manager:
                self.member_manager.broadcast_leave()
            if self.network_discovery:
                self.network_discovery.stop()
            if self.file_transfer:
                self.file_transfer.stop()
            event.accept()
        else:
            event.ignore()

