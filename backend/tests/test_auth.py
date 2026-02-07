import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from datetime import timedelta
from unittest.mock import Mock, patch

from app.main import app
from app.db.base import get_db
from app.core.security import get_password_hash, verify_password, create_access_token, decode_access_token
from app.models.user import User

# Create test database
SQLALCHEMY_DATABASE_URL = "sqlite:///./test_auth.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)


class TestPasswordHashing:
    """Test password hashing and verification."""
    
    def test_password_hash_and_verify(self):
        """Test that password hashing and verification work correctly."""
        password = "mysecretpassword"
        hashed = get_password_hash(password)
        
        assert hashed != password
        assert verify_password(password, hashed) is True
        assert verify_password("wrongpassword", hashed) is False


class TestJWTToken:
    """Test JWT token creation and decoding."""
    
    def test_create_access_token(self):
        """Test JWT token creation."""
        data = {"sub": "testuser", "user_id": "123", "role": "teaching_office"}
        token = create_access_token(data)
        
        assert token is not None
        assert isinstance(token, str)
    
    def test_decode_access_token(self):
        """Test JWT token decoding."""
        data = {"sub": "testuser", "user_id": "123", "role": "teaching_office"}
        token = create_access_token(data)
        
        decoded = decode_access_token(token)
        
        assert decoded is not None
        assert decoded["sub"] == "testuser"
        assert decoded["user_id"] == "123"
        assert decoded["role"] == "teaching_office"
    
    def test_decode_invalid_token(self):
        """Test decoding an invalid token."""
        invalid_token = "invalid.token.here"
        decoded = decode_access_token(invalid_token)
        
        assert decoded is None
    
    def test_token_expiration(self):
        """Test token with custom expiration."""
        data = {"sub": "testuser", "user_id": "123", "role": "teaching_office"}
        token = create_access_token(data, expires_delta=timedelta(minutes=30))
        
        decoded = decode_access_token(token)
        
        assert decoded is not None
        assert "exp" in decoded


class TestLoginEndpoint:
    """Test login endpoint with mocked database."""
    
    @patch('app.api.v1.endpoints.auth.get_db')
    def test_login_success(self, mock_get_db):
        """Test successful login."""
        # Create mock user
        mock_user = Mock(spec=User)
        mock_user.id = "test-user-id"
        mock_user.username = "testuser"
        mock_user.password_hash = get_password_hash("testpassword")
        mock_user.role = "teaching_office"
        
        # Mock database session
        mock_db = Mock(spec=Session)
        mock_query = Mock()
        mock_query.filter.return_value.first.return_value = mock_user
        mock_db.query.return_value = mock_query
        mock_get_db.return_value.__enter__.return_value = mock_db
        
        response = client.post(
            "/api/auth/login",
            json={
                "username": "testuser",
                "password": "testpassword",
                "role": "teaching_office"
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "token" in data
        assert "userId" in data
        assert "role" in data
        assert data["role"] == "teaching_office"
        assert "expiresIn" in data
    
    @patch('app.api.v1.endpoints.auth.get_db')
    def test_login_wrong_password(self, mock_get_db):
        """Test login with wrong password."""
        # Create mock user
        mock_user = Mock(spec=User)
        mock_user.username = "testuser"
        mock_user.password_hash = get_password_hash("testpassword")
        mock_user.role = "teaching_office"
        
        # Mock database session
        mock_db = Mock(spec=Session)
        mock_query = Mock()
        mock_query.filter.return_value.first.return_value = mock_user
        mock_db.query.return_value = mock_query
        mock_get_db.return_value.__enter__.return_value = mock_db
        
        response = client.post(
            "/api/auth/login",
            json={
                "username": "testuser",
                "password": "wrongpassword",
                "role": "teaching_office"
            }
        )
        
        assert response.status_code == 401
        assert "Incorrect username or password" in response.json()["detail"]
    
    @patch('app.api.v1.endpoints.auth.get_db')
    def test_login_nonexistent_user(self, mock_get_db):
        """Test login with non-existent user."""
        # Mock database session
        mock_db = Mock(spec=Session)
        mock_query = Mock()
        mock_query.filter.return_value.first.return_value = None
        mock_db.query.return_value = mock_query
        mock_get_db.return_value.__enter__.return_value = mock_db
        
        response = client.post(
            "/api/auth/login",
            json={
                "username": "nonexistent",
                "password": "password",
                "role": "teaching_office"
            }
        )
        
        assert response.status_code == 401
        assert "Incorrect username or password" in response.json()["detail"]
    
    @patch('app.api.v1.endpoints.auth.get_db')
    def test_login_wrong_role(self, mock_get_db):
        """Test login with wrong role."""
        # Create mock user
        mock_user = Mock(spec=User)
        mock_user.username = "testuser"
        mock_user.password_hash = get_password_hash("testpassword")
        mock_user.role = "teaching_office"
        
        # Mock database session
        mock_db = Mock(spec=Session)
        mock_query = Mock()
        mock_query.filter.return_value.first.return_value = mock_user
        mock_db.query.return_value = mock_query
        mock_get_db.return_value.__enter__.return_value = mock_db
        
        response = client.post(
            "/api/auth/login",
            json={
                "username": "testuser",
                "password": "testpassword",
                "role": "evaluation_team"
            }
        )
        
        assert response.status_code == 403
        assert "role does not match" in response.json()["detail"]


class TestTokenVerification:
    """Test token verification endpoint."""
    
    @patch('app.core.deps.get_db')
    def test_verify_valid_token(self, mock_get_db):
        """Test verification with valid token."""
        # Create mock user
        mock_user = Mock(spec=User)
        mock_user.id = "test-user-id"
        mock_user.username = "testuser"
        mock_user.role = "teaching_office"
        
        # Mock database session
        mock_db = Mock(spec=Session)
        mock_query = Mock()
        mock_query.filter.return_value.first.return_value = mock_user
        mock_db.query.return_value = mock_query
        mock_get_db.return_value.__enter__.return_value = mock_db
        
        # Create a valid token
        token = create_access_token({
            "sub": "testuser",
            "user_id": "test-user-id",
            "role": "teaching_office"
        })
        
        # Verify token
        response = client.get(
            "/api/auth/verify",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["valid"] is True
        assert "userId" in data
        assert "role" in data
        assert data["role"] == "teaching_office"
    
    def test_verify_invalid_token(self):
        """Test verification with invalid token."""
        response = client.get(
            "/api/auth/verify",
            headers={"Authorization": "Bearer invalid.token.here"}
        )
        
        assert response.status_code == 401
    
    def test_verify_missing_token(self):
        """Test verification without token."""
        response = client.get("/api/auth/verify")
        
        assert response.status_code == 401



class TestRoleBasedPermissions:
    """Test role-based permission middleware."""
    
    @patch('app.core.deps.get_db')
    def test_role_checker_allows_authorized_role(self, mock_get_db):
        """Test that RoleChecker allows users with authorized roles."""
        from app.core.deps import RoleChecker
        
        # Create mock user with teaching_office role
        mock_user = Mock(spec=User)
        mock_user.id = "test-user-id"
        mock_user.username = "testuser"
        mock_user.role = "teaching_office"
        
        # Mock database session
        mock_db = Mock(spec=Session)
        mock_query = Mock()
        mock_query.filter.return_value.first.return_value = mock_user
        mock_db.query.return_value = mock_query
        mock_get_db.return_value = mock_db
        
        # Create role checker for teaching_office
        role_checker = RoleChecker(["teaching_office"])
        
        # Should not raise exception
        result = role_checker(current_user=mock_user)
        assert result == mock_user
    
    @patch('app.core.deps.get_db')
    def test_role_checker_denies_unauthorized_role(self, mock_get_db):
        """Test that RoleChecker denies users without authorized roles."""
        from app.core.deps import RoleChecker
        from fastapi import HTTPException
        
        # Create mock user with teaching_office role
        mock_user = Mock(spec=User)
        mock_user.id = "test-user-id"
        mock_user.username = "testuser"
        mock_user.role = "teaching_office"
        
        # Mock database session
        mock_db = Mock(spec=Session)
        mock_query = Mock()
        mock_query.filter.return_value.first.return_value = mock_user
        mock_db.query.return_value = mock_query
        mock_get_db.return_value = mock_db
        
        # Create role checker for evaluation_team (user doesn't have this role)
        role_checker = RoleChecker(["evaluation_team"])
        
        # Should raise 403 exception
        with pytest.raises(HTTPException) as exc_info:
            role_checker(current_user=mock_user)
        
        assert exc_info.value.status_code == 403
        assert "Access denied" in exc_info.value.detail
        assert "evaluation_team" in exc_info.value.detail
    
    @patch('app.core.deps.get_db')
    def test_role_checker_allows_multiple_roles(self, mock_get_db):
        """Test that RoleChecker allows any of multiple authorized roles."""
        from app.core.deps import RoleChecker
        
        # Create mock user with evaluation_office role
        mock_user = Mock(spec=User)
        mock_user.id = "test-user-id"
        mock_user.username = "testuser"
        mock_user.role = "evaluation_office"
        
        # Mock database session
        mock_db = Mock(spec=Session)
        mock_query = Mock()
        mock_query.filter.return_value.first.return_value = mock_user
        mock_db.query.return_value = mock_query
        mock_get_db.return_value = mock_db
        
        # Create role checker for evaluation_team OR evaluation_office
        role_checker = RoleChecker(["evaluation_team", "evaluation_office"])
        
        # Should not raise exception (user has evaluation_office)
        result = role_checker(current_user=mock_user)
        assert result == mock_user
    
    @patch('app.core.deps.get_db')
    def test_require_teaching_office(self, mock_get_db):
        """Test require_teaching_office convenience function."""
        from app.core.deps import require_teaching_office
        
        # Create mock user with teaching_office role
        mock_user = Mock(spec=User)
        mock_user.id = "test-user-id"
        mock_user.username = "testuser"
        mock_user.role = "teaching_office"
        
        # Mock database session
        mock_db = Mock(spec=Session)
        mock_query = Mock()
        mock_query.filter.return_value.first.return_value = mock_user
        mock_db.query.return_value = mock_query
        mock_get_db.return_value = mock_db
        
        # Should not raise exception
        result = require_teaching_office(current_user=mock_user)
        assert result == mock_user
    
    @patch('app.core.deps.get_db')
    def test_require_evaluation_team(self, mock_get_db):
        """Test require_evaluation_team convenience function."""
        from app.core.deps import require_evaluation_team
        
        # Create mock user with evaluation_team role
        mock_user = Mock(spec=User)
        mock_user.id = "test-user-id"
        mock_user.username = "testuser"
        mock_user.role = "evaluation_team"
        
        # Mock database session
        mock_db = Mock(spec=Session)
        mock_query = Mock()
        mock_query.filter.return_value.first.return_value = mock_user
        mock_db.query.return_value = mock_query
        mock_get_db.return_value = mock_db
        
        # Should not raise exception
        result = require_evaluation_team(current_user=mock_user)
        assert result == mock_user
    
    @patch('app.core.deps.get_db')
    def test_require_evaluation_office(self, mock_get_db):
        """Test require_evaluation_office convenience function."""
        from app.core.deps import require_evaluation_office
        
        # Create mock user with evaluation_office role
        mock_user = Mock(spec=User)
        mock_user.id = "test-user-id"
        mock_user.username = "testuser"
        mock_user.role = "evaluation_office"
        
        # Mock database session
        mock_db = Mock(spec=Session)
        mock_query = Mock()
        mock_query.filter.return_value.first.return_value = mock_user
        mock_db.query.return_value = mock_query
        mock_get_db.return_value = mock_db
        
        # Should not raise exception
        result = require_evaluation_office(current_user=mock_user)
        assert result == mock_user
    
    @patch('app.core.deps.get_db')
    def test_require_president_office(self, mock_get_db):
        """Test require_president_office convenience function."""
        from app.core.deps import require_president_office
        
        # Create mock user with president_office role
        mock_user = Mock(spec=User)
        mock_user.id = "test-user-id"
        mock_user.username = "testuser"
        mock_user.role = "president_office"
        
        # Mock database session
        mock_db = Mock(spec=Session)
        mock_query = Mock()
        mock_query.filter.return_value.first.return_value = mock_user
        mock_db.query.return_value = mock_query
        mock_get_db.return_value = mock_db
        
        # Should not raise exception
        result = require_president_office(current_user=mock_user)
        assert result == mock_user
    
    @patch('app.core.deps.get_db')
    def test_require_management_roles(self, mock_get_db):
        """Test require_management_roles allows evaluation_team and evaluation_office."""
        from app.core.deps import require_management_roles
        
        # Test with evaluation_team role
        mock_user_team = Mock(spec=User)
        mock_user_team.id = "test-user-id-1"
        mock_user_team.username = "teamuser"
        mock_user_team.role = "evaluation_team"
        
        result = require_management_roles(current_user=mock_user_team)
        assert result == mock_user_team
        
        # Test with evaluation_office role
        mock_user_office = Mock(spec=User)
        mock_user_office.id = "test-user-id-2"
        mock_user_office.username = "officeuser"
        mock_user_office.role = "evaluation_office"
        
        result = require_management_roles(current_user=mock_user_office)
        assert result == mock_user_office
    
    @patch('app.core.deps.get_db')
    def test_require_management_roles_denies_other_roles(self, mock_get_db):
        """Test require_management_roles denies non-management roles."""
        from app.core.deps import RoleChecker
        from fastapi import HTTPException
        
        # Create mock user with teaching_office role (not a management role)
        mock_user = Mock(spec=User)
        mock_user.id = "test-user-id"
        mock_user.username = "testuser"
        mock_user.role = "teaching_office"
        
        # Create role checker for management roles
        role_checker = RoleChecker(["evaluation_team", "evaluation_office"])
        
        # Should raise 403 exception
        with pytest.raises(HTTPException) as exc_info:
            role_checker(current_user=mock_user)
        
        assert exc_info.value.status_code == 403
    
    @patch('app.core.deps.get_db')
    def test_require_any_role_allows_all_valid_roles(self, mock_get_db):
        """Test require_any_role allows all valid system roles."""
        from app.core.deps import require_any_role
        
        roles = ["teaching_office", "evaluation_team", "evaluation_office", "president_office"]
        
        for role in roles:
            mock_user = Mock(spec=User)
            mock_user.id = f"test-user-{role}"
            mock_user.username = f"user-{role}"
            mock_user.role = role
            
            result = require_any_role(current_user=mock_user)
            assert result == mock_user
    
    @patch('app.core.deps.get_db')
    def test_role_checker_with_all_four_roles(self, mock_get_db):
        """Test that all four system roles work correctly with RoleChecker."""
        from app.core.deps import RoleChecker
        
        roles = ["teaching_office", "evaluation_team", "evaluation_office", "president_office"]
        
        for role in roles:
            mock_user = Mock(spec=User)
            mock_user.id = f"test-user-{role}"
            mock_user.username = f"user-{role}"
            mock_user.role = role
            
            # Create role checker for this specific role
            role_checker = RoleChecker([role])
            
            # Should allow the user
            result = role_checker(current_user=mock_user)
            assert result == mock_user
            
            # Create role checker for a different role
            other_roles = [r for r in roles if r != role]
            role_checker_deny = RoleChecker([other_roles[0]])
            
            # Should deny the user
            from fastapi import HTTPException
            with pytest.raises(HTTPException) as exc_info:
                role_checker_deny(current_user=mock_user)
            
            assert exc_info.value.status_code == 403
