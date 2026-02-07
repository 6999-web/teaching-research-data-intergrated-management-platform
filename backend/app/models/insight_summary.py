from sqlalchemy import Column, DateTime, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

from app.db.base import Base


class InsightSummary(Base):
    __tablename__ = "insight_summaries"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    evaluation_id = Column(UUID(as_uuid=True), ForeignKey("self_evaluations.id"), unique=True, nullable=False)
    summary = Column(Text, nullable=False)
    generated_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    evaluation = relationship("SelfEvaluation", back_populates="insight_summary")
