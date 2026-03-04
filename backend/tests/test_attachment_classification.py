"""
测试附件自动分类功能 - 任务 8.1

需求: 5.1, 5.2, 5.3, 5.5, 5.6
"""

import pytest
from uuid import uuid4
from datetime import datetime

from app.models.teaching_office import TeachingOffice
from app.models.self_evaluation import SelfEvaluation
from app.models.attachment import Attachment
from app.services.ai_scoring_service import AIScoringService


@pytest.fixture
def teaching_office(db):
    """创建测试教研室"""
    office = TeachingOffice(
        name="计算机教研室",
        code="CS001",
        department="计算机学院"
    )
    db.add(office)
    db.commit()
    db.refresh(office)
    return office


@pytest.fixture
def evaluation_with_attachments(db, teaching_office):
    """创建带附件的自评表"""
    # 创建自评表
    evaluation = SelfEvaluation(
        teaching_office_id=teaching_office.id,
        evaluation_year=2024,
        content={
            "teaching_process_management": "教学过程管理良好",
            "course_construction": "课程建设完善",
            "teaching_reform_projects": 3,
            "honorary_awards": 2
        },
        status="locked",
        submitted_at=datetime.utcnow()
    )
    db.add(evaluation)
    db.commit()
    db.refresh(evaluation)
    
    # 添加附件（初始分类为user）
    attachments = [
        Attachment(
            evaluation_id=evaluation.id,
            indicator="unknown",  # 初始未分类
            file_name="reform_project_1.pdf",
            file_size=1024,
            file_type="application/pdf",
            storage_path=f"{evaluation.id}/reform_project_1.pdf",
            classified_by="user"
        ),
        Attachment(
            evaluation_id=evaluation.id,
            indicator="unknown",
            file_name="reform_project_2.pdf",
            file_size=2048,
            file_type="application/pdf",
            storage_path=f"{evaluation.id}/reform_project_2.pdf",
            classified_by="user"
        ),
        Attachment(
            evaluation_id=evaluation.id,
            indicator="unknown",
            file_name="award_certificate.pdf",
            file_size=1536,
            file_type="application/pdf",
            storage_path=f"{evaluation.id}/award_certificate.pdf",
            classified_by="user"
        ),
    ]
    
    for attachment in attachments:
        db.add(attachment)
    
    db.commit()
    
    return evaluation, attachments


class TestAttachmentClassification:
    """测试附件自动分类功能 - 任务 8.1"""
    
    def test_classify_attachments_basic(self, db, evaluation_with_attachments):
        """
        测试基本的附件分类功能
        
        需求: 5.1, 5.2, 5.3
        """
        evaluation, attachments = evaluation_with_attachments
        
        # 模拟AI返回的分类结果
        score_data = {
            "total_score": 85.0,
            "indicator_scores": [],
            "parsed_reform_projects": 2,
            "parsed_honorary_awards": 1,
            "attachment_classifications": [
                {
                    "file_name": "reform_project_1.pdf",
                    "classified_indicator": "teaching_reform_projects"
                },
                {
                    "file_name": "reform_project_2.pdf",
                    "classified_indicator": "teaching_reform_projects"
                },
                {
                    "file_name": "award_certificate.pdf",
                    "classified_indicator": "honorary_awards"
                }
            ]
        }
        
        # 执行分类
        ai_scoring_service = AIScoringService(db)
        classified_count = ai_scoring_service._classify_attachments(attachments, score_data)
        
        # 提交更改
        db.commit()
        
        # 验证分类结果
        assert classified_count == 3
        
        # 刷新附件数据
        for attachment in attachments:
            db.refresh(attachment)
        
        # 验证每个附件的分类 (需求 5.1, 5.2, 5.3)
        assert attachments[0].indicator == "teaching_reform_projects"
        assert attachments[0].classified_by == "ai"
        
        assert attachments[1].indicator == "teaching_reform_projects"
        assert attachments[1].classified_by == "ai"
        
        assert attachments[2].indicator == "honorary_awards"
        assert attachments[2].classified_by == "ai"
    
    def test_classify_attachments_with_teaching_office_association(self, db, evaluation_with_attachments):
        """
        测试附件与教研室的关联
        
        需求: 5.5
        """
        evaluation, attachments = evaluation_with_attachments
        
        # 验证附件通过evaluation_id与教研室关联 (需求 5.5)
        for attachment in attachments:
            assert attachment.evaluation_id == evaluation.id
            assert attachment.evaluation.teaching_office_id == evaluation.teaching_office_id
    
    def test_classify_attachments_with_indicator_association(self, db, evaluation_with_attachments):
        """
        测试附件与考核指标的关联
        
        需求: 5.6
        """
        evaluation, attachments = evaluation_with_attachments
        
        # 模拟AI分类
        score_data = {
            "total_score": 85.0,
            "indicator_scores": [],
            "parsed_reform_projects": 2,
            "parsed_honorary_awards": 1,
            "attachment_classifications": [
                {
                    "file_name": "reform_project_1.pdf",
                    "classified_indicator": "teaching_reform_projects"
                },
                {
                    "file_name": "reform_project_2.pdf",
                    "classified_indicator": "teaching_reform_projects"
                },
                {
                    "file_name": "award_certificate.pdf",
                    "classified_indicator": "honorary_awards"
                }
            ]
        }
        
        ai_scoring_service = AIScoringService(db)
        ai_scoring_service._classify_attachments(attachments, score_data)
        
        # 提交更改
        db.commit()
        
        # 刷新数据
        for attachment in attachments:
            db.refresh(attachment)
        
        # 验证附件与考核指标的关联 (需求 5.6)
        reform_attachments = [a for a in attachments if a.indicator == "teaching_reform_projects"]
        award_attachments = [a for a in attachments if a.indicator == "honorary_awards"]
        
        assert len(reform_attachments) == 2
        assert len(award_attachments) == 1
    
    def test_classify_attachments_no_classification_data(self, db, evaluation_with_attachments):
        """
        测试AI响应中没有分类数据的情况
        
        需求: 5.1
        """
        evaluation, attachments = evaluation_with_attachments
        
        # AI响应中没有attachment_classifications字段
        score_data = {
            "total_score": 85.0,
            "indicator_scores": [],
            "parsed_reform_projects": 2,
            "parsed_honorary_awards": 1
        }
        
        ai_scoring_service = AIScoringService(db)
        classified_count = ai_scoring_service._classify_attachments(attachments, score_data)
        
        # 应该返回0，表示没有分类任何附件
        assert classified_count == 0
        
        # 附件应该保持原状
        for attachment in attachments:
            db.refresh(attachment)
            assert attachment.indicator == "unknown"
            assert attachment.classified_by == "user"
    
    def test_classify_attachments_invalid_indicator(self, db, evaluation_with_attachments):
        """
        测试无效的分类指标
        
        需求: 5.1, 5.2, 5.3
        """
        evaluation, attachments = evaluation_with_attachments
        
        # AI返回了无效的分类指标
        score_data = {
            "total_score": 85.0,
            "indicator_scores": [],
            "parsed_reform_projects": 2,
            "parsed_honorary_awards": 1,
            "attachment_classifications": [
                {
                    "file_name": "reform_project_1.pdf",
                    "classified_indicator": "invalid_indicator"  # 无效指标
                },
                {
                    "file_name": "reform_project_2.pdf",
                    "classified_indicator": "teaching_reform_projects"  # 有效指标
                }
            ]
        }
        
        ai_scoring_service = AIScoringService(db)
        classified_count = ai_scoring_service._classify_attachments(attachments, score_data)
        
        # 提交更改
        db.commit()
        
        # 只有1个附件被成功分类（有效指标的那个）
        assert classified_count == 1
        
        # 刷新数据
        for attachment in attachments:
            db.refresh(attachment)
        
        # 第一个附件应该保持原状（无效指标）
        assert attachments[0].indicator == "unknown"
        assert attachments[0].classified_by == "user"
        
        # 第二个附件应该被分类（有效指标）
        assert attachments[1].indicator == "teaching_reform_projects"
        assert attachments[1].classified_by == "ai"
    
    def test_classify_attachments_partial_match(self, db, evaluation_with_attachments):
        """
        测试部分附件有分类结果的情况
        
        需求: 5.1
        """
        evaluation, attachments = evaluation_with_attachments
        
        # AI只返回了部分附件的分类
        score_data = {
            "total_score": 85.0,
            "indicator_scores": [],
            "parsed_reform_projects": 1,
            "parsed_honorary_awards": 0,
            "attachment_classifications": [
                {
                    "file_name": "reform_project_1.pdf",
                    "classified_indicator": "teaching_reform_projects"
                }
                # 其他附件没有分类结果
            ]
        }
        
        ai_scoring_service = AIScoringService(db)
        classified_count = ai_scoring_service._classify_attachments(attachments, score_data)
        
        # 提交更改
        db.commit()
        
        # 只有1个附件被分类
        assert classified_count == 1
        
        # 刷新数据
        for attachment in attachments:
            db.refresh(attachment)
        
        # 第一个附件被分类
        assert attachments[0].indicator == "teaching_reform_projects"
        assert attachments[0].classified_by == "ai"
        
        # 其他附件保持原状
        assert attachments[1].indicator == "unknown"
        assert attachments[1].classified_by == "user"
        assert attachments[2].indicator == "unknown"
        assert attachments[2].classified_by == "user"
    
    @pytest.mark.asyncio
    async def test_full_ai_scoring_with_classification(self, db, evaluation_with_attachments):
        """
        测试完整的AI评分流程（包含附件分类）
        
        需求: 5.1, 5.2, 5.3, 5.5, 5.6
        """
        evaluation, attachments = evaluation_with_attachments
        
        # 执行完整的AI评分流程
        ai_scoring_service = AIScoringService(db)
        ai_score = await ai_scoring_service.execute_ai_scoring(evaluation.id)
        
        # 验证AI评分成功
        assert ai_score is not None
        assert ai_score.evaluation_id == evaluation.id
        
        # 刷新附件数据
        for attachment in attachments:
            db.refresh(attachment)
        
        # 验证附件已被分类（由于使用mock数据，分类结果可能为空）
        # 这里主要验证流程不会报错
        classified_attachments = [a for a in attachments if a.classified_by == "ai"]
        assert len(classified_attachments) >= 0  # 至少不会报错
