@echo off
echo ========================================
echo   重新开启防火墙
echo ========================================
echo.
echo 正在开启防火墙...
netsh advfirewall set allprofiles state on
echo.
if %errorlevel% == 0 (
    echo ✓ 防火墙已重新开启
) else (
    echo × 开启失败，请以管理员身份运行此脚本
)
echo.
pause


