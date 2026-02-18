@echo off
chcp 65001 >nul
echo ========================================
echo 教研室数据管理平台 - 服务重启脚本
echo ========================================
echo.

echo [1/5] 停止所有Python进程...
taskkill /F /IM python.exe >nul 2>&1
if %errorlevel% == 0 (
    echo ✓ Python进程已停止
) else (
    echo ℹ 没有运行中的Python进程
)

echo.
echo [2/5] 停止所有Node进程...
taskkill /F /IM node.exe >nul 2>&1
if %errorlevel% == 0 (
    echo ✓ Node进程已停止
) else (
    echo ℹ 没有运行中的Node进程
)

echo.
echo [3/5] 等待3秒...
timeout /t 3 /nobreak >nul

echo.
echo [4/5] 启动后端服务...
start "后端服务 - 教研室数据管理平台" cmd /k "cd /d %~dp0backend && python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000"
echo ✓ 后端服务已启动（端口8000）

echo.
echo [5/5] 等待5秒让后端完全启动...
timeout /t 5 /nobreak >nul

echo.
echo [6/6] 启动前端服务...
start "前端服务 - 教研室数据管理平台" cmd /k "cd /d %~dp0frontend && npm run dev"
echo ✓ 前端服务已启动（端口3000）

echo.
echo ========================================
echo ✓ 所有服务已成功重启！
echo ========================================
echo.
echo 访问地址：
echo   前端: http://localhost:3000
echo   后端: http://localhost:8000
echo   API文档: http://localhost:8000/docs
echo.
echo 测试账号：
echo   教研室端: director1 / password123
echo   管理端: admin / 123
echo.
echo 按任意键关闭此窗口...
pause >nul
