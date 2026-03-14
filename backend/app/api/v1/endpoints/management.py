"""
管理端结果汇总 API

提供确定最终得分、得分统计等管理端所需的考评结果列表
"""

import logging

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import Optional, List

from app.core.deps import get_db, require_management_roles
from app.models.user import User
from app.models.self_evaluation import SelfEvaluation
from app.models.teaching_office import TeachingOffice
from app.models.ai_score import AIScore
from app.models.manual_score import ManualScore
from app.models.final_score import FinalScore

router = APIRouter()


def _manual_score_total(scores_json) -> float:
    """从 ManualScore.scores JSON 计算总分（各指标得分之和）"""
    if not scores_json or not isinstance(scores_json, list):
        return 0.0
    total = 0.0
    for item in scores_json:
        try:
            if isinstance(item, dict) and "score" in item:
                total += float(item["score"])
            elif hasattr(item, "score"):
                total += float(item["score"])
        except (TypeError, ValueError):
            continue
    return total


@router.get("/results")
def get_management_results(
    year: Optional[int] = Query(None, description="考评年度"),
    status: Optional[str] = Query(None, description="状态筛选: finalized, approved, published 等"),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_management_roles),
):
    """
    获取管理端考评结果汇总列表（用于「确定最终得分」与「得分统计」）.
    返回各教研室的自评、AI 评分、人工评分及最终得分等信息。
    """
    logger = logging.getLogger(__name__)
    try:
        query = (
            db.query(SelfEvaluation)
            .join(TeachingOffice, SelfEvaluation.teaching_office_id == TeachingOffice.id)
            .filter(
                SelfEvaluation.status.in_([
                    "submitted", "ai_scored", "manually_scored",
                    "ready_for_final", "finalized", "rejected", "approved",
                    "published", "distributed"
                ])
            )
        )
        if year is not None:
            query = query.filter(SelfEvaluation.evaluation_year == year)
        if status:
            query = query.filter(SelfEvaluation.status == status)
        query = query.order_by(SelfEvaluation.submitted_at.desc())
        evaluations = query.all()
    except Exception as e:
        logger.exception("get_management_results query failed: %s", e)
        return []

    result_list: List[dict] = []
    for ev in evaluations:
        try:
            office = ev.teaching_office
            teaching_office_name = office.name if office else ""

            ai_score = (
                db.query(AIScore)
                .filter(AIScore.evaluation_id == ev.id)
                .first()
            )
            ai_score_value = float(ai_score.total_score) if ai_score else None

            manual_scores = (
                db.query(ManualScore)
                .filter(ManualScore.evaluation_id == ev.id)
                .all()
            )
            manual_totals = [_manual_score_total(getattr(m, "scores", None)) for m in manual_scores]
            manual_score_avg = (
                sum(manual_totals) / len(manual_totals) if manual_totals else None
            )

            final = (
                db.query(FinalScore)
                .filter(FinalScore.evaluation_id == ev.id)
                .first()
            )
            final_score_value = float(final.final_score) if final else None
            summary = final.summary if final else None
            determined_at = (final.determined_at.isoformat() if final.determined_at else None) if final else None

            approval_status = "approved" if final else ("rejected" if ev.status == "rejected" else "pending")
            if ev.status == "approved":
                approval_status = "approved"
            if ev.status == "published":
                approval_status = "published"
            if ev.status == "distributed":
                approval_status = "distributed"

            result_list.append({
                "id": str(ev.id),
                "teaching_office_id": str(ev.teaching_office_id),
                "teaching_office_name": teaching_office_name,
                "evaluation_year": int(ev.evaluation_year) if ev.evaluation_year is not None else None,
                "final_score": final_score_value,
                "ai_score": ai_score_value,
                "manual_score_avg": float(manual_score_avg) if manual_score_avg is not None else None,
                "manual_reviewer_count": len(manual_scores),
                "approval_status": approval_status,
                "status": ev.status or "draft",
                "summary": summary,
                "approved_at": determined_at,
                "published_at": None,
                "submitted_at": ev.submitted_at.isoformat() if ev.submitted_at else None,
            })
        except Exception as e:
            logger.exception("Error building management result row for evaluation %s: %s", ev.id, e)
            continue

    return result_list
