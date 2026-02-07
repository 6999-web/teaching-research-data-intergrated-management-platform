"""
操作日志相关的Pydantic模型

用于API请求和响应的数据验证
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from uuid import UUID
from datetime import datetime


class OperationLogResponse(BaseModel):
    """
    操作日志响应模型
    """
    id: UUID = Field(..., description="日志ID")
    operation_type: str = Field(..., description="操作类型")
    operator_id: UUID = Field(..., description="操作人ID")
    operator_name: str = Field(..., description="操作人姓名")
    operator_role: str = Field(..., description="操作人角色")
    target_id: UUID = Field(..., description="目标对象ID")
    target_type: str = Field(..., description="目标对象类型")
    details: Optional[Dict[str, Any]] = Field(None, description="操作详情")
    operated_at: datetime = Field(..., description="操作时间")
    
    class Config:
        from_attributes = True


class OperationLogListResponse(BaseModel):
    """
    操作日志列表响应模型
    """
    total: int = Field(..., description="总记录数")
    skip: int = Field(..., description="跳过记录数")
    limit: int = Field(..., description="返回记录数")
    logs: List[OperationLogResponse] = Field(..., description="日志列表")


class OperationLogQueryParams(BaseModel):
    """
    操作日志查询参数模型
    """
    operation_type: Optional[str] = Field(None, description="操作类型筛选")
    operator_id: Optional[UUID] = Field(None, description="操作人ID筛选")
    target_id: Optional[UUID] = Field(None, description="目标对象ID筛选")
    target_type: Optional[str] = Field(None, description="目标对象类型筛选")
    start_date: Optional[datetime] = Field(None, description="开始时间筛选")
    end_date: Optional[datetime] = Field(None, description="结束时间筛选")
    skip: int = Field(0, ge=0, description="跳过记录数")
    limit: int = Field(100, ge=1, le=1000, description="返回记录数")
