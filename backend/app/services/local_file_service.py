"""
本地文件存储服务（MinIO 的备用方案）

当 MinIO 服务不可用时，使用本地文件系统存储附件
"""
import os
import shutil
from pathlib import Path
from fastapi import UploadFile
from typing import Optional

from app.core.safe_log import safe_print

class LocalFileService:
    def __init__(self, base_path: str = "uploads"):
        """初始化本地文件服务"""
        self.base_path = Path(base_path)
        self.base_path.mkdir(parents=True, exist_ok=True)
    
    async def upload_file_object(self, file: UploadFile, object_name: str) -> bool:
        """
        上传文件到本地文件系统
        
        Args:
            file: FastAPI UploadFile 对象
            object_name: 文件存储路径（相对路径）
        
        Returns:
            bool: 上传是否成功
        """
        try:
            content = await file.read()
            return self.upload_bytes(object_name, content)
        except Exception as e:
            safe_print("Error uploading file to local storage:", e)
            return False

    def upload_bytes(self, object_name: str, content: bytes) -> bool:
        """直接使用字节内容写入本地文件，避免 UploadFile 二次读取或 seek 失败"""
        try:
            # 规范为 POSIX 风格路径，避免 Windows 下混用导致的问题
            parts = object_name.replace("\\", "/").strip("/").split("/")
            file_path = self.base_path
            for p in parts:
                file_path = file_path / p
            file_path.parent.mkdir(parents=True, exist_ok=True)
            with open(file_path, "wb") as buffer:
                buffer.write(content)
            return True
        except OSError as e:
            safe_print("Error writing file to local storage (path or permission):", e)
            return False
        except Exception as e:
            safe_print("Error uploading bytes to local storage:", e)
            return False
    
    def get_file_stream(self, object_name: str):
        """
        获取文件流用于下载
        
        Args:
            object_name: 文件存储路径（相对路径）
        
        Returns:
            文件对象或 None
        """
        try:
            file_path = self.base_path / object_name
            if file_path.exists():
                return open(file_path, "rb")
            return None
        except Exception as e:
            safe_print("Error getting file stream:", e)
            return None
    
    def check_file_exists(self, object_name: str) -> bool:
        """
        检查文件是否存在
        
        Args:
            object_name: 文件存储路径（相对路径）
        
        Returns:
            bool: 文件是否存在
        """
        try:
            file_path = self.base_path / object_name
            return file_path.exists()
        except Exception as e:
            safe_print("Error checking file existence:", e)
            return False
    
    def delete_file(self, object_name: str) -> bool:
        """
        删除文件
        
        Args:
            object_name: 文件存储路径（相对路径）
        
        Returns:
            bool: 删除是否成功
        """
        try:
            file_path = self.base_path / object_name
            if file_path.exists():
                file_path.unlink()
                return True
            return False
        except Exception as e:
            safe_print("Error deleting file:", e)
            return False

# 创建全局实例
local_file_service = LocalFileService()
