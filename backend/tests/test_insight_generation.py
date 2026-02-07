"""
测试感悟总结生成功能

需求: 15.1, 15.2, 15.3, 15.4, 15.5, 15.6
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from uuid import uuid4
from datetime import datetime

from app.models.teaching_office import TeachingOffice
from app.models.self_evaluation import SelfEvaluation
from app.models.ai_score import AIScore
from app.models.manual_score import ManualScore
from app.models.final_score import FinalScore
from app.models.insight_summary import InsightSummary
from app.models.approval import Approval
from app.models.user import User
from app.services.insight_service import InsightGenerationService


@pytest.fixture
def approved_evaluation(db: Session, evaluation_office_user: User) -> tuple:
    """创建已审定的评估数据"""
    # Create teaching office
    teaching_office = TeachingOffice(
        name="计算机教研室",
        code="CS001",
        department="计算机学院"
    )
    db.add(teaching_office)
    db.commit()
    db.refresh(teaching_office)
    
    # Create evaluation with approved status
    evaluation = SelfEvaluation(
        teaching_office_id=teaching_office.id,
        evaluation_year=2024,
        content={
            "teachingProcessManagement": "教学过程管理良好",
            "courseConstruction": "课程建设完善",
            "teachingReformProjects": 3,
            "honoraryAwards": 2
        },
        status="approved"
    )
    db.add(evaluation)
    db.commit()
    db.refresh(evaluation)
    
    # Create final score
    final_score = FinalScore(
        evaluation_id=evaluation.id,
        final_score=87.5,
        summary="综合评分良好",
        determined_by=evaluation_office_user.id
    )
    db.add(final_score)
    db.commit()
    
    # Create approval record
    approval = Approval(
        evaluation_ids=[str(evaluation.id)],
        decision="approve",
        approved_by=uuid4(),
        approved_at=datetime.utcnow()
    )
    db.add(approval)
    db.commit()
    
    return teaching_office, evaluation


@pytest.fixture
def evaluation_with_scores(db: Session, evaluation_office_user: User):
    """创建包含完整评分数据的自评表"""
    # Create teaching office
    teaching_office = TeachingOffice(
        name="测试教研室",
        code="TEST001",
        department="测试学院"
    )
    db.add(teaching_office)
    db.flush()
    
    # Create self evaluation
    evaluation = SelfEvaluation(
        teaching_office_id=teaching_office.id,
        evaluation_year=2024,
        content={
            "teaching_process_management": "教学过程管理规范",
            "course_construction": "课程建设良好",
            "teaching_reform_projects": 3,
            "honorary_awards": 2,
            "teaching_quality": "教学质量优秀"
        },
        status="finalized"
    )
    db.add(evaluation)
    db.flush()
    
    # Create AI score
    ai_score = AIScore(
        evaluation_id=evaluation.id,
        total_score=85.5,
        indicator_scores=[
            {"indicator": "teaching_process_management", "score": 90.0, "reasoning": "管理规范"},
            {"indicator": "course_construction", "score": 85.0, "reasoning": "建设良好"},
            {"indicator": "teaching_reform_projects", "score": 88.0, "reasoning": "项目突出"},
            {"indicator": "honorary_awards", "score": 80.0, "reasoning": "荣誉较多"},
            {"indicator": "teaching_quality", "score": 84.0, "reasoning": "质量优秀"}
        ],
        parsed_reform_projects=3,
        parsed_honorary_awards=2
    )
    db.add(ai_score)
    
    # Create manual scores
    manual_score1 = ManualScore(
        evaluation_id=evaluation.id,
        reviewer_id=evaluation_office_user.id,
        reviewer_name="评审员1",
        reviewer_role="evaluation_team",
        weight=0.6,
        scores=[
            {"indicator": "teaching_process_management", "score": 88.0, "comment": "很好"},
            {"indicator": "course_construction", "score": 82.0, "comment": "良好"},
            {"indicator": "teaching_reform_projects", "score": 90.0, "comment": "优秀"},
            {"indicator": "honorary_awards", "score": 78.0, "comment": "不错"},
            {"indicator": "teaching_quality", "score": 86.0, "comment": "优秀"}
        ]
    )
    db.add(manual_score1)
    
    manual_score2 = ManualScore(
        evaluation_id=evaluation.id,
        reviewer_id=evaluation_office_user.id,
        reviewer_name="评审员2",
        reviewer_role="evaluation_office",
        weight=0.4,
        scores=[
            {"indicator": "teaching_process_management", "score": 85.0, "comment": "良好"},
            {"indicator": "course_construction", "score": 80.0, "comment": "一般"},
            {"indicator": "teaching_reform_projects", "score": 87.0, "comment": "很好"},
            {"indicator": "honorary_awards", "score": 75.0, "comment": "待提升"},
            {"indicator": "teaching_quality", "score": 83.0, "comment": "良好"}
        ]
    )
    db.add(manual_score2)
    
    # Create final score
    final_score = FinalScore(
        evaluation_id=evaluation.id,
        final_score=85.0,
        summary="综合评分良好",
        determined_by=evaluation_office_user.id
    )
    db.add(final_score)
    
    db.commit()
    db.refresh(evaluation)
    
    return evaluation


def test_generate_insight_summary_service(db: Session, evaluation_with_scores: SelfEvaluation):
    """
    测试感悟总结生成服务
    
    需求: 15.1, 15.2, 15.3, 15.4, 15.5
    """
    service = InsightGenerationService(db)
    
    # Generate insight summary
    summary = service.generate_insight_summary(evaluation_with_scores.id)
    
    # Verify summary is generated
    assert summary is not None
    assert isinstance(summary, str)
    assert len(summary) > 0
    
    # Verify summary contains key elements
    # 需求 15.4: 包含突出指标说明
    assert "突出" in summary or "优秀" in summary or "良好" in summary
    
    # 需求 15.5: 包含待提升指标说明
    # Note: May not always have weak indicators if all scores are good
    
    # Verify summary mentions score level
    assert "85.00" in summary or "优秀" in summary or "良好" in summary
    
    print(f"\n生成的感悟总结:\n{summary}")


def test_save_insight_summary(db: Session, evaluation_with_scores: SelfEvaluation):
    """
    测试保存感悟总结
    
    需求: 15.1
    """
    service = InsightGenerationService(db)
    
    # Generate and save
    insight = service.generate_and_save(evaluation_with_scores.id)
    
    # Verify saved to database
    assert insight.id is not None
    assert insight.evaluation_id == evaluation_with_scores.id
    assert insight.summary is not None
    assert insight.generated_at is not None
    
    # Verify can be retrieved
    retrieved = db.query(InsightSummary).filter(
        InsightSummary.evaluation_id == evaluation_with_scores.id
    ).first()
    
    assert retrieved is not None
    assert retrieved.id == insight.id
    assert retrieved.summary == insight.summary


def test_insight_summary_update(db: Session, evaluation_with_scores: SelfEvaluation):
    """
    测试更新已存在的感悟总结
    
    需求: 15.1
    """
    service = InsightGenerationService(db)
    
    # First generation
    insight1 = service.generate_and_save(evaluation_with_scores.id)
    first_id = insight1.id
    first_summary = insight1.summary
    
    # Second generation (should update, not create new)
    insight2 = service.generate_and_save(evaluation_with_scores.id)
    
    # Verify same ID (updated, not created new)
    assert insight2.id == first_id
    
    # Verify only one record exists
    count = db.query(InsightSummary).filter(
        InsightSummary.evaluation_id == evaluation_with_scores.id
    ).count()
    assert count == 1


def test_generate_insight_api(
    client: TestClient,
    db: Session,
    evaluation_office_token: str,
    evaluation_with_scores: SelfEvaluation
):
    """
    测试通过API生成感悟总结
    
    需求: 15.1, 15.6
    """
    response = client.post(
        "/api/insight/generate",
        json={
            "evaluation_id": str(evaluation_with_scores.id)
        },
        headers={"Authorization": f"Bearer {evaluation_office_token}"}
    )
    
    assert response.status_code == 200
    data = response.json()
    
    # Verify response structure
    assert "insight_summary" in data
    assert "message" in data
    
    insight = data["insight_summary"]
    assert "id" in insight
    assert "evaluation_id" in insight
    assert "summary" in insight
    assert "generated_at" in insight
    
    # Verify summary content
    assert len(insight["summary"]) > 0
    
    # 需求 15.6: 禁止人工填写感悟总结（系统自动生成）
    assert "successfully" in data["message"].lower()


def test_get_insight_summary_api(
    client: TestClient,
    db: Session,
    evaluation_office_token: str,
    evaluation_with_scores: SelfEvaluation
):
    """
    测试通过API查询感悟总结
    
    需求: 15.1
    """
    # First generate
    service = InsightGenerationService(db)
    insight = service.generate_and_save(evaluation_with_scores.id)
    
    # Then retrieve via API
    response = client.get(
        f"/api/insight/{evaluation_with_scores.id}",
        headers={"Authorization": f"Bearer {evaluation_office_token}"}
    )
    
    assert response.status_code == 200
    data = response.json()
    
    # Verify response structure
    assert data["id"] == str(insight.id)
    assert data["evaluation_id"] == str(evaluation_with_scores.id)
    assert data["summary"] == insight.summary


def test_generate_insight_without_final_score(
    client: TestClient,
    db: Session,
    evaluation_office_token: str
):
    """
    测试在没有最终得分时生成感悟总结应该失败
    
    需求: 15.1
    """
    # Create evaluation without final score
    teaching_office = TeachingOffice(
        name="无最终得分教研室",
        code="NOFS001",
        department="测试学院"
    )
    db.add(teaching_office)
    db.flush()
    
    evaluation = SelfEvaluation(
        teaching_office_id=teaching_office.id,
        evaluation_year=2024,
        content={"test": "data"},
        status="submitted"
    )
    db.add(evaluation)
    db.commit()
    
    response = client.post(
        "/api/insight/generate",
        json={
            "evaluation_id": str(evaluation.id)
        },
        headers={"Authorization": f"Bearer {evaluation_office_token}"}
    )
    
    assert response.status_code == 400
    assert "final score" in response.json()["detail"].lower()


def test_get_nonexistent_insight(
    client: TestClient,
    db: Session,
    evaluation_office_token: str,
    evaluation_with_scores: SelfEvaluation
):
    """
    测试查询不存在的感悟总结
    """
    response = client.get(
        f"/api/insight/{evaluation_with_scores.id}",
        headers={"Authorization": f"Bearer {evaluation_office_token}"}
    )
    
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()


def test_insight_identifies_strong_indicators(db: Session, evaluation_office_user: User):
    """
    测试感悟总结能识别突出指标
    
    需求: 15.2, 15.4
    """
    # Create evaluation with clearly strong indicators
    teaching_office = TeachingOffice(
        name="强项教研室",
        code="STRONG001",
        department="测试学院"
    )
    db.add(teaching_office)
    db.flush()
    
    evaluation = SelfEvaluation(
        teaching_office_id=teaching_office.id,
        evaluation_year=2024,
        content={"test": "data"},
        status="finalized"
    )
    db.add(evaluation)
    db.flush()
    
    # Create scores with clear strong indicators
    ai_score = AIScore(
        evaluation_id=evaluation.id,
        total_score=90.0,
        indicator_scores=[
            {"indicator": "teaching_reform_projects", "score": 95.0, "reasoning": "优秀"},
            {"indicator": "honorary_awards", "score": 92.0, "reasoning": "优秀"},
            {"indicator": "teaching_quality", "score": 88.0, "reasoning": "良好"},
            {"indicator": "course_construction", "score": 70.0, "reasoning": "一般"}
        ],
        parsed_reform_projects=5,
        parsed_honorary_awards=4
    )
    db.add(ai_score)
    
    final_score = FinalScore(
        evaluation_id=evaluation.id,
        final_score=90.0,
        summary="优秀",
        determined_by=evaluation_office_user.id
    )
    db.add(final_score)
    db.commit()
    
    # Generate insight
    service = InsightGenerationService(db)
    summary = service.generate_insight_summary(evaluation.id)
    
    # Verify strong indicators are mentioned
    # 需求 15.4: 包含突出指标说明
    assert "教学改革项目" in summary or "teaching_reform_projects" in summary
    assert "突出" in summary or "优秀" in summary
    
    print(f"\n强项识别测试 - 生成的感悟总结:\n{summary}")


def test_insight_identifies_weak_indicators(db: Session, evaluation_office_user: User):
    """
    测试感悟总结能识别待提升指标
    
    需求: 15.3, 15.5
    """
    # Create evaluation with clearly weak indicators
    teaching_office = TeachingOffice(
        name="弱项教研室",
        code="WEAK001",
        department="测试学院"
    )
    db.add(teaching_office)
    db.flush()
    
    evaluation = SelfEvaluation(
        teaching_office_id=teaching_office.id,
        evaluation_year=2024,
        content={"test": "data"},
        status="finalized"
    )
    db.add(evaluation)
    db.flush()
    
    # Create scores with clear weak indicators
    ai_score = AIScore(
        evaluation_id=evaluation.id,
        total_score=65.0,
        indicator_scores=[
            {"indicator": "teaching_reform_projects", "score": 80.0, "reasoning": "良好"},
            {"indicator": "honorary_awards", "score": 55.0, "reasoning": "待提升"},
            {"indicator": "course_construction", "score": 50.0, "reasoning": "不足"},
            {"indicator": "teaching_quality", "score": 75.0, "reasoning": "一般"}
        ],
        parsed_reform_projects=2,
        parsed_honorary_awards=1
    )
    db.add(ai_score)
    
    final_score = FinalScore(
        evaluation_id=evaluation.id,
        final_score=65.0,
        summary="合格",
        determined_by=evaluation_office_user.id
    )
    db.add(final_score)
    db.commit()
    
    # Generate insight
    service = InsightGenerationService(db)
    summary = service.generate_insight_summary(evaluation.id)
    
    # Verify weak indicators are mentioned
    # 需求 15.5: 包含待提升指标说明
    assert "待提升" in summary or "提升" in summary or "加强" in summary
    assert "建议" in summary or "改进" in summary
    
    print(f"\n弱项识别测试 - 生成的感悟总结:\n{summary}")


def test_distribute_generates_insight_summary(
    client: TestClient,
    db: Session,
    evaluation_office_token: str,
    approved_evaluation: tuple
):
    """
    测试分发结果时自动生成感悟总结
    
    需求: 14.6, 15.1, 15.6
    """
    _, evaluation = approved_evaluation
    
    # First, publish the evaluation
    pub_response = client.post(
        "/api/publication/publish",
        json={
            "evaluation_ids": [str(evaluation.id)]
        },
        headers={"Authorization": f"Bearer {evaluation_office_token}"}
    )
    assert pub_response.status_code == 200
    publication_id = pub_response.json()["publication_id"]
    
    # Now distribute the results
    response = client.post(
        "/api/publication/distribute",
        json={
            "publication_id": publication_id
        },
        headers={"Authorization": f"Bearer {evaluation_office_token}"}
    )
    
    assert response.status_code == 200
    
    # Verify insight summary was generated
    # 需求 15.1: 基于综合考核指标自动生成感悟总结
    # 需求 15.6: 禁止人工填写感悟总结
    insight = db.query(InsightSummary).filter(
        InsightSummary.evaluation_id == evaluation.id
    ).first()
    
    assert insight is not None
    assert insight.summary is not None
    assert len(insight.summary) > 0
    
    # Verify insight can be retrieved via API
    # 需求 14.6: 分发至教研室端时显示系统生成的感悟总结
    insight_response = client.get(
        f"/api/insight/{evaluation.id}",
        headers={"Authorization": f"Bearer {evaluation_office_token}"}
    )
    
    assert insight_response.status_code == 200
    insight_data = insight_response.json()
    assert insight_data["summary"] == insight.summary

