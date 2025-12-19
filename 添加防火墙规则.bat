@echo off
echo ========================================
echo   添加防火墙规则（永久解决）
echo ========================================
echo.
echo 正在添加聊天工具的防火墙规则...
echo.

netsh advfirewall firewall add rule name="聊天工具UDP入站" dir=in action=allow protocol=UDP localport=8888
netsh advfirewall firewall add rule name="聊天工具TCP入站" dir=in action=allow protocol=TCP localport=8889
netsh advfirewall firewall add rule name="聊天工具UDP出站" dir=out action=allow protocol=UDP localport=8888
netsh advfirewall firewall add rule name="聊天工具TCP出站" dir=out action=allow protocol=TCP localport=8889

echo.
if %errorlevel% == 0 (
    echo ✓ 防火墙规则添加成功！
    echo.
    echo 已添加以下规则：
    echo - UDP 8888 入站/出站
    echo - TCP 8889 入站/出站
    echo.
    echo 现在可以正常使用聊天程序了！
) else (
    echo × 添加失败，请以管理员身份运行此脚本
    echo.
    echo 方法：右键点击此文件 → 以管理员身份运行
)
echo.
pause

