#!/usr/bin/env python3
"""
测试教研室端提交功能

这个脚本用于测试：
1. 登录功能
2. 保存自评表
3. 提交自评表
4. 触发AI评分
"""

import requests
import json
from datetime import datetime

# 配置
BASE_URL = "http://localhost:8000/api"
USERNAME = "test_teaching_office"
PASSWORD = "password123"
ROLE = "teaching_office"

def print_section(title):
    """打印分隔线"""
    print("\n" + "="*60)
    print(f"  {title}")
    print("="*60)

def test_login():
    """测试登录"""
    print_section("测试1: 登录")
    
    url = f"{BASE_URL}/auth/login"
    data = {
        "username": USERNAME,
        "password": PASSWORD,
        "role": ROLE
    }
    
    print(f"请求URL: {url}")
    print(f"请求数据: {json.dumps(data, indent=2, ensure_ascii=False)}")
    
    try:
        response = requests.post(url, json=data)
        print(f"\n响应状态码: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ 登录成功!")
            print(f"Token: {result.get('access_token', '')[:50]}...")
            print(f"用户: {result.get('user', {}).get('name')}")
            print(f"角色: {result.get('user', {}).get('role')}")
            return result.get('access_token')
        else:
            print(f"❌ 登录失败!")
            print(f"错误信息: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ 请求失败: {str(e)}")
        return None

def test_save_evaluation(token):
    """测试保存自评表"""
    print_section("测试2: 保存自评表")
    
    url = f"{BASE_URL}/teaching-office/self-evaluation"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    # 构造测试数据
    data = {
        "teaching_office_id": "teaching-office-001",
        "evaluation_year": datetime.now().year,
        "content": {
            "regularTeaching": {
                "teachingProcessManagement": {
                    "content": "制定了详细的年度教研室工作计划，并采取有效措施保证计划落实。",
                    "selfScore": 9.0,
                    "maxScore": 10
                },
                "teachingQualityManagement": {
                    "content": "定期组织教师相互听课学习，开展教学评议活动。",
                    "selfScore": 8.5,
                    "maxScore": 10
                },
                "courseAssessment": {
                    "content": "试题规范无错漏，课程考核能有效检测教学目标达成度。",
                    "selfScore": 9.0,
                    "maxScore": 10
                },
                "educationResearch": {
                    "content": "组织教师开展教学方法、教学内容、教学手段的探索与实践。",
                    "selfScore": 8.0,
                    "maxScore": 10
                },
                "courseConstruction": {
                    "content": "每门课程配备主讲教师，所有课程均有规范的教学大纲。",
                    "selfScore": 9.0,
                    "maxScore": 10
                },
                "teacherTeamBuilding": {
                    "content": "制订了教师培养规划，有计划地安排青年教师的培训。",
                    "selfScore": 8.5,
                    "maxScore": 10
                },
                "researchAndExchange": {
                    "content": "承担多项科研项目，开展有计划的社会服务活动。",
                    "selfScore": 8.0,
                    "maxScore": 10
                },
                "archiveManagement": {
                    "content": "各类教学档案齐全，教学管理档案归档及时。",
                    "selfScore": 9.0,
                    "maxScore": 10
                }
            },
            "highlights": {
                "teachingReformProjects": {
                    "items": [
                        {
                            "name": "基于OBE理念的课程改革",
                            "level": "provincial_key",
                            "score": 6
                        }
                    ],
                    "totalScore": 6
                },
                "teachingHonors": {
                    "items": [],
                    "totalScore": 0
                },
                "teachingCompetitions": {
                    "items": [],
                    "totalScore": 0
                },
                "innovationCompetitions": {
                    "items": [],
                    "totalScore": 0
                }
            },
            "negativeList": {
                "ethicsViolations": {
                    "count": 0,
                    "deduction": 0
                },
                "teachingAccidents": {
                    "count": 0,
                    "deduction": 0
                },
                "ideologyIssues": {
                    "count": 0,
                    "deduction": 0
                },
                "workloadIncomplete": {
                    "percentage": 0,
                    "deduction": 0
                }
            }
        }
    }
    
    print(f"请求URL: {url}")
    print(f"请求头: Authorization: Bearer {token[:50]}...")
    
    try:
        response = requests.post(url, json=data, headers=headers)
        print(f"\n响应状态码: {response.status_code}")
        
        if response.status_code in [200, 201]:
            result = response.json()
            print(f"✅ 保存成功!")
            print(f"自评表ID: {result.get('evaluation_id')}")
            return result.get('evaluation_id')
        else:
            print(f"❌ 保存失败!")
            print(f"错误信息: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ 请求失败: {str(e)}")
        return None

def test_submit_evaluation(token, evaluation_id):
    """测试提交自评表"""
    print_section("测试3: 提交自评表")
    
    url = f"{BASE_URL}/teaching-office/self-evaluation/{evaluation_id}/submit"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    print(f"请求URL: {url}")
    print(f"自评表ID: {evaluation_id}")
    
    try:
        response = requests.post(url, headers=headers)
        print(f"\n响应状态码: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ 提交成功!")
            print(f"状态: {result.get('status')}")
            print(f"提交时间: {result.get('submitted_at')}")
            return True
        else:
            print(f"❌ 提交失败!")
            print(f"错误信息: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ 请求失败: {str(e)}")
        return False

def test_trigger_ai_scoring(token, evaluation_id):
    """测试触发AI评分"""
    print_section("测试4: 触发AI评分")
    
    url = f"{BASE_URL}/teaching-office/trigger-ai-scoring"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    data = {
        "evaluation_id": evaluation_id
    }
    
    print(f"请求URL: {url}")
    print(f"自评表ID: {evaluation_id}")
    
    try:
        response = requests.post(url, json=data, headers=headers)
        print(f"\n响应状态码: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ AI评分触发成功!")
            print(f"AI评分ID: {result.get('ai_score_id')}")
            print(f"总分: {result.get('total_score')}")
            return True
        else:
            print(f"⚠️  AI评分触发失败（这是可选的）")
            print(f"错误信息: {response.text}")
            return False
            
    except Exception as e:
        print(f"⚠️  AI评分请求失败（这是可选的）: {str(e)}")
        return False

def main():
    """主函数"""
    print("\n" + "="*60)
    print("  教研室端提交功能测试")
    print("="*60)
    print(f"\n测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"后端地址: {BASE_URL}")
    print(f"测试账号: {USERNAME}")
    
    # 测试1: 登录
    token = test_login()
    if not token:
        print("\n❌ 测试失败: 无法登录")
        return
    
    # 测试2: 保存自评表
    evaluation_id = test_save_evaluation(token)
    if not evaluation_id:
        print("\n❌ 测试失败: 无法保存自评表")
        return
    
    # 测试3: 提交自评表
    submit_success = test_submit_evaluation(token, evaluation_id)
    if not submit_success:
        print("\n❌ 测试失败: 无法提交自评表")
        return
    
    # 测试4: 触发AI评分（可选）
    test_trigger_ai_scoring(token, evaluation_id)
    
    # 总结
    print_section("测试总结")
    print("✅ 所有核心功能测试通过!")
    print(f"\n自评表ID: {evaluation_id}")
    print("\n下一步:")
    print("1. 登录考评小组端")
    print("2. 访问手动评分页面")
    print("3. 验证能否看到刚提交的自评表")

if __name__ == "__main__":
    main()
