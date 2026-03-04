from sqlalchemy import Column, String, DateTime, ForeignKey
from app.db.types import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

from app.db.base import Base


class TeachingOffice(Base):
    __tablename__ = "teaching_offices"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    code = Column(String(50), unique=True, nullable=False, index=True)
    department = Column(String(255))
    college_id = Column(UUID(as_uuid=True), ForeignKey("colleges.id"))
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    self_evaluations = relationship("SelfEvaluation", back_populates="teaching_office")
    users = relationship("User", back_populates="teaching_office")
    college = relationship("College", back_populates="teaching_offices")
