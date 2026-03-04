"""
操作日志查询API端点

提供操作日志的查询和筛选功能

需求: 17.10
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from uuid import UUID
from datetime import datetime

from app.core.deps import get_db, require_any_role
from app.models.user import User
from app.models.operation_log import OperationLog
from app.schemas.operation_log import (
    OperationLogResponse,
    OperationLogListResponse,
    OperationLogQueryParams,
)

router = APIRouter()


@router.get("", response_model=OperationLogListResponse)
def get_operation_logs(
    operation_type: Optional[str] = Query(None, description="操作类型筛选"),
    operator_id: Optional[UUID] = Query(None, description="操作人ID筛选"),
    target_id: Optional[UUID] = Query(None, description="目标对象ID筛选"),
    target_type: Optional[str] = Query(None, description="目标对象类型筛选"),
    start_date: Optional[datetime] = Query(None, description="开始时间筛选"),
    end_date: Optional[datetime] = Query(None, description="结束时间筛选"),
    skip: int = Query(0, ge=0, description="跳过记录数"),
    limit: int = Query(100, ge=1, le=1000, description="返回记录数"),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_any_role)
):
    """
    查询操作日志 (Query operation logs).
    
    需求: 17.10
    
    - 支持按操作类型筛选
    - 支持按操作人筛选
    - 支持按时间范围筛选
    - 支持按目标对象筛选
    - 支持分页
    - 所有认证用户都可以查询日志
    """
    # 构建查询
    query = db.query(OperationLog)
    
    # 应用筛选条件
    if operation_type:
        query = query.filter(OperationLog.operation_type == operation_type)
    
    if operator_id:
        query = query.filter(OperationLog.operator_id == operator_id)
    
    if target_id:
        query = query.filter(OperationLog.target_id == target_id)
    
    if target_type:
        query = query.filter(OperationLog.target_type == target_type)
    
    if start_date:
        query = query.filter(OperationLog.operated_at >= start_date)
    
    if end_date:
        query = query.filter(OperationLog.operated_at <= end_date)
    
    # 获取总数
    total = query.count()
    
    # 应用分页和排序
    logs = query.order_by(
        OperationLog.operated_at.desc()
    ).offset(skip).limit(limit).all()
    
    # 转换为响应模型
    log_responses = [
        OperationLogResponse(
            id=log.id,
            operation_type=log.operation_type,
            operator_id=log.operator_id,
            operator_name=log.operator_name,
            operator_role=log.operator_role,
            target_id=log.target_id,
            target_type=log.target_type,
            details=log.details,
            operated_at=log.operated_at
        )
        for log in logs
    ]
    
    return OperationLogListResponse(
        total=total,
        skip=skip,
        limit=limit,
        logs=log_responses
    )


@router.get("/{log_id}", response_model=OperationLogResponse)
def get_operation_log_detail(
    log_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_any_role)
):
    """
    查询单个操作日志详情 (Get operation log detail).
    
    需求: 17.10
    
    - 返回完整的操作日志信息
    - 所有认证用户都可以查询
    """
    log = db.query(OperationLog).filter(OperationLog.id == log_id).first()
    
    if not log:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Operation log with id {log_id} not found"
        )
    
    return OperationLogResponse(
        id=log.id,
        operation_type=log.operation_type,
        operator_id=log.operator_id,
        operator_name=log.operator_name,
        operator_role=log.operator_role,
        target_id=log.target_id,
        target_type=log.target_type,
        details=log.details,
        operated_at=log.operated_at
    )


@router.get("/by-evaluation/{evaluation_id}", response_model=OperationLogListResponse)
def get_logs_by_evaluation(
    evaluation_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_any_role)
):
    """
    查询特定自评表的所有操作日志 (Get all logs for a specific evaluation).
    
    需求: 17.10
    
    - 返回与指定自评表相关的所有操作日志
    - 按时间倒序排列
    - 所有认证用户都可以查询
    """
    # 查询直接针对该自评表的日志
    logs = db.query(OperationLog).filter(
        OperationLog.target_id == evaluation_id
    ).order_by(OperationLog.operated_at.desc()).all()
    
    # 转换为响应模型
    log_responses = [
        OperationLogResponse(
            id=log.id,
            operation_type=log.operation_type,
            operator_id=log.operator_id,
            operator_name=log.operator_name,
            operator_role=log.operator_role,
            target_id=log.target_id,
            target_type=log.target_type,
            details=log.details,
            operated_at=log.operated_at
        )
        for log in logs
    ]
    
    return OperationLogListResponse(
        total=len(log_responses),
        skip=0,
        limit=len(log_responses),
        logs=log_responses
    )
