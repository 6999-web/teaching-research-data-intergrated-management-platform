# 教研室工作考评系统

教研室工作考评系统是一个三端分离的Web应用系统,实现教研室自评、AI自动评分、管理端审核、校长办公会审定、结果公示与分发的全流程数字化管理。

## 技术栈

### 前端
- Vue 3 + TypeScript
- Element Plus
- Vite
- Pinia (状态管理)
- Vue Router

### 后端
- FastAPI + Python
- SQLAlchemy (ORM)
- PostgreSQL (数据库)
- MinIO (对象存储)
- Alembic (数据库迁移)
- DeepSeek API (AI评分)

## 项目结构

```
.
├── frontend/              # 前端项目
│   ├── src/
│   │   ├── api/          # API客户端
│   │   ├── components/   # Vue组件
│   │   ├── router/       # 路由配置
│   │   ├── views/        # 页面视图
│   │   ├── App.vue       # 根组件
│   │   └── main.ts       # 入口文件
│   ├── package.json
│   └── vite.config.ts
│
├── backend/              # 后端项目
│   ├── alembic/         # 数据库迁移
│   ├── app/
│   │   ├── api/         # API路由
│   │   ├── core/        # 核心配置
│   │   ├── db/          # 数据库配置
│   │   ├── models/      # 数据模型
│   │   ├── services/    # 业务服务
│   │   └── main.py      # 应用入口
│   ├── tests/           # 测试文件
│   └── requirements.txt
│
└── docker-compose.yml   # Docker编排配置
```

## 快速开始

### 前置要求

- Node.js 18+
- Python 3.11+
- PostgreSQL 15+
- MinIO (或使用Docker)

### 使用Docker启动依赖服务

```bash
docker-compose up -d
```

这将启动:
- PostgreSQL (端口 5432)
- MinIO (端口 9000, 控制台 9001)

### 后端设置

1. 进入后端目录:
```bash
cd backend
```

2. 创建虚拟环境并安装依赖:
```bash
python -m venv venv
# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate

pip install -r requirements.txt
```

3. 配置环境变量:
```bash
copy .env.example .env
# 编辑 .env 文件,配置数据库和MinIO连接信息
```

4. 运行数据库迁移:
```bash
alembic upgrade head
```

5. 启动后端服务:
```bash
uvicorn app.main:app --reload --port 8000
```

后端API文档: http://localhost:8000/docs

### 前端设置

1. 进入前端目录:
```bash
cd frontend
```

2. 安装依赖:
```bash
npm install
```

3. 启动开发服务器:
```bash
npm run dev
```

前端应用: http://localhost:3000

## 开发指南

### 代码规范

- 前端使用 ESLint + TypeScript
- 后端遵循 PEP 8 规范
- 提交前运行 lint 检查

### 测试

前端测试:
```bash
cd frontend
npm run test
```

后端测试:
```bash
cd backend
pytest
```

### 数据库迁移

创建新迁移:
```bash
cd backend
alembic revision --autogenerate -m "描述"
```

应用迁移:
```bash
alembic upgrade head
```

回滚迁移:
```bash
alembic downgrade -1
```

## 部署

### 开发环境部署

使用Docker Compose快速启动开发环境:

```bash
docker-compose up -d
```

### 生产环境部署

#### 快速部署

使用自动化部署脚本:

```bash
# 1. 配置环境变量
cp backend/.env.production backend/.env
# 编辑 backend/.env 文件,设置生产环境配置

# 2. 配置SSL证书
# 将证书放置在 ssl/ 目录

# 3. 运行部署脚本
./deploy-production.sh
```

#### 手动部署

详细的生产环境部署步骤,请参考:

- **[部署指南](DEPLOYMENT_GUIDE.md)** - 完整的部署文档
- **[部署检查清单](DEPLOYMENT_CHECKLIST.md)** - 部署前检查清单
- **[配置摘要](CONFIGURATION_SUMMARY.md)** - 所有配置说明

#### 主要配置文件

- `backend/.env.production` - 生产环境变量模板
- `docker-compose.production.yml` - 生产环境Docker配置
- `nginx/nginx.conf` - Nginx配置
- `ssl/` - SSL证书目录
- `scripts/` - 备份和维护脚本

#### 备份策略

系统提供自动化备份功能:

- **数据库备份**: 每日自动备份,保留30天
- **MinIO备份**: 支持手动或定时备份
- **备份脚本**: 位于 `scripts/` 目录

详细信息请参考 [scripts/README.md](scripts/README.md)

#### 部署要求

**最低配置**:
- CPU: 4核
- 内存: 8GB
- 存储: 100GB SSD
- 操作系统: Linux (Ubuntu 20.04+ 或 CentOS 8+)

**软件要求**:
- Docker 20.10+
- Docker Compose 2.0+
- SSL证书 (Let's Encrypt 或商业CA)

#### 安全配置

生产环境必须配置:

1. **HTTPS**: 使用有效的SSL证书
2. **强密码**: 所有密码和密钥使用强随机值
3. **防火墙**: 仅开放必要端口 (80, 443)
4. **备份**: 配置自动备份和异地备份
5. **监控**: 配置服务监控和告警

#### 监控和维护

- 日志位置: `backend/logs/`
- 备份位置: `backups/`
- 健康检查: `https://your-domain.com/api/health`

查看服务状态:
```bash
docker-compose -f docker-compose.production.yml ps
```

查看日志:
```bash
docker-compose -f docker-compose.production.yml logs -f
```

## 文档

- [部署指南](DEPLOYMENT_GUIDE.md) - 完整的生产环境部署指南
- [部署检查清单](DEPLOYMENT_CHECKLIST.md) - 部署前后检查清单
- [配置摘要](CONFIGURATION_SUMMARY.md) - 所有配置文件说明
- [备份脚本说明](scripts/README.md) - 备份和恢复程序
- [SSL配置](ssl/README.md) - SSL证书配置说明
- [快速开始](QUICK_START.md) - 快速开始指南
- [项目状态](PROJECT_STATUS.md) - 项目当前状态

## 许可证

MIT
