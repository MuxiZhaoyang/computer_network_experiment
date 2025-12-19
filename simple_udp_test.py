"""
简单UDP通信测试 - 两台电脑互测
不依赖广播，直接点对点测试
"""

import socket
import sys
import json
import time
import threading

def get_local_ip():
    """获取本机IP"""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('8.8.8.8', 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except:
        return '127.0.0.1'

def server_mode(port=8888):
    """服务器模式 - 接收消息"""
    print(f"\n=== 服务器模式 ===")
    print(f"本机IP: {get_local_ip()}")
    print(f"监听端口: {port}")
    print(f"等待接收消息...\n")
    
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind(('0.0.0.0', port))
    sock.settimeout(1.0)
    
    received_count = 0
    
    try:
        while True:
            try:
                data, addr = sock.recvfrom(4096)
                received_count += 1
                message = data.decode('utf-8')
                print(f"✓ [{time.strftime('%H:%M:%S')}] 收到第{received_count}条消息")
                print(f"  来自: {addr[0]}:{addr[1]}")
                print(f"  内容: {message}")
                print()
            except socket.timeout:
                continue
            except KeyboardInterrupt:
                break
    except KeyboardInterrupt:
        pass
    finally:
        sock.close()
        print(f"\n总共收到 {received_count} 条消息")

def client_mode(target_ip, port=8888):
    """客户端模式 - 发送消息"""
    print(f"\n=== 客户端模式 ===")
    print(f"本机IP: {get_local_ip()}")
    print(f"目标IP: {target_ip}")
    print(f"目标端口: {port}")
    print(f"开始发送测试消息...\n")
    
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    
    for i in range(1, 6):
        try:
            message = f"测试消息 #{i} from {get_local_ip()}"
            sock.sendto(message.encode('utf-8'), (target_ip, port))
            print(f"✓ [{time.strftime('%H:%M:%S')}] 已发送第{i}条消息: {message}")
            time.sleep(1)
        except Exception as e:
            print(f"× 发送失败: {e}")
    
    sock.close()
    print(f"\n发送完成！")

def interactive_test():
    """交互式测试"""
    print("\n" + "="*60)
    print("         UDP通信测试工具 - 双机互测版")
    print("="*60)
    print(f"\n【本机信息】")
    print(f"IP地址: {get_local_ip()}")
    print(f"测试端口: 8888")
    
    print("\n【测试说明】")
    print("需要两台电脑配合测试：")
    print("- 电脑A运行此程序，选择模式1（接收）")
    print("- 电脑B运行此程序，选择模式2（发送），输入电脑A的IP")
    print("- 查看电脑A是否收到消息")
    print("- 如果收到，说明网络正常，问题在程序")
    print("- 如果没收到，说明是防火墙或网络问题")
    
    print("\n" + "="*60)
    print("请选择模式：")
    print("1. 接收模式（在电脑A上运行）")
    print("2. 发送模式（在电脑B上运行）")
    print("="*60)
    
    choice = input("\n请输入选择 (1 或 2): ").strip()
    
    if choice == '1':
        print("\n准备接收...")
        print("请在另一台电脑上运行此程序，选择模式2，并输入此IP:")
        print(f">>> {get_local_ip()} <<<")
        input("\n按回车开始接收...")
        server_mode()
    elif choice == '2':
        target_ip = input("\n请输入对方电脑的IP地址: ").strip()
        if not target_ip:
            print("× 未输入IP地址")
            return
        print(f"\n准备向 {target_ip} 发送测试消息...")
        input("按回车开始发送...")
        client_mode(target_ip)
    else:
        print("× 无效的选择")

if __name__ == '__main__':
    try:
        interactive_test()
    except KeyboardInterrupt:
        print("\n\n程序已退出")
    except Exception as e:
        print(f"\n× 错误: {e}")
    
    input("\n按回车键退出...")


