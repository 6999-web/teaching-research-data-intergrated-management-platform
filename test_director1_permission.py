#!/usr/bin/env python
"""
测试 director1 用户的权限检查

这个脚本会：
1. 使用 director1 登录
2. 获取 Token
3. 尝试提交自评表
4. 验证权限检查是否正常工作
"""

import requests
import json
from datetime import datetime

# 配置
BASE_URL = "http://localhost:8000/api"
DIRECTOR1_USERNAME = "director1"
DIRECTOR1_PASSWORD = "password123"
TEACHING_OFFICE_ID = "a1b2c3d4-e5f6-4a5b-8c9d-111111111111"  # 示例 UUID

def print_section(title):
    """打印分隔符"""
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}\n")

def test_login():
    """测试登录"""
    print_section("步骤 1: 测试登录")
    
    login_data = {
        "username": DIRECTOR1_USERNAME,
        "password": DIRECTOR1_PASSWORD,
        "role": "teaching_office"
    }
    
    print(f"请求: POST {BASE_URL}/auth/login")
    print(f"数据: {json.dumps(login_data, indent=2)}")
    
    try:
        response = requests.post(f"{BASE_URL}/auth/login", json=login_data)
        print(f"\n响应状态码: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"响应数据:")
            print(f"  - Token: {data['token'][:50]}...")
            print(f"  - User ID: {data['userId']}")
            print(f"  - Role: {data['role']}")
            print(f"  - Teaching Office ID: {data.get('teachingOfficeId', 'N/A')}")
            print(f"  - Expires In: {data['expiresIn']} 秒")
            
            if data['role'] != 'teaching_office':
                print(f"\n⚠️  警告: 角色不是 'teaching_office'，而是 '{data['role']}'")
                return None
            
            print(f"\n✓ 登录成功")
            return data['token']
        else:
            print(f"错误: {response.text}")
            return None
    except Exception as e:
        print(f"异常: {e}")
        return None

def test_submit_self_evaluation(token):
    """测试提交自评表"""
    print_section("步骤 2: 测试提交自评表")
    
    if not token:
        print("❌ 没有有效的 Token，跳过此步骤")
        return False
    
    # 首先保存自评表
    print("2.1 保存自评表...")
    
    save_data = {
        "teaching_office_id": TEACHING_OFFICE_ID,
        "evaluation_year": datetime.now().year,
        "content": {
            "常规教学工作总分": 80,
            "特色与亮点项目总分": 0,
            "负面清单扣分": 0
        }
    }
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    print(f"请求: POST {BASE_URL}/teaching-office/self-evaluation")
    print(f"请求头: Authorization: Bearer {token[:50]}...")
    print(f"数据: {json.dumps(save_data, indent=2)}")
    
    try:
        response = requests.post(
            f"{BASE_URL}/teaching-office/self-evaluation",
            json=save_data,
            headers=headers
        )
        
        print(f"\n响应状态码: {response.status_code}")
        
        if response.status_code == 201:
            data = response.json()
            evaluation_id = data['evaluation_id']
            print(f"✓ 自评表保存成功")
            print(f"  - Evaluation ID: {evaluation_id}")
            print(f"  - Status: {data['status']}")
            
            # 现在尝试提交
            print(f"\n2.2 提交自评表...")
            
            submit_url = f"{BASE_URL}/teaching-office/self-evaluation/{evaluation_id}/submit"
            print(f"请求: POST {submit_url}")
            print(f"请求头: Authorization: Bearer {token[:50]}...")
            
            response = requests.post(submit_url, headers=headers)
            
            print(f"\n响应状态码: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"✓ 自评表提交成功")
                print(f"  - Evaluation ID: {data['evaluation_id']}")
                print(f"  - Status: {data['status']}")
                print(f"  - Message: {data['message']}")
                return True
            else:
                print(f"❌ 提交失败")
                print(f"错误: {response.text}")
                
                # 检查是否是权限错误
                if response.status_code == 403:
                    print(f"\n⚠️  这是一个权限错误 (403 Forbidden)")
                    print(f"可能的原因:")
                    print(f"  1. Token 中的角色不是 'teaching_office'")
                    print(f"  2. 后端权限检查配置有误")
                    print(f"  3. 用户角色在数据库中不正确")
                
                return False
        else:
            print(f"❌ 保存失败")
            print(f"错误: {response.text}")
            
            if response.status_code == 403:
                print(f"\n⚠️  这是一个权限错误 (403 Forbidden)")
                error_data = response.json()
                print(f"错误详情: {error_data.get('detail', 'N/A')}")
            
            return False
    except Exception as e:
        print(f"异常: {e}")
        return False

def test_unauthorized_access():
    """测试未授权访问"""
    print_section("步骤 3: 测试未授权访问（使用无效 Token）")
    
    invalid_token = "invalid_token_12345"
    headers = {
        "Authorization": f"Bearer {invalid_token}",
        "Content-Type": "application/json"
    }
    
    save_data = {
        "teaching_office_id": TEACHING_OFFICE_ID,
        "evaluation_year": datetime.now().year,
        "content": {}
    }
    
    print(f"请求: POST {BASE_URL}/teaching-office/self-evaluation")
    print(f"请求头: Authorization: Bearer {invalid_token}")
    
    try:
        response = requests.post(
            f"{BASE_URL}/teaching-office/self-evaluation",
            json=save_data,
            headers=headers
        )
        
        print(f"\n响应状态码: {response.status_code}")
        
        if response.status_code == 401:
            print(f"✓ 正确返回 401 Unauthorized")
            print(f"错误: {response.json().get('detail', 'N/A')}")
        else:
            print(f"❌ 预期 401，但得到 {response.status_code}")
    except Exception as e:
        print(f"异常: {e}")

def main():
    """主函数"""
    print("\n" + "="*60)
    print("  director1 权限检查测试")
    print("="*60)
    print(f"\n测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"API 地址: {BASE_URL}")
    print(f"用户名: {DIRECTOR1_USERNAME}")
    
    # 步骤 1: 测试登录
    token = test_login()
    
    if token:
        # 步骤 2: 测试提交自评表
        success = test_submit_self_evaluation(token)
        
        if success:
            print_section("✓ 所有测试通过")
            print("director1 用户可以正常提交自评表")
        else:
            print_section("❌ 提交自评表失败")
            print("请检查权限配置")
    else:
        print_section("❌ 登录失败")
        print("请检查用户名和密码")
    
    # 步骤 3: 测试未授权访问
    test_unauthorized_access()
    
    print("\n" + "="*60)
    print("  测试完成")
    print("="*60 + "\n")

if __name__ == "__main__":
    main()
