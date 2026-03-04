#!/usr/bin/env python3
"""
SQLite 数据库初始化脚本

快速初始化 SQLite 数据库，创建所有表和初始数据
"""

import sys
import os

# 添加项目根目录到 Python 路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.db.base import Base, engine
from app.db.init_db import init_db
from app.core.config import settings

def main():
    """初始化数据库"""
    print("=" * 60)
    print("SQLite 数据库初始化")
    print("=" * 60)
    
    # 检查数据库类型
    if not settings.DATABASE_URL.startswith("sqlite"):
        print("❌ 错误：当前配置不是 SQLite 数据库")
        print(f"   DATABASE_URL: {settings.DATABASE_URL}")
        print("\n请修改 backend/.env 文件，设置：")
        print("   DATABASE_URL=sqlite:///./teaching_office_evaluation.db")
        sys.exit(1)
    
    print(f"✓ 数据库类型：SQLite")
    print(f"✓ 数据库文件：{settings.DATABASE_URL.replace('sqlite:///', '')}")
    print()
    
    # 创建所有表
    print("正在创建数据库表...")
    try:
        Base.metadata.create_all(bind=engine)
        print("✓ 数据库表创建成功")
    except Exception as e:
        print(f"❌ 创建表失败：{e}")
        sys.exit(1)
    
    # 初始化数据
    print("\n正在初始化数据...")
    try:
        init_db()
        print("✓ 数据初始化成功")
    except Exception as e:
        print(f"❌ 数据初始化失败：{e}")
        sys.exit(1)
    
    print("\n" + "=" * 60)
    print("✓ SQLite 数据库初始化完成！")
    print("=" * 60)
    print("\n可以使用以下命令启动应用：")
    print("  cd backend")
    print("  uvicorn app.main:app --reload --host 0.0.0.0 --port 8000")
    print("\n或访问 API 文档：")
    print("  http://localhost:8000/docs")
    print()

if __name__ == "__main__":
    main()
