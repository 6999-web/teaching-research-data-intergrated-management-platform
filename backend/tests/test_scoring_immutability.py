"""
Tests for scoring record immutability.

需求 19.1, 19.2, 19.3, 19.4:
- 永久保留所有评审人打分记录
- 永久保留AI评分记录
- 永久保留管理端最终得分
- 禁止篡改评分记录
"""
import pytest
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from datetime import datetime
from decimal import Decimal
import uuid

from app.models.ai_score import AIScore
from app.models.manual_score import ManualScore
from app.models.final_score import FinalScore
from app.models.self_evaluation import SelfEvaluation
from app.models.teaching_office import TeachingOffice
from app.models.user import User


class TestAIScoreImmutability:
    """Test AI score record immutability."""
    
    def test_ai_score_creation_succeeds(self, db: Session, test_evaluation):
        """Test that AI score records can be created."""
        ai_score = AIScore(
            evaluation_id=test_evaluation.id,
            total_score=Decimal("85.50"),
            indicator_scores=[
                {"indicator": "teaching_reform", "score": 20, "reasoning": "Good work"}
            ],
            parsed_reform_projects=3,
            parsed_honorary_awards=2
        )
        
        db.add(ai_score)
        db.commit()
        db.refresh(ai_score)
        
        assert ai_score.id is not None
        assert ai_score.total_score == Decimal("85.50")
        assert ai_score.scored_at is not None
    
    def test_ai_score_update_fails(self, db: Session, test_evaluation):
        """Test that AI score records cannot be updated (需求 19.2, 19.4)."""
        # Create AI score
        ai_score = AIScore(
            evaluation_id=test_evaluation.id,
            total_score=Decimal("85.50"),
            indicator_scores=[{"indicator": "test", "score": 20}],
            parsed_reform_projects=3,
            parsed_honorary_awards=2
        )
        db.add(ai_score)
        db.commit()
        
        # Attempt to update - should fail
        with pytest.raises(IntegrityError) as exc_info:
            ai_score.total_score = Decimal("90.00")
            db.commit()
        
        assert "immutable" in str(exc_info.value).lower()
        db.rollback()
    
    def test_ai_score_delete_fails(self, db: Session, test_evaluation):
        """Test that AI score records cannot be deleted (需求 19.2, 19.4)."""
        # Create AI score
        ai_score = AIScore(
            evaluation_id=test_evaluation.id,
            total_score=Decimal("85.50"),
            indicator_scores=[{"indicator": "test", "score": 20}],
            parsed_reform_projects=3,
            parsed_honorary_awards=2
        )
        db.add(ai_score)
        db.commit()
        
        # Attempt to delete - should fail
        with pytest.raises(IntegrityError) as exc_info:
            db.delete(ai_score)
            db.commit()
        
        assert "immutable" in str(exc_info.value).lower()
        db.rollback()
    
    def test_ai_score_persists_permanently(self, db: Session, test_evaluation):
        """Test that AI score records persist permanently (需求 19.2)."""
        # Create AI score
        ai_score = AIScore(
            evaluation_id=test_evaluation.id,
            total_score=Decimal("85.50"),
            indicator_scores=[{"indicator": "test", "score": 20}],
            parsed_reform_projects=3,
            parsed_honorary_awards=2
        )
        db.add(ai_score)
        db.commit()
        score_id = ai_score.id
        
        # Clear session and retrieve again
        db.expire_all()
        retrieved_score = db.query(AIScore).filter(AIScore.id == score_id).first()
        
        assert retrieved_score is not None
        assert retrieved_score.total_score == Decimal("85.50")
        assert retrieved_score.scored_at is not None


class TestManualScoreImmutability:
    """Test manual score record immutability."""
    
    def test_manual_score_creation_succeeds(self, db: Session, test_evaluation, test_reviewer):
        """Test that manual score records can be created."""
        manual_score = ManualScore(
            evaluation_id=test_evaluation.id,
            reviewer_id=test_reviewer.id,
            reviewer_name=test_reviewer.name,
            reviewer_role=test_reviewer.role,
            weight=Decimal("0.70"),
            scores=[
                {"indicator": "teaching_reform", "score": 18, "comment": "Excellent"}
            ]
        )
        
        db.add(manual_score)
        db.commit()
        db.refresh(manual_score)
        
        assert manual_score.id is not None
        assert manual_score.weight == Decimal("0.70")
        assert manual_score.submitted_at is not None
    
    def test_manual_score_update_fails(self, db: Session, test_evaluation, test_reviewer):
        """Test that manual score records cannot be updated (需求 19.1, 19.4)."""
        # Create manual score
        manual_score = ManualScore(
            evaluation_id=test_evaluation.id,
            reviewer_id=test_reviewer.id,
            reviewer_name=test_reviewer.name,
            reviewer_role=test_reviewer.role,
            weight=Decimal("0.70"),
            scores=[{"indicator": "test", "score": 18, "comment": "Good"}]
        )
        db.add(manual_score)
        db.commit()
        
        # Attempt to update - should fail
        with pytest.raises(IntegrityError) as exc_info:
            manual_score.weight = Decimal("0.80")
            db.commit()
        
        assert "immutable" in str(exc_info.value).lower()
        db.rollback()
    
    def test_manual_score_delete_fails(self, db: Session, test_evaluation, test_reviewer):
        """Test that manual score records cannot be deleted (需求 19.1, 19.4)."""
        # Create manual score
        manual_score = ManualScore(
            evaluation_id=test_evaluation.id,
            reviewer_id=test_reviewer.id,
            reviewer_name=test_reviewer.name,
            reviewer_role=test_reviewer.role,
            weight=Decimal("0.70"),
            scores=[{"indicator": "test", "score": 18, "comment": "Good"}]
        )
        db.add(manual_score)
        db.commit()
        
        # Attempt to delete - should fail
        with pytest.raises(IntegrityError) as exc_info:
            db.delete(manual_score)
            db.commit()
        
        assert "immutable" in str(exc_info.value).lower()
        db.rollback()
    
    def test_manual_score_persists_permanently(self, db: Session, test_evaluation, test_reviewer):
        """Test that manual score records persist permanently (需求 19.1)."""
        # Create manual score
        manual_score = ManualScore(
            evaluation_id=test_evaluation.id,
            reviewer_id=test_reviewer.id,
            reviewer_name=test_reviewer.name,
            reviewer_role=test_reviewer.role,
            weight=Decimal("0.70"),
            scores=[{"indicator": "test", "score": 18, "comment": "Good"}]
        )
        db.add(manual_score)
        db.commit()
        score_id = manual_score.id
        
        # Clear session and retrieve again
        db.expire_all()
        retrieved_score = db.query(ManualScore).filter(ManualScore.id == score_id).first()
        
        assert retrieved_score is not None
        assert retrieved_score.weight == Decimal("0.70")
        assert retrieved_score.submitted_at is not None


class TestFinalScoreImmutability:
    """Test final score record immutability."""
    
    def test_final_score_creation_succeeds(self, db: Session, test_evaluation, test_reviewer):
        """Test that final score records can be created."""
        final_score = FinalScore(
            evaluation_id=test_evaluation.id,
            final_score=Decimal("88.75"),
            summary="Comprehensive evaluation summary",
            determined_by=test_reviewer.id
        )
        
        db.add(final_score)
        db.commit()
        db.refresh(final_score)
        
        assert final_score.id is not None
        assert final_score.final_score == Decimal("88.75")
        assert final_score.determined_at is not None
    
    def test_final_score_update_fails(self, db: Session, test_evaluation, test_reviewer):
        """Test that final score records cannot be updated (需求 19.3, 19.4)."""
        # Create final score
        final_score = FinalScore(
            evaluation_id=test_evaluation.id,
            final_score=Decimal("88.75"),
            summary="Summary",
            determined_by=test_reviewer.id
        )
        db.add(final_score)
        db.commit()
        
        # Attempt to update - should fail
        with pytest.raises(IntegrityError) as exc_info:
            final_score.final_score = Decimal("92.00")
            db.commit()
        
        assert "immutable" in str(exc_info.value).lower()
        db.rollback()
    
    def test_final_score_delete_fails(self, db: Session, test_evaluation, test_reviewer):
        """Test that final score records cannot be deleted (需求 19.3, 19.4)."""
        # Create final score
        final_score = FinalScore(
            evaluation_id=test_evaluation.id,
            final_score=Decimal("88.75"),
            summary="Summary",
            determined_by=test_reviewer.id
        )
        db.add(final_score)
        db.commit()
        
        # Attempt to delete - should fail
        with pytest.raises(IntegrityError) as exc_info:
            db.delete(final_score)
            db.commit()
        
        assert "immutable" in str(exc_info.value).lower()
        db.rollback()
    
    def test_final_score_persists_permanently(self, db: Session, test_evaluation, test_reviewer):
        """Test that final score records persist permanently (需求 19.3)."""
        # Create final score
        final_score = FinalScore(
            evaluation_id=test_evaluation.id,
            final_score=Decimal("88.75"),
            summary="Summary",
            determined_by=test_reviewer.id
        )
        db.add(final_score)
        db.commit()
        score_id = final_score.id
        
        # Clear session and retrieve again
        db.expire_all()
        retrieved_score = db.query(FinalScore).filter(FinalScore.id == score_id).first()
        
        assert retrieved_score is not None
        assert retrieved_score.final_score == Decimal("88.75")
        assert retrieved_score.determined_at is not None


class TestScoringRecordsPermanence:
    """Test that all scoring records are permanently saved."""
    
    def test_all_scoring_records_persist_together(
        self, db: Session, test_evaluation, test_reviewer
    ):
        """
        Test that AI scores, manual scores, and final scores all persist permanently.
        
        需求 19.1, 19.2, 19.3
        """
        # Create AI score
        ai_score = AIScore(
            evaluation_id=test_evaluation.id,
            total_score=Decimal("85.50"),
            indicator_scores=[{"indicator": "test", "score": 20}],
            parsed_reform_projects=3,
            parsed_honorary_awards=2
        )
        db.add(ai_score)
        
        # Create manual score
        manual_score = ManualScore(
            evaluation_id=test_evaluation.id,
            reviewer_id=test_reviewer.id,
            reviewer_name=test_reviewer.name,
            reviewer_role=test_reviewer.role,
            weight=Decimal("0.70"),
            scores=[{"indicator": "test", "score": 18, "comment": "Good"}]
        )
        db.add(manual_score)
        
        # Create final score
        final_score = FinalScore(
            evaluation_id=test_evaluation.id,
            final_score=Decimal("88.75"),
            summary="Summary",
            determined_by=test_reviewer.id
        )
        db.add(final_score)
        
        db.commit()
        
        # Store IDs
        ai_score_id = ai_score.id
        manual_score_id = manual_score.id
        final_score_id = final_score.id
        
        # Clear session
        db.expire_all()
        
        # Verify all records persist
        retrieved_ai = db.query(AIScore).filter(AIScore.id == ai_score_id).first()
        retrieved_manual = db.query(ManualScore).filter(ManualScore.id == manual_score_id).first()
        retrieved_final = db.query(FinalScore).filter(FinalScore.id == final_score_id).first()
        
        assert retrieved_ai is not None
        assert retrieved_manual is not None
        assert retrieved_final is not None
        
        # Verify they all reference the same evaluation
        assert retrieved_ai.evaluation_id == test_evaluation.id
        assert retrieved_manual.evaluation_id == test_evaluation.id
        assert retrieved_final.evaluation_id == test_evaluation.id
