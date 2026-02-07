import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from uuid import uuid4
from datetime import datetime

from app.models.user import User
from app.models.teaching_office import TeachingOffice
from app.models.self_evaluation import SelfEvaluation
from app.models.manual_score import ManualScore
from app.models.ai_score import AIScore
from app.models.final_score import FinalScore
from app.core.security import create_access_token


def test_submit_manual_score_success(client: TestClient, db: Session):
    """Test successful manual score submission."""
    # Create teaching office
    teaching_office = TeachingOffice(
        name="测试教研室",
        code="TEST001",
        department="测试学院"
    )
    db.add(teaching_office)
    db.commit()
    
    # Create evaluation team user
    user = User(
        username="reviewer1",
        password_hash="hashed_password",
        role="evaluation_team",
        name="评审员1",
        email="reviewer1@test.com"
    )
    db.add(user)
    db.commit()
    
    # Create self evaluation
    evaluation = SelfEvaluation(
        teaching_office_id=teaching_office.id,
        evaluation_year=2024,
        content={
            "teachingProcessManagement": "测试内容",
            "courseConstruction": "测试内容",
            "teachingReformProjects": 5,
            "honoraryAwards": 3
        },
        status="submitted"
    )
    db.add(evaluation)
    db.commit()
    
    # Create access token
    token = create_access_token(
        data={"sub": user.username, "user_id": str(user.id), "role": user.role}
    )
    
    # Submit manual score
    response = client.post(
        "/api/scoring/manual-score",
        json={
            "evaluation_id": str(evaluation.id),
            "scores": [
                {
                    "indicator": "教学过程管理",
                    "score": 85.5,
                    "comment": "管理规范，执行到位"
                },
                {
                    "indicator": "课程建设",
                    "score": 90.0,
                    "comment": "课程建设成效显著"
                }
            ]
        },
        headers={"Authorization": f"Bearer {token}"}
    )
    
    assert response.status_code == 201
    data = response.json()
    assert "score_record_id" in data
    assert "submitted_at" in data
    
    # Verify score was saved in database
    score = db.query(ManualScore).filter(
        ManualScore.evaluation_id == evaluation.id,
        ManualScore.reviewer_id == user.id
    ).first()
    
    assert score is not None
    assert score.reviewer_name == "评审员1"
    assert score.reviewer_role == "evaluation_team"
    assert float(score.weight) == 0.70  # evaluation_team has higher weight
    assert len(score.scores) == 2


def test_submit_manual_score_duplicate_rejected(client: TestClient, db: Session):
    """Test that duplicate score submission is rejected (immutability requirement)."""
    # Create teaching office
    teaching_office = TeachingOffice(
        name="测试教研室",
        code="TEST002",
        department="测试学院"
    )
    db.add(teaching_office)
    db.commit()
    
    # Create evaluation office user
    user = User(
        username="reviewer2",
        password_hash="hashed_password",
        role="evaluation_office",
        name="评审员2",
        email="reviewer2@test.com"
    )
    db.add(user)
    db.commit()
    
    # Create self evaluation
    evaluation = SelfEvaluation(
        teaching_office_id=teaching_office.id,
        evaluation_year=2024,
        content={
            "teachingProcessManagement": "测试内容",
            "courseConstruction": "测试内容",
            "teachingReformProjects": 5,
            "honoraryAwards": 3
        },
        status="submitted"
    )
    db.add(evaluation)
    db.commit()
    
    # Create existing manual score
    existing_score = ManualScore(
        evaluation_id=evaluation.id,
        reviewer_id=user.id,
        reviewer_name=user.name,
        reviewer_role=user.role,
        weight=0.50,
        scores=[
            {
                "indicator": "教学过程管理",
                "score": 80.0,
                "comment": "良好"
            }
        ]
    )
    db.add(existing_score)
    db.commit()
    
    # Create access token
    token = create_access_token(
        data={"sub": user.username, "user_id": str(user.id), "role": user.role}
    )
    
    # Try to submit another score (should be rejected)
    response = client.post(
        "/api/scoring/manual-score",
        json={
            "evaluation_id": str(evaluation.id),
            "scores": [
                {
                    "indicator": "教学过程管理",
                    "score": 90.0,
                    "comment": "优秀"
                }
            ]
        },
        headers={"Authorization": f"Bearer {token}"}
    )
    
    assert response.status_code == 400
    assert "cannot be modified" in response.json()["detail"]


def test_submit_manual_score_unauthorized(client: TestClient, db: Session):
    """Test that teaching office users cannot submit manual scores."""
    # Create teaching office
    teaching_office = TeachingOffice(
        name="测试教研室",
        code="TEST003",
        department="测试学院"
    )
    db.add(teaching_office)
    db.commit()
    
    # Create teaching office user (not authorized for manual scoring)
    user = User(
        username="teacher1",
        password_hash="hashed_password",
        role="teaching_office",
        name="教师1",
        email="teacher1@test.com",
        teaching_office_id=teaching_office.id
    )
    db.add(user)
    db.commit()
    
    # Create self evaluation
    evaluation = SelfEvaluation(
        teaching_office_id=teaching_office.id,
        evaluation_year=2024,
        content={
            "teachingProcessManagement": "测试内容",
            "courseConstruction": "测试内容",
            "teachingReformProjects": 5,
            "honoraryAwards": 3
        },
        status="submitted"
    )
    db.add(evaluation)
    db.commit()
    
    # Create access token
    token = create_access_token(
        data={"sub": user.username, "user_id": str(user.id), "role": user.role}
    )
    
    # Try to submit manual score (should be rejected)
    response = client.post(
        "/api/scoring/manual-score",
        json={
            "evaluation_id": str(evaluation.id),
            "scores": [
                {
                    "indicator": "教学过程管理",
                    "score": 85.0,
                    "comment": "良好"
                }
            ]
        },
        headers={"Authorization": f"Bearer {token}"}
    )
    
    assert response.status_code == 403
    assert "Access denied" in response.json()["detail"]


def test_get_all_scores_success(client: TestClient, db: Session):
    """Test retrieving all scores for an evaluation."""
    # Create teaching office
    teaching_office = TeachingOffice(
        name="测试教研室",
        code="TEST004",
        department="测试学院"
    )
    db.add(teaching_office)
    db.commit()
    
    # Create evaluation team user
    user = User(
        username="reviewer3",
        password_hash="hashed_password",
        role="evaluation_team",
        name="评审员3",
        email="reviewer3@test.com"
    )
    db.add(user)
    db.commit()
    
    # Create self evaluation
    evaluation = SelfEvaluation(
        teaching_office_id=teaching_office.id,
        evaluation_year=2024,
        content={
            "teachingProcessManagement": "测试内容",
            "courseConstruction": "测试内容",
            "teachingReformProjects": 5,
            "honoraryAwards": 3
        },
        status="ai_scored"
    )
    db.add(evaluation)
    db.commit()
    
    # Create AI score
    ai_score = AIScore(
        evaluation_id=evaluation.id,
        total_score=88.5,
        indicator_scores=[
            {"indicator": "教学过程管理", "score": 85.0, "reasoning": "AI评分说明"},
            {"indicator": "课程建设", "score": 92.0, "reasoning": "AI评分说明"}
        ],
        parsed_reform_projects=5,
        parsed_honorary_awards=3
    )
    db.add(ai_score)
    db.commit()
    
    # Create manual scores from different reviewers
    manual_score1 = ManualScore(
        evaluation_id=evaluation.id,
        reviewer_id=user.id,
        reviewer_name=user.name,
        reviewer_role=user.role,
        weight=0.70,
        scores=[
            {"indicator": "教学过程管理", "score": 87.0, "comment": "良好"},
            {"indicator": "课程建设", "score": 90.0, "comment": "优秀"}
        ]
    )
    db.add(manual_score1)
    db.commit()
    
    # Create access token
    token = create_access_token(
        data={"sub": user.username, "user_id": str(user.id), "role": user.role}
    )
    
    # Get all scores
    response = client.get(
        f"/api/scoring/all-scores/{evaluation.id}",
        headers={"Authorization": f"Bearer {token}"}
    )
    
    assert response.status_code == 200
    data = response.json()
    
    assert data["evaluation_id"] == str(evaluation.id)
    assert data["ai_score"] is not None
    assert data["ai_score"]["total_score"] == 88.5
    assert len(data["manual_scores"]) == 1
    assert data["manual_scores"][0]["reviewer_name"] == "评审员3"
    assert data["manual_scores"][0]["weight"] == 0.70
    assert data["final_score"] is None  # No final score yet


def test_get_all_scores_evaluation_not_found(client: TestClient, db: Session):
    """Test getting scores for non-existent evaluation."""
    # Create evaluation team user
    user = User(
        username="reviewer4",
        password_hash="hashed_password",
        role="evaluation_team",
        name="评审员4",
        email="reviewer4@test.com"
    )
    db.add(user)
    db.commit()
    
    # Create access token
    token = create_access_token(
        data={"sub": user.username, "user_id": str(user.id), "role": user.role}
    )
    
    # Try to get scores for non-existent evaluation
    fake_id = uuid4()
    response = client.get(
        f"/api/scoring/all-scores/{fake_id}",
        headers={"Authorization": f"Bearer {token}"}
    )
    
    assert response.status_code == 404
    assert "not found" in response.json()["detail"]


def test_evaluation_team_has_higher_weight(client: TestClient, db: Session):
    """Test that evaluation_team has higher weight than evaluation_office."""
    # Create teaching office
    teaching_office = TeachingOffice(
        name="测试教研室",
        code="TEST005",
        department="测试学院"
    )
    db.add(teaching_office)
    db.commit()
    
    # Create evaluation team user
    team_user = User(
        username="team_reviewer",
        password_hash="hashed_password",
        role="evaluation_team",
        name="考评小组成员",
        email="team@test.com"
    )
    db.add(team_user)
    
    # Create evaluation office user
    office_user = User(
        username="office_reviewer",
        password_hash="hashed_password",
        role="evaluation_office",
        name="考评办公室成员",
        email="office@test.com"
    )
    db.add(office_user)
    db.commit()
    
    # Create self evaluation
    evaluation = SelfEvaluation(
        teaching_office_id=teaching_office.id,
        evaluation_year=2024,
        content={
            "teachingProcessManagement": "测试内容",
            "courseConstruction": "测试内容",
            "teachingReformProjects": 5,
            "honoraryAwards": 3
        },
        status="submitted"
    )
    db.add(evaluation)
    db.commit()
    
    # Submit score from evaluation team
    team_token = create_access_token(
        data={"sub": team_user.username, "user_id": str(team_user.id), "role": team_user.role}
    )
    
    response1 = client.post(
        "/api/scoring/manual-score",
        json={
            "evaluation_id": str(evaluation.id),
            "scores": [
                {"indicator": "教学过程管理", "score": 85.0, "comment": "良好"}
            ]
        },
        headers={"Authorization": f"Bearer {team_token}"}
    )
    assert response1.status_code == 201
    
    # Submit score from evaluation office
    office_token = create_access_token(
        data={"sub": office_user.username, "user_id": str(office_user.id), "role": office_user.role}
    )
    
    response2 = client.post(
        "/api/scoring/manual-score",
        json={
            "evaluation_id": str(evaluation.id),
            "scores": [
                {"indicator": "教学过程管理", "score": 80.0, "comment": "一般"}
            ]
        },
        headers={"Authorization": f"Bearer {office_token}"}
    )
    assert response2.status_code == 201
    
    # Verify weights in database
    team_score = db.query(ManualScore).filter(
        ManualScore.reviewer_id == team_user.id
    ).first()
    office_score = db.query(ManualScore).filter(
        ManualScore.reviewer_id == office_user.id
    ).first()
    
    assert float(team_score.weight) == 0.70
    assert float(office_score.weight) == 0.50
    assert float(team_score.weight) > float(office_score.weight)


def test_determine_final_score_success(client: TestClient, db: Session):
    """Test successful final score determination."""
    # Create teaching office
    teaching_office = TeachingOffice(
        name="测试教研室",
        code="TEST006",
        department="测试学院"
    )
    db.add(teaching_office)
    db.commit()
    
    # Create evaluation office user (only they can determine final score)
    user = User(
        username="office_admin",
        password_hash="hashed_password",
        role="evaluation_office",
        name="考评办公室管理员",
        email="office_admin@test.com"
    )
    db.add(user)
    db.commit()
    
    # Create self evaluation
    evaluation = SelfEvaluation(
        teaching_office_id=teaching_office.id,
        evaluation_year=2024,
        content={
            "teachingProcessManagement": "测试内容",
            "courseConstruction": "测试内容",
            "teachingReformProjects": 5,
            "honoraryAwards": 3
        },
        status="manually_scored"
    )
    db.add(evaluation)
    db.commit()
    
    # Create manual scores (required before final score)
    manual_score1 = ManualScore(
        evaluation_id=evaluation.id,
        reviewer_id=user.id,
        reviewer_name="评审员1",
        reviewer_role="evaluation_team",
        weight=0.70,
        scores=[
            {"indicator": "教学过程管理", "score": 85.0, "comment": "良好"},
            {"indicator": "课程建设", "score": 90.0, "comment": "优秀"}
        ]
    )
    db.add(manual_score1)
    db.commit()
    
    # Create access token
    token = create_access_token(
        data={"sub": user.username, "user_id": str(user.id), "role": user.role}
    )
    
    # Determine final score
    response = client.post(
        "/api/scoring/final-score",
        json={
            "evaluation_id": str(evaluation.id),
            "final_score": 87.5,
            "summary": "综合各评审人打分，该教研室在教学过程管理和课程建设方面表现优秀，最终得分87.5分。"
        },
        headers={"Authorization": f"Bearer {token}"}
    )
    
    assert response.status_code == 201
    data = response.json()
    assert "final_score_id" in data
    assert data["status"] == "finalized"
    
    # Verify final score was saved in database
    final_score = db.query(FinalScore).filter(
        FinalScore.evaluation_id == evaluation.id
    ).first()
    
    assert final_score is not None
    assert float(final_score.final_score) == 87.5
    assert final_score.summary == "综合各评审人打分，该教研室在教学过程管理和课程建设方面表现优秀，最终得分87.5分。"
    assert final_score.determined_by == user.id
    
    # Verify evaluation status was updated
    db.refresh(evaluation)
    assert evaluation.status == "finalized"


def test_determine_final_score_only_evaluation_office(client: TestClient, db: Session):
    """Test that only evaluation_office can determine final score."""
    # Create teaching office
    teaching_office = TeachingOffice(
        name="测试教研室",
        code="TEST007",
        department="测试学院"
    )
    db.add(teaching_office)
    db.commit()
    
    # Create evaluation team user (not authorized to determine final score)
    user = User(
        username="team_member",
        password_hash="hashed_password",
        role="evaluation_team",
        name="考评小组成员",
        email="team@test.com"
    )
    db.add(user)
    db.commit()
    
    # Create self evaluation
    evaluation = SelfEvaluation(
        teaching_office_id=teaching_office.id,
        evaluation_year=2024,
        content={
            "teachingProcessManagement": "测试内容",
            "courseConstruction": "测试内容",
            "teachingReformProjects": 5,
            "honoraryAwards": 3
        },
        status="manually_scored"
    )
    db.add(evaluation)
    db.commit()
    
    # Create manual score
    manual_score = ManualScore(
        evaluation_id=evaluation.id,
        reviewer_id=user.id,
        reviewer_name=user.name,
        reviewer_role=user.role,
        weight=0.70,
        scores=[
            {"indicator": "教学过程管理", "score": 85.0, "comment": "良好"}
        ]
    )
    db.add(manual_score)
    db.commit()
    
    # Create access token
    token = create_access_token(
        data={"sub": user.username, "user_id": str(user.id), "role": user.role}
    )
    
    # Try to determine final score (should be rejected)
    response = client.post(
        "/api/scoring/final-score",
        json={
            "evaluation_id": str(evaluation.id),
            "final_score": 85.0,
            "summary": "测试汇总"
        },
        headers={"Authorization": f"Bearer {token}"}
    )
    
    assert response.status_code == 403
    assert "Only evaluation office" in response.json()["detail"]


def test_determine_final_score_duplicate_rejected(client: TestClient, db: Session):
    """Test that duplicate final score determination is rejected."""
    # Create teaching office
    teaching_office = TeachingOffice(
        name="测试教研室",
        code="TEST008",
        department="测试学院"
    )
    db.add(teaching_office)
    db.commit()
    
    # Create evaluation office user
    user = User(
        username="office_admin2",
        password_hash="hashed_password",
        role="evaluation_office",
        name="考评办公室管理员2",
        email="office_admin2@test.com"
    )
    db.add(user)
    db.commit()
    
    # Create self evaluation
    evaluation = SelfEvaluation(
        teaching_office_id=teaching_office.id,
        evaluation_year=2024,
        content={
            "teachingProcessManagement": "测试内容",
            "courseConstruction": "测试内容",
            "teachingReformProjects": 5,
            "honoraryAwards": 3
        },
        status="finalized"
    )
    db.add(evaluation)
    db.commit()
    
    # Create manual score
    manual_score = ManualScore(
        evaluation_id=evaluation.id,
        reviewer_id=user.id,
        reviewer_name=user.name,
        reviewer_role=user.role,
        weight=0.50,
        scores=[
            {"indicator": "教学过程管理", "score": 85.0, "comment": "良好"}
        ]
    )
    db.add(manual_score)
    db.commit()
    
    # Create existing final score
    existing_final_score = FinalScore(
        evaluation_id=evaluation.id,
        final_score=85.0,
        summary="已确定的最终得分",
        determined_by=user.id
    )
    db.add(existing_final_score)
    db.commit()
    
    # Create access token
    token = create_access_token(
        data={"sub": user.username, "user_id": str(user.id), "role": user.role}
    )
    
    # Try to determine final score again (should be rejected)
    response = client.post(
        "/api/scoring/final-score",
        json={
            "evaluation_id": str(evaluation.id),
            "final_score": 90.0,
            "summary": "新的汇总说明"
        },
        headers={"Authorization": f"Bearer {token}"}
    )
    
    assert response.status_code == 400
    assert "already been determined" in response.json()["detail"]


def test_determine_final_score_requires_manual_scores(client: TestClient, db: Session):
    """Test that final score requires at least one manual score."""
    # Create teaching office
    teaching_office = TeachingOffice(
        name="测试教研室",
        code="TEST009",
        department="测试学院"
    )
    db.add(teaching_office)
    db.commit()
    
    # Create evaluation office user
    user = User(
        username="office_admin3",
        password_hash="hashed_password",
        role="evaluation_office",
        name="考评办公室管理员3",
        email="office_admin3@test.com"
    )
    db.add(user)
    db.commit()
    
    # Create self evaluation (no manual scores)
    evaluation = SelfEvaluation(
        teaching_office_id=teaching_office.id,
        evaluation_year=2024,
        content={
            "teachingProcessManagement": "测试内容",
            "courseConstruction": "测试内容",
            "teachingReformProjects": 5,
            "honoraryAwards": 3
        },
        status="ai_scored"
    )
    db.add(evaluation)
    db.commit()
    
    # Create access token
    token = create_access_token(
        data={"sub": user.username, "user_id": str(user.id), "role": user.role}
    )
    
    # Try to determine final score without manual scores (should be rejected)
    response = client.post(
        "/api/scoring/final-score",
        json={
            "evaluation_id": str(evaluation.id),
            "final_score": 85.0,
            "summary": "测试汇总"
        },
        headers={"Authorization": f"Bearer {token}"}
    )
    
    assert response.status_code == 400
    assert "No manual scores found" in response.json()["detail"]


def test_determine_final_score_validates_reasonableness(client: TestClient, db: Session):
    """Test that final score is validated against calculated weighted average."""
    # Create teaching office
    teaching_office = TeachingOffice(
        name="测试教研室",
        code="TEST010",
        department="测试学院"
    )
    db.add(teaching_office)
    db.commit()
    
    # Create evaluation office user
    user = User(
        username="office_admin4",
        password_hash="hashed_password",
        role="evaluation_office",
        name="考评办公室管理员4",
        email="office_admin4@test.com"
    )
    db.add(user)
    db.commit()
    
    # Create self evaluation
    evaluation = SelfEvaluation(
        teaching_office_id=teaching_office.id,
        evaluation_year=2024,
        content={
            "teachingProcessManagement": "测试内容",
            "courseConstruction": "测试内容",
            "teachingReformProjects": 5,
            "honoraryAwards": 3
        },
        status="manually_scored"
    )
    db.add(evaluation)
    db.commit()
    
    # Create manual scores with known values
    # Score 1: 80 + 90 = 170, weight 0.70
    # Score 2: 85 + 88 = 173, weight 0.50
    # Weighted avg: (170 * 0.70 + 173 * 0.50) / (0.70 + 0.50) = (119 + 86.5) / 1.2 = 171.25
    manual_score1 = ManualScore(
        evaluation_id=evaluation.id,
        reviewer_id=user.id,
        reviewer_name="评审员1",
        reviewer_role="evaluation_team",
        weight=0.70,
        scores=[
            {"indicator": "教学过程管理", "score": 80.0, "comment": "良好"},
            {"indicator": "课程建设", "score": 90.0, "comment": "优秀"}
        ]
    )
    db.add(manual_score1)
    
    manual_score2 = ManualScore(
        evaluation_id=evaluation.id,
        reviewer_id=uuid4(),
        reviewer_name="评审员2",
        reviewer_role="evaluation_office",
        weight=0.50,
        scores=[
            {"indicator": "教学过程管理", "score": 85.0, "comment": "良好"},
            {"indicator": "课程建设", "score": 88.0, "comment": "良好"}
        ]
    )
    db.add(manual_score2)
    db.commit()
    
    # Create access token
    token = create_access_token(
        data={"sub": user.username, "user_id": str(user.id), "role": user.role}
    )
    
    # Try to determine final score with unreasonable value (should be rejected)
    # Calculated is ~171.25, providing 50 is >20% difference
    response = client.post(
        "/api/scoring/final-score",
        json={
            "evaluation_id": str(evaluation.id),
            "final_score": 50.0,
            "summary": "测试汇总"
        },
        headers={"Authorization": f"Bearer {token}"}
    )
    
    assert response.status_code == 400
    assert "differs significantly" in response.json()["detail"]
    
    # Now try with reasonable value (within 20%)
    response = client.post(
        "/api/scoring/final-score",
        json={
            "evaluation_id": str(evaluation.id),
            "final_score": 170.0,
            "summary": "综合评审人打分，最终确定得分为170分"
        },
        headers={"Authorization": f"Bearer {token}"}
    )
    
    assert response.status_code == 201
