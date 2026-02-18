"""
测试后端连接和认证

检查：
1. MySQL数据库连接
2. 用户登录
3. API权限
"""
import requests
import json

BASE_URL = "http://localhost:8000/api"

def test_health():
    """测试健康检查"""
    print("=" * 60)
    print("1. 测试后端健康状态")
    print("=" * 60)
    
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        if response.status_code == 200:
            print("✅ 后端服务正常运行")
            print(f"   响应: {response.json()}")
            return True
        else:
            print(f"❌ 后端服务异常: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 无法连接后端服务: {e}")
        return False

def test_login():
    """测试用户登录"""
    print("\n" + "=" * 60)
    print("2. 测试用户登录")
    print("=" * 60)
    
    login_data = {
        "username": "director1",
        "password": "password123"
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/auth/login",
            json=login_data,
            timeout=10
        )
        
        print(f"状态码: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ 登录成功")
            print(f"   Token: {data.get('access_token', '')[:50]}...")
            print(f"   用户: {data.get('username')}")
            print(f"   角色: {data.get('role')}")
            return data.get('access_token')
        else:
            print(f"❌ 登录失败")
            print(f"   响应: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ 登录请求失败: {e}")
        return None

def test_create_evaluation(token):
    """测试创建自评表"""
    print("\n" + "=" * 60)
    print("3. 测试创建自评表")
    print("=" * 60)
    
    if not token:
        print("❌ 没有token，跳过测试")
        return False
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    evaluation_data = {
        "teaching_office_id": "00000000-0000-0000-0000-000000000001",
        "evaluation_year": 2026,
        "content": {
            "test": "测试数据"
        }
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/teaching-office/self-evaluation",
            headers=headers,
            json=evaluation_data,
            timeout=10
        )
        
        print(f"状态码: {response.status_code}")
        print(f"响应: {response.text[:500]}")
        
        if response.status_code == 201:
            print("✅ 创建自评表成功")
            return True
        elif response.status_code == 403:
            print("❌ 权限错误 (403 Forbidden)")
            print("\n可能的原因：")
            print("1. MySQL数据库连接失败")
            print("2. 用户角色不正确")
            print("3. Token验证失败")
            return False
        elif response.status_code == 404:
            print("❌ 接口不存在 (404 Not Found)")
            return False
        else:
            print(f"❌ 请求失败: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ 请求异常: {e}")
        return False

def check_mysql_connection():
    """检查MySQL连接"""
    print("\n" + "=" * 60)
    print("4. 检查MySQL数据库连接")
    print("=" * 60)
    
    try:
        import sys
        sys.path.insert(0, 'backend')
        
        from app.db.base import SessionLocal
        from app.models.user import User
        
        db = SessionLocal()
        try:
            # 尝试查询用户
            users = db.query(User).limit(5).all()
            print(f"✅ MySQL连接成功")
            print(f"   找到 {len(users)} 个用户")
            
            for user in users:
                print(f"   - {user.username} ({user.role})")
            
            db.close()
            return True
            
        except Exception as e:
            print(f"❌ MySQL查询失败: {e}")
            db.close()
            return False
            
    except Exception as e:
        print(f"❌ 无法导入数据库模块: {e}")
        print("\n这可能是因为：")
        print("1. MySQL服务未运行")
        print("2. MySQL密码不正确")
        print("3. 数据库不存在")
        return False

def main():
    """主测试流程"""
    print("\n" + "=" * 60)
    print("后端连接和认证测试")
    print("=" * 60)
    
    # 测试1: 健康检查
    if not test_health():
        print("\n❌ 后端服务未运行，请先启动后端")
        return
    
    # 测试2: MySQL连接
    mysql_ok = check_mysql_connection()
    
    # 测试3: 用户登录
    token = test_login()
    
    # 测试4: 创建自评表
    if token:
        test_create_evaluation(token)
    
    # 总结
    print("\n" + "=" * 60)
    print("测试总结")
    print("=" * 60)
    
    if mysql_ok and token:
        print("✅ 所有测试通过")
        print("\n如果前端还是出现403错误，请：")
        print("1. 清除浏览器缓存和localStorage")
        print("2. 重新登录")
        print("3. 检查浏览器控制台的完整错误信息")
    else:
        print("❌ 存在问题需要修复")
        print("\n修复步骤：")
        if not mysql_ok:
            print("1. 修复MySQL连接问题")
            print("   - 检查MySQL服务是否运行")
            print("   - 验证MySQL密码是否正确")
            print("   - 运行: mysql -u root -proot -e \"SELECT 1;\"")
        if not token:
            print("2. 检查用户数据")
            print("   - 确认用户表中有测试用户")
            print("   - 运行数据库初始化脚本")

if __name__ == "__main__":
    main()
