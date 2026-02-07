"""
操作日志记录中间件

自动记录所有关键操作的日志，包括：
- 表单提交 (submit)
- AI评分 (ai_score)
- 手动评分 (manual_score)
- 异常处理 (handle_anomaly)
- 数据同步 (sync)
- 审定 (approve)
- 公示 (publish)
- 结果分发 (distribute)

需求: 17.1, 17.2, 17.3, 17.4, 17.5, 17.6, 17.7, 17.8, 17.9
"""

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp
from sqlalchemy.orm import Session
from typing import Callable, Optional
from uuid import UUID
import json
import logging
from datetime import datetime

from app.models.operation_log import OperationLog
from app.db.base import SessionLocal

logger = logging.getLogger(__name__)


# Define which endpoints should be logged and their operation types
LOGGED_OPERATIONS = {
    # 表单提交 - 需求 17.1
    "POST /api/v1/teaching-office/self-evaluation": "submit",
    "PUT /api/v1/teaching-office/self-evaluation/{evaluation_id}": "submit",
    "POST /api/v1/teaching-office/self-evaluation/{evaluation_id}/submit": "submit",
    
    # AI评分 - 需求 17.2
    "POST /api/v1/teaching-office/trigger-ai-scoring": "ai_score",
    
    # 手动评分 - 需求 17.3
    "POST /api/v1/scoring/manual-score": "manual_score",
    
    # 异常处理 - 需求 17.4
    "POST /api/v1/review/handle-anomaly": "handle_anomaly",
    
    # 数据同步 - 需求 17.5
    "POST /api/v1/review/sync-to-president-office": "sync",
    
    # 审定 - 需求 17.6
    "POST /api/v1/president-office/approve": "approve",
    
    # 公示 - 需求 17.7
    "POST /api/v1/publication/publish": "publish",
    
    # 结果分发 (distribute operation is logged in the endpoint itself)
    "POST /api/v1/publication/distribute": "distribute",
}


def extract_target_info(path: str, body: dict, response_body: dict) -> tuple[Optional[UUID], str]:
    """
    从请求路径、请求体和响应体中提取目标ID和目标类型
    
    Args:
        path: 请求路径
        body: 请求体
        response_body: 响应体
        
    Returns:
        (target_id, target_type) 元组
    """
    target_id = None
    target_type = "unknown"
    
    try:
        # 表单提交操作
        if "self-evaluation" in path:
            if "evaluation_id" in response_body:
                target_id = UUID(response_body["evaluation_id"])
            elif "evaluation_id" in body:
                target_id = UUID(body["evaluation_id"])
            target_type = "self_evaluation"
        
        # AI评分操作
        elif "trigger-ai-scoring" in path:
            if "scoring_task_id" in response_body:
                target_id = UUID(str(response_body["scoring_task_id"]))
            elif "evaluation_id" in body:
                target_id = UUID(body["evaluation_id"])
            target_type = "ai_scoring_task"
        
        # 手动评分操作
        elif "manual-score" in path:
            if "score_record_id" in response_body:
                target_id = UUID(str(response_body["score_record_id"]))
            elif "evaluation_id" in body:
                target_id = UUID(body["evaluation_id"])
            target_type = "manual_score"
        
        # 异常处理操作
        elif "handle-anomaly" in path:
            if "anomaly_id" in body:
                target_id = UUID(body["anomaly_id"])
            elif "anomaly_id" in response_body:
                target_id = UUID(str(response_body["anomaly_id"]))
            target_type = "anomaly"
        
        # 数据同步操作
        elif "sync-to-president-office" in path:
            if "sync_task_id" in response_body:
                target_id = UUID(str(response_body["sync_task_id"]))
            target_type = "sync_task"
        
        # 审定操作
        elif "approve" in path:
            if "approval_id" in response_body:
                target_id = UUID(str(response_body["approval_id"]))
            target_type = "approval"
        
        # 公示操作
        elif "publish" in path and "distribute" not in path:
            if "publication_id" in response_body:
                target_id = UUID(str(response_body["publication_id"]))
            target_type = "publication"
        
        # 结果分发操作
        elif "distribute" in path:
            if "publication_id" in body:
                target_id = UUID(body["publication_id"])
            target_type = "publication"
    
    except (ValueError, KeyError, TypeError) as e:
        logger.warning(f"Failed to extract target info from path {path}: {str(e)}")
    
    return target_id, target_type


def extract_user_info(request: Request) -> tuple[Optional[UUID], str, str]:
    """
    从请求中提取用户信息
    
    Args:
        request: FastAPI请求对象
        
    Returns:
        (user_id, user_name, user_role) 元组
    """
    user_id = None
    user_name = "Unknown"
    user_role = "unknown"
    
    try:
        # 从请求状态中获取当前用户（由认证中间件设置）
        if hasattr(request.state, "user"):
            user = request.state.user
            user_id = user.id
            user_name = user.name
            user_role = user.role
    except Exception as e:
        logger.warning(f"Failed to extract user info: {str(e)}")
    
    return user_id, user_name, user_role


class OperationLoggingMiddleware(BaseHTTPMiddleware):
    """
    操作日志记录中间件
    
    自动记录所有关键操作的日志，包括操作人和操作时间
    
    需求: 17.1-17.9
    """
    
    def __init__(self, app: ASGIApp):
        super().__init__(app)
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """
        处理请求并记录操作日志
        
        Args:
            request: 请求对象
            call_next: 下一个中间件或路由处理器
            
        Returns:
            响应对象
        """
        # 构建路径键（方法 + 路径）
        path = request.url.path
        method = request.method
        path_key = f"{method} {path}"
        
        # 检查是否需要记录此操作
        operation_type = None
        for pattern, op_type in LOGGED_OPERATIONS.items():
            # 简单的路径匹配（支持路径参数）
            pattern_parts = pattern.split("/")
            path_parts = path.split("/")
            
            if len(pattern_parts) == len(path_parts):
                match = True
                for pp, p in zip(pattern_parts, path_parts):
                    if pp.startswith("{") and pp.endswith("}"):
                        # 路径参数，跳过
                        continue
                    elif pp != p:
                        match = False
                        break
                
                if match and pattern.startswith(method):
                    operation_type = op_type
                    break
        
        # 如果不需要记录，直接处理请求
        if not operation_type:
            return await call_next(request)
        
        # 读取请求体（用于提取目标信息）
        request_body = {}
        try:
            if request.method in ["POST", "PUT", "PATCH"]:
                body_bytes = await request.body()
                if body_bytes:
                    request_body = json.loads(body_bytes.decode())
                
                # 重新设置请求体，以便后续处理器可以读取
                async def receive():
                    return {"type": "http.request", "body": body_bytes}
                request._receive = receive
        except Exception as e:
            logger.warning(f"Failed to read request body: {str(e)}")
        
        # 处理请求
        response = await call_next(request)
        
        # 只记录成功的操作（2xx状态码）
        if 200 <= response.status_code < 300:
            # 读取响应体
            response_body = {}
            try:
                # 注意：这里需要小心处理响应体，避免消耗流
                # 在实际生产环境中，可能需要更复杂的处理
                # 这里我们假设响应体已经在endpoint中设置了必要的信息
                pass
            except Exception as e:
                logger.warning(f"Failed to read response body: {str(e)}")
            
            # 提取用户信息
            user_id, user_name, user_role = extract_user_info(request)
            
            # 提取目标信息
            # 注意：由于我们无法轻易读取响应体，我们主要依赖请求体
            target_id, target_type = extract_target_info(path, request_body, response_body)
            
            # 如果无法提取target_id，使用请求体中的第一个UUID字段
            if not target_id:
                for key, value in request_body.items():
                    if isinstance(value, str):
                        try:
                            target_id = UUID(value)
                            break
                        except (ValueError, TypeError):
                            pass
            
            # 记录操作日志
            if user_id and target_id:
                try:
                    db = SessionLocal()
                    try:
                        operation_log = OperationLog(
                            operation_type=operation_type,
                            operator_id=user_id,
                            operator_name=user_name,
                            operator_role=user_role,
                            target_id=target_id,
                            target_type=target_type,
                            details={
                                "path": path,
                                "method": method,
                                "request_body": request_body,
                                "status_code": response.status_code,
                            }
                        )
                        db.add(operation_log)
                        db.commit()
                        
                        logger.info(
                            f"Operation logged: {operation_type} by {user_name} ({user_role}) "
                            f"on {target_type} {target_id}"
                        )
                    finally:
                        db.close()
                except Exception as e:
                    logger.error(f"Failed to log operation: {str(e)}")
        
        return response


def log_operation(
    db: Session,
    operation_type: str,
    operator_id: UUID,
    operator_name: str,
    operator_role: str,
    target_id: UUID,
    target_type: str,
    details: dict = None
) -> OperationLog:
    """
    手动记录操作日志的辅助函数
    
    用于在endpoint中直接记录操作日志，适用于需要更精确控制的场景
    
    Args:
        db: 数据库会话
        operation_type: 操作类型
        operator_id: 操作人ID
        operator_name: 操作人姓名
        operator_role: 操作人角色
        target_id: 目标对象ID
        target_type: 目标对象类型
        details: 操作详情
        
    Returns:
        创建的操作日志对象
        
    需求: 17.1-17.9
    """
    operation_log = OperationLog(
        operation_type=operation_type,
        operator_id=operator_id,
        operator_name=operator_name,
        operator_role=operator_role,
        target_id=target_id,
        target_type=target_type,
        details=details or {}
    )
    
    db.add(operation_log)
    db.commit()
    db.refresh(operation_log)
    
    logger.info(
        f"Operation logged: {operation_type} by {operator_name} ({operator_role}) "
        f"on {target_type} {target_id}"
    )
    
    return operation_log
