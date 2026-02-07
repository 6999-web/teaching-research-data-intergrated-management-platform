from sqlalchemy import Column, String, DateTime, ForeignKey, Index, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

from app.db.base import Base


class OperationLog(Base):
    __tablename__ = "operation_logs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    operation_type = Column(String(50), nullable=False)
    operator_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    operator_name = Column(String(255), nullable=False)
    operator_role = Column(String(50), nullable=False)
    target_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    target_type = Column(String(50), nullable=False)
    details = Column(JSON)  # Changed from JSONB to JSON for SQLite compatibility
    operated_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    operator = relationship("User", foreign_keys=[operator_id])

    __table_args__ = (
        Index('idx_operation_logs_operator', 'operator_id'),
        Index('idx_operation_logs_target', 'target_id'),
    )
