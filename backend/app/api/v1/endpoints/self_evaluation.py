from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session
from typing import Optional
from uuid import UUID, uuid4
from datetime import datetime

from app.core.deps import get_db, get_current_user, RoleChecker
from app.models.user import User
from app.models.self_evaluation import SelfEvaluation
from app.models.attachment import Attachment
from app.models.operation_log import OperationLog
from app.models.teaching_office import TeachingOffice
from app.models.ai_score import AIScore
from app.models.manual_score import ManualScore
from app.models.final_score import FinalScore
from app.models.insight_summary import InsightSummary
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

# Role checker for teaching office endpoints
# 允许教研室端的所有角色访问：teaching_office, director, teacher
require_teaching_office = RoleChecker(["teaching_office", "director", "teacher"])


@router.post("/self-evaluation", response_model=SelfEvaluationSaveResponse, status_code=status.HTTP_201_CREATED)
def create_self_evaluation(
    evaluation_data: SelfEvaluationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_teaching_office),
):
    """
    创建自评表
    
    - 每年可以提交多次考评表，每次创建新记录
    - 状态默认为 'draft'
    """
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
    - 教研室和管理端都可以查看
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


@router.get("/result/{evaluation_id}")
def get_teaching_office_result(
    evaluation_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_teaching_office),
):
    """
    教研室端查看已公示/已分发的考评结果（让教研室看到自己的成绩）.
    仅当考评状态为 published 或 distributed 且属于当前用户所在教研室时可查看。
    """
    evaluation = (
        db.query(SelfEvaluation)
        .filter(SelfEvaluation.id == evaluation_id)
        .first()
    )
    if not evaluation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="自评表不存在",
        )
    if not current_user.teaching_office_id or str(evaluation.teaching_office_id) != str(current_user.teaching_office_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="只能查看本教研室的考评结果",
        )
    if evaluation.status not in ("published", "distributed"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="该考评尚未公示或分发，暂无法查看结果",
        )

    office = db.query(TeachingOffice).filter(TeachingOffice.id == evaluation.teaching_office_id).first()
    teaching_office_name = office.name if office else ""

    ai_score = db.query(AIScore).filter(AIScore.evaluation_id == evaluation_id).first()
    ai_score_detail = None
    if ai_score:
        ai_score_detail = {
            "id": str(ai_score.id),
            "evaluation_id": str(ai_score.evaluation_id),
            "total_score": float(ai_score.total_score),
            "indicator_scores": ai_score.indicator_scores or [],
            "parsed_reform_projects": ai_score.parsed_reform_projects or 0,
            "parsed_honorary_awards": ai_score.parsed_honorary_awards or 0,
            "scored_at": ai_score.scored_at.isoformat() if ai_score.scored_at else None,
        }

    manual_scores_raw = (
        db.query(ManualScore)
        .filter(ManualScore.evaluation_id == evaluation_id)
        .order_by(ManualScore.submitted_at.desc())
        .all()
    )
    manual_scores_detail = []
    for score in manual_scores_raw:
        scores_list = score.scores if isinstance(score.scores, list) else []
        manual_scores_detail.append({
            "id": str(score.id),
            "evaluation_id": str(score.evaluation_id),
            "reviewer_id": str(score.reviewer_id),
            "reviewer_name": score.reviewer_name,
            "reviewer_role": score.reviewer_role,
            "weight": float(score.weight),
            "scores": scores_list,
            "submitted_at": score.submitted_at.isoformat() if score.submitted_at else None,
        })

    final = db.query(FinalScore).filter(FinalScore.evaluation_id == evaluation_id).first()
    final_score_detail = None
    if final:
        final_score_detail = {
            "id": str(final.id),
            "evaluation_id": str(final.evaluation_id),
            "final_score": float(final.final_score),
            "summary": final.summary,
            "determined_by": str(final.determined_by),
            "determined_at": final.determined_at.isoformat() if final.determined_at else None,
        }

    insight = db.query(InsightSummary).filter(InsightSummary.evaluation_id == evaluation_id).first()
    insight_summary = None
    if insight:
        insight_summary = {
            "id": str(insight.id),
            "evaluation_id": str(insight.evaluation_id),
            "summary": insight.summary,
            "generated_at": insight.generated_at.isoformat() if insight.generated_at else None,
        }

    return {
        "evaluation_id": str(evaluation.id),
        "teaching_office_id": str(evaluation.teaching_office_id),
        "teaching_office_name": teaching_office_name,
        "evaluation_year": int(evaluation.evaluation_year) if evaluation.evaluation_year is not None else None,
        "status": evaluation.status or "",
        "ai_score": ai_score_detail,
        "manual_scores": manual_scores_detail,
        "final_score": final_score_detail,
        "insight_summary": insight_summary,
        "published_at": None,
        "distributed_at": None,
    }


@router.get("/published-results")
def get_published_results(
    teaching_office_id: Optional[str] = None,
    year: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_teaching_office),
):
    """
    教研室端获取已公示/已分发的考评结果列表。
    允许教研室查看自己的所有已公示结果。
    """
    # 从当前用户的 teaching_office_id 或参数获取
    office_id_to_use = teaching_office_id or str(current_user.teaching_office_id) if current_user.teaching_office_id else None

    if not office_id_to_use:
        return []

    query = (
        db.query(SelfEvaluation)
        .filter(
            SelfEvaluation.teaching_office_id == UUID(office_id_to_use),
            SelfEvaluation.status.in_(["published", "distributed"])
        )
        .order_by(SelfEvaluation.evaluation_year.desc())
    )
    if year:
        query = query.filter(SelfEvaluation.evaluation_year == year)

    evaluations = query.all()
    results = []
    for ev in evaluations:
        office = db.query(TeachingOffice).filter(TeachingOffice.id == ev.teaching_office_id).first()
        ai_score = db.query(AIScore).filter(AIScore.evaluation_id == ev.id).first()
        manual_scores_raw = db.query(ManualScore).filter(ManualScore.evaluation_id == ev.id).all()
        final = db.query(FinalScore).filter(FinalScore.evaluation_id == ev.id).first()

        def _manual_score_total(scores_json) -> float:
            if not scores_json or not isinstance(scores_json, list):
                return 0.0
            total = 0.0
            for item in scores_json:
                try:
                    if isinstance(item, dict) and "score" in item:
                        total += float(item["score"])
                except Exception:
                    continue
            return total

        manual_scores_detail = [
            {
                "reviewer_name": s.reviewer_name,
                "reviewer_role": s.reviewer_role,
                "submitted_at": s.submitted_at.isoformat() if s.submitted_at else None,
                "total": _manual_score_total(s.scores)
            }
            for s in manual_scores_raw
        ]

        calculated_final = None
        if final:
            calculated_final = float(final.final_score)
        elif manual_scores_raw:
            tot = sum([_manual_score_total(s.scores) for s in manual_scores_raw])
            calculated_final = tot / len(manual_scores_raw)

        results.append({
            "evaluation_id": str(ev.id),
            "teaching_office_id": str(ev.teaching_office_id),
            "teaching_office_name": office.name if office else "",
            "evaluation_year": ev.evaluation_year,
            "status": ev.status,
            "ai_score": {"total_score": float(ai_score.total_score)} if ai_score else None,
            "manual_scores": manual_scores_detail,
            "final_score": {
                "final_score": calculated_final,
                "summary": final.summary if final else "综合得分",
                "determined_at": final.determined_at.isoformat() if final and final.determined_at else None,
            } if calculated_final is not None else None,
        })

    return results


@router.put("/self-evaluation/{evaluation_id}", response_model=SelfEvaluationResponse)
def update_self_evaluation(
    evaluation_id: UUID,
    evaluation_data: SelfEvaluationUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_teaching_office),
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
    current_user: User = Depends(require_teaching_office),
):
    """
    提交自评表
    
    - 检查自评表是否存在
    - 更新状态为 'submitted'（不锁定，可继续修改）
    """
    evaluation = db.query(SelfEvaluation).filter(
        SelfEvaluation.id == evaluation_id
    ).first()
    
    if not evaluation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="自评表不存在"
        )
    
    # 检查是否已经提交
    if evaluation.status == "submitted":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="自评表已经提交"
        )
    
    # 检查附件数量
    attachments_count = db.query(Attachment).filter(
        Attachment.evaluation_id == evaluation_id
    ).count()
    
    # 更新状态为 submitted（不锁定）
    evaluation.status = "submitted"
    evaluation.submitted_at = datetime.now()
    evaluation.updated_at = datetime.now()
    
    db.commit()
    db.refresh(evaluation)
    
    # 记录操作日志
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
                "action": "submit",
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
        message="自评表已成功提交到考评小组"
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
    current_user: User = Depends(require_teaching_office),
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
