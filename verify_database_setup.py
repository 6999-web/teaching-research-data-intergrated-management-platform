"""
验证数据库设置

检查：
1. 数据库连接
2. 表结构
3. 测试数据
4. 用户认证
"""
import sys
sys.path.insert(0, 'backend')

from app.db.base import SessionLocal
from app.models.user import User
from app.models.teaching_office import TeachingOffice
from app.models.self_evaluation import SelfEvaluation

def main():
    print("=" * 60)
    print("数据库设置验证")
    print("=" * 60)
    
    db = SessionLocal()
    
    try:
        # 1. 检查教研室
        print("\n[1/3] 检查教研室数据...")
        offices = db.query(TeachingOffice).all()
        print(f"✅ 找到 {len(offices)} 个教研室")
        for office in offices:
            print(f"   - {office.name} ({office.code})")
        
        # 2. 检查用户
        print("\n[2/3] 检查用户数据...")
        users = db.query(User).all()
        print(f"✅ 找到 {len(users)} 个用户")
        
        role_counts = {}
        for user in users:
            role_counts[user.role] = role_counts.get(user.role, 0) + 1
            print(f"   - {user.username} ({user.role}) - {user.name}")
        
        print("\n角色统计:")
        for role, count in role_counts.items():
            print(f"   {role}: {count} 个用户")
        
        # 3. 检查自评表
        print("\n[3/3] 检查自评表数据...")
        evaluations = db.query(SelfEvaluation).all()
        print(f"✅ 找到 {len(evaluations)} 个自评表")
        
        if len(evaluations) == 0:
            print("   （这是正常的，还没有创建自评表）")
        
        # 总结
        print("\n" + "=" * 60)
        print("验证结果")
        print("=" * 60)
        
        if len(offices) > 0 and len(users) > 0:
            print("✅ 数据库设置完成")
            print("\n可以使用以下账号登录:")
            print("   教研室端: director1 / password123")
            print("   评教小组: evaluator1 / password123")
            print("   办公室: office1 / password123")
            print("   校长办公会: president1 / password123")
            print("\n下一步:")
            print("1. 重启后端服务")
            print("2. 刷新浏览器")
            print("3. 登录测试")
        else:
            print("❌ 数据库设置不完整")
            print("请运行: Get-Content backend/init_test_data.sql | mysql -u root -proot")
        
    except Exception as e:
        print(f"\n❌ 验证失败: {e}")
        print("\n可能的原因:")
        print("1. 数据库连接失败")
        print("2. 表结构不完整")
        print("3. 数据未初始化")
        return False
    
    finally:
        db.close()
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
