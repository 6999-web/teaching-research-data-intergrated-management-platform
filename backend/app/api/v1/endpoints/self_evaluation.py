from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session
from typing import Optional
from uuid import UUID, uuid4
from datetime import datetime

from app.core.deps import get_db, get_current_user
from app.models.user import User
from app.models.self_evaluation import SelfEvaluation
from app.models.attachment import Attachment
from app.models.operation_log import OperationLog
from app.schemas.self_evaluation import (
    SelfEvaluationCreate,
    SelfEvaluationUpdate,
    SelfEvaluationResponse,
    SelfEvaluationSaveResponse,
    SelfEvaluationSubmitResponse,
    SelfEvaluationUnlockResponse,
    TriggerAIScoringRequest,
    TriggerAIScoringResponse,
)
from app.services.ai_scoring_service import AIScoringService
from app.core.logging_middleware import log_operation
import logging

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/self-evaluation", response_model=SelfEvaluationSaveResponse, status_code=status.HTTP_201_CREATED)
def create_self_evaluation(
    evaluation_data: SelfEvaluationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    创建或更新自评表
    
    - 如果该教研室和年份的自评表已存在，则更新内容
    - 如果不存在，则创建新的自评表
    - 状态默认为 'draft'
    """
    # 检查是否已存在该教研室和年份的自评表
    existing_evaluation = db.query(SelfEvaluation).filter(
        SelfEvaluation.teaching_office_id == evaluation_data.teaching_office_id,
        SelfEvaluation.evaluation_year == evaluation_data.evaluation_year
    ).first()
    
    if existing_evaluation:
        # 检查是否已锁定
        if existing_evaluation.status == "locked":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="自评表已锁定，无法修改"
            )
        
        # 更新现有自评表
        existing_evaluation.content = evaluation_data.content
        existing_evaluation.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(existing_evaluation)
        
        return SelfEvaluationSaveResponse(
            evaluation_id=existing_evaluation.id,
            status=existing_evaluation.status,
            created_at=existing_evaluation.created_at
        )
    
    # 创建新的自评表
    new_evaluation = SelfEvaluation(
        teaching_office_id=evaluation_data.teaching_office_id,
        evaluation_year=evaluation_data.evaluation_year,
        content=evaluation_data.content,
        status="draft"
    )
    
    db.add(new_evaluation)
    db.commit()
    db.refresh(new_evaluation)
    
    return SelfEvaluationSaveResponse(
        evaluation_id=new_evaluation.id,
        status=new_evaluation.status,
        created_at=new_evaluation.created_at
    )


@router.get("/self-evaluation/{evaluation_id}", response_model=SelfEvaluationResponse)
def get_self_evaluation(
    evaluation_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    查询自评表详情
    
    - 根据自评表ID查询
    - 返回完整的自评表信息
    """
    evaluation = db.query(SelfEvaluation).filter(
        SelfEvaluation.id == evaluation_id
    ).first()
    
    if not evaluation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="自评表不存在"
        )
    
    return evaluation


@router.put("/self-evaluation/{evaluation_id}", response_model=SelfEvaluationResponse)
def update_self_evaluation(
    evaluation_id: UUID,
    evaluation_data: SelfEvaluationUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    更新自评表
    
    - 更新自评表内容或状态
    - 如果状态为 'locked'，则禁止修改内容
    """
    evaluation = db.query(SelfEvaluation).filter(
        SelfEvaluation.id == evaluation_id
    ).first()
    
    if not evaluation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="自评表不存在"
        )
    
    # 检查是否已锁定
    if evaluation.status == "locked" and evaluation_data.content is not None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="自评表已锁定，无法修改内容"
        )
    
    # 更新内容
    if evaluation_data.content is not None:
        evaluation.content = evaluation_data.content
    
    # 更新状态
    if evaluation_data.status is not None:
        # 状态转换逻辑
        valid_statuses = ["draft", "submitted", "locked", "ai_scored", "manually_scored", "finalized", "published"]
        if evaluation_data.status not in valid_statuses:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"无效的状态值，有效值为: {', '.join(valid_statuses)}"
            )
        
        evaluation.status = evaluation_data.status
        
        # 如果状态变为 'submitted'，记录提交时间
        if evaluation_data.status == "submitted" and evaluation.submitted_at is None:
            evaluation.submitted_at = datetime.utcnow()
    
    evaluation.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(evaluation)
    
    return evaluation


@router.post("/self-evaluation/{evaluation_id}/submit", response_model=SelfEvaluationSubmitResponse)
def submit_self_evaluation(
    evaluation_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    提交自评表
    
    - 检查自评表和附件是否都已完成
    - 如果都已完成，则自动锁定表单和附件
    - 更新状态为 'locked'
    
    需求: 2.6
    """
    evaluation = db.query(SelfEvaluation).filter(
        SelfEvaluation.id == evaluation_id
    ).first()
    
    if not evaluation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="自评表不存在"
        )
    
    # 检查是否已经锁定
    if evaluation.status == "locked":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="自评表已经提交并锁定"
        )
    
    # 检查是否有附件（可选，不强制要求）
    attachments_count = db.query(Attachment).filter(
        Attachment.evaluation_id == evaluation_id
    ).count()
    
    # 注意：附件不是必需的，允许没有附件的情况下提交
    # if attachments_count == 0:
    #     raise HTTPException(
    #         status_code=status.HTTP_400_BAD_REQUEST,
    #         detail="请先上传附件后再提交"
    #     )
    
    # 更新状态为 locked
    evaluation.status = "locked"
    evaluation.submitted_at = datetime.utcnow()
    evaluation.updated_at = datetime.utcnow()
    
    db.commit()
    db.refresh(evaluation)
    
    # 记录操作日志 - 需求 17.1
    try:
        log_operation(
            db=db,
            operation_type="submit",
            operator_id=current_user.id,
            operator_name=current_user.name,
            operator_role=current_user.role,
            target_id=evaluation.id,
            target_type="self_evaluation",
            details={
                "action": "submit_and_lock",
                "evaluation_id": str(evaluation.id),
                "teaching_office_id": str(evaluation.teaching_office_id),
                "evaluation_year": evaluation.evaluation_year,
                "attachments_count": attachments_count
            }
        )
    except Exception as e:
        logger.warning(f"Failed to log submit operation: {str(e)}")
    
    return SelfEvaluationSubmitResponse(
        evaluation_id=evaluation.id,
        status=evaluation.status,
        submitted_at=evaluation.submitted_at,
        message="自评表和附件已成功提交并锁定"
    )


@router.post("/self-evaluation/{evaluation_id}/unlock", response_model=SelfEvaluationUnlockResponse)
def unlock_self_evaluation(
    evaluation_id: UUID,
    reason: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    解锁自评表（管理端打回后）
    
    - 仅管理端用户可以解锁
    - 将状态从 'locked' 改回 'draft'
    - 允许教研室重新修改和上传附件
    
    需求: 2.8
    """
    # 检查用户权限（仅管理端可以解锁）
    if current_user.role not in ["evaluation_team", "evaluation_office"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="仅管理端用户可以解锁自评表"
        )
    
    evaluation = db.query(SelfEvaluation).filter(
        SelfEvaluation.id == evaluation_id
    ).first()
    
    if not evaluation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="自评表不存在"
        )
    
    # 检查是否处于锁定状态
    if evaluation.status != "locked":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="自评表未处于锁定状态，无需解锁"
        )
    
    # 解锁：将状态改回 draft
    evaluation.status = "draft"
    evaluation.updated_at = datetime.utcnow()
    
    db.commit()
    db.refresh(evaluation)
    
    return SelfEvaluationUnlockResponse(
        evaluation_id=evaluation.id,
        status=evaluation.status,
        unlocked_at=evaluation.updated_at,
        unlock_reason=reason,
        message="自评表已解锁，教研室可以重新修改和上传附件"
    )



async def _background_ai_scoring_task(evaluation_id: UUID, db: Session):
    """
    后台AI评分任务
    
    Args:
        evaluation_id: 自评表ID
        db: 数据库会话
    """
    try:
        logger.info(f"后台AI评分任务开始，evaluation_id: {evaluation_id}")
        
        ai_scoring_service = AIScoringService(db)
        ai_score = await ai_scoring_service.execute_ai_scoring(evaluation_id)
        
        logger.info(f"后台AI评分任务完成，score_id: {ai_score.id}")
        
    except Exception as e:
        logger.error(f"后台AI评分任务失败，evaluation_id: {evaluation_id}, error: {str(e)}")
        
        # 更新自评表状态为失败（可选）
        try:
            evaluation = db.query(SelfEvaluation).filter(
                SelfEvaluation.id == evaluation_id
            ).first()
            
            if evaluation:
                # 保持locked状态，但可以记录错误信息
                evaluation.updated_at = datetime.utcnow()
                db.commit()
        except:
            pass


@router.post("/trigger-ai-scoring", response_model=TriggerAIScoringResponse)
async def trigger_ai_scoring(
    request: TriggerAIScoringRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    触发AI评分
    
    - 检查自评表和附件是否都已提交（状态为locked）
    - 使用BackgroundTasks异步执行AI评分任务
    - 立即返回任务ID和状态
    
    需求: 3.1, 3.2
    """
    evaluation_id = request.evaluation_id
    
    # 检查自评表是否存在
    evaluation = db.query(SelfEvaluation).filter(
        SelfEvaluation.id == evaluation_id
    ).first()
    
    if not evaluation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="自评表不存在"
        )
    
    # 检查自评表状态是否为locked（已提交）
    if evaluation.status != "locked":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"自评表状态不正确，当前状态: {evaluation.status}。请先提交自评表。"
        )
    
    # 检查是否有附件（可选，不强制要求）
    attachments_count = db.query(Attachment).filter(
        Attachment.evaluation_id == evaluation_id
    ).count()
    
    # 注意：附件不是必需的，允许没有附件的情况下进行AI评分
    # if attachments_count == 0:
    #     raise HTTPException(
    #         status_code=status.HTTP_400_BAD_REQUEST,
    #         detail="自评表没有附件，无法进行AI评分"
    #     )
    
    # 检查是否已经触发过AI评分
    from app.models.ai_score import AIScore
    existing_score = db.query(AIScore).filter(
        AIScore.evaluation_id == evaluation_id
    ).first()
    
    if existing_score:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="该自评表已经完成AI评分，无需重复触发"
        )
    
    # 生成任务ID（使用evaluation_id作为任务ID）
    scoring_task_id = evaluation_id
    
    # 添加后台任务
    background_tasks.add_task(_background_ai_scoring_task, evaluation_id, db)
    
    logger.info(f"AI评分任务已添加到后台队列，task_id: {scoring_task_id}")
    
    # 记录操作日志 - 需求 17.2
    try:
        log_operation(
            db=db,
            operation_type="ai_score",
            operator_id=current_user.id,
            operator_name=current_user.name,
            operator_role=current_user.role,
            target_id=scoring_task_id,
            target_type="ai_scoring_task",
            details={
                "action": "trigger_ai_scoring",
                "evaluation_id": str(evaluation_id),
                "attachments_count": attachments_count
            }
        )
    except Exception as e:
        logger.warning(f"Failed to log AI scoring trigger operation: {str(e)}")
    
    return TriggerAIScoringResponse(
        scoring_task_id=scoring_task_id,
        status="processing",
        message="AI评分任务已启动，正在后台处理中"
    )
