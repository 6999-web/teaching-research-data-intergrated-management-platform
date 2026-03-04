from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
import time
import logging

from app.core.config import settings
from app.core.security import verify_password, create_access_token
from app.core.deps import get_db, get_current_user
from app.models.user import User
from app.schemas.auth import LoginRequest, LoginResponse

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/login", response_model=LoginResponse)
def login(
    login_data: LoginRequest,
    db: Session = Depends(get_db)
):
    """
    User login endpoint.
    
    Authenticates user credentials and returns a JWT token.
    """
    # Performance logging
    start_total = time.time()
    logger.info(f"LOGIN START: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(start_total))}")
    
    # Step 1: Query user by username
    start_step1 = time.time()
    logger.info("Step 1: Query user from database START")
    user = db.query(User).filter(User.username == login_data.username).first()
    step1_duration = (time.time() - start_step1) * 1000
    logger.info(f"Step 1: Query user from database END - Duration: {step1_duration:.2f}ms")
    
    # Verify user exists
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Step 2: Verify password (optimized with bcrypt cost 8)
    start_step2 = time.time()
    logger.info("Step 2: Password verification START")
    password_valid = verify_password(login_data.password, user.password_hash)
    step2_duration = (time.time() - start_step2) * 1000
    logger.info(f"Step 2: Password verification END - Duration: {step2_duration:.2f}ms (bcrypt cost 8)")
    
    if not password_valid:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Step 3: Role validation (if provided)
    start_step3 = time.time()
    logger.info("Step 3: Role validation START")
    if login_data.role and user.role != login_data.role:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"用户角色不匹配。您的角色是 {user.role}，但尝试以 {login_data.role} 身份登录",
        )
    step3_duration = (time.time() - start_step3) * 1000
    logger.info(f"Step 3: Role validation END - Duration: {step3_duration:.2f}ms")
    
    # Step 4: Create access token
    start_step4 = time.time()
    logger.info("Step 4: JWT token generation START")
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={
            "sub": user.username,
            "user_id": str(user.id),
            "role": user.role
        },
        expires_delta=access_token_expires
    )
    step4_duration = (time.time() - start_step4) * 1000
    logger.info(f"Step 4: JWT token generation END - Duration: {step4_duration:.2f}ms")
    
    # Step 5: Prepare response
    start_step5 = time.time()
    logger.info("Step 5: Response preparation START")
    teaching_office_id = None
    if user.role == "teaching_office" and user.teaching_office_id:
        teaching_office_id = str(user.teaching_office_id)
    
    response = LoginResponse(
        token=access_token,
        userId=str(user.id),
        role=user.role,
        teachingOfficeId=teaching_office_id,
        expiresIn=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
    )
    step5_duration = (time.time() - start_step5) * 1000
    logger.info(f"Step 5: Response preparation END - Duration: {step5_duration:.2f}ms")
    
    # Total duration
    total_duration = (time.time() - start_total) * 1000
    logger.info(f"LOGIN END: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())}")
    logger.info(f"LOGIN DURATION BREAKDOWN:")
    logger.info(f"  - DB Query: {step1_duration:.2f}ms")
    logger.info(f"  - Password Verify: {step2_duration:.2f}ms (bcrypt cost 8 - optimized)")
    logger.info(f"  - Role Validation: {step3_duration:.2f}ms")
    logger.info(f"  - JWT Generation: {step4_duration:.2f}ms")
    logger.info(f"  - Response Prep: {step5_duration:.2f}ms")
    logger.info(f"  - TOTAL: {total_duration:.2f}ms")
    
    return response


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
