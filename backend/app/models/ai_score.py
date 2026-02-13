from sqlalchemy import Column, Integer, DateTime, ForeignKey, Numeric, JSON, event
from app.db.types import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.exc import IntegrityError
from datetime import datetime
import uuid

from app.db.base import Base


class AIScore(Base):
    __tablename__ = "ai_scores"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    evaluation_id = Column(UUID(as_uuid=True), ForeignKey("self_evaluations.id"), nullable=False, index=True)
    total_score = Column(Numeric(5, 2), nullable=False)
    indicator_scores = Column(JSON, nullable=False)  # Changed from JSONB to JSON for SQLite compatibility
    parsed_reform_projects = Column(Integer, nullable=False)
    parsed_honorary_awards = Column(Integer, nullable=False)
    scored_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    evaluation = relationship("SelfEvaluation", back_populates="ai_scores")


# Event listeners to enforce immutability (需求 19.1, 19.2, 19.4)
@event.listens_for(AIScore, 'before_update')
def prevent_ai_score_update(mapper, connection, target):
    """Prevent any updates to AI score records."""
    raise IntegrityError(
        statement="UPDATE ai_scores",
        params={},
        orig=Exception(f"AI score records are immutable and cannot be modified. Record ID: {target.id}")
    )


@event.listens_for(AIScore, 'before_delete')
def prevent_ai_score_delete(mapper, connection, target):
    """Prevent any deletions of AI score records."""
    raise IntegrityError(
        statement="DELETE FROM ai_scores",
        params={},
        orig=Exception(f"AI score records are immutable and cannot be deleted. Record ID: {target.id}")
    )
