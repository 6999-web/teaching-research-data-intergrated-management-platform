from sqlalchemy.orm import Session
from app.db.base import Base, engine

def init_db() -> None:
    """Initialize database tables"""
    Base.metadata.create_all(bind=engine)
