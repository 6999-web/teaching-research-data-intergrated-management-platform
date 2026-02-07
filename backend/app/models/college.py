from sqlalchemy import Column, String, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid

from app.db.base import Base


class College(Base):
    __tablename__ = "colleges"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), unique=True, nullable=False)
    dean_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))

    # Relationships
    teaching_offices = relationship("TeachingOffice", back_populates="college")
    users = relationship("User", back_populates="college", foreign_keys="User.college_id")
    dean = relationship("User", foreign_keys=[dean_id], back_populates="managed_college")
