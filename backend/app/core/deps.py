from typing import Generator, Optional, List, Callable
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.db.base import SessionLocal
from app.core.security import decode_access_token
from app.models.user import User
from app.schemas.auth import TokenData

oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"/api/auth/login")


def get_db() -> Generator:
    """Get database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> User:
    """Get current authenticated user from JWT token."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    payload = decode_access_token(token)
    if payload is None:
        raise credentials_exception
    
    username: str = payload.get("sub")
    user_id: str = payload.get("user_id")
    role: str = payload.get("role")
    
    if username is None or user_id is None or role is None:
        raise credentials_exception
    
    token_data = TokenData(username=username, user_id=user_id, role=role)
    
    user = db.query(User).filter(User.username == token_data.username).first()
    if user is None:
        raise credentials_exception
    
    return user


def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """Get current active user."""
    return current_user


class RoleChecker:
    """
    Role-based permission checker.
    
    Usage:
        @router.get("/endpoint")
        def endpoint(user: User = Depends(RoleChecker(["teaching_office"]))):
            ...
    """
    
    def __init__(self, allowed_roles: List[str]):
        """
        Initialize role checker with allowed roles.
        
        Args:
            allowed_roles: List of roles that are allowed to access the endpoint.
                          Valid roles: teaching_office, evaluation_team, 
                          evaluation_office, president_office
        """
        self.allowed_roles = allowed_roles
    
    def __call__(self, current_user: User = Depends(get_current_user)) -> User:
        """
        Check if current user has required role.
        
        Args:
            current_user: Current authenticated user
            
        Returns:
            User object if authorized
            
        Raises:
            HTTPException: 403 if user doesn't have required role
        """
        if current_user.role not in self.allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied. Required roles: {', '.join(self.allowed_roles)}. Your role: {current_user.role}"
            )
        return current_user


# Convenience functions for common role checks
def require_teaching_office(
    current_user: User = Depends(RoleChecker(["teaching_office"]))
) -> User:
    """Require teaching_office role."""
    return current_user


def require_evaluation_team(
    current_user: User = Depends(RoleChecker(["evaluation_team"]))
) -> User:
    """Require evaluation_team role."""
    return current_user


def require_evaluation_office(
    current_user: User = Depends(RoleChecker(["evaluation_office"]))
) -> User:
    """Require evaluation_office role."""
    return current_user


def require_president_office(
    current_user: User = Depends(RoleChecker(["president_office"]))
) -> User:
    """Require president_office role."""
    return current_user


def require_management_roles(
    current_user: User = Depends(RoleChecker(["evaluation_team", "evaluation_office"]))
) -> User:
    """Require evaluation_team or evaluation_office role (management roles)."""
    return current_user


def require_any_role(
    current_user: User = Depends(RoleChecker([
        "teaching_office", 
        "evaluation_team", 
        "evaluation_office", 
        "president_office"
    ]))
) -> User:
    """Allow any authenticated user with a valid role."""
    return current_user
