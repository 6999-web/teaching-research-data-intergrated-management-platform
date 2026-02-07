from datetime import datetime
from uuid import UUID
from typing import Optional, List
from pydantic import BaseModel, Field

from app.models.improvement_plan import ImprovementPlanStatus


class ImprovementPlanBase(BaseModel):
    indicator_item_id: int
    target: str
    measures: str
    deadline: datetime


class ImprovementPlanCreate(ImprovementPlanBase):
    evaluation_id: UUID
    charger_id: UUID


class ImprovementPlanUpdate(BaseModel):
    target: Optional[str] = None
    measures: Optional[str] = None
    deadline: Optional[datetime] = None
    charger_id: Optional[UUID] = None


class ImprovementPlanReview(BaseModel):
    status: ImprovementPlanStatus
    supervisor_comment: Optional[str] = None

class ImprovementPlanResponse(ImprovementPlanBase):
    id: UUID
    evaluation_id: UUID
    charger_id: UUID
    status: ImprovementPlanStatus
    supervisor_comment: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ImprovementPlanList(BaseModel):
    evaluation_id: UUID
    plans: List[ImprovementPlanResponse]
