#!/usr/bin/env python3
"""
测试自评表提交功能
"""
import requests
import json

# 配置
BASE_URL = "http://localhost:8000/api"
USERNAME = "office1"
PASSWORD = "password123"

def test_login():
    """测试登录"""
    print("=" * 50)
    print("1. 测试登录")
    print("=" * 50)
    
    url = f"{BASE_URL}/auth/login"
    data = {
        "username": USERNAME,
        "password": PASSWORD,
        "role": "teaching_office"
    }
    
    response = requests.post(url, json=data)
    print(f"状态码: {response.status_code}")
    print(f"响应: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
    
    if response.status_code == 200:
        return response.json()["token"]
    else:
        print("登录失败！")
        return None

def test_save_evaluation(token):
    """测试保存自评表"""
    print("\n" + "=" * 50)
    print("2. 测试保存自评表")
    print("=" * 50)
    
    url = f"{BASE_URL}/teaching-office/self-evaluation"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    data = {
        "teaching_office_id": "a1b2c3d4-e5f6-4a5b-8c9d-111111111111",
        "evaluation_year": 2026,
        "content": {
            "regularTeaching": {
                "teachingProcessManagement": {
                    "content": "测试内容",
                    "selfScore": 8,
                    "maxScore": 10
                }
            }
        }
    }
    
    response = requests.post(url, json=data, headers=headers)
    print(f"状态码: {response.status_code}")
    print(f"响应: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
    
    if response.status_code == 201:
        return response.json()["evaluation_id"]
    else:
        print("保存失败！")
        return None

def test_submit_evaluation(token, evaluation_id):
    """测试提交自评表"""
    print("\n" + "=" * 50)
    print("3. 测试提交自评表")
    print("=" * 50)
    
    url = f"{BASE_URL}/teaching-office/self-evaluation/{evaluation_id}/submit"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    response = requests.post(url, headers=headers)
    print(f"状态码: {response.status_code}")
    
    if response.status_code == 200:
        print(f"响应: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
        print("\n✅ 提交成功！")
        return True
    else:
        print(f"响应: {response.text}")
        print("\n❌ 提交失败！")
        return False

def test_trigger_ai_scoring(token, evaluation_id):
    """测试触发AI评分"""
    print("\n" + "=" * 50)
    print("4. 测试触发AI评分")
    print("=" * 50)
    
    url = f"{BASE_URL}/teaching-office/trigger-ai-scoring"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    data = {
        "evaluation_id": evaluation_id
    }
    
    response = requests.post(url, json=data, headers=headers)
    print(f"状态码: {response.status_code}")
    
    if response.status_code == 200:
        print(f"响应: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
        print("\n✅ AI评分触发成功！")
        return True
    else:
        print(f"响应: {response.text}")
        print("\n⚠️  AI评分触发失败（这是正常的，可能AI服务未配置）")
        return False

def main():
    """主函数"""
    print("\n" + "=" * 50)
    print("教研室自评表提交功能测试")
    print("=" * 50)
    
    # 1. 登录
    token = test_login()
    if not token:
        print("\n❌ 测试失败：无法登录")
        return
    
    # 2. 保存自评表
    evaluation_id = test_save_evaluation(token)
    if not evaluation_id:
        print("\n❌ 测试失败：无法保存自评表")
        return
    
    # 3. 提交自评表
    submit_success = test_submit_evaluation(token, evaluation_id)
    if not submit_success:
        print("\n❌ 测试失败：无法提交自评表")
        return
    
    # 4. 触发AI评分（可选）
    test_trigger_ai_scoring(token, evaluation_id)
    
    print("\n" + "=" * 50)
    print("测试完成！")
    print("=" * 50)

if __name__ == "__main__":
    main()
