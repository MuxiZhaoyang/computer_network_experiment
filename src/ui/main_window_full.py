"""
主窗口 - 完整功能版本
包含所有功能：消息、文件传输、成员管理等
"""

import sys
import os
from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QTextEdit, QLineEdit, QPushButton, QListWidget,
    QLabel, QMessageBox, QInputDialog, QSplitter,
    QGroupBox, QProgressBar, QFileDialog
)
from PyQt5.QtCore import Qt

from ..common.config import *
from ..common.message_types import *
from ..common.utils import *
from ..core import *


class MainWindow(QMainWindow):
    """主窗口类 - 完整版本"""
    
    def __init__(self):
        super().__init__()
        self.local_member = None
        self.current_transfer_info = None  # 当前待处理的文件传输请求
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
        
        # 创建菜单栏
        self.create_menu_bar()
        
        self.statusBar().showMessage('准备就绪')
    
    def create_menu_bar(self):
        """创建菜单栏"""
        menubar = self.menuBar()
        
        # 文件菜单
        file_menu = menubar.addMenu('文件')
        
        open_downloads_action = file_menu.addAction('打开下载文件夹')
        open_downloads_action.triggered.connect(self.open_downloads_folder)
        
        file_menu.addSeparator()
        
        exit_action = file_menu.addAction('退出')
        exit_action.triggered.connect(self.close)
        
        # 帮助菜单
        help_menu = menubar.addMenu('帮助')
        
        about_action = help_menu.addAction('关于')
        about_action.triggered.connect(self.show_about)
    
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
        
        # 聊天显示区
        self.text_chat = QTextEdit()
        self.text_chat.setReadOnly(True)
        layout.addWidget(self.text_chat)
        
        # 进度条
        self.progress_file = QProgressBar()
        self.progress_file.setVisible(False)
        self.label_progress = QLabel()
        self.label_progress.setVisible(False)
        layout.addWidget(self.label_progress)
        layout.addWidget(self.progress_file)
        
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
        self.file_transfer = FileTransfer(self.local_member)
        self.file_transfer.start()
        
        print(f"[系统] 用户 {username} 已启动")
        print(f"[系统] UDP端口: {DEFAULT_UDP_PORT}, TCP端口: {DEFAULT_TCP_PORT}")
    
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
        
        # 文件传输信号
        self.file_transfer.file_request_received.connect(
            self.on_file_request)
        self.file_transfer.transfer_progress.connect(
            self.on_transfer_progress)
        self.file_transfer.transfer_completed.connect(
            self.on_transfer_completed)
        
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
    
    def on_send_file(self):
        """发送文件"""
        selected_items = self.list_members.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, '提示', '请先选择接收者！')
            return
        
        # 选择文件
        file_path, _ = QFileDialog.getOpenFileName(
            self, '选择要发送的文件', '', 'All Files (*.*)'
        )
        
        if not file_path:
            return
        
        # 检查文件大小
        filesize = os.path.getsize(file_path)
        if filesize > MAX_FILE_SIZE:
            QMessageBox.warning(
                self, '文件过大',
                f'文件大小超过限制！\n最大: {format_file_size(MAX_FILE_SIZE)}\n当前: {format_file_size(filesize)}'
            )
            return
        
        # 获取接收者
        member_index = self.list_members.row(selected_items[0])
        members = self.member_manager.get_member_list()
        if member_index < len(members):
            receiver = members[member_index]
            filename = os.path.basename(file_path)
            
            self.append_chat_message(
                "系统",
                f"正在发送文件 [{filename}] 到 {receiver.username}",
                False
            )
            
            # 发送文件
            self.file_transfer.send_file(file_path, receiver)
    
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
    
    def on_file_request(self, file_info: FileTransferInfo):
        """收到文件传输请求"""
        self.current_transfer_info = file_info
        
        reply = QMessageBox.question(
            self,
            '文件传输请求',
            f'用户 {file_info.sender.username} 请求发送文件：\n\n'
            f'文件名：{file_info.filename}\n'
            f'大小：{format_file_size(file_info.filesize)}\n\n'
            f'是否接受？',
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            self.file_transfer.accept_file(file_info)
            self.append_chat_message(
                "系统",
                f"正在接收文件 [{file_info.filename}] 来自 {file_info.sender.username}",
                False
            )
        else:
            self.file_transfer.reject_file(file_info)
            self.append_chat_message(
                "系统",
                f"已拒绝文件 [{file_info.filename}]",
                False
            )
    
    def on_transfer_progress(self, filename: str, percentage: int):
        """文件传输进度更新"""
        self.progress_file.setVisible(True)
        self.label_progress.setVisible(True)
        self.progress_file.setValue(percentage)
        self.label_progress.setText(f"传输中: {filename} - {percentage}%")
    
    def on_transfer_completed(self, filename: str, success: bool):
        """文件传输完成"""
        self.progress_file.setVisible(False)
        self.label_progress.setVisible(False)
        
        if success:
            self.append_chat_message(
                "系统",
                f"文件传输完成: {filename}",
                False
            )
            self.statusBar().showMessage(f'文件传输完成: {filename}', 5000)
        else:
            self.append_chat_message(
                "系统",
                f"文件传输失败: {filename}",
                False
            )
            self.statusBar().showMessage(f'文件传输失败: {filename}', 5000)
    
    def append_chat_message(self, sender: str, content: str, is_broadcast: bool):
        """添加聊天消息"""
        from datetime import datetime
        timestamp = datetime.now().strftime("%H:%M:%S")
        msg_type = "[广播]" if is_broadcast else "[消息]"
        self.text_chat.append(f"[{timestamp}] {msg_type} {sender}: {content}")
    
    def open_downloads_folder(self):
        """打开下载文件夹"""
        if os.path.exists(DOWNLOAD_DIR):
            os.startfile(DOWNLOAD_DIR)
        else:
            QMessageBox.information(self, '提示', '下载文件夹不存在')
    
    def show_about(self):
        """显示关于对话框"""
        QMessageBox.about(
            self,
            "关于",
            f"{WINDOW_TITLE}\n\n"
            "一个功能完整的局域网即时通信工具\n"
            "支持UDP广播发现、P2P消息、广播消息和TCP文件传输\n\n"
            "技术栈：Python + PyQt5\n"
            "开发团队：计算机网络实验小组6"
        )
    
    def closeEvent(self, event):
        """窗口关闭事件"""
        reply = QMessageBox.question(
            self, '确认退出', '确定要退出吗？',
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            # 清理资源
            print("[系统] 正在退出...")
            if hasattr(self, 'member_manager'):
                self.member_manager.broadcast_leave()
            if hasattr(self, 'message_dispatcher'):
                self.message_dispatcher.stop()
            if hasattr(self, 'file_transfer'):
                self.file_transfer.stop()
            event.accept()
        else:
            event.ignore()



