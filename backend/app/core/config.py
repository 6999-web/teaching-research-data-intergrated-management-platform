from typing import List
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "教研室工作考评系统"
    API_V1_STR: str = "/api"
    
    # Database
    POSTGRES_SERVER: str = "localhost"
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "postgres"
    POSTGRES_DB: str = "teaching_office_evaluation"
    POSTGRES_PORT: int = 5432
    
    @property
    def DATABASE_URL(self) -> str:
        # Use SQLite for quick testing if PostgreSQL is not available
        import os
        if os.getenv("USE_SQLITE", "false").lower() == "true":
            return "sqlite:///./test.db"
        return f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_SERVER}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
    
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
    
    # CORS
    BACKEND_CORS_ORIGINS: List[str] = ["http://localhost:3000"]
    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()
