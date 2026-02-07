from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api.v1.api import api_router
from app.core.logging_middleware import OperationLoggingMiddleware
from app.core.security import decode_access_token
from app.models.user import User
from app.db.base import SessionLocal
import logging

logger = logging.getLogger(__name__)

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def attach_user_to_request(request: Request, call_next):
    """
    中间件：将当前用户附加到请求状态
    
    这样操作日志中间件就可以访问用户信息
    """
    # 尝试从Authorization header中提取用户信息
    auth_header = request.headers.get("Authorization")
    if auth_header and auth_header.startswith("Bearer "):
        token = auth_header.replace("Bearer ", "")
        try:
            payload = decode_access_token(token)
            if payload:
                username = payload.get("sub")
                user_id = payload.get("user_id")
                
                # 从数据库获取用户信息
                db = SessionLocal()
                try:
                    user = db.query(User).filter(User.username == username).first()
                    if user:
                        request.state.user = user
                except Exception as db_error:
                    logger.debug(f"Database error while attaching user: {str(db_error)}")
                finally:
                    db.close()
        except Exception as e:
            logger.debug(f"Failed to attach user to request: {str(e)}")
    
    response = await call_next(request)
    return response


# 添加操作日志中间件
app.add_middleware(OperationLoggingMiddleware)

app.include_router(api_router, prefix=settings.API_V1_STR)

@app.get("/")
def root():
    return {"message": "教研室工作考评系统 API"}
