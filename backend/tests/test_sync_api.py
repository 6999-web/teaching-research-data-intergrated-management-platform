"""
测试数据同步API

Feature: teaching-office-evaluation-system
Task: 13.1 实现数据同步API
需求: 9.1, 9.2, 9.3, 9.4, 9.5, 9.6, 9.7, 9.8
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from uuid import uuid4
from datetime import datetime

from app.main import app
from app.models.self_evaluation import SelfEvaluation
from app.models.teaching_office import TeachingOffice
from app.models.user import User
from app.models.ai_score import AIScore
from app.models.manual_score import ManualScore
from app.models.final_score import FinalScore
from app.models.attachment import Attachment
from app.models.anomaly import Anomaly
from app.core.security import get_password_hash


@pytest.fixture
def evaluation_office_user(db: Session) -> User:
    """创建考评办公室用户"""
    user = User(
        id=uuid4(),
        username="eval_office_user",
        password_hash=get_password_hash("password123"),
        role="evaluation_office",
        name="考评办公室用户",
        email="eval@example.com"
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@pytest.fixture
def teaching_office(db: Session) -> TeachingOffice:
    """创建教研室"""
    office = TeachingOffice(
        id=uuid4(),
        name="计算机教研室",
        code="CS001",
        department="计算机学院"
    )
    db.add(office)
    db.commit()
    db.refresh(office)
    return office


@pytest.fixture
def complete_evaluation(
    db: Session, 
    teaching_office: TeachingOffice,
    evaluation_office_user: User
) -> SelfEvaluation:
    """创建完整的自评表（包含AI评分、手动评分、最终得分）"""
    # Create evaluation
    evaluation = SelfEvaluation(
        id=uuid4(),
        teaching_office_id=teaching_office.id,
        evaluation_year=2024,
        content={
            "teachingProcessManagement": "教学过程管理良好",
            "courseConstruction": "课程建设完善",
            "teachingReformProjects": 3,
            "honoraryAwards": 2
        },
        status="finalized",
        submitted_at=datetime.utcnow()
    )
    db.add(evaluation)
    db.flush()
    
    # Add AI score
    ai_score = AIScore(
        id=uuid4(),
        evaluation_id=evaluation.id,
        total_score=85.5,
        indicator_scores=[
            {"indicator": "教学过程管理", "score": 90, "reasoning": "管理规范"},
            {"indicator": "课程建设", "score": 85, "reasoning": "建设完善"}
        ],
        parsed_reform_projects=3,
        parsed_honorary_awards=2,
        scored_at=datetime.utcnow()
    )
    db.add(ai_score)
    
    # Add manual score
    manual_score = ManualScore(
        id=uuid4(),
        evaluation_id=evaluation.id,
        reviewer_id=evaluation_office_user.id,
        reviewer_name=evaluation_office_user.name,
        reviewer_role="evaluation_office",
        weight=0.5,
        scores=[
            {"indicator": "教学过程管理", "score": 88, "comment": "良好"}
        ],
        submitted_at=datetime.utcnow()
    )
    db.add(manual_score)
    
    # Add final score
    final_score = FinalScore(
        id=uuid4(),
        evaluation_id=evaluation.id,
        final_score=87.0,
        summary="综合评分良好",
        determined_by=evaluation_office_user.id,
        determined_at=datetime.utcnow()
    )
    db.add(final_score)
    
    # Add attachment
    attachment = Attachment(
        id=uuid4(),
        evaluation_id=evaluation.id,
        indicator="教学改革项目",
        file_name="project1.pdf",
        file_size=1024000,
        file_type="application/pdf",
        storage_path="/attachments/project1.pdf",
        classified_by="ai",
        uploaded_at=datetime.utcnow()
    )
    db.add(attachment)
    
    # Add anomaly (handled)
    anomaly = Anomaly(
        id=uuid4(),
        evaluation_id=evaluation.id,
        type="count_mismatch",
        indicator="教学改革项目",
        declared_count=3,
        parsed_count=2,
        description="填写3项，解析出2项",
        status="handled",
        handled_by=evaluation_office_user.id,
        handled_action="correct",
        handled_at=datetime.utcnow()
    )
    db.add(anomaly)
    
    db.commit()
    db.refresh(evaluation)
    return evaluation


def test_sync_to_president_office_success(
    client: TestClient,
    db: Session,
    evaluation_office_user: User,
    complete_evaluation: SelfEvaluation,
    evaluation_office_token: str
):
    """
    测试成功同步数据至校长办公会
    
    需求: 9.1, 9.2, 9.3, 9.4, 9.5, 9.6, 9.7
    """
    response = client.post(
        "/api/review/sync-to-president-office",
        json={
            "evaluation_ids": [str(complete_evaluation.id)]
        },
        headers={"Authorization": f"Bearer {evaluation_office_token}"}
    )
    
    assert response.status_code == 200
    data = response.json()
    
    # Verify response structure
    assert "sync_task_id" in data
    assert data["status"] == "syncing"
    assert data["synced_count"] == 0  # Initial count
    assert data["failed_count"] == 0
    assert "message" in data
    assert "synced_at" in data


def test_sync_without_final_score_fails(
    client: TestClient,
    db: Session,
    teaching_office: TeachingOffice,
    evaluation_office_token: str
):
    """
    测试没有最终得分的自评表无法同步
    
    需求: 9.1
    """
    # Create evaluation without final score
    evaluation = SelfEvaluation(
        id=uuid4(),
        teaching_office_id=teaching_office.id,
        evaluation_year=2024,
        content={"test": "data"},
        status="submitted",
        submitted_at=datetime.utcnow()
    )
    db.add(evaluation)
    db.commit()
    
    response = client.post(
        "/api/review/sync-to-president-office",
        json={
            "evaluation_ids": [str(evaluation.id)]
        },
        headers={"Authorization": f"Bearer {evaluation_office_token}"}
    )
    
    assert response.status_code == 400
    assert "does not have a final score" in response.json()["detail"]


def test_sync_nonexistent_evaluation_fails(
    client: TestClient,
    evaluation_office_token: str
):
    """
    测试同步不存在的自评表失败
    
    需求: 9.1
    """
    fake_id = uuid4()
    response = client.post(
        "/api/review/sync-to-president-office",
        json={
            "evaluation_ids": [str(fake_id)]
        },
        headers={"Authorization": f"Bearer {evaluation_office_token}"}
    )
    
    assert response.status_code == 404
    assert "not found" in response.json()["detail"]


def test_sync_requires_evaluation_office_role(
    client: TestClient,
    db: Session,
    complete_evaluation: SelfEvaluation,
    teaching_office_token: str
):
    """
    测试只有考评办公室可以同步数据
    
    需求: 9.1
    """
    response = client.post(
        "/api/review/sync-to-president-office",
        json={
            "evaluation_ids": [str(complete_evaluation.id)]
        },
        headers={"Authorization": f"Bearer {teaching_office_token}"}
    )
    
    assert response.status_code == 403


def test_get_sync_status(
    client: TestClient,
    db: Session,
    evaluation_office_user: User,
    complete_evaluation: SelfEvaluation,
    evaluation_office_token: str
):
    """
    测试查询同步任务状态
    
    需求: 9.7, 9.8
    """
    # First create a sync task
    response = client.post(
        "/api/review/sync-to-president-office",
        json={
            "evaluation_ids": [str(complete_evaluation.id)]
        },
        headers={"Authorization": f"Bearer {evaluation_office_token}"}
    )
    
    assert response.status_code == 200
    sync_task_id = response.json()["sync_task_id"]
    
    # Query sync status
    status_response = client.get(
        f"/api/review/sync-status/{sync_task_id}",
        headers={"Authorization": f"Bearer {evaluation_office_token}"}
    )
    
    assert status_response.status_code == 200
    status_data = status_response.json()
    
    assert status_data["sync_task_id"] == sync_task_id
    assert status_data["status"] in ["pending", "syncing", "completed", "failed"]
    assert "synced_count" in status_data
    assert "failed_count" in status_data
    assert "total_count" in status_data
    assert "started_at" in status_data


def test_get_sync_status_nonexistent_task(
    client: TestClient,
    evaluation_office_token: str
):
    """
    测试查询不存在的同步任务
    
    需求: 9.7
    """
    fake_id = uuid4()
    response = client.get(
        f"/api/review/sync-status/{fake_id}",
        headers={"Authorization": f"Bearer {evaluation_office_token}"}
    )
    
    assert response.status_code == 404
    assert "not found" in response.json()["detail"]


def test_sync_multiple_evaluations(
    client: TestClient,
    db: Session,
    teaching_office: TeachingOffice,
    evaluation_office_user: User,
    evaluation_office_token: str
):
    """
    测试同步多个自评表
    
    需求: 9.1, 9.3
    """
    # Create multiple complete evaluations
    evaluation_ids = []
    for i in range(3):
        evaluation = SelfEvaluation(
            id=uuid4(),
            teaching_office_id=teaching_office.id,
            evaluation_year=2024,
            content={"test": f"data{i}"},
            status="finalized",
            submitted_at=datetime.utcnow()
        )
        db.add(evaluation)
        db.flush()
        
        # Add final score
        final_score = FinalScore(
            id=uuid4(),
            evaluation_id=evaluation.id,
            final_score=85.0 + i,
            summary=f"Summary {i}",
            determined_by=evaluation_office_user.id,
            determined_at=datetime.utcnow()
        )
        db.add(final_score)
        evaluation_ids.append(str(evaluation.id))
    
    db.commit()
    
    response = client.post(
        "/api/review/sync-to-president-office",
        json={
            "evaluation_ids": evaluation_ids
        },
        headers={"Authorization": f"Bearer {evaluation_office_token}"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "syncing"
