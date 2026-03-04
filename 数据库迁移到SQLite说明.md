# 数据库迁移到 SQLite 说明

## 更新时间
2024年（最新版本）

## 迁移概述
将教研室数据管理平台的数据库从 PostgreSQL 迁移到 SQLite，简化部署和开发环境配置。

---

## 一、迁移原因

### 为什么选择 SQLite？

1. **简化部署**
   - 无需安装和配置 PostgreSQL 服务器
   - 数据库文件直接存储在项目目录
   - 适合单机部署和小规模应用

2. **开发便利**
   - 零配置，开箱即用
   - 便于版本控制和备份
   - 适合开发和测试环境

3. **性能足够**
   - 对于中小规模应用，SQLite 性能完全够用
   - 读取性能优秀
   - 适合单服务器部署

### 何时应该使用 PostgreSQL？

如果你的应用有以下需求，建议继续使用 PostgreSQL：
- 高并发写入（>1000 TPS）
- 多服务器部署
- 需要复杂的查询优化
- 需要高级数据库特性（如全文搜索、JSON 查询等）

---

## 二、已完成的修改

### 1. 配置文件修改

#### backend/app/core/config.py
```python
# 修改前
POSTGRES_SERVER: str = "localhost"
POSTGRES_USER: str = "postgres"
POSTGRES_PASSWORD: str = "postgres"
POSTGRES_DB: str = "teaching_office_evaluation"
POSTGRES_PORT: int = 5432

@property
def DATABASE_URL(self) -> str:
    return f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_SERVER}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"

# 修改后
DATABASE_URL: str = "sqlite:///./teaching_office_evaluation.db"

# PostgreSQL 配置（备用）
POSTGRES_SERVER: str = "localhost"
POSTGRES_USER: str = "postgres"
POSTGRES_PASSWORD: str = "postgres"
POSTGRES_DB: str = "teaching_office_evaluation"
POSTGRES_PORT: int = 5432
```

### 2. 数据库引擎配置

#### backend/app/db/base.py
```python
# 添加了 SQLite 和 PostgreSQL 的条件配置
if settings.DATABASE_URL.startswith("sqlite"):
    # SQLite 配置
    engine = create_engine(
        settings.DATABASE_URL,
        connect_args={"check_same_thread": False},
        echo=False
    )
else:
    # PostgreSQL 配置（带连接池）
    engine = create_engine(
        settings.DATABASE_URL,
        poolclass=QueuePool,
        pool_size=20,
        max_overflow=10,
        pool_recycle=3600,
        pool_pre_ping=True,
        pool_timeout=30,
        echo=False
    )
```

**关键点**：
- SQLite 需要 `check_same_thread=False` 以支持多线程
- SQLite 不需要连接池配置
- PostgreSQL 保留了原有的连接池配置

### 3. 环境变量文件

#### backend/.env
```properties
# 修改前
POSTGRES_SERVER=localhost
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_DB=teaching_office_evaluation
POSTGRES_PORT=5432

# 修改后
DATABASE_URL=sqlite:///./teaching_office_evaluation.db

# PostgreSQL (备用配置)
# POSTGRES_SERVER=localhost
# POSTGRES_USER=postgres
# POSTGRES_PASSWORD=postgres
# POSTGRES_DB=teaching_office_evaluation
# POSTGRES_PORT=5432
```

---

## 三、数据类型兼容性

### SQLAlchemy 自动处理的类型转换

| PostgreSQL 类型 | SQLite 存储 | SQLAlchemy 处理 |
|----------------|------------|----------------|
| UUID | TEXT | 自动转换为字符串 |
| TIMESTAMP | TEXT | 自动转换为 ISO 8601 格式 |
| BOOLEAN | INTEGER | 0/1 |
| JSON/JSONB | TEXT | 自动序列化/反序列化 |
| ARRAY | TEXT | 需要手动处理 |

### 注意事项

1. **UUID 字段**
   - PostgreSQL: 原生 UUID 类型
   - SQLite: 存储为 TEXT (36字符)
   - SQLAlchemy 自动处理转换，代码无需修改

2. **日期时间字段**
   - PostgreSQL: TIMESTAMP WITH TIME ZONE
   - SQLite: TEXT (ISO 8601 格式)
   - SQLAlchemy 自动处理转换

3. **JSON 字段**
   - PostgreSQL: JSONB (二进制 JSON)
   - SQLite: TEXT (JSON 字符串)
   - SQLAlchemy 自动序列化/反序列化

4. **数组字段**
   - PostgreSQL: ARRAY 类型
   - SQLite: 不支持，需要使用 JSON 或关联表
   - 本项目未使用数组字段，无需处理

---

## 四、迁移步骤

### 步骤 1：备份现有数据（如果有）

如果你已经在使用 PostgreSQL 并有数据，请先备份：

```bash
# 导出 PostgreSQL 数据
pg_dump -U postgres teaching_office_evaluation > backup.sql

# 或使用 Python 脚本导出为 JSON
python export_data.py
```

### 步骤 2：删除旧的数据库文件

```bash
cd backend
rm -f test.db teaching_office_evaluation.db
```

### 步骤 3：运行数据库迁移

```bash
cd backend

# 初始化 Alembic（如果还没有）
alembic upgrade head
```

### 步骤 4：初始化数据库

```bash
# 运行初始化脚本
python -c "from app.db.init_db import init_db; init_db()"
```

### 步骤 5：启动应用

```bash
# 开发环境
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# 生产环境
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

### 步骤 6：验证

访问 http://localhost:8000/docs 查看 API 文档，测试各个接口。

---

## 五、数据迁移（PostgreSQL → SQLite）

如果需要将现有的 PostgreSQL 数据迁移到 SQLite：

### 方法 1：使用 Python 脚本

创建 `migrate_data.py`：

```python
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models import *
from app.core.config import settings

# 源数据库（PostgreSQL）
source_url = "postgresql://postgres:postgres@localhost:5432/teaching_office_evaluation"
source_engine = create_engine(source_url)
SourceSession = sessionmaker(bind=source_engine)

# 目标数据库（SQLite）
target_url = "sqlite:///./teaching_office_evaluation.db"
target_engine = create_engine(target_url)
TargetSession = sessionmaker(bind=target_engine)

def migrate_table(model_class):
    """迁移单个表的数据"""
    source_session = SourceSession()
    target_session = TargetSession()
    
    try:
        # 读取源数据
        records = source_session.query(model_class).all()
        print(f"迁移 {model_class.__tablename__}: {len(records)} 条记录")
        
        # 写入目标数据库
        for record in records:
            # 创建新对象（避免 session 冲突）
            new_record = model_class(**{
                c.name: getattr(record, c.name)
                for c in model_class.__table__.columns
            })
            target_session.add(new_record)
        
        target_session.commit()
        print(f"✓ {model_class.__tablename__} 迁移完成")
        
    except Exception as e:
        print(f"✗ {model_class.__tablename__} 迁移失败: {e}")
        target_session.rollback()
    finally:
        source_session.close()
        target_session.close()

# 按依赖顺序迁移表
tables_to_migrate = [
    TeachingOffice,
    User,
    College,
    SelfEvaluation,
    Attachment,
    AIScore,
    ManualScore,
    FinalScore,
    Anomaly,
    Approval,
    Publication,
    InsightSummary,
    OperationLog,
    SyncTask,
    ImprovementPlan,
]

for model in tables_to_migrate:
    migrate_table(model)

print("\n数据迁移完成！")
```

运行迁移：
```bash
python migrate_data.py
```

### 方法 2：使用 pgloader（推荐）

```bash
# 安装 pgloader
sudo apt-get install pgloader  # Ubuntu/Debian
brew install pgloader           # macOS

# 创建迁移配置文件 migrate.load
cat > migrate.load << EOF
LOAD DATABASE
    FROM postgresql://postgres:postgres@localhost:5432/teaching_office_evaluation
    INTO sqlite:///./teaching_office_evaluation.db
    WITH include drop, create tables, create indexes, reset sequences
    SET work_mem to '16MB', maintenance_work_mem to '512 MB';
EOF

# 执行迁移
pgloader migrate.load
```

---

## 六、性能优化建议

### 1. 启用 WAL 模式

SQLite 的 WAL (Write-Ahead Logging) 模式可以提高并发性能：

```python
# 在 backend/app/db/base.py 中添加
from sqlalchemy import event

@event.listens_for(engine, "connect")
def set_sqlite_pragma(dbapi_conn, connection_record):
    if settings.DATABASE_URL.startswith("sqlite"):
        cursor = dbapi_conn.cursor()
        cursor.execute("PRAGMA journal_mode=WAL")
        cursor.execute("PRAGMA synchronous=NORMAL")
        cursor.execute("PRAGMA cache_size=-64000")  # 64MB cache
        cursor.execute("PRAGMA temp_store=MEMORY")
        cursor.close()
```

### 2. 定期优化数据库

```bash
# 定期运行 VACUUM 命令
sqlite3 teaching_office_evaluation.db "VACUUM;"

# 分析查询性能
sqlite3 teaching_office_evaluation.db "ANALYZE;"
```

### 3. 索引优化

确保常用查询字段有索引：
```sql
CREATE INDEX IF NOT EXISTS idx_self_evaluations_teaching_office 
ON self_evaluations(teaching_office_id);

CREATE INDEX IF NOT EXISTS idx_attachments_evaluation 
ON attachments(evaluation_id);
```

---

## 七、限制和注意事项

### SQLite 的限制

1. **并发写入**
   - SQLite 同时只能有一个写入操作
   - 适合读多写少的场景
   - 如果有高并发写入需求，建议使用 PostgreSQL

2. **数据库大小**
   - 理论上限：281 TB
   - 实际建议：< 100 GB
   - 超过此大小建议使用 PostgreSQL

3. **网络访问**
   - SQLite 是文件数据库，不支持网络访问
   - 只能在本地访问
   - 多服务器部署必须使用 PostgreSQL

4. **用户权限**
   - SQLite 没有用户权限系统
   - 依赖文件系统权限
   - 生产环境需要注意文件权限设置

### 兼容性注意事项

1. **迁移文件**
   - 现有的 Alembic 迁移文件使用了 `postgresql.UUID`
   - SQLAlchemy 会自动将其转换为 TEXT
   - 迁移可以正常运行，无需修改

2. **查询语法**
   - 避免使用 PostgreSQL 特定的 SQL 语法
   - 使用 SQLAlchemy ORM 可以自动处理大部分差异

3. **事务处理**
   - SQLite 的事务隔离级别与 PostgreSQL 不同
   - 默认是 SERIALIZABLE
   - 注意处理并发事务

---

## 八、切换回 PostgreSQL

如果将来需要切换回 PostgreSQL：

### 1. 修改配置

```python
# backend/app/core/config.py
DATABASE_URL: str = f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_SERVER}:{POSTGRES_PORT}/{POSTGRES_DB}"
```

### 2. 修改环境变量

```properties
# backend/.env
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/teaching_office_evaluation
```

### 3. 迁移数据

使用上面提到的迁移脚本，反向迁移数据。

---

## 九、测试清单

### 功能测试
- [ ] 用户登录/注册
- [ ] 自评表填写和保存
- [ ] 附件上传和下载
- [ ] AI 评分功能
- [ ] 手动评分功能
- [ ] 最终得分计算
- [ ] 数据公示
- [ ] 改进措施管理

### 性能测试
- [ ] 并发读取测试
- [ ] 并发写入测试
- [ ] 大数据量查询测试
- [ ] 数据库文件大小监控

### 兼容性测试
- [ ] Windows 环境测试
- [ ] Linux 环境测试
- [ ] macOS 环境测试
- [ ] Docker 容器测试

---

## 十、文件清单

### 修改的文件
1. `backend/app/core/config.py` - 数据库配置
2. `backend/app/db/base.py` - 数据库引擎配置
3. `backend/.env` - 环境变量

### 新增的文件
1. `数据库迁移到SQLite说明.md` - 本文档

### 数据库文件
- `backend/teaching_office_evaluation.db` - SQLite 数据库文件（自动生成）
- `backend/teaching_office_evaluation.db-shm` - 共享内存文件（WAL 模式）
- `backend/teaching_office_evaluation.db-wal` - 预写日志文件（WAL 模式）

---

## 十一、常见问题

### Q1: 数据库文件在哪里？
A: 在 `backend/teaching_office_evaluation.db`

### Q2: 如何备份数据库？
A: 直接复制 `.db` 文件即可：
```bash
cp teaching_office_evaluation.db teaching_office_evaluation.db.backup
```

### Q3: 如何查看数据库内容？
A: 使用 SQLite 命令行工具：
```bash
sqlite3 teaching_office_evaluation.db
.tables  # 查看所有表
SELECT * FROM users;  # 查询数据
.quit  # 退出
```

或使用图形化工具：
- DB Browser for SQLite (推荐)
- DBeaver
- DataGrip

### Q4: 迁移后性能下降怎么办？
A: 
1. 启用 WAL 模式（见性能优化部分）
2. 添加必要的索引
3. 定期运行 VACUUM 和 ANALYZE
4. 如果仍然不够，考虑切换回 PostgreSQL

### Q5: 可以同时支持两种数据库吗？
A: 可以，通过环境变量切换：
```bash
# 使用 SQLite
export DATABASE_URL="sqlite:///./teaching_office_evaluation.db"

# 使用 PostgreSQL
export DATABASE_URL="postgresql://postgres:postgres@localhost:5432/teaching_office_evaluation"
```

---

## 十二、总结

本次迁移成功将数据库从 PostgreSQL 改为 SQLite，主要优势：

1. ✅ 简化部署，无需安装数据库服务器
2. ✅ 零配置，开箱即用
3. ✅ 便于开发和测试
4. ✅ 适合单机部署和中小规模应用
5. ✅ 保留了切换回 PostgreSQL 的能力

对于教研室数据管理平台这样的应用场景，SQLite 完全能够满足需求。如果将来有更高的并发或分布式部署需求，可以随时切换回 PostgreSQL。

---

**文档版本**：v1.0  
**更新日期**：2024年  
**维护人员**：开发团队
