"""
数据同步任务模型

用于跟踪管理端向校长办公会端的数据同步任务
"""

from sqlalchemy import Column, String, Integer, DateTime, Text, JSON
from app.db.types import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

from app.db.base import Base


class SyncTask(Base):
    __tablename__ = "sync_tasks"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    evaluation_ids = Column(JSON, nullable=False)  # Store as JSON array for SQLite compatibility
    status = Column(String(20), nullable=False, default="pending")  # pending, syncing, completed, failed
    synced_count = Column(Integer, default=0, nullable=False)
    failed_count = Column(Integer, default=0, nullable=False)
    total_count = Column(Integer, nullable=False)
    started_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    completed_at = Column(DateTime)
    error_message = Column(Text)
    retry_count = Column(Integer, default=0, nullable=False)
    checksum = Column(String(64))  # SHA256 checksum for data integrity
    
    # Store the sync data package for retry purposes
    sync_data = Column(JSON)

    __table_args__ = (
        {"schema": None},
    )
