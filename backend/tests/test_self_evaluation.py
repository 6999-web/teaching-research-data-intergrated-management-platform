import pytest
from uuid import uuid4
from datetime import datetime
from fastapi import status

from app.models.teaching_office import TeachingOffice
from app.models.user import User
from app.models.self_evaluation import SelfEvaluation
from app.core.security import get_password_hash


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
def test_user(db, teaching_office):
    """创建测试用户"""
    user = User(
        username="testuser",
        password_hash=get_password_hash("testpass123"),
        role="teaching_office",
        teaching_office_id=teaching_office.id,
        name="测试用户",
        email="test@example.com"
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@pytest.fixture
def auth_headers(client, test_user):
    """获取认证头"""
    response = client.post(
        "/api/v1/auth/login",
        json={
            "username": "testuser",
            "password": "testpass123",
            "role": "teaching_office"
        }
    )
    # Debug: print response if it fails
    if response.status_code != 200:
        print(f"Login failed: {response.status_code}, {response.json()}")
    token = response.json()["token"]
    return {"Authorization": f"Bearer {token}"}


class TestSelfEvaluationCreate:
    """测试自评表创建功能"""
    
    def test_create_self_evaluation_success(self, client, auth_headers, teaching_office):
        """测试成功创建自评表"""
        evaluation_data = {
            "teaching_office_id": str(teaching_office.id),
            "evaluation_year": 2024,
            "content": {
                "teaching_process_management": "教学过程管理良好",
                "course_construction": "课程建设完善",
                "teaching_reform_projects": 3,
                "honorary_awards": 2
            }
        }
        
        response = client.post(
            "/api/v1/teaching-office/self-evaluation",
            json=evaluation_data,
            headers=auth_headers
        )
        
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert "evaluation_id" in data
        assert data["status"] == "draft"
        assert "created_at" in data
    
    def test_create_self_evaluation_updates_existing(self, client, auth_headers, teaching_office, db):
        """测试更新已存在的自评表"""
        # 先创建一个自评表
        existing_evaluation = SelfEvaluation(
            teaching_office_id=teaching_office.id,
            evaluation_year=2024,
            content={
                "teaching_process_management": "旧内容",
                "course_construction": "旧内容",
                "teaching_reform_projects": 1,
                "honorary_awards": 1
            },
            status="draft"
        )
        db.add(existing_evaluation)
        db.commit()
        db.refresh(existing_evaluation)
        
        # 尝试创建相同年份的自评表
        evaluation_data = {
            "teaching_office_id": str(teaching_office.id),
            "evaluation_year": 2024,
            "content": {
                "teaching_process_management": "新内容",
                "course_construction": "新内容",
                "teaching_reform_projects": 3,
                "honorary_awards": 2
            }
        }
        
        response = client.post(
            "/api/v1/teaching-office/self-evaluation",
            json=evaluation_data,
            headers=auth_headers
        )
        
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["evaluation_id"] == str(existing_evaluation.id)
        
        # 验证内容已更新
        db.refresh(existing_evaluation)
        assert existing_evaluation.content["teaching_process_management"] == "新内容"
    
    def test_create_self_evaluation_locked_fails(self, client, auth_headers, teaching_office, db):
        """测试锁定状态下无法创建/更新自评表"""
        # 创建一个已锁定的自评表
        locked_evaluation = SelfEvaluation(
            teaching_office_id=teaching_office.id,
            evaluation_year=2024,
            content={
                "teaching_process_management": "内容",
                "course_construction": "内容",
                "teaching_reform_projects": 1,
                "honorary_awards": 1
            },
            status="locked"
        )
        db.add(locked_evaluation)
        db.commit()
        
        # 尝试更新
        evaluation_data = {
            "teaching_office_id": str(teaching_office.id),
            "evaluation_year": 2024,
            "content": {
                "teaching_process_management": "新内容",
                "course_construction": "新内容",
                "teaching_reform_projects": 3,
                "honorary_awards": 2
            }
        }
        
        response = client.post(
            "/api/v1/teaching-office/self-evaluation",
            json=evaluation_data,
            headers=auth_headers
        )
        
        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert "锁定" in response.json()["detail"]


class TestSelfEvaluationGet:
    """测试自评表查询功能"""
    
    def test_get_self_evaluation_success(self, client, auth_headers, teaching_office, db):
        """测试成功查询自评表"""
        # 创建自评表
        evaluation = SelfEvaluation(
            teaching_office_id=teaching_office.id,
            evaluation_year=2024,
            content={
                "teaching_process_management": "内容",
                "course_construction": "内容",
                "teaching_reform_projects": 3,
                "honorary_awards": 2
            },
            status="draft"
        )
        db.add(evaluation)
        db.commit()
        db.refresh(evaluation)
        
        response = client.get(
            f"/api/v1/teaching-office/self-evaluation/{evaluation.id}",
            headers=auth_headers
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["id"] == str(evaluation.id)
        assert data["status"] == "draft"
        assert data["evaluation_year"] == 2024
        assert data["content"]["teaching_reform_projects"] == 3
    
    def test_get_self_evaluation_not_found(self, client, auth_headers):
        """测试查询不存在的自评表"""
        fake_id = uuid4()
        response = client.get(
            f"/api/v1/teaching-office/self-evaluation/{fake_id}",
            headers=auth_headers
        )
        
        assert response.status_code == status.HTTP_404_NOT_FOUND


class TestSelfEvaluationUpdate:
    """测试自评表更新功能"""
    
    def test_update_self_evaluation_content(self, client, auth_headers, teaching_office, db):
        """测试更新自评表内容"""
        # 创建自评表
        evaluation = SelfEvaluation(
            teaching_office_id=teaching_office.id,
            evaluation_year=2024,
            content={
                "teaching_process_management": "旧内容",
                "course_construction": "旧内容",
                "teaching_reform_projects": 1,
                "honorary_awards": 1
            },
            status="draft"
        )
        db.add(evaluation)
        db.commit()
        db.refresh(evaluation)
        
        update_data = {
            "content": {
                "teaching_process_management": "新内容",
                "course_construction": "新内容",
                "teaching_reform_projects": 5,
                "honorary_awards": 3
            }
        }
        
        response = client.put(
            f"/api/v1/teaching-office/self-evaluation/{evaluation.id}",
            json=update_data,
            headers=auth_headers
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["content"]["teaching_reform_projects"] == 5
        assert data["content"]["honorary_awards"] == 3
    
    def test_update_self_evaluation_status(self, client, auth_headers, teaching_office, db):
        """测试更新自评表状态"""
        # 创建自评表
        evaluation = SelfEvaluation(
            teaching_office_id=teaching_office.id,
            evaluation_year=2024,
            content={
                "teaching_process_management": "内容",
                "course_construction": "内容",
                "teaching_reform_projects": 1,
                "honorary_awards": 1
            },
            status="draft"
        )
        db.add(evaluation)
        db.commit()
        db.refresh(evaluation)
        
        update_data = {
            "status": "submitted"
        }
        
        response = client.put(
            f"/api/v1/teaching-office/self-evaluation/{evaluation.id}",
            json=update_data,
            headers=auth_headers
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["status"] == "submitted"
        assert data["submitted_at"] is not None
    
    def test_update_locked_evaluation_fails(self, client, auth_headers, teaching_office, db):
        """测试更新锁定的自评表失败"""
        # 创建已锁定的自评表
        evaluation = SelfEvaluation(
            teaching_office_id=teaching_office.id,
            evaluation_year=2024,
            content={
                "teaching_process_management": "内容",
                "course_construction": "内容",
                "teaching_reform_projects": 1,
                "honorary_awards": 1
            },
            status="locked"
        )
        db.add(evaluation)
        db.commit()
        db.refresh(evaluation)
        
        update_data = {
            "content": {
                "teaching_process_management": "新内容",
                "course_construction": "新内容",
                "teaching_reform_projects": 5,
                "honorary_awards": 3
            }
        }
        
        response = client.put(
            f"/api/v1/teaching-office/self-evaluation/{evaluation.id}",
            json=update_data,
            headers=auth_headers
        )
        
        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert "锁定" in response.json()["detail"]
    
    def test_update_status_to_invalid_value(self, client, auth_headers, teaching_office, db):
        """测试更新状态为无效值"""
        # 创建自评表
        evaluation = SelfEvaluation(
            teaching_office_id=teaching_office.id,
            evaluation_year=2024,
            content={
                "teaching_process_management": "内容",
                "course_construction": "内容",
                "teaching_reform_projects": 1,
                "honorary_awards": 1
            },
            status="draft"
        )
        db.add(evaluation)
        db.commit()
        db.refresh(evaluation)
        
        update_data = {
            "status": "invalid_status"
        }
        
        response = client.put(
            f"/api/v1/teaching-office/self-evaluation/{evaluation.id}",
            json=update_data,
            headers=auth_headers
        )
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST


class TestSelfEvaluationStatusManagement:
    """测试自评表状态管理"""
    
    def test_status_transitions(self, client, auth_headers, teaching_office, db):
        """测试状态转换流程"""
        # 创建自评表
        evaluation = SelfEvaluation(
            teaching_office_id=teaching_office.id,
            evaluation_year=2024,
            content={
                "teaching_process_management": "内容",
                "course_construction": "内容",
                "teaching_reform_projects": 1,
                "honorary_awards": 1
            },
            status="draft"
        )
        db.add(evaluation)
        db.commit()
        db.refresh(evaluation)
        
        # draft -> submitted
        response = client.put(
            f"/api/v1/teaching-office/self-evaluation/{evaluation.id}",
            json={"status": "submitted"},
            headers=auth_headers
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.json()["status"] == "submitted"
        
        # submitted -> locked
        response = client.put(
            f"/api/v1/teaching-office/self-evaluation/{evaluation.id}",
            json={"status": "locked"},
            headers=auth_headers
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.json()["status"] == "locked"


class TestSelfEvaluationLocking:
    """测试自评表锁定机制 - 需求 2.6, 2.7, 2.8"""
    
    def test_submit_locks_evaluation_with_attachments(self, client, auth_headers, teaching_office, db):
        """测试提交自评表时自动锁定（有附件）- 需求 2.6"""
        from app.models.attachment import Attachment
        
        # 创建自评表
        evaluation = SelfEvaluation(
            teaching_office_id=teaching_office.id,
            evaluation_year=2024,
            content={
                "teaching_process_management": "内容",
                "course_construction": "内容",
                "teaching_reform_projects": 1,
                "honorary_awards": 1
            },
            status="draft"
        )
        db.add(evaluation)
        db.commit()
        db.refresh(evaluation)
        
        # 添加附件
        attachment = Attachment(
            evaluation_id=evaluation.id,
            indicator="teaching_reform_projects",
            file_name="test.pdf",
            file_size=1024,
            file_type="application/pdf",
            storage_path=f"{evaluation.id}/teaching_reform_projects/test.pdf",
            classified_by="user"
        )
        db.add(attachment)
        db.commit()
        
        # 提交自评表
        response = client.post(
            f"/api/v1/teaching-office/self-evaluation/{evaluation.id}/submit",
            headers=auth_headers
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["status"] == "locked"
        assert data["submitted_at"] is not None
        assert "锁定" in data["message"]
        
        # 验证数据库中的状态
        db.refresh(evaluation)
        assert evaluation.status == "locked"
        assert evaluation.submitted_at is not None
    
    def test_submit_without_attachments_fails(self, client, auth_headers, teaching_office, db):
        """测试没有附件时无法提交 - 需求 2.6"""
        # 创建自评表（无附件）
        evaluation = SelfEvaluation(
            teaching_office_id=teaching_office.id,
            evaluation_year=2024,
            content={
                "teaching_process_management": "内容",
                "course_construction": "内容",
                "teaching_reform_projects": 1,
                "honorary_awards": 1
            },
            status="draft"
        )
        db.add(evaluation)
        db.commit()
        db.refresh(evaluation)
        
        # 尝试提交
        response = client.post(
            f"/api/v1/teaching-office/self-evaluation/{evaluation.id}/submit",
            headers=auth_headers
        )
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "附件" in response.json()["detail"]
    
    def test_submit_already_locked_fails(self, client, auth_headers, teaching_office, db):
        """测试已锁定的自评表无法再次提交 - 需求 2.7"""
        from app.models.attachment import Attachment
        
        # 创建已锁定的自评表
        evaluation = SelfEvaluation(
            teaching_office_id=teaching_office.id,
            evaluation_year=2024,
            content={
                "teaching_process_management": "内容",
                "course_construction": "内容",
                "teaching_reform_projects": 1,
                "honorary_awards": 1
            },
            status="locked",
            submitted_at=datetime.utcnow()
        )
        db.add(evaluation)
        db.commit()
        db.refresh(evaluation)
        
        # 添加附件
        attachment = Attachment(
            evaluation_id=evaluation.id,
            indicator="teaching_reform_projects",
            file_name="test.pdf",
            file_size=1024,
            file_type="application/pdf",
            storage_path=f"{evaluation.id}/teaching_reform_projects/test.pdf",
            classified_by="user"
        )
        db.add(attachment)
        db.commit()
        
        # 尝试再次提交
        response = client.post(
            f"/api/v1/teaching-office/self-evaluation/{evaluation.id}/submit",
            headers=auth_headers
        )
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "已经提交" in response.json()["detail"] or "锁定" in response.json()["detail"]
    
    def test_locked_evaluation_prevents_modification(self, client, auth_headers, teaching_office, db):
        """测试锁定状态下禁止修改 - 需求 2.7"""
        # 创建已锁定的自评表
        evaluation = SelfEvaluation(
            teaching_office_id=teaching_office.id,
            evaluation_year=2024,
            content={
                "teaching_process_management": "内容",
                "course_construction": "内容",
                "teaching_reform_projects": 1,
                "honorary_awards": 1
            },
            status="locked"
        )
        db.add(evaluation)
        db.commit()
        db.refresh(evaluation)
        
        # 尝试修改内容
        update_data = {
            "content": {
                "teaching_process_management": "新内容",
                "course_construction": "新内容",
                "teaching_reform_projects": 5,
                "honorary_awards": 3
            }
        }
        
        response = client.put(
            f"/api/v1/teaching-office/self-evaluation/{evaluation.id}",
            json=update_data,
            headers=auth_headers
        )
        
        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert "锁定" in response.json()["detail"]
    
    def test_unlock_by_management(self, client, teaching_office, db):
        """测试管理端解锁自评表 - 需求 2.8"""
        # 创建管理端用户
        management_user = User(
            username="management",
            password_hash=get_password_hash("testpass123"),
            role="evaluation_office",
            name="管理员",
            email="management@example.com"
        )
        db.add(management_user)
        db.commit()
        
        # 获取管理端认证头
        response = client.post(
            "/api/v1/auth/login",
            json={
                "username": "management",
                "password": "testpass123",
                "role": "evaluation_office"
            }
        )
        management_headers = {"Authorization": f"Bearer {response.json()['token']}"}
        
        # 创建已锁定的自评表
        evaluation = SelfEvaluation(
            teaching_office_id=teaching_office.id,
            evaluation_year=2024,
            content={
                "teaching_process_management": "内容",
                "course_construction": "内容",
                "teaching_reform_projects": 1,
                "honorary_awards": 1
            },
            status="locked",
            submitted_at=datetime.utcnow()
        )
        db.add(evaluation)
        db.commit()
        db.refresh(evaluation)
        
        # 管理端解锁
        response = client.post(
            f"/api/v1/teaching-office/self-evaluation/{evaluation.id}/unlock",
            params={"reason": "需要补充材料"},
            headers=management_headers
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["status"] == "draft"
        assert data["unlocked_at"] is not None
        assert data["unlock_reason"] == "需要补充材料"
        assert "解锁" in data["message"]
        
        # 验证数据库中的状态
        db.refresh(evaluation)
        assert evaluation.status == "draft"
    
    def test_unlock_by_teaching_office_fails(self, client, auth_headers, teaching_office, db):
        """测试教研室用户无法解锁 - 需求 2.8"""
        # 创建已锁定的自评表
        evaluation = SelfEvaluation(
            teaching_office_id=teaching_office.id,
            evaluation_year=2024,
            content={
                "teaching_process_management": "内容",
                "course_construction": "内容",
                "teaching_reform_projects": 1,
                "honorary_awards": 1
            },
            status="locked"
        )
        db.add(evaluation)
        db.commit()
        db.refresh(evaluation)
        
        # 教研室用户尝试解锁
        response = client.post(
            f"/api/v1/teaching-office/self-evaluation/{evaluation.id}/unlock",
            headers=auth_headers
        )
        
        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert "管理端" in response.json()["detail"]
    
    def test_unlock_non_locked_evaluation_fails(self, client, teaching_office, db):
        """测试解锁未锁定的自评表失败 - 需求 2.8"""
        # 创建管理端用户
        management_user = User(
            username="management2",
            password_hash=get_password_hash("testpass123"),
            role="evaluation_office",
            name="管理员",
            email="management2@example.com"
        )
        db.add(management_user)
        db.commit()
        
        # 获取管理端认证头
        response = client.post(
            "/api/v1/auth/login",
            json={
                "username": "management2",
                "password": "testpass123",
                "role": "evaluation_office"
            }
        )
        management_headers = {"Authorization": f"Bearer {response.json()['token']}"}
        
        # 创建draft状态的自评表
        evaluation = SelfEvaluation(
            teaching_office_id=teaching_office.id,
            evaluation_year=2024,
            content={
                "teaching_process_management": "内容",
                "course_construction": "内容",
                "teaching_reform_projects": 1,
                "honorary_awards": 1
            },
            status="draft"
        )
        db.add(evaluation)
        db.commit()
        db.refresh(evaluation)
        
        # 尝试解锁
        response = client.post(
            f"/api/v1/teaching-office/self-evaluation/{evaluation.id}/unlock",
            headers=management_headers
        )
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "未处于锁定状态" in response.json()["detail"]

