# 项目初始化指南

本指南将帮助您完成教研室工作考评系统的初始化和配置。

## 系统要求

### 必需软件
- **Node.js**: 18.0 或更高版本
- **Python**: 3.11 或更高版本
- **Docker**: 最新版本 (用于运行 PostgreSQL 和 MinIO)
- **Git**: 用于版本控制

### 可选软件
- **PostgreSQL**: 15+ (如果不使用 Docker)
- **MinIO**: 最新版本 (如果不使用 Docker)

## 快速开始

### 方式一: 使用自动化脚本 (推荐)

#### Windows
```bash
setup.bat
```

#### Linux/Mac
```bash
chmod +x setup.sh
./setup.sh
```

### 方式二: 手动设置

#### 1. 启动依赖服务

使用 Docker Compose 启动 PostgreSQL 和 MinIO:

```bash
docker-compose up -d
```

验证服务状态:
```bash
docker-compose ps
```

#### 2. 后端设置

进入后端目录:
```bash
cd backend
```

创建并激活虚拟环境:

**Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

**Linux/Mac:**
```bash
python -m venv venv
source venv/bin/activate
```

安装依赖:
```bash
pip install -r requirements.txt
```

配置环境变量:
```bash
# Windows
copy .env.example .env

# Linux/Mac
cp .env.example .env
```

编辑 `.env` 文件,根据需要修改配置。

运行数据库迁移:
```bash
alembic upgrade head
```

启动后端服务:
```bash
uvicorn app.main:app --reload --port 8000
```

#### 3. 前端设置

打开新终端,进入前端目录:
```bash
cd frontend
```

安装依赖:
```bash
npm install
```

启动开发服务器:
```bash
npm run dev
```

## 验证安装

### 检查后端

访问以下地址验证后端是否正常运行:

- API 根路径: http://localhost:8000
- API 文档 (Swagger): http://localhost:8000/docs
- 健康检查: http://localhost:8000/api/health

预期响应:
```json
{
  "status": "healthy"
}
```

### 检查前端

访问: http://localhost:3000

应该看到系统首页显示 "教研室工作考评系统"。

### 检查数据库

使用 PostgreSQL 客户端连接:
```bash
psql -h localhost -U postgres -d teaching_office_evaluation
```

密码: `postgres`

### 检查 MinIO

访问 MinIO 控制台: http://localhost:9001

登录凭据:
- 用户名: `minioadmin`
- 密码: `minioadmin`

## 配置说明

### 后端配置 (.env)

```env
# 数据库配置
POSTGRES_SERVER=localhost
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_DB=teaching_office_evaluation
POSTGRES_PORT=5432

# MinIO 配置
MINIO_ENDPOINT=localhost:9000
MINIO_ACCESS_KEY=minioadmin
MINIO_SECRET_KEY=minioadmin
MINIO_BUCKET=teaching-office-attachments
MINIO_SECURE=false

# JWT 配置
SECRET_KEY=your-secret-key-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=10080

# DeepSeek API 配置
DEEPSEEK_API_KEY=your-deepseek-api-key
DEEPSEEK_API_URL=https://api.deepseek.com/v1/chat/completions

# CORS 配置
BACKEND_CORS_ORIGINS=["http://localhost:3000"]
```

### 前端配置

前端配置在 `vite.config.ts` 中:

```typescript
server: {
  port: 3000,
  proxy: {
    '/api': {
      target: 'http://localhost:8000',
      changeOrigin: true
    }
  }
}
```

## 常见问题

### 1. Docker 服务无法启动

**问题**: `docker-compose up -d` 失败

**解决方案**:
- 确保 Docker Desktop 正在运行
- 检查端口 5432 和 9000 是否被占用
- 运行 `docker-compose down` 清理后重试

### 2. Python 依赖安装失败

**问题**: `pip install -r requirements.txt` 失败

**解决方案**:
- 确保使用 Python 3.11+
- 升级 pip: `pip install --upgrade pip`
- 如果是 Windows,可能需要安装 Visual C++ Build Tools

### 3. 数据库连接失败

**问题**: 后端无法连接到 PostgreSQL

**解决方案**:
- 确保 Docker 容器正在运行: `docker-compose ps`
- 检查 `.env` 文件中的数据库配置
- 等待几秒让数据库完全启动

### 4. 前端无法访问后端 API

**问题**: 前端请求返回 CORS 错误

**解决方案**:
- 确保后端正在运行
- 检查 `backend/app/core/config.py` 中的 CORS 配置
- 确认前端地址在 `BACKEND_CORS_ORIGINS` 列表中

### 5. MinIO 连接失败

**问题**: 文件上传失败

**解决方案**:
- 确保 MinIO 容器正在运行
- 访问 http://localhost:9001 验证 MinIO 控制台
- 检查 `.env` 中的 MinIO 配置

## 开发工作流

### 启动开发环境

1. 启动 Docker 服务:
```bash
docker-compose up -d
```

2. 启动后端 (新终端):
```bash
cd backend
source venv/bin/activate  # Windows: venv\Scripts\activate
uvicorn app.main:app --reload
```

3. 启动前端 (新终端):
```bash
cd frontend
npm run dev
```

### 停止开发环境

1. 停止前端和后端 (Ctrl+C)

2. 停止 Docker 服务:
```bash
docker-compose down
```

### 运行测试

后端测试:
```bash
cd backend
pytest
```

前端测试:
```bash
cd frontend
npm run test
```

## 下一步

项目初始化完成后,您可以:

1. 查看 [README.md](README.md) 了解项目概述
2. 查看 [.kiro/specs/teaching-office-evaluation-system/](..kiro/specs/teaching-office-evaluation-system/) 了解详细需求和设计
3. 开始实现 Task 2: 数据库设计和初始化

## 获取帮助

如果遇到问题:
1. 检查本文档的"常见问题"部分
2. 查看项目 README.md
3. 检查 Docker 和服务日志
4. 联系项目维护者
