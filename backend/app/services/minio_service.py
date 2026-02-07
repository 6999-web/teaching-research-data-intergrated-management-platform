from minio import Minio
from minio.error import S3Error
from minio.lifecycleconfig import LifecycleConfig, Rule, Expiration
from fastapi import UploadFile
from io import BytesIO
from app.core.config import settings

class MinIOService:
    def __init__(self):
        self.client = None
        self._initialized = False
    
    def _initialize(self):
        """Lazy initialization of MinIO client"""
        if not self._initialized:
            try:
                self.client = Minio(
                    settings.MINIO_ENDPOINT,
                    access_key=settings.MINIO_ACCESS_KEY,
                    secret_key=settings.MINIO_SECRET_KEY,
                    secure=settings.MINIO_SECURE
                )
                self._ensure_bucket_exists()
                self._setup_long_term_storage_policy()
                self._initialized = True
            except Exception as e:
                print(f"Warning: MinIO initialization failed: {e}")
                # Don't raise exception, allow tests to run with mocked service
    
    def _ensure_bucket_exists(self):
        """Ensure the bucket exists, create if not"""
        try:
            if self.client and not self.client.bucket_exists(settings.MINIO_BUCKET):
                self.client.make_bucket(settings.MINIO_BUCKET)
        except S3Error as e:
            print(f"Error creating bucket: {e}")
    
    def _setup_long_term_storage_policy(self):
        """
        设置长期存储策略（需求 18.1, 18.4）
        
        - 附件默认永久保存
        - 可选：设置生命周期规则用于归档到冷存储
        """
        try:
            if not self.client:
                return
            
            # 注意：MinIO 的生命周期配置需要企业版或特定配置
            # 这里提供基础实现，实际部署时可根据需求调整
            # 默认策略：所有附件永久保存，不设置过期时间
            
            # 如果需要设置归档策略，可以取消注释以下代码：
            # config = LifecycleConfig(
            #     [
            #         Rule(
            #             rule_id="archive-old-attachments",
            #             status="Enabled",
            #             # 可以设置转移到冷存储的规则
            #             # transition=Transition(days=365, storage_class="GLACIER")
            #         )
            #     ]
            # )
            # self.client.set_bucket_lifecycle(settings.MINIO_BUCKET, config)
            
            pass  # 默认永久保存策略
            
        except Exception as e:
            print(f"Warning: Could not setup storage policy: {e}")
    
    def upload_file(self, file_path: str, object_name: str):
        """Upload a file to MinIO from file path"""
        self._initialize()
        try:
            if not self.client:
                return False
            self.client.fput_object(
                settings.MINIO_BUCKET,
                object_name,
                file_path
            )
            return True
        except S3Error as e:
            print(f"Error uploading file: {e}")
            return False
    
    async def upload_file_object(self, file: UploadFile, object_name: str) -> bool:
        """
        Upload a file to MinIO from FastAPI UploadFile
        
        实现长期存储：
        - 文件上传到 MinIO 对象存储
        - 使用唯一的 object_name 避免冲突
        - 支持大文件上传
        
        需求: 18.1, 18.4
        """
        self._initialize()
        try:
            if not self.client:
                return False
            
            # Read file content
            file_content = await file.read()
            file_size = len(file_content)
            
            # Upload to MinIO with metadata for long-term archiving
            self.client.put_object(
                settings.MINIO_BUCKET,
                object_name,
                BytesIO(file_content),
                file_size,
                content_type=file.content_type or "application/octet-stream",
                metadata={
                    "original-filename": file.filename,
                    "archived": "true",  # 标记为已归档
                    "retention": "permanent"  # 永久保存
                }
            )
            
            # Reset file pointer for potential reuse
            await file.seek(0)
            
            return True
        except S3Error as e:
            print(f"Error uploading file: {e}")
            return False
    
    def download_file(self, object_name: str, file_path: str):
        """Download a file from MinIO"""
        self._initialize()
        try:
            if not self.client:
                return False
            self.client.fget_object(
                settings.MINIO_BUCKET,
                object_name,
                file_path
            )
            return True
        except S3Error as e:
            print(f"Error downloading file: {e}")
            return False
    
    def get_file_url(self, object_name: str, expires: int = 3600) -> str:
        """
        Get a presigned URL for file access
        
        用于长期归档的附件访问（需求 18.5, 18.6）
        """
        self._initialize()
        try:
            if not self.client:
                return ""
            url = self.client.presigned_get_object(
                settings.MINIO_BUCKET,
                object_name,
                expires=expires
            )
            return url
        except S3Error as e:
            print(f"Error generating presigned URL: {e}")
            return ""
    
    def get_file_stream(self, object_name: str):
        """
        Get file as stream for download
        
        用于附件下载（需求 18.6）
        """
        self._initialize()
        try:
            if not self.client:
                return None
            response = self.client.get_object(
                settings.MINIO_BUCKET,
                object_name
            )
            return response
        except S3Error as e:
            print(f"Error getting file stream: {e}")
            return None
    
    def check_file_exists(self, object_name: str) -> bool:
        """
        Check if a file exists in storage
        
        用于验证归档文件的存在性（需求 18.4）
        """
        self._initialize()
        try:
            if not self.client:
                return False
            self.client.stat_object(settings.MINIO_BUCKET, object_name)
            return True
        except S3Error:
            return False

minio_service = MinIOService()
