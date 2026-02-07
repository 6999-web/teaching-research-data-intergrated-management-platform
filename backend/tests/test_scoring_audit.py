import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from uuid import uuid4
from datetime import datetime, timedelta

from app.models.user import User
from app.models.teaching_office import TeachingOffice
from app.models.self_evaluation import SelfEvaluation
from app.models.manual_score import ManualScore
from app.models.ai_score import AIScore
from app.models.final_score import FinalScore
from app.core.security import create_access_token


def test_get_scoring_audit_all_records(client: TestClient, db: Session):
    """Test retrieving all scoring audit records without filters."""
    # Create teaching offices
    teaching_office1 = TeachingOffice(
        name="教研室A",
        code="TO001",
        department="学院A"
    )
    teaching_office2 = TeachingOffice(
        name="教研室B",
        code="TO002",
        department="学院B"
    )
    db.add_all([teaching_office1, teaching_office2])
    db.commit()
    
    # Create users
    reviewer1 = User(
        username="reviewer1",
        password_hash="hashed_password",
        role="evaluation_team",
        name="评审员1",
        email="reviewer1@test.com"
    )
    reviewer2 = User(
        username="reviewer2",
        password_hash="hashed_password",
        role="evaluation_office",
        name="评审员2",
        email="reviewer2@test.com"
    )
    db.add_all([reviewer1, reviewer2])
    db.commit()
    
    # Create evaluations
    evaluation1 = SelfEvaluation(
        teaching_office_id=teaching_office1.id,
        evaluation_year=2024,
        content={"teachingProcessManagement": "内容1"},
        status="finalized"
    )
    evaluation2 = SelfEvaluation(
        teaching_office_id=teaching_office2.id,
        evaluation_year=2024,
        content={"teachingProcessManagement": "内容2"},
        status="manually_scored"
    )
    db.add_all([evaluation1, evaluation2])
    db.commit()
    
    # Create AI scores
    ai_score1 = AIScore(
        evaluation_id=evaluation1.id,
        total_score=85.5,
        indicator_scores=[{"indicator": "教学过程管理", "score": 85.5, "reasoning": "AI评分"}],
        parsed_reform_projects=5,
        parsed_honorary_awards=3
    )
    ai_score2 = AIScore(
        evaluation_id=evaluation2.id,
        total_score=90.0,
        indicator_scores=[{"indicator": "教学过程管理", "score": 90.0, "reasoning": "AI评分"}],
        parsed_reform_projects=4,
        parsed_honorary_awards=2
    )
    db.add_all([ai_score1, ai_score2])
    db.commit()
    
    # Create manual scores
    manual_score1 = ManualScore(
        evaluation_id=evaluation1.id,
        reviewer_id=reviewer1.id,
        reviewer_name=reviewer1.name,
        reviewer_role=reviewer1.role,
        weight=0.70,
        scores=[{"indicator": "教学过程管理", "score": 88.0, "comment": "良好"}]
    )
    manual_score2 = ManualScore(
        evaluation_id=evaluation2.id,
        reviewer_id=reviewer2.id,
        reviewer_name=reviewer2.name,
        reviewer_role=reviewer2.role,
        weight=0.50,
        scores=[{"indicator": "教学过程管理", "score": 92.0, "comment": "优秀"}]
    )
    db.add_all([manual_score1, manual_score2])
    db.commit()
    
    # Create final score
    final_score1 = FinalScore(
        evaluation_id=evaluation1.id,
        final_score=87.0,
        summary="综合评分",
        determined_by=reviewer2.id
    )
    db.add(final_score1)
    db.commit()
    
    # Create access token
    token = create_access_token(
        data={"sub": reviewer1.username, "user_id": str(reviewer1.id), "role": reviewer1.role}
    )
    
    # Get audit records
    response = client.get(
        "/api/scoring/audit",
        headers={"Authorization": f"Bearer {token}"}
    )
    
    assert response.status_code == 200
    data = response.json()
    
    assert data["total_count"] == 5  # 2 AI scores + 2 manual scores + 1 final score
    assert len(data["records"]) == 5
    
    # Verify record types
    score_types = [record["score_type"] for record in data["records"]]
    assert score_types.count("ai_score") == 2
    assert score_types.count("manual_score") == 2
    assert score_types.count("final_score") == 1


def test_get_scoring_audit_filter_by_teaching_office(client: TestClient, db: Session):
    """Test filtering audit records by teaching office."""
    # Create teaching offices
    teaching_office1 = TeachingOffice(
        name="教研室A",
        code="TO003",
        department="学院A"
    )
    teaching_office2 = TeachingOffice(
        name="教研室B",
        code="TO004",
        department="学院B"
    )
    db.add_all([teaching_office1, teaching_office2])
    db.commit()
    
    # Create user
    reviewer = User(
        username="reviewer3",
        password_hash="hashed_password",
        role="evaluation_team",
        name="评审员3",
        email="reviewer3@test.com"
    )
    db.add(reviewer)
    db.commit()
    
    # Create evaluations
    evaluation1 = SelfEvaluation(
        teaching_office_id=teaching_office1.id,
        evaluation_year=2024,
        content={"teachingProcessManagement": "内容1"},
        status="ai_scored"
    )
    evaluation2 = SelfEvaluation(
        teaching_office_id=teaching_office2.id,
        evaluation_year=2024,
        content={"teachingProcessManagement": "内容2"},
        status="ai_scored"
    )
    db.add_all([evaluation1, evaluation2])
    db.commit()
    
    # Create AI scores
    ai_score1 = AIScore(
        evaluation_id=evaluation1.id,
        total_score=85.0,
        indicator_scores=[{"indicator": "教学过程管理", "score": 85.0, "reasoning": "AI评分"}],
        parsed_reform_projects=5,
        parsed_honorary_awards=3
    )
    ai_score2 = AIScore(
        evaluation_id=evaluation2.id,
        total_score=90.0,
        indicator_scores=[{"indicator": "教学过程管理", "score": 90.0, "reasoning": "AI评分"}],
        parsed_reform_projects=4,
        parsed_honorary_awards=2
    )
    db.add_all([ai_score1, ai_score2])
    db.commit()
    
    # Create access token
    token = create_access_token(
        data={"sub": reviewer.username, "user_id": str(reviewer.id), "role": reviewer.role}
    )
    
    # Get audit records filtered by teaching_office1
    response = client.get(
        f"/api/scoring/audit?teaching_office_id={teaching_office1.id}",
        headers={"Authorization": f"Bearer {token}"}
    )
    
    assert response.status_code == 200
    data = response.json()
    
    assert data["total_count"] == 1
    assert len(data["records"]) == 1
    assert data["records"][0]["teaching_office_id"] == str(teaching_office1.id)
    assert data["records"][0]["teaching_office_name"] == "教研室A"


def test_get_scoring_audit_filter_by_reviewer(client: TestClient, db: Session):
    """Test filtering audit records by reviewer."""
    # Create teaching office
    teaching_office = TeachingOffice(
        name="教研室C",
        code="TO005",
        department="学院C"
    )
    db.add(teaching_office)
    db.commit()
    
    # Create users
    reviewer1 = User(
        username="reviewer4",
        password_hash="hashed_password",
        role="evaluation_team",
        name="评审员4",
        email="reviewer4@test.com"
    )
    reviewer2 = User(
        username="reviewer5",
        password_hash="hashed_password",
        role="evaluation_office",
        name="评审员5",
        email="reviewer5@test.com"
    )
    db.add_all([reviewer1, reviewer2])
    db.commit()
    
    # Create evaluation
    evaluation = SelfEvaluation(
        teaching_office_id=teaching_office.id,
        evaluation_year=2024,
        content={"teachingProcessManagement": "内容"},
        status="manually_scored"
    )
    db.add(evaluation)
    db.commit()
    
    # Create manual scores from different reviewers
    manual_score1 = ManualScore(
        evaluation_id=evaluation.id,
        reviewer_id=reviewer1.id,
        reviewer_name=reviewer1.name,
        reviewer_role=reviewer1.role,
        weight=0.70,
        scores=[{"indicator": "教学过程管理", "score": 85.0, "comment": "良好"}]
    )
    manual_score2 = ManualScore(
        evaluation_id=evaluation.id,
        reviewer_id=reviewer2.id,
        reviewer_name=reviewer2.name,
        reviewer_role=reviewer2.role,
        weight=0.50,
        scores=[{"indicator": "教学过程管理", "score": 88.0, "comment": "优秀"}]
    )
    db.add_all([manual_score1, manual_score2])
    db.commit()
    
    # Create access token
    token = create_access_token(
        data={"sub": reviewer1.username, "user_id": str(reviewer1.id), "role": reviewer1.role}
    )
    
    # Get audit records filtered by reviewer1
    response = client.get(
        f"/api/scoring/audit?reviewer_id={reviewer1.id}",
        headers={"Authorization": f"Bearer {token}"}
    )
    
    assert response.status_code == 200
    data = response.json()
    
    assert data["total_count"] == 1
    assert len(data["records"]) == 1
    assert data["records"][0]["reviewer_id"] == str(reviewer1.id)
    assert data["records"][0]["reviewer_name"] == "评审员4"
    assert data["records"][0]["score_type"] == "manual_score"


def test_get_scoring_audit_filter_by_date_range(client: TestClient, db: Session):
    """Test filtering audit records by date range."""
    # Create teaching office
    teaching_office = TeachingOffice(
        name="教研室D",
        code="TO006",
        department="学院D"
    )
    db.add(teaching_office)
    db.commit()
    
    # Create user
    reviewer = User(
        username="reviewer6",
        password_hash="hashed_password",
        role="evaluation_team",
        name="评审员6",
        email="reviewer6@test.com"
    )
    db.add(reviewer)
    db.commit()
    
    # Create evaluation
    evaluation = SelfEvaluation(
        teaching_office_id=teaching_office.id,
        evaluation_year=2024,
        content={"teachingProcessManagement": "内容"},
        status="manually_scored"
    )
    db.add(evaluation)
    db.commit()
    
    # Create manual score (will have current timestamp)
    manual_score = ManualScore(
        evaluation_id=evaluation.id,
        reviewer_id=reviewer.id,
        reviewer_name=reviewer.name,
        reviewer_role=reviewer.role,
        weight=0.70,
        scores=[{"indicator": "教学过程管理", "score": 85.0, "comment": "良好"}]
    )
    db.add(manual_score)
    db.commit()
    
    # Create access token
    token = create_access_token(
        data={"sub": reviewer.username, "user_id": str(reviewer.id), "role": reviewer.role}
    )
    
    # Query with date range that includes today
    now = datetime.utcnow()
    start_date = (now - timedelta(days=1)).isoformat()
    end_date = (now + timedelta(days=1)).isoformat()
    
    response = client.get(
        f"/api/scoring/audit?start_date={start_date}&end_date={end_date}",
        headers={"Authorization": f"Bearer {token}"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["total_count"] == 1  # Should include the score created today
    assert data["records"][0]["evaluation_id"] == str(evaluation.id)
    
    # Query with date range in the past (should not include today's score)
    past_start = (now - timedelta(days=10)).isoformat()
    past_end = (now - timedelta(days=5)).isoformat()
    
    response = client.get(
        f"/api/scoring/audit?start_date={past_start}&end_date={past_end}",
        headers={"Authorization": f"Bearer {token}"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["total_count"] == 0  # Should not include today's score


def test_get_scoring_audit_combined_filters(client: TestClient, db: Session):
    """Test combining multiple filters."""
    # Create teaching offices
    teaching_office1 = TeachingOffice(
        name="教研室E",
        code="TO007",
        department="学院E"
    )
    teaching_office2 = TeachingOffice(
        name="教研室F",
        code="TO008",
        department="学院F"
    )
    db.add_all([teaching_office1, teaching_office2])
    db.commit()
    
    # Create users
    reviewer1 = User(
        username="reviewer7",
        password_hash="hashed_password",
        role="evaluation_team",
        name="评审员7",
        email="reviewer7@test.com"
    )
    reviewer2 = User(
        username="reviewer8",
        password_hash="hashed_password",
        role="evaluation_office",
        name="评审员8",
        email="reviewer8@test.com"
    )
    db.add_all([reviewer1, reviewer2])
    db.commit()
    
    # Create evaluations
    evaluation1 = SelfEvaluation(
        teaching_office_id=teaching_office1.id,
        evaluation_year=2024,
        content={"teachingProcessManagement": "内容1"},
        status="manually_scored"
    )
    evaluation2 = SelfEvaluation(
        teaching_office_id=teaching_office2.id,
        evaluation_year=2024,
        content={"teachingProcessManagement": "内容2"},
        status="manually_scored"
    )
    db.add_all([evaluation1, evaluation2])
    db.commit()
    
    # Create manual scores
    manual_score1 = ManualScore(
        evaluation_id=evaluation1.id,
        reviewer_id=reviewer1.id,
        reviewer_name=reviewer1.name,
        reviewer_role=reviewer1.role,
        weight=0.70,
        scores=[{"indicator": "教学过程管理", "score": 85.0, "comment": "良好"}]
    )
    manual_score2 = ManualScore(
        evaluation_id=evaluation1.id,
        reviewer_id=reviewer2.id,
        reviewer_name=reviewer2.name,
        reviewer_role=reviewer2.role,
        weight=0.50,
        scores=[{"indicator": "教学过程管理", "score": 88.0, "comment": "优秀"}]
    )
    manual_score3 = ManualScore(
        evaluation_id=evaluation2.id,
        reviewer_id=reviewer1.id,
        reviewer_name=reviewer1.name,
        reviewer_role=reviewer1.role,
        weight=0.70,
        scores=[{"indicator": "教学过程管理", "score": 90.0, "comment": "优秀"}]
    )
    db.add_all([manual_score1, manual_score2, manual_score3])
    db.commit()
    
    # Create access token
    token = create_access_token(
        data={"sub": reviewer1.username, "user_id": str(reviewer1.id), "role": reviewer1.role}
    )
    
    # Filter by teaching_office1 AND reviewer1
    response = client.get(
        f"/api/scoring/audit?teaching_office_id={teaching_office1.id}&reviewer_id={reviewer1.id}",
        headers={"Authorization": f"Bearer {token}"}
    )
    
    assert response.status_code == 200
    data = response.json()
    
    assert data["total_count"] == 1
    assert data["records"][0]["teaching_office_id"] == str(teaching_office1.id)
    assert data["records"][0]["reviewer_id"] == str(reviewer1.id)


def test_get_scoring_audit_unauthorized(client: TestClient, db: Session):
    """Test that teaching office users cannot access audit records."""
    # Create teaching office
    teaching_office = TeachingOffice(
        name="教研室G",
        code="TO009",
        department="学院G"
    )
    db.add(teaching_office)
    db.commit()
    
    # Create teaching office user (not authorized)
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
    
    # Create access token
    token = create_access_token(
        data={"sub": user.username, "user_id": str(user.id), "role": user.role}
    )
    
    # Try to access audit records (should be rejected)
    response = client.get(
        "/api/scoring/audit",
        headers={"Authorization": f"Bearer {token}"}
    )
    
    assert response.status_code == 403
    assert "Access denied" in response.json()["detail"]


def test_get_scoring_audit_includes_all_score_types(client: TestClient, db: Session):
    """Test that audit includes AI scores, manual scores, and final scores."""
    # Create teaching office
    teaching_office = TeachingOffice(
        name="教研室H",
        code="TO010",
        department="学院H"
    )
    db.add(teaching_office)
    db.commit()
    
    # Create users
    reviewer1 = User(
        username="reviewer9",
        password_hash="hashed_password",
        role="evaluation_team",
        name="评审员9",
        email="reviewer9@test.com"
    )
    reviewer2 = User(
        username="reviewer10",
        password_hash="hashed_password",
        role="evaluation_office",
        name="评审员10",
        email="reviewer10@test.com"
    )
    db.add_all([reviewer1, reviewer2])
    db.commit()
    
    # Create evaluation
    evaluation = SelfEvaluation(
        teaching_office_id=teaching_office.id,
        evaluation_year=2024,
        content={"teachingProcessManagement": "内容"},
        status="finalized"
    )
    db.add(evaluation)
    db.commit()
    
    # Create AI score
    ai_score = AIScore(
        evaluation_id=evaluation.id,
        total_score=85.0,
        indicator_scores=[{"indicator": "教学过程管理", "score": 85.0, "reasoning": "AI评分"}],
        parsed_reform_projects=5,
        parsed_honorary_awards=3
    )
    db.add(ai_score)
    db.commit()
    
    # Create manual score
    manual_score = ManualScore(
        evaluation_id=evaluation.id,
        reviewer_id=reviewer1.id,
        reviewer_name=reviewer1.name,
        reviewer_role=reviewer1.role,
        weight=0.70,
        scores=[{"indicator": "教学过程管理", "score": 88.0, "comment": "良好"}]
    )
    db.add(manual_score)
    db.commit()
    
    # Create final score
    final_score = FinalScore(
        evaluation_id=evaluation.id,
        final_score=87.0,
        summary="综合评分",
        determined_by=reviewer2.id
    )
    db.add(final_score)
    db.commit()
    
    # Create access token
    token = create_access_token(
        data={"sub": reviewer1.username, "user_id": str(reviewer1.id), "role": reviewer1.role}
    )
    
    # Get audit records
    response = client.get(
        "/api/scoring/audit",
        headers={"Authorization": f"Bearer {token}"}
    )
    
    assert response.status_code == 200
    data = response.json()
    
    assert data["total_count"] == 3
    
    # Verify all three types are present
    score_types = {record["score_type"] for record in data["records"]}
    assert score_types == {"ai_score", "manual_score", "final_score"}
    
    # Verify AI score details
    ai_record = next(r for r in data["records"] if r["score_type"] == "ai_score")
    assert ai_record["score_value"] == 85.0
    assert ai_record["reviewer_id"] is None
    assert ai_record["reviewer_name"] is None
    
    # Verify manual score details
    manual_record = next(r for r in data["records"] if r["score_type"] == "manual_score")
    assert manual_record["score_value"] == 88.0
    assert manual_record["reviewer_id"] == str(reviewer1.id)
    assert manual_record["reviewer_name"] == "评审员9"
    
    # Verify final score details
    final_record = next(r for r in data["records"] if r["score_type"] == "final_score")
    assert final_record["score_value"] == 87.0
    assert final_record["reviewer_id"] == str(reviewer2.id)
    assert final_record["reviewer_name"] == "评审员10"
