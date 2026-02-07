from datetime import datetime
from uuid import UUID
from typing import Optional, List, Dict, Any
from pydantic import BaseModel


class CollegeBase(BaseModel):
    name: str

class CollegeCreate(CollegeBase):
    dean_id: Optional[UUID] = None

class CollegeResponse(CollegeBase):
    id: UUID
    dean_id: Optional[UUID] = None

    class Config:
        from_attributes = True


class CollegeStats(BaseModel):
    avg_score: float
    rank_list: List[Dict[str, Any]]
    weakness_analysis: List[Dict[str, Any]]
