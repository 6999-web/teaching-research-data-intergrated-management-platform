@echo off
echo ========================================
echo 测试MySQL密码
echo ========================================
echo.

echo 正在测试密码 'root'...
mysql -u root -proot -e "SELECT 1;" 2>nul
if %errorlevel% equ 0 (
    echo ✅ 密码 'root' 正确
    goto :success
)

echo ❌ 密码 'root' 不正确
echo.
echo 正在测试空密码...
mysql -u root -e "SELECT 1;" 2>nul
if %errorlevel% equ 0 (
    echo ✅ MySQL使用空密码
    echo.
    echo 正在设置密码为 'root'...
    mysql -u root -e "ALTER USER 'root'@'localhost' IDENTIFIED BY 'root'; FLUSH PRIVILEGES;"
    if %errorlevel% equ 0 (
        echo ✅ 密码已设置为 'root'
        goto :success
    ) else (
        echo ❌ 设置密码失败
        goto :fail
    )
)

echo ❌ 空密码也不正确
echo.
echo 正在测试密码 '123456'...
mysql -u root -p123456 -e "SELECT 1;" 2>nul
if %errorlevel% equ 0 (
    echo ✅ 密码是 '123456'
    echo.
    echo 正在修改密码为 'root'...
    mysql -u root -p123456 -e "ALTER USER 'root'@'localhost' IDENTIFIED BY 'root'; FLUSH PRIVILEGES;"
    if %errorlevel% equ 0 (
        echo ✅ 密码已修改为 'root'
        goto :success
    ) else (
        echo ❌ 修改密码失败
        goto :fail
    )
)

echo.
echo ========================================
echo ❌ 无法确定MySQL密码
echo ========================================
echo.
echo 请手动输入MySQL密码测试：
echo.
mysql -u root -p -e "SELECT 1;"
if %errorlevel% equ 0 (
    echo.
    echo ✅ 连接成功！
    echo.
    echo 现在请手动修改密码为 'root'：
    echo.
    mysql -u root -p -e "ALTER USER 'root'@'localhost' IDENTIFIED BY 'root'; FLUSH PRIVILEGES;"
    if %errorlevel% equ 0 (
        echo ✅ 密码已修改为 'root'
        goto :success
    )
)
goto :fail

:success
echo.
echo ========================================
echo ✅ MySQL密码配置成功
echo ========================================
echo.
echo 下一步：
echo 1. 重启后端服务
echo 2. 刷新浏览器页面
echo 3. 重新登录
echo.
pause
exit /b 0

:fail
echo.
echo ========================================
echo ❌ MySQL密码配置失败
echo ========================================
echo.
echo 请查看 "快速修复403错误.md" 获取详细解决方案
echo.
pause
exit /b 1
