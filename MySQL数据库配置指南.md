# MySQL数据库配置指南

## 📋 概述

本指南将帮助您将教研室数据管理平台的数据库从SQLite迁移到MySQL。

---

## 🔧 准备工作

### 1. 安装MySQL

#### Windows
1. 下载MySQL安装包: https://dev.mysql.com/downloads/mysql/
2. 运行安装程序
3. 设置root密码
4. 启动MySQL服务

#### Linux (Ubuntu/Debian)
```bash
sudo apt update
sudo apt install mysql-server
sudo mysql_secure_installation
```

#### Linux (CentOS/RHEL)
```bash
sudo yum install mysql-server
sudo systemctl start mysqld
sudo mysql_secure_installation
```

### 2. 创建数据库

登录MySQL:
```bash
mysql -u root -p
```

创建数据库:
```sql
CREATE DATABASE teaching_office_evaluation CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

创建用户（可选，推荐）:
```sql
CREATE USER 'teaching_office'@'localhost' IDENTIFIED BY 'your_secure_password';
GRANT ALL PRIVILEGES ON teaching_office_evaluation.* TO 'teaching_office'@'localhost';
FLUSH PRIVILEGES;
```

退出MySQL:
```sql
EXIT;
```

---

## ⚙️ 配置步骤

### 1. 安装Python依赖

```bash
cd backend
pip install -r requirements.txt
```

主要新增的依赖:
- `pymysql`: MySQL数据库驱动
- `cryptography`: 加密支持

### 2. 配置环境变量

编辑 `backend/.env` 文件:

```env
# MySQL 数据库配置
MYSQL_SERVER=localhost
MYSQL_USER=root
MYSQL_PASSWORD=your_password
MYSQL_DB=teaching_office_evaluation
MYSQL_PORT=3306
```

**重要**: 
- 将 `your_password` 替换为您的MySQL密码
- 如果创建了专用用户，使用该用户名和密码

### 3. 运行数据库迁移

```bash
cd backend

# 初始化数据库表结构
alembic upgrade head
```

---

## 🔄 数据迁移（可选）

如果您需要从SQLite迁移现有数据到MySQL:

### 方法1: 使用Python脚本

创建 `backend/migrate_to_mysql.py`:

```python
import sqlite3
import pymysql
from app.core.config import settings

# 连接SQLite
sqlite_conn = sqlite3.connect('teaching_office_evaluation.db')
sqlite_cursor = sqlite_conn.cursor()

# 连接MySQL
mysql_conn = pymysql.connect(
    host=settings.MYSQL_SERVER,
    user=settings.MYSQL_USER,
    password=settings.MYSQL_PASSWORD,
    database=settings.MYSQL_DB,
    charset='utf8mb4'
)
mysql_cursor = mysql_conn.cursor()

# 获取所有表名
sqlite_cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = sqlite_cursor.fetchall()

for table in tables:
    table_name = table[0]
    if table_name == 'sqlite_sequence':
        continue
    
    print(f"迁移表: {table_name}")
    
    # 获取表数据
    sqlite_cursor.execute(f"SELECT * FROM {table_name}")
    rows = sqlite_cursor.fetchall()
    
    if rows:
        # 获取列名
        column_names = [description[0] for description in sqlite_cursor.description]
        placeholders = ', '.join(['%s'] * len(column_names))
        columns = ', '.join(column_names)
        
        # 插入数据
        insert_query = f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders})"
        mysql_cursor.executemany(insert_query, rows)
        mysql_conn.commit()
        print(f"  - 迁移了 {len(rows)} 条记录")

print("数据迁移完成！")

sqlite_conn.close()
mysql_conn.close()
```

运行迁移脚本:
```bash
python migrate_to_mysql.py
```

### 方法2: 使用工具

使用 `mysql-workbench` 或其他数据库迁移工具进行可视化迁移。

---

## 🚀 启动应用

### 开发环境

```bash
cd backend
python -m uvicorn app.main:app --reload --port 8000
```

### 生产环境

```bash
cd backend
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker -b 0.0.0.0:8000
```

---

## ✅ 验证配置

### 1. 检查数据库连接

访问: http://localhost:8000/api/health

应该返回:
```json
{
  "status": "healthy",
  "database": "connected"
}
```

### 2. 查看日志

启动应用时应该看到:
```
INFO: 使用 MySQL 数据库
INFO: 数据库连接已建立
```

### 3. 测试API

访问API文档: http://localhost:8000/docs

测试几个API端点确保数据库操作正常。

---

## 🔧 常见问题

### 问题1: 连接被拒绝

**错误**: `Can't connect to MySQL server`

**解决方案**:
1. 确认MySQL服务正在运行:
   ```bash
   # Windows
   net start MySQL
   
   # Linux
   sudo systemctl status mysql
   ```

2. 检查防火墙设置
3. 确认MySQL端口（默认3306）未被占用

### 问题2: 认证失败

**错误**: `Access denied for user`

**解决方案**:
1. 检查用户名和密码是否正确
2. 确认用户有数据库访问权限:
   ```sql
   SHOW GRANTS FOR 'your_user'@'localhost';
   ```

### 问题3: 字符集问题

**错误**: 中文乱码

**解决方案**:
1. 确认数据库字符集:
   ```sql
   SHOW VARIABLES LIKE 'character_set%';
   ```

2. 设置为utf8mb4:
   ```sql
   ALTER DATABASE teaching_office_evaluation CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
   ```

### 问题4: 连接池耗尽

**错误**: `QueuePool limit exceeded`

**解决方案**:
调整 `backend/app/db/base.py` 中的连接池参数:
```python
engine = create_engine(
    settings.DATABASE_URL,
    pool_size=30,  # 增加连接池大小
    max_overflow=20,  # 增加溢出连接数
    pool_recycle=3600,
    pool_pre_ping=True
)
```

---

## 📊 性能优化

### 1. 索引优化

为常用查询字段添加索引:
```sql
-- 示例：为用户表的username字段添加索引
CREATE INDEX idx_user_username ON user(username);

-- 为自评表的年份字段添加索引
CREATE INDEX idx_self_evaluation_year ON self_evaluation(evaluation_year);
```

### 2. 连接池配置

根据服务器性能调整连接池参数:
- `pool_size`: 基础连接数（建议: CPU核心数 * 2）
- `max_overflow`: 额外连接数（建议: pool_size的50%）
- `pool_recycle`: 连接回收时间（建议: 3600秒）

### 3. 查询优化

使用 `EXPLAIN` 分析慢查询:
```sql
EXPLAIN SELECT * FROM self_evaluation WHERE evaluation_year = 2024;
```

---

## 🔐 安全建议

### 1. 使用专用数据库用户

不要使用root用户，创建专用用户:
```sql
CREATE USER 'teaching_office'@'localhost' IDENTIFIED BY 'strong_password';
GRANT SELECT, INSERT, UPDATE, DELETE ON teaching_office_evaluation.* TO 'teaching_office'@'localhost';
```

### 2. 限制远程访问

如果不需要远程访问，只允许本地连接:
```sql
CREATE USER 'teaching_office'@'localhost' IDENTIFIED BY 'password';
```

### 3. 定期备份

设置自动备份:
```bash
# 创建备份脚本
cat > /usr/local/bin/backup_mysql.sh << 'EOF'
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
mysqldump -u root -p teaching_office_evaluation > /backup/teaching_office_$DATE.sql
# 保留最近7天的备份
find /backup -name "teaching_office_*.sql" -mtime +7 -delete
EOF

chmod +x /usr/local/bin/backup_mysql.sh

# 添加到crontab（每天凌晨2点备份）
crontab -e
0 2 * * * /usr/local/bin/backup_mysql.sh
```

---

## 📝 配置文件示例

### 生产环境 `.env`

```env
# MySQL 数据库配置
MYSQL_SERVER=localhost
MYSQL_USER=teaching_office
MYSQL_PASSWORD=your_secure_password_here
MYSQL_DB=teaching_office_evaluation
MYSQL_PORT=3306

# MinIO
MINIO_ENDPOINT=localhost:9000
MINIO_ACCESS_KEY=your_minio_access_key
MINIO_SECRET_KEY=your_minio_secret_key
MINIO_BUCKET=teaching-office-attachments
MINIO_SECURE=false

# JWT
SECRET_KEY=your_very_long_and_random_secret_key_here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=10080

# DeepSeek API
DEEPSEEK_API_KEY=your_deepseek_api_key
DEEPSEEK_API_URL=https://api.deepseek.com/v1/chat/completions

# CORS
BACKEND_CORS_ORIGINS=["http://101.33.211.98"]
```

---

## 🎯 总结

完成以上步骤后，您的系统将成功从SQLite迁移到MySQL。MySQL提供了更好的：
- ✅ 并发性能
- ✅ 数据完整性
- ✅ 扩展性
- ✅ 企业级特性

如有问题，请参考常见问题部分或查看MySQL官方文档。

---

**文档版本**: v1.0  
**更新日期**: 2024-02  
**适用版本**: v2.0.0+
