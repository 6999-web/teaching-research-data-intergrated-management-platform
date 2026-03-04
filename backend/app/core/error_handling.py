"""
全局错误处理模块

实现任务 22.1 的错误处理机制：
- API调用失败重试机制
- 文件上传断点续传
- 数据库连接池和自动重连
- 并发冲突处理（乐观锁和悲观锁）
"""

import logging
import functools
from typing import Callable, Any, Optional, Type, Tuple
from datetime import datetime
import httpx
from sqlalchemy.exc import OperationalError, IntegrityError, DBAPIError
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type,
    before_sleep_log,
    RetryError
)

logger = logging.getLogger(__name__)


# ============================================================================
# 1. API调用失败重试机制
# ============================================================================

def retry_on_api_failure(
    max_attempts: int = 3,
    min_wait: int = 1,
    max_wait: int = 10,
    exceptions: Tuple[Type[Exception], ...] = (httpx.HTTPError, httpx.TimeoutException)
):
    """
    API调用失败重试装饰器
    
    使用指数退避策略重试失败的API调用
    
    Args:
        max_attempts: 最大重试次数（默认3次）
        min_wait: 最小等待时间（秒，默认1秒）
        max_wait: 最大等待时间（秒，默认10秒）
        exceptions: 需要重试的异常类型
        
    Example:
        @retry_on_api_failure(max_attempts=3)
        async def call_external_api():
            async with httpx.AsyncClient() as client:
                response = await client.get("https://api.example.com")
                return response.json()
    """
    def decorator(func: Callable) -> Callable:
        @retry(
            stop=stop_after_attempt(max_attempts),
            wait=wait_exponential(multiplier=1, min=min_wait, max=max_wait),
            retry=retry_if_exception_type(exceptions),
            before_sleep=before_sleep_log(logger, logging.WARNING),
            reraise=True
        )
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            try:
                return await func(*args, **kwargs)
            except RetryError as e:
                logger.error(f"API调用失败，已重试{max_attempts}次: {str(e)}")
                raise HTTPException(
                    status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                    detail=f"外部服务暂时不可用，请稍后重试"
                )
        return wrapper
    return decorator


class APIRetryHandler:
    """
    API重试处理器
    
    提供更灵活的API调用重试机制
    """
    
    @staticmethod
    async def call_with_retry(
        func: Callable,
        *args,
        max_attempts: int = 3,
        timeout: float = 30.0,
        **kwargs
    ) -> Any:
        """
        执行带重试的API调用
        
        Args:
            func: 要调用的异步函数
            max_attempts: 最大重试次数
            timeout: 超时时间（秒）
            *args, **kwargs: 传递给func的参数
            
        Returns:
            API调用结果
            
        Raises:
            HTTPException: 如果所有重试都失败
        """
        last_exception = None
        
        for attempt in range(1, max_attempts + 1):
            try:
                logger.info(f"API调用尝试 {attempt}/{max_attempts}")
                
                # 调用函数（不自动添加timeout参数）
                result = await func(*args, **kwargs)
                logger.info(f"API调用成功（第{attempt}次尝试）")
                return result
                
            except (httpx.HTTPError, httpx.TimeoutException) as e:
                last_exception = e
                logger.warning(
                    f"API调用失败（第{attempt}次尝试）: {str(e)}"
                )
                
                if attempt < max_attempts:
                    # 指数退避
                    wait_time = min(2 ** (attempt - 1), 10)
                    logger.info(f"等待{wait_time}秒后重试...")
                    import asyncio
                    await asyncio.sleep(wait_time)
                else:
                    logger.error(f"API调用失败，已达到最大重试次数")
            
            except Exception as e:
                # 非网络错误，不重试
                logger.error(f"API调用发生非网络错误: {str(e)}")
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"API调用失败: {str(e)}"
                )
        
        # 所有重试都失败
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"外部服务暂时不可用: {str(last_exception)}"
        )


# ============================================================================
# 2. 文件上传断点续传支持
# ============================================================================

class ChunkedUploadManager:
    """
    分块上传管理器
    
    支持大文件的分块上传和断点续传
    """
    
    # 存储上传会话信息（生产环境应使用Redis等持久化存储）
    _upload_sessions = {}
    
    # 默认分块大小：5MB
    DEFAULT_CHUNK_SIZE = 5 * 1024 * 1024
    
    @classmethod
    def create_upload_session(
        cls,
        upload_id: str,
        file_name: str,
        file_size: int,
        total_chunks: int
    ) -> dict:
        """
        创建上传会话
        
        Args:
            upload_id: 上传唯一标识
            file_name: 文件名
            file_size: 文件总大小
            total_chunks: 总分块数
            
        Returns:
            上传会话信息
        """
        session = {
            "upload_id": upload_id,
            "file_name": file_name,
            "file_size": file_size,
            "total_chunks": total_chunks,
            "uploaded_chunks": set(),
            "created_at": datetime.utcnow(),
            "status": "in_progress"
        }
        
        cls._upload_sessions[upload_id] = session
        logger.info(f"创建上传会话: {upload_id}, 文件: {file_name}, 分块数: {total_chunks}")
        
        return session
    
    @classmethod
    def get_upload_session(cls, upload_id: str) -> Optional[dict]:
        """获取上传会话信息"""
        return cls._upload_sessions.get(upload_id)
    
    @classmethod
    def mark_chunk_uploaded(cls, upload_id: str, chunk_index: int) -> bool:
        """
        标记分块已上传
        
        Args:
            upload_id: 上传标识
            chunk_index: 分块索引
            
        Returns:
            是否所有分块都已上传
        """
        session = cls._upload_sessions.get(upload_id)
        if not session:
            logger.warning(f"上传会话不存在: {upload_id}")
            return False
        
        session["uploaded_chunks"].add(chunk_index)
        logger.info(
            f"分块上传完成: {upload_id}, "
            f"分块 {chunk_index + 1}/{session['total_chunks']}"
        )
        
        # 检查是否所有分块都已上传
        if len(session["uploaded_chunks"]) == session["total_chunks"]:
            session["status"] = "completed"
            logger.info(f"文件上传完成: {upload_id}")
            return True
        
        return False
    
    @classmethod
    def get_missing_chunks(cls, upload_id: str) -> list:
        """
        获取缺失的分块列表（用于断点续传）
        
        Args:
            upload_id: 上传标识
            
        Returns:
            缺失的分块索引列表
        """
        session = cls._upload_sessions.get(upload_id)
        if not session:
            return []
        
        all_chunks = set(range(session["total_chunks"]))
        uploaded_chunks = session["uploaded_chunks"]
        missing_chunks = list(all_chunks - uploaded_chunks)
        
        logger.info(
            f"上传会话 {upload_id} 缺失分块: {len(missing_chunks)}/{session['total_chunks']}"
        )
        
        return sorted(missing_chunks)
    
    @classmethod
    def cleanup_session(cls, upload_id: str):
        """清理上传会话"""
        if upload_id in cls._upload_sessions:
            del cls._upload_sessions[upload_id]
            logger.info(f"清理上传会话: {upload_id}")
    
    @classmethod
    def calculate_chunks(cls, file_size: int, chunk_size: int = None) -> int:
        """
        计算文件需要的分块数
        
        Args:
            file_size: 文件大小（字节）
            chunk_size: 分块大小（字节），默认5MB
            
        Returns:
            分块数量
        """
        if chunk_size is None:
            chunk_size = cls.DEFAULT_CHUNK_SIZE
        
        return (file_size + chunk_size - 1) // chunk_size


# ============================================================================
# 3. 数据库连接池和自动重连
# ============================================================================

def retry_on_db_error(max_attempts: int = 3):
    """
    数据库操作失败重试装饰器
    
    自动重试因连接问题导致的数据库操作失败
    
    Args:
        max_attempts: 最大重试次数
        
    Example:
        @retry_on_db_error(max_attempts=3)
        def get_user(db: Session, user_id: int):
            return db.query(User).filter(User.id == user_id).first()
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None
            
            for attempt in range(1, max_attempts + 1):
                try:
                    return func(*args, **kwargs)
                    
                except (OperationalError, DBAPIError) as e:
                    last_exception = e
                    logger.warning(
                        f"数据库操作失败（第{attempt}次尝试）: {str(e)}"
                    )
                    
                    # 如果是连接错误，尝试重新连接
                    if "connection" in str(e).lower() or "lost" in str(e).lower():
                        if attempt < max_attempts:
                            logger.info("尝试重新连接数据库...")
                            # 获取Session对象（假设第一个参数是db）
                            if args and hasattr(args[0], 'rollback'):
                                db = args[0]
                                try:
                                    db.rollback()
                                except:
                                    pass
                            
                            import time
                            time.sleep(2 ** (attempt - 1))  # 指数退避
                        else:
                            logger.error("数据库连接失败，已达到最大重试次数")
                            raise HTTPException(
                                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                                detail="数据库服务暂时不可用，请稍后重试"
                            )
                    else:
                        # 非连接错误，直接抛出
                        raise
                        
                except IntegrityError as e:
                    # 完整性约束错误，不重试
                    logger.error(f"数据完整性错误: {str(e)}")
                    raise HTTPException(
                        status_code=status.HTTP_409_CONFLICT,
                        detail="数据冲突，请检查输入"
                    )
                    
                except Exception as e:
                    # 其他错误，不重试
                    logger.error(f"数据库操作发生未预期错误: {str(e)}")
                    raise
            
            # 所有重试都失败
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=f"数据库操作失败: {str(last_exception)}"
            )
        
        return wrapper
    return decorator


class DatabaseConnectionManager:
    """
    数据库连接管理器
    
    提供连接池管理和自动重连功能
    """
    
    @staticmethod
    def test_connection(db: Session) -> bool:
        """
        测试数据库连接是否正常
        
        Args:
            db: 数据库会话
            
        Returns:
            连接是否正常
        """
        try:
            # 执行简单查询测试连接
            db.execute("SELECT 1")
            return True
        except Exception as e:
            logger.warning(f"数据库连接测试失败: {str(e)}")
            return False
    
    @staticmethod
    def ensure_connection(db: Session, max_retries: int = 3) -> bool:
        """
        确保数据库连接可用，必要时重新连接
        
        Args:
            db: 数据库会话
            max_retries: 最大重试次数
            
        Returns:
            连接是否成功建立
        """
        for attempt in range(1, max_retries + 1):
            if DatabaseConnectionManager.test_connection(db):
                return True
            
            logger.warning(f"数据库连接不可用，尝试重新连接（第{attempt}次）")
            
            try:
                db.rollback()
                db.close()
                # Session会在下次使用时自动重新连接
                return True
            except Exception as e:
                logger.error(f"重新连接失败: {str(e)}")
                
                if attempt < max_retries:
                    import time
                    time.sleep(2 ** (attempt - 1))
        
        return False


# ============================================================================
# 4. 并发冲突处理（乐观锁和悲观锁）
# ============================================================================

class OptimisticLockError(Exception):
    """乐观锁冲突异常"""
    pass


class ConcurrencyControl:
    """
    并发控制工具类
    
    提供乐观锁和悲观锁的实现
    """
    
    @staticmethod
    def check_version(db: Session, model_instance: Any, expected_version: int):
        """
        检查版本号（乐观锁）
        
        使用版本号防止并发更新冲突
        
        Args:
            db: 数据库会话
            model_instance: 模型实例
            expected_version: 期望的版本号
            
        Raises:
            OptimisticLockError: 如果版本号不匹配
            
        Example:
            # 在模型中添加version字段
            class MyModel(Base):
                version = Column(Integer, default=1, nullable=False)
            
            # 使用乐观锁
            obj = db.query(MyModel).filter(MyModel.id == obj_id).first()
            ConcurrencyControl.check_version(db, obj, expected_version=1)
            obj.some_field = new_value
            obj.version += 1
            db.commit()
        """
        if not hasattr(model_instance, 'version'):
            logger.warning(f"模型 {type(model_instance).__name__} 没有version字段，跳过版本检查")
            return
        
        current_version = model_instance.version
        
        if current_version != expected_version:
            logger.warning(
                f"乐观锁冲突: 期望版本 {expected_version}, "
                f"当前版本 {current_version}"
            )
            raise OptimisticLockError(
                f"数据已被其他用户修改，请刷新后重试"
            )
    
    @staticmethod
    def acquire_pessimistic_lock(
        db: Session,
        model_class: Type,
        record_id: Any,
        timeout: int = 10
    ) -> Optional[Any]:
        """
        获取悲观锁（行级锁）
        
        使用SELECT ... FOR UPDATE锁定记录，防止并发修改
        
        Args:
            db: 数据库会话
            model_class: 模型类
            record_id: 记录ID
            timeout: 锁超时时间（秒）
            
        Returns:
            锁定的记录，如果获取失败返回None
            
        Example:
            # 使用悲观锁
            with db.begin():
                obj = ConcurrencyControl.acquire_pessimistic_lock(
                    db, MyModel, obj_id
                )
                if obj:
                    obj.some_field = new_value
                    db.commit()
        """
        try:
            # 使用 FOR UPDATE 锁定记录
            # 其他事务必须等待此事务完成才能访问该记录
            record = db.query(model_class).filter(
                model_class.id == record_id
            ).with_for_update(nowait=False).first()
            
            if record:
                logger.info(f"成功获取悲观锁: {model_class.__name__} id={record_id}")
            else:
                logger.warning(f"记录不存在: {model_class.__name__} id={record_id}")
            
            return record
            
        except OperationalError as e:
            # 锁超时或死锁
            logger.error(f"获取悲观锁失败: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="资源正在被其他用户使用，请稍后重试"
            )
    
    @staticmethod
    def increment_version(model_instance: Any):
        """
        增加版本号（用于乐观锁）
        
        Args:
            model_instance: 模型实例
        """
        if hasattr(model_instance, 'version'):
            model_instance.version += 1
            logger.debug(f"版本号递增: {type(model_instance).__name__} version={model_instance.version}")


# ============================================================================
# 5. 全局异常处理器
# ============================================================================

class GlobalExceptionHandler:
    """
    全局异常处理器
    
    统一处理各类异常，返回友好的错误信息
    """
    
    @staticmethod
    def handle_database_error(e: Exception) -> HTTPException:
        """处理数据库错误"""
        if isinstance(e, IntegrityError):
            return HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="数据冲突，请检查输入"
            )
        elif isinstance(e, (OperationalError, DBAPIError)):
            return HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="数据库服务暂时不可用"
            )
        else:
            return HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"数据库操作失败: {str(e)}"
            )
    
    @staticmethod
    def handle_api_error(e: Exception) -> HTTPException:
        """处理API调用错误"""
        if isinstance(e, httpx.TimeoutException):
            return HTTPException(
                status_code=status.HTTP_504_GATEWAY_TIMEOUT,
                detail="外部服务响应超时"
            )
        elif isinstance(e, httpx.HTTPError):
            return HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="外部服务暂时不可用"
            )
        else:
            return HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"API调用失败: {str(e)}"
            )
    
    @staticmethod
    def handle_concurrency_error(e: Exception) -> HTTPException:
        """处理并发冲突错误"""
        if isinstance(e, OptimisticLockError):
            return HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=str(e)
            )
        else:
            return HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="并发操作冲突，请重试"
            )
