from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from uuid import UUID
from decimal import Decimal
from datetime import datetime

from app.core.deps import get_db, require_management_roles
from app.models.user import User
from app.models.manual_score import ManualScore
from app.models.ai_score import AIScore
from app.models.final_score import FinalScore
from app.models.self_evaluation import SelfEvaluation
from app.models.teaching_office import TeachingOffice
from app.models.operation_log import OperationLog
from app.schemas.scoring import (
    ManualScoreCreate,
    ManualScoreResponse,
    AllScoresResponse,
    ManualScoreDetail,
    AIScoreDetail,
    FinalScoreDetail,
    IndicatorScore,
    FinalScoreCreate,
    FinalScoreResponse,
    ScoringAuditRecord,
    ScoringAuditResponse,
)
from app.core.logging_middleware import log_operation

router = APIRouter()


def get_reviewer_weight(reviewer_role: str) -> Decimal:
    """
    Get weight for reviewer based on role.
    
    考评小组 (evaluation_team) has higher weight than 考评办公室 (evaluation_office).
    """
    weights = {
        "evaluation_team": Decimal("0.70"),  # 考评小组权重更高
        "evaluation_office": Decimal("0.50"),
    }
    return weights.get(reviewer_role, Decimal("0.50"))


@router.post("/manual-score", response_model=ManualScoreResponse, status_code=status.HTTP_201_CREATED)
def submit_manual_score(
    score_data: ManualScoreCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_management_roles)
):
    """
    提交手动评分 (Submit manual score).
    
    需求: 6.1, 6.2, 6.3, 6.4, 6.7
    
    - 仅考评小组和考评办公室可以提交评分
    - 评分记录一旦提交不可删除和修改
    - 保留评审人的原始打分记录
    - 考评小组评分权重高于考评办公室
    """
    # Verify evaluation exists
    evaluation = db.query(SelfEvaluation).filter(
        SelfEvaluation.id == score_data.evaluation_id
    ).first()
    
    if not evaluation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Evaluation with id {score_data.evaluation_id} not found"
        )
    
    # Check if this reviewer has already submitted a score for this evaluation
    existing_score = db.query(ManualScore).filter(
        ManualScore.evaluation_id == score_data.evaluation_id,
        ManualScore.reviewer_id == current_user.id
    ).first()
    
    if existing_score:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You have already submitted a score for this evaluation. Scores cannot be modified once submitted."
        )
    
    # Get weight based on reviewer role
    weight = get_reviewer_weight(current_user.role)
    
    # Convert scores to dict format for JSON storage
    scores_dict = [score.model_dump() for score in score_data.scores]
    
    # Create manual score record
    manual_score = ManualScore(
        evaluation_id=score_data.evaluation_id,
        reviewer_id=current_user.id,
        reviewer_name=current_user.name,
        reviewer_role=current_user.role,
        weight=weight,
        scores=scores_dict
    )
    
    db.add(manual_score)
    db.commit()
    db.refresh(manual_score)
    
    # 记录操作日志 - 需求 17.3
    try:
        log_operation(
            db=db,
            operation_type="manual_score",
            operator_id=current_user.id,
            operator_name=current_user.name,
            operator_role=current_user.role,
            target_id=manual_score.id,
            target_type="manual_score",
            details={
                "action": "submit_manual_score",
                "evaluation_id": str(score_data.evaluation_id),
                "reviewer_role": current_user.role,
                "weight": float(weight),
                "scores_count": len(score_data.scores)
            }
        )
    except Exception as e:
        # Don't fail the request if logging fails
        pass
    
    return ManualScoreResponse(
        score_record_id=manual_score.id,
        submitted_at=manual_score.submitted_at
    )


@router.get("/all-scores/{evaluation_id}", response_model=AllScoresResponse)
def get_all_scores(
    evaluation_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_management_roles)
):
    """
    查看所有评审人打分 (Get all reviewer scores for an evaluation).
    
    需求: 6.7
    
    - 返回AI评分、所有评审人打分记录和最终得分
    - 仅管理端（考评小组和考评办公室）可以查看
    """
    # Verify evaluation exists
    evaluation = db.query(SelfEvaluation).filter(
        SelfEvaluation.id == evaluation_id
    ).first()
    
    if not evaluation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Evaluation with id {evaluation_id} not found"
        )
    
    # Get AI score
    ai_score = db.query(AIScore).filter(
        AIScore.evaluation_id == evaluation_id
    ).first()
    
    ai_score_detail = None
    if ai_score:
        ai_score_detail = AIScoreDetail(
            id=ai_score.id,
            evaluation_id=ai_score.evaluation_id,
            total_score=float(ai_score.total_score),
            indicator_scores=ai_score.indicator_scores,
            parsed_reform_projects=ai_score.parsed_reform_projects,
            parsed_honorary_awards=ai_score.parsed_honorary_awards,
            scored_at=ai_score.scored_at
        )
    
    # Get all manual scores
    manual_scores = db.query(ManualScore).filter(
        ManualScore.evaluation_id == evaluation_id
    ).order_by(ManualScore.submitted_at.desc()).all()
    
    manual_scores_detail = []
    for score in manual_scores:
        # Convert JSON scores back to IndicatorScore objects
        indicator_scores = [IndicatorScore(**s) for s in score.scores]
        
        manual_scores_detail.append(ManualScoreDetail(
            id=score.id,
            evaluation_id=score.evaluation_id,
            reviewer_id=score.reviewer_id,
            reviewer_name=score.reviewer_name,
            reviewer_role=score.reviewer_role,
            weight=float(score.weight),
            scores=indicator_scores,
            submitted_at=score.submitted_at
        ))
    
    # Get final score
    final_score = db.query(FinalScore).filter(
        FinalScore.evaluation_id == evaluation_id
    ).first()
    
    final_score_detail = None
    if final_score:
        final_score_detail = FinalScoreDetail(
            id=final_score.id,
            evaluation_id=final_score.evaluation_id,
            final_score=float(final_score.final_score),
            summary=final_score.summary,
            determined_by=final_score.determined_by,
            determined_at=final_score.determined_at
        )
    
    return AllScoresResponse(
        evaluation_id=evaluation_id,
        ai_score=ai_score_detail,
        manual_scores=manual_scores_detail,
        final_score=final_score_detail
    )


@router.post("/final-score", response_model=FinalScoreResponse, status_code=status.HTTP_201_CREATED)
def determine_final_score(
    score_data: FinalScoreCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_management_roles)
):
    """
    确定最终得分 (Determine final score).
    
    需求: 7.1, 7.2, 7.3, 7.4, 7.5, 7.6
    
    - 综合所有评审人打分计算最终得分
    - 保留最终得分和汇总说明
    - 仅考评办公室可以确定最终得分
    """
    # Verify user is from evaluation_office
    if current_user.role != "evaluation_office":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only evaluation office can determine final score"
        )
    
    # Verify evaluation exists
    evaluation = db.query(SelfEvaluation).filter(
        SelfEvaluation.id == score_data.evaluation_id
    ).first()
    
    if not evaluation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Evaluation with id {score_data.evaluation_id} not found"
        )
    
    # Check if final score already exists
    existing_final_score = db.query(FinalScore).filter(
        FinalScore.evaluation_id == score_data.evaluation_id
    ).first()
    
    if existing_final_score:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Final score has already been determined for this evaluation"
        )
    
    # Get all manual scores for calculation reference
    manual_scores = db.query(ManualScore).filter(
        ManualScore.evaluation_id == score_data.evaluation_id
    ).all()
    
    if not manual_scores:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No manual scores found. At least one manual score is required before determining final score."
        )
    
    # Calculate weighted average of manual scores (for reference/validation)
    # This is a reference calculation - the actual final_score comes from the request
    total_weighted_score = Decimal("0")
    total_weight = Decimal("0")
    
    for manual_score in manual_scores:
        # Calculate total score for this reviewer
        reviewer_total = sum(Decimal(str(score_item["score"])) for score_item in manual_score.scores)
        total_weighted_score += reviewer_total * manual_score.weight
        total_weight += manual_score.weight
    
    calculated_score = total_weighted_score / total_weight if total_weight > 0 else Decimal("0")
    
    # Validate that provided final_score is reasonable (within 20% of calculated)
    provided_score = Decimal(str(score_data.final_score))
    if calculated_score > 0:
        difference_ratio = abs(provided_score - calculated_score) / calculated_score
        if difference_ratio > Decimal("0.2"):  # More than 20% difference
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Provided final score ({provided_score}) differs significantly from calculated score ({calculated_score:.2f}). Please review."
            )
    
    # Create final score record
    final_score = FinalScore(
        evaluation_id=score_data.evaluation_id,
        final_score=provided_score,
        summary=score_data.summary,
        determined_by=current_user.id
    )
    
    db.add(final_score)
    
    # Update evaluation status
    evaluation.status = "finalized"
    
    db.commit()
    db.refresh(final_score)
    
    return FinalScoreResponse(
        final_score_id=final_score.id,
        status="finalized"
    )


@router.get("/audit", response_model=ScoringAuditResponse)
def get_scoring_audit(
    teaching_office_id: Optional[UUID] = Query(None, description="按教研室筛选"),
    reviewer_id: Optional[UUID] = Query(None, description="按评审人筛选"),
    start_date: Optional[datetime] = Query(None, description="开始时间"),
    end_date: Optional[datetime] = Query(None, description="结束时间"),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_management_roles)
):
    """
    查询评分记录审计 (Query scoring audit records).
    
    需求: 19.5, 19.6
    
    - 支持按教研室、评审人、时间范围查询
    - 返回所有评分记录（AI评分、手动评分、最终得分）
    - 支持后续审计和追溯
    """
    audit_records = []
    
    # Query AI scores
    ai_query = db.query(
        AIScore.id,
        AIScore.evaluation_id,
        AIScore.total_score,
        AIScore.scored_at,
        SelfEvaluation.teaching_office_id,
        SelfEvaluation.evaluation_year,
        TeachingOffice.name.label("teaching_office_name")
    ).join(
        SelfEvaluation, AIScore.evaluation_id == SelfEvaluation.id
    ).join(
        TeachingOffice, SelfEvaluation.teaching_office_id == TeachingOffice.id
    )
    
    # Apply filters for AI scores
    if teaching_office_id:
        ai_query = ai_query.filter(SelfEvaluation.teaching_office_id == teaching_office_id)
    if start_date:
        ai_query = ai_query.filter(AIScore.scored_at >= start_date)
    if end_date:
        ai_query = ai_query.filter(AIScore.scored_at <= end_date)
    
    ai_scores = ai_query.all()
    
    for score in ai_scores:
        audit_records.append(ScoringAuditRecord(
            id=score.id,
            evaluation_id=score.evaluation_id,
            teaching_office_id=score.teaching_office_id,
            teaching_office_name=score.teaching_office_name,
            evaluation_year=score.evaluation_year,
            score_type="ai_score",
            score_value=float(score.total_score),
            reviewer_id=None,
            reviewer_name=None,
            reviewer_role=None,
            created_at=score.scored_at
        ))
    
    # Query manual scores
    manual_query = db.query(
        ManualScore.id,
        ManualScore.evaluation_id,
        ManualScore.reviewer_id,
        ManualScore.reviewer_name,
        ManualScore.reviewer_role,
        ManualScore.scores,
        ManualScore.submitted_at,
        SelfEvaluation.teaching_office_id,
        SelfEvaluation.evaluation_year,
        TeachingOffice.name.label("teaching_office_name")
    ).join(
        SelfEvaluation, ManualScore.evaluation_id == SelfEvaluation.id
    ).join(
        TeachingOffice, SelfEvaluation.teaching_office_id == TeachingOffice.id
    )
    
    # Apply filters for manual scores
    if teaching_office_id:
        manual_query = manual_query.filter(SelfEvaluation.teaching_office_id == teaching_office_id)
    if reviewer_id:
        manual_query = manual_query.filter(ManualScore.reviewer_id == reviewer_id)
    if start_date:
        manual_query = manual_query.filter(ManualScore.submitted_at >= start_date)
    if end_date:
        manual_query = manual_query.filter(ManualScore.submitted_at <= end_date)
    
    manual_scores = manual_query.all()
    
    for score in manual_scores:
        # Calculate total score from indicator scores
        total_score = sum(float(s["score"]) for s in score.scores)
        
        audit_records.append(ScoringAuditRecord(
            id=score.id,
            evaluation_id=score.evaluation_id,
            teaching_office_id=score.teaching_office_id,
            teaching_office_name=score.teaching_office_name,
            evaluation_year=score.evaluation_year,
            score_type="manual_score",
            score_value=total_score,
            reviewer_id=score.reviewer_id,
            reviewer_name=score.reviewer_name,
            reviewer_role=score.reviewer_role,
            created_at=score.submitted_at
        ))
    
    # Query final scores
    final_query = db.query(
        FinalScore.id,
        FinalScore.evaluation_id,
        FinalScore.final_score,
        FinalScore.determined_by,
        FinalScore.determined_at,
        SelfEvaluation.teaching_office_id,
        SelfEvaluation.evaluation_year,
        TeachingOffice.name.label("teaching_office_name"),
        User.name.label("determiner_name")
    ).join(
        SelfEvaluation, FinalScore.evaluation_id == SelfEvaluation.id
    ).join(
        TeachingOffice, SelfEvaluation.teaching_office_id == TeachingOffice.id
    ).join(
        User, FinalScore.determined_by == User.id
    )
    
    # Apply filters for final scores
    if teaching_office_id:
        final_query = final_query.filter(SelfEvaluation.teaching_office_id == teaching_office_id)
    if start_date:
        final_query = final_query.filter(FinalScore.determined_at >= start_date)
    if end_date:
        final_query = final_query.filter(FinalScore.determined_at <= end_date)
    
    final_scores = final_query.all()
    
    for score in final_scores:
        audit_records.append(ScoringAuditRecord(
            id=score.id,
            evaluation_id=score.evaluation_id,
            teaching_office_id=score.teaching_office_id,
            teaching_office_name=score.teaching_office_name,
            evaluation_year=score.evaluation_year,
            score_type="final_score",
            score_value=float(score.final_score),
            reviewer_id=score.determined_by,
            reviewer_name=score.determiner_name,
            reviewer_role="evaluation_office",
            created_at=score.determined_at
        ))
    
    # Sort by created_at descending
    audit_records.sort(key=lambda x: x.created_at, reverse=True)
    
    return ScoringAuditResponse(
        total_count=len(audit_records),
        records=audit_records
    )
