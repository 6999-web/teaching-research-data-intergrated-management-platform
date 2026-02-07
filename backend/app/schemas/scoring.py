from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
from uuid import UUID


class IndicatorScore(BaseModel):
    """Individual indicator score."""
    indicator: str = Field(..., description="考核指标名称")
    score: float = Field(..., ge=0, description="该指标得分")
    comment: str = Field(..., description="评分说明")


class ManualScoreCreate(BaseModel):
    """Request model for submitting manual score."""
    evaluation_id: UUID = Field(..., description="自评表ID")
    scores: List[IndicatorScore] = Field(..., min_items=1, description="各指标评分")


class ManualScoreResponse(BaseModel):
    """Response model for manual score submission."""
    score_record_id: UUID = Field(..., description="评分记录ID")
    submitted_at: datetime = Field(..., description="提交时间")

    class Config:
        from_attributes = True


class ManualScoreDetail(BaseModel):
    """Detailed manual score information."""
    id: UUID
    evaluation_id: UUID
    reviewer_id: UUID
    reviewer_name: str
    reviewer_role: str
    weight: float
    scores: List[IndicatorScore]
    submitted_at: datetime

    class Config:
        from_attributes = True


class AIScoreDetail(BaseModel):
    """AI score information."""
    id: UUID
    evaluation_id: UUID
    total_score: float
    indicator_scores: List[dict]
    parsed_reform_projects: int
    parsed_honorary_awards: int
    scored_at: datetime

    class Config:
        from_attributes = True


class FinalScoreDetail(BaseModel):
    """Final score information."""
    id: UUID
    evaluation_id: UUID
    final_score: float
    summary: Optional[str]
    determined_by: UUID
    determined_at: datetime

    class Config:
        from_attributes = True


class AllScoresResponse(BaseModel):
    """Response model for all scores of an evaluation."""
    evaluation_id: UUID
    ai_score: Optional[AIScoreDetail] = Field(None, description="AI评分结果")
    manual_scores: List[ManualScoreDetail] = Field(default_factory=list, description="所有评审人打分记录")
    final_score: Optional[FinalScoreDetail] = Field(None, description="最终得分")

    class Config:
        from_attributes = True


class FinalScoreCreate(BaseModel):
    """Request model for determining final score."""
    evaluation_id: UUID = Field(..., description="自评表ID")
    final_score: float = Field(..., ge=0, description="最终得分")
    summary: str = Field(..., min_length=1, description="汇总说明")


class FinalScoreResponse(BaseModel):
    """Response model for final score determination."""
    final_score_id: UUID = Field(..., description="最终得分记录ID")
    status: str = Field(..., description="状态")

    class Config:
        from_attributes = True


class ScoringAuditRecord(BaseModel):
    """Audit record for scoring."""
    id: UUID
    evaluation_id: UUID
    teaching_office_id: UUID
    teaching_office_name: str
    evaluation_year: int
    score_type: str = Field(..., description="评分类型: ai_score, manual_score, final_score")
    score_value: Optional[float] = Field(None, description="分数值")
    reviewer_id: Optional[UUID] = Field(None, description="评审人ID (仅手动评分)")
    reviewer_name: Optional[str] = Field(None, description="评审人姓名 (仅手动评分)")
    reviewer_role: Optional[str] = Field(None, description="评审人角色 (仅手动评分)")
    created_at: datetime = Field(..., description="创建时间")

    class Config:
        from_attributes = True


class ScoringAuditResponse(BaseModel):
    """Response model for scoring audit query."""
    total_count: int = Field(..., description="总记录数")
    records: List[ScoringAuditRecord] = Field(..., description="审计记录列表")

    class Config:
        from_attributes = True
