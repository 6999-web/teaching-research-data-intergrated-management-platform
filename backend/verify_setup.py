#!/usr/bin/env python
"""
验证后端项目设置是否正确
"""
import sys

def check_imports():
    """检查关键模块是否可以导入"""
    print("检查 Python 模块导入...")
    
    try:
        import fastapi
        print("✓ FastAPI 已安装")
    except ImportError:
        print("✗ FastAPI 未安装")
        return False
    
    try:
        import sqlalchemy
        print("✓ SQLAlchemy 已安装")
    except ImportError:
        print("✗ SQLAlchemy 未安装")
        return False
    
    try:
        import pydantic
        print("✓ Pydantic 已安装")
    except ImportError:
        print("✗ Pydantic 未安装")
        return False
    
    try:
        import minio
        print("✓ MinIO 已安装")
    except ImportError:
        print("✗ MinIO 未安装")
        return False
    
    try:
        import alembic
        print("✓ Alembic 已安装")
    except ImportError:
        print("✗ Alembic 未安装")
        return False
    
    return True

def check_app_structure():
    """检查应用结构"""
    print("\n检查应用结构...")
    
    try:
        from app.core.config import settings
        print(f"✓ 配置模块加载成功")
        print(f"  项目名称: {settings.PROJECT_NAME}")
    except Exception as e:
        print(f"✗ 配置模块加载失败: {e}")
        return False
    
    try:
        from app.main import app
        print("✓ 主应用模块加载成功")
    except Exception as e:
        print(f"✗ 主应用模块加载失败: {e}")
        return False
    
    try:
        from app.db.base import Base, engine
        print("✓ 数据库模块加载成功")
    except Exception as e:
        print(f"✗ 数据库模块加载失败: {e}")
        return False
    
    return True

def main():
    print("=" * 50)
    print("教研室工作考评系统 - 后端设置验证")
    print("=" * 50)
    print()
    
    if not check_imports():
        print("\n❌ 依赖检查失败。请运行: pip install -r requirements.txt")
        sys.exit(1)
    
    if not check_app_structure():
        print("\n❌ 应用结构检查失败。")
        sys.exit(1)
    
    print("\n" + "=" * 50)
    print("✅ 所有检查通过! 后端设置正确。")
    print("=" * 50)
    print("\n可以启动服务:")
    print("  uvicorn app.main:app --reload")
    print()

if __name__ == "__main__":
    main()
