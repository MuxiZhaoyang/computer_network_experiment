"""
使用Tkinter版本启动（Python自带GUI，无需额外安装）
如果PyQt6有问题，使用此版本
"""

import sys
import os

# 将src目录添加到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

import tkinter as tk
from src.ui.main_window_tkinter import main

if __name__ == '__main__':
    main()



