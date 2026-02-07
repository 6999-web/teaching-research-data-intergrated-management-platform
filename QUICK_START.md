# 快速开始指南

## 5分钟快速启动

### 前置条件
- Docker Desktop 已安装并运行
- Node.js 18+ 已安装
- Python 3.11+ 已安装

### 步骤 1: 克隆项目 (如果需要)
```bash
# 如果项目已在本地,跳过此步骤
git clone <repository-url>
cd teaching-office-evaluation-system
```

### 步骤 2: 启动依赖服务
```bash
docker-compose up -d
```

等待约 10 秒让服务完全启动。

### 步骤 3: 设置后端

**Windows:**
```bash
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
alembic upgrade head
uvicorn app.main:app --reload
```

**Linux/Mac:**
```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
alembic upgrade head
uvicorn app.main:app --reload
```

### 步骤 4: 设置前端 (新终端)
```bash
cd frontend
npm install
npm run dev
```

### 步骤 5: 访问应用

- **前端**: http://localhost:3000
- **后端 API 文档**: http://localhost:8000/docs
- **MinIO 控制台**: http://localhost:9001 (minioadmin/minioadmin)

## 自动化安装

### Windows
双击运行 `setup.bat`

### Linux/Mac
```bash
chmod +x setup.sh
./setup.sh
```

## 验证安装

### 检查后端
```bash
cd backend
python verify_setup.py
```

### 检查 Docker 服务
```bash
docker-compose ps
```

应该看到两个服务都在运行:
- `teaching_office_postgres`
- `teaching_office_minio`

### 运行测试
```bash
# 后端测试
cd backend
pytest

# 前端测试
cd frontend
npm run test
```

## 常用命令

### 启动所有服务
```bash
# 终端 1: Docker 服务
docker-compose up -d

# 终端 2: 后端
cd backend && source venv/bin/activate && uvicorn app.main:app --reload

# 终端 3: 前端
cd frontend && npm run dev
```

### 停止所有服务
```bash
# 停止前端和后端 (Ctrl+C)
# 停止 Docker
docker-compose down
```

### 查看日志
```bash
# Docker 服务日志
docker-compose logs -f

# 后端日志
# 在运行 uvicorn 的终端查看

# 前端日志
# 在运行 npm run dev 的终端查看
```

## 故障排除

### 端口被占用
如果端口 3000, 8000, 5432, 或 9000 被占用:
1. 停止占用端口的程序
2. 或修改配置文件中的端口号

### Docker 服务无法启动
```bash
docker-compose down
docker-compose up -d
```

### Python 依赖安装失败
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 数据库连接失败
确保 Docker 服务正在运行:
```bash
docker-compose ps
```

## 下一步

1. 查看 [README.md](README.md) 了解项目详情
2. 查看 [SETUP_GUIDE.md](SETUP_GUIDE.md) 了解详细配置
3. 查看 [PROJECT_STATUS.md](PROJECT_STATUS.md) 了解项目进度
4. 开始实现下一个任务: 数据库设计和初始化

## 获取帮助

- 查看 API 文档: http://localhost:8000/docs
- 查看项目规范: `.kiro/specs/teaching-office-evaluation-system/`
- 检查日志文件
