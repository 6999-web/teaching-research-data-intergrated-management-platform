"""
公示相关的API端点

包括发起公示、结果分发等功能
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID
from datetime import datetime

from app.core.deps import get_db, require_evaluation_office
from app.models.user import User
from app.models.publication import Publication
from app.models.self_evaluation import SelfEvaluation
from app.models.approval import Approval
from app.models.operation_log import OperationLog
from app.schemas.publication import (
    PublishRequest,
    PublishResponse,
    PublicationDetail,
    DistributeRequest,
    DistributeResponse,
)
from app.services.insight_service import generate_insight_for_evaluation

router = APIRouter()


@router.post("/publish", response_model=PublishResponse, status_code=status.HTTP_200_OK)
def publish(
    request: PublishRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_evaluation_office)
):
    """
    发起公示 (Initiate publication).
    
    需求: 13.1, 13.2, 13.3, 13.4
    
    - 仅在校长办公会审定同意后显示"发起公示"按钮
    - 考评办公室手动点击按钮发起公示
    - 禁止自动发起公示
    - 显示成功提示
    - 仅考评办公室可以发起公示
    """
    # Validate that all evaluations exist and are approved
    evaluations = []
    for eval_id in request.evaluation_ids:
        evaluation = db.query(SelfEvaluation).filter(
            SelfEvaluation.id == eval_id
        ).first()
        
        if not evaluation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Evaluation with id {eval_id} not found"
            )
        
        evaluations.append(evaluation)
    
    # Check if any of the evaluations have already been published
    # This check must happen before status validation
    existing_publication = db.query(Publication).filter(
        Publication.evaluation_ids.contains([str(eval_id) for eval_id in request.evaluation_ids])
    ).first()
    
    if existing_publication:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="One or more evaluations have already been published."
        )
    
    # Now check if evaluations are approved by president office
    for evaluation in evaluations:
        # Check if evaluation is approved by president office
        # 需求 13.1: 仅在校长办公会审定同意后显示"发起公示"按钮
        if evaluation.status != "approved":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Evaluation {eval_id} has not been approved by president office yet. Current status: {evaluation.status}"
            )
    
    # Verify that there is an approval record for these evaluations
    # This ensures the president office has actually approved them
    approval = db.query(Approval).filter(
        Approval.decision == "approve"
    ).order_by(Approval.approved_at.desc()).first()
    
    if not approval:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No approval record found. President office must approve before publication."
        )
    
    # Create publication record
    # 需求 13.2: 考评办公室点击"发起公示"按钮时，系统启动公示流程
    published_at = datetime.utcnow()
    publication = Publication(
        evaluation_ids=[str(eval_id) for eval_id in request.evaluation_ids],
        published_by=current_user.id,
        published_at=published_at
    )
    db.add(publication)
    
    # Update evaluation status to published
    for evaluation in evaluations:
        evaluation.status = "published"
    
    # Flush to get the publication ID before creating operation log
    db.flush()
    
    # Record operation log
    # 需求 17.7: 公示时记录操作日志
    operation_log = OperationLog(
        operation_type="publish",
        operator_id=current_user.id,
        operator_name=current_user.name,
        operator_role=current_user.role,
        target_id=publication.id,
        target_type="publication",
        details={
            "evaluation_ids": [str(eid) for eid in request.evaluation_ids],
            "evaluation_count": len(request.evaluation_ids)
        }
    )
    db.add(operation_log)
    
    # Commit all changes
    db.commit()
    db.refresh(publication)
    
    # 需求 13.4: 公示启动时显示成功提示
    return PublishResponse(
        publication_id=publication.id,
        published_at=published_at,
        message="Publication initiated successfully. Results are now visible to all teaching offices."
    )


@router.get("/publications", response_model=List[PublicationDetail])
def get_publications(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_evaluation_office)
):
    """
    查询公示记录列表 (Get list of publications).
    
    - 仅考评办公室可以查看
    """
    publications = db.query(Publication).order_by(
        Publication.published_at.desc()
    ).all()
    
    return [
        PublicationDetail(
            id=pub.id,
            evaluation_ids=[UUID(eid) for eid in pub.evaluation_ids],
            published_by=pub.published_by,
            published_at=pub.published_at,
            distributed_at=pub.distributed_at
        )
        for pub in publications
    ]


@router.get("/publications/{publication_id}", response_model=PublicationDetail)
def get_publication_detail(
    publication_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_evaluation_office)
):
    """
    查询单个公示记录详情 (Get publication detail).
    
    - 仅考评办公室可以查看
    """
    publication = db.query(Publication).filter(
        Publication.id == publication_id
    ).first()
    
    if not publication:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Publication with id {publication_id} not found"
        )
    
    return PublicationDetail(
        id=publication.id,
        evaluation_ids=[UUID(eid) for eid in publication.evaluation_ids],
        published_by=publication.published_by,
        published_at=publication.published_at,
        distributed_at=publication.distributed_at
    )


@router.post("/distribute", response_model=DistributeResponse, status_code=status.HTTP_200_OK)
def distribute(
    request: DistributeRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_evaluation_office)
):
    """
    自动分发结果 (Distribute results).
    
    需求: 14.1, 14.2
    
    - 公示无异议后，自动分发最终考评结果至管理端和教研室端
    - 分发至教研室端时显示最终得分、详细评分细则、所有评审人打分记录、系统生成的感悟总结
    - 分发至管理端时显示所有教研室最终得分和审定结果
    - 仅考评办公室可以触发分发
    """
    # Validate that publication exists
    publication = db.query(Publication).filter(
        Publication.id == request.publication_id
    ).first()
    
    if not publication:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Publication with id {request.publication_id} not found"
        )
    
    # Check if already distributed
    if publication.distributed_at:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Publication {request.publication_id} has already been distributed at {publication.distributed_at}"
        )
    
    # Validate that all evaluations in the publication exist
    evaluation_ids = [UUID(eid) for eid in publication.evaluation_ids]
    evaluations = db.query(SelfEvaluation).filter(
        SelfEvaluation.id.in_(evaluation_ids)
    ).all()
    
    if len(evaluations) != len(evaluation_ids):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Some evaluations in the publication do not exist"
        )
    
    # Verify all evaluations are published
    for evaluation in evaluations:
        if evaluation.status != "published":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Evaluation {evaluation.id} is not in published status. Current status: {evaluation.status}"
            )
    
    # Update publication distributed_at timestamp
    # 需求 14.1, 14.2: 自动分发最终考评结果至管理端和教研室端
    distributed_at = datetime.utcnow()
    publication.distributed_at = distributed_at
    
    # Update evaluation status to distributed
    # This allows the teaching office and management to view the results
    for evaluation in evaluations:
        evaluation.status = "distributed"
    
    # Generate insight summaries for all evaluations
    # 需求 15.1: 基于综合考核指标自动生成感悟总结
    # 需求 15.6: 禁止人工填写感悟总结
    insight_count = 0
    for evaluation in evaluations:
        try:
            generate_insight_for_evaluation(db, evaluation.id)
            insight_count += 1
        except Exception as e:
            # Log error but don't fail the entire distribution
            print(f"Warning: Failed to generate insight for evaluation {evaluation.id}: {str(e)}")
    
    # Record operation log
    operation_log = OperationLog(
        operation_type="distribute",
        operator_id=current_user.id,
        operator_name=current_user.name,
        operator_role=current_user.role,
        target_id=publication.id,
        target_type="publication",
        details={
            "publication_id": str(request.publication_id),
            "evaluation_ids": [str(eid) for eid in evaluation_ids],
            "evaluation_count": len(evaluations)
        }
    )
    db.add(operation_log)
    
    # Commit all changes
    db.commit()
    db.refresh(publication)
    
    return DistributeResponse(
        distributed_count=len(evaluations),
        distributed_at=distributed_at,
        message=f"Results distributed successfully to management and teaching offices. {len(evaluations)} evaluation(s) are now accessible."
    )
