"""
数据同步相关的Schema定义

用于管理端向校长办公会端同步数据
"""

from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from uuid import UUID


class SyncToPresidentOfficeRequest(BaseModel):
    """上传至校长办公会的请求模型"""
    evaluation_ids: List[UUID] = Field(..., min_items=1, description="要同步的自评表ID列表")


class SyncToPresidentOfficeResponse(BaseModel):
    """上传至校长办公会的响应模型"""
    sync_task_id: UUID = Field(..., description="同步任务ID")
    status: str = Field(..., description="同步状态")
    synced_count: int = Field(..., description="成功同步的数量")
    failed_count: int = Field(0, description="失败的数量")
    message: str = Field(..., description="同步结果消息")
    synced_at: datetime = Field(..., description="同步时间")

    class Config:
        from_attributes = True


class EvaluationSyncData(BaseModel):
    """单个自评表的同步数据"""
    evaluation_id: UUID
    teaching_office_id: UUID
    teaching_office_name: str
    evaluation_year: int
    content: Dict[str, Any]
    status: str
    submitted_at: Optional[datetime]
    
    # AI评分数据
    ai_score: Optional[Dict[str, Any]] = None
    
    # 手动评分数据
    manual_scores: List[Dict[str, Any]] = Field(default_factory=list)
    
    # 最终得分
    final_score: Optional[Dict[str, Any]] = None
    
    # 附件信息
    attachments: List[Dict[str, Any]] = Field(default_factory=list)
    
    # 异常处理结果
    anomalies: List[Dict[str, Any]] = Field(default_factory=list)


class SyncDataPackage(BaseModel):
    """完整的同步数据包"""
    sync_task_id: UUID
    evaluations: List[EvaluationSyncData]
    total_count: int
    synced_at: datetime
    checksum: str = Field(..., description="数据完整性校验和")


class SyncStatusResponse(BaseModel):
    """同步状态查询响应"""
    sync_task_id: UUID
    status: str = Field(..., description="同步状态: pending, syncing, completed, failed")
    synced_count: int
    failed_count: int
    total_count: int
    started_at: datetime
    completed_at: Optional[datetime] = None
    error_message: Optional[str] = None

    class Config:
        from_attributes = True
