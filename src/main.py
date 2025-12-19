"""
主程序入口
"""

import sys
from PyQt5.QtWidgets import QApplication, QInputDialog, QMessageBox

from .common.config import *
from .common.message_types import *
from .common.utils import *
from .ui.main_window import MainWindow


def get_username() -> str:
    """
    获取用户名
    
    Returns:
        str: 用户名
    """
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    
    username, ok = QInputDialog.getText(
        None,
        '设置用户名',
        '请输入您的用户名：',
        text=f'User_{get_local_ip().split(".")[-1]}'
    )
    
    if ok and username:
        return username
    else:
        QMessageBox.warning(None, '警告', '必须设置用户名才能使用！')
        sys.exit(0)


def main():
    """
    主函数
    """
    # 创建应用程序
    app = QApplication(sys.argv)
    
    # 设置应用程序信息
    app.setApplicationName(WINDOW_TITLE)
    app.setOrganizationName("ChatGroup")
    
    # 创建主窗口
    window = MainWindow()
    window.show()
    
    # 运行应用程序
    sys.exit(app.exec())


if __name__ == '__main__':
    main()

