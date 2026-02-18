#!/usr/bin/env python
"""
教研室工作考评系统 - 自动化测试脚本

这个脚本会自动测试所有关键功能，包括：
1. 教研室端登录和表单提交
2. 附件上传
3. 考评小组端加载数据
4. 评分功能
"""

import requests
import json
import time
from datetime import datetime
from typing import Dict, Any, Tuple

# 配置
BASE_URL = "http://localhost:8000/api"
FRONTEND_URL = "http://localhost:3000"

# 测试账号
TEACHING_OFFICE_USER = {
    "username": "director1",
    "password": "password123",
    "role": "teaching_office"
}

EVALUATOR_USER = {
    "username": "evaluator1",
    "password": "password123",
    "role": "evaluation_team"
}

# 测试结果
test_results = {
    "教研室端": {},
    "考评小组端": {}
}

def print_section(title: str):
    """打印分隔符"""
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}\n")

def print_test(name: str, status: bool, message: str = ""):
    """打印测试结果"""
    icon = "✅" if status else "❌"
    print(f"{icon} {name}")
    if message:
        print(f"   {message}")

def login(user: Dict[str, str]) -> Tuple[bool, str, Dict[str, Any]]:
    """
    测试登录功能
    
    返回: (成功, Token, 用户数据)
    """
    print_section(f"测试登录 - {user['username']}")
    
    try:
        response = requests.post(
            f"{BASE_URL}/auth/login",
            json={
                "username": user["username"],
                "password": user["password"],
                "role": user["role"]
            }
        )
        
        print(f"请求: POST {BASE_URL}/auth/login")
        print(f"状态码: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            token = data.get("token")
            print_test("登录成功", True, f"Token: {token[:50]}...")
            print_test("角色验证", data.get("role") == user["role"], f"角色: {data.get('role')}")
            return True, token, data
        else:
            print_test("登录失败", False, f"状态码: {response.status_code}")
            print(f"响应: {response.text}")
            return False, "", {}
    except Exception as e:
        print_test("登录异常", False, str(e))
        return False, "", {}

def test_self_evaluation_creation(token: str, teaching_office_id: str) -> Tuple[bool, str]:
    """
    测试考评表创建
    
    返回: (成功, evaluation_id)
    """
    print_section("测试考评表创建")
    
    try:
        headers = {"Authorization": f"Bearer {token}"}
        
        # 使用当前年份 + 随机数来避免冲突
        import random
        year = 2024 + random.randint(0, 10)
        
        payload = {
            "teaching_office_id": teaching_office_id,
            "evaluation_year": year,
            "content": {
                "regularTeaching": {
                    "teachingProcessManagement": {
                        "content": "test content",
                        "selfScore": 8
                    }
                }
            }
        }
        
        response = requests.post(
            f"{BASE_URL}/teaching-office/self-evaluation",
            json=payload,
            headers=headers
        )
        
        print(f"请求: POST {BASE_URL}/teaching-office/self-evaluation")
        print(f"年份: {year}")
        print(f"状态码: {response.status_code}")
        
        if response.status_code in [200, 201]:
            data = response.json()
            evaluation_id = data.get("evaluation_id")
            print_test("考评表创建成功", True, f"ID: {evaluation_id}")
            return True, evaluation_id
        else:
            print_test("考评表创建失败", False, f"状态码: {response.status_code}")
            print(f"响应: {response.text}")
            return False, ""
    except Exception as e:
        print_test("考评表创建异常", False, str(e))
        return False, ""

def test_attachment_upload(token: str, evaluation_id: str) -> Tuple[bool, list]:
    """
    测试附件上传
    
    返回: (成功, attachment_ids)
    """
    print_section("测试附件上传")
    
    try:
        headers = {"Authorization": f"Bearer {token}"}
        
        # 创建测试文件
        files = {
            'files': ('test.txt', 'test file content'.encode('utf-8'), 'text/plain')
        }
        
        data = {
            'evaluation_id': evaluation_id,
            'indicator': '教学过程管理'
        }
        
        response = requests.post(
            f"{BASE_URL}/teaching-office/attachments",
            files=files,
            data=data,
            headers=headers,
            timeout=10
        )
        
        print(f"请求: POST {BASE_URL}/teaching-office/attachments")
        print(f"状态码: {response.status_code}")
        
        if response.status_code in [200, 201]:
            result = response.json()
            attachment_ids = result.get("attachment_ids", [])
            print_test("附件上传成功", True, f"数量: {len(attachment_ids)}")
            return True, attachment_ids
        else:
            print_test("附件上传失败", False, f"状态码: {response.status_code}")
            print(f"响应: {response.text}")
            return False, []
    except requests.exceptions.Timeout:
        print_test("附件上传超时", False, "请检查 MinIO 服务是否运行")
        return False, []
    except Exception as e:
        print_test("附件上传异常", False, str(e))
        return False, []

def test_self_evaluation_submit(token: str, evaluation_id: str) -> bool:
    """
    测试考评表提交
    """
    print_section("测试考评表提交")
    
    try:
        headers = {"Authorization": f"Bearer {token}"}
        
        response = requests.post(
            f"{BASE_URL}/teaching-office/self-evaluation/{evaluation_id}/submit",
            headers=headers
        )
        
        print(f"请求: POST {BASE_URL}/teaching-office/self-evaluation/{evaluation_id}/submit")
        print(f"状态码: {response.status_code}")
        
        if response.status_code == 200:
            print_test("考评表提交成功", True)
            return True
        else:
            print_test("考评表提交失败", False, f"状态码: {response.status_code}")
            print(f"响应: {response.text}")
            return False
    except Exception as e:
        print_test("考评表提交异常", False, str(e))
        return False

def test_load_self_evaluation(token: str, evaluation_id: str) -> bool:
    """
    测试加载考评表
    """
    print_section("测试加载考评表")
    
    try:
        headers = {"Authorization": f"Bearer {token}"}
        
        response = requests.get(
            f"{BASE_URL}/teaching-office/self-evaluation/{evaluation_id}",
            headers=headers
        )
        
        print(f"请求: GET {BASE_URL}/teaching-office/self-evaluation/{evaluation_id}")
        print(f"状态码: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print_test("加载考评表成功", True, f"状态: {data.get('status')}")
            return True
        else:
            print_test("加载考评表失败", False, f"状态码: {response.status_code}")
            print(f"响应: {response.text}")
            return False
    except Exception as e:
        print_test("加载考评表异常", False, str(e))
        return False

def test_load_attachments(token: str, evaluation_id: str) -> bool:
    """
    测试加载附件列表
    """
    print_section("测试加载附件列表")
    
    try:
        headers = {"Authorization": f"Bearer {token}"}
        
        response = requests.get(
            f"{BASE_URL}/teaching-office/attachments/{evaluation_id}",
            headers=headers
        )
        
        print(f"请求: GET {BASE_URL}/teaching-office/attachments/{evaluation_id}")
        print(f"状态码: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print_test("加载附件列表成功", True, f"数量: {len(data) if isinstance(data, list) else 0}")
            return True
        else:
            print_test("加载附件列表失败", False, f"状态码: {response.status_code}")
            print(f"响应: {response.text}")
            return False
    except Exception as e:
        print_test("加载附件列表异常", False, str(e))
        return False

def test_manual_scoring(token: str, evaluation_id: str) -> bool:
    """
    测试手动评分
    """
    print_section("测试手动评分")
    
    try:
        headers = {"Authorization": f"Bearer {token}"}
        
        payload = {
            "evaluation_id": evaluation_id,
            "scores": [
                {
                    "indicator": "教学过程管理",
                    "score": 8,
                    "comment": "test scoring"
                }
            ]
        }
        
        response = requests.post(
            f"{BASE_URL}/scoring/manual-score",
            json=payload,
            headers=headers
        )
        
        print(f"请求: POST {BASE_URL}/scoring/manual-score")
        print(f"状态码: {response.status_code}")
        
        if response.status_code in [200, 201]:
            print_test("手动评分成功", True)
            return True
        else:
            print_test("手动评分失败", False, f"状态码: {response.status_code}")
            print(f"响应: {response.text}")
            return False
    except Exception as e:
        print_test("手动评分异常", False, str(e))
        return False

def main():
    """主测试函数"""
    print("\n" + "="*60)
    print("  教研室工作考评系统 - 自动化测试")
    print("="*60)
    print(f"  开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"  API地址: {BASE_URL}")
    print("="*60)
    
    # 第一阶段：教研室端测试
    print_section("第一阶段：教研室端测试")
    
    # 登录
    success, token, user_data = login(TEACHING_OFFICE_USER)
    if not success:
        print("\n❌ 教研室端登录失败，无法继续测试")
        return
    
    teaching_office_id = user_data.get("teachingOfficeId", "a1b2c3d4-e5f6-4a5b-8c9d-111111111111")
    
    # 创建考评表
    success, evaluation_id = test_self_evaluation_creation(token, teaching_office_id)
    if not success:
        print("\n❌ 考评表创建失败，无法继续测试")
        return
    
    # 上传附件
    success, attachment_ids = test_attachment_upload(token, evaluation_id)
    
    # 提交考评表
    test_self_evaluation_submit(token, evaluation_id)
    
    # 第二阶段：考评小组端测试
    print_section("第二阶段：考评小组端测试")
    
    # 登录
    success, token, user_data = login(EVALUATOR_USER)
    if not success:
        print("\n❌ 考评小组端登录失败，无法继续测试")
        return
    
    # 加载考评表
    test_load_self_evaluation(token, evaluation_id)
    
    # 加载附件
    test_load_attachments(token, evaluation_id)
    
    # 手动评分
    test_manual_scoring(token, evaluation_id)
    
    # 总结
    print_section("测试完成")
    print(f"完成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("\n请查看上面的测试结果，确认所有功能是否正常。")

if __name__ == "__main__":
    main()
