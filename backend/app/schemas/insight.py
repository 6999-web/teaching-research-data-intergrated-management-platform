"""
感悟总结相关的Pydantic模型
"""

from pydantic import BaseModel, Field
from datetime import datetime
from uuid import UUID


class InsightSummaryResponse(BaseModel):
    """感悟总结响应模型"""
    id: UUID = Field(..., description="感悟总结ID")
    evaluation_id: UUID = Field(..., description="自评表ID")
    summary: str = Field(..., description="感悟总结内容")
    generated_at: datetime = Field(..., description="生成时间")

    class Config:
        from_attributes = True


class InsightSummaryGenerate(BaseModel):
    """生成感悟总结请求模型"""
    evaluation_id: UUID = Field(..., description="自评表ID")


class InsightSummaryGenerateResponse(BaseModel):
    """生成感悟总结响应模型"""
    insight_summary: InsightSummaryResponse = Field(..., description="生成的感悟总结")
    message: str = Field(..., description="操作消息")
