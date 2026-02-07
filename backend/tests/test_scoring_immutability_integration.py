"""
Integration test for scoring record immutability.

This test verifies that the immutability constraints work correctly
in a realistic scenario with all scoring types.
"""
import pytest
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from decimal import Decimal

from app.models.ai_score import AIScore
from app.models.manual_score import ManualScore
from app.models.final_score import FinalScore
from app.models.self_evaluation import SelfEvaluation
from app.models.teaching_office import TeachingOffice
from app.models.user import User


def test_complete_scoring_workflow_with_immutability(db: Session, test_evaluation, test_reviewer):
    """
    Test complete scoring workflow ensuring all records are immutable.
    
    需求 19.1, 19.2, 19.3, 19.4:
    - Create AI score, manual score, and final score
    - Verify all can be created successfully
    - Verify none can be updated
    - Verify none can be deleted
    - Verify all persist permanently
    """
    # Step 1: Create AI score
    ai_score = AIScore(
        evaluation_id=test_evaluation.id,
        total_score=Decimal("85.50"),
        indicator_scores=[
            {"indicator": "teaching_reform", "score": 20, "reasoning": "Good work"},
            {"indicator": "course_construction", "score": 18, "reasoning": "Excellent"}
        ],
        parsed_reform_projects=3,
        parsed_honorary_awards=2
    )
    db.add(ai_score)
    db.commit()
    ai_score_id = ai_score.id
    
    # Step 2: Create manual score
    manual_score = ManualScore(
        evaluation_id=test_evaluation.id,
        reviewer_id=test_reviewer.id,
        reviewer_name=test_reviewer.name,
        reviewer_role=test_reviewer.role,
        weight=Decimal("0.70"),
        scores=[
            {"indicator": "teaching_reform", "score": 18, "comment": "Excellent"},
            {"indicator": "course_construction", "score": 17, "comment": "Good"}
        ]
    )
    db.add(manual_score)
    db.commit()
    manual_score_id = manual_score.id
    
    # Step 3: Create final score
    final_score = FinalScore(
        evaluation_id=test_evaluation.id,
        final_score=Decimal("88.75"),
        summary="Comprehensive evaluation summary with all details",
        determined_by=test_reviewer.id
    )
    db.add(final_score)
    db.commit()
    final_score_id = final_score.id
    
    # Step 4: Verify all records were created
    assert ai_score.id is not None
    assert manual_score.id is not None
    assert final_score.id is not None
    
    # Step 5: Attempt to update AI score - should fail
    with pytest.raises(IntegrityError):
        ai_score.total_score = Decimal("90.00")
        db.commit()
    db.rollback()
    
    # Step 6: Attempt to update manual score - should fail
    with pytest.raises(IntegrityError):
        manual_score.weight = Decimal("0.80")
        db.commit()
    db.rollback()
    
    # Step 7: Attempt to update final score - should fail
    with pytest.raises(IntegrityError):
        final_score.final_score = Decimal("92.00")
        db.commit()
    db.rollback()
    
    # Step 8: Attempt to delete AI score - should fail
    with pytest.raises(IntegrityError):
        db.delete(ai_score)
        db.commit()
    db.rollback()
    
    # Step 9: Attempt to delete manual score - should fail
    with pytest.raises(IntegrityError):
        db.delete(manual_score)
        db.commit()
    db.rollback()
    
    # Step 10: Attempt to delete final score - should fail
    with pytest.raises(IntegrityError):
        db.delete(final_score)
        db.commit()
    db.rollback()
    
    # Step 11: Verify all records still exist and are unchanged
    db.expire_all()
    
    retrieved_ai = db.query(AIScore).filter(AIScore.id == ai_score_id).first()
    retrieved_manual = db.query(ManualScore).filter(ManualScore.id == manual_score_id).first()
    retrieved_final = db.query(FinalScore).filter(FinalScore.id == final_score_id).first()
    
    assert retrieved_ai is not None
    assert retrieved_ai.total_score == Decimal("85.50")
    
    assert retrieved_manual is not None
    assert retrieved_manual.weight == Decimal("0.70")
    
    assert retrieved_final is not None
    assert retrieved_final.final_score == Decimal("88.75")
    
    # Step 12: Verify timestamps are preserved
    assert retrieved_ai.scored_at is not None
    assert retrieved_manual.submitted_at is not None
    assert retrieved_final.determined_at is not None


def test_scoring_records_survive_session_changes(db: Session, test_evaluation, test_reviewer):
    """
    Test that scoring records persist across session changes.
    
    需求 19.1, 19.2, 19.3
    """
    # Create all scoring records
    ai_score = AIScore(
        evaluation_id=test_evaluation.id,
        total_score=Decimal("85.50"),
        indicator_scores=[{"indicator": "test", "score": 20}],
        parsed_reform_projects=3,
        parsed_honorary_awards=2
    )
    db.add(ai_score)
    
    manual_score = ManualScore(
        evaluation_id=test_evaluation.id,
        reviewer_id=test_reviewer.id,
        reviewer_name=test_reviewer.name,
        reviewer_role=test_reviewer.role,
        weight=Decimal("0.70"),
        scores=[{"indicator": "test", "score": 18, "comment": "Good"}]
    )
    db.add(manual_score)
    
    final_score = FinalScore(
        evaluation_id=test_evaluation.id,
        final_score=Decimal("88.75"),
        summary="Summary",
        determined_by=test_reviewer.id
    )
    db.add(final_score)
    
    db.commit()
    
    # Store IDs
    ai_id = ai_score.id
    manual_id = manual_score.id
    final_id = final_score.id
    
    # Close and reopen session (simulating application restart)
    db.close()
    
    # Create new session
    from tests.conftest import TestingSessionLocal
    new_db = TestingSessionLocal()
    
    try:
        # Retrieve records in new session
        retrieved_ai = new_db.query(AIScore).filter(AIScore.id == ai_id).first()
        retrieved_manual = new_db.query(ManualScore).filter(ManualScore.id == manual_id).first()
        retrieved_final = new_db.query(FinalScore).filter(FinalScore.id == final_id).first()
        
        # Verify all records still exist
        assert retrieved_ai is not None
        assert retrieved_manual is not None
        assert retrieved_final is not None
        
        # Verify data integrity
        assert retrieved_ai.total_score == Decimal("85.50")
        assert retrieved_manual.weight == Decimal("0.70")
        assert retrieved_final.final_score == Decimal("88.75")
        
    finally:
        new_db.close()
