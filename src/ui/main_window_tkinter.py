"""
主窗口 - Tkinter版本（Python自带GUI，无需额外安装）
完整功能实现
"""

import sys
import os
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, filedialog, simpledialog
from datetime import datetime
import threading

from ..common.config import *
from ..common.message_types import *
from ..common.utils import *
from ..core import *


class MainWindow:
    """主窗口类 - Tkinter完整版本"""
    
    def __init__(self, root):
        self.root = root
        self.local_member = None
        self.current_transfer_info = None
        
        # 初始化
        self.init_modules()
        self.init_ui()
        self.connect_signals()
        
        # 设置关闭处理
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
    
    def init_ui(self):
        """初始化界面"""
        self.root.title(WINDOW_TITLE)
        self.root.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}")
        
        # 主框架
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # 创建左右分栏
        # 左侧：成员列表（30%）
        left_frame = self.create_member_panel(main_frame)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, padx=(0, 5))
        
        # 右侧：聊天区域（70%）
        right_frame = self.create_chat_panel(main_frame)
        right_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # 状态栏
        self.status_label = ttk.Label(self.root, text="准备就绪", relief=tk.SUNKEN)
        self.status_label.pack(side=tk.BOTTOM, fill=tk.X)
    
    def create_member_panel(self, parent):
        """创建成员列表面板"""
        frame = ttk.Frame(parent, width=250)
        
        # 用户信息组
        user_frame = ttk.LabelFrame(frame, text="用户信息", padding=10)
        user_frame.pack(fill=tk.X, pady=(0, 5))
        
        self.label_username = ttk.Label(user_frame, text=f"用户名：{self.local_member.username}")
        self.label_username.pack()
        
        self.label_ip = ttk.Label(user_frame, text=f"IP：{self.local_member.ip}")
        self.label_ip.pack()
        
        # 在线成员组
        member_frame = ttk.LabelFrame(frame, text="在线成员", padding=10)
        member_frame.pack(fill=tk.BOTH, expand=True)
        
        # 刷新按钮
        btn_refresh = ttk.Button(member_frame, text="🔄 刷新成员列表", 
                                  command=self.on_refresh_members)
        btn_refresh.pack(fill=tk.X, pady=(0, 5))
        
        # 成员列表
        list_frame = ttk.Frame(member_frame)
        list_frame.pack(fill=tk.BOTH, expand=True)
        
        scrollbar = ttk.Scrollbar(list_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.listbox_members = tk.Listbox(list_frame, yscrollcommand=scrollbar.set)
        self.listbox_members.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.listbox_members.yview)
        
        return frame
    
    def create_chat_panel(self, parent):
        """创建聊天面板"""
        frame = ttk.Frame(parent)
        
        # 聊天显示区
        self.text_chat = scrolledtext.ScrolledText(frame, wrap=tk.WORD, height=20)
        self.text_chat.pack(fill=tk.BOTH, expand=True, pady=(0, 5))
        self.text_chat.config(state=tk.DISABLED)
        
        # 进度条
        self.progress_frame = ttk.Frame(frame)
        self.label_progress = ttk.Label(self.progress_frame, text="")
        self.label_progress.pack()
        self.progress_bar = ttk.Progressbar(self.progress_frame, mode='determinate')
        self.progress_bar.pack(fill=tk.X)
        # 默认隐藏
        
        # 输入区域
        input_frame = ttk.Frame(frame)
        input_frame.pack(fill=tk.X)
        
        self.entry_message = ttk.Entry(input_frame)
        self.entry_message.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        self.entry_message.bind('<Return>', lambda e: self.on_send_message())
        
        btn_send = ttk.Button(input_frame, text="发送", command=self.on_send_message)
        btn_send.pack(side=tk.LEFT, padx=2)
        
        btn_broadcast = ttk.Button(input_frame, text="广播", command=self.on_broadcast_message)
        btn_broadcast.pack(side=tk.LEFT, padx=2)
        
        btn_file = ttk.Button(input_frame, text="发送文件", command=self.on_send_file)
        btn_file.pack(side=tk.LEFT, padx=2)
        
        return frame
    
    def init_modules(self):
        """初始化核心模块"""
        # 获取用户名
        username = simpledialog.askstring("设置用户名", "请输入您的用户名：",
                                          initialvalue=f'User_{get_local_ip().split(".")[-1]}')
        
        if not username:
            messagebox.showwarning('警告', '必须设置用户名！')
            sys.exit(0)
        
        # 创建本地成员
        local_ip = get_local_ip()
        self.local_member = Member(
            username=username,
            ip=local_ip,
            udp_port=DEFAULT_UDP_PORT,
            tcp_port=DEFAULT_TCP_PORT
        )
        
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
    
    def connect_signals(self):
        """连接信号和槽"""
        # Dispatcher → 各模块（使用Qt信号自动调用）
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
        
        # 各模块 → UI（使用线程安全的after调用）
        self.network_discovery.member_discovered.connect(
            lambda m: self.root.after(0, self.on_member_discovered, m))
        self.message_p2p.message_received.connect(
            lambda m: self.root.after(0, self.on_message_received, m))
        self.message_broadcast.broadcast_received.connect(
            lambda m: self.root.after(0, self.on_broadcast_received, m))
        self.member_manager.member_list_updated.connect(
            lambda members: self.root.after(0, self.on_member_list_updated, members))
        
        # 文件传输信号
        self.file_transfer.file_request_received.connect(
            lambda info: self.root.after(0, self.on_file_request, info))
        self.file_transfer.transfer_progress.connect(
            lambda f, p: self.root.after(0, self.on_transfer_progress, f, p))
        self.file_transfer.transfer_completed.connect(
            lambda f, s: self.root.after(0, self.on_transfer_completed, f, s))
        
        # 成员列表同步
        self.member_manager.member_list_updated.connect(
            self.message_broadcast.update_member_list)
        
        # 发送初始广播
        self.network_discovery.send_discovery_broadcast()
    
    def on_refresh_members(self):
        """刷新成员列表"""
        self.member_refresh.refresh_members()
        self.update_status('正在刷新...')
    
    def on_send_message(self):
        """发送一对一消息"""
        content = self.entry_message.get().strip()
        if not content:
            return
        
        selection = self.listbox_members.curselection()
        if not selection:
            messagebox.showwarning('提示', '请先选择接收者！')
            return
        
        member_index = selection[0]
        members = self.member_manager.get_member_list()
        if member_index < len(members):
            receiver = members[member_index]
            
            if self.message_p2p.send_p2p_message(receiver, content):
                self.append_chat_message(f"我 → {receiver.username}", content, False)
                self.entry_message.delete(0, tk.END)
            else:
                self.update_status('发送失败')
    
    def on_broadcast_message(self):
        """发送广播消息"""
        content = self.entry_message.get().strip()
        if not content:
            return
        
        if self.message_broadcast.send_broadcast_message(content):
            self.append_chat_message("我（广播）", content, True)
            self.entry_message.delete(0, tk.END)
        else:
            self.update_status('广播失败')
    
    def on_send_file(self):
        """发送文件"""
        selection = self.listbox_members.curselection()
        if not selection:
            messagebox.showwarning('提示', '请先选择接收者！')
            return
        
        file_path = filedialog.askopenfilename(title='选择要发送的文件')
        if not file_path:
            return
        
        # 检查文件大小
        filesize = os.path.getsize(file_path)
        if filesize > MAX_FILE_SIZE:
            messagebox.showwarning(
                '文件过大',
                f'文件超过限制！\n最大: {format_file_size(MAX_FILE_SIZE)}\n当前: {format_file_size(filesize)}'
            )
            return
        
        member_index = selection[0]
        members = self.member_manager.get_member_list()
        if member_index < len(members):
            receiver = members[member_index]
            filename = os.path.basename(file_path)
            
            self.append_chat_message(
                "系统",
                f"正在发送文件 [{filename}] 到 {receiver.username}",
                False
            )
            
            self.file_transfer.send_file(file_path, receiver)
    
    def on_member_discovered(self, member: Member):
        """发现新成员"""
        self.member_manager.add_member(member)
    
    def on_message_received(self, message: ChatMessage):
        """接收消息"""
        sender_name = message.sender.username
        self.append_chat_message(sender_name, message.content, False)
    
    def on_broadcast_received(self, message: ChatMessage):
        """接收广播"""
        sender_name = message.sender.username
        self.append_chat_message(f"{sender_name}（广播）", message.content, True)
    
    def on_member_list_updated(self, members: list):
        """成员列表更新"""
        self.listbox_members.delete(0, tk.END)
        for member in members:
            self.listbox_members.insert(tk.END, f"{member.username} ({member.ip})")
        
        self.update_status(f'在线成员：{len(members)}人')
    
    def on_file_request(self, file_info: FileTransferInfo):
        """收到文件传输请求"""
        self.current_transfer_info = file_info
        
        result = messagebox.askyesno(
            '文件传输请求',
            f'用户 {file_info.sender.username} 请求发送文件：\n\n'
            f'文件名：{file_info.filename}\n'
            f'大小：{format_file_size(file_info.filesize)}\n\n'
            f'是否接受？'
        )
        
        if result:
            self.file_transfer.accept_file(file_info)
            self.append_chat_message(
                "系统",
                f"正在接收文件 [{file_info.filename}] 来自 {file_info.sender.username}",
                False
            )
        else:
            self.file_transfer.reject_file(file_info)
            self.append_chat_message("系统", f"已拒绝文件 [{file_info.filename}]", False)
    
    def on_transfer_progress(self, filename: str, percentage: int):
        """文件传输进度"""
        self.progress_frame.pack(fill=tk.X, pady=5)
        self.label_progress.config(text=f"传输中: {filename} - {percentage}%")
        self.progress_bar['value'] = percentage
        self.root.update()
    
    def on_transfer_completed(self, filename: str, success: bool):
        """文件传输完成"""
        self.progress_frame.pack_forget()
        
        if success:
            self.append_chat_message("系统", f"文件传输完成: {filename}", False)
            self.update_status(f'文件传输完成: {filename}')
        else:
            self.append_chat_message("系统", f"文件传输失败: {filename}", False)
            self.update_status(f'文件传输失败: {filename}')
    
    def append_chat_message(self, sender: str, content: str, is_broadcast: bool):
        """添加聊天消息"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        msg_type = "[广播]" if is_broadcast else "[消息]"
        message = f"[{timestamp}] {msg_type} {sender}: {content}\n"
        
        self.text_chat.config(state=tk.NORMAL)
        self.text_chat.insert(tk.END, message)
        self.text_chat.see(tk.END)
        self.text_chat.config(state=tk.DISABLED)
    
    def update_status(self, text: str):
        """更新状态栏"""
        self.status_label.config(text=text)
    
    def on_closing(self):
        """关闭窗口"""
        if messagebox.askokcancel("退出", "确定要退出吗？"):
            print("[系统] 正在退出...")
            if hasattr(self, 'member_manager'):
                self.member_manager.broadcast_leave()
            if hasattr(self, 'message_dispatcher'):
                self.message_dispatcher.stop()
            if hasattr(self, 'file_transfer'):
                self.file_transfer.stop()
            self.root.destroy()


def main():
    """主函数 - Tkinter版本"""
    # 创建root窗口（用于获取用户名）
    temp_root = tk.Tk()
    temp_root.withdraw()
    
    root = tk.Tk()
    app = MainWindow(root)
    root.mainloop()



