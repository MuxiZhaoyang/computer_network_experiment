"""
网络诊断工具
帮助诊断网络通信问题
"""

import socket
import json

def get_all_network_interfaces():
    """获取所有网络接口信息"""
    print("=" * 60)
    print("网络接口信息")
    print("=" * 60)
    
    hostname = socket.gethostname()
    print(f"主机名: {hostname}\n")
    
    try:
        # 获取所有地址
        addr_infos = socket.getaddrinfo(hostname, None)
        seen_ips = set()
        
        for addr_info in addr_infos:
            ip = addr_info[4][0]
            if ip not in seen_ips and ':' not in ip:  # 忽略IPv6
                seen_ips.add(ip)
                print(f"IP地址: {ip}")
                
                # 判断IP类型
                if ip.startswith('192.168.'):
                    print(f"  类型: 局域网IP (推荐用于聊天)")
                elif ip.startswith('10.'):
                    print(f"  类型: 局域网IP (推荐用于聊天)")
                elif ip.startswith('172.'):
                    octets = ip.split('.')
                    if len(octets) >= 2 and 16 <= int(octets[1]) <= 31:
                        print(f"  类型: 局域网IP (推荐用于聊天)")
                elif ip == '127.0.0.1':
                    print(f"  类型: 回环地址 (只能本机通信)")
                elif ip.startswith('198.18.'):
                    print(f"  类型: VPN或测试网络 (可能无法与其他电脑通信)")
                else:
                    print(f"  类型: 公网或特殊地址")
                print()
                
    except Exception as e:
        print(f"获取网络接口失败: {e}")

def test_udp_broadcast():
    """测试UDP广播功能"""
    print("=" * 60)
    print("UDP广播测试")
    print("=" * 60)
    
    port = 8888
    
    try:
        # 创建UDP socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.settimeout(2.0)
        
        # 绑定
        sock.bind(('0.0.0.0', port))
        print(f"✓ 成功绑定到端口 {port}")
        
        # 测试发送广播
        test_message = json.dumps({'test': 'broadcast'}).encode('utf-8')
        sock.sendto(test_message, ('255.255.255.255', port))
        print(f"✓ 成功发送广播消息")
        
        # 尝试接收
        try:
            data, addr = sock.recvfrom(4096)
            print(f"✓ 收到广播消息，来自 {addr}")
        except socket.timeout:
            print("! 2秒内未收到消息（可能是防火墙阻止）")
        
        sock.close()
        print("\n✓ UDP广播功能正常")
        
    except Exception as e:
        print(f"\n× UDP广播测试失败: {e}")

def check_firewall():
    """检查防火墙建议"""
    print("=" * 60)
    print("防火墙检查建议")
    print("=" * 60)
    
    print("""
如果无法发现其他用户，可能是防火墙阻止了UDP通信。

解决方法：

方法1：临时关闭防火墙（仅用于测试）
  1. 打开 Windows Defender 防火墙
  2. 点击"启用或关闭 Windows Defender 防火墙"
  3. 临时关闭私有网络和公用网络防火墙
  4. 测试程序
  5. 测试完成后重新开启防火墙

方法2：添加防火墙规则（推荐）
  1. 打开 Windows Defender 防火墙
  2. 点击"高级设置"
  3. 选择"入站规则" -> "新建规则"
  4. 规则类型：端口
  5. 协议：UDP，端口：8888
  6. 操作：允许连接
  7. 配置文件：全选
  8. 名称：简易聊天工具
  9. 同样为端口8889（TCP）创建规则

方法3：首次运行时允许访问
  首次运行程序时，Windows会弹出防火墙提示
  请点击"允许访问"
""")

def main():
    """主函数"""
    print("\n")
    print("╔" + "=" * 58 + "╗")
    print("║" + " " * 15 + "网络诊断工具" + " " * 27 + "║")
    print("╚" + "=" * 58 + "╝")
    print()
    
    # 1. 获取网络接口
    get_all_network_interfaces()
    
    # 2. 测试UDP广播
    test_udp_broadcast()
    
    # 3. 防火墙建议
    check_firewall()
    
    print("=" * 60)
    print("诊断完成")
    print("=" * 60)
    print()
    
    input("按回车键退出...")

if __name__ == '__main__':
    main()


