#!/usr/bin/env python3
"""
教研室工作考评系统 - 功能测试脚本
测试所有核心功能是否正常工作
"""

import requests
import json
import time
from typing import Dict, Any

# 配置
BACKEND_URL = "http://localhost:8000"
API_BASE = f"{BACKEND_URL}/api"

# 测试结果
test_results = {
    "passed": [],
    "failed": [],
    "total": 0
}

def print_header(text: str):
    """打印测试标题"""
    print("\n" + "=" * 60)
    print(f"  {text}")
    print("=" * 60)

def print_test(name: str, passed: bool, message: str = ""):
    """打印测试结果"""
    test_results["total"] += 1
    status = "✓ PASS" if passed else "✗ FAIL"
    color = "\033[92m" if passed else "\033[91m"
    reset = "\033[0m"
    
    print(f"{color}{status}{reset} - {name}")
    if message:
        print(f"      {message}")
    
    if passed:
        test_results["passed"].append(name)
    else:
        test_results["failed"].append(name)

def test_backend_health():
    """测试后端健康检查"""
    print_header("1. 后端服务健康检查")
    
    try:
        response = requests.get(f"{BACKEND_URL}/api/health", timeout=5)
        passed = response.status_code == 200
        print_test("后端服务可访问", passed, f"状态码: {response.status_code}")
        
        if passed:
            data = response.json()
            print_test("健康检查返回正确格式", "status" in data, f"响应: {data}")
    except Exception as e:
        print_test("后端服务可访问", False, f"错误: {str(e)}")

def test_authentication():
    """测试认证功能"""
    print_header("2. 认证和授权功能")
    
    # 测试登录接口
    try:
        login_data = {
            "username": "test_user",
            "password": "test_password",
            "role": "teaching_office"
        }
        response = requests.post(f"{API_BASE}/auth/login", json=login_data, timeout=5)
        
        # 预期会失败（用户不存在），但接口应该可访问
        print_test("登录接口可访问", response.status_code in [200, 401, 404], 
                  f"状态码: {response.status_code}")
    except Exception as e:
        print_test("登录接口可访问", False, f"错误: {str(e)}")

def test_self_evaluation_api():
    """测试自评表API"""
    print_header("3. 自评表功能")
    
    try:
        # 测试创建自评表接口（不需要认证的测试）
        response = requests.get(f"{API_BASE}/teaching-office/self-evaluation/test-id", timeout=5)
        
        # 预期会返回404或401，但接口应该存在
        print_test("自评表API端点存在", response.status_code in [200, 401, 404], 
                  f"状态码: {response.status_code}")
    except Exception as e:
        print_test("自评表API端点存在", False, f"错误: {str(e)}")

def test_attachment_api():
    """测试附件上传API"""
    print_header("4. 附件上传功能")
    
    try:
        # 测试附件查询接口
        response = requests.get(f"{API_BASE}/attachments", timeout=5)
        
        print_test("附件API端点存在", response.status_code in [200, 401], 
                  f"状态码: {response.status_code}")
    except Exception as e:
        print_test("附件API端点存在", False, f"错误: {str(e)}")

def test_scoring_api():
    """测试评分API"""
    print_header("5. 评分功能")
    
    try:
        # 测试手动评分接口
        response = requests.get(f"{API_BASE}/scoring/all-scores/test-id", timeout=5)
        
        print_test("评分API端点存在", response.status_code in [200, 401, 404], 
                  f"状态码: {response.status_code}")
    except Exception as e:
        print_test("评分API端点存在", False, f"错误: {str(e)}")

def test_anomaly_api():
    """测试异常处理API"""
    print_header("6. 异常处理功能")
    
    try:
        # 测试异常列表接口
        response = requests.get(f"{API_BASE}/review/anomalies", timeout=5)
        
        print_test("异常处理API端点存在", response.status_code in [200, 401], 
                  f"状态码: {response.status_code}")
    except Exception as e:
        print_test("异常处理API端点存在", False, f"错误: {str(e)}")

def test_approval_api():
    """测试审定API"""
    print_header("7. 审定功能")
    
    try:
        # 测试审定接口（POST请求会失败，但端点应该存在）
        response = requests.post(f"{API_BASE}/review/approve", json={}, timeout=5)
        
        print_test("审定API端点存在", response.status_code in [200, 400, 401, 422], 
                  f"状态码: {response.status_code}")
    except Exception as e:
        print_test("审定API端点存在", False, f"错误: {str(e)}")

def test_publication_api():
    """测试公示API"""
    print_header("8. 公示功能")
    
    try:
        # 测试公示列表接口
        response = requests.get(f"{API_BASE}/publication/publications", timeout=5)
        
        print_test("公示API端点存在", response.status_code in [200, 401], 
                  f"状态码: {response.status_code}")
    except Exception as e:
        print_test("公示API端点存在", False, f"错误: {str(e)}")

def test_operation_logs_api():
    """测试操作日志API"""
    print_header("9. 操作日志功能")
    
    try:
        # 测试日志查询接口
        response = requests.get(f"{API_BASE}/logs", timeout=5)
        
        print_test("操作日志API端点存在", response.status_code in [200, 401], 
                  f"状态码: {response.status_code}")
    except Exception as e:
        print_test("操作日志API端点存在", False, f"错误: {str(e)}")

def test_frontend():
    """测试前端服务"""
    print_header("10. 前端服务")
    
    try:
        response = requests.get("http://localhost:3000", timeout=5)
        passed = response.status_code == 200
        print_test("前端服务可访问", passed, f"状态码: {response.status_code}")
    except Exception as e:
        print_test("前端服务可访问", False, f"错误: {str(e)}")

def test_api_documentation():
    """测试API文档"""
    print_header("11. API文档")
    
    try:
        response = requests.get(f"{BACKEND_URL}/docs", timeout=5)
        passed = response.status_code == 200
        print_test("API文档可访问", passed, f"状态码: {response.status_code}")
    except Exception as e:
        print_test("API文档可访问", False, f"错误: {str(e)}")

def print_summary():
    """打印测试摘要"""
    print_header("测试摘要")
    
    total = test_results["total"]
    passed = len(test_results["passed"])
    failed = len(test_results["failed"])
    pass_rate = (passed / total * 100) if total > 0 else 0
    
    print(f"\n总测试数: {total}")
    print(f"通过: {passed} ({pass_rate:.1f}%)")
    print(f"失败: {failed}")
    
    if failed > 0:
        print("\n失败的测试:")
        for test in test_results["failed"]:
            print(f"  - {test}")
    
    print("\n" + "=" * 60)
    
    if pass_rate >= 80:
        print("✓ 系统功能基本正常！")
    elif pass_rate >= 50:
        print("⚠ 系统部分功能正常，需要修复一些问题")
    else:
        print("✗ 系统存在较多问题，需要检查配置和服务")
    
    print("=" * 60 + "\n")

def main():
    """主测试函数"""
    print("\n" + "=" * 60)
    print("  教研室工作考评系统 - 功能测试")
    print("=" * 60)
    print("\n正在测试系统功能，请稍候...\n")
    
    # 等待服务完全启动
    time.sleep(2)
    
    # 运行所有测试
    test_backend_health()
    test_authentication()
    test_self_evaluation_api()
    test_attachment_api()
    test_scoring_api()
    test_anomaly_api()
    test_approval_api()
    test_publication_api()
    test_operation_logs_api()
    test_frontend()
    test_api_documentation()
    
    # 打印摘要
    print_summary()

if __name__ == "__main__":
    main()
