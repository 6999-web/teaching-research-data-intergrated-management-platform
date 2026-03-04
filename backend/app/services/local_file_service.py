"""
本地文件存储服务（MinIO 的备用方案）

当 MinIO 服务不可用时，使用本地文件系统存储附件
"""
import os
import shutil
from pathlib import Path
from fastapi import UploadFile
from typing import Optional

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
            # 构建完整的文件路径
            file_path = self.base_path / object_name
            
            # 创建目录（如果不存在）
            file_path.parent.mkdir(parents=True, exist_ok=True)
            
            # 保存文件
            with open(file_path, "wb") as buffer:
                content = await file.read()
                buffer.write(content)
            
            # 重置文件指针
            await file.seek(0)
            
            return True
        except Exception as e:
            print(f"Error uploading file to local storage: {e}")
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
            print(f"Error getting file stream: {e}")
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
            print(f"Error checking file existence: {e}")
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
            print(f"Error deleting file: {e}")
            return False

# 创建全局实例
local_file_service = LocalFileService()
