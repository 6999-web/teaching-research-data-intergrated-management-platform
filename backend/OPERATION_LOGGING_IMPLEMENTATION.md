# 操作日志记录实现文档

## 概述

本文档描述了教研室工作考评系统中操作日志记录功能的实现。

## 实现的功能

### 1. 操作日志记录中间件 (`backend/app/core/logging_middleware.py`)

自动记录所有关键操作的日志，包括：

- **表单提交** (submit) - 需求 17.1
  - POST /api/v1/teaching-office/self-evaluation
  - PUT /api/v1/teaching-office/self-evaluation/{evaluation_id}
  - POST /api/v1/teaching-office/self-evaluation/{evaluation_id}/submit

- **AI评分** (ai_score) - 需求 17.2
  - POST /api/v1/teaching-office/trigger-ai-scoring

- **手动评分** (manual_score) - 需求 17.3
  - POST /api/v1/scoring/manual-score

- **异常处理** (handle_anomaly) - 需求 17.4
  - POST /api/v1/review/handle-anomaly

- **数据同步** (sync) - 需求 17.5
  - POST /api/v1/review/sync-to-president-office

- **审定** (approve) - 需求 17.6
  - POST /api/v1/president-office/approve

- **公示** (publish) - 需求 17.7
  - POST /api/v1/publication/publish

- **结果分发** (distribute) - 需求 17.8
  - POST /api/v1/publication/distribute

### 2. 操作日志查询API (`backend/app/api/v1/endpoints/logs.py`)

提供操作日志的查询和筛选功能 - 需求 17.10

#### 端点：

- **GET /api/v1/logs** - 查询操作日志列表
  - 支持按操作类型筛选 (operation_type)
  - 支持按操作人筛选 (operator_id)
  - 支持按目标对象筛选 (target_id, target_type)
  - 支持按时间范围筛选 (start_date, end_date)
  - 支持分页 (skip, limit)

- **GET /api/v1/logs/{log_id}** - 查询单个操作日志详情

- **GET /api/v1/logs/by-evaluation/{evaluation_id}** - 查询特定自评表的所有操作日志

### 3. 操作日志数据模型

#### 数据库模型 (`backend/app/models/operation_log.py`)

```python
class OperationLog(Base):
    id: UUID
    operation_type: str  # 操作类型
    operator_id: UUID  # 操作人ID
    operator_name: str  # 操作人姓名
    operator_role: str  # 操作人角色
    target_id: UUID  # 目标对象ID
    target_type: str  # 目标对象类型
    details: JSON  # 操作详情
    operated_at: DateTime  # 操作时间
```

#### Pydantic模型 (`backend/app/schemas/operation_log.py`)

- `OperationLogResponse` - 操作日志响应模型
- `OperationLogListResponse` - 操作日志列表响应模型
- `OperationLogQueryParams` - 操作日志查询参数模型

### 4. 中间件集成 (`backend/app/main.py`)

- **attach_user_to_request** - 将当前用户附加到请求状态，供日志中间件使用
- **OperationLoggingMiddleware** - 自动记录操作日志

### 5. 手动日志记录

对于需要更精确控制的场景，提供了 `log_operation()` 辅助函数：

```python
from app.core.logging_middleware import log_operation

log_operation(
    db=db,
    operation_type="submit",
    operator_id=current_user.id,
    operator_name=current_user.name,
    operator_role=current_user.role,
    target_id=evaluation.id,
    target_type="self_evaluation",
    details={"action": "submit_and_lock"}
)
```

## 已更新的端点

以下端点已添加手动日志记录：

1. **backend/app/api/v1/endpoints/self_evaluation.py**
   - `submit_self_evaluation` - 表单提交日志
   - `trigger_ai_scoring` - AI评分触发日志

2. **backend/app/api/v1/endpoints/scoring.py**
   - `submit_manual_score` - 手动评分日志

3. **backend/app/api/v1/endpoints/review.py**
   - `handle_anomaly` - 异常处理日志（已存在）
   - `sync_to_president_office` - 数据同步日志（已存在）

4. **backend/app/api/v1/endpoints/president_office.py**
   - `approve_evaluation_results` - 审定日志（已存在）

5. **backend/app/api/v1/endpoints/publication.py**
   - `publish` - 公示日志（已存在）
   - `distribute` - 结果分发日志（已存在）

## 日志记录内容

每条操作日志包含以下信息（需求 17.8, 17.9）：

- **操作类型** (operation_type) - 标识操作的类型
- **操作人ID** (operator_id) - 执行操作的用户ID
- **操作人姓名** (operator_name) - 执行操作的用户姓名
- **操作人角色** (operator_role) - 执行操作的用户角色
- **目标对象ID** (target_id) - 操作的目标对象ID
- **目标对象类型** (target_type) - 操作的目标对象类型
- **操作详情** (details) - 包含操作的详细信息（JSON格式）
- **操作时间** (operated_at) - 操作发生的时间戳

## 使用示例

### 查询所有操作日志

```bash
GET /api/v1/logs?skip=0&limit=100
Authorization: Bearer <token>
```

### 按操作类型筛选

```bash
GET /api/v1/logs?operation_type=submit&skip=0&limit=50
Authorization: Bearer <token>
```

### 按时间范围筛选

```bash
GET /api/v1/logs?start_date=2024-01-01T00:00:00&end_date=2024-12-31T23:59:59
Authorization: Bearer <token>
```

### 查询特定自评表的所有操作

```bash
GET /api/v1/logs/by-evaluation/{evaluation_id}
Authorization: Bearer <token>
```

## 权限控制

- 所有认证用户都可以查询操作日志
- 使用 `require_any_role` 依赖确保用户已认证

## 错误处理

- 日志记录失败不会影响主要业务流程
- 所有日志记录错误都会被捕获并记录到应用日志中
- 中间件中的数据库错误会被优雅处理，不会中断请求

## 性能考虑

- 日志记录使用独立的数据库会话，不影响主业务事务
- 中间件只记录成功的操作（2xx状态码）
- 查询接口支持分页，避免一次性加载大量数据

## 测试

操作日志功能可以通过以下方式测试：

1. 执行任何关键操作（如提交自评表、触发AI评分等）
2. 调用日志查询API验证日志是否正确记录
3. 验证日志包含所有必要信息（操作人、操作时间、目标对象等）

## 需求覆盖

本实现覆盖了以下需求：

- ✅ 需求 17.1 - 表单提交时记录操作日志
- ✅ 需求 17.2 - AI评分时记录操作日志
- ✅ 需求 17.3 - 手动评分时记录操作日志
- ✅ 需求 17.4 - 异常处理时记录操作日志
- ✅ 需求 17.5 - 数据同步时记录操作日志
- ✅ 需求 17.6 - 审定时记录操作日志
- ✅ 需求 17.7 - 公示时记录操作日志
- ✅ 需求 17.8 - 操作日志包含操作人信息
- ✅ 需求 17.9 - 操作日志包含操作时间信息
- ✅ 需求 17.10 - 支持追溯每一步操作

## 未来改进

1. 添加日志归档功能，定期归档旧日志
2. 添加日志导出功能，支持导出为CSV或Excel
3. 添加日志统计功能，生成操作统计报表
4. 考虑使用消息队列异步记录日志，进一步提升性能
