from sqlalchemy import create_engine, event
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import QueuePool
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)

# 创建数据库引擎
# MySQL 配置（带连接池）
engine = create_engine(
    settings.DATABASE_URL,
    # 启用连接池
    poolclass=QueuePool,
    # 连接池大小：最多保持20个连接
    pool_size=20,
    # 连接池溢出：最多额外创建10个连接
    max_overflow=10,
    # 连接回收时间：1小时后回收连接（防止连接过期）
    pool_recycle=3600,
    # 连接前ping：确保连接可用（自动重连）
    pool_pre_ping=True,
    # 连接超时：30秒
    pool_timeout=30,
    # 启用SQL日志（开发环境）
    echo=False
)
logger.info("使用 MySQL 数据库")

# 监听连接事件，记录连接池状态
@event.listens_for(engine, "connect")
def receive_connect(dbapi_conn, connection_record):
    """连接建立时的回调"""
    logger.debug("数据库连接已建立")

@event.listens_for(engine, "checkout")
def receive_checkout(dbapi_conn, connection_record, connection_proxy):
    """从连接池获取连接时的回调"""
    logger.debug("从连接池获取连接")

@event.listens_for(engine, "checkin")
def receive_checkin(dbapi_conn, connection_record):
    """连接归还到连接池时的回调"""
    logger.debug("连接归还到连接池")

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    """
    获取数据库会话
    
    使用依赖注入提供数据库会话，自动处理连接的获取和释放
    """
    db = SessionLocal()
    try:
        yield db
    except Exception as e:
        logger.error(f"数据库会话异常: {str(e)}")
        db.rollback()
        raise
    finally:
        db.close()
