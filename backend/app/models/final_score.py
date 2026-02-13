from sqlalchemy import Column, DateTime, ForeignKey, Numeric, Text, Integer, event
from app.db.types import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.exc import IntegrityError
from datetime import datetime
import uuid

from app.db.base import Base


class FinalScore(Base):
    __tablename__ = "final_scores"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    evaluation_id = Column(UUID(as_uuid=True), ForeignKey("self_evaluations.id"), unique=True, nullable=False)
    final_score = Column(Numeric(5, 2), nullable=False)
    summary = Column(Text)
    determined_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    determined_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    # 任务 22.1: 乐观锁版本控制
    version = Column(Integer, default=1, nullable=False)

    # Relationships
    evaluation = relationship("SelfEvaluation", back_populates="final_score")
    determiner = relationship("User", foreign_keys=[determined_by])


# Event listeners to enforce immutability (需求 19.3, 19.4)
@event.listens_for(FinalScore, 'before_update')
def prevent_final_score_update(mapper, connection, target):
    """Prevent any updates to final score records."""
    raise IntegrityError(
        statement="UPDATE final_scores",
        params={},
        orig=Exception(f"Final score records are immutable and cannot be modified. Record ID: {target.id}")
    )


@event.listens_for(FinalScore, 'before_delete')
def prevent_final_score_delete(mapper, connection, target):
    """Prevent any deletions of final score records."""
    raise IntegrityError(
        statement="DELETE FROM final_scores",
        params={},
        orig=Exception(f"Final score records are immutable and cannot be deleted. Record ID: {target.id}")
    )
