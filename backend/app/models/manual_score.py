from sqlalchemy import Column, String, DateTime, ForeignKey, Numeric, JSON, event
from app.db.types import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.exc import IntegrityError
from datetime import datetime
import uuid

from app.db.base import Base


class ManualScore(Base):
    __tablename__ = "manual_scores"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    evaluation_id = Column(UUID(as_uuid=True), ForeignKey("self_evaluations.id"), nullable=False, index=True)
    reviewer_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    reviewer_name = Column(String(255), nullable=False)
    reviewer_role = Column(String(50), nullable=False)
    weight = Column(Numeric(3, 2), nullable=False)
    scores = Column(JSON, nullable=False)  # Changed from JSONB to JSON for SQLite compatibility
    submitted_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    evaluation = relationship("SelfEvaluation", back_populates="manual_scores")
    reviewer = relationship("User", foreign_keys=[reviewer_id])


# Event listeners to enforce immutability (需求 19.1, 19.4)
@event.listens_for(ManualScore, 'before_update')
def prevent_manual_score_update(mapper, connection, target):
    """Prevent any updates to manual score records."""
    raise IntegrityError(
        statement="UPDATE manual_scores",
        params={},
        orig=Exception(f"Manual score records are immutable and cannot be modified. Record ID: {target.id}")
    )


@event.listens_for(ManualScore, 'before_delete')
def prevent_manual_score_delete(mapper, connection, target):
    """Prevent any deletions of manual score records."""
    raise IntegrityError(
        statement="DELETE FROM manual_scores",
        params={},
        orig=Exception(f"Manual score records are immutable and cannot be deleted. Record ID: {target.id}")
    )
