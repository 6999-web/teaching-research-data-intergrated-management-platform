"""
公示相关的Pydantic模型
"""

from pydantic import BaseModel, Field
from typing import List, Optional
from uuid import UUID
from datetime import datetime


class PublishRequest(BaseModel):
    """
    发起公示请求模型
    
    需求: 13.1, 13.2, 13.3, 13.4
    """
    evaluation_ids: List[UUID] = Field(..., description="待公示的评估ID列表")
    
    class Config:
        json_schema_extra = {
            "example": {
                "evaluation_ids": ["123e4567-e89b-12d3-a456-426614174000"]
            }
        }


class PublishResponse(BaseModel):
    """
    发起公示响应模型
    
    需求: 13.4
    """
    publication_id: UUID = Field(..., description="公示记录ID")
    published_at: datetime = Field(..., description="公示时间")
    message: str = Field(..., description="操作结果消息")
    
    class Config:
        json_schema_extra = {
            "example": {
                "publication_id": "123e4567-e89b-12d3-a456-426614174000",
                "published_at": "2024-01-01T12:00:00",
                "message": "Publication initiated successfully."
            }
        }


class PublicationDetail(BaseModel):
    """
    公示详情模型
    """
    id: UUID
    evaluation_ids: List[UUID]
    published_by: UUID
    published_at: datetime
    distributed_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class DistributeRequest(BaseModel):
    """
    结果分发请求模型
    
    需求: 14.1, 14.2
    """
    publication_id: UUID = Field(..., description="公示记录ID")
    
    class Config:
        json_schema_extra = {
            "example": {
                "publication_id": "123e4567-e89b-12d3-a456-426614174000"
            }
        }


class DistributeResponse(BaseModel):
    """
    结果分发响应模型
    
    需求: 14.1, 14.2
    """
    distributed_count: int = Field(..., description="分发的评估数量")
    distributed_at: datetime = Field(..., description="分发时间")
    message: str = Field(..., description="操作结果消息")
    
    class Config:
        json_schema_extra = {
            "example": {
                "distributed_count": 5,
                "distributed_at": "2024-01-01T12:00:00",
                "message": "Results distributed successfully to management and teaching offices."
            }
        }
