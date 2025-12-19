@echo off
chcp 65001
cls
echo ========================================
echo   简易聊天工具 - 智能启动
echo ========================================
echo.

echo 正在检测Python环境...
python --version >nul 2>&1
if errorlevel 1 (
    echo × Python未安装！
    echo 请先安装Python 3.8或更高版本
    pause
    exit /b 1
)
echo ✓ Python已安装

echo.
echo 正在检测PyQt6...
python -c "from PyQt6 import QtWidgets" >nul 2>&1
if errorlevel 1 (
    echo × PyQt6不可用，使用Tkinter版本
    echo.
    echo 启动Tkinter版本（Python自带GUI）...
    python run_tkinter.py
) else (
    echo ✓ PyQt6可用
    echo.
    echo 启动PyQt6版本...
    python run.py
)

if errorlevel 1 (
    echo.
    echo 启动失败！
    echo 请查看错误信息
    pause
)

