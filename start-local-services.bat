@echo off
echo ========================================
echo 启动本地服务
echo ========================================

echo.
echo [1/3] 检查MySQL服务...
mysql -u root -proot -e "SELECT 1;" >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ MySQL未运行，请先启动MySQL服务
    pause
    exit /b 1
)
echo ✅ MySQL服务正常

echo.
echo [2/3] 启动后端服务 (端口8000)...
cd backend
start "后端服务" cmd /k "python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000"
cd ..

echo.
echo 等待后端服务启动...
timeout /t 5 /nobreak >nul

echo.
echo [3/3] 启动前端服务 (端口3000)...
cd frontend
start "前端服务" cmd /k "npm run dev"
cd ..

echo.
echo ========================================
echo ✅ 所有服务已启动！
echo ========================================
echo.
echo 后端服务: http://localhost:8000
echo 前端服务: http://localhost:3000
echo API文档: http://localhost:8000/api/docs
echo.
echo 按任意键关闭此窗口...
pause >nul
