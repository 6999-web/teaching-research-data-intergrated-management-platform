# 全局错误处理使用指南

本文档说明任务 22.1 实现的全局错误处理机制的使用方法。

## 目录

1. [API调用失败重试机制](#1-api调用失败重试机制)
2. [文件上传断点续传](#2-文件上传断点续传)
3. [数据库连接池和自动重连](#3-数据库连接池和自动重连)
4. [并发冲突处理](#4-并发冲突处理)

---

## 1. API调用失败重试机制

### 功能说明

自动重试失败的外部API调用，使用指数退避策略，最多重试3次。

### 使用方法

#### 方法1: 使用装饰器

```python
from app.core.error_handling import retry_on_api_failure
import httpx

@retry_on_api_failure(max_attempts=3, min_wait=1, max_wait=10)
async def call_deepseek_api(prompt: str):
    """调用DeepSeek API（自动重试）"""
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.post(
            "https://api.deepseek.com/v1/chat/completions",
            headers={"Authorization": f"Bearer {api_key}"},
            json={"model": "deepseek-chat", "messages": [{"role": "user", "content": prompt}]}
        )
        response.raise_for_status()
        return response.json()
```

#### 方法2: 使用重试处理器

```python
from app.core.error_handling import APIRetryHandler
import httpx

async def call_external_service():
    async def api_call():
        async with httpx.AsyncClient() as client:
            response = await client.get("https://api.example.com/data")
            return response.json()
    
    # 自动重试，最多3次，超时30秒
    result = await APIRetryHandler.call_with_retry(
        api_call,
        max_attempts=3,
        timeout=30.0
    )
    return result
```

### 特性

- **自动重试**: 网络错误和超时自动重试
- **指数退避**: 重试间隔逐渐增加（1秒、2秒、4秒...）
- **最大重试次数**: 默认3次，可配置
- **友好错误**: 失败后返回用户友好的错误信息

---

## 2. 文件上传断点续传

### 功能说明

支持大文件分块上传和断点续传，网络中断后可以从断点继续上传。

### API端点

#### 2.1 初始化上传

```http
POST /api/chunked/upload/init
Content-Type: multipart/form-data

file_name: "large_file.pdf"
file_size: 104857600  # 100MB
evaluation_id: "uuid"
indicator: "teaching_reform_projects"
chunk_size: 5242880  # 5MB (可选)
```

**响应:**
```json
{
  "upload_id": "uuid",
  "total_chunks": 20,
  "chunk_size": 5242880,
  "status": "initialized"
}
```

#### 2.2 上传分块

```http
POST /api/chunked/upload/chunk
Content-Type: multipart/form-data

upload_id: "uuid"
chunk_index: 0
chunk: <binary data>
```

**响应:**
```json
{
  "upload_id": "uuid",
  "chunk_index": 0,
  "status": "in_progress",
  "progress": 0.05,
  "uploaded_chunks": 1,
  "total_chunks": 20
}
```

#### 2.3 查询上传状态（断点续传）

```http
GET /api/chunked/upload/status/{upload_id}
```

**响应:**
```json
{
  "upload_id": "uuid",
  "status": "in_progress",
  "file_name": "large_file.pdf",
  "file_size": 104857600,
  "total_chunks": 20,
  "uploaded_chunks": 15,
  "missing_chunks": [16, 17, 18, 19],
  "progress": 0.75
}
```

#### 2.4 完成上传

```http
POST /api/chunked/upload/complete
Content-Type: multipart/form-data

upload_id: "uuid"
evaluation_id: "uuid"
indicator: "teaching_reform_projects"
```

**响应:**
```json
{
  "attachment_id": "uuid",
  "file_name": "large_file.pdf",
  "file_size": 104857600,
  "status": "completed"
}
```

### 前端使用示例

```typescript
// 初始化上传
async function uploadLargeFile(file: File, evaluationId: string, indicator: string) {
  const CHUNK_SIZE = 5 * 1024 * 1024; // 5MB
  
  // 1. 初始化上传
  const initResponse = await fetch('/api/chunked/upload/init', {
    method: 'POST',
    body: new FormData({
      file_name: file.name,
      file_size: file.size,
      evaluation_id: evaluationId,
      indicator: indicator,
      chunk_size: CHUNK_SIZE
    })
  });
  
  const { upload_id, total_chunks } = await initResponse.json();
  
  // 2. 上传每个分块
  for (let i = 0; i < total_chunks; i++) {
    const start = i * CHUNK_SIZE;
    const end = Math.min(start + CHUNK_SIZE, file.size);
    const chunk = file.slice(start, end);
    
    try {
      await uploadChunk(upload_id, i, chunk);
    } catch (error) {
      // 网络错误，可以稍后重试
      console.error(`分块 ${i} 上传失败:`, error);
      // 保存 upload_id，稍后可以查询状态并续传
      localStorage.setItem('pending_upload', upload_id);
      throw error;
    }
  }
  
  // 3. 完成上传
  const completeResponse = await fetch('/api/chunked/upload/complete', {
    method: 'POST',
    body: new FormData({
      upload_id: upload_id,
      evaluation_id: evaluationId,
      indicator: indicator
    })
  });
  
  return await completeResponse.json();
}

// 断点续传
async function resumeUpload(uploadId: string, file: File) {
  // 查询上传状态
  const statusResponse = await fetch(`/api/chunked/upload/status/${uploadId}`);
  const { missing_chunks } = await statusResponse.json();
  
  // 只上传缺失的分块
  for (const chunkIndex of missing_chunks) {
    const start = chunkIndex * CHUNK_SIZE;
    const end = Math.min(start + CHUNK_SIZE, file.size);
    const chunk = file.slice(start, end);
    
    await uploadChunk(uploadId, chunkIndex, chunk);
  }
}
```

---

## 3. 数据库连接池和自动重连

### 功能说明

使用SQLAlchemy连接池管理数据库连接，自动处理连接失败和重连。

### 配置说明

在 `backend/app/db/base.py` 中已配置：

```python
engine = create_engine(
    settings.DATABASE_URL,
    poolclass=QueuePool,        # 使用队列连接池
    pool_size=20,                # 连接池大小：20个连接
    max_overflow=10,             # 最多额外创建10个连接
    pool_recycle=3600,           # 1小时后回收连接
    pool_pre_ping=True,          # 连接前ping，确保连接可用
    pool_timeout=30              # 连接超时：30秒
)
```

### 使用方法

#### 方法1: 使用装饰器（推荐）

```python
from app.core.error_handling import retry_on_db_error
from sqlalchemy.orm import Session

@retry_on_db_error(max_attempts=3)
def get_evaluation(db: Session, evaluation_id: UUID):
    """获取自评表（自动重试数据库错误）"""
    return db.query(SelfEvaluation).filter(
        SelfEvaluation.id == evaluation_id
    ).first()
```

#### 方法2: 手动检查连接

```python
from app.core.error_handling import DatabaseConnectionManager
from sqlalchemy.orm import Session

def safe_database_operation(db: Session):
    # 确保连接可用
    if not DatabaseConnectionManager.ensure_connection(db):
        raise Exception("无法连接到数据库")
    
    # 执行数据库操作
    result = db.query(SelfEvaluation).all()
    return result
```

### 特性

- **连接池**: 复用数据库连接，提高性能
- **自动重连**: 连接失败时自动重试
- **连接回收**: 定期回收长时间未使用的连接
- **连接检测**: 使用前ping连接，确保可用

---

## 4. 并发冲突处理

### 功能说明

提供乐观锁和悲观锁两种并发控制机制，防止数据冲突。

### 4.1 乐观锁（Optimistic Locking）

**适用场景**: 冲突较少的场景，如自评表编辑

**原理**: 使用版本号检测并发修改

#### 使用方法

```python
from app.core.error_handling import ConcurrencyControl, OptimisticLockError
from sqlalchemy.orm import Session

def update_evaluation_with_optimistic_lock(
    db: Session,
    evaluation_id: UUID,
    new_content: dict,
    expected_version: int
):
    """使用乐观锁更新自评表"""
    
    # 1. 获取记录
    evaluation = db.query(SelfEvaluation).filter(
        SelfEvaluation.id == evaluation_id
    ).first()
    
    if not evaluation:
        raise ValueError("自评表不存在")
    
    try:
        # 2. 检查版本号
        ConcurrencyControl.check_version(db, evaluation, expected_version)
        
        # 3. 更新数据
        evaluation.content = new_content
        evaluation.updated_at = datetime.utcnow()
        
        # 4. 增加版本号
        ConcurrencyControl.increment_version(evaluation)
        
        # 5. 提交事务
        db.commit()
        db.refresh(evaluation)
        
        return evaluation
        
    except OptimisticLockError as e:
        db.rollback()
        raise HTTPException(
            status_code=409,
            detail="数据已被其他用户修改，请刷新后重试"
        )
```

#### 前端使用示例

```typescript
// 前端需要保存版本号
interface Evaluation {
  id: string;
  content: any;
  version: number;  // 版本号
}

async function updateEvaluation(evaluation: Evaluation, newContent: any) {
  try {
    const response = await fetch(`/api/evaluations/${evaluation.id}`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        content: newContent,
        version: evaluation.version  // 发送当前版本号
      })
    });
    
    if (response.status === 409) {
      // 版本冲突，提示用户刷新
      alert('数据已被其他用户修改，请刷新后重试');
      return;
    }
    
    const updated = await response.json();
    // 更新本地版本号
    evaluation.version = updated.version;
    
  } catch (error) {
    console.error('更新失败:', error);
  }
}
```

### 4.2 悲观锁（Pessimistic Locking）

**适用场景**: 冲突频繁的场景，如最终得分确定

**原理**: 使用数据库行锁锁定记录

#### 使用方法

```python
from app.core.error_handling import ConcurrencyControl
from sqlalchemy.orm import Session

def determine_final_score_with_pessimistic_lock(
    db: Session,
    evaluation_id: UUID,
    final_score: float,
    summary: str,
    user_id: UUID
):
    """使用悲观锁确定最终得分"""
    
    try:
        # 开始事务
        with db.begin():
            # 1. 获取悲观锁（锁定记录）
            evaluation = ConcurrencyControl.acquire_pessimistic_lock(
                db, SelfEvaluation, evaluation_id
            )
            
            if not evaluation:
                raise ValueError("自评表不存在")
            
            # 2. 检查是否已有最终得分
            existing_score = db.query(FinalScore).filter(
                FinalScore.evaluation_id == evaluation_id
            ).first()
            
            if existing_score:
                raise ValueError("最终得分已确定，不可重复提交")
            
            # 3. 创建最终得分记录
            final_score_record = FinalScore(
                evaluation_id=evaluation_id,
                final_score=final_score,
                summary=summary,
                determined_by=user_id
            )
            
            db.add(final_score_record)
            
            # 4. 更新自评表状态
            evaluation.status = "finalized"
            
            # 5. 提交事务（自动释放锁）
            db.commit()
            
            return final_score_record
            
    except HTTPException:
        # 锁冲突，重新抛出
        raise
    except Exception as e:
        db.rollback()
        raise
```

### 乐观锁 vs 悲观锁

| 特性 | 乐观锁 | 悲观锁 |
|------|--------|--------|
| **适用场景** | 冲突少 | 冲突多 |
| **性能** | 高（无锁等待） | 低（需要等待锁） |
| **实现** | 版本号检测 | 数据库行锁 |
| **冲突处理** | 提交时检测 | 获取锁时阻塞 |
| **推荐使用** | 自评表编辑、附件上传 | 最终得分确定、公示操作 |

---

## 5. 综合使用示例

### 示例1: 带重试的AI评分服务

```python
from app.core.error_handling import retry_on_api_failure, retry_on_db_error
import httpx

class AIScoringService:
    
    @retry_on_api_failure(max_attempts=3)
    async def call_deepseek_api(self, prompt: str):
        """调用DeepSeek API（自动重试）"""
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                self.api_url,
                headers={"Authorization": f"Bearer {self.api_key}"},
                json={"model": "deepseek-chat", "messages": [{"role": "user", "content": prompt}]}
            )
            response.raise_for_status()
            return response.json()
    
    @retry_on_db_error(max_attempts=3)
    def save_ai_score(self, db: Session, score_data: dict):
        """保存AI评分结果（自动重试数据库错误）"""
        ai_score = AIScore(**score_data)
        db.add(ai_score)
        db.commit()
        db.refresh(ai_score)
        return ai_score
```

### 示例2: 带并发控制的最终得分确定

```python
from app.core.error_handling import ConcurrencyControl, retry_on_db_error

@retry_on_db_error(max_attempts=3)
def determine_final_score(
    db: Session,
    evaluation_id: UUID,
    final_score: float,
    summary: str,
    user_id: UUID
):
    """确定最终得分（悲观锁 + 数据库重试）"""
    
    with db.begin():
        # 使用悲观锁防止并发冲突
        evaluation = ConcurrencyControl.acquire_pessimistic_lock(
            db, SelfEvaluation, evaluation_id
        )
        
        # 创建最终得分记录
        final_score_record = FinalScore(
            evaluation_id=evaluation_id,
            final_score=final_score,
            summary=summary,
            determined_by=user_id
        )
        
        db.add(final_score_record)
        evaluation.status = "finalized"
        
        db.commit()
        
        return final_score_record
```

---

## 6. 错误处理最佳实践

### 6.1 API调用

✅ **推荐做法:**
```python
@retry_on_api_failure(max_attempts=3)
async def call_external_api():
    # API调用逻辑
    pass
```

❌ **不推荐做法:**
```python
async def call_external_api():
    # 手动实现重试逻辑（容易出错）
    for i in range(3):
        try:
            # API调用
            pass
        except:
            pass
```

### 6.2 数据库操作

✅ **推荐做法:**
```python
@retry_on_db_error(max_attempts=3)
def database_operation(db: Session):
    # 数据库操作
    pass
```

❌ **不推荐做法:**
```python
def database_operation(db: Session):
    # 不处理连接错误
    result = db.query(Model).all()
```

### 6.3 并发控制

✅ **推荐做法:**
```python
# 冲突少的场景使用乐观锁
ConcurrencyControl.check_version(db, obj, expected_version)
obj.field = new_value
ConcurrencyControl.increment_version(obj)
db.commit()

# 冲突多的场景使用悲观锁
obj = ConcurrencyControl.acquire_pessimistic_lock(db, Model, obj_id)
obj.field = new_value
db.commit()
```

❌ **不推荐做法:**
```python
# 不处理并发冲突
obj = db.query(Model).filter(Model.id == obj_id).first()
obj.field = new_value
db.commit()  # 可能覆盖其他用户的修改
```

---

## 7. 监控和日志

所有错误处理机制都会记录详细日志：

```python
import logging
logger = logging.getLogger(__name__)

# API重试日志
logger.warning(f"API调用失败（第{attempt}次尝试）: {str(e)}")

# 数据库重连日志
logger.info("尝试重新连接数据库...")

# 并发冲突日志
logger.warning(f"乐观锁冲突: 期望版本 {expected_version}, 当前版本 {current_version}")
```

建议在生产环境中配置日志聚合工具（如ELK、Grafana Loki）监控错误率。

---

## 8. 测试

### 单元测试示例

```python
import pytest
from app.core.error_handling import ConcurrencyControl, OptimisticLockError

def test_optimistic_lock_conflict(db_session):
    """测试乐观锁冲突检测"""
    
    # 创建测试数据
    evaluation = SelfEvaluation(content={}, version=1)
    db_session.add(evaluation)
    db_session.commit()
    
    # 模拟版本冲突
    with pytest.raises(OptimisticLockError):
        ConcurrencyControl.check_version(db_session, evaluation, expected_version=2)
```

---

## 总结

任务 22.1 实现的全局错误处理机制提供了：

1. ✅ **API调用失败重试机制**: 自动重试，指数退避
2. ✅ **文件上传断点续传**: 分块上传，支持续传
3. ✅ **数据库连接池和自动重连**: 连接池管理，自动重连
4. ✅ **并发冲突处理**: 乐观锁和悲观锁

这些机制大大提高了系统的稳定性和可靠性，确保在网络不稳定、数据库连接问题、并发访问等场景下系统仍能正常运行。
