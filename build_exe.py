"""
打包脚本 - 使用PyInstaller
生成Windows可执行文件
"""

import os
import sys
import subprocess

def build_executable():
    """构建可执行文件"""
    print("=== 开始构建简易聊天工具 ===\n")
    
    # 检查PyInstaller
    try:
        import PyInstaller
        print("✓ PyInstaller已安装")
    except ImportError:
        print("× PyInstaller未安装，正在安装...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])
        print("✓ PyInstaller安装完成")
    
    # PyInstaller命令
    cmd = [
        "pyinstaller",
        "--name=简易聊天工具",
        "--onefile",              # 单文件
        "--windowed",             # 无控制台窗口
        "--icon=NONE",            # 图标（可选）
        "--add-data", "src;src",  # 包含源代码
        "run.py"
    ]
    
    print("\n正在打包...")
    print(f"命令: {' '.join(cmd)}\n")
    
    try:
        subprocess.check_call(cmd)
        print("\n✓ 打包成功！")
        print(f"可执行文件位置: dist\\简易聊天工具.exe")
    except subprocess.CalledProcessError as e:
        print(f"\n× 打包失败: {e}")
        return False
    
    return True

if __name__ == "__main__":
    success = build_executable()
    if success:
        print("\n=== 构建完成 ===")
        print("\n使用方法：")
        print("1. 运行 dist\\简易聊天工具.exe")
        print("2. 在多台电脑上运行测试互相发现")
        print("3. 享受聊天！")
    else:
        print("\n=== 构建失败 ===")
        print("请检查错误信息并重试")
    
    input("\n按回车键退出...")



