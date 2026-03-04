"""
测试登录功能

测试不同角色的用户登录
"""
import requests
import json

BASE_URL = "http://localhost:8000/api"

def test_login(username, password, role=None):
    """测试登录"""
    print(f"\n{'='*60}")
    print(f"测试登录: {username}")
    print(f"{'='*60}")
    
    login_data = {
        "username": username,
        "password": password
    }
    
    if role:
        login_data["role"] = role
    
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
            print(f"   Token: {data.get('token', '')[:50]}...")
            print(f"   用户ID: {data.get('userId')}")
            print(f"   角色: {data.get('role')}")
            print(f"   教研室ID: {data.get('teachingOfficeId')}")
            return True
        else:
            print("❌ 登录失败")
            try:
                error = response.json()
                print(f"   错误: {error.get('detail', response.text)}")
            except:
                print(f"   响应: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ 请求失败: {e}")
        return False

def main():
    print("\n" + "="*60)
    print("登录功能测试")
    print("="*60)
    
    # 测试教研室用户（不需要role）
    test_login("director1", "password123")
    
    # 测试教研室用户（带role）
    test_login("director1", "password123", "teaching_office")
    
    # 测试评教小组用户
    test_login("evaluator1", "password123", "evaluation_team")
    
    # 测试办公室用户
    test_login("office1", "password123", "evaluation_office")
    
    # 测试校长办公会用户
    test_login("president1", "password123", "president_office")
    
    # 测试错误密码
    test_login("director1", "wrongpassword")
    
    # 测试不存在的用户
    test_login("nonexistent", "password123")
    
    print("\n" + "="*60)
    print("测试完成")
    print("="*60)

if __name__ == "__main__":
    main()
