"""
测试全局错误处理功能

任务 22.1: 测试API重试、数据库重连、并发控制等功能
"""

import pytest
import asyncio
from unittest.mock import Mock, patch, AsyncMock
from sqlalchemy.exc import OperationalError, IntegrityError
import httpx

from app.core.error_handling import (
    APIRetryHandler,
    ChunkedUploadManager,
    DatabaseConnectionManager,
    ConcurrencyControl,
    OptimisticLockError,
    retry_on_api_failure,
    retry_on_db_error
)
from app.models.self_evaluation import SelfEvaluation
from app.models.final_score import FinalScore


# ============================================================================
# 1. API重试机制测试
# ============================================================================

@pytest.mark.asyncio
async def test_api_retry_success_on_first_attempt():
    """测试API调用第一次就成功"""
    
    async def successful_api_call():
        return {"status": "success"}
    
    result = await APIRetryHandler.call_with_retry(successful_api_call)
    
    assert result == {"status": "success"}


@pytest.mark.asyncio
async def test_api_retry_success_after_failures():
    """测试API调用失败后重试成功"""
    
    call_count = 0
    
    async def flaky_api_call():
        nonlocal call_count
        call_count += 1
        
        if call_count < 3:
            raise httpx.HTTPError("Network error")
        
        return {"status": "success"}
    
    result = await APIRetryHandler.call_with_retry(
        flaky_api_call,
        max_attempts=3
    )
    
    assert result == {"status": "success"}
    assert call_count == 3


@pytest.mark.asyncio
async def test_api_retry_all_attempts_fail():
    """测试API调用所有重试都失败"""
    
    async def failing_api_call():
        raise httpx.HTTPError("Network error")
    
    with pytest.raises(Exception) as exc_info:
        await APIRetryHandler.call_with_retry(
            failing_api_call,
            max_attempts=3
        )
    
    assert "暂时不可用" in str(exc_info.value)


@pytest.mark.asyncio
async def test_retry_decorator():
    """测试重试装饰器"""
    
    call_count = 0
    
    @retry_on_api_failure(max_attempts=3)
    async def decorated_api_call():
        nonlocal call_count
        call_count += 1
        
        if call_count < 2:
            raise httpx.TimeoutException("Timeout")
        
        return {"status": "success"}
    
    result = await decorated_api_call()
    
    assert result == {"status": "success"}
    assert call_count == 2


# ============================================================================
# 2. 分块上传测试
# ============================================================================

def test_calculate_chunks():
    """测试分块数量计算"""
    
    # 10MB文件，5MB分块 = 2块
    chunks = ChunkedUploadManager.calculate_chunks(
        file_size=10 * 1024 * 1024,
        chunk_size=5 * 1024 * 1024
    )
    assert chunks == 2
    
    # 11MB文件，5MB分块 = 3块
    chunks = ChunkedUploadManager.calculate_chunks(
        file_size=11 * 1024 * 1024,
        chunk_size=5 * 1024 * 1024
    )
    assert chunks == 3


def test_create_upload_session():
    """测试创建上传会话"""
    
    session = ChunkedUploadManager.create_upload_session(
        upload_id="test-upload-1",
        file_name="test.pdf",
        file_size=10485760,
        total_chunks=2
    )
    
    assert session["upload_id"] == "test-upload-1"
    assert session["file_name"] == "test.pdf"
    assert session["total_chunks"] == 2
    assert session["status"] == "in_progress"
    assert len(session["uploaded_chunks"]) == 0


def test_mark_chunk_uploaded():
    """测试标记分块已上传"""
    
    # 创建会话
    ChunkedUploadManager.create_upload_session(
        upload_id="test-upload-2",
        file_name="test.pdf",
        file_size=10485760,
        total_chunks=3
    )
    
    # 上传第一个分块
    is_complete = ChunkedUploadManager.mark_chunk_uploaded("test-upload-2", 0)
    assert not is_complete
    
    # 上传第二个分块
    is_complete = ChunkedUploadManager.mark_chunk_uploaded("test-upload-2", 1)
    assert not is_complete
    
    # 上传第三个分块
    is_complete = ChunkedUploadManager.mark_chunk_uploaded("test-upload-2", 2)
    assert is_complete
    
    # 检查会话状态
    session = ChunkedUploadManager.get_upload_session("test-upload-2")
    assert session["status"] == "completed"


def test_get_missing_chunks():
    """测试获取缺失分块（断点续传）"""
    
    # 创建会话
    ChunkedUploadManager.create_upload_session(
        upload_id="test-upload-3",
        file_name="test.pdf",
        file_size=10485760,
        total_chunks=5
    )
    
    # 上传部分分块
    ChunkedUploadManager.mark_chunk_uploaded("test-upload-3", 0)
    ChunkedUploadManager.mark_chunk_uploaded("test-upload-3", 2)
    ChunkedUploadManager.mark_chunk_uploaded("test-upload-3", 4)
    
    # 获取缺失分块
    missing = ChunkedUploadManager.get_missing_chunks("test-upload-3")
    
    assert missing == [1, 3]


def test_cleanup_session():
    """测试清理上传会话"""
    
    # 创建会话
    ChunkedUploadManager.create_upload_session(
        upload_id="test-upload-4",
        file_name="test.pdf",
        file_size=10485760,
        total_chunks=2
    )
    
    # 确认会话存在
    session = ChunkedUploadManager.get_upload_session("test-upload-4")
    assert session is not None
    
    # 清理会话
    ChunkedUploadManager.cleanup_session("test-upload-4")
    
    # 确认会话已删除
    session = ChunkedUploadManager.get_upload_session("test-upload-4")
    assert session is None


# ============================================================================
# 3. 数据库连接测试
# ============================================================================

def test_database_connection_test(db):
    """测试数据库连接检测"""
    
    # 正常连接应该返回True
    is_connected = DatabaseConnectionManager.test_connection(db)
    assert is_connected


def test_retry_on_db_error_decorator(db):
    """测试数据库重试装饰器"""
    
    call_count = 0
    
    @retry_on_db_error(max_attempts=3)
    def flaky_db_operation(db):
        nonlocal call_count
        call_count += 1
        
        if call_count < 2:
            raise OperationalError("Connection lost", None, None)
        
        return "success"
    
    result = flaky_db_operation(db)
    
    assert result == "success"
    assert call_count == 2


def test_retry_on_db_error_integrity_error(db):
    """测试数据库完整性错误不重试"""
    
    @retry_on_db_error(max_attempts=3)
    def db_operation_with_integrity_error(db):
        raise IntegrityError("Duplicate key", None, None)
    
    with pytest.raises(Exception) as exc_info:
        db_operation_with_integrity_error(db)
    
    assert "冲突" in str(exc_info.value)


# ============================================================================
# 4. 并发控制测试
# ============================================================================

def test_optimistic_lock_version_check_success(db):
    """测试乐观锁版本检查成功"""
    
    # 创建测试数据
    evaluation = SelfEvaluation(
        teaching_office_id="00000000-0000-0000-0000-000000000001",
        evaluation_year=2024,
        content={"test": "data"},
        status="draft",
        version=1
    )
    db.add(evaluation)
    db.commit()
    
    # 版本号匹配，应该成功
    ConcurrencyControl.check_version(db, evaluation, expected_version=1)


def test_optimistic_lock_version_conflict(db):
    """测试乐观锁版本冲突"""
    
    # 创建测试数据
    evaluation = SelfEvaluation(
        teaching_office_id="00000000-0000-0000-0000-000000000001",
        evaluation_year=2024,
        content={"test": "data"},
        status="draft",
        version=2
    )
    db.add(evaluation)
    db.commit()
    
    # 版本号不匹配，应该抛出异常
    with pytest.raises(OptimisticLockError) as exc_info:
        ConcurrencyControl.check_version(db, evaluation, expected_version=1)
    
    assert "已被其他用户修改" in str(exc_info.value)


def test_increment_version(db):
    """测试版本号递增"""
    
    # 创建测试数据
    evaluation = SelfEvaluation(
        teaching_office_id="00000000-0000-0000-0000-000000000001",
        evaluation_year=2024,
        content={"test": "data"},
        status="draft",
        version=1
    )
    db.add(evaluation)
    db.commit()
    
    # 递增版本号
    ConcurrencyControl.increment_version(evaluation)
    
    assert evaluation.version == 2


def test_pessimistic_lock_acquire(db):
    """测试悲观锁获取"""
    
    # 创建测试数据
    evaluation = SelfEvaluation(
        teaching_office_id="00000000-0000-0000-0000-000000000001",
        evaluation_year=2024,
        content={"test": "data"},
        status="draft",
        version=1
    )
    db.add(evaluation)
    db.commit()
    
    # 获取悲观锁
    locked_evaluation = ConcurrencyControl.acquire_pessimistic_lock(
        db,
        SelfEvaluation,
        evaluation.id
    )
    
    assert locked_evaluation is not None
    assert locked_evaluation.id == evaluation.id


def test_pessimistic_lock_nonexistent_record(db):
    """测试悲观锁获取不存在的记录"""
    
    from uuid import uuid4
    
    # 尝试锁定不存在的记录
    locked_evaluation = ConcurrencyControl.acquire_pessimistic_lock(
        db,
        SelfEvaluation,
        uuid4()
    )
    
    assert locked_evaluation is None


# ============================================================================
# 5. 综合场景测试
# ============================================================================

def test_concurrent_update_with_optimistic_lock(db):
    """测试使用乐观锁的并发更新场景"""
    
    # 创建测试数据
    evaluation = SelfEvaluation(
        teaching_office_id="00000000-0000-0000-0000-000000000001",
        evaluation_year=2024,
        content={"score": 80},
        status="draft",
        version=1
    )
    db.add(evaluation)
    db.commit()
    
    # 模拟用户A读取数据
    user_a_version = evaluation.version
    
    # 模拟用户B更新数据
    ConcurrencyControl.check_version(db, evaluation, expected_version=1)
    evaluation.content = {"score": 85}
    ConcurrencyControl.increment_version(evaluation)
    db.commit()
    
    # 刷新数据
    db.refresh(evaluation)
    
    # 用户A尝试更新（应该失败）
    with pytest.raises(OptimisticLockError):
        ConcurrencyControl.check_version(db, evaluation, expected_version=user_a_version)


def test_final_score_with_pessimistic_lock(db):
    """测试使用悲观锁确定最终得分"""
    
    from uuid import uuid4
    
    # 创建测试数据
    evaluation = SelfEvaluation(
        teaching_office_id="00000000-0000-0000-0000-000000000001",
        evaluation_year=2024,
        content={"test": "data"},
        status="manually_scored",
        version=1
    )
    db.add(evaluation)
    db.commit()
    
    # 使用悲观锁确定最终得分
    with db.begin_nested():
        locked_evaluation = ConcurrencyControl.acquire_pessimistic_lock(
            db,
            SelfEvaluation,
            evaluation.id
        )
        
        assert locked_evaluation is not None
        
        # 创建最终得分
        final_score = FinalScore(
            evaluation_id=evaluation.id,
            final_score=88.5,
            summary="综合评分",
            determined_by=uuid4(),
            version=1
        )
        
        db.add(final_score)
        locked_evaluation.status = "finalized"
        
        db.commit()
    
    # 验证结果
    db.refresh(evaluation)
    assert evaluation.status == "finalized"


# ============================================================================
# 6. 边界条件测试
# ============================================================================

def test_chunked_upload_zero_size_file():
    """测试零大小文件的分块计算"""
    
    chunks = ChunkedUploadManager.calculate_chunks(file_size=0)
    assert chunks == 0


def test_chunked_upload_single_byte_file():
    """测试单字节文件的分块计算"""
    
    chunks = ChunkedUploadManager.calculate_chunks(
        file_size=1,
        chunk_size=5 * 1024 * 1024
    )
    assert chunks == 1


def test_version_check_without_version_field(db):
    """测试没有version字段的模型"""
    
    # 创建一个没有version字段的mock对象
    mock_obj = Mock()
    del mock_obj.version  # 删除version属性
    
    # 应该不抛出异常，只是警告
    ConcurrencyControl.check_version(db, mock_obj, expected_version=1)


def test_increment_version_without_version_field():
    """测试对没有version字段的对象递增版本"""
    
    mock_obj = Mock()
    del mock_obj.version
    
    # 应该不抛出异常
    ConcurrencyControl.increment_version(mock_obj)
