@echo off
chcp 65001 >nul
echo.
echo ╔════════════════════════════════════════════════════════════╗
echo ║          教研室数据管理平台 - 403错误一键修复             ║
echo ╚════════════════════════════════════════════════════════════╝
echo.

REM 检查管理员权限
net session >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ 请以管理员身份运行此脚本
    echo.
    echo 右键点击此文件，选择"以管理员身份运行"
    echo.
    pause
    exit /b 1
)

echo ✅ 管理员权限确认
echo.

REM 步骤1：检查MySQL服务
echo ════════════════════════════════════════════════════════════
echo 步骤 1/5: 检查MySQL服务
echo ════════════════════════════════════════════════════════════
sc query MySQL80 | find "RUNNING" >nul
if %errorlevel% equ 0 (
    echo ✅ MySQL服务正在运行
) else (
    echo ⚠️  MySQL服务未运行，正在启动...
    net start MySQL80
    if %errorlevel% neq 0 (
        echo ❌ 启动MySQL服务失败
        echo.
        echo 请检查：
        echo 1. MySQL是否已安装
        echo 2. 服务名称是否为 MySQL80
        echo.
        pause
        exit /b 1
    )
    echo ✅ MySQL服务已启动
)
echo.

REM 步骤2：测试并修复MySQL密码
echo ════════════════════════════════════════════════════════════
echo 步骤 2/5: 测试并修复MySQL密码
echo ════════════════════════════════════════════════════════════

REM 测试密码 'root'
mysql -u root -proot -e "SELECT 1;" >nul 2>&1
if %errorlevel% equ 0 (
    echo ✅ MySQL密码已经是 'root'
    goto :password_ok
)

REM 测试空密码
echo 正在测试空密码...
mysql -u root -e "SELECT 1;" >nul 2>&1
if %errorlevel% equ 0 (
    echo ✅ MySQL使用空密码，正在设置为 'root'...
    mysql -u root -e "ALTER USER 'root'@'localhost' IDENTIFIED BY 'root'; FLUSH PRIVILEGES;" >nul 2>&1
    if %errorlevel% equ 0 (
        echo ✅ 密码已设置为 'root'
        goto :password_ok
    )
)

REM 测试密码 '123456'
echo 正在测试密码 '123456'...
mysql -u root -p123456 -e "SELECT 1;" >nul 2>&1
if %errorlevel% equ 0 (
    echo ✅ 找到密码 '123456'，正在修改为 'root'...
    mysql -u root -p123456 -e "ALTER USER 'root'@'localhost' IDENTIFIED BY 'root'; FLUSH PRIVILEGES;" >nul 2>&1
    if %errorlevel% equ 0 (
        echo ✅ 密码已修改为 'root'
        goto :password_ok
    )
)

REM 需要手动输入密码
echo.
echo ⚠️  无法自动确定MySQL密码
echo.
echo 请手动输入MySQL root用户的当前密码：
mysql -u root -p -e "ALTER USER 'root'@'localhost' IDENTIFIED BY 'root'; FLUSH PRIVILEGES;"
if %errorlevel% equ 0 (
    echo ✅ 密码已修改为 'root'
    goto :password_ok
) else (
    echo ❌ 密码修改失败
    echo.
    echo 请查看 "完整问题诊断和修复.md" 获取详细解决方案
    pause
    exit /b 1
)

:password_ok
echo.

REM 步骤3：检查数据库
echo ════════════════════════════════════════════════════════════
echo 步骤 3/5: 检查数据库
echo ════════════════════════════════════════════════════════════
mysql -u root -proot -e "SHOW DATABASES LIKE 'teaching_office_evaluation';" | find "teaching_office_evaluation" >nul
if %errorlevel% equ 0 (
    echo ✅ 数据库 teaching_office_evaluation 存在
) else (
    echo ⚠️  数据库不存在，正在创建...
    mysql -u root -proot -e "CREATE DATABASE teaching_office_evaluation CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"
    if %errorlevel% equ 0 (
        echo ✅ 数据库已创建
    ) else (
        echo ❌ 数据库创建失败
        pause
        exit /b 1
    )
)
echo.

REM 步骤4：测试后端连接
echo ════════════════════════════════════════════════════════════
echo 步骤 4/5: 测试后端连接
echo ════════════════════════════════════════════════════════════
python test_backend_connection.py >nul 2>&1
if %errorlevel% equ 0 (
    echo ✅ 后端连接测试通过
) else (
    echo ⚠️  后端连接测试失败，但可以继续
    echo    （后端服务可能需要重启）
)
echo.

REM 步骤5：提示重启后端
echo ════════════════════════════════════════════════════════════
echo 步骤 5/5: 重启后端服务
echo ════════════════════════════════════════════════════════════
echo.
echo ⚠️  请手动重启后端服务：
echo.
echo 1. 找到运行后端的命令行窗口
echo 2. 按 Ctrl+C 停止服务
echo 3. 重新运行：
echo    cd backend
echo    python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
echo.

REM 完成
echo.
echo ╔════════════════════════════════════════════════════════════╗
echo ║                    ✅ 修复完成                             ║
echo ╚════════════════════════════════════════════════════════════╝
echo.
echo 下一步操作：
echo.
echo 1. ✅ MySQL密码已配置为 'root'
echo 2. ✅ 数据库已准备就绪
echo 3. ⚠️  请重启后端服务（见上方说明）
echo 4. 🌐 刷新浏览器页面
echo 5. 🔐 重新登录系统
echo.
echo 如果还有问题，请查看：
echo - 完整问题诊断和修复.md
echo - 快速修复403错误.md
echo.
pause
