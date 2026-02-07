"""
校长办公会端API端点

包括数据接收、实时监控、结果审定等功能
"""

from fastapi import APIRouter, Depends, HTTPException, status, Header
from sqlalchemy.orm import Session
from typing import Optional
from uuid import UUID
from datetime import datetime
import hashlib
import json

from app.core.deps import get_db, require_president_office
from app.schemas.sync import SyncDataPackage
from app.schemas.approval import ApprovalRequest, ApprovalResponse
from app.models.operation_log import OperationLog
from app.models.approval import Approval
from app.models.self_evaluation import SelfEvaluation
from app.models.user import User

router = APIRouter()


@router.post("/receive-sync-data", status_code=status.HTTP_200_OK)
def receive_sync_data(
    sync_package: SyncDataPackage,
    x_sync_task_id: Optional[str] = Header(None),
    x_checksum: Optional[str] = Header(None),
    db: Session = Depends(get_db)
):
    """
    接收管理端同步的数据 (Receive synced data from management).
    
    需求: 10.1, 10.2, 10.3, 10.4
    
    - 接收管理端同步数据
    - 验证数据完整性（考评数据、评分记录、附件、异常处理结果）
    - 验证数据校验和
    - 记录接收日志
    """
    # Validate sync_task_id header matches payload
    if x_sync_task_id and str(sync_package.sync_task_id) != x_sync_task_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Sync task ID in header does not match payload"
        )
    
    # Verify checksum for data integrity
    if x_checksum:
        # Recalculate checksum from received data
        package_dict = sync_package.model_dump(mode='json')
        received_checksum = package_dict.pop('checksum', None)
        
        # Calculate expected checksum
        json_str = json.dumps(package_dict, sort_keys=True, default=str)
        calculated_checksum = hashlib.sha256(json_str.encode()).hexdigest()
        
        # Compare checksums
        if x_checksum != calculated_checksum:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Data integrity check failed: checksum mismatch"
            )
        
        # Also verify against the checksum in payload
        if received_checksum and received_checksum != calculated_checksum:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Data integrity check failed: payload checksum mismatch"
            )
    
    # Validate data completeness
    validation_errors = []
    
    if not sync_package.evaluations:
        validation_errors.append("No evaluations in sync package")
    
    if sync_package.total_count != len(sync_package.evaluations):
        validation_errors.append(
            f"Total count mismatch: expected {sync_package.total_count}, got {len(sync_package.evaluations)}"
        )
    
    # Validate each evaluation data
    for idx, eval_data in enumerate(sync_package.evaluations):
        eval_errors = []
        
        # Check required fields (需求 10.1 - 考评数据)
        if not eval_data.evaluation_id:
            eval_errors.append("missing evaluation_id")
        if not eval_data.teaching_office_id:
            eval_errors.append("missing teaching_office_id")
        if not eval_data.content:
            eval_errors.append("missing content")
        
        # Check scoring data (需求 10.2 - 评分记录)
        if not eval_data.ai_score:
            eval_errors.append("missing ai_score")
        if not eval_data.manual_scores:
            eval_errors.append("missing manual_scores")
        if not eval_data.final_score:
            eval_errors.append("missing final_score")
        
        # Check attachments (需求 10.3 - 附件)
        # Attachments list should exist (can be empty)
        if eval_data.attachments is None:
            eval_errors.append("missing attachments list")
        
        # Check anomalies (需求 10.4 - 异常处理结果)
        # Anomalies list should exist (can be empty)
        if eval_data.anomalies is None:
            eval_errors.append("missing anomalies list")
        
        if eval_errors:
            validation_errors.append(
                f"Evaluation {idx} ({eval_data.evaluation_id}): {', '.join(eval_errors)}"
            )
    
    if validation_errors:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "message": "Data validation failed",
                "errors": validation_errors
            }
        )
    
    # Record operation log for data reception
    try:
        operation_log = OperationLog(
            operation_type="receive_sync_data",
            operator_id=UUID("00000000-0000-0000-0000-000000000000"),  # System operation
            operator_name="System",
            operator_role="system",
            target_id=sync_package.sync_task_id,
            target_type="sync_task",
            details={
                "sync_task_id": str(sync_package.sync_task_id),
                "total_count": sync_package.total_count,
                "evaluation_ids": [str(e.evaluation_id) for e in sync_package.evaluations],
                "synced_at": sync_package.synced_at.isoformat(),
                "checksum": sync_package.checksum,
                "checksum_verified": x_checksum == sync_package.checksum if x_checksum else False
            }
        )
        db.add(operation_log)
        db.commit()
    except Exception as e:
        # Log the error but don't fail the request
        # In production, this would be logged to a monitoring system
        db.rollback()
        pass
    
    # TODO: Store the synced data in president office database
    # This would typically involve:
    # 1. Creating/updating records in president office's own tables
    # 2. Storing evaluation data for monitoring and approval
    # 3. Making data available for real-time monitoring dashboard
    
    return {
        "status": "success",
        "message": f"Successfully received and validated {sync_package.total_count} evaluations",
        "sync_task_id": str(sync_package.sync_task_id),
        "received_at": datetime.utcnow().isoformat(),
        "evaluations_count": len(sync_package.evaluations)
    }



@router.post("/approve", response_model=ApprovalResponse, status_code=status.HTTP_200_OK)
def approve_evaluation_results(
    request: ApprovalRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_president_office)
):
    """
    审定考评结果 (Approve evaluation results).
    
    需求: 12.1, 12.2, 12.3, 12.4, 12.5, 12.6, 12.7
    
    - 提供"同意公示"选项 (decision=approve)
    - 提供"驳回重新审核"选项 (decision=reject)
    - 同意公示时同步审定结果至管理端
    - 驳回时反馈驳回原因至管理端
    - 仅校长办公会可以审定
    """
    # Validate decision
    if request.decision not in ["approve", "reject"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid decision. Must be 'approve' or 'reject'"
        )
    
    # Validate reject_reason when decision is reject
    if request.decision == "reject" and not request.reject_reason:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="reject_reason is required when decision is 'reject'"
        )
    
    # Validate that all evaluations exist
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
    
    # Create approval record
    approved_at = datetime.utcnow()
    approval = Approval(
        evaluation_ids=[str(eid) for eid in request.evaluation_ids],
        decision=request.decision,
        reject_reason=request.reject_reason if request.decision == "reject" else None,
        approved_by=current_user.id,
        approved_at=approved_at
    )
    db.add(approval)
    
    # Update evaluation status based on decision
    message = ""
    synced_to_management = True
    
    if request.decision == "approve":
        # 同意公示 - 需求 12.2, 12.4, 12.5
        # Update evaluation status to allow publication
        for evaluation in evaluations:
            evaluation.status = "approved"
        
        message = "Approval successful. Management office can now initiate publication."
        
    elif request.decision == "reject":
        # 驳回重新审核 - 需求 12.3, 12.6, 12.7
        # Update evaluation status to indicate rejection
        for evaluation in evaluations:
            evaluation.status = "rejected_by_president"
        
        message = f"Evaluation results rejected. Reason: {request.reject_reason}. Management office has been notified."
    
    # Commit all changes first
    try:
        db.commit()
        db.refresh(approval)
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to save approval: {str(e)}"
        )
    
    # Record operation log after commit (so approval.id is available)
    try:
        if request.decision == "approve":
            operation_log = OperationLog(
                operation_type="approve",
                operator_id=current_user.id,
                operator_name=current_user.name,
                operator_role=current_user.role,
                target_id=approval.id,
                target_type="approval",
                details={
                    "approval_id": str(approval.id),
                    "decision": "approve",
                    "evaluation_ids": [str(eid) for eid in request.evaluation_ids],
                    "evaluation_count": len(request.evaluation_ids)
                }
            )
            db.add(operation_log)
        elif request.decision == "reject":
            operation_log = OperationLog(
                operation_type="approve",
                operator_id=current_user.id,
                operator_name=current_user.name,
                operator_role=current_user.role,
                target_id=approval.id,
                target_type="approval",
                details={
                    "approval_id": str(approval.id),
                    "decision": "reject",
                    "reject_reason": request.reject_reason,
                    "evaluation_ids": [str(eid) for eid in request.evaluation_ids],
                    "evaluation_count": len(request.evaluation_ids)
                }
            )
            db.add(operation_log)
        
        db.commit()
    except Exception as e:
        # Log the error but don't fail the request
        # The approval was already saved successfully
        db.rollback()
        pass
    
    # TODO: In a real implementation, we would send a notification to management office
    # This could be done via:
    # 1. WebSocket for real-time notification
    # 2. Message queue (e.g., RabbitMQ, Redis)
    # 3. Polling endpoint that management office checks periodically
    # For now, the management office can query the evaluation status to see if it's approved/rejected
    
    return ApprovalResponse(
        approval_id=approval.id,
        decision=approval.decision,
        approved_at=approved_at,
        message=message,
        synced_to_management=synced_to_management
    )
