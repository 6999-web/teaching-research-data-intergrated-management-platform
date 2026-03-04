"""
自定义数据库类型

为了支持MySQL，我们需要自定义UUID类型
"""

from sqlalchemy import TypeDecorator, CHAR
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
import uuid


class UUID(TypeDecorator):
    """
    跨平台UUID类型
    
    - PostgreSQL: 使用原生UUID类型
    - MySQL: 使用CHAR(36)存储UUID字符串
    - SQLite: 使用CHAR(36)存储UUID字符串
    """
    impl = CHAR
    cache_ok = True

    def __init__(self, as_uuid=True):
        """
        初始化UUID类型
        
        Args:
            as_uuid: 兼容参数，保持与postgresql UUID的接口一致
        """
        self.as_uuid = as_uuid
        super().__init__()

    def load_dialect_impl(self, dialect):
        if dialect.name == 'postgresql':
            return dialect.type_descriptor(PG_UUID(as_uuid=self.as_uuid))
        else:
            return dialect.type_descriptor(CHAR(36))

    def process_bind_param(self, value, dialect):
        if value is None:
            return value
        elif dialect.name == 'postgresql':
            return str(value)
        else:
            if isinstance(value, uuid.UUID):
                return str(value)
            else:
                return str(uuid.UUID(value))

    def process_result_value(self, value, dialect):
        if value is None:
            return value
        else:
            if isinstance(value, uuid.UUID):
                return value
            else:
                return uuid.UUID(value)
