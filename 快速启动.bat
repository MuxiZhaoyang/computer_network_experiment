@echo off
chcp 65001
echo ========================================
echo     简易聊天工具 - 快速启动
echo ========================================
echo.

echo 正在启动程序...
python run.py

if errorlevel 1 (
    echo.
    echo 启动失败！请检查：
    echo 1. 是否已安装Python 3.8+
    echo 2. 是否已安装依赖：pip install -r requirements.txt
    echo.
    pause
)



