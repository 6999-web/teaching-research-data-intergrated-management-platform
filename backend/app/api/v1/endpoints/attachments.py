from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session, joinedload
from typing import List, Optional
from uuid import UUID, uuid4
from datetime import datetime
import os
import re
import logging
from fastapi.concurrency import run_in_threadpool

logger = logging.getLogger(__name__)

from app.core.deps import get_db, get_current_user, RoleChecker
from app.models.user import User
from app.models.attachment import Attachment
from app.models.self_evaluation import SelfEvaluation
from app.models.teaching_office import TeachingOffice
from app.schemas.attachment import (
    AttachmentUploadResponse, 
    AttachmentInfo, 
    AttachmentWithRelations,
    AttachmentClassificationUpdate, 
    AttachmentClassificationResponse
)
from app.services.minio_service import minio_service

router = APIRouter()

# Role checkers
require_teaching_office = RoleChecker(["teaching_office", "director", "teacher"])
require_management_roles = RoleChecker(["evaluation_team", "evaluation_office"])


def _sanitize_path_segment(segment: str) -> str:
    """移除路径中非法字符，避免 Windows/本地存储报错"""
    if not segment or not isinstance(segment, str):
        return "unknown"
    # 保留字母数字、中文、下划线、连字符，其余替换为下划线
    segment = re.sub(r'[<>:"/\\|?*\x00-\x1f]', "_", segment)
    return segment.strip() or "unknown"


@router.post("/attachments", response_model=AttachmentUploadResponse, status_code=status.HTTP_201_CREATED)
async def upload_attachments(
    evaluation_id: UUID = Form(..., description="自评表ID"),
    indicator: str = Form(..., description="考核指标"),
    files: List[UploadFile] = File(..., description="上传的文件列表"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    上传附件
    
    - 支持多文件上传
    - 将文件上传到MinIO对象存储
    - 保存文件元数据到数据库
    - 支持证书类和项目类文件上传
    - 自动归档附件（需求 18.1, 18.4）
    
    需求: 2.1, 2.2, 2.3, 2.4, 2.5, 18.1, 18.4
    """
    # 验证自评表是否存在
    evaluation = db.query(SelfEvaluation).filter(
        SelfEvaluation.id == evaluation_id
    ).first()
    
    if not evaluation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="自评表不存在"
        )
    
    # 检查自评表是否已锁定
    if evaluation.status == "locked":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="自评表已锁定，无法上传附件"
        )
    
    # 验证文件列表不为空
    if not files:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="至少需要上传一个文件"
        )
    
    uploaded_attachments = []
    
    # 对 indicator 做路径安全处理，避免 Windows 非法字符导致写入失败
    indicator_safe = _sanitize_path_segment(indicator)

    # 处理每个文件
    for file in files:
        try:
            # 读取一次内容，避免 upload 时二次 read 或 seek(0) 失败导致 500
            file_content = await file.read()
            file_size = len(file_content)
            if file_size == 0:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"文件 {file.filename or '未知'} 为空，无法上传"
                )

            # 生成唯一的文件名（避免 file.filename 为空）
            raw_filename = file.filename or "unknown"
            file_extension = os.path.splitext(raw_filename)[1]
            unique_filename = f"{uuid4()}{file_extension}"
            
            # 构建存储路径: evaluation_id/indicator_safe/unique_filename（路径中只用安全字符）
            storage_path = f"{evaluation_id}/{indicator_safe}/{unique_filename}"
            
            # 使用 run_in_threadpool 防止同步方法阻塞事件循环，从而导致上传速度慢
            upload_success = await run_in_threadpool(
                minio_service.upload_file_bytes,
                storage_path,
                file_content,
                content_type=file.content_type or "application/octet-stream",
                original_filename=raw_filename,
            )
            
            if not upload_success:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"文件 {raw_filename} 写入存储失败"
                )
            
            # 创建附件记录（自动归档），file_name 不允许为空
            attachment = Attachment(
                evaluation_id=evaluation_id,
                indicator=indicator,
                file_name=raw_filename,
                file_size=file_size,
                file_type=file.content_type or "application/octet-stream",
                storage_path=storage_path,
                classified_by="user",  # 用户上传时分类方式为 'user'
                uploaded_at=datetime.utcnow(),
                is_archived=True,  # 自动归档（需求 18.1, 18.4）
                archived_at=datetime.utcnow()
            )
            
            db.add(attachment)
            uploaded_attachments.append(attachment)
            
        except HTTPException:
            raise
        except UnicodeEncodeError as e:
            logger.exception("附件上传时发生编码错误: %s", e)
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="文件上传失败，请稍后重试"
            )
        except Exception as e:
            logger.exception("附件上传失败: %s", e)
            db.rollback()
            # 返回通用错误信息，避免将编码异常等敏感信息暴露给前端
            detail = "文件上传失败，请稍后重试"
            try:
                err_str = str(e)
                if err_str and "\u26a0" not in err_str and "codec" not in err_str.lower():
                    detail = f"文件上传过程中发生错误: {err_str}"
            except Exception:
                pass
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=detail
            )
    
    # 提交所有附件记录
    try:
        db.commit()
        
        # 刷新所有附件以获取生成的ID
        for attachment in uploaded_attachments:
            db.refresh(attachment)
        
        return AttachmentUploadResponse(
            attachment_ids=[attachment.id for attachment in uploaded_attachments],
            uploaded_count=len(uploaded_attachments)
        )
    
    except UnicodeEncodeError as e:
        logger.exception("保存附件元数据时编码错误: %s", e)
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="保存附件失败，请稍后重试"
        )
    except Exception as e:
        logger.exception("保存附件元数据失败: %s", e)
        db.rollback()
        detail = "保存附件元数据失败，请稍后重试"
        try:
            err_str = str(e)
            if err_str and "codec" not in err_str.lower():
                detail = f"保存附件元数据失败: {err_str}"
        except Exception:
            pass
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=detail
        )


@router.get("/attachments/{evaluation_id}", response_model=List[AttachmentInfo])
def get_attachments(
    evaluation_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    查询自评表的所有附件
    
    - 根据自评表ID查询所有附件
    - 返回附件元数据列表
    """
    # 验证自评表是否存在
    evaluation = db.query(SelfEvaluation).filter(
        SelfEvaluation.id == evaluation_id
    ).first()
    
    if not evaluation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="自评表不存在"
        )
    
    # 查询所有附件
    attachments = db.query(Attachment).filter(
        Attachment.evaluation_id == evaluation_id
    ).all()
    
    return attachments


@router.get("/attachments", response_model=List[AttachmentWithRelations])
def query_attachments(
    teaching_office_id: Optional[UUID] = Query(None, description="按教研室ID筛选"),
    indicator: Optional[str] = Query(None, description="按考核指标筛选"),
    evaluation_year: Optional[int] = Query(None, description="按考核年度筛选"),
    is_archived: Optional[bool] = Query(None, description="按归档状态筛选"),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_management_roles),
):
    """
    查询附件（支持多条件筛选）
    
    - 支持按教研室、考核指标、年度筛选
    - 返回附件及其关联信息（教研室、考核指标）
    - 需求: 18.2, 18.3, 18.5
    """
    # 构建查询，使用 joinedload 预加载关联数据
    query = db.query(Attachment).options(
        joinedload(Attachment.evaluation).joinedload(SelfEvaluation.teaching_office)
    )
    
    # 按教研室筛选
    if teaching_office_id:
        query = query.join(SelfEvaluation).filter(
            SelfEvaluation.teaching_office_id == teaching_office_id
        )
    
    # 按考核指标筛选
    if indicator:
        query = query.filter(Attachment.indicator == indicator)
    
    # 按考核年度筛选
    if evaluation_year:
        if not teaching_office_id:
            query = query.join(SelfEvaluation)
        query = query.filter(SelfEvaluation.evaluation_year == evaluation_year)
    
    # 按归档状态筛选
    if is_archived is not None:
        query = query.filter(Attachment.is_archived == is_archived)
    
    attachments = query.all()
    
    # 构建响应，包含关联信息
    result = []
    for attachment in attachments:
        attachment_dict = {
            "id": attachment.id,
            "evaluation_id": attachment.evaluation_id,
            "indicator": attachment.indicator,
            "file_name": attachment.file_name,
            "file_size": attachment.file_size,
            "file_type": attachment.file_type,
            "storage_path": attachment.storage_path,
            "classified_by": attachment.classified_by,
            "uploaded_at": attachment.uploaded_at,
            "is_archived": attachment.is_archived,
            "archived_at": attachment.archived_at,
            "teaching_office_id": attachment.evaluation.teaching_office_id if attachment.evaluation else None,
            "teaching_office_name": attachment.evaluation.teaching_office.name if attachment.evaluation and attachment.evaluation.teaching_office else None,
            "evaluation_year": attachment.evaluation.evaluation_year if attachment.evaluation else None,
        }
        result.append(AttachmentWithRelations(**attachment_dict))
    
    return result


@router.get("/attachments/{attachment_id}/download")
async def download_attachment(
    attachment_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    下载附件
    
    - 根据附件ID下载文件
    - 从MinIO对象存储获取文件流
    - 支持长期归档的附件访问
    - 需求: 18.5, 18.6
    """
    # 查询附件
    attachment = db.query(Attachment).filter(
        Attachment.id == attachment_id
    ).first()
    
    if not attachment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="附件不存在"
        )
    
    # 验证附件是否已归档（需求 18.4）
    if not attachment.is_archived:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="附件未归档，无法下载"
        )
    
    # 从MinIO获取文件流
    file_stream = minio_service.get_file_stream(attachment.storage_path)
    
    if not file_stream:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="无法获取文件，请稍后重试"
        )
    
    from urllib.parse import quote
    
    # 对文件名进行URL编码以支持中文文件名
    encoded_filename = quote(attachment.file_name, encoding='utf-8')
    
    # 返回文件流响应
    return StreamingResponse(
        file_stream,
        media_type=attachment.file_type or "application/octet-stream",
        headers={
            "Content-Disposition": f"attachment; filename*=UTF-8''{encoded_filename}",
            "Content-Length": str(attachment.file_size)
        }
    )


@router.delete("/attachments/{attachment_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_attachment(
    attachment_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    删除附件
    
    - 仅允许删除未锁定自评表下的附件 (如果是教研室端)。管理端可随时删除。
    - 同步删除 MinIO/本地存储中的文件
    """
    attachment = db.query(Attachment).filter(Attachment.id == attachment_id).first()
    if not attachment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="附件不存在"
        )
    evaluation = db.query(SelfEvaluation).filter(
        SelfEvaluation.id == attachment.evaluation_id
    ).first()
    if not evaluation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="自评表不存在"
        )
    if evaluation.status == "locked" and current_user.role in ["teaching_office", "director", "teacher"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="自评表已锁定，无法删除附件"
        )
    storage_path = attachment.storage_path
    try:
        db.delete(attachment)
        db.commit()
        minio_service.delete_file(storage_path)
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"删除附件失败: {str(e)}"
        )


@router.put("/attachments/{attachment_id}/classification", response_model=AttachmentClassificationResponse)
def update_attachment_classification(
    attachment_id: UUID,
    classification_update: AttachmentClassificationUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_management_roles),
):
    """
    管理端调整附件分类标签
    
    - 允许管理端用户调整AI自动分类的附件
    - 更新附件的考核指标分类
    - 维护附件与考核指标的关联（需求 18.3）
    - 需求: 5.4, 18.3
    """
    # 验证用户权限（仅管理端用户可以调整分类）
    if current_user.role not in ["evaluation_team", "evaluation_office"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="仅管理端用户可以调整附件分类"
        )
    
    # 查询附件
    attachment = db.query(Attachment).filter(
        Attachment.id == attachment_id
    ).first()
    
    if not attachment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="附件不存在"
        )
    
    # 更新分类标签（维护附件与考核指标的关联）
    old_indicator = attachment.indicator
    attachment.indicator = classification_update.indicator
    
    try:
        db.commit()
        db.refresh(attachment)
        
        return AttachmentClassificationResponse(
            id=attachment.id,
            indicator=attachment.indicator,
            message=f"附件分类已从 '{old_indicator}' 更新为 '{classification_update.indicator}'"
        )
    
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"更新附件分类失败: {str(e)}"
        )
