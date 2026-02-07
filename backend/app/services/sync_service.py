"""
数据同步服务

负责将考评数据从管理端同步至校长办公会端
包含HTTPS传输、数据完整性验证、失败重试机制
"""

import hashlib
import json
from typing import List, Dict, Any, Optional
from uuid import UUID
from datetime import datetime
from sqlalchemy.orm import Session
import httpx
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type,
    before_sleep_log
)
import logging

from app.models.self_evaluation import SelfEvaluation
from app.models.teaching_office import TeachingOffice
from app.models.ai_score import AIScore
from app.models.manual_score import ManualScore
from app.models.final_score import FinalScore
from app.models.attachment import Attachment
from app.models.anomaly import Anomaly
from app.models.sync_task import SyncTask
from app.schemas.sync import EvaluationSyncData, SyncDataPackage

logger = logging.getLogger(__name__)


class SyncService:
    """数据同步服务类"""
    
    def __init__(self, president_office_url: str = "https://president-office.example.com/api"):
        """
        初始化同步服务
        
        Args:
            president_office_url: 校长办公会端API地址 (HTTPS)
        """
        self.president_office_url = president_office_url
        # Configure HTTPS client with timeout and SSL verification
        self.client = httpx.AsyncClient(
            timeout=httpx.Timeout(30.0, connect=10.0),
            verify=True,  # Enable SSL certificate verification
            follow_redirects=True
        )
    
    async def close(self):
        """关闭HTTP客户端"""
        await self.client.aclose()
    
    def collect_evaluation_data(
        self, 
        db: Session, 
        evaluation_id: UUID
    ) -> Optional[EvaluationSyncData]:
        """
        收集单个自评表的完整数据
        
        需求: 9.3, 9.4, 9.5, 9.6
        
        Args:
            db: 数据库会话
            evaluation_id: 自评表ID
            
        Returns:
            EvaluationSyncData: 完整的自评表数据，如果不存在则返回None
        """
        # Get evaluation
        evaluation = db.query(SelfEvaluation).filter(
            SelfEvaluation.id == evaluation_id
        ).first()
        
        if not evaluation:
            logger.warning(f"Evaluation {evaluation_id} not found")
            return None
        
        # Get teaching office
        teaching_office = db.query(TeachingOffice).filter(
            TeachingOffice.id == evaluation.teaching_office_id
        ).first()
        
        if not teaching_office:
            logger.warning(f"Teaching office {evaluation.teaching_office_id} not found")
            return None
        
        # Get AI score
        ai_score = db.query(AIScore).filter(
            AIScore.evaluation_id == evaluation_id
        ).first()
        
        ai_score_data = None
        if ai_score:
            ai_score_data = {
                "id": str(ai_score.id),
                "total_score": float(ai_score.total_score),
                "indicator_scores": ai_score.indicator_scores,
                "parsed_reform_projects": ai_score.parsed_reform_projects,
                "parsed_honorary_awards": ai_score.parsed_honorary_awards,
                "scored_at": ai_score.scored_at.isoformat()
            }
        
        # Get manual scores
        manual_scores = db.query(ManualScore).filter(
            ManualScore.evaluation_id == evaluation_id
        ).all()
        
        manual_scores_data = [
            {
                "id": str(score.id),
                "reviewer_id": str(score.reviewer_id),
                "reviewer_name": score.reviewer_name,
                "reviewer_role": score.reviewer_role,
                "weight": float(score.weight),
                "scores": score.scores,
                "submitted_at": score.submitted_at.isoformat()
            }
            for score in manual_scores
        ]
        
        # Get final score
        final_score = db.query(FinalScore).filter(
            FinalScore.evaluation_id == evaluation_id
        ).first()
        
        final_score_data = None
        if final_score:
            final_score_data = {
                "id": str(final_score.id),
                "final_score": float(final_score.final_score),
                "summary": final_score.summary,
                "determined_by": str(final_score.determined_by),
                "determined_at": final_score.determined_at.isoformat()
            }
        
        # Get attachments
        attachments = db.query(Attachment).filter(
            Attachment.evaluation_id == evaluation_id
        ).all()
        
        attachments_data = [
            {
                "id": str(att.id),
                "indicator": att.indicator,
                "file_name": att.file_name,
                "file_size": att.file_size,
                "file_type": att.file_type,
                "storage_path": att.storage_path,
                "classified_by": att.classified_by,
                "uploaded_at": att.uploaded_at.isoformat()
            }
            for att in attachments
        ]
        
        # Get anomalies
        anomalies = db.query(Anomaly).filter(
            Anomaly.evaluation_id == evaluation_id
        ).all()
        
        anomalies_data = [
            {
                "id": str(anomaly.id),
                "type": anomaly.type,
                "indicator": anomaly.indicator,
                "declared_count": anomaly.declared_count,
                "parsed_count": anomaly.parsed_count,
                "description": anomaly.description,
                "status": anomaly.status,
                "handled_by": str(anomaly.handled_by) if anomaly.handled_by else None,
                "handled_action": anomaly.handled_action,
                "handled_at": anomaly.handled_at.isoformat() if anomaly.handled_at else None
            }
            for anomaly in anomalies
        ]
        
        # Build sync data
        return EvaluationSyncData(
            evaluation_id=evaluation.id,
            teaching_office_id=evaluation.teaching_office_id,
            teaching_office_name=teaching_office.name,
            evaluation_year=evaluation.evaluation_year,
            content=evaluation.content,
            status=evaluation.status,
            submitted_at=evaluation.submitted_at,
            ai_score=ai_score_data,
            manual_scores=manual_scores_data,
            final_score=final_score_data,
            attachments=attachments_data,
            anomalies=anomalies_data
        )
    
    def calculate_checksum(self, data: Dict[str, Any]) -> str:
        """
        计算数据包的SHA256校验和
        
        需求: 9.3 (数据完整性验证)
        
        Args:
            data: 要计算校验和的数据
            
        Returns:
            str: SHA256校验和
        """
        # Convert to JSON string with sorted keys for consistent hashing
        json_str = json.dumps(data, sort_keys=True, default=str)
        return hashlib.sha256(json_str.encode()).hexdigest()
    
    def verify_data_integrity(
        self, 
        sync_data: EvaluationSyncData
    ) -> tuple[bool, List[str]]:
        """
        验证同步数据的完整性
        
        需求: 9.3, 9.4, 9.5, 9.6
        
        Args:
            sync_data: 要验证的同步数据
            
        Returns:
            tuple[bool, List[str]]: (是否完整, 缺失项列表)
        """
        missing_items = []
        
        # Check required fields
        if not sync_data.evaluation_id:
            missing_items.append("evaluation_id")
        
        if not sync_data.teaching_office_id:
            missing_items.append("teaching_office_id")
        
        if not sync_data.content:
            missing_items.append("content")
        
        # Check if evaluation has been scored
        if not sync_data.ai_score:
            missing_items.append("ai_score")
        
        if not sync_data.manual_scores:
            missing_items.append("manual_scores")
        
        if not sync_data.final_score:
            missing_items.append("final_score")
        
        # Attachments and anomalies are optional but should be checked
        # (they may be empty but should exist as lists)
        
        is_complete = len(missing_items) == 0
        return is_complete, missing_items
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type((httpx.HTTPError, httpx.TimeoutException)),
        before_sleep=before_sleep_log(logger, logging.WARNING)
    )
    async def send_sync_request(
        self, 
        sync_package: SyncDataPackage
    ) -> Dict[str, Any]:
        """
        发送同步请求至校长办公会端 (带重试机制)
        
        需求: 9.2, 9.8 (HTTPS传输, 同步失败重试)
        
        Args:
            sync_package: 同步数据包
            
        Returns:
            Dict[str, Any]: 校长办公会端的响应
            
        Raises:
            httpx.HTTPError: HTTP请求失败
            httpx.TimeoutException: 请求超时
        """
        url = f"{self.president_office_url}/receive-sync-data"
        
        # Convert to dict for JSON serialization
        payload = sync_package.model_dump(mode='json')
        
        logger.info(f"Sending sync request to {url} for task {sync_package.sync_task_id}")
        
        try:
            response = await self.client.post(
                url,
                json=payload,
                headers={
                    "Content-Type": "application/json",
                    "X-Sync-Task-Id": str(sync_package.sync_task_id),
                    "X-Checksum": sync_package.checksum
                }
            )
            
            response.raise_for_status()
            
            logger.info(f"Sync request successful for task {sync_package.sync_task_id}")
            return response.json()
            
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error during sync: {e.response.status_code} - {e.response.text}")
            raise
        except httpx.TimeoutException as e:
            logger.error(f"Timeout during sync: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error during sync: {str(e)}")
            raise
    
    async def sync_evaluations(
        self,
        db: Session,
        evaluation_ids: List[UUID],
        sync_task_id: UUID
    ) -> tuple[int, int, Optional[str]]:
        """
        同步多个自评表数据至校长办公会端
        
        需求: 9.1, 9.2, 9.3, 9.4, 9.5, 9.6, 9.7, 9.8
        
        Args:
            db: 数据库会话
            evaluation_ids: 要同步的自评表ID列表
            sync_task_id: 同步任务ID
            
        Returns:
            tuple[int, int, Optional[str]]: (成功数量, 失败数量, 错误消息)
        """
        synced_count = 0
        failed_count = 0
        error_message = None
        
        # Collect all evaluation data
        evaluations_data = []
        for eval_id in evaluation_ids:
            eval_data = self.collect_evaluation_data(db, eval_id)
            if eval_data:
                # Verify data integrity
                is_complete, missing_items = self.verify_data_integrity(eval_data)
                if not is_complete:
                    logger.warning(
                        f"Evaluation {eval_id} data incomplete. Missing: {missing_items}"
                    )
                    failed_count += 1
                    error_message = f"Data incomplete for evaluation {eval_id}: missing {', '.join(missing_items)}"
                    continue
                
                evaluations_data.append(eval_data)
            else:
                failed_count += 1
                error_message = f"Evaluation {eval_id} not found"
        
        if not evaluations_data:
            return synced_count, failed_count, error_message or "No valid evaluations to sync"
        
        # Build sync package
        sync_package = SyncDataPackage(
            sync_task_id=sync_task_id,
            evaluations=evaluations_data,
            total_count=len(evaluations_data),
            synced_at=datetime.utcnow(),
            checksum=""  # Will be calculated below
        )
        
        # Calculate checksum
        package_dict = sync_package.model_dump(mode='json')
        package_dict.pop('checksum', None)  # Remove checksum field before calculating
        checksum = self.calculate_checksum(package_dict)
        sync_package.checksum = checksum
        
        # Send sync request with retry
        try:
            response = await self.send_sync_request(sync_package)
            
            # Check response
            if response.get("status") == "success":
                synced_count = len(evaluations_data)
                logger.info(f"Successfully synced {synced_count} evaluations")
            else:
                failed_count = len(evaluations_data)
                error_message = response.get("message", "Unknown error from president office")
                logger.error(f"Sync failed: {error_message}")
        
        except Exception as e:
            failed_count = len(evaluations_data)
            error_message = f"Sync request failed after retries: {str(e)}"
            logger.error(error_message)
        
        return synced_count, failed_count, error_message


# Global sync service instance
_sync_service: Optional[SyncService] = None


def get_sync_service() -> SyncService:
    """获取同步服务实例"""
    global _sync_service
    if _sync_service is None:
        # TODO: Get URL from config
        _sync_service = SyncService()
    return _sync_service
