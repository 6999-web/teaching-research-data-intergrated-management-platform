from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
from uuid import UUID


class AttachmentUploadResponse(BaseModel):
    """附件上传响应模型"""
    attachment_ids: List[UUID] = Field(..., description="上传的附件ID列表")
    uploaded_count: int = Field(..., description="成功上传的文件数量")


class AttachmentInfo(BaseModel):
    """附件信息模型"""
    id: UUID = Field(..., description="附件ID")
    evaluation_id: UUID = Field(..., description="自评表ID")
    indicator: str = Field(..., description="考核指标")
    file_name: str = Field(..., description="文件名")
    file_size: int = Field(..., description="文件大小（字节）")
    file_type: str = Field(..., description="文件类型")
    storage_path: str = Field(..., description="存储路径")
    classified_by: str = Field(..., description="分类方式: user 或 ai")
    uploaded_at: datetime = Field(..., description="上传时间")
    is_archived: bool = Field(..., description="是否已归档")
    archived_at: datetime = Field(..., description="归档时间")

    class Config:
        from_attributes = True


class AttachmentWithRelations(AttachmentInfo):
    """附件信息模型（包含关联信息）- 需求 18.2, 18.3"""
    teaching_office_id: Optional[UUID] = Field(None, description="关联的教研室ID")
    teaching_office_name: Optional[str] = Field(None, description="关联的教研室名称")
    evaluation_year: Optional[int] = Field(None, description="考核年度")


class AttachmentClassificationUpdate(BaseModel):
    """附件分类更新请求模型"""
    indicator: str = Field(..., description="新的考核指标分类")


class AttachmentClassificationResponse(BaseModel):
    """附件分类更新响应模型"""
    id: UUID = Field(..., description="附件ID")
    indicator: str = Field(..., description="更新后的考核指标")
    message: str = Field(..., description="操作结果消息")

    class Config:
        from_attributes = True


class AttachmentQueryParams(BaseModel):
    """附件查询参数模型 - 需求 18.5"""
    teaching_office_id: Optional[UUID] = Field(None, description="按教研室ID筛选")
    indicator: Optional[str] = Field(None, description="按考核指标筛选")
    evaluation_year: Optional[int] = Field(None, description="按考核年度筛选")
    is_archived: Optional[bool] = Field(None, description="按归档状态筛选")
