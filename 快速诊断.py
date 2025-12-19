"""
快速诊断工具 - 自动检测防火墙和网卡问题
"""

import subprocess
import socket
import re

def check_firewall():
    """检查防火墙状态"""
    print("\n" + "="*60)
    print("【1/4】检查防火墙状态")
    print("="*60)
    
    try:
        result = subprocess.run(
            ['netsh', 'advfirewall', 'show', 'allprofiles', 'state'],
            capture_output=True,
            text=True,
            encoding='gbk'
        )
        
        output = result.stdout
        
        if '启用' in output or 'ON' in output:
            print("⚠️  防火墙状态: 已启用")
            print("\n【可能原因】防火墙正在阻止UDP通信")
            print("\n【解决方案】")
            print("方案1 - 临时测试（推荐）：")
            print("  以管理员身份运行CMD，执行：")
            print("  netsh advfirewall set allprofiles state off")
            print("  测试完后记得开启：")
            print("  netsh advfirewall set allprofiles state on")
            print("\n方案2 - 添加规则（永久解决）：")
            print("  以管理员身份运行CMD，执行：")
            print("  netsh advfirewall firewall add rule name=\"聊天UDP\" dir=in action=allow protocol=UDP localport=8888")
            return False
        else:
            print("✓ 防火墙状态: 已关闭")
            return True
    except Exception as e:
        print(f"× 无法检查防火墙: {e}")
        return None

def get_all_interfaces():
    """获取所有网络接口"""
    print("\n" + "="*60)
    print("【2/4】检查网络接口")
    print("="*60)
    
    try:
        result = subprocess.run(['ipconfig', '/all'], capture_output=True, text=True, encoding='gbk')
        output = result.stdout
        
        # 解析网络适配器
        adapters = []
        current_adapter = None
        ipv4_address = None
        
        for line in output.split('\n'):
            line = line.strip()
            
            # 检测适配器名称
            if '适配器' in line and ':' in line:
                if current_adapter and ipv4_address:
                    adapters.append({
                        'name': current_adapter,
                        'ip': ipv4_address,
                        'is_virtual': is_virtual_adapter(current_adapter)
                    })
                current_adapter = line.split('适配器')[1].split(':')[0].strip()
                ipv4_address = None
            
            # 检测IPv4地址
            if 'IPv4' in line and '.' in line:
                match = re.search(r'(\d+\.\d+\.\d+\.\d+)', line)
                if match:
                    ipv4_address = match.group(1)
        
        # 添加最后一个适配器
        if current_adapter and ipv4_address:
            adapters.append({
                'name': current_adapter,
                'ip': ipv4_address,
                'is_virtual': is_virtual_adapter(current_adapter)
            })
        
        # 显示结果
        real_adapters = []
        virtual_adapters = []
        
        for adapter in adapters:
            if adapter['is_virtual']:
                virtual_adapters.append(adapter)
                print(f"⚠️  虚拟网卡: {adapter['name']}")
                print(f"    IP: {adapter['ip']}")
            else:
                real_adapters.append(adapter)
                print(f"✓ 物理网卡: {adapter['name']}")
                print(f"    IP: {adapter['ip']}")
        
        if virtual_adapters:
            print(f"\n⚠️  发现 {len(virtual_adapters)} 个虚拟网卡！")
            print("\n【可能原因】程序可能绑定到了虚拟网卡的IP")
            print("\n【解决方案】")
            print("方案1 - 临时禁用虚拟网卡：")
            print("  1. Win+R 输入 ncpa.cpl")
            print("  2. 右键虚拟网卡 → 禁用")
            print("  3. 重启聊天程序")
            print("\n方案2 - 关闭VPN/虚拟机：")
            print("  关闭所有VPN软件和虚拟机")
            
        if real_adapters:
            print(f"\n✓ 建议使用的IP地址：")
            for adapter in real_adapters:
                if adapter['ip'].startswith('192.168') or adapter['ip'].startswith('10.'):
                    print(f"  → {adapter['ip']} (推荐)")
                else:
                    print(f"    {adapter['ip']}")
        
        return len(virtual_adapters) == 0
        
    except Exception as e:
        print(f"× 无法检查网络接口: {e}")
        return None

def is_virtual_adapter(name):
    """判断是否是虚拟网卡"""
    virtual_keywords = [
        'VirtualBox', 'VMware', 'Hyper-V', 'Virtual',
        'TAP', 'Tunnel', 'VPN', 'Loopback',
        '虚拟', 'Npcap', 'WireGuard', 'OpenVPN'
    ]
    
    name_upper = name.upper()
    for keyword in virtual_keywords:
        if keyword.upper() in name_upper:
            return True
    return False

def check_port_usage():
    """检查端口占用"""
    print("\n" + "="*60)
    print("【3/4】检查端口占用")
    print("="*60)
    
    try:
        result = subprocess.run(
            ['netstat', '-ano'],
            capture_output=True,
            text=True,
            encoding='gbk'
        )
        
        output = result.stdout
        port_8888_used = False
        port_8889_used = False
        
        for line in output.split('\n'):
            if ':8888' in line and 'LISTENING' in line:
                port_8888_used = True
            if ':8889' in line and 'LISTENING' in line:
                port_8889_used = True
        
        if port_8888_used:
            print("⚠️  端口8888已被占用")
            print("   可能是另一个聊天程序实例正在运行")
        else:
            print("✓ 端口8888空闲")
        
        if port_8889_used:
            print("⚠️  端口8889已被占用")
        else:
            print("✓ 端口8889空闲")
        
        return not (port_8888_used or port_8889_used)
        
    except Exception as e:
        print(f"× 无法检查端口: {e}")
        return None

def get_recommended_ip():
    """获取推荐使用的IP"""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('8.8.8.8', 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except:
        return '127.0.0.1'

def provide_summary():
    """提供诊断总结"""
    print("\n" + "="*60)
    print("【4/4】诊断总结和建议")
    print("="*60)
    
    current_ip = get_recommended_ip()
    print(f"\n当前程序会使用的IP: {current_ip}")
    
    # 判断IP类型
    if current_ip.startswith('192.168') or current_ip.startswith('10.'):
        print("✓ IP类型: 正常局域网IP")
        ip_ok = True
    elif current_ip.startswith('172.'):
        octets = current_ip.split('.')
        if len(octets) >= 2 and 16 <= int(octets[1]) <= 31:
            print("✓ IP类型: 正常局域网IP")
            ip_ok = True
        else:
            print("⚠️  IP类型: 可能不是标准局域网IP")
            ip_ok = False
    elif current_ip.startswith('198.18'):
        print("⚠️  IP类型: VPN或虚拟网络IP")
        ip_ok = False
    elif current_ip == '127.0.0.1':
        print("× IP类型: 回环地址（无法与其他电脑通信）")
        ip_ok = False
    else:
        print("⚠️  IP类型: 特殊IP地址")
        ip_ok = False
    
    return ip_ok

def main():
    """主函数"""
    print("\n╔" + "="*58 + "╗")
    print("║" + " "*15 + "快速诊断工具" + " "*27 + "║")
    print("╚" + "="*58 + "╝")
    print("\n正在自动检测可能的问题...\n")
    
    # 执行检查
    firewall_ok = check_firewall()
    network_ok = get_all_interfaces()
    port_ok = check_port_usage()
    ip_ok = provide_summary()
    
    # 总结
    print("\n" + "="*60)
    print("【诊断结果】")
    print("="*60)
    
    issues = []
    
    if firewall_ok == False:
        issues.append("防火墙已启用，可能阻止通信")
    if network_ok == False:
        issues.append("发现虚拟网卡，可能导致IP错误")
    if port_ok == False:
        issues.append("端口被占用")
    if ip_ok == False:
        issues.append("当前IP不适合局域网通信")
    
    if issues:
        print("\n⚠️  发现以下问题：")
        for i, issue in enumerate(issues, 1):
            print(f"  {i}. {issue}")
        
        print("\n【推荐操作】按优先级执行：")
        print("1. 关闭所有VPN和虚拟机软件")
        print("2. 临时关闭防火墙测试")
        print("3. 如果可以通信，添加防火墙规则")
        print("4. 重新运行聊天程序")
    else:
        print("\n✓ 未发现明显问题！")
        print("\n如果仍无法通信，可能是：")
        print("1. 路由器开启了AP隔离")
        print("2. 两台电脑不在同一网段")
        print("3. 网络类型设置为公用网络")
    
    print("\n" + "="*60)
    print("详细排查步骤请查看：🔧故障排查步骤.txt")
    print("="*60)

if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        print(f"\n× 诊断过程出错: {e}")
    
    input("\n\n按回车键退出...")


