from sqlalchemy import Column, String, DateTime, ForeignKey
from app.db.types import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

from app.db.base import Base


class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    username = Column(String(100), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    role = Column(String(50), nullable=False)
    teaching_office_id = Column(UUID(as_uuid=True), ForeignKey("teaching_offices.id"))
    college_id = Column(UUID(as_uuid=True), ForeignKey("colleges.id"))
    name = Column(String(255), nullable=False)
    email = Column(String(255))
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    teaching_office = relationship("TeachingOffice", back_populates="users")
    college = relationship("College", foreign_keys=[college_id], back_populates="users")
    managed_college = relationship("College", foreign_keys="College.dean_id", back_populates="dean", uselist=False)
