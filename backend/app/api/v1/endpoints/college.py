from typing import Any, List, Dict
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.deps import get_db, get_current_user
from app.models.user import User
from app.models.college import College
from app.schemas.college import CollegeCreate, CollegeResponse, CollegeStats

router = APIRouter()


@router.post("/", response_model=CollegeResponse)
def create_college(
    *,
    db: Session = Depends(get_db),
    college_in: CollegeCreate,
    current_user: User = Depends(get_current_user),
) -> Any:
    """
    Create new college.
    """
    college = College(name=college_in.name, dean_id=college_in.dean_id)
    db.add(college)
    db.commit()
    db.refresh(college)
    return college


@router.get("/dashboard/stats", response_model=CollegeStats)
def get_dashboard_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Any:
    """
    Get dashboard stats for the college the user belongs to.
    """
    # Assuming user is Dean or relevant personnel
    # logic to get college_id
    if not current_user.college_id:
         # Fallback or error
         # For demo, return mock if no college
         return {
            "avg_score": 0.0,
            "rank_list": [],
            "weakness_analysis": [] 
         }

    # In strict implementation we would aggregate scores here.
    # For MVP fast implementation:
    return {
        "avg_score": 85.5,
        "rank_list": [
            {"name": "软件工程教研室", "score": 92.5},
            {"name": "网络工程教研室", "score": 88.0},
            {"name": "大数据教研室", "score": 76.0}
        ],
        "weakness_analysis": [
             {"indicator": "师资队伍", "avg_loss_rate": 0.15},
             {"indicator": "教学运行", "avg_loss_rate": 0.05}
        ] 
    }
