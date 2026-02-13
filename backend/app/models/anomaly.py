from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, Text
from app.db.types import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

from app.db.base import Base


class Anomaly(Base):
    __tablename__ = "anomalies"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    evaluation_id = Column(UUID(as_uuid=True), ForeignKey("self_evaluations.id"), nullable=False, index=True)
    type = Column(String(50), nullable=False)
    indicator = Column(String(255), nullable=False)
    declared_count = Column(Integer)
    parsed_count = Column(Integer)
    description = Column(Text, nullable=False)
    status = Column(String(20), nullable=False, default="pending")
    handled_by = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    handled_action = Column(String(20))
    handled_at = Column(DateTime)

    # Relationships
    evaluation = relationship("SelfEvaluation", back_populates="anomalies")
    handler = relationship("User", foreign_keys=[handled_by])
