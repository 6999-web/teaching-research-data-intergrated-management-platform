"""
管理端审核相关的API端点

包括异常处理、数据同步、审定操作等功能
"""

from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID, uuid4
from datetime import datetime

from app.core.deps import get_db, require_evaluation_office
from app.models.user import User
from app.models.anomaly import Anomaly
from app.models.self_evaluation import SelfEvaluation
from app.models.operation_log import OperationLog
from app.models.sync_task import SyncTask
from app.schemas.anomaly import (
    HandleAnomalyRequest,
    HandleAnomalyResponse,
    AnomalyResponse,
    AnomalyListResponse,
)
from app.schemas.sync import (
    SyncToPresidentOfficeRequest,
    SyncToPresidentOfficeResponse,
    SyncStatusResponse,
)
from app.services.sync_service import get_sync_service

router = APIRouter()


@router.post("/handle-anomaly", response_model=HandleAnomalyResponse, status_code=status.HTTP_200_OK)
def handle_anomaly(
    request: HandleAnomalyRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_evaluation_office)
):
    """
    处理异常数据 (Handle anomaly data).
    
    需求: 8.1, 8.2, 8.3, 8.4
    
    - 支持打回教研室补充材料 (action=reject)
    - 支持直接修正异常数据 (action=correct)
    - 记录异常处理结果
    - 仅考评办公室可以处理异常
    """
    # Validate action
    if request.action not in ["reject", "correct"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid action. Must be 'reject' or 'correct'"
        )
    
    # Validate action-specific fields
    if request.action == "reject" and not request.reject_reason:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="reject_reason is required when action is 'reject'"
        )
    
    if request.action == "correct" and not request.corrected_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="corrected_data is required when action is 'correct'"
        )
    
    # Get anomaly
    anomaly = db.query(Anomaly).filter(Anomaly.id == request.anomaly_id).first()
    
    if not anomaly:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Anomaly with id {request.anomaly_id} not found"
        )
    
    # Check if anomaly is already handled
    if anomaly.status == "handled":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="This anomaly has already been handled"
        )
    
    # Get associated evaluation
    evaluation = db.query(SelfEvaluation).filter(
        SelfEvaluation.id == anomaly.evaluation_id
    ).first()
    
    if not evaluation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Evaluation with id {anomaly.evaluation_id} not found"
        )
    
    # Handle based on action
    handled_at = datetime.utcnow()
    message = ""
    
    if request.action == "reject":
        # 打回教研室补充材料
        # Unlock the evaluation so teaching office can modify
        evaluation.status = "rejected"
        
        # Update anomaly record
        anomaly.status = "handled"
        anomaly.handled_by = current_user.id
        anomaly.handled_action = "reject"
        anomaly.handled_at = handled_at
        
        message = f"Anomaly rejected. Evaluation unlocked for teaching office to supplement materials. Reason: {request.reject_reason}"
        
        # Record operation log
        operation_log = OperationLog(
            operation_type="handle_anomaly",
            operator_id=current_user.id,
            operator_name=current_user.name,
            operator_role=current_user.role,
            target_id=anomaly.id,
            target_type="anomaly",
            details={
                "action": "reject",
                "anomaly_id": str(anomaly.id),
                "evaluation_id": str(evaluation.id),
                "reject_reason": request.reject_reason,
                "anomaly_type": anomaly.type,
                "indicator": anomaly.indicator,
            }
        )
        db.add(operation_log)
        
    elif request.action == "correct":
        # 直接修正异常数据
        # Update anomaly record
        anomaly.status = "handled"
        anomaly.handled_by = current_user.id
        anomaly.handled_action = "correct"
        anomaly.handled_at = handled_at
        
        # Apply corrected data to evaluation content
        # The corrected_data should contain the fields to update
        if request.corrected_data:
            for key, value in request.corrected_data.items():
                if key in evaluation.content:
                    evaluation.content[key] = value
            
            # Mark the evaluation as modified to trigger SQLAlchemy update
            from sqlalchemy.orm.attributes import flag_modified
            flag_modified(evaluation, "content")
        
        message = f"Anomaly corrected. Data has been updated directly."
        
        # Record operation log
        operation_log = OperationLog(
            operation_type="handle_anomaly",
            operator_id=current_user.id,
            operator_name=current_user.name,
            operator_role=current_user.role,
            target_id=anomaly.id,
            target_type="anomaly",
            details={
                "action": "correct",
                "anomaly_id": str(anomaly.id),
                "evaluation_id": str(evaluation.id),
                "corrected_data": request.corrected_data,
                "anomaly_type": anomaly.type,
                "indicator": anomaly.indicator,
            }
        )
        db.add(operation_log)
    
    # Commit all changes
    db.commit()
    db.refresh(anomaly)
    
    return HandleAnomalyResponse(
        anomaly_id=anomaly.id,
        status="handled",
        handled_at=handled_at,
        message=message
    )


@router.get("/anomalies", response_model=AnomalyListResponse)
def get_anomalies(
    evaluation_id: UUID = None,
    status: str = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_evaluation_office)
):
    """
    查询异常数据列表 (Get list of anomalies).
    
    需求: 8.1
    
    - 支持按evaluation_id筛选
    - 支持按status筛选 (pending, handled)
    - 显示详细对比说明
    - 仅考评办公室可以查看
    """
    query = db.query(Anomaly)
    
    # Apply filters
    if evaluation_id:
        query = query.filter(Anomaly.evaluation_id == evaluation_id)
    
    if status:
        if status not in ["pending", "handled"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid status. Must be 'pending' or 'handled'"
            )
        query = query.filter(Anomaly.status == status)
    
    # Get all matching anomalies
    anomalies = query.order_by(Anomaly.handled_at.desc().nullsfirst()).all()
    
    # Convert to response models
    anomaly_responses = [
        AnomalyResponse(
            id=anomaly.id,
            evaluation_id=anomaly.evaluation_id,
            type=anomaly.type,
            indicator=anomaly.indicator,
            declared_count=anomaly.declared_count,
            parsed_count=anomaly.parsed_count,
            description=anomaly.description,
            status=anomaly.status,
            handled_by=anomaly.handled_by,
            handled_action=anomaly.handled_action,
            handled_at=anomaly.handled_at
        )
        for anomaly in anomalies
    ]
    
    return AnomalyListResponse(
        total=len(anomaly_responses),
        anomalies=anomaly_responses
    )


@router.get("/anomalies/{anomaly_id}", response_model=AnomalyResponse)
def get_anomaly_detail(
    anomaly_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_evaluation_office)
):
    """
    查询单个异常数据详情 (Get anomaly detail).
    
    需求: 8.1
    
    - 显示详细对比说明
    - 仅考评办公室可以查看
    """
    anomaly = db.query(Anomaly).filter(Anomaly.id == anomaly_id).first()
    
    if not anomaly:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Anomaly with id {anomaly_id} not found"
        )
    
    return AnomalyResponse(
        id=anomaly.id,
        evaluation_id=anomaly.evaluation_id,
        type=anomaly.type,
        indicator=anomaly.indicator,
        declared_count=anomaly.declared_count,
        parsed_count=anomaly.parsed_count,
        description=anomaly.description,
        status=anomaly.status,
        handled_by=anomaly.handled_by,
        handled_action=anomaly.handled_action,
        handled_at=anomaly.handled_at
    )



@router.post("/sync-to-president-office", response_model=SyncToPresidentOfficeResponse, status_code=status.HTTP_200_OK)
async def sync_to_president_office(
    request: SyncToPresidentOfficeRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_evaluation_office)
):
    """
    上传至校长办公会 (Sync data to president office).
    
    需求: 9.1, 9.2, 9.3, 9.4, 9.5, 9.6, 9.7, 9.8
    
    - 实现HTTPS数据传输
    - 实现数据完整性验证（考评数据、评分记录、附件、异常处理结果）
    - 实现同步失败重试机制
    - 仅考评办公室可以上传
    """
    # Validate that all evaluations exist and are ready for sync
    for eval_id in request.evaluation_ids:
        evaluation = db.query(SelfEvaluation).filter(
            SelfEvaluation.id == eval_id
        ).first()
        
        if not evaluation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Evaluation with id {eval_id} not found"
            )
        
        # Check if evaluation has final score (required for sync)
        from app.models.final_score import FinalScore
        final_score = db.query(FinalScore).filter(
            FinalScore.evaluation_id == eval_id
        ).first()
        
        if not final_score:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Evaluation {eval_id} does not have a final score yet. Cannot sync."
            )
    
    # Create sync task
    sync_task_id = uuid4()
    sync_task = SyncTask(
        id=sync_task_id,
        evaluation_ids=[str(eid) for eid in request.evaluation_ids],
        status="syncing",
        synced_count=0,
        failed_count=0,
        total_count=len(request.evaluation_ids),
        started_at=datetime.utcnow()
    )
    db.add(sync_task)
    db.commit()
    db.refresh(sync_task)
    
    # Record operation log
    operation_log = OperationLog(
        operation_type="sync",
        operator_id=current_user.id,
        operator_name=current_user.name,
        operator_role=current_user.role,
        target_id=sync_task_id,
        target_type="sync_task",
        details={
            "evaluation_ids": [str(eid) for eid in request.evaluation_ids],
            "total_count": len(request.evaluation_ids)
        }
    )
    db.add(operation_log)
    db.commit()
    
    # Perform sync in background
    background_tasks.add_task(
        perform_sync_task,
        sync_task_id=sync_task_id,
        evaluation_ids=request.evaluation_ids
    )
    
    return SyncToPresidentOfficeResponse(
        sync_task_id=sync_task_id,
        status="syncing",
        synced_count=0,
        failed_count=0,
        message="Sync task started. Data is being synchronized to president office.",
        synced_at=datetime.utcnow()
    )


@router.get("/sync-status/{sync_task_id}", response_model=SyncStatusResponse)
def get_sync_status(
    sync_task_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_evaluation_office)
):
    """
    查询同步任务状态 (Get sync task status).
    
    需求: 9.7, 9.8
    
    - 查询同步进度
    - 查询成功/失败状态
    - 仅考评办公室可以查询
    """
    sync_task = db.query(SyncTask).filter(SyncTask.id == sync_task_id).first()
    
    if not sync_task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Sync task with id {sync_task_id} not found"
        )
    
    return SyncStatusResponse(
        sync_task_id=sync_task.id,
        status=sync_task.status,
        synced_count=sync_task.synced_count,
        failed_count=sync_task.failed_count,
        total_count=sync_task.total_count,
        started_at=sync_task.started_at,
        completed_at=sync_task.completed_at,
        error_message=sync_task.error_message
    )


async def perform_sync_task(sync_task_id: UUID, evaluation_ids: List[UUID]):
    """
    执行同步任务的后台任务
    
    需求: 9.1, 9.2, 9.3, 9.4, 9.5, 9.6, 9.8
    """
    from app.db.base import SessionLocal
    
    db = SessionLocal()
    sync_service = get_sync_service()
    
    try:
        # Perform sync with retry mechanism
        synced_count, failed_count, error_message = await sync_service.sync_evaluations(
            db=db,
            evaluation_ids=evaluation_ids,
            sync_task_id=sync_task_id
        )
        
        # Update sync task status
        sync_task = db.query(SyncTask).filter(SyncTask.id == sync_task_id).first()
        if sync_task:
            sync_task.synced_count = synced_count
            sync_task.failed_count = failed_count
            sync_task.completed_at = datetime.utcnow()
            
            if failed_count == 0:
                sync_task.status = "completed"
            else:
                sync_task.status = "failed"
                sync_task.error_message = error_message
            
            db.commit()
    
    except Exception as e:
        # Update sync task as failed
        sync_task = db.query(SyncTask).filter(SyncTask.id == sync_task_id).first()
        if sync_task:
            sync_task.status = "failed"
            sync_task.failed_count = sync_task.total_count
            sync_task.completed_at = datetime.utcnow()
            sync_task.error_message = str(e)
            db.commit()
    
    finally:
        db.close()
        await sync_service.close()
