#!/usr/bin/env python3
"""
数据库配置检测脚本
检测当前系统使用的是哪个数据库
"""

import os
import sys
from pathlib import Path

# 添加backend目录到路径
backend_dir = Path(__file__).parent / "backend"
sys.path.insert(0, str(backend_dir))

def check_database_config():
    print("=" * 60)
    print("数据库配置检测")
    print("=" * 60)
    
    # 1. 检查环境变量
    print("\n【1】环境变量检测:")
    use_sqlite = os.getenv("USE_SQLITE", "").lower()
    if use_sqlite:
        print(f"   USE_SQLITE = {use_sqlite}")
        if use_sqlite in ["true", "1", "yes"]:
            print("   ✓ 配置为使用 SQLite")
        else:
            print("   ✓ 配置为使用 MySQL/PostgreSQL")
    else:
        print("   ⚠ 未设置 USE_SQLITE 环境变量")
    
    # 2. 检查.env文件
    print("\n【2】.env 文件检测:")
    env_file = backend_dir / ".env"
    if env_file.exists():
        print(f"   ✓ 找到 .env 文件: {env_file}")
        with open(env_file, 'r', encoding='utf-8') as f:
            content = f.read()
            if "USE_SQLITE" in content:
                for line in content.split('\n'):
                    if line.strip().startswith("USE_SQLITE"):
                        print(f"   {line}")
            if "MYSQL_" in content or "POSTGRES_" in content:
                print("   包含 MySQL/PostgreSQL 配置")
    else:
        print(f"   ✗ 未找到 .env 文件: {env_file}")
    
    # 3. 检查config.py
    print("\n【3】config.py 配置:")
    try:
        from app.core.config import settings
        
        # 检查是否有DATABASE_URL属性
        if hasattr(settings, 'DATABASE_URL'):
            db_url = settings.DATABASE_URL
            print(f"   DATABASE_URL: {db_url[:50]}...")
            
            if "mysql" in db_url.lower():
                print("   ✓ 配置为 MySQL 数据库")
                print(f"   服务器: {settings.MYSQL_SERVER}")
                print(f"   端口: {settings.MYSQL_PORT}")
                print(f"   数据库: {settings.MYSQL_DB}")
                print(f"   用户: {settings.MYSQL_USER}")
            elif "postgresql" in db_url.lower():
                print("   ✓ 配置为 PostgreSQL 数据库")
            elif "sqlite" in db_url.lower():
                print("   ✓ 配置为 SQLite 数据库")
        else:
            print("   ⚠ 未找到 DATABASE_URL 配置")
            
    except Exception as e:
        print(f"   ✗ 无法加载配置: {e}")
    
    # 4. 检查SQLite数据库文件
    print("\n【4】SQLite 数据库文件:")
    sqlite_files = [
        backend_dir / "test.db",
        Path(__file__).parent / "test.db",
        Path(__file__).parent / "test_auth.db"
    ]
    
    found_sqlite = False
    for db_file in sqlite_files:
        if db_file.exists():
            size = db_file.stat().st_size
            print(f"   ✓ 找到: {db_file} ({size:,} bytes)")
            found_sqlite = True
    
    if not found_sqlite:
        print("   ✗ 未找到 SQLite 数据库文件")
    
    # 5. 检查MySQL连接
    print("\n【5】MySQL 连接测试:")
    try:
        import pymysql
        from app.core.config import settings
        
        conn = pymysql.connect(
            host=settings.MYSQL_SERVER,
            port=settings.MYSQL_PORT,
            user=settings.MYSQL_USER,
            password=settings.MYSQL_PASSWORD,
            database=settings.MYSQL_DB
        )
        print(f"   ✓ MySQL 连接成功!")
        print(f"   服务器: {settings.MYSQL_SERVER}:{settings.MYSQL_PORT}")
        print(f"   数据库: {settings.MYSQL_DB}")
        
        # 检查是否是本地数据库
        if settings.MYSQL_SERVER in ["localhost", "127.0.0.1", "::1"]:
            print(f"   ✓ 这是本地 MySQL 数据库")
        else:
            print(f"   ⚠ 这是远程 MySQL 数据库: {settings.MYSQL_SERVER}")
        
        # 查询表数量
        cursor = conn.cursor()
        cursor.execute("SHOW TABLES")
        tables = cursor.fetchall()
        print(f"   数据库表数量: {len(tables)}")
        
        conn.close()
        
    except ImportError:
        print("   ⚠ pymysql 未安装,无法测试 MySQL 连接")
    except Exception as e:
        print(f"   ✗ MySQL 连接失败: {e}")
    
    # 6. 总结
    print("\n" + "=" * 60)
    print("检测总结:")
    print("=" * 60)
    
    try:
        from app.core.config import settings
        db_url = settings.DATABASE_URL
        
        if "mysql" in db_url.lower():
            if settings.MYSQL_SERVER in ["localhost", "127.0.0.1", "::1"]:
                print("✓ 当前使用: 本地 MySQL 数据库")
                print(f"  地址: {settings.MYSQL_SERVER}:{settings.MYSQL_PORT}")
                print(f"  数据库: {settings.MYSQL_DB}")
            else:
                print("⚠ 当前使用: 远程 MySQL 数据库")
                print(f"  地址: {settings.MYSQL_SERVER}:{settings.MYSQL_PORT}")
        elif "sqlite" in db_url.lower():
            print("✓ 当前使用: SQLite 数据库 (本地文件)")
        elif "postgresql" in db_url.lower():
            print("✓ 当前使用: PostgreSQL 数据库")
    except:
        print("⚠ 无法确定数据库类型")
    
    print("=" * 60)

if __name__ == "__main__":
    check_database_config()
