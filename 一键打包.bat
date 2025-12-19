@echo off
chcp 65001
echo ========================================
echo     简易聊天工具 - 一键打包
echo ========================================
echo.

echo 正在检查环境...
python --version
if errorlevel 1 (
    echo × Python未安装或未添加到PATH
    pause
    exit /b 1
)

echo.
echo 正在打包程序...
python build_exe.py

echo.
echo ========================================
echo 打包完成！
echo 可执行文件位置: dist\简易聊天工具.exe
echo ========================================
pause

