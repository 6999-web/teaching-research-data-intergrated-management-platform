from sqlalchemy import Column, String, DateTime, ForeignKey, Text, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

from app.db.base import Base


class Approval(Base):
    __tablename__ = "approvals"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    evaluation_ids = Column(JSON, nullable=False)  # Changed from ARRAY to JSON for SQLite compatibility
    decision = Column(String(20), nullable=False)
    reject_reason = Column(Text)
    approved_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    approved_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    approver = relationship("User", foreign_keys=[approved_by])
