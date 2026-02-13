from sqlalchemy import Column, String, BigInteger, DateTime, ForeignKey, Boolean
from app.db.types import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

from app.db.base import Base


class Attachment(Base):
    __tablename__ = "attachments"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    evaluation_id = Column(UUID(as_uuid=True), ForeignKey("self_evaluations.id"), nullable=False, index=True)
    indicator = Column(String(255), nullable=False, index=True)  # Added index for faster queries
    file_name = Column(String(255), nullable=False)
    file_size = Column(BigInteger, nullable=False)
    file_type = Column(String(100))
    storage_path = Column(String(500), nullable=False, unique=True)  # Ensure unique storage paths
    classified_by = Column(String(20), nullable=False)
    uploaded_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Archiving fields for long-term storage (需求 18.1, 18.4)
    is_archived = Column(Boolean, default=True, nullable=False)  # All attachments are archived by default
    archived_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    evaluation = relationship("SelfEvaluation", back_populates="attachments")
    
    @property
    def teaching_office_id(self):
        """获取关联的教研室ID (需求 18.2)"""
        return self.evaluation.teaching_office_id if self.evaluation else None
    
    @property
    def teaching_office(self):
        """获取关联的教研室 (需求 18.2)"""
        return self.evaluation.teaching_office if self.evaluation else None
