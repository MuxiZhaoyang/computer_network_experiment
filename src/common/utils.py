"""
工具函数模块
提供通用的工具函数
"""

import json
import socket
import struct
from typing import Optional


def get_local_ip() -> str:
    """
    获取本机IP地址
    
    Returns:
        str: 本机IP地址
    """
    try:
        # 创建一个UDP socket
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        # 连接到外部地址（不会真正发送数据）
        s.connect(('8.8.8.8', 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return '127.0.0.1'


def serialize_message(message_dict: dict) -> bytes:
    """
    序列化消息为字节流
    
    Args:
        message_dict: 消息字典
        
    Returns:
        bytes: 序列化后的字节流
    """
    json_str = json.dumps(message_dict, ensure_ascii=False)
    return json_str.encode('utf-8')


def deserialize_message(data: bytes) -> Optional[dict]:
    """
    反序列化字节流为消息字典
    
    Args:
        data: 字节流数据
        
    Returns:
        dict: 消息字典，失败返回None
    """
    try:
        json_str = data.decode('utf-8')
        return json.loads(json_str)
    except Exception as e:
        print(f"反序列化消息失败: {e}")
        return None


def format_file_size(size: int) -> str:
    """
    格式化文件大小显示
    
    Args:
        size: 文件大小（字节）
        
    Returns:
        str: 格式化后的文件大小
    """
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size < 1024.0:
            return f"{size:.2f} {unit}"
        size /= 1024.0
    return f"{size:.2f} TB"


def validate_ip(ip: str) -> bool:
    """
    验证IP地址格式
    
    Args:
        ip: IP地址字符串
        
    Returns:
        bool: 是否有效
    """
    try:
        socket.inet_aton(ip)
        return True
    except socket.error:
        return False


def validate_port(port: int) -> bool:
    """
    验证端口号
    
    Args:
        port: 端口号
        
    Returns:
        bool: 是否有效
    """
    return 1024 <= port <= 65535

