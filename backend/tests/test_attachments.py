import pytest
from fastapi.testclient import TestClient
from io import BytesIO
from uuid import uuid4
from unittest.mock import patch, AsyncMock

from app.models.teaching_office import TeachingOffice
from app.models.self_evaluation import SelfEvaluation
from app.models.user import User
from app.core.security import get_password_hash


@pytest.fixture
def test_user(db):
    """Create a test user"""
    user = User(
        username="testuser",
        password_hash=get_password_hash("testpassword"),
        role="teaching_office",
        name="Test User",
        email="test@example.com"
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@pytest.fixture
def test_teaching_office(db):
    """Create a test teaching office"""
    office = TeachingOffice(
        name="测试教研室",
        code="TEST001",
        department="测试部门"
    )
    db.add(office)
    db.commit()
    db.refresh(office)
    return office


@pytest.fixture
def test_evaluation(db, test_teaching_office):
    """Create a test self evaluation"""
    evaluation = SelfEvaluation(
        teaching_office_id=test_teaching_office.id,
        evaluation_year=2024,
        content={
            "teaching_process_management": "测试内容",
            "course_construction": "测试内容",
            "teaching_reform_projects": 2,
            "honorary_awards": 3
        },
        status="draft"
    )
    db.add(evaluation)
    db.commit()
    db.refresh(evaluation)
    return evaluation


@pytest.fixture
def auth_headers(client, test_user):
    """Get authentication headers"""
    response = client.post(
        "/api/auth/login",
        json={
            "username": "testuser",
            "password": "testpassword",
            "role": "teaching_office"
        }
    )
    token = response.json()["token"]
    return {"Authorization": f"Bearer {token}"}


def test_upload_single_attachment(client, db, test_evaluation, auth_headers):
    """Test uploading a single attachment"""
    # Mock MinIO upload
    with patch('app.services.minio_service.minio_service.upload_file_object', new_callable=AsyncMock) as mock_upload:
        mock_upload.return_value = True
        
        # Create test file
        file_content = b"Test file content"
        files = {
            "files": ("test.pdf", BytesIO(file_content), "application/pdf")
        }
        data = {
            "evaluation_id": str(test_evaluation.id),
            "indicator": "teaching_reform_projects"
        }
        
        response = client.post(
            "/api/teaching-office/attachments",
            files=files,
            data=data,
            headers=auth_headers
        )
        
        assert response.status_code == 201
        result = response.json()
        assert "attachment_ids" in result
        assert result["uploaded_count"] == 1
        assert len(result["attachment_ids"]) == 1


def test_upload_multiple_attachments(client, db, test_evaluation, auth_headers):
    """Test uploading multiple attachments (需求 2.3)"""
    # Mock MinIO upload
    with patch('app.services.minio_service.minio_service.upload_file_object', new_callable=AsyncMock) as mock_upload:
        mock_upload.return_value = True
        
        # Create multiple test files
        files = [
            ("files", ("test1.pdf", BytesIO(b"Test file 1"), "application/pdf")),
            ("files", ("test2.pdf", BytesIO(b"Test file 2"), "application/pdf")),
            ("files", ("test3.pdf", BytesIO(b"Test file 3"), "application/pdf"))
        ]
        data = {
            "evaluation_id": str(test_evaluation.id),
            "indicator": "honorary_awards"
        }
        
        response = client.post(
            "/api/teaching-office/attachments",
            files=files,
            data=data,
            headers=auth_headers
        )
        
        assert response.status_code == 201
        result = response.json()
        assert result["uploaded_count"] == 3
        assert len(result["attachment_ids"]) == 3


def test_upload_attachment_evaluation_not_found(client, auth_headers):
    """Test uploading attachment with non-existent evaluation"""
    with patch('app.services.minio_service.minio_service.upload_file_object', new_callable=AsyncMock) as mock_upload:
        mock_upload.return_value = True
        
        files = {
            "files": ("test.pdf", BytesIO(b"Test file"), "application/pdf")
        }
        data = {
            "evaluation_id": str(uuid4()),
            "indicator": "teaching_reform_projects"
        }
        
        response = client.post(
            "/api/teaching-office/attachments",
            files=files,
            data=data,
            headers=auth_headers
        )
        
        assert response.status_code == 404
        assert "自评表不存在" in response.json()["detail"]


def test_upload_attachment_locked_evaluation(client, db, test_evaluation, auth_headers):
    """Test uploading attachment to locked evaluation (需求 2.7)"""
    # Lock the evaluation
    test_evaluation.status = "locked"
    db.commit()
    
    with patch('app.services.minio_service.minio_service.upload_file_object', new_callable=AsyncMock) as mock_upload:
        mock_upload.return_value = True
        
        files = {
            "files": ("test.pdf", BytesIO(b"Test file"), "application/pdf")
        }
        data = {
            "evaluation_id": str(test_evaluation.id),
            "indicator": "teaching_reform_projects"
        }
        
        response = client.post(
            "/api/teaching-office/attachments",
            files=files,
            data=data,
            headers=auth_headers
        )
        
        assert response.status_code == 403
        assert "已锁定" in response.json()["detail"]


def test_get_attachments(client, db, test_evaluation, auth_headers):
    """Test retrieving attachments for an evaluation"""
    # Mock MinIO upload and create an attachment first
    with patch('app.services.minio_service.minio_service.upload_file_object', new_callable=AsyncMock) as mock_upload:
        mock_upload.return_value = True
        
        files = {
            "files": ("test.pdf", BytesIO(b"Test file"), "application/pdf")
        }
        data = {
            "evaluation_id": str(test_evaluation.id),
            "indicator": "teaching_reform_projects"
        }
        
        # Upload attachment
        client.post(
            "/api/teaching-office/attachments",
            files=files,
            data=data,
            headers=auth_headers
        )
        
        # Get attachments
        response = client.get(
            f"/api/teaching-office/attachments/{test_evaluation.id}",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        attachments = response.json()
        assert len(attachments) == 1
        assert attachments[0]["file_name"] == "test.pdf"
        assert attachments[0]["indicator"] == "teaching_reform_projects"
        assert attachments[0]["classified_by"] == "user"


def test_upload_certificate_and_project_files(client, db, test_evaluation, auth_headers):
    """Test uploading certificate and project type files (需求 2.4, 2.5)"""
    with patch('app.services.minio_service.minio_service.upload_file_object', new_callable=AsyncMock) as mock_upload:
        mock_upload.return_value = True
        
        # Upload certificate file
        cert_files = {
            "files": ("certificate.pdf", BytesIO(b"Certificate content"), "application/pdf")
        }
        cert_data = {
            "evaluation_id": str(test_evaluation.id),
            "indicator": "honorary_awards"
        }
        
        cert_response = client.post(
            "/api/teaching-office/attachments",
            files=cert_files,
            data=cert_data,
            headers=auth_headers
        )
        
        assert cert_response.status_code == 201
        
        # Upload project file
        project_files = {
            "files": ("project.docx", BytesIO(b"Project content"), "application/vnd.openxmlformats-officedocument.wordprocessingml.document")
        }
        project_data = {
            "evaluation_id": str(test_evaluation.id),
            "indicator": "teaching_reform_projects"
        }
        
        project_response = client.post(
            "/api/teaching-office/attachments",
            files=project_files,
            data=project_data,
            headers=auth_headers
        )
        
        assert project_response.status_code == 201
        
        # Verify both files are stored
        get_response = client.get(
            f"/api/teaching-office/attachments/{test_evaluation.id}",
            headers=auth_headers
        )
        
        assert get_response.status_code == 200
        attachments = get_response.json()
        assert len(attachments) == 2


@pytest.fixture
def management_user(db):
    """Create a management user for testing classification updates"""
    user = User(
        username="management_user",
        password_hash=get_password_hash("testpassword"),
        role="evaluation_office",
        name="Management User",
        email="management@example.com"
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@pytest.fixture
def management_auth_headers(client, management_user):
    """Get authentication headers for management user"""
    response = client.post(
        "/api/auth/login",
        json={
            "username": "management_user",
            "password": "testpassword",
            "role": "evaluation_office"
        }
    )
    token = response.json()["token"]
    return {"Authorization": f"Bearer {token}"}


def test_update_attachment_classification_success(client, db, test_evaluation, auth_headers, management_auth_headers):
    """Test successfully updating attachment classification (需求 5.4)"""
    with patch('app.services.minio_service.minio_service.upload_file_object', new_callable=AsyncMock) as mock_upload:
        mock_upload.return_value = True
        
        # Upload an attachment first
        files = {
            "files": ("test.pdf", BytesIO(b"Test file"), "application/pdf")
        }
        data = {
            "evaluation_id": str(test_evaluation.id),
            "indicator": "teaching_reform_projects"
        }
        
        upload_response = client.post(
            "/api/teaching-office/attachments",
            files=files,
            data=data,
            headers=auth_headers
        )
        
        assert upload_response.status_code == 201
        attachment_id = upload_response.json()["attachment_ids"][0]
        
        # Update classification as management user
        update_response = client.put(
            f"/api/teaching-office/attachments/{attachment_id}/classification",
            json={"indicator": "honorary_awards"},
            headers=management_auth_headers
        )
        
        assert update_response.status_code == 200
        result = update_response.json()
        assert result["id"] == attachment_id
        assert result["indicator"] == "honorary_awards"
        assert "teaching_reform_projects" in result["message"]
        assert "honorary_awards" in result["message"]


def test_update_attachment_classification_not_found(client, management_auth_headers):
    """Test updating classification for non-existent attachment"""
    response = client.put(
        f"/api/teaching-office/attachments/{uuid4()}/classification",
        json={"indicator": "honorary_awards"},
        headers=management_auth_headers
    )
    
    assert response.status_code == 404
    assert "附件不存在" in response.json()["detail"]


def test_update_attachment_classification_forbidden(client, db, test_evaluation, auth_headers):
    """Test that non-management users cannot update classification"""
    with patch('app.services.minio_service.minio_service.upload_file_object', new_callable=AsyncMock) as mock_upload:
        mock_upload.return_value = True
        
        # Upload an attachment
        files = {
            "files": ("test.pdf", BytesIO(b"Test file"), "application/pdf")
        }
        data = {
            "evaluation_id": str(test_evaluation.id),
            "indicator": "teaching_reform_projects"
        }
        
        upload_response = client.post(
            "/api/teaching-office/attachments",
            files=files,
            data=data,
            headers=auth_headers
        )
        
        assert upload_response.status_code == 201
        attachment_id = upload_response.json()["attachment_ids"][0]
        
        # Try to update classification as teaching office user (should fail)
        update_response = client.put(
            f"/api/teaching-office/attachments/{attachment_id}/classification",
            json={"indicator": "honorary_awards"},
            headers=auth_headers
        )
        
        assert update_response.status_code == 403
        assert "仅管理端用户可以调整附件分类" in update_response.json()["detail"]


def test_update_attachment_classification_persists(client, db, test_evaluation, auth_headers, management_auth_headers):
    """Test that classification update persists in database"""
    with patch('app.services.minio_service.minio_service.upload_file_object', new_callable=AsyncMock) as mock_upload:
        mock_upload.return_value = True
        
        # Upload an attachment
        files = {
            "files": ("test.pdf", BytesIO(b"Test file"), "application/pdf")
        }
        data = {
            "evaluation_id": str(test_evaluation.id),
            "indicator": "teaching_reform_projects"
        }
        
        upload_response = client.post(
            "/api/teaching-office/attachments",
            files=files,
            data=data,
            headers=auth_headers
        )
        
        attachment_id = upload_response.json()["attachment_ids"][0]
        
        # Update classification
        client.put(
            f"/api/teaching-office/attachments/{attachment_id}/classification",
            json={"indicator": "honorary_awards"},
            headers=management_auth_headers
        )
        
        # Verify the update persisted by fetching attachments
        get_response = client.get(
            f"/api/teaching-office/attachments/{test_evaluation.id}",
            headers=auth_headers
        )
        
        assert get_response.status_code == 200
        attachments = get_response.json()
        assert len(attachments) == 1
        assert attachments[0]["indicator"] == "honorary_awards"


def test_query_attachments_no_filters(client, db, test_evaluation, auth_headers):
    """Test querying all attachments without filters (需求 18.5)"""
    with patch('app.services.minio_service.minio_service.upload_file_object', new_callable=AsyncMock) as mock_upload:
        mock_upload.return_value = True
        
        # Upload some attachments
        files = {
            "files": ("test.pdf", BytesIO(b"Test file"), "application/pdf")
        }
        data = {
            "evaluation_id": str(test_evaluation.id),
            "indicator": "teaching_reform_projects"
        }
        
        client.post(
            "/api/teaching-office/attachments",
            files=files,
            data=data,
            headers=auth_headers
        )
        
        # Query all attachments
        response = client.get(
            "/api/teaching-office/attachments",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        attachments = response.json()
        assert len(attachments) >= 1
        assert "teaching_office_id" in attachments[0]
        assert "teaching_office_name" in attachments[0]
        assert "evaluation_year" in attachments[0]


def test_query_attachments_by_teaching_office(client, db, test_evaluation, test_teaching_office, auth_headers):
    """Test querying attachments by teaching office (需求 18.2, 18.5)"""
    with patch('app.services.minio_service.minio_service.upload_file_object', new_callable=AsyncMock) as mock_upload:
        mock_upload.return_value = True
        
        # Upload an attachment
        files = {
            "files": ("test.pdf", BytesIO(b"Test file"), "application/pdf")
        }
        data = {
            "evaluation_id": str(test_evaluation.id),
            "indicator": "teaching_reform_projects"
        }
        
        client.post(
            "/api/teaching-office/attachments",
            files=files,
            data=data,
            headers=auth_headers
        )
        
        # Query by teaching office
        response = client.get(
            f"/api/teaching-office/attachments?teaching_office_id={test_teaching_office.id}",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        attachments = response.json()
        assert len(attachments) >= 1
        assert all(att["teaching_office_id"] == str(test_teaching_office.id) for att in attachments)


def test_query_attachments_by_indicator(client, db, test_evaluation, auth_headers):
    """Test querying attachments by indicator (需求 18.3, 18.5)"""
    with patch('app.services.minio_service.minio_service.upload_file_object', new_callable=AsyncMock) as mock_upload:
        mock_upload.return_value = True
        
        # Upload attachments with different indicators
        files1 = {
            "files": ("test1.pdf", BytesIO(b"Test file 1"), "application/pdf")
        }
        data1 = {
            "evaluation_id": str(test_evaluation.id),
            "indicator": "teaching_reform_projects"
        }
        client.post("/api/teaching-office/attachments", files=files1, data=data1, headers=auth_headers)
        
        files2 = {
            "files": ("test2.pdf", BytesIO(b"Test file 2"), "application/pdf")
        }
        data2 = {
            "evaluation_id": str(test_evaluation.id),
            "indicator": "honorary_awards"
        }
        client.post("/api/teaching-office/attachments", files=files2, data=data2, headers=auth_headers)
        
        # Query by specific indicator
        response = client.get(
            "/api/teaching-office/attachments?indicator=teaching_reform_projects",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        attachments = response.json()
        assert len(attachments) >= 1
        assert all(att["indicator"] == "teaching_reform_projects" for att in attachments)


def test_query_attachments_by_year(client, db, test_evaluation, auth_headers):
    """Test querying attachments by evaluation year (需求 18.5)"""
    with patch('app.services.minio_service.minio_service.upload_file_object', new_callable=AsyncMock) as mock_upload:
        mock_upload.return_value = True
        
        # Upload an attachment
        files = {
            "files": ("test.pdf", BytesIO(b"Test file"), "application/pdf")
        }
        data = {
            "evaluation_id": str(test_evaluation.id),
            "indicator": "teaching_reform_projects"
        }
        
        client.post(
            "/api/teaching-office/attachments",
            files=files,
            data=data,
            headers=auth_headers
        )
        
        # Query by year
        response = client.get(
            f"/api/teaching-office/attachments?evaluation_year={test_evaluation.evaluation_year}",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        attachments = response.json()
        assert len(attachments) >= 1
        assert all(att["evaluation_year"] == test_evaluation.evaluation_year for att in attachments)


def test_download_attachment_success(client, db, test_evaluation, auth_headers):
    """Test downloading an attachment successfully (需求 18.6)"""
    with patch('app.services.minio_service.minio_service.upload_file_object', new_callable=AsyncMock) as mock_upload:
        mock_upload.return_value = True
        
        # Upload an attachment
        file_content = b"Test file content for download"
        files = {
            "files": ("test_download.pdf", BytesIO(file_content), "application/pdf")
        }
        data = {
            "evaluation_id": str(test_evaluation.id),
            "indicator": "teaching_reform_projects"
        }
        
        upload_response = client.post(
            "/api/teaching-office/attachments",
            files=files,
            data=data,
            headers=auth_headers
        )
        
        attachment_id = upload_response.json()["attachment_ids"][0]
        
        # Mock MinIO file stream
        from unittest.mock import MagicMock
        mock_stream = MagicMock()
        mock_stream.read.return_value = file_content
        mock_stream.__iter__ = lambda self: iter([file_content])
        
        with patch('app.services.minio_service.minio_service.get_file_stream') as mock_get_stream:
            mock_get_stream.return_value = mock_stream
            
            # Download the attachment
            download_response = client.get(
                f"/api/teaching-office/attachments/{attachment_id}/download",
                headers=auth_headers
            )
            
            assert download_response.status_code == 200
            assert download_response.headers["content-type"] == "application/pdf"
            assert "attachment" in download_response.headers["content-disposition"]
            assert "test_download.pdf" in download_response.headers["content-disposition"]


def test_download_attachment_not_found(client, auth_headers):
    """Test downloading non-existent attachment (需求 18.6)"""
    response = client.get(
        f"/api/teaching-office/attachments/{uuid4()}/download",
        headers=auth_headers
    )
    
    assert response.status_code == 404
    assert "附件不存在" in response.json()["detail"]


def test_download_attachment_not_archived(client, db, test_evaluation, auth_headers):
    """Test downloading attachment that is not archived"""
    with patch('app.services.minio_service.minio_service.upload_file_object', new_callable=AsyncMock) as mock_upload:
        mock_upload.return_value = True
        
        # Upload an attachment
        files = {
            "files": ("test.pdf", BytesIO(b"Test file"), "application/pdf")
        }
        data = {
            "evaluation_id": str(test_evaluation.id),
            "indicator": "teaching_reform_projects"
        }
        
        upload_response = client.post(
            "/api/teaching-office/attachments",
            files=files,
            data=data,
            headers=auth_headers
        )
        
        attachment_id = upload_response.json()["attachment_ids"][0]
        
        # Manually set is_archived to False
        from app.models.attachment import Attachment
        from uuid import UUID
        attachment = db.query(Attachment).filter(Attachment.id == UUID(attachment_id)).first()
        attachment.is_archived = False
        db.commit()
        
        # Try to download
        response = client.get(
            f"/api/teaching-office/attachments/{attachment_id}/download",
            headers=auth_headers
        )
        
        assert response.status_code == 400
        assert "未归档" in response.json()["detail"]


def test_download_attachment_minio_failure(client, db, test_evaluation, auth_headers):
    """Test downloading attachment when MinIO fails"""
    with patch('app.services.minio_service.minio_service.upload_file_object', new_callable=AsyncMock) as mock_upload:
        mock_upload.return_value = True
        
        # Upload an attachment
        files = {
            "files": ("test.pdf", BytesIO(b"Test file"), "application/pdf")
        }
        data = {
            "evaluation_id": str(test_evaluation.id),
            "indicator": "teaching_reform_projects"
        }
        
        upload_response = client.post(
            "/api/teaching-office/attachments",
            files=files,
            data=data,
            headers=auth_headers
        )
        
        attachment_id = upload_response.json()["attachment_ids"][0]
        
        # Mock MinIO failure
        with patch('app.services.minio_service.minio_service.get_file_stream') as mock_get_stream:
            mock_get_stream.return_value = None
            
            # Try to download
            response = client.get(
                f"/api/teaching-office/attachments/{attachment_id}/download",
                headers=auth_headers
            )
            
            assert response.status_code == 500
            assert "无法获取文件" in response.json()["detail"]

