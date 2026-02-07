"""
测试公示操作API

Feature: teaching-office-evaluation-system
Task: 17.1 实现公示操作API
需求: 13.1, 13.2, 13.3, 13.4
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
from app.models.publication import Publication


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
        status="approved"  # 需求 13.1: 仅在审定同意后可以发起公示
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


def test_publish_success(
    client: TestClient,
    db: Session,
    evaluation_office_token: str,
    approved_evaluation: tuple
):
    """
    测试成功发起公示
    
    需求: 13.1, 13.2, 13.4
    """
    _, evaluation = approved_evaluation
    
    response = client.post(
        "/api/publication/publish",
        json={
            "evaluation_ids": [str(evaluation.id)]
        },
        headers={"Authorization": f"Bearer {evaluation_office_token}"}
    )
    
    if response.status_code != 200:
        print(f"Error response: {response.text}")
    
    assert response.status_code == 200
    data = response.json()
    
    # Verify response structure - 需求 13.4: 显示成功提示
    assert "publication_id" in data
    assert "published_at" in data
    assert "message" in data
    assert "successfully" in data["message"].lower()
    
    # Verify publication record was created
    from uuid import UUID as UUIDType
    publication = db.query(Publication).filter(
        Publication.id == UUIDType(data["publication_id"])
    ).first()
    assert publication is not None
    assert str(evaluation.id) in publication.evaluation_ids
    
    # Verify evaluation status was updated to published
    db.refresh(evaluation)
    assert evaluation.status == "published"


def test_publish_unapproved_evaluation(
    client: TestClient,
    db: Session,
    evaluation_office_token: str,
    evaluation_office_user: User
):
    """
    测试未审定的评估无法发起公示
    
    需求: 13.1 - 仅在校长办公会审定同意后显示"发起公示"按钮
    """
    # Create teaching office
    teaching_office = TeachingOffice(
        name="数学教研室",
        code="MATH001",
        department="数学学院"
    )
    db.add(teaching_office)
    db.commit()
    
    # Create evaluation without approved status
    evaluation = SelfEvaluation(
        teaching_office_id=teaching_office.id,
        evaluation_year=2024,
        content={"test": "data"},
        status="finalized"  # Not approved
    )
    db.add(evaluation)
    db.commit()
    
    # Create final score
    final_score = FinalScore(
        evaluation_id=evaluation.id,
        final_score=85.0,
        summary="评分",
        determined_by=evaluation_office_user.id
    )
    db.add(final_score)
    db.commit()
    
    response = client.post(
        "/api/publication/publish",
        json={
            "evaluation_ids": [str(evaluation.id)]
        },
        headers={"Authorization": f"Bearer {evaluation_office_token}"}
    )
    
    assert response.status_code == 400
    assert "not been approved" in response.json()["detail"]


def test_publish_multiple_evaluations(
    client: TestClient,
    db: Session,
    evaluation_office_token: str,
    evaluation_office_user: User
):
    """
    测试批量发起公示
    
    需求: 13.2
    """
    evaluation_ids = []
    
    # Create multiple approved evaluations
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
            status="approved"
        )
        db.add(evaluation)
        db.commit()
        
        final_score = FinalScore(
            evaluation_id=evaluation.id,
            final_score=85.0 + i,
            summary=f"评分{i}",
            determined_by=evaluation_office_user.id
        )
        db.add(final_score)
        db.commit()
        
        evaluation_ids.append(str(evaluation.id))
    
    # Create approval record for all evaluations
    approval = Approval(
        evaluation_ids=evaluation_ids,
        decision="approve",
        approved_by=uuid4(),
        approved_at=datetime.utcnow()
    )
    db.add(approval)
    db.commit()
    
    response = client.post(
        "/api/publication/publish",
        json={
            "evaluation_ids": evaluation_ids
        },
        headers={"Authorization": f"Bearer {evaluation_office_token}"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "publication_id" in data
    
    # Verify all evaluations were updated to published
    from uuid import UUID as UUIDType
    for eval_id in evaluation_ids:
        evaluation = db.query(SelfEvaluation).filter(
            SelfEvaluation.id == UUIDType(eval_id)
        ).first()
        assert evaluation.status == "published"


def test_publish_nonexistent_evaluation(
    client: TestClient,
    db: Session,
    evaluation_office_token: str
):
    """
    测试发起公示不存在的评估
    
    需求: 13.2
    """
    fake_id = uuid4()
    
    response = client.post(
        "/api/publication/publish",
        json={
            "evaluation_ids": [str(fake_id)]
        },
        headers={"Authorization": f"Bearer {evaluation_office_token}"}
    )
    
    assert response.status_code == 404
    assert f"Evaluation with id {fake_id} not found" in response.json()["detail"]


def test_publish_without_authentication(
    client: TestClient,
    db: Session,
    approved_evaluation: tuple
):
    """
    测试未认证时无法发起公示
    
    需求: 13.2
    """
    _, evaluation = approved_evaluation
    
    response = client.post(
        "/api/publication/publish",
        json={
            "evaluation_ids": [str(evaluation.id)]
        }
    )
    
    assert response.status_code == 401


def test_publish_with_wrong_role(
    client: TestClient,
    db: Session,
    teaching_office_token: str,  # Wrong role
    approved_evaluation: tuple
):
    """
    测试非考评办公室角色无法发起公示
    
    需求: 13.2 - 仅考评办公室可以发起公示
    """
    _, evaluation = approved_evaluation
    
    response = client.post(
        "/api/publication/publish",
        json={
            "evaluation_ids": [str(evaluation.id)]
        },
        headers={"Authorization": f"Bearer {teaching_office_token}"}
    )
    
    assert response.status_code == 403
    assert "Access denied" in response.json()["detail"]


def test_publish_already_published_evaluation(
    client: TestClient,
    db: Session,
    evaluation_office_token: str,
    evaluation_office_user: User,
    approved_evaluation: tuple
):
    """
    测试已公示的评估无法再次公示
    
    需求: 13.3 - 禁止自动发起公示（隐含：禁止重复公示）
    """
    _, evaluation = approved_evaluation
    
    # First publication
    response1 = client.post(
        "/api/publication/publish",
        json={
            "evaluation_ids": [str(evaluation.id)]
        },
        headers={"Authorization": f"Bearer {evaluation_office_token}"}
    )
    assert response1.status_code == 200
    
    # Try to publish again
    response2 = client.post(
        "/api/publication/publish",
        json={
            "evaluation_ids": [str(evaluation.id)]
        },
        headers={"Authorization": f"Bearer {evaluation_office_token}"}
    )
    
    assert response2.status_code == 400
    assert "already been published" in response2.json()["detail"]


def test_get_publications_list(
    client: TestClient,
    db: Session,
    evaluation_office_token: str,
    approved_evaluation: tuple
):
    """
    测试查询公示记录列表
    """
    _, evaluation = approved_evaluation
    
    # Create a publication
    client.post(
        "/api/publication/publish",
        json={
            "evaluation_ids": [str(evaluation.id)]
        },
        headers={"Authorization": f"Bearer {evaluation_office_token}"}
    )
    
    # Get publications list
    response = client.get(
        "/api/publication/publications",
        headers={"Authorization": f"Bearer {evaluation_office_token}"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0
    assert "id" in data[0]
    assert "evaluation_ids" in data[0]
    assert "published_at" in data[0]


def test_get_publication_detail(
    client: TestClient,
    db: Session,
    evaluation_office_token: str,
    approved_evaluation: tuple
):
    """
    测试查询单个公示记录详情
    """
    _, evaluation = approved_evaluation
    
    # Create a publication
    pub_response = client.post(
        "/api/publication/publish",
        json={
            "evaluation_ids": [str(evaluation.id)]
        },
        headers={"Authorization": f"Bearer {evaluation_office_token}"}
    )
    publication_id = pub_response.json()["publication_id"]
    
    # Get publication detail
    response = client.get(
        f"/api/publication/publications/{publication_id}",
        headers={"Authorization": f"Bearer {evaluation_office_token}"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == publication_id
    assert str(evaluation.id) in data["evaluation_ids"]


def test_get_nonexistent_publication(
    client: TestClient,
    db: Session,
    evaluation_office_token: str
):
    """
    测试查询不存在的公示记录
    """
    fake_id = uuid4()
    
    response = client.get(
        f"/api/publication/publications/{fake_id}",
        headers={"Authorization": f"Bearer {evaluation_office_token}"}
    )
    
    assert response.status_code == 404
    assert f"Publication with id {fake_id} not found" in response.json()["detail"]


def test_distribute_success(
    client: TestClient,
    db: Session,
    evaluation_office_token: str,
    approved_evaluation: tuple
):
    """
    测试成功分发结果
    
    需求: 14.1, 14.2
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
    
    if response.status_code != 200:
        print(f"Error response: {response.text}")
    
    assert response.status_code == 200
    data = response.json()
    
    # Verify response structure - 需求 14.1, 14.2
    assert "distributed_count" in data
    assert "distributed_at" in data
    assert "message" in data
    assert data["distributed_count"] == 1
    assert "successfully" in data["message"].lower()
    
    # Verify publication distributed_at was updated
    from uuid import UUID as UUIDType
    publication = db.query(Publication).filter(
        Publication.id == UUIDType(publication_id)
    ).first()
    assert publication is not None
    assert publication.distributed_at is not None
    
    # Verify evaluation status was updated to distributed
    db.refresh(evaluation)
    assert evaluation.status == "distributed"


def test_distribute_multiple_evaluations(
    client: TestClient,
    db: Session,
    evaluation_office_token: str,
    evaluation_office_user: User
):
    """
    测试批量分发结果
    
    需求: 14.1, 14.2
    """
    evaluation_ids = []
    
    # Create multiple approved evaluations
    for i in range(3):
        teaching_office = TeachingOffice(
            name=f"分发教研室{i}",
            code=f"DIST{i:03d}",
            department="测试学院"
        )
        db.add(teaching_office)
        db.commit()
        
        evaluation = SelfEvaluation(
            teaching_office_id=teaching_office.id,
            evaluation_year=2024,
            content={"test": f"data{i}"},
            status="approved"
        )
        db.add(evaluation)
        db.commit()
        
        final_score = FinalScore(
            evaluation_id=evaluation.id,
            final_score=85.0 + i,
            summary=f"评分{i}",
            determined_by=evaluation_office_user.id
        )
        db.add(final_score)
        db.commit()
        
        evaluation_ids.append(str(evaluation.id))
    
    # Create approval record
    approval = Approval(
        evaluation_ids=evaluation_ids,
        decision="approve",
        approved_by=uuid4(),
        approved_at=datetime.utcnow()
    )
    db.add(approval)
    db.commit()
    
    # Publish the evaluations
    pub_response = client.post(
        "/api/publication/publish",
        json={
            "evaluation_ids": evaluation_ids
        },
        headers={"Authorization": f"Bearer {evaluation_office_token}"}
    )
    assert pub_response.status_code == 200
    publication_id = pub_response.json()["publication_id"]
    
    # Distribute the results
    response = client.post(
        "/api/publication/distribute",
        json={
            "publication_id": publication_id
        },
        headers={"Authorization": f"Bearer {evaluation_office_token}"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["distributed_count"] == 3
    
    # Verify all evaluations were updated to distributed
    from uuid import UUID as UUIDType
    for eval_id in evaluation_ids:
        evaluation = db.query(SelfEvaluation).filter(
            SelfEvaluation.id == UUIDType(eval_id)
        ).first()
        assert evaluation.status == "distributed"


def test_distribute_nonexistent_publication(
    client: TestClient,
    db: Session,
    evaluation_office_token: str
):
    """
    测试分发不存在的公示记录
    
    需求: 14.1, 14.2
    """
    fake_id = uuid4()
    
    response = client.post(
        "/api/publication/distribute",
        json={
            "publication_id": str(fake_id)
        },
        headers={"Authorization": f"Bearer {evaluation_office_token}"}
    )
    
    assert response.status_code == 404
    assert f"Publication with id {fake_id} not found" in response.json()["detail"]


def test_distribute_already_distributed(
    client: TestClient,
    db: Session,
    evaluation_office_token: str,
    approved_evaluation: tuple
):
    """
    测试重复分发
    
    需求: 14.1, 14.2
    """
    _, evaluation = approved_evaluation
    
    # Publish the evaluation
    pub_response = client.post(
        "/api/publication/publish",
        json={
            "evaluation_ids": [str(evaluation.id)]
        },
        headers={"Authorization": f"Bearer {evaluation_office_token}"}
    )
    assert pub_response.status_code == 200
    publication_id = pub_response.json()["publication_id"]
    
    # First distribution
    response1 = client.post(
        "/api/publication/distribute",
        json={
            "publication_id": publication_id
        },
        headers={"Authorization": f"Bearer {evaluation_office_token}"}
    )
    assert response1.status_code == 200
    
    # Try to distribute again
    response2 = client.post(
        "/api/publication/distribute",
        json={
            "publication_id": publication_id
        },
        headers={"Authorization": f"Bearer {evaluation_office_token}"}
    )
    
    assert response2.status_code == 400
    assert "already been distributed" in response2.json()["detail"]


def test_distribute_without_authentication(
    client: TestClient,
    db: Session,
    approved_evaluation: tuple
):
    """
    测试未认证时无法分发结果
    
    需求: 14.1, 14.2
    """
    _, evaluation = approved_evaluation
    
    # Create a publication directly in the database
    publication = Publication(
        evaluation_ids=[str(evaluation.id)],
        published_by=uuid4(),
        published_at=datetime.utcnow()
    )
    db.add(publication)
    db.commit()
    
    response = client.post(
        "/api/publication/distribute",
        json={
            "publication_id": str(publication.id)
        }
    )
    
    assert response.status_code == 401


def test_distribute_with_wrong_role(
    client: TestClient,
    db: Session,
    teaching_office_token: str,  # Wrong role
    approved_evaluation: tuple
):
    """
    测试非考评办公室角色无法分发结果
    
    需求: 14.1, 14.2
    """
    _, evaluation = approved_evaluation
    
    # Create a publication directly in the database
    publication = Publication(
        evaluation_ids=[str(evaluation.id)],
        published_by=uuid4(),
        published_at=datetime.utcnow()
    )
    db.add(publication)
    db.commit()
    
    response = client.post(
        "/api/publication/distribute",
        json={
            "publication_id": str(publication.id)
        },
        headers={"Authorization": f"Bearer {teaching_office_token}"}
    )
    
    assert response.status_code == 403
    assert "Access denied" in response.json()["detail"]
