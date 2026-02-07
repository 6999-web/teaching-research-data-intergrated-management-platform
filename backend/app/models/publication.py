from sqlalchemy import Column, DateTime, ForeignKey, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

from app.db.base import Base


class Publication(Base):
    __tablename__ = "publications"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    evaluation_ids = Column(JSON, nullable=False)  # Changed from ARRAY to JSON for SQLite compatibility
    published_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    published_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    distributed_at = Column(DateTime)

    # Relationships
    publisher = relationship("User", foreign_keys=[published_by])
