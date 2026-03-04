"""
测试异常处理API

验证需求: 8.1, 8.2, 8.3, 8.4
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from uuid import uuid4
from datetime import datetime

from app.models.anomaly import Anomaly
from app.models.self_evaluation import SelfEvaluation
from app.models.teaching_office import TeachingOffice
from app.models.user import User
from app.models.operation_log import OperationLog


def test_handle_anomaly_reject(client: TestClient, db: Session, evaluation_office_token: str):
    """
    测试打回教研室补充材料
    
    需求: 8.2, 8.4
    """
    # Create teaching office
    teaching_office = TeachingOffice(
        name="Test Teaching Office",
        code="TEST001",
        department="Test Department"
    )
    db.add(teaching_office)
    db.commit()
    
    # Create evaluation
    evaluation = SelfEvaluation(
        teaching_office_id=teaching_office.id,
        evaluation_year=2024,
        content={
            "teachingProcessManagement": "Test content",
            "teachingReformProjects": 5,
            "honoraryAwards": 3
        },
        status="submitted"
    )
    db.add(evaluation)
    db.commit()
    
    # Create anomaly
    anomaly = Anomaly(
        evaluation_id=evaluation.id,
        type="count_mismatch",
        indicator="teaching_reform_projects",
        declared_count=5,
        parsed_count=3,
        description="自评表填写5项教学改革项目,附件仅解析出3份证书",
        status="pending"
    )
    db.add(anomaly)
    db.commit()
    
    # Handle anomaly - reject
    response = client.post(
        "/api/review/handle-anomaly",
        json={
            "anomaly_id": str(anomaly.id),
            "action": "reject",
            "reject_reason": "请补充缺失的2份教学改革项目证书"
        },
        headers={"Authorization": f"Bearer {evaluation_office_token}"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "handled"
    assert "rejected" in data["message"].lower()
    
    # Verify anomaly was updated
    db.refresh(anomaly)
    assert anomaly.status == "handled"
    assert anomaly.handled_action == "reject"
    assert anomaly.handled_at is not None
    
    # Verify evaluation was unlocked
    db.refresh(evaluation)
    assert evaluation.status == "rejected"
    
    # Verify operation log was created
    log = db.query(OperationLog).filter(
        OperationLog.operation_type == "handle_anomaly",
        OperationLog.target_id == anomaly.id
    ).first()
    assert log is not None
    assert log.details["action"] == "reject"
    assert log.details["reject_reason"] == "请补充缺失的2份教学改革项目证书"


def test_handle_anomaly_correct(client: TestClient, db: Session, evaluation_office_token: str):
    """
    测试直接修正异常数据
    
    需求: 8.3, 8.4
    """
    # Create teaching office
    teaching_office = TeachingOffice(
        name="Test Teaching Office",
        code="TEST002",
        department="Test Department"
    )
    db.add(teaching_office)
    db.commit()
    
    # Create evaluation
    evaluation = SelfEvaluation(
        teaching_office_id=teaching_office.id,
        evaluation_year=2024,
        content={
            "teachingProcessManagement": "Test content",
            "teachingReformProjects": 5,
            "honoraryAwards": 3
        },
        status="submitted"
    )
    db.add(evaluation)
    db.commit()
    
    # Create anomaly
    anomaly = Anomaly(
        evaluation_id=evaluation.id,
        type="count_mismatch",
        indicator="teaching_reform_projects",
        declared_count=5,
        parsed_count=3,
        description="自评表填写5项教学改革项目,附件仅解析出3份证书",
        status="pending"
    )
    db.add(anomaly)
    db.commit()
    
    # Handle anomaly - correct
    response = client.post(
        "/api/review/handle-anomaly",
        json={
            "anomaly_id": str(anomaly.id),
            "action": "correct",
            "corrected_data": {
                "teachingReformProjects": 3
            }
        },
        headers={"Authorization": f"Bearer {evaluation_office_token}"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "handled"
    assert "corrected" in data["message"].lower()
    
    # Verify anomaly was updated
    db.refresh(anomaly)
    assert anomaly.status == "handled"
    assert anomaly.handled_action == "correct"
    assert anomaly.handled_at is not None
    
    # Verify evaluation content was corrected
    db.refresh(evaluation)
    assert evaluation.content["teachingReformProjects"] == 3
    
    # Verify operation log was created
    log = db.query(OperationLog).filter(
        OperationLog.operation_type == "handle_anomaly",
        OperationLog.target_id == anomaly.id
    ).first()
    assert log is not None
    assert log.details["action"] == "correct"
    assert log.details["corrected_data"]["teachingReformProjects"] == 3


def test_handle_anomaly_already_handled(client: TestClient, db: Session, evaluation_office_token: str):
    """
    测试处理已处理的异常应该失败
    """
    # Create teaching office
    teaching_office = TeachingOffice(
        name="Test Teaching Office",
        code="TEST003",
        department="Test Department"
    )
    db.add(teaching_office)
    db.commit()
    
    # Create evaluation
    evaluation = SelfEvaluation(
        teaching_office_id=teaching_office.id,
        evaluation_year=2024,
        content={
            "teachingProcessManagement": "Test content",
            "teachingReformProjects": 5
        },
        status="submitted"
    )
    db.add(evaluation)
    db.commit()
    
    # Create already handled anomaly
    user = db.query(User).filter(User.role == "evaluation_office").first()
    anomaly = Anomaly(
        evaluation_id=evaluation.id,
        type="count_mismatch",
        indicator="teaching_reform_projects",
        declared_count=5,
        parsed_count=3,
        description="Test anomaly",
        status="handled",
        handled_by=user.id,
        handled_action="reject",
        handled_at=datetime.utcnow()
    )
    db.add(anomaly)
    db.commit()
    
    # Try to handle again
    response = client.post(
        "/api/review/handle-anomaly",
        json={
            "anomaly_id": str(anomaly.id),
            "action": "reject",
            "reject_reason": "Test reason"
        },
        headers={"Authorization": f"Bearer {evaluation_office_token}"}
    )
    
    assert response.status_code == 400
    assert "already been handled" in response.json()["detail"]


def test_handle_anomaly_invalid_action(client: TestClient, db: Session, evaluation_office_token: str):
    """
    测试无效的action应该失败
    """
    response = client.post(
        "/api/review/handle-anomaly",
        json={
            "anomaly_id": str(uuid4()),
            "action": "invalid_action"
        },
        headers={"Authorization": f"Bearer {evaluation_office_token}"}
    )
    
    assert response.status_code == 400
    assert "Invalid action" in response.json()["detail"]


def test_handle_anomaly_missing_reject_reason(client: TestClient, db: Session, evaluation_office_token: str):
    """
    测试reject action缺少reject_reason应该失败
    """
    response = client.post(
        "/api/review/handle-anomaly",
        json={
            "anomaly_id": str(uuid4()),
            "action": "reject"
        },
        headers={"Authorization": f"Bearer {evaluation_office_token}"}
    )
    
    assert response.status_code == 400
    assert "reject_reason is required" in response.json()["detail"]


def test_handle_anomaly_missing_corrected_data(client: TestClient, db: Session, evaluation_office_token: str):
    """
    测试correct action缺少corrected_data应该失败
    """
    response = client.post(
        "/api/review/handle-anomaly",
        json={
            "anomaly_id": str(uuid4()),
            "action": "correct"
        },
        headers={"Authorization": f"Bearer {evaluation_office_token}"}
    )
    
    assert response.status_code == 400
    assert "corrected_data is required" in response.json()["detail"]


def test_get_anomalies_list(client: TestClient, db: Session, evaluation_office_token: str):
    """
    测试查询异常数据列表
    
    需求: 8.1
    """
    # Create teaching office
    teaching_office = TeachingOffice(
        name="Test Teaching Office",
        code="TEST004",
        department="Test Department"
    )
    db.add(teaching_office)
    db.commit()
    
    # Create evaluation
    evaluation = SelfEvaluation(
        teaching_office_id=teaching_office.id,
        evaluation_year=2024,
        content={"test": "content"},
        status="submitted"
    )
    db.add(evaluation)
    db.commit()
    
    # Create multiple anomalies
    anomaly1 = Anomaly(
        evaluation_id=evaluation.id,
        type="count_mismatch",
        indicator="teaching_reform_projects",
        declared_count=5,
        parsed_count=3,
        description="Test anomaly 1",
        status="pending"
    )
    anomaly2 = Anomaly(
        evaluation_id=evaluation.id,
        type="count_mismatch",
        indicator="honorary_awards",
        declared_count=2,
        parsed_count=1,
        description="Test anomaly 2",
        status="pending"
    )
    db.add_all([anomaly1, anomaly2])
    db.commit()
    
    # Get all anomalies
    response = client.get(
        "/api/review/anomalies",
        headers={"Authorization": f"Bearer {evaluation_office_token}"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["total"] >= 2
    assert len(data["anomalies"]) >= 2


def test_get_anomalies_filtered_by_evaluation(client: TestClient, db: Session, evaluation_office_token: str):
    """
    测试按evaluation_id筛选异常数据
    
    需求: 8.1
    """
    # Create teaching office
    teaching_office = TeachingOffice(
        name="Test Teaching Office",
        code="TEST005",
        department="Test Department"
    )
    db.add(teaching_office)
    db.commit()
    
    # Create evaluation
    evaluation = SelfEvaluation(
        teaching_office_id=teaching_office.id,
        evaluation_year=2024,
        content={"test": "content"},
        status="submitted"
    )
    db.add(evaluation)
    db.commit()
    
    # Create anomaly
    anomaly = Anomaly(
        evaluation_id=evaluation.id,
        type="count_mismatch",
        indicator="teaching_reform_projects",
        declared_count=5,
        parsed_count=3,
        description="Test anomaly",
        status="pending"
    )
    db.add(anomaly)
    db.commit()
    
    # Get anomalies for this evaluation
    response = client.get(
        f"/api/review/anomalies?evaluation_id={evaluation.id}",
        headers={"Authorization": f"Bearer {evaluation_office_token}"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["total"] >= 1
    assert all(a["evaluation_id"] == str(evaluation.id) for a in data["anomalies"])


def test_get_anomaly_detail(client: TestClient, db: Session, evaluation_office_token: str):
    """
    测试查询单个异常数据详情
    
    需求: 8.1
    """
    # Create teaching office
    teaching_office = TeachingOffice(
        name="Test Teaching Office",
        code="TEST006",
        department="Test Department"
    )
    db.add(teaching_office)
    db.commit()
    
    # Create evaluation
    evaluation = SelfEvaluation(
        teaching_office_id=teaching_office.id,
        evaluation_year=2024,
        content={"test": "content"},
        status="submitted"
    )
    db.add(evaluation)
    db.commit()
    
    # Create anomaly
    anomaly = Anomaly(
        evaluation_id=evaluation.id,
        type="count_mismatch",
        indicator="teaching_reform_projects",
        declared_count=5,
        parsed_count=3,
        description="详细对比说明: 自评表填写5项,附件解析3项",
        status="pending"
    )
    db.add(anomaly)
    db.commit()
    
    # Get anomaly detail
    response = client.get(
        f"/api/review/anomalies/{anomaly.id}",
        headers={"Authorization": f"Bearer {evaluation_office_token}"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == str(anomaly.id)
    assert data["type"] == "count_mismatch"
    assert data["indicator"] == "teaching_reform_projects"
    assert data["declared_count"] == 5
    assert data["parsed_count"] == 3
    assert "详细对比说明" in data["description"]


def test_handle_anomaly_requires_evaluation_office_role(client: TestClient, db: Session, teaching_office_token: str):
    """
    测试只有考评办公室可以处理异常
    """
    response = client.post(
        "/api/review/handle-anomaly",
        json={
            "anomaly_id": str(uuid4()),
            "action": "reject",
            "reject_reason": "Test"
        },
        headers={"Authorization": f"Bearer {teaching_office_token}"}
    )
    
    assert response.status_code == 403
    assert "Access denied" in response.json()["detail"]
