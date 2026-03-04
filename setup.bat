@echo off
echo ==========================================
echo 教研室工作考评系统 - 项目初始化
echo ==========================================

REM Check if Docker is installed
docker --version >nul 2>&1
if errorlevel 1 (
    echo 警告: Docker 未安装。请先安装 Docker。
    exit /b 1
)

REM Start Docker services
echo.
echo 1. 启动 Docker 服务 (PostgreSQL + MinIO)...
docker-compose up -d

REM Wait for services to be ready
echo 等待服务启动...
timeout /t 10 /nobreak >nul

REM Backend setup
echo.
echo 2. 设置后端...
cd backend

REM Create virtual environment if it doesn't exist
if not exist "venv" (
    echo 创建 Python 虚拟环境...
    python -m venv venv
)

REM Activate virtual environment
echo 激活虚拟环境...
call venv\Scripts\activate.bat

REM Install dependencies
echo 安装 Python 依赖...
pip install -r requirements.txt

REM Create .env file if it doesn't exist
if not exist ".env" (
    echo 创建 .env 文件...
    copy .env.example .env
)

REM Run database migrations
echo 运行数据库迁移...
alembic upgrade head

cd ..

REM Frontend setup
echo.
echo 3. 设置前端...
cd frontend

REM Install dependencies
echo 安装 Node.js 依赖...
call npm install

cd ..

echo.
echo ==========================================
echo 初始化完成!
echo ==========================================
echo.
echo 启动服务:
echo   后端: cd backend ^&^& venv\Scripts\activate ^&^& uvicorn app.main:app --reload
echo   前端: cd frontend ^&^& npm run dev
echo.
echo 访问地址:
echo   前端: http://localhost:3000
echo   后端API: http://localhost:8000
echo   API文档: http://localhost:8000/docs
echo   MinIO控制台: http://localhost:9001 (minioadmin/minioadmin)
echo.
pause
