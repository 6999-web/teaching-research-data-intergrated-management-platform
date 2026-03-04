"""
测试校长办公会端结果审定API

Feature: teaching-office-evaluation-system
Task: 15.1 实现结果审定API
需求: 12.1, 12.2, 12.3, 12.4, 12.5, 12.6, 12.7
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from uuid import uuid4
from datetime import datetime

from app.models.user import User
from app.models.teaching_office import TeachingOffice
from app.models.self_evaluation import SelfEvaluation
from app.models.final_score import FinalScore
from app.models.approval import Approval


# president_office_user and president_office_token fixtures are provided by conftest.py


@pytest.fixture
def teaching_office_with_evaluation(db: Session) -> tuple:
    """创建教研室和评估数据"""
    # Create teaching office
    teaching_office = TeachingOffice(
        name="计算机教研室",
        code="CS001",
        department="计算机学院"
    )
    db.add(teaching_office)
    db.commit()
    db.refresh(teaching_office)
    
    # Create evaluation
    evaluation = SelfEvaluation(
        teaching_office_id=teaching_office.id,
        evaluation_year=2024,
        content={
            "teachingProcessManagement": "教学过程管理良好",
            "courseConstruction": "课程建设完善",
            "teachingReformProjects": 3,
            "honoraryAwards": 2
        },
        status="finalized"
    )
    db.add(evaluation)
    db.commit()
    db.refresh(evaluation)
    
    # Create final score
    final_score = FinalScore(
        evaluation_id=evaluation.id,
        final_score=87.5,
        summary="综合评分良好",
        determined_by=uuid4()
    )
    db.add(final_score)
    db.commit()
    
    return teaching_office, evaluation


def test_approve_evaluation_success(
    client: TestClient,
    db: Session,
    president_office_token: str,
    teaching_office_with_evaluation: tuple
):
    """
    测试成功审定（同意公示）
    
    需求: 12.1, 12.2, 12.4, 12.5
    """
    _, evaluation = teaching_office_with_evaluation
    
    response = client.post(
        "/api/president-office/approve",
        json={
            "evaluation_ids": [str(evaluation.id)],
            "decision": "approve"
        },
        headers={"Authorization": f"Bearer {president_office_token}"}
    )
    
    if response.status_code != 200:
        print(f"Error response: {response.text}")
    
    assert response.status_code == 200
    data = response.json()
    
    # Verify response structure
    assert "approval_id" in data
    assert data["decision"] == "approve"
    assert "approved_at" in data
    assert "Management office can now initiate publication" in data["message"]
    assert data["synced_to_management"] is True
    
    # Verify approval record was created
    from uuid import UUID as UUIDType
    approval = db.query(Approval).filter(
        Approval.id == UUIDType(data["approval_id"])
    ).first()
    assert approval is not None
    assert approval.decision == "approve"
    assert approval.reject_reason is None
    
    # Verify evaluation status was updated
    db.refresh(evaluation)
    assert evaluation.status == "approved"


def test_reject_evaluation_success(
    client: TestClient,
    db: Session,
    president_office_token: str,
    teaching_office_with_evaluation: tuple
):
    """
    测试成功驳回
    
    需求: 12.1, 12.3, 12.6, 12.7
    """
    _, evaluation = teaching_office_with_evaluation
    reject_reason = "数据不完整，需要补充材料"
    
    response = client.post(
        "/api/president-office/approve",
        json={
            "evaluation_ids": [str(evaluation.id)],
            "decision": "reject",
            "reject_reason": reject_reason
        },
        headers={"Authorization": f"Bearer {president_office_token}"}
    )
    
    assert response.status_code == 200
    data = response.json()
    
    # Verify response structure
    assert "approval_id" in data
    assert data["decision"] == "reject"
    assert "approved_at" in data
    assert reject_reason in data["message"]
    assert "Management office has been notified" in data["message"]
    assert data["synced_to_management"] is True
    
    # Verify approval record was created with reject reason
    from uuid import UUID as UUIDType
    approval = db.query(Approval).filter(
        Approval.id == UUIDType(data["approval_id"])
    ).first()
    assert approval is not None
    assert approval.decision == "reject"
    assert approval.reject_reason == reject_reason
    
    # Verify evaluation status was updated
    db.refresh(evaluation)
    assert evaluation.status == "rejected_by_president"


def test_approve_multiple_evaluations(
    client: TestClient,
    db: Session,
    president_office_token: str
):
    """
    测试批量审定多个评估
    
    需求: 12.1, 12.2, 12.4, 12.5
    """
    # Create multiple evaluations
    evaluation_ids = []
    for i in range(3):
        teaching_office = TeachingOffice(
            name=f"教研室{i}",
            code=f"TO{i:03d}",
            department="测试学院"
        )
        db.add(teaching_office)
        db.commit()
        
        evaluation = SelfEvaluation(
            teaching_office_id=teaching_office.id,
            evaluation_year=2024,
            content={"test": f"data{i}"},
            status="finalized"
        )
        db.add(evaluation)
        db.commit()
        
        final_score = FinalScore(
            evaluation_id=evaluation.id,
            final_score=85.0 + i,
            summary=f"评分{i}",
            determined_by=uuid4()
        )
        db.add(final_score)
        db.commit()
        
        evaluation_ids.append(str(evaluation.id))
    
    response = client.post(
        "/api/president-office/approve",
        json={
            "evaluation_ids": evaluation_ids,
            "decision": "approve"
        },
        headers={"Authorization": f"Bearer {president_office_token}"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["decision"] == "approve"
    
    # Verify all evaluations were updated
    from uuid import UUID as UUIDType
    for eval_id in evaluation_ids:
        evaluation = db.query(SelfEvaluation).filter(
            SelfEvaluation.id == UUIDType(eval_id)
        ).first()
        assert evaluation.status == "approved"


def test_approve_invalid_decision(
    client: TestClient,
    db: Session,
    president_office_token: str,
    teaching_office_with_evaluation: tuple
):
    """
    测试无效的决定值
    
    需求: 12.1
    """
    _, evaluation = teaching_office_with_evaluation
    
    response = client.post(
        "/api/president-office/approve",
        json={
            "evaluation_ids": [str(evaluation.id)],
            "decision": "invalid_decision"
        },
        headers={"Authorization": f"Bearer {president_office_token}"}
    )
    
    assert response.status_code == 400
    assert "Invalid decision" in response.json()["detail"]


def test_reject_without_reason(
    client: TestClient,
    db: Session,
    president_office_token: str,
    teaching_office_with_evaluation: tuple
):
    """
    测试驳回时缺少驳回原因
    
    需求: 12.6
    """
    _, evaluation = teaching_office_with_evaluation
    
    response = client.post(
        "/api/president-office/approve",
        json={
            "evaluation_ids": [str(evaluation.id)],
            "decision": "reject"
            # Missing reject_reason
        },
        headers={"Authorization": f"Bearer {president_office_token}"}
    )
    
    assert response.status_code == 400
    assert "reject_reason is required" in response.json()["detail"]


def test_approve_nonexistent_evaluation(
    client: TestClient,
    db: Session,
    president_office_token: str
):
    """
    测试审定不存在的评估
    
    需求: 12.1
    """
    fake_id = uuid4()
    
    response = client.post(
        "/api/president-office/approve",
        json={
            "evaluation_ids": [str(fake_id)],
            "decision": "approve"
        },
        headers={"Authorization": f"Bearer {president_office_token}"}
    )
    
    assert response.status_code == 404
    assert f"Evaluation with id {fake_id} not found" in response.json()["detail"]


def test_approve_without_authentication(
    client: TestClient,
    db: Session,
    teaching_office_with_evaluation: tuple
):
    """
    测试未认证时无法审定
    
    需求: 12.1
    """
    _, evaluation = teaching_office_with_evaluation
    
    response = client.post(
        "/api/president-office/approve",
        json={
            "evaluation_ids": [str(evaluation.id)],
            "decision": "approve"
        }
    )
    
    assert response.status_code == 401


def test_approve_with_wrong_role(
    client: TestClient,
    db: Session,
    evaluation_office_token: str,  # Use evaluation_office user (wrong role)
    teaching_office_with_evaluation: tuple
):
    """
    测试非校长办公会角色无法审定
    
    需求: 12.1
    """
    _, evaluation = teaching_office_with_evaluation
    
    response = client.post(
        "/api/president-office/approve",
        json={
            "evaluation_ids": [str(evaluation.id)],
            "decision": "approve"
        },
        headers={"Authorization": f"Bearer {evaluation_office_token}"}
    )
    
    assert response.status_code == 403
    assert "Access denied" in response.json()["detail"]


def test_approve_empty_evaluation_list(
    client: TestClient,
    db: Session,
    president_office_token: str
):
    """
    测试空评估列表
    
    需求: 12.1
    """
    response = client.post(
        "/api/president-office/approve",
        json={
            "evaluation_ids": [],
            "decision": "approve"
        },
        headers={"Authorization": f"Bearer {president_office_token}"}
    )
    
    # Should accept empty list (no evaluations to approve)
    assert response.status_code == 200


def test_approve_with_reject_reason_ignored(
    client: TestClient,
    db: Session,
    president_office_token: str,
    teaching_office_with_evaluation: tuple
):
    """
    测试同意公示时驳回原因被忽略
    
    需求: 12.2
    """
    _, evaluation = teaching_office_with_evaluation
    
    response = client.post(
        "/api/president-office/approve",
        json={
            "evaluation_ids": [str(evaluation.id)],
            "decision": "approve",
            "reject_reason": "这个原因应该被忽略"
        },
        headers={"Authorization": f"Bearer {president_office_token}"}
    )
    
    assert response.status_code == 200
    data = response.json()
    
    # Verify approval record doesn't have reject_reason
    from uuid import UUID as UUIDType
    approval = db.query(Approval).filter(
        Approval.id == UUIDType(data["approval_id"])
    ).first()
    assert approval.reject_reason is None
