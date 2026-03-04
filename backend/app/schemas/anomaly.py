"""
异常数据相关的Pydantic模型

用于管理端查询和处理异常数据
"""

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from uuid import UUID


class AnomalyResponse(BaseModel):
    """异常数据响应模型"""
    id: UUID = Field(..., description="异常数据ID")
    evaluation_id: UUID = Field(..., description="自评表ID")
    type: str = Field(..., description="异常类型: count_mismatch, missing_attachment, invalid_data")
    indicator: str = Field(..., description="考核指标")
    declared_count: Optional[int] = Field(None, description="自评表声明的数量")
    parsed_count: Optional[int] = Field(None, description="AI解析出的数量")
    description: str = Field(..., description="清晰的对比说明")
    status: str = Field(..., description="状态: pending, handled")
    handled_by: Optional[UUID] = Field(None, description="处理人ID")
    handled_action: Optional[str] = Field(None, description="处理动作: reject, correct")
    handled_at: Optional[datetime] = Field(None, description="处理时间")

    class Config:
        from_attributes = True


class AnomalyListResponse(BaseModel):
    """异常数据列表响应模型"""
    total: int = Field(..., description="异常数据总数")
    anomalies: list[AnomalyResponse] = Field(..., description="异常数据列表")


class HandleAnomalyRequest(BaseModel):
    """处理异常数据请求模型"""
    anomaly_id: UUID = Field(..., description="异常数据ID")
    action: str = Field(..., description="处理动作: reject (打回教研室), correct (直接修正)")
    corrected_data: Optional[dict] = Field(None, description="修正后的数据（如果action=correct）")
    reject_reason: Optional[str] = Field(None, description="打回原因（如果action=reject）")


class HandleAnomalyResponse(BaseModel):
    """处理异常数据响应模型"""
    anomaly_id: UUID = Field(..., description="异常数据ID")
    status: str = Field(..., description="处理后的状态")
    handled_at: datetime = Field(..., description="处理时间")
    message: str = Field(..., description="处理结果消息")
