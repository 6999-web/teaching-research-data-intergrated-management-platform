"""
感悟总结相关的API端点

提供感悟总结的生成和查询功能
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from uuid import UUID

from app.core.deps import get_db, get_current_user
from app.models.user import User
from app.models.insight_summary import InsightSummary
from app.models.self_evaluation import SelfEvaluation
from app.schemas.insight import (
    InsightSummaryResponse,
    InsightSummaryGenerate,
    InsightSummaryGenerateResponse,
)
from app.services.insight_service import generate_insight_for_evaluation

router = APIRouter()


@router.post("/generate", response_model=InsightSummaryGenerateResponse, status_code=status.HTTP_200_OK)
def generate_insight_summary(
    request: InsightSummaryGenerate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    生成感悟总结 (Generate insight summary).
    
    需求: 15.1, 15.2, 15.3, 15.4, 15.5, 15.6
    
    - 基于综合考核指标自动生成感悟总结
    - 分析各教研室得分高低和指标达标情况
    - 生成包含突出指标和待提升指标的总结
    - 禁止人工填写感悟总结（此接口仅用于系统自动生成）
    
    注意：此接口通常由系统在结果分发时自动调用，也可手动触发重新生成
    """
    # Validate that evaluation exists
    evaluation = db.query(SelfEvaluation).filter(
        SelfEvaluation.id == request.evaluation_id
    ).first()
    
    if not evaluation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Evaluation with id {request.evaluation_id} not found"
        )
    
    # Check if evaluation has final score
    if not evaluation.final_score:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot generate insight summary: evaluation does not have a final score yet"
        )
    
    # Generate insight summary
    try:
        insight = generate_insight_for_evaluation(db, request.evaluation_id)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate insight summary: {str(e)}"
        )
    
    return InsightSummaryGenerateResponse(
        insight_summary=InsightSummaryResponse(
            id=insight.id,
            evaluation_id=insight.evaluation_id,
            summary=insight.summary,
            generated_at=insight.generated_at
        ),
        message="Insight summary generated successfully"
    )


@router.get("/{evaluation_id}", response_model=InsightSummaryResponse)
def get_insight_summary(
    evaluation_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    查询感悟总结 (Get insight summary).
    
    - 教研室端和管理端都可以查询
    - 用于在结果分发后查看感悟总结
    """
    # Validate that evaluation exists
    evaluation = db.query(SelfEvaluation).filter(
        SelfEvaluation.id == evaluation_id
    ).first()
    
    if not evaluation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Evaluation with id {evaluation_id} not found"
        )
    
    # Get insight summary
    insight = db.query(InsightSummary).filter(
        InsightSummary.evaluation_id == evaluation_id
    ).first()
    
    if not insight:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Insight summary not found for evaluation {evaluation_id}"
        )
    
    return InsightSummaryResponse(
        id=insight.id,
        evaluation_id=insight.evaluation_id,
        summary=insight.summary,
        generated_at=insight.generated_at
    )
