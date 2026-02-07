from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime
from uuid import UUID


class SelfEvaluationContent(BaseModel):
    """自评表内容结构"""
    teaching_process_management: str = Field(..., description="教学过程管理")
    course_construction: str = Field(..., description="课程建设")
    teaching_reform_projects: int = Field(..., ge=0, description="教学改革项目个数")
    honorary_awards: int = Field(..., ge=0, description="荣誉表彰个数")
    # 可以根据实际需求添加更多字段
    additional_fields: Optional[Dict[str, Any]] = Field(default=None, description="其他自评内容")


class SelfEvaluationCreate(BaseModel):
    """创建自评表请求模型"""
    teaching_office_id: UUID = Field(..., description="教研室ID")
    evaluation_year: int = Field(..., ge=2000, le=2100, description="考评年份")
    content: SelfEvaluationContent = Field(..., description="自评内容")


class SelfEvaluationUpdate(BaseModel):
    """更新自评表请求模型"""
    content: Optional[SelfEvaluationContent] = Field(None, description="自评内容")
    status: Optional[str] = Field(None, description="表单状态")


class SelfEvaluationResponse(BaseModel):
    """自评表响应模型"""
    id: UUID = Field(..., description="自评表ID")
    teaching_office_id: UUID = Field(..., description="教研室ID")
    evaluation_year: int = Field(..., description="考评年份")
    content: Dict[str, Any] = Field(..., description="自评内容")
    status: str = Field(..., description="表单状态: draft, submitted, locked, ai_scored, manually_scored, finalized, published")
    submitted_at: Optional[datetime] = Field(None, description="提交时间")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: datetime = Field(..., description="更新时间")

    class Config:
        from_attributes = True


class SelfEvaluationSaveResponse(BaseModel):
    """保存自评表响应模型"""
    evaluation_id: UUID = Field(..., description="自评表ID")
    status: str = Field(..., description="表单状态")
    created_at: datetime = Field(..., description="创建时间")


class SelfEvaluationSubmitResponse(BaseModel):
    """提交自评表响应模型"""
    evaluation_id: UUID = Field(..., description="自评表ID")
    status: str = Field(..., description="表单状态")
    submitted_at: datetime = Field(..., description="提交时间")
    message: str = Field(..., description="提交结果消息")


class SelfEvaluationUnlockResponse(BaseModel):
    """解锁自评表响应模型"""
    evaluation_id: UUID = Field(..., description="自评表ID")
    status: str = Field(..., description="表单状态")
    unlocked_at: datetime = Field(..., description="解锁时间")
    unlock_reason: Optional[str] = Field(None, description="解锁原因")
    message: str = Field(..., description="解锁结果消息")


class TriggerAIScoringRequest(BaseModel):
    """触发AI评分请求模型"""
    evaluation_id: UUID = Field(..., description="自评表ID")


class TriggerAIScoringResponse(BaseModel):
    """触发AI评分响应模型"""
    scoring_task_id: UUID = Field(..., description="评分任务ID")
    status: str = Field(..., description="任务状态: processing")
    message: str = Field(..., description="触发结果消息")

