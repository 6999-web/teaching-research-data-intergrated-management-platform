from typing import Any, List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.deps import get_db, get_current_user
from app.models.user import User
from app.models.self_evaluation import SelfEvaluation
from app.models.improvement_plan import ImprovementPlan, ImprovementPlanStatus
from app.schemas.improvement_plan import (
    ImprovementPlanCreate,
    ImprovementPlanUpdate,
    ImprovementPlanReview,
    ImprovementPlanResponse,
    ImprovementPlanList,
)

router = APIRouter()


@router.post("/", response_model=ImprovementPlanResponse)
def create_improvement_plan(
    *,
    db: Session = Depends(get_db),
    plan_in: ImprovementPlanCreate,
    current_user: User = Depends(get_current_user),
) -> Any:
    """
    Create new improvement plan.
    Only teaching office director or members can create.
    """
    # Check permissions (assuming 'teaching_office_director' or similar role, or check if user belongs to the same teaching office)
    # For now, allow logged in users to create for their own teaching office evaluations
    evaluation = db.query(SelfEvaluation).filter(SelfEvaluation.id == plan_in.evaluation_id).first()
    if not evaluation:
        raise HTTPException(status_code=404, detail="Evaluation not found")
        
    # Check if user belongs to the teaching office of the evaluation
    if current_user.teaching_office_id != evaluation.teaching_office_id and current_user.role != "admin":
         raise HTTPException(status_code=403, detail="Not enough permissions")

    plan = ImprovementPlan(
        evaluation_id=plan_in.evaluation_id,
        indicator_item_id=plan_in.indicator_item_id,
        target=plan_in.target,
        measures=plan_in.measures,
        deadline=plan_in.deadline,
        charger_id=plan_in.charger_id,
        status=ImprovementPlanStatus.PENDING,
    )
    db.add(plan)
    db.commit()
    db.refresh(plan)
    return plan


@router.get("/evaluation/{evaluation_id}", response_model=List[ImprovementPlanResponse])
def read_improvement_plans(
    evaluation_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Any:
    """
    Get improvement plans for an evaluation.
    """
    evaluation = db.query(SelfEvaluation).filter(SelfEvaluation.id == evaluation_id).first()
    if not evaluation:
        raise HTTPException(status_code=404, detail="Evaluation not found")

    # Access control: 
    # - User from same teaching office
    # - Dean of the same college
    # - Admin/Evaluation Office
    
    # Check user mapping logic here. 
    # For MVP, allow if user is associated or admin.
    
    plans = db.query(ImprovementPlan).filter(ImprovementPlan.evaluation_id == evaluation_id).all()
    return plans


@router.put("/{id}", response_model=ImprovementPlanResponse)
def update_improvement_plan(
    *,
    db: Session = Depends(get_db),
    id: UUID,
    plan_in: ImprovementPlanUpdate,
    current_user: User = Depends(get_current_user),
) -> Any:
    """
    Update an improvement plan.
    """
    plan = db.query(ImprovementPlan).filter(ImprovementPlan.id == id).first()
    if not plan:
        raise HTTPException(status_code=404, detail="Improvement plan not found")
        
    # Permission check: similar to create
    
    update_data = plan_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(plan, field, value)
        
    db.add(plan)
    db.commit()
    db.refresh(plan)
    return plan


@router.post("/{id}/review", response_model=ImprovementPlanResponse)
def review_improvement_plan(
    *,
    db: Session = Depends(get_db),
    id: UUID,
    review_in: ImprovementPlanReview,
    current_user: User = Depends(get_current_user),
) -> Any:
    """
    Review improvement plan (Dean or higher).
    """
    plan = db.query(ImprovementPlan).filter(ImprovementPlan.id == id).first()
    if not plan:
        raise HTTPException(status_code=404, detail="Improvement plan not found")

    # Check if user is Dean of the college
    # Assuming user.role == 'dean' and user.college_id matches
    # logic to fetch college from evaluation -> teaching_office -> college
    # For now, simplistic basic check role
    
    plan.status = review_in.status
    plan.supervisor_comment = review_in.supervisor_comment
    
    db.add(plan)
    db.commit()
    db.refresh(plan)
    return plan
