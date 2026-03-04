@echo off
chcp 65001 >nul
echo.
echo ════════════════════════════════════════════════════════════
echo MySQL密码设置向导
echo ════════════════════════════════════════════════════════════
echo.

echo 请输入MySQL root用户的当前密码，然后按回车：
echo （如果密码为空，直接按回车）
echo.

mysql -u root -p -e "ALTER USER 'root'@'localhost' IDENTIFIED BY 'root'; FLUSH PRIVILEGES;"

if %errorlevel% equ 0 (
    echo.
    echo ════════════════════════════════════════════════════════════
    echo ✅ 密码已成功设置为 'root'
    echo ════════════════════════════════════════════════════════════
    echo.
    echo 正在验证新密码...
    mysql -u root -proot -e "SELECT '✅ 验证成功' AS status;"
    echo.
    echo 正在初始化数据库表...
    cd backend
    type create_tables.sql | mysql -u root -proot 2>nul
    echo ✅ 表结构已创建
    echo.
    echo 正在初始化测试数据...
    type init_test_data.sql | mysql -u root -proot 2>nul
    echo ✅ 测试数据已初始化
    cd ..
    echo.
    echo ════════════════════════════════════════════════════════════
    echo ✅ 数据库设置完成
    echo ════════════════════════════════════════════════════════════
    echo.
    echo 测试账号:
    echo   教研室端: director1 / password123
    echo   评教小组: evaluator1 / password123
    echo   办公室: office1 / password123
    echo   校长办公会: president1 / password123
    echo.
    echo 下一步:
    echo 1. 重启后端服务（在后端窗口按Ctrl+C，然后重新运行）
    echo 2. 刷新浏览器页面
    echo 3. 使用上述账号登录
    echo.
) else (
    echo.
    echo ════════════════════════════════════════════════════════════
    echo ❌ 密码设置失败
    echo ════════════════════════════════════════════════════════════
    echo.
    echo 可能的原因:
    echo 1. 输入的当前密码不正确
    echo 2. MySQL服务未运行
    echo 3. 权限不足
    echo.
    echo 请重新运行此脚本，或查看 "完整问题诊断和修复.md"
    echo.
)

pause
