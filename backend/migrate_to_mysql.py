"""
MySQL数据库迁移脚本

此脚本用于：
1. 创建MySQL数据库表结构
2. 可选：从SQLite迁移现有数据到MySQL

使用方法：
    python migrate_to_mysql.py --create-tables  # 仅创建表结构
    python migrate_to_mysql.py --migrate-data   # 创建表并迁移数据
"""

import sys
import argparse
from sqlalchemy import create_engine, inspect
from sqlalchemy.orm import sessionmaker

# 导入配置和所有模型
from app.core.config import settings
from app.db.base import Base
from app.models.user import User
from app.models.college import College
from app.models.teaching_office import TeachingOffice
from app.models.self_evaluation import SelfEvaluation
from app.models.ai_score import AIScore
from app.models.manual_score import ManualScore
from app.models.final_score import FinalScore
from app.models.attachment import Attachment
from app.models.anomaly import Anomaly
from app.models.publication import Publication
from app.models.approval import Approval
from app.models.operation_log import OperationLog
from app.models.sync_task import SyncTask
from app.models.insight_summary import InsightSummary
from app.models.improvement_plan import ImprovementPlan


def create_tables():
    """创建所有数据库表"""
    print("=" * 60)
    print("开始创建MySQL数据库表结构...")
    print("=" * 60)
    
    # 创建MySQL引擎
    mysql_url = settings.DATABASE_URL
    print(f"\n连接到MySQL数据库: {settings.MYSQL_SERVER}:{settings.MYSQL_PORT}/{settings.MYSQL_DB}")
    
    engine = create_engine(
        mysql_url,
        pool_pre_ping=True,
        pool_recycle=3600,
        echo=True  # 显示SQL语句
    )
    
    try:
        # 创建所有表
        print("\n创建表结构...")
        Base.metadata.create_all(bind=engine)
        
        # 验证表是否创建成功
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        
        print("\n" + "=" * 60)
        print(f"✅ 成功创建 {len(tables)} 个表:")
        print("=" * 60)
        for table in sorted(tables):
            print(f"  ✓ {table}")
        
        print("\n" + "=" * 60)
        print("数据库表结构创建完成！")
        print("=" * 60)
        
        return True
        
    except Exception as e:
        print(f"\n❌ 创建表结构失败: {str(e)}")
        return False
    finally:
        engine.dispose()


def migrate_data():
    """从SQLite迁移数据到MySQL"""
    print("\n" + "=" * 60)
    print("开始数据迁移...")
    print("=" * 60)
    
    # SQLite连接
    sqlite_db_path = "teaching_office_evaluation.db"
    sqlite_url = f"sqlite:///{sqlite_db_path}"
    
    try:
        sqlite_engine = create_engine(sqlite_url)
        SQLiteSession = sessionmaker(bind=sqlite_engine)
        sqlite_session = SQLiteSession()
        
        # MySQL连接
        mysql_engine = create_engine(settings.DATABASE_URL)
        MySQLSession = sessionmaker(bind=mysql_engine)
        mysql_session = MySQLSession()
        
        # 定义迁移顺序（考虑外键依赖）
        migration_order = [
            (User, "users"),
            (College, "colleges"),
            (TeachingOffice, "teaching_offices"),
            (SelfEvaluation, "self_evaluations"),
            (AIScore, "ai_scores"),
            (ManualScore, "manual_scores"),
            (FinalScore, "final_scores"),
            (Attachment, "attachments"),
            (Anomaly, "anomalies"),
            (Publication, "publications"),
            (Approval, "approvals"),
            (OperationLog, "operation_logs"),
            (SyncTask, "sync_tasks"),
            (InsightSummary, "insight_summaries"),
            (ImprovementPlan, "improvement_plans"),
        ]
        
        total_migrated = 0
        
        for model, table_name in migration_order:
            try:
                # 从SQLite读取数据
                records = sqlite_session.query(model).all()
                
                if records:
                    print(f"\n迁移表 {table_name}: {len(records)} 条记录")
                    
                    # 批量插入到MySQL
                    for record in records:
                        # 创建新对象（避免session冲突）
                        record_dict = {
                            c.name: getattr(record, c.name)
                            for c in record.__table__.columns
                        }
                        new_record = model(**record_dict)
                        mysql_session.add(new_record)
                    
                    mysql_session.commit()
                    total_migrated += len(records)
                    print(f"  ✓ 成功迁移 {len(records)} 条记录")
                else:
                    print(f"\n表 {table_name}: 无数据")
                    
            except Exception as e:
                print(f"  ❌ 迁移表 {table_name} 失败: {str(e)}")
                mysql_session.rollback()
                continue
        
        print("\n" + "=" * 60)
        print(f"✅ 数据迁移完成！共迁移 {total_migrated} 条记录")
        print("=" * 60)
        
        sqlite_session.close()
        mysql_session.close()
        
        return True
        
    except Exception as e:
        print(f"\n❌ 数据迁移失败: {str(e)}")
        return False
    finally:
        sqlite_engine.dispose()
        mysql_engine.dispose()


def verify_migration():
    """验证迁移结果"""
    print("\n" + "=" * 60)
    print("验证数据库...")
    print("=" * 60)
    
    engine = create_engine(settings.DATABASE_URL)
    Session = sessionmaker(bind=engine)
    session = Session()
    
    try:
        # 检查每个表的记录数
        models = [
            (User, "users"),
            (College, "colleges"),
            (TeachingOffice, "teaching_offices"),
            (SelfEvaluation, "self_evaluations"),
            (AIScore, "ai_scores"),
            (ManualScore, "manual_scores"),
            (FinalScore, "final_scores"),
            (Attachment, "attachments"),
            (Anomaly, "anomalies"),
            (Publication, "publications"),
            (Approval, "approvals"),
            (OperationLog, "operation_logs"),
            (SyncTask, "sync_tasks"),
            (InsightSummary, "insight_summaries"),
            (ImprovementPlan, "improvement_plans"),
        ]
        
        print("\n表记录统计:")
        for model, table_name in models:
            count = session.query(model).count()
            print(f"  {table_name:30s}: {count:6d} 条记录")
        
        print("\n" + "=" * 60)
        print("✅ 验证完成！")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ 验证失败: {str(e)}")
    finally:
        session.close()
        engine.dispose()


def main():
    parser = argparse.ArgumentParser(description="MySQL数据库迁移工具")
    parser.add_argument(
        "--create-tables",
        action="store_true",
        help="仅创建表结构"
    )
    parser.add_argument(
        "--migrate-data",
        action="store_true",
        help="创建表并迁移数据"
    )
    parser.add_argument(
        "--verify",
        action="store_true",
        help="验证迁移结果"
    )
    
    args = parser.parse_args()
    
    # 如果没有指定参数，默认只创建表
    if not any([args.create_tables, args.migrate_data, args.verify]):
        args.create_tables = True
    
    print("\n" + "=" * 60)
    print("MySQL数据库迁移工具")
    print("=" * 60)
    print(f"\n数据库配置:")
    print(f"  服务器: {settings.MYSQL_SERVER}:{settings.MYSQL_PORT}")
    print(f"  数据库: {settings.MYSQL_DB}")
    print(f"  用户名: {settings.MYSQL_USER}")
    
    success = True
    
    if args.create_tables or args.migrate_data:
        success = create_tables()
        
        if not success:
            print("\n❌ 表结构创建失败，终止操作")
            sys.exit(1)
    
    if args.migrate_data and success:
        success = migrate_data()
        
        if not success:
            print("\n⚠️  数据迁移失败，但表结构已创建")
    
    if args.verify:
        verify_migration()
    
    if success:
        print("\n✅ 所有操作完成！")
        print("\n下一步:")
        print("  1. 启动后端服务: cd backend && python -m uvicorn app.main:app --reload")
        print("  2. 访问API文档: http://localhost:8000/docs")
    else:
        print("\n⚠️  部分操作失败，请检查错误信息")
        sys.exit(1)


if __name__ == "__main__":
    main()
