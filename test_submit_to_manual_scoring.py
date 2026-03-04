#!/usr/bin/env python3
"""
测试提交表单到手动评分的完整流程
"""

import requests
import json
from datetime import datetime

BASE_URL = "http://localhost:8000/api"

def test_complete_flow():
    """测试完整流程：登录 -> 提交表单 -> 查看手动评分列表"""
    
    print("=" * 60)
    print("测试：提交表单到手动评分完整流程")
    print("=" * 60)
    
    # Step 1: 教研室端登录
    print("\n[步骤1] 教研室端用户登录...")
    login_data = {
        "username": "test_teaching_office",
        "password": "password123",
        "role": "teaching_office"
    }
    
    response = requests.post(
        f"{BASE_URL}/auth/login",
        json=login_data
    )
    
    if response.status_code != 200:
        print(f"❌ 登录失败: {response.status_code}")
        print(f"   错误信息: {response.text}")
        return False
    
    teaching_token = response.json()["access_token"]
    print(f"✅ 教研室端登录成功")
    print(f"   Token: {teaching_token[:20]}...")
    
    # Step 2: 提交自评表
    print("\n[步骤2] 提交自评表...")
    
    # 2.1 保存自评表
    evaluation_data = {
        "teaching_office_id": "test-office-001",
        "evaluation_year": 2025,
        "content": {
            "regularTeaching": {
                "teachingProcessManagement": {
                    "content": "制定了完善的年度工作计划，各项教学环节运转正常。",
                    "selfScore": 9.0,
                    "maxScore": 10
                },
                "teachingQualityManagement": {
                    "content": "定期组织教师听课学习，开展教学评议活动。",
                    "selfScore": 8.5,
                    "maxScore": 10
                },
                "courseAssessment": {
                    "content": "试题规范，考核有效检测教学目标达成度。",
                    "selfScore": 9.0,
                    "maxScore": 10
                },
                "educationResearch": {
                    "content": "组织教师开展教学方法探索，指导学生创新创业项目。",
                    "selfScore": 8.0,
                    "maxScore": 10
                },
                "courseConstruction": {
                    "content": "所有课程配备主讲教师，教学大纲规范完整。",
                    "selfScore": 9.0,
                    "maxScore": 10
                },
                "teacherTeamBuilding": {
                    "content": "制订教师培养规划，安排青年教师进修深造。",
                    "selfScore": 8.5,
                    "maxScore": 10
                },
                "researchAndExchange": {
                    "content": "承担科研项目，参与学术交流活动。",
                    "selfScore": 8.0,
                    "maxScore": 10
                },
                "archiveManagement": {
                    "content": "教学档案齐全，归档及时。",
                    "selfScore": 9.0,
                    "maxScore": 10
                }
            },
            "highlights": {
                "teachingReformProjects": {
                    "items": [
                        {"name": "教学改革项目A", "level": "provincial_key", "score": 6}
                    ],
                    "totalScore": 6
                },
                "teachingHonors": {
                    "items": [
                        {"name": "优秀教学团队", "level": "provincial", "score": 5}
                    ],
                    "totalScore": 5
                },
                "teachingCompetitions": {
                    "items": [
                        {"name": "教学比赛", "levelPrize": "provincial_first", "score": 6}
                    ],
                    "totalScore": 6
                },
                "innovationCompetitions": {
                    "items": [
                        {"name": "创新创业大赛", "levelPrize": "provincial_gold", "score": 6}
                    ],
                    "totalScore": 6
                }
            },
            "negativeList": {
                "ethicsViolations": {"count": 0, "deduction": 0},
                "teachingAccidents": {"count": 0, "deduction": 0},
                "ideologyIssues": {"count": 0, "deduction": 0},
                "workloadIncomplete": {"percentage": 0, "deduction": 0}
            }
        }
    }
    
    headers = {"Authorization": f"Bearer {teaching_token}"}
    
    response = requests.post(
        f"{BASE_URL}/teaching-office/self-evaluation",
        json=evaluation_data,
        headers=headers
    )
    
    if response.status_code != 201:
        print(f"❌ 保存自评表失败: {response.status_code}")
        print(f"   错误信息: {response.text}")
        return False
    
    evaluation_id = response.json()["evaluation_id"]
    print(f"✅ 自评表保存成功")
    print(f"   评估ID: {evaluation_id}")
    
    # 2.2 提交并锁定
    print("\n[步骤3] 提交并锁定自评表...")
    response = requests.post(
        f"{BASE_URL}/teaching-office/self-evaluation/{evaluation_id}/submit",
        headers=headers
    )
    
    if response.status_code != 200:
        print(f"❌ 提交失败: {response.status_code}")
        print(f"   错误信息: {response.text}")
        return False
    
    result = response.json()
    print(f"✅ 自评表提交成功")
    print(f"   状态: {result['status']}")
    print(f"   提交时间: {result['submitted_at']}")
    
    # 2.3 触发AI评分（可选）
    print("\n[步骤4] 触发AI评分（可选）...")
    response = requests.post(
        f"{BASE_URL}/teaching-office/trigger-ai-scoring",
        json={"evaluation_id": evaluation_id},
        headers=headers
    )
    
    if response.status_code == 200:
        print(f"✅ AI评分已触发")
    else:
        print(f"⚠️  AI评分触发失败（不影响手动评分）: {response.status_code}")
    
    # Step 3: 考评小组端登录
    print("\n[步骤5] 考评小组用户登录...")
    login_data = {
        "username": "test_eval_team",
        "password": "password123",
        "role": "evaluation_team"
    }
    
    response = requests.post(
        f"{BASE_URL}/auth/login",
        json=login_data
    )
    
    if response.status_code != 200:
        print(f"❌ 考评小组登录失败: {response.status_code}")
        print(f"   错误信息: {response.text}")
        return False
    
    eval_token = response.json()["access_token"]
    print(f"✅ 考评小组登录成功")
    
    # Step 4: 查看手动评分列表
    print("\n[步骤6] 查看手动评分列表...")
    headers = {"Authorization": f"Bearer {eval_token}"}
    
    response = requests.get(
        f"{BASE_URL}/scoring/evaluations-for-scoring",
        headers=headers
    )
    
    if response.status_code != 200:
        print(f"❌ 获取待评分列表失败: {response.status_code}")
        print(f"   错误信息: {response.text}")
        return False
    
    evaluations = response.json()
    print(f"✅ 成功获取待评分列表")
    print(f"   共有 {len(evaluations)} 个待评分的自评表")
    
    # 查找刚提交的自评表
    found = False
    for eval_item in evaluations:
        if eval_item["id"] == evaluation_id:
            found = True
            print(f"\n✅ 找到刚提交的自评表！")
            print(f"   教研室: {eval_item['teaching_office_name']}")
            print(f"   年度: {eval_item['evaluation_year']}")
            print(f"   状态: {eval_item['status']}")
            print(f"   提交时间: {eval_item['submitted_at']}")
            break
    
    if not found:
        print(f"\n❌ 未找到刚提交的自评表（ID: {evaluation_id}）")
        print(f"   列表中的自评表:")
        for eval_item in evaluations:
            print(f"   - {eval_item['teaching_office_name']} ({eval_item['status']})")
        return False
    
    print("\n" + "=" * 60)
    print("✅ 测试通过！提交表单到手动评分功能正常工作")
    print("=" * 60)
    return True

if __name__ == "__main__":
    try:
        success = test_complete_flow()
        exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ 测试过程中发生错误: {str(e)}")
        import traceback
        traceback.print_exc()
        exit(1)
