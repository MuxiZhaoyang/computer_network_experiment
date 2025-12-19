@echo off
echo ========================================
echo   临时关闭防火墙（仅用于测试）
echo ========================================
echo.
echo 警告：此操作会临时关闭Windows防火墙
echo 仅用于测试网络通信
echo 测试完成后请运行"重新开启防火墙.bat"
echo.
pause
echo.
echo 正在关闭防火墙...
netsh advfirewall set allprofiles state off
echo.
if %errorlevel% == 0 (
    echo ✓ 防火墙已关闭
    echo.
    echo 现在请测试聊天程序是否能通信
    echo 测试完成后务必运行"重新开启防火墙.bat"
) else (
    echo × 关闭失败，请以管理员身份运行此脚本
)
echo.
pause


