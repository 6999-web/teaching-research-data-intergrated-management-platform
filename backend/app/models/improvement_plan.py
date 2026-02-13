from sqlalchemy import Column, String, DateTime, ForeignKey, Text, Integer, Enum
from app.db.types import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
import enum

from app.db.base import Base


class ImprovementPlanStatus(str, enum.Enum):
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    COMPLETED = "COMPLETED"


class ImprovementPlan(Base):
    __tablename__ = "improvement_plans"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    evaluation_id = Column(UUID(as_uuid=True), ForeignKey("self_evaluations.id"), nullable=False)
    indicator_item_id = Column(Integer, nullable=False)  # Refers to the specific item index or ID
    target = Column(Text, nullable=False)
    measures = Column(Text, nullable=False)
    charger_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    deadline = Column(DateTime, nullable=False)
    status = Column(Enum(ImprovementPlanStatus), default=ImprovementPlanStatus.PENDING, nullable=False)
    supervisor_comment = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    evaluation = relationship("SelfEvaluation", back_populates="improvement_plans")
    charger = relationship("User", foreign_keys=[charger_id])
