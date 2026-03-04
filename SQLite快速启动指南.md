# SQLite 快速启动指南

## 简介
本指南帮助你快速启动使用 SQLite 数据库的教研室数据管理平台。

---

## 前提条件

### 必需软件
- Python 3.8+ （已安装）
- Node.js 16+ （已安装）
- SQLite 3 （Python 内置，无需额外安装）

### 可选软件
- DB Browser for SQLite（查看数据库内容）
- SQLite 命令行工具（调试用）

---

## 快速启动步骤

### 1. 后端启动

#### 方法 A：使用初始化脚本（推荐）

```bash
# 进入后端目录
cd backend

# 运行初始化脚本
python init_sqlite.py

# 启动后端服务
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

#### 方法 B：手动初始化

```bash
# 进入后端目录
cd backend

# 安装依赖（如果还没有）
pip install -r requirements.txt

# 运行数据库迁移
alembic upgrade head

# 初始化数据
python -c "from app.db.init_db import init_db; init_db()"

# 启动后端服务
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 2. 前端启动

```bash
# 进入前端目录
cd frontend

# 安装依赖（如果还没有）
npm install

# 启动前端服务
npm run dev
```

### 3. 访问应用

- **前端页面**：http://localhost:5173
- **后端 API 文档**：http://localhost:8000/docs
- **数据大屏**：http://localhost:5173/data-dashboard

---

## 验证安装

### 1. 检查数据库文件

```bash
cd backend
ls -lh teaching_office_evaluation.db
```

应该看到数据库文件已创建。

### 2. 查看数据库内容

```bash
# 使用 SQLite 命令行
sqlite3 teaching_office_evaluation.db

# 查看所有表
.tables

# 查看用户表
SELECT * FROM users;

# 退出
.quit
```

### 3. 测试 API

访问 http://localhost:8000/docs，测试以下接口：

- `GET /api/health` - 健康检查
- `POST /api/auth/login` - 登录测试

---

## 默认账号

系统初始化后会创建以下测试账号：

### 教研室端
- 用户名：`director1`
- 密码：`password123`
- 角色：教研室

### 管理端 - 评教小组
- 用户名：`evaluator1`
- 密码：`password123`
- 角色：评教小组

### 管理端 - 评教小组办公室
- 用户名：`office1`
- 密码：`password123`
- 角色：评教小组办公室

### 管理端 - 校长办公会
- 用户名：`president1`
- 密码：`password123`
- 角色：校长办公会

---

## 常见问题

### Q1: 数据库文件在哪里？
A: `backend/teaching_office_evaluation.db`

### Q2: 如何重置数据库？
```bash
cd backend
rm teaching_office_evaluation.db
python init_sqlite.py
```

### Q3: 如何备份数据库？
```bash
cd backend
cp teaching_office_evaluation.db teaching_office_evaluation.db.backup
```

### Q4: 如何恢复数据库？
```bash
cd backend
cp teaching_office_evaluation.db.backup teaching_office_evaluation.db
```

### Q5: 启动时报错 "database is locked"
这通常是因为有其他进程正在使用数据库。解决方法：
```bash
# 停止所有后端进程
pkill -f uvicorn

# 重新启动
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Q6: 如何查看数据库日志？
```bash
# 启动时启用 SQL 日志
cd backend
# 修改 app/db/base.py，设置 echo=True
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

---

## 性能优化

### 1. 启用 WAL 模式（已自动启用）

WAL (Write-Ahead Logging) 模式可以提高并发性能，系统已自动启用。

验证：
```bash
sqlite3 teaching_office_evaluation.db "PRAGMA journal_mode;"
# 应该输出：wal
```

### 2. 定期维护

```bash
# 优化数据库
sqlite3 teaching_office_evaluation.db "VACUUM;"

# 更新统计信息
sqlite3 teaching_office_evaluation.db "ANALYZE;"
```

建议每周运行一次。

### 3. 监控数据库大小

```bash
# 查看数据库文件大小
du -h teaching_office_evaluation.db

# 查看详细信息
sqlite3 teaching_office_evaluation.db ".dbinfo"
```

---

## 开发工具

### 1. DB Browser for SQLite（推荐）

**下载**：https://sqlitebrowser.org/

**功能**：
- 可视化查看和编辑数据
- 执行 SQL 查询
- 导入/导出数据
- 查看表结构

### 2. SQLite 命令行工具

**安装**：
```bash
# Ubuntu/Debian
sudo apt-get install sqlite3

# macOS
brew install sqlite3

# Windows
# 从 https://www.sqlite.org/download.html 下载
```

**常用命令**：
```bash
# 打开数据库
sqlite3 teaching_office_evaluation.db

# 查看所有表
.tables

# 查看表结构
.schema users

# 执行查询
SELECT * FROM users;

# 导出数据
.output users.sql
.dump users

# 导入数据
.read users.sql

# 退出
.quit
```

### 3. DBeaver（通用数据库工具）

**下载**：https://dbeaver.io/

支持多种数据库，包括 SQLite。

---

## 生产环境部署

### 1. 文件权限

```bash
# 设置数据库文件权限
chmod 644 teaching_office_evaluation.db

# 设置目录权限
chmod 755 backend
```

### 2. 备份策略

```bash
# 创建备份脚本 backup.sh
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
cp teaching_office_evaluation.db backups/teaching_office_evaluation_$DATE.db
# 保留最近7天的备份
find backups/ -name "*.db" -mtime +7 -delete
```

### 3. 使用 Gunicorn

```bash
# 生产环境启动
gunicorn app.main:app \
  -w 4 \
  -k uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:8000 \
  --access-logfile access.log \
  --error-logfile error.log
```

---

## 切换到 PostgreSQL

如果将来需要切换到 PostgreSQL：

### 1. 修改配置

```bash
# 编辑 backend/.env
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/teaching_office_evaluation
```

### 2. 安装 PostgreSQL

```bash
# Ubuntu/Debian
sudo apt-get install postgresql postgresql-contrib

# macOS
brew install postgresql
```

### 3. 创建数据库

```bash
# 创建数据库
createdb teaching_office_evaluation

# 运行迁移
cd backend
alembic upgrade head
```

### 4. 迁移数据（可选）

使用 `数据库迁移到SQLite说明.md` 中的迁移脚本。

---

## 总结

使用 SQLite 的优势：
- ✅ 零配置，开箱即用
- ✅ 无需安装数据库服务器
- ✅ 便于开发和测试
- ✅ 适合单机部署
- ✅ 数据库文件易于备份和迁移

现在你可以开始使用教研室数据管理平台了！

---

**文档版本**：v1.0  
**更新日期**：2024年  
**维护人员**：开发团队
