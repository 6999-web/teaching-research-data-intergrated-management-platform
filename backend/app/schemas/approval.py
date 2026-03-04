"""
审定相关的Pydantic模型
"""

from pydantic import BaseModel, Field
from typing import List, Optional
from uuid import UUID
from datetime import datetime


class ApprovalRequest(BaseModel):
    """
    审定请求模型
    
    需求: 12.1, 12.2, 12.3, 12.6
    """
    evaluation_ids: List[UUID] = Field(..., description="待审定的评估ID列表")
    decision: str = Field(..., description="审定决定: 'approve' 或 'reject'")
    reject_reason: Optional[str] = Field(None, description="驳回原因（当decision为reject时必填）")
    
    class Config:
        json_schema_extra = {
            "example": {
                "evaluation_ids": ["123e4567-e89b-12d3-a456-426614174000"],
                "decision": "approve"
            }
        }


class ApprovalResponse(BaseModel):
    """
    审定响应模型
    
    需求: 12.4, 12.5, 12.7
    """
    approval_id: UUID = Field(..., description="审定记录ID")
    decision: str = Field(..., description="审定决定")
    approved_at: datetime = Field(..., description="审定时间")
    message: str = Field(..., description="操作结果消息")
    synced_to_management: bool = Field(..., description="是否已同步至管理端")
    
    class Config:
        json_schema_extra = {
            "example": {
                "approval_id": "123e4567-e89b-12d3-a456-426614174000",
                "decision": "approve",
                "approved_at": "2024-01-01T12:00:00",
                "message": "Approval successful. Management office can now initiate publication.",
                "synced_to_management": True
            }
        }


class ApprovalDetail(BaseModel):
    """
    审定详情模型
    """
    id: UUID
    evaluation_ids: List[UUID]
    decision: str
    reject_reason: Optional[str]
    approved_by: UUID
    approved_at: datetime
    
    class Config:
        from_attributes = True
