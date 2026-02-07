from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.security import verify_password, create_access_token
from app.core.deps import get_db, get_current_user
from app.models.user import User
from app.schemas.auth import LoginRequest, LoginResponse

router = APIRouter()


@router.post("/login", response_model=LoginResponse)
def login(
    login_data: LoginRequest,
    db: Session = Depends(get_db)
):
    """
    User login endpoint.
    
    Authenticates user credentials and returns a JWT token.
    """
    # Query user by username
    user = db.query(User).filter(User.username == login_data.username).first()
    
    # Verify user exists
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Verify password
    if not verify_password(login_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Verify role matches
    if user.role != login_data.role:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User role does not match requested role",
        )
    
    # Create access token
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={
            "sub": user.username,
            "user_id": str(user.id),
            "role": user.role
        },
        expires_delta=access_token_expires
    )
    
    return LoginResponse(
        token=access_token,
        userId=str(user.id),
        role=user.role,
        expiresIn=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60  # Convert to seconds
    )


@router.get("/verify")
def verify_token(current_user: User = Depends(get_current_user)):
    """
    Verify JWT token endpoint.
    
    Returns user information if token is valid.
    """
    return {
        "valid": True,
        "userId": str(current_user.id),
        "role": current_user.role
    }
