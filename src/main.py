"""
主程序入口
"""

import sys
import os
import traceback
import logging
from datetime import datetime
from PyQt5.QtWidgets import QApplication, QInputDialog, QMessageBox
from PyQt5.QtCore import qInstallMessageHandler, QtMsgType

from .common.config import *
from .common.message_types import *
from .common.utils import *
from .ui.main_window import MainWindow


# 设置日志
def setup_logging():
    """设置日志系统"""
    # 日志文件路径
    if getattr(sys, 'frozen', False):
        # 打包后的exe
        log_dir = os.path.dirname(sys.executable)
    else:
        # 开发环境
        log_dir = os.path.dirname(os.path.abspath(__file__))
    
    log_file = os.path.join(log_dir, f'crash_log_{datetime.now().strftime("%Y%m%d_%H%M%S")}.txt')
    
    # 配置日志
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s [%(levelname)s] %(message)s',
        handlers=[
            logging.FileHandler(log_file, encoding='utf-8'),
            logging.StreamHandler(sys.stdout)
        ]
    )
    
    logging.info("="*60)
    logging.info("程序启动")
    logging.info(f"日志文件: {log_file}")
    logging.info(f"Python版本: {sys.version}")
    logging.info("="*60)
    
    return log_file


def qt_message_handler(mode, context, message):
    """Qt消息处理器"""
    if mode == QtMsgType.QtDebugMsg:
        logging.debug(f"Qt: {message}")
    elif mode == QtMsgType.QtWarningMsg:
        logging.warning(f"Qt: {message}")
    elif mode == QtMsgType.QtCriticalMsg:
        logging.error(f"Qt: {message}")
    elif mode == QtMsgType.QtFatalMsg:
        logging.critical(f"Qt: {message}")


def exception_hook(exc_type, exc_value, exc_traceback):
    """全局异常处理"""
    if issubclass(exc_type, KeyboardInterrupt):
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return
    
    logging.critical("发生未处理的异常！")
    logging.critical(f"异常类型: {exc_type.__name__}")
    logging.critical(f"异常信息: {exc_value}")
    logging.critical("异常堆栈:")
    for line in traceback.format_tb(exc_traceback):
        logging.critical(line.rstrip())
    
    # 也输出到控制台
    sys.__excepthook__(exc_type, exc_value, exc_traceback)


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
    try:
        # 设置日志
        log_file = setup_logging()
        
        # 安装全局异常处理
        sys.excepthook = exception_hook
        
        # 创建应用程序
        app = QApplication(sys.argv)
        
        # 安装Qt消息处理器
        qInstallMessageHandler(qt_message_handler)
        
        # 设置应用程序信息
        app.setApplicationName(WINDOW_TITLE)
        app.setOrganizationName("ChatGroup")
        
        logging.info("创建主窗口...")
        # 创建主窗口
        window = MainWindow()
        window.show()
        
        logging.info("主窗口已显示，进入事件循环")
        # 运行应用程序
        result = app.exec()
        
        logging.info(f"程序退出，返回码: {result}")
        sys.exit(result)
        
    except Exception as e:
        logging.critical("程序启动失败！")
        logging.critical(f"错误: {e}")
        logging.critical(traceback.format_exc())
        
        # 显示错误对话框
        try:
            QMessageBox.critical(
                None,
                "程序错误",
                f"程序启动失败！\n\n错误信息:\n{e}\n\n详细日志已保存到:\n{log_file}"
            )
        except:
            pass
        
        sys.exit(1)


if __name__ == '__main__':
    main()

