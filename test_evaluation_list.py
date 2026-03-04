#!/usr/bin/env python3
"""
测试考评小组端是否能接收到教研室提交的考评表
"""
import requests
import json

# 配置
BASE_URL = "http://localhost:8000/api"

def login(username, password):
    """登录获取token"""
    response = requests.post(
        f"{BASE_URL}/auth/login",
        json={"username": username, "password": password}
    )
    if response.status_code == 200:
        data = response.json()
        return data.get("access_token")
    else:
        print(f"登录失败: {response.status_code}")
        print(response.text)
        return None

def get_evaluations_for_scoring(token):
    """获取待评分的考评表列表"""
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(
        f"{BASE_URL}/scoring/evaluations-for-scoring",
        headers=headers
    )
    if response.status_code == 200:
        return response.json()
    else:
        print(f"获取列表失败: {response.status_code}")
        print(response.text)
        return None

def main():
    print("=" * 60)
    print("测试考评小组端接收教研室提交的考评表")
    print("=" * 60)
    
    # 1. 使用考评小组账号登录
    print("\n1. 登录考评小组账号...")
    # 尝试多个可能的账号
    accounts = [
        ("admin", "123"),
        ("evaluator1", "password123"),
        ("test_eval_team", "password")
    ]
    
    token = None
    for username, password in accounts:
        print(f"   尝试账号: {username}")
        token = login(username, password)
        if token:
            print(f"✓ 使用账号 {username} 登录成功")
            break
    
    if not token:
        print("❌ 所有账号登录失败")
        return
    
    # 2. 获取待评分列表
    print("\n2. 获取待评分的考评表列表...")
    evaluations = get_evaluations_for_scoring(token)
    if evaluations is None:
        print("❌ 获取列表失败")
        return
    
    print(f"✓ 成功获取 {len(evaluations)} 个待评分的考评表")
    
    # 3. 显示列表详情
    if len(evaluations) == 0:
        print("\n⚠️  没有待评分的考评表")
        print("\n可能的原因：")
        print("  1. 教研室还没有提交考评表")
        print("  2. 考评表状态不是 'submitted', 'ai_scored', 'manually_scored', 'ready_for_final'")
        print("  3. 数据库中没有数据")
    else:
        print("\n待评分的考评表列表：")
        print("-" * 60)
        for i, evaluation in enumerate(evaluations, 1):
            print(f"\n{i}. 教研室: {evaluation.get('teaching_office_name')}")
            print(f"   ID: {evaluation.get('id')}")
            print(f"   年度: {evaluation.get('evaluation_year')}")
            print(f"   状态: {evaluation.get('status')}")
            print(f"   提交时间: {evaluation.get('submitted_at')}")
    
    print("\n" + "=" * 60)
    print("测试完成")
    print("=" * 60)

if __name__ == "__main__":
    main()
