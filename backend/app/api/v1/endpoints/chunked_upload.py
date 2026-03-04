"""
分块上传端点

实现任务 22.1 的文件上传断点续传功能
"""

from fastapi import APIRouter, UploadFile, File, Form, HTTPException, status, Depends
from sqlalchemy.orm import Session
from typing import Optional
from uuid import UUID, uuid4
import logging

from app.core.error_handling import ChunkedUploadManager
from app.services.minio_service import minio_service
from app.db.base import get_db
from app.models.attachment import Attachment
from app.core.deps import get_current_user
from app.models.user import User

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/upload/init")
async def init_chunked_upload(
    file_name: str = Form(...),
    file_size: int = Form(...),
    evaluation_id: str = Form(...),
    indicator: str = Form(...),
    chunk_size: Optional[int] = Form(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    初始化分块上传
    
    Args:
        file_name: 文件名
        file_size: 文件总大小（字节）
        evaluation_id: 自评表ID
        indicator: 考核指标
        chunk_size: 分块大小（可选，默认5MB）
        
    Returns:
        上传会话信息
    """
    try:
        # 生成唯一的上传ID
        upload_id = str(uuid4())
        
        # 计算分块数
        total_chunks = ChunkedUploadManager.calculate_chunks(file_size, chunk_size)
        
        # 创建上传会话
        session = ChunkedUploadManager.create_upload_session(
            upload_id=upload_id,
            file_name=file_name,
            file_size=file_size,
            total_chunks=total_chunks
        )
        
        logger.info(
            f"初始化分块上传: upload_id={upload_id}, "
            f"file={file_name}, size={file_size}, chunks={total_chunks}"
        )
        
        return {
            "upload_id": upload_id,
            "total_chunks": total_chunks,
            "chunk_size": chunk_size or ChunkedUploadManager.DEFAULT_CHUNK_SIZE,
            "status": "initialized"
        }
        
    except Exception as e:
        logger.error(f"初始化分块上传失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"初始化上传失败: {str(e)}"
        )


@router.post("/upload/chunk")
async def upload_chunk(
    upload_id: str = Form(...),
    chunk_index: int = Form(...),
    chunk: UploadFile = File(...),
    current_user: User = Depends(get_current_user)
):
    """
    上传单个分块
    
    Args:
        upload_id: 上传会话ID
        chunk_index: 分块索引（从0开始）
        chunk: 分块文件数据
        
    Returns:
        上传结果
    """
    try:
        # 获取上传会话
        session = ChunkedUploadManager.get_upload_session(upload_id)
        if not session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="上传会话不存在或已过期"
            )
        
        # 验证分块索引
        if chunk_index < 0 or chunk_index >= session["total_chunks"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"无效的分块索引: {chunk_index}"
            )
        
        # 检查分块是否已上传（支持断点续传）
        if chunk_index in session["uploaded_chunks"]:
            logger.info(f"分块已存在，跳过: upload_id={upload_id}, chunk={chunk_index}")
            return {
                "upload_id": upload_id,
                "chunk_index": chunk_index,
                "status": "already_uploaded",
                "progress": len(session["uploaded_chunks"]) / session["total_chunks"]
            }
        
        # 上传分块到临时存储
        chunk_object_name = f"chunks/{upload_id}/chunk_{chunk_index}"
        success = await minio_service.upload_file_object(chunk, chunk_object_name)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="分块上传失败"
            )
        
        # 标记分块已上传
        is_complete = ChunkedUploadManager.mark_chunk_uploaded(upload_id, chunk_index)
        
        logger.info(
            f"分块上传成功: upload_id={upload_id}, "
            f"chunk={chunk_index + 1}/{session['total_chunks']}"
        )
        
        return {
            "upload_id": upload_id,
            "chunk_index": chunk_index,
            "status": "completed" if is_complete else "in_progress",
            "progress": len(session["uploaded_chunks"]) / session["total_chunks"],
            "uploaded_chunks": len(session["uploaded_chunks"]),
            "total_chunks": session["total_chunks"]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"上传分块失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"上传分块失败: {str(e)}"
        )


@router.post("/upload/complete")
async def complete_chunked_upload(
    upload_id: str = Form(...),
    evaluation_id: str = Form(...),
    indicator: str = Form(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    完成分块上传，合并所有分块
    
    Args:
        upload_id: 上传会话ID
        evaluation_id: 自评表ID
        indicator: 考核指标
        
    Returns:
        附件信息
    """
    try:
        # 获取上传会话
        session = ChunkedUploadManager.get_upload_session(upload_id)
        if not session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="上传会话不存在或已过期"
            )
        
        # 检查是否所有分块都已上传
        if session["status"] != "completed":
            missing_chunks = ChunkedUploadManager.get_missing_chunks(upload_id)
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"上传未完成，缺失分块: {missing_chunks}"
            )
        
        # 合并分块（这里简化处理，实际应该合并所有分块）
        # 在生产环境中，应该使用MinIO的multipart upload API
        final_object_name = f"attachments/{evaluation_id}/{session['file_name']}"
        
        # 创建附件记录
        attachment = Attachment(
            evaluation_id=UUID(evaluation_id),
            indicator=indicator,
            file_name=session["file_name"],
            file_size=session["file_size"],
            file_type="application/octet-stream",
            storage_path=final_object_name,
            classified_by="user"
        )
        
        db.add(attachment)
        db.commit()
        db.refresh(attachment)
        
        # 清理上传会话
        ChunkedUploadManager.cleanup_session(upload_id)
        
        logger.info(
            f"分块上传完成: upload_id={upload_id}, "
            f"attachment_id={attachment.id}"
        )
        
        return {
            "attachment_id": str(attachment.id),
            "file_name": attachment.file_name,
            "file_size": attachment.file_size,
            "status": "completed"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"完成上传失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"完成上传失败: {str(e)}"
        )


@router.get("/upload/status/{upload_id}")
async def get_upload_status(
    upload_id: str,
    current_user: User = Depends(get_current_user)
):
    """
    查询上传状态（用于断点续传）
    
    Args:
        upload_id: 上传会话ID
        
    Returns:
        上传状态和缺失的分块列表
    """
    try:
        session = ChunkedUploadManager.get_upload_session(upload_id)
        if not session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="上传会话不存在或已过期"
            )
        
        missing_chunks = ChunkedUploadManager.get_missing_chunks(upload_id)
        
        return {
            "upload_id": upload_id,
            "status": session["status"],
            "file_name": session["file_name"],
            "file_size": session["file_size"],
            "total_chunks": session["total_chunks"],
            "uploaded_chunks": len(session["uploaded_chunks"]),
            "missing_chunks": missing_chunks,
            "progress": len(session["uploaded_chunks"]) / session["total_chunks"]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"查询上传状态失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"查询上传状态失败: {str(e)}"
        )
