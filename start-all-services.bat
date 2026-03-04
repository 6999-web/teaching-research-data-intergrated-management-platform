@echo off
echo ========================================
echo 启动教研室工作考评系统
echo ========================================
echo.

REM 设置环境变量使用SQLite
set USE_SQLITE=true

echo [1/3] 检查Python虚拟环境...
if not exist "backend\venv" (
    echo 创建Python虚拟环境...
    cd backend
    python -m venv venv
    cd ..
)

echo.
echo [2/3] 启动后端服务 (端口 8000)...
start "后端服务" cmd /k "cd backend && venv\Scripts\activate && set USE_SQLITE=true && python -m uvicorn app.main:app --reload --port 8000"

timeout /t 5 /nobreak > nul

echo.
echo [3/3] 启动前端服务 (端口 3000)...
start "前端服务" cmd /k "cd frontend && npm run dev"

echo.
echo ========================================
echo 所有服务启动完成！
echo ========================================
echo.
echo 前端地址: http://localhost:3000
echo 后端API文档: http://localhost:8000/docs
echo.
echo 按任意键关闭此窗口...
pause > nul
