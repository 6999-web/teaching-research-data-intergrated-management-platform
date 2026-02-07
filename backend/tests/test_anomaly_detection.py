"""
测试异常数据检测逻辑 - 任务 7.3

需求: 4.7, 4.8, 4.9, 4.10
"""

import pytest
from datetime import datetime
from uuid import uuid4

from app.models.teaching_office import TeachingOffice
from app.models.self_evaluation import SelfEvaluation
from app.models.attachment import Attachment
from app.models.anomaly import Anomaly
from app.services.ai_scoring_service import AIScoringService


@pytest.fixture
def teaching_office(db):
    """创建测试教研室"""
    office = TeachingOffice(
        name="测试教研室",
        code="TEST001",
        department="测试学院"
    )
    db.add(office)
    db.commit()
    db.refresh(office)
    return office


class TestAnomalyDetection:
    """测试异常数据检测逻辑 - 任务 7.3"""
    
    @pytest.mark.asyncio
    async def test_detect_reform_projects_mismatch(self, db, teaching_office):
        """
        测试检测教学改革项目个数不一致
        
        需求: 4.4, 4.7, 4.8
        """
        # 创建自评表：声称5个教学改革项目
        evaluation = SelfEvaluation(
            teaching_office_id=teaching_office.id,
            evaluation_year=2024,
            content={
                "teaching_process_management": "良好",
                "course_construction": "完善",
                "teaching_reform_projects": 5,  # 声称5个
                "honorary_awards": 2
            },
            status="locked",
            submitted_at=datetime.utcnow()
        )
        db.add(evaluation)
        db.commit()
        db.refresh(evaluation)
        
        # 添加附件：实际只有3个教学改革项目
        for i in range(3):
            attachment = Attachment(
                evaluation_id=evaluation.id,
                indicator="teaching_reform_projects",
                file_name=f"reform{i+1}.pdf",
                file_size=1024,
                file_type="application/pdf",
                storage_path=f"{evaluation.id}/teaching_reform_projects/reform{i+1}.pdf",
                classified_by="user"
            )
            db.add(attachment)
        
        # 添加荣誉表彰附件（数量一致）
        for i in range(2):
            attachment = Attachment(
                evaluation_id=evaluation.id,
                indicator="honorary_awards",
                file_name=f"award{i+1}.pdf",
                file_size=1024,
                file_type="application/pdf",
                storage_path=f"{evaluation.id}/honorary_awards/award{i+1}.pdf",
                classified_by="user"
            )
            db.add(attachment)
        
        db.commit()
        
        # 执行AI评分
        ai_scoring_service = AIScoringService(db)
        ai_score = await ai_scoring_service.execute_ai_scoring(evaluation.id)
        
        # 验证异常数据被检测到 (需求 4.7)
        anomalies = db.query(Anomaly).filter(
            Anomaly.evaluation_id == evaluation.id
        ).all()
        
        # 应该检测到1个异常（教学改革项目个数不一致）
        assert len(anomalies) == 1
        
        anomaly = anomalies[0]
        
        # 验证异常数据字段 (需求 4.7, 4.8)
        assert anomaly.type == "count_mismatch"
        assert anomaly.indicator == "teaching_reform_projects"
        assert anomaly.declared_count == 5
        assert anomaly.parsed_count == 3
        
        # 验证清晰的对比说明 (需求 4.8)
        assert "自评表填写5项教学改革项目" in anomaly.description
        assert "附件仅解析出3份证书" in anomaly.description
        assert "缺少2份支撑材料" in anomaly.description
        
        # 验证异常状态为pending，转人工复核 (需求 4.10)
        assert anomaly.status == "pending"
    
    @pytest.mark.asyncio
    async def test_detect_honorary_awards_mismatch(self, db, teaching_office):
        """
        测试检测荣誉表彰个数不一致
        
        需求: 4.5, 4.7, 4.8
        """
        # 创建自评表：声称3个荣誉表彰
        evaluation = SelfEvaluation(
            teaching_office_id=teaching_office.id,
            evaluation_year=2024,
            content={
                "teaching_process_management": "良好",
                "course_construction": "完善",
                "teaching_reform_projects": 2,
                "honorary_awards": 3  # 声称3个
            },
            status="locked",
            submitted_at=datetime.utcnow()
        )
        db.add(evaluation)
        db.commit()
        db.refresh(evaluation)
        
        # 添加教学改革项目附件（数量一致）
        for i in range(2):
            attachment = Attachment(
                evaluation_id=evaluation.id,
                indicator="teaching_reform_projects",
                file_name=f"reform{i+1}.pdf",
                file_size=1024,
                file_type="application/pdf",
                storage_path=f"{evaluation.id}/teaching_reform_projects/reform{i+1}.pdf",
                classified_by="user"
            )
            db.add(attachment)
        
        # 添加附件：实际只有1个荣誉表彰
        attachment = Attachment(
            evaluation_id=evaluation.id,
            indicator="honorary_awards",
            file_name="award1.pdf",
            file_size=1024,
            file_type="application/pdf",
            storage_path=f"{evaluation.id}/honorary_awards/award1.pdf",
            classified_by="user"
        )
        db.add(attachment)
        db.commit()
        
        # 执行AI评分
        ai_scoring_service = AIScoringService(db)
        ai_score = await ai_scoring_service.execute_ai_scoring(evaluation.id)
        
        # 验证异常数据被检测到 (需求 4.7)
        anomalies = db.query(Anomaly).filter(
            Anomaly.evaluation_id == evaluation.id
        ).all()
        
        # 应该检测到1个异常（荣誉表彰个数不一致）
        assert len(anomalies) == 1
        
        anomaly = anomalies[0]
        
        # 验证异常数据字段 (需求 4.7, 4.8)
        assert anomaly.type == "count_mismatch"
        assert anomaly.indicator == "honorary_awards"
        assert anomaly.declared_count == 3
        assert anomaly.parsed_count == 1
        
        # 验证清晰的对比说明 (需求 4.8)
        assert "自评表填写3项荣誉表彰" in anomaly.description
        assert "附件仅解析出1份证书" in anomaly.description
        assert "缺少2份支撑材料" in anomaly.description
        
        # 验证异常状态为pending，转人工复核 (需求 4.10)
        assert anomaly.status == "pending"
    
    @pytest.mark.asyncio
    async def test_detect_multiple_anomalies(self, db, teaching_office):
        """
        测试同时检测多个异常
        
        需求: 4.7, 4.8
        """
        # 创建自评表：两个指标都不一致
        evaluation = SelfEvaluation(
            teaching_office_id=teaching_office.id,
            evaluation_year=2024,
            content={
                "teaching_process_management": "良好",
                "course_construction": "完善",
                "teaching_reform_projects": 4,  # 声称4个
                "honorary_awards": 3  # 声称3个
            },
            status="locked",
            submitted_at=datetime.utcnow()
        )
        db.add(evaluation)
        db.commit()
        db.refresh(evaluation)
        
        # 添加附件：实际只有2个教学改革项目，1个荣誉表彰
        for i in range(2):
            attachment = Attachment(
                evaluation_id=evaluation.id,
                indicator="teaching_reform_projects",
                file_name=f"reform{i+1}.pdf",
                file_size=1024,
                file_type="application/pdf",
                storage_path=f"{evaluation.id}/teaching_reform_projects/reform{i+1}.pdf",
                classified_by="user"
            )
            db.add(attachment)
        
        attachment = Attachment(
            evaluation_id=evaluation.id,
            indicator="honorary_awards",
            file_name="award1.pdf",
            file_size=1024,
            file_type="application/pdf",
            storage_path=f"{evaluation.id}/honorary_awards/award1.pdf",
            classified_by="user"
        )
        db.add(attachment)
        db.commit()
        
        # 执行AI评分
        ai_scoring_service = AIScoringService(db)
        ai_score = await ai_scoring_service.execute_ai_scoring(evaluation.id)
        
        # 验证异常数据被检测到 (需求 4.7)
        anomalies = db.query(Anomaly).filter(
            Anomaly.evaluation_id == evaluation.id
        ).all()
        
        # 应该检测到2个异常
        assert len(anomalies) == 2
        
        # 验证两个异常都有正确的状态 (需求 4.10)
        for anomaly in anomalies:
            assert anomaly.status == "pending"
            assert anomaly.type == "count_mismatch"
    
    @pytest.mark.asyncio
    async def test_no_anomaly_when_counts_match(self, db, teaching_office):
        """
        测试当个数一致时不产生异常
        
        需求: 4.7
        """
        # 创建自评表：声称2个教学改革项目，2个荣誉表彰
        evaluation = SelfEvaluation(
            teaching_office_id=teaching_office.id,
            evaluation_year=2024,
            content={
                "teaching_process_management": "良好",
                "course_construction": "完善",
                "teaching_reform_projects": 2,
                "honorary_awards": 2
            },
            status="locked",
            submitted_at=datetime.utcnow()
        )
        db.add(evaluation)
        db.commit()
        db.refresh(evaluation)
        
        # 添加附件：实际也是2个教学改革项目，2个荣誉表彰
        for i in range(2):
            attachment = Attachment(
                evaluation_id=evaluation.id,
                indicator="teaching_reform_projects",
                file_name=f"reform{i+1}.pdf",
                file_size=1024,
                file_type="application/pdf",
                storage_path=f"{evaluation.id}/teaching_reform_projects/reform{i+1}.pdf",
                classified_by="user"
            )
            db.add(attachment)
        
        for i in range(2):
            attachment = Attachment(
                evaluation_id=evaluation.id,
                indicator="honorary_awards",
                file_name=f"award{i+1}.pdf",
                file_size=1024,
                file_type="application/pdf",
                storage_path=f"{evaluation.id}/honorary_awards/award{i+1}.pdf",
                classified_by="user"
            )
            db.add(attachment)
        
        db.commit()
        
        # 执行AI评分
        ai_scoring_service = AIScoringService(db)
        ai_score = await ai_scoring_service.execute_ai_scoring(evaluation.id)
        
        # 验证没有异常数据
        anomalies = db.query(Anomaly).filter(
            Anomaly.evaluation_id == evaluation.id
        ).all()
        
        assert len(anomalies) == 0
    
    @pytest.mark.asyncio
    async def test_anomaly_synced_to_management(self, db, teaching_office):
        """
        测试异常信息同步至管理端
        
        需求: 4.9
        """
        # 创建自评表
        evaluation = SelfEvaluation(
            teaching_office_id=teaching_office.id,
            evaluation_year=2024,
            content={
                "teaching_process_management": "良好",
                "course_construction": "完善",
                "teaching_reform_projects": 3,
                "honorary_awards": 2
            },
            status="locked",
            submitted_at=datetime.utcnow()
        )
        db.add(evaluation)
        db.commit()
        db.refresh(evaluation)
        
        # 添加附件（个数不一致）
        attachment = Attachment(
            evaluation_id=evaluation.id,
            indicator="teaching_reform_projects",
            file_name="reform1.pdf",
            file_size=1024,
            file_type="application/pdf",
            storage_path=f"{evaluation.id}/teaching_reform_projects/reform1.pdf",
            classified_by="user"
        )
        db.add(attachment)
        
        attachment = Attachment(
            evaluation_id=evaluation.id,
            indicator="honorary_awards",
            file_name="award1.pdf",
            file_size=1024,
            file_type="application/pdf",
            storage_path=f"{evaluation.id}/honorary_awards/award1.pdf",
            classified_by="user"
        )
        db.add(attachment)
        db.commit()
        
        # 执行AI评分
        ai_scoring_service = AIScoringService(db)
        ai_score = await ai_scoring_service.execute_ai_scoring(evaluation.id)
        
        # 验证管理端可以查询到待处理的异常 (需求 4.9)
        pending_anomalies = ai_scoring_service.get_pending_anomalies()
        
        assert len(pending_anomalies) >= 2
        
        # 验证可以按evaluation_id查询
        evaluation_anomalies = ai_scoring_service.get_pending_anomalies(evaluation.id)
        assert len(evaluation_anomalies) == 2
        
        # 验证异常信息完整
        for anomaly in evaluation_anomalies:
            assert anomaly.evaluation_id == evaluation.id
            assert anomaly.status == "pending"
            assert anomaly.description is not None
            assert len(anomaly.description) > 0
    
    @pytest.mark.asyncio
    async def test_anomaly_description_for_excess_attachments(self, db, teaching_office):
        """
        测试附件多于声明数量时的描述
        
        需求: 4.8
        """
        # 创建自评表：声称1个教学改革项目
        evaluation = SelfEvaluation(
            teaching_office_id=teaching_office.id,
            evaluation_year=2024,
            content={
                "teaching_process_management": "良好",
                "course_construction": "完善",
                "teaching_reform_projects": 1,  # 声称1个
                "honorary_awards": 1
            },
            status="locked",
            submitted_at=datetime.utcnow()
        )
        db.add(evaluation)
        db.commit()
        db.refresh(evaluation)
        
        # 添加附件：实际有3个教学改革项目（多出2个）
        for i in range(3):
            attachment = Attachment(
                evaluation_id=evaluation.id,
                indicator="teaching_reform_projects",
                file_name=f"reform{i+1}.pdf",
                file_size=1024,
                file_type="application/pdf",
                storage_path=f"{evaluation.id}/teaching_reform_projects/reform{i+1}.pdf",
                classified_by="user"
            )
            db.add(attachment)
        
        # 添加荣誉表彰附件（数量一致）
        attachment = Attachment(
            evaluation_id=evaluation.id,
            indicator="honorary_awards",
            file_name="award1.pdf",
            file_size=1024,
            file_type="application/pdf",
            storage_path=f"{evaluation.id}/honorary_awards/award1.pdf",
            classified_by="user"
        )
        db.add(attachment)
        db.commit()
        
        # 执行AI评分
        ai_scoring_service = AIScoringService(db)
        ai_score = await ai_scoring_service.execute_ai_scoring(evaluation.id)
        
        # 验证异常描述 (需求 4.8)
        anomalies = db.query(Anomaly).filter(
            Anomaly.evaluation_id == evaluation.id,
            Anomaly.indicator == "teaching_reform_projects"
        ).all()
        
        assert len(anomalies) == 1
        anomaly = anomalies[0]
        
        # 验证描述包含"多出"信息
        assert "自评表填写1项教学改革项目" in anomaly.description
        assert "附件解析出3份证书" in anomaly.description
        assert "多出2份材料" in anomaly.description
