"""
测试登录和提交自评表的完整流程
"""
import requests
import json

# API基础URL
BASE_URL = "http://localhost:8000/api"

def test_login():
    """测试登录功能"""
    print("\n=== 测试登录 ===")
    
    url = f"{BASE_URL}/auth/login"
    
    # 测试用户凭证（需要先在数据库中创建用户）
    data = {
        "username": "test_teaching_office",
        "password": "password123"
    }
    
    try:
        response = requests.post(url, data=data)
        print(f"状态码: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"登录成功！")
            print(f"Token: {result.get('access_token', '')[:50]}...")
            print(f"用户角色: {result.get('role', '')}")
            return result.get('access_token')
        else:
            print(f"登录失败: {response.json()}")
            return None
    except Exception as e:
        print(f"请求失败: {str(e)}")
        return None


def test_create_self_evaluation(token):
    """测试创建自评表"""
    print("\n=== 测试创建自评表 ===")
    
    url = f"{BASE_URL}/teaching-office/self-evaluation"
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    # 新评分表数据结构
    data = {
        "teaching_office_id": "test-office-001",
        "evaluation_year": 2024,
        "content": {
            "regularTeaching": {
                "teachingProcessManagement": {
                    "content": "教学过程管理完善",
                    "selfScore": 9.5,
                    "maxScore": 10
                },
                "teachingQualityManagement": {
                    "content": "教学质量管理良好",
                    "selfScore": 9.0,
                    "maxScore": 10
                },
                "courseAssessment": {
                    "content": "课程考核规范",
                    "selfScore": 9.0,
                    "maxScore": 10
                },
                "educationResearch": {
                    "content": "教育教学科研积极",
                    "selfScore": 8.5,
                    "maxScore": 10
                },
                "courseConstruction": {
                    "content": "课程建设完善",
                    "selfScore": 9.0,
                    "maxScore": 10
                },
                "teacherTeamBuilding": {
                    "content": "教师队伍建设良好",
                    "selfScore": 8.5,
                    "maxScore": 10
                },
                "researchAndExchange": {
                    "content": "科研与学术交流活跃",
                    "selfScore": 8.0,
                    "maxScore": 10
                },
                "archiveManagement": {
                    "content": "档案管理规范",
                    "selfScore": 9.0,
                    "maxScore": 10
                }
            },
            "highlights": {
                "teachingReformProjects": {
                    "items": [
                        {"name": "混合式教学改革", "level": "省级", "score": 5}
                    ],
                    "totalScore": 5
                },
                "teachingHonors": {
                    "items": [
                        {"name": "优秀教学团队", "level": "省级", "score": 5}
                    ],
                    "totalScore": 5
                },
                "teachingCompetitions": {
                    "items": [
                        {"name": "教学技能大赛", "levelPrize": "国家级一等奖", "score": 10}
                    ],
                    "totalScore": 10
                },
                "innovationCompetitions": {
                    "items": [
                        {"name": "创新创业大赛", "levelPrize": "省级二等奖", "score": 3}
                    ],
                    "totalScore": 3
                }
            },
            "negativeList": {
                "ethicsViolations": {"count": 0, "deduction": 0},
                "teachingAccidents": {"count": 0, "deduction": 0},
                "studentComplaints": {"count": 0, "deduction": 0},
                "otherViolations": {"count": 0, "deduction": 0}
            }
        }
    }
    
    try:
        response = requests.post(url, json=data, headers=headers)
        print(f"状态码: {response.status_code}")
        print(f"响应: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
        
        if response.status_code == 201:
            evaluation_id = response.json()["evaluation_id"]
            print(f"\n自评表创建成功，ID: {evaluation_id}")
            return evaluation_id
        else:
            print(f"错误: {response.json()}")
            return None
    except Exception as e:
        print(f"请求失败: {str(e)}")
        return None


def test_submit_self_evaluation(token, evaluation_id):
    """测试提交自评表"""
    print(f"\n=== 测试提交自评表 (ID: {evaluation_id}) ===")
    
    url = f"{BASE_URL}/teaching-office/self-evaluation/{evaluation_id}/submit"
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.post(url, headers=headers)
        print(f"状态码: {response.status_code}")
        print(f"响应: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
        
        if response.status_code == 200:
            print("\n自评表提交成功")
            return True
        else:
            print(f"错误: {response.json()}")
            return False
    except Exception as e:
        print(f"请求失败: {str(e)}")
        return False


def test_get_evaluations_for_scoring(token):
    """测试获取待评分列表"""
    print("\n=== 测试获取待评分列表 ===")
    
    url = f"{BASE_URL}/scoring/evaluations-for-scoring"
    params = {
        "status": "locked"  # 获取已锁定的自评表
    }
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.get(url, params=params, headers=headers)
        print(f"状态码: {response.status_code}")
        
        if response.status_code == 200:
            evaluations = response.json()
            print(f"找到 {len(evaluations)} 个待评分的自评表")
            for eval in evaluations:
                print(f"  - {eval['teaching_office_name']} ({eval['evaluation_year']}年) - 状态: {eval['status']}")
            return evaluations
        else:
            print(f"错误: {response.json()}")
            return []
    except Exception as e:
        print(f"请求失败: {str(e)}")
        return []


def main():
    """主测试流程"""
    print("=" * 60)
    print("自评表提交完整流程测试")
    print("=" * 60)
    
    # 步骤1：登录
    token = test_login()
    if not token:
        print("\n❌ 登录失败，无法继续测试")
        print("\n请先创建测试用户：")
        print("  用户名: test_teaching_office")
        print("  密码: password123")
        print("  角色: teaching_office")
        return
    
    # 步骤2：创建自评表
    evaluation_id = test_create_self_evaluation(token)
    if not evaluation_id:
        print("\n❌ 创建自评表失败")
        return
    
    # 步骤3：提交自评表
    if not test_submit_self_evaluation(token, evaluation_id):
        print("\n❌ 提交自评表失败")
        return
    
    # 步骤4：查看待评分列表
    test_get_evaluations_for_scoring(token)
    
    print("\n" + "=" * 60)
    print("✅ 测试完成")
    print("=" * 60)


if __name__ == "__main__":
    main()
