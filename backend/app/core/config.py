from typing import List
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "教研室工作考评系统"
    API_V1_STR: str = "/api"
    
    # Database - 使用 SQLite
    DATABASE_URL: str = "sqlite:///./teaching_office_evaluation.db"
    
    # PostgreSQL 配置（备用）
    POSTGRES_SERVER: str = "localhost"
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "postgres"
    POSTGRES_DB: str = "teaching_office_evaluation"
    POSTGRES_PORT: int = 5432
    
    # MinIO
    MINIO_ENDPOINT: str = "localhost:9000"
    MINIO_ACCESS_KEY: str = "minioadmin"
    MINIO_SECRET_KEY: str = "minioadmin"
    MINIO_BUCKET: str = "teaching-office-attachments"
    MINIO_SECURE: bool = False
    
    # JWT
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days
    
    # DeepSeek API
    DEEPSEEK_API_KEY: str = ""
    DEEPSEEK_API_URL: str = "https://api.deepseek.com/v1/chat/completions"
    
    # CORS - 允许的前端访问地址
    BACKEND_CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:5173",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173",
        "http://101.33.211.98",
        "http://101.33.211.98:80",
        "http://101.33.211.98:3000",
        "http://101.33.211.98:5173",
        "http://101.33.211.98:8000",
        "https://101.33.211.98",
        "https://101.33.211.98:443"
    ]
    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()
