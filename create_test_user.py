"""
创建测试用户
"""
import sys
import os

# 设置环境变量
os.environ['MYSQL_PASSWORD'] = 'root'

sys.path.append('backend')

from app.db.base import SessionLocal
from app.models.user import User
from app.models.teaching_office import TeachingOffice
from app.core.security import get_password_hash
from uuid import uuid4

def create_test_users():
    """创建测试用户"""
    db = SessionLocal()
    
    try:
        # 1. 创建教研室
        teaching_office = db.query(TeachingOffice).filter(
            TeachingOffice.id == "test-office-001"
        ).first()
        
        if not teaching_office:
            teaching_office = TeachingOffice(
                id="test-office-001",
                name="测试教研室",
                description="用于测试的教研室"
            )
            db.add(teaching_office)
            print("✅ 创建测试教研室")
        else:
            print("ℹ️  测试教研室已存在")
        
        # 2. 创建教研室端用户
        teaching_user = db.query(User).filter(
            User.username == "test_teaching_office"
        ).first()
        
        if not teaching_user:
            teaching_user = User(
                id=str(uuid4()),
                username="test_teaching_office",
                name="测试教研室用户",
                email="teaching@test.com",
                hashed_password=get_password_hash("password123"),
                role="teaching_office",
                teaching_office_id="test-office-001"
            )
            db.add(teaching_user)
            print("✅ 创建教研室端测试用户")
            print("   用户名: test_teaching_office")
            print("   密码: password123")
        else:
            print("ℹ️  教研室端测试用户已存在")
        
        # 3. 创建考评小组用户
        eval_team_user = db.query(User).filter(
            User.username == "test_eval_team"
        ).first()
        
        if not eval_team_user:
            eval_team_user = User(
                id=str(uuid4()),
                username="test_eval_team",
                name="测试考评小组用户",
                email="evalteam@test.com",
                hashed_password=get_password_hash("password123"),
                role="evaluation_team"
            )
            db.add(eval_team_user)
            print("✅ 创建考评小组测试用户")
            print("   用户名: test_eval_team")
            print("   密码: password123")
        else:
            print("ℹ️  考评小组测试用户已存在")
        
        # 4. 创建考评办公室用户
        eval_office_user = db.query(User).filter(
            User.username == "test_eval_office"
        ).first()
        
        if not eval_office_user:
            eval_office_user = User(
                id=str(uuid4()),
                username="test_eval_office",
                name="测试考评办公室用户",
                email="evaloffice@test.com",
                hashed_password=get_password_hash("password123"),
                role="evaluation_office"
            )
            db.add(eval_office_user)
            print("✅ 创建考评办公室测试用户")
            print("   用户名: test_eval_office")
            print("   密码: password123")
        else:
            print("ℹ️  考评办公室测试用户已存在")
        
        db.commit()
        print("\n✅ 所有测试用户创建完成！")
        
        print("\n可用的测试账号：")
        print("1. 教研室端:")
        print("   用户名: test_teaching_office")
        print("   密码: password123")
        print("\n2. 考评小组:")
        print("   用户名: test_eval_team")
        print("   密码: password123")
        print("\n3. 考评办公室:")
        print("   用户名: test_eval_office")
        print("   密码: password123")
        
    except Exception as e:
        print(f"❌ 创建用户失败: {str(e)}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    print("=" * 60)
    print("创建测试用户")
    print("=" * 60)
    print()
    create_test_users()
