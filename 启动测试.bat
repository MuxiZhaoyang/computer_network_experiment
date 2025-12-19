@echo off
chcp 65001
echo ========================================
echo     测试程序运行
echo ========================================
echo.
echo 正在启动第一个实例...
start "聊天工具-User1" cmd /k "python run.py"
timeout /t 2
echo 正在启动第二个实例...
start "聊天工具-User2" cmd /k "python run.py"
timeout /t 2
echo 正在启动第三个实例...
start "聊天工具-User3" cmd /k "python run.py"
echo.
echo ========================================
echo 已启动3个实例用于测试！
echo 请在每个窗口输入不同的用户名
echo ========================================
pause


