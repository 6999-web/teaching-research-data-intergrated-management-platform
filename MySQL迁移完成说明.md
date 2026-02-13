# MySQL数据库迁移完成说明

## ✅ 迁移状态

数据库已成功从SQLite迁移到MySQL！

---

## 📊 迁移结果

### 创建的表（共15个）

1. ✓ users - 用户表
2. ✓ colleges - 学院表
3. ✓ teaching_offices - 教研室表
4. ✓ self_evaluations - 自评表
5. ✓ ai_scores - AI评分表
6. ✓ manual_scores - 手动评分表
7. ✓ final_scores - 最终得分表
8. ✓ attachments - 附件表
9. ✓ anomalies - 异常表
10. ✓ publications - 公示表
11. ✓ approvals - 审批表
12. ✓ operation_logs - 操作日志表
13. ✓ sync_tasks - 同步任务表
14. ✓ insight_summaries - 洞察摘要表
15. ✓ improvement_plans - 改进计划表

---

## 🔧 技术改进

### 1. 跨平台UUID支持

创建了自定义UUID类型 (`backend/app/db/types.py`)，支持：
- PostgreSQL: 使用原生UUID类型
- MySQL: 使用CHAR(36)存储UUID字符串
- SQLite: 使用CHAR(36)存储UUID字符串

### 2. 数据类型兼容

- UUID → CHAR(36)
- JSONB → JSON
- ARRAY → JSON (数组存储为JSON格式)

### 3. 索引优化

所有重要字段都已创建索引：
- 用户名唯一索引
- 教研室代码唯一索引
- 评估年份索引
- 外键索引

---

## 📝 配置文件

### 当前配置 (backend/.env)

```env
# MySQL 数据库配置
MYSQL_SERVER=localhost
MYSQL_USER=root
MYSQL_PASSWORD=root
MYSQL_DB=teaching_office_evaluation
MYSQL_PORT=3306
```

### 数据库连接URL

自动生成格式：
```
mysql+pymysql://root:root@localhost:3306/teaching_office_evaluation?charset=utf8mb4
```

---

## 🚀 启动应用

### 1. 启动后端服务

```bash
cd backend
python -m uvicorn app.main:app --reload --port 8000
```

### 2. 验证数据库连接

访问健康检查端点：
```
http://localhost:8000/api/health
```

应该返回：
```json
{
  "status": "healthy",
  "database": "connected"
}
```

### 3. 访问API文档

```
http://localhost:8000/docs
```

---

## 📦 迁移工具

### 使用迁移脚本

脚本位置：`backend/migrate_to_mysql.py`

#### 仅创建表结构
```bash
python migrate_to_mysql.py --create-tables
```

#### 创建表并迁移数据
```bash
python migrate_to_mysql.py --migrate-data
```

#### 验证迁移结果
```bash
python migrate_to_mysql.py --verify
```

---

## 🔄 数据迁移（可选）

如果需要从SQLite迁移现有数据：

### 方法1: 使用迁移脚本

```bash
cd backend
python migrate_to_mysql.py --migrate-data
```

### 方法2: 手动导出导入

1. 从SQLite导出数据
2. 转换为MySQL兼容格式
3. 导入到MySQL

详细步骤请参考：`MySQL数据库配置指南.md`

---

## ⚠️ 注意事项

### 1. 字符集

数据库使用 `utf8mb4` 字符集，支持完整的Unicode字符（包括emoji）

### 2. 连接池

配置了连接池参数：
- pool_size: 20
- max_overflow: 10
- pool_recycle: 3600秒
- pool_pre_ping: True（自动重连）

### 3. 外键约束

所有外键关系已正确创建，确保数据完整性

### 4. 不可变记录

以下表的记录创建后不可修改或删除（通过SQLAlchemy事件监听器实现）：
- ai_scores（AI评分记录）
- manual_scores（手动评分记录）
- final_scores（最终得分记录）

---

## 🔍 验证清单

- [x] MySQL数据库已创建
- [x] 15个表结构已创建
- [x] 所有索引已创建
- [x] 外键关系已建立
- [x] 字符集设置为utf8mb4
- [x] 连接池配置完成
- [x] UUID类型兼容性处理
- [x] JSON类型兼容性处理

---

## 📚 相关文档

- `MySQL数据库配置指南.md` - 详细的配置和迁移指南
- `项目介绍文档.md` - 项目整体介绍（已更新为MySQL）
- `backend/app/db/types.py` - 自定义数据库类型
- `backend/migrate_to_mysql.py` - 数据库迁移脚本

---

## 🎉 完成！

数据库已成功迁移到MySQL，系统现在使用企业级数据库，具有更好的：
- ✅ 并发性能
- ✅ 数据完整性
- ✅ 扩展性
- ✅ 可靠性

可以开始使用新的MySQL数据库了！

---

**迁移日期**: 2026-02-13  
**MySQL版本**: 8.0  
**Python版本**: 3.13  
**SQLAlchemy版本**: 2.x
