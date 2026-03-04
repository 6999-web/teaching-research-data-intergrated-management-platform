"""
测试附件归档功能

需求: 18.1, 18.2, 18.3, 18.4
"""
import pytest
from uuid import uuid4
from io import BytesIO
from app.models.teaching_office import TeachingOffice
from app.models.self_evaluation import SelfEvaluation
from app.models.attachment import Attachment


def test_attachment_auto_archived_on_upload(client, db, teaching_office_token, teaching_office_user):
    """
    测试附件上传时自动归档
    
    需求: 18.1, 18.4
    """
    # 创建教研室
    teaching_office = TeachingOffice(
        name="计算机教研室",
        code="CS001",
        department="计算机学院"
    )
    db.add(teaching_office)
    db.commit()
    db.refresh(teaching_office)
    
    # 创建自评表
    evaluation = SelfEvaluation(
        teaching_office_id=teaching_office.id,
        evaluation_year=2024,
        content={"test": "data"},
        status="draft"
    )
    db.add(evaluation)
    db.commit()
    db.refresh(evaluation)
    
    # 上传附件
    file_content = b"Test file content"
    files = [("files", ("test.pdf", BytesIO(file_content), "application/pdf"))]
    
    response = client.post(
        "/api/teaching-office/attachments",
        data={
            "evaluation_id": str(evaluation.id),
            "indicator": "teaching_reform_projects"
        },
        files=files,
        headers={"Authorization": f"Bearer {teaching_office_token}"}
    )
    
    assert response.status_code == 201
    data = response.json()
    assert data["uploaded_count"] == 1
    
    # 验证附件已自动归档
    attachment = db.query(Attachment).filter(
        Attachment.id == data["attachment_ids"][0]
    ).first()
    
    assert attachment is not None
    assert attachment.is_archived is True
    assert attachment.archived_at is not None


def test_attachment_teaching_office_relationship(client, db, teaching_office_token):
    """
    测试附件与教研室的关联
    
    需求: 18.2
    """
    # 创建教研室
    teaching_office = TeachingOffice(
        name="数学教研室",
        code="MATH001",
        department="数学学院"
    )
    db.add(teaching_office)
    db.commit()
    db.refresh(teaching_office)
    
    # 创建自评表
    evaluation = SelfEvaluation(
        teaching_office_id=teaching_office.id,
        evaluation_year=2024,
        content={"test": "data"},
        status="draft"
    )
    db.add(evaluation)
    db.commit()
    db.refresh(evaluation)
    
    # 上传附件
    file_content = b"Test file content"
    files = [("files", ("test.pdf", BytesIO(file_content), "application/pdf"))]
    
    response = client.post(
        "/api/teaching-office/attachments",
        data={
            "evaluation_id": str(evaluation.id),
            "indicator": "honorary_awards"
        },
        files=files,
        headers={"Authorization": f"Bearer {teaching_office_token}"}
    )
    
    assert response.status_code == 201
    data = response.json()
    
    # 验证附件与教研室的关联
    attachment = db.query(Attachment).filter(
        Attachment.id == data["attachment_ids"][0]
    ).first()
    
    assert attachment is not None
    assert attachment.teaching_office_id == teaching_office.id
    assert attachment.teaching_office.name == "数学教研室"


def test_attachment_indicator_relationship(client, db, teaching_office_token):
    """
    测试附件与考核指标的关联
    
    需求: 18.3
    """
    # 创建教研室
    teaching_office = TeachingOffice(
        name="物理教研室",
        code="PHY001",
        department="物理学院"
    )
    db.add(teaching_office)
    db.commit()
    db.refresh(teaching_office)
    
    # 创建自评表
    evaluation = SelfEvaluation(
        teaching_office_id=teaching_office.id,
        evaluation_year=2024,
        content={"test": "data"},
        status="draft"
    )
    db.add(evaluation)
    db.commit()
    db.refresh(evaluation)
    
    # 上传附件到不同考核指标
    indicators = ["teaching_reform_projects", "honorary_awards", "course_construction"]
    
    for indicator in indicators:
        file_content = f"Test file for {indicator}".encode()
        files = [("files", (f"{indicator}.pdf", BytesIO(file_content), "application/pdf"))]
        
        response = client.post(
            "/api/teaching-office/attachments",
            data={
                "evaluation_id": str(evaluation.id),
                "indicator": indicator
            },
            files=files,
            headers={"Authorization": f"Bearer {teaching_office_token}"}
        )
        
        assert response.status_code == 201
    
    # 验证所有附件都有正确的考核指标关联
    attachments = db.query(Attachment).filter(
        Attachment.evaluation_id == evaluation.id
    ).all()
    
    assert len(attachments) == 3
    attachment_indicators = [att.indicator for att in attachments]
    assert set(attachment_indicators) == set(indicators)


def test_query_attachments_by_teaching_office(client, db, evaluation_office_token):
    """
    测试按教研室查询附件
    
    需求: 18.2, 18.5
    """
    # 创建两个教研室
    teaching_office1 = TeachingOffice(
        name="化学教研室",
        code="CHEM001",
        department="化学学院"
    )
    teaching_office2 = TeachingOffice(
        name="生物教研室",
        code="BIO001",
        department="生物学院"
    )
    db.add_all([teaching_office1, teaching_office2])
    db.commit()
    db.refresh(teaching_office1)
    db.refresh(teaching_office2)
    
    # 为每个教研室创建自评表和附件
    for office in [teaching_office1, teaching_office2]:
        evaluation = SelfEvaluation(
            teaching_office_id=office.id,
            evaluation_year=2024,
            content={"test": "data"},
            status="draft"
        )
        db.add(evaluation)
        db.commit()
        db.refresh(evaluation)
        
        attachment = Attachment(
            evaluation_id=evaluation.id,
            indicator="teaching_reform_projects",
            file_name=f"{office.name}_test.pdf",
            file_size=1024,
            file_type="application/pdf",
            storage_path=f"{evaluation.id}/test/{uuid4()}.pdf",
            classified_by="user",
            is_archived=True
        )
        db.add(attachment)
    
    db.commit()
    
    # 查询第一个教研室的附件
    response = client.get(
        f"/api/teaching-office/attachments?teaching_office_id={teaching_office1.id}",
        headers={"Authorization": f"Bearer {evaluation_office_token}"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["teaching_office_id"] == str(teaching_office1.id)
    assert data[0]["teaching_office_name"] == "化学教研室"


def test_query_attachments_by_indicator(client, db, evaluation_office_token):
    """
    测试按考核指标查询附件
    
    需求: 18.3, 18.5
    """
    # 创建教研室
    teaching_office = TeachingOffice(
        name="英语教研室",
        code="ENG001",
        department="外语学院"
    )
    db.add(teaching_office)
    db.commit()
    db.refresh(teaching_office)
    
    # 创建自评表
    evaluation = SelfEvaluation(
        teaching_office_id=teaching_office.id,
        evaluation_year=2024,
        content={"test": "data"},
        status="draft"
    )
    db.add(evaluation)
    db.commit()
    db.refresh(evaluation)
    
    # 创建不同考核指标的附件
    indicators = ["teaching_reform_projects", "honorary_awards"]
    for indicator in indicators:
        for i in range(2):
            attachment = Attachment(
                evaluation_id=evaluation.id,
                indicator=indicator,
                file_name=f"{indicator}_{i}.pdf",
                file_size=1024,
                file_type="application/pdf",
                storage_path=f"{evaluation.id}/{indicator}/{uuid4()}.pdf",
                classified_by="user",
                is_archived=True
            )
            db.add(attachment)
    
    db.commit()
    
    # 查询特定考核指标的附件
    response = client.get(
        "/api/teaching-office/attachments?indicator=teaching_reform_projects",
        headers={"Authorization": f"Bearer {evaluation_office_token}"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert all(att["indicator"] == "teaching_reform_projects" for att in data)


def test_query_attachments_by_year(client, db, evaluation_office_token):
    """
    测试按考核年度查询附件
    
    需求: 18.5
    """
    # 创建教研室
    teaching_office = TeachingOffice(
        name="历史教研室",
        code="HIST001",
        department="历史学院"
    )
    db.add(teaching_office)
    db.commit()
    db.refresh(teaching_office)
    
    # 创建不同年度的自评表和附件
    for year in [2023, 2024]:
        evaluation = SelfEvaluation(
            teaching_office_id=teaching_office.id,
            evaluation_year=year,
            content={"test": "data"},
            status="draft"
        )
        db.add(evaluation)
        db.commit()
        db.refresh(evaluation)
        
        attachment = Attachment(
            evaluation_id=evaluation.id,
            indicator="teaching_reform_projects",
            file_name=f"test_{year}.pdf",
            file_size=1024,
            file_type="application/pdf",
            storage_path=f"{evaluation.id}/test/{uuid4()}.pdf",
            classified_by="user",
            is_archived=True
        )
        db.add(attachment)
    
    db.commit()
    
    # 查询2024年的附件
    response = client.get(
        "/api/teaching-office/attachments?evaluation_year=2024",
        headers={"Authorization": f"Bearer {evaluation_office_token}"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["evaluation_year"] == 2024


def test_query_attachments_multiple_filters(client, db, evaluation_office_token):
    """
    测试多条件组合查询附件
    
    需求: 18.2, 18.3, 18.5
    """
    # 创建两个教研室
    teaching_office1 = TeachingOffice(
        name="地理教研室",
        code="GEO001",
        department="地理学院"
    )
    teaching_office2 = TeachingOffice(
        name="政治教研室",
        code="POL001",
        department="政治学院"
    )
    db.add_all([teaching_office1, teaching_office2])
    db.commit()
    
    # 为每个教研室创建多年度、多指标的附件
    for office in [teaching_office1, teaching_office2]:
        for year in [2023, 2024]:
            evaluation = SelfEvaluation(
                teaching_office_id=office.id,
                evaluation_year=year,
                content={"test": "data"},
                status="draft"
            )
            db.add(evaluation)
            db.commit()
            db.refresh(evaluation)
            
            for indicator in ["teaching_reform_projects", "honorary_awards"]:
                attachment = Attachment(
                    evaluation_id=evaluation.id,
                    indicator=indicator,
                    file_name=f"{office.name}_{year}_{indicator}.pdf",
                    file_size=1024,
                    file_type="application/pdf",
                    storage_path=f"{evaluation.id}/{indicator}/{uuid4()}.pdf",
                    classified_by="user",
                    is_archived=True
                )
                db.add(attachment)
    
    db.commit()
    
    # 组合查询：特定教研室 + 特定年度 + 特定指标
    response = client.get(
        f"/api/teaching-office/attachments?teaching_office_id={teaching_office1.id}&evaluation_year=2024&indicator=teaching_reform_projects",
        headers={"Authorization": f"Bearer {evaluation_office_token}"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["teaching_office_id"] == str(teaching_office1.id)
    assert data[0]["evaluation_year"] == 2024
    assert data[0]["indicator"] == "teaching_reform_projects"


def test_attachment_classification_maintains_relationship(client, db, evaluation_office_token):
    """
    测试调整附件分类时维护与考核指标的关联
    
    需求: 18.3
    """
    # 创建教研室
    teaching_office = TeachingOffice(
        name="体育教研室",
        code="PE001",
        department="体育学院"
    )
    db.add(teaching_office)
    db.commit()
    db.refresh(teaching_office)
    
    # 创建自评表
    evaluation = SelfEvaluation(
        teaching_office_id=teaching_office.id,
        evaluation_year=2024,
        content={"test": "data"},
        status="draft"
    )
    db.add(evaluation)
    db.commit()
    db.refresh(evaluation)
    
    # 创建附件
    attachment = Attachment(
        evaluation_id=evaluation.id,
        indicator="teaching_reform_projects",
        file_name="test.pdf",
        file_size=1024,
        file_type="application/pdf",
        storage_path=f"{evaluation.id}/test/{uuid4()}.pdf",
        classified_by="ai",
        is_archived=True
    )
    db.add(attachment)
    db.commit()
    db.refresh(attachment)
    
    # 调整分类
    response = client.put(
        f"/api/teaching-office/attachments/{attachment.id}/classification",
        json={"indicator": "honorary_awards"},
        headers={"Authorization": f"Bearer {evaluation_office_token}"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["indicator"] == "honorary_awards"
    
    # 验证关联已更新
    db.refresh(attachment)
    assert attachment.indicator == "honorary_awards"
    
    # 验证可以通过新指标查询到该附件
    response = client.get(
        "/api/teaching-office/attachments?indicator=honorary_awards",
        headers={"Authorization": f"Bearer {evaluation_office_token}"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["id"] == str(attachment.id)


def test_archived_attachments_query(client, db, evaluation_office_token):
    """
    测试查询已归档的附件
    
    需求: 18.4
    """
    # 创建教研室
    teaching_office = TeachingOffice(
        name="音乐教研室",
        code="MUS001",
        department="音乐学院"
    )
    db.add(teaching_office)
    db.commit()
    db.refresh(teaching_office)
    
    # 创建自评表
    evaluation = SelfEvaluation(
        teaching_office_id=teaching_office.id,
        evaluation_year=2024,
        content={"test": "data"},
        status="draft"
    )
    db.add(evaluation)
    db.commit()
    db.refresh(evaluation)
    
    # 创建已归档和未归档的附件
    archived_attachment = Attachment(
        evaluation_id=evaluation.id,
        indicator="teaching_reform_projects",
        file_name="archived.pdf",
        file_size=1024,
        file_type="application/pdf",
        storage_path=f"{evaluation.id}/test/{uuid4()}.pdf",
        classified_by="user",
        is_archived=True
    )
    
    db.add(archived_attachment)
    db.commit()
    
    # 查询已归档的附件
    response = client.get(
        "/api/teaching-office/attachments?is_archived=true",
        headers={"Authorization": f"Bearer {evaluation_office_token}"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 1
    assert all(att["is_archived"] is True for att in data)
