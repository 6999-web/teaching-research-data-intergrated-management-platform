@echo off
echo ========================================
echo MySQL连接问题修复脚本
echo ========================================
echo.

echo [步骤 1/4] 检查MySQL服务状态...
sc query MySQL80 | find "RUNNING" >nul
if %errorlevel% equ 0 (
    echo ✅ MySQL服务正在运行
) else (
    echo ❌ MySQL服务未运行，正在启动...
    net start MySQL80
    if %errorlevel% neq 0 (
        echo ❌ 启动MySQL服务失败，请以管理员身份运行此脚本
        pause
        exit /b 1
    )
    echo ✅ MySQL服务已启动
)

echo.
echo [步骤 2/4] 测试MySQL连接...
echo 请输入MySQL root用户的当前密码（如果不知道，请按Ctrl+C退出，查看文档）
mysql -u root -p -e "SELECT 1;" >nul 2>&1
if %errorlevel% equ 0 (
    echo ✅ MySQL连接成功
    echo.
    echo 现在将修改密码为 'root'
    echo 请再次输入当前密码：
    mysql -u root -p -e "ALTER USER 'root'@'localhost' IDENTIFIED BY 'root'; FLUSH PRIVILEGES;"
    if %errorlevel% equ 0 (
        echo ✅ 密码已修改为 'root'
    ) else (
        echo ❌ 密码修改失败
        pause
        exit /b 1
    )
) else (
    echo ❌ MySQL连接失败
    echo.
    echo 可能的原因：
    echo 1. 密码不正确
    echo 2. root用户被锁定
    echo 3. MySQL配置问题
    echo.
    echo 请查看 "诊断和修复403错误.md" 文档获取详细解决方案
    pause
    exit /b 1
)

echo.
echo [步骤 3/4] 验证新密码...
mysql -u root -proot -e "SELECT 1;" >nul 2>&1
if %errorlevel% equ 0 (
    echo ✅ 新密码验证成功
) else (
    echo ❌ 新密码验证失败
    pause
    exit /b 1
)

echo.
echo [步骤 4/4] 检查数据库...
mysql -u root -proot -e "SHOW DATABASES LIKE 'teaching_office_evaluation';" >nul 2>&1
if %errorlevel% equ 0 (
    echo ✅ 数据库 teaching_office_evaluation 存在
) else (
    echo ⚠️  数据库 teaching_office_evaluation 不存在
    echo 正在创建数据库...
    mysql -u root -proot -e "CREATE DATABASE IF NOT EXISTS teaching_office_evaluation CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"
    if %errorlevel% equ 0 (
        echo ✅ 数据库已创建
    ) else (
        echo ❌ 数据库创建失败
    )
)

echo.
echo ========================================
echo ✅ MySQL连接问题已修复！
echo ========================================
echo.
echo 下一步：
echo 1. 重启后端服务（在后端服务窗口按 Ctrl+C，然后重新运行）
echo 2. 刷新浏览器页面
echo 3. 重新登录测试
echo.
echo 按任意键关闭此窗口...
pause >nul
