from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, JSON
from app.db.types import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

from app.db.base import Base


class SelfEvaluation(Base):
    __tablename__ = "self_evaluations"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    teaching_office_id = Column(UUID(as_uuid=True), ForeignKey("teaching_offices.id"), nullable=False, index=True)
    evaluation_year = Column(Integer, nullable=False, index=True)
    content = Column(JSON, nullable=False)  # Changed from JSONB to JSON for SQLite compatibility
    status = Column(String(50), nullable=False, default="draft")
    submitted_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    # 任务 22.1: 乐观锁版本控制
    version = Column(Integer, default=1, nullable=False)

    # Relationships
    teaching_office = relationship("TeachingOffice", back_populates="self_evaluations")
    attachments = relationship("Attachment", back_populates="evaluation", cascade="all, delete-orphan")
    ai_scores = relationship("AIScore", back_populates="evaluation", cascade="all, delete-orphan")
    anomalies = relationship("Anomaly", back_populates="evaluation", cascade="all, delete-orphan")
    manual_scores = relationship("ManualScore", back_populates="evaluation", cascade="all, delete-orphan")
    final_score = relationship("FinalScore", back_populates="evaluation", uselist=False, cascade="all, delete-orphan")
    insight_summary = relationship("InsightSummary", back_populates="evaluation", uselist=False, cascade="all, delete-orphan")
    improvement_plans = relationship("ImprovementPlan", back_populates="evaluation", cascade="all, delete-orphan")
    improvement_plans = relationship("ImprovementPlan", back_populates="evaluation", cascade="all, delete-orphan")

    __table_args__ = (
        {"schema": None},
    )
