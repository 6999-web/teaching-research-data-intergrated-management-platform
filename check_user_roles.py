#!/usr/bin/env python
"""
检查数据库中的用户角色
"""

import sys
sys.path.insert(0, 'backend')

from app.models.user import User
from app.db.base import SessionLocal

db = SessionLocal()
try:
    print("=" * 60)
    print("数据库中的所有用户")
    print("=" * 60)
    
    users = db.query(User).all()
    
    if not users:
        print("数据库中没有用户")
    else:
        for user in users:
            print(f"\n用户名: {user.username}")
            print(f"  姓名: {user.name}")
            print(f"  角色: {user.role}")
            print(f"  邮箱: {user.email}")
            print(f"  教研室ID: {user.teaching_office_id}")
    
    print("\n" + "=" * 60)
    print("检查 director1 用户")
    print("=" * 60)
    
    director1 = db.query(User).filter(User.username == 'director1').first()
    if director1:
        print(f"✓ 用户存在")
        print(f"  用户名: {director1.username}")
        print(f"  姓名: {director1.name}")
        print(f"  角色: {director1.role}")
        print(f"  邮箱: {director1.email}")
        print(f"  教研室ID: {director1.teaching_office_id}")
        
        if director1.role == 'teaching_office':
            print(f"\n✓ 角色正确: teaching_office")
        else:
            print(f"\n❌ 角色错误: {director1.role} (应该是 teaching_office)")
    else:
        print("❌ 用户不存在")
    
finally:
    db.close()
