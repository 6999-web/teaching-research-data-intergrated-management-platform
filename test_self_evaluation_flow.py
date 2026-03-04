"""
测试自评表提交到手动评分的完整流程
"""
import requests
import json
from datetime import datetime

# API基础URL
BASE_URL = "http://localhost:8000/api"

# 测试用户凭证（需要先登录获取token）
# 这里使用模拟的token，实际使用时需要先调用登录接口获取
TOKEN = "your_token_here"

headers = {
    "Authorization": f"Bearer {TOKEN}",
    "Content-Type": "application/json"
}

def test_get_evaluations_for_scoring():
    """测试获取待评分的自评表列表"""
    print("\n=== 测试获取待评分列表 ===")
    
    url = f"{BASE_URL}/scoring/evaluations-for-scoring"
    params = {
        "status": "ai_scored"
    }
    
    try:
        response = requests.get(url, params=params, headers=headers)
        print(f"状态码: {response.status_code}")
        print(f"响应: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
        
        if response.status_code == 200:
            evaluations = response.json()
            print(f"\n找到 {len(evaluations)} 个待评分的自评表")
            return evaluations
        else:
            print(f"错误: {response.json()}")
            return []
    except Exception as e:
        print(f"请求失败: {str(e)}")
        return []


def test_create_self_evaluation():
    """测试创建自评表"""
    print("\n=== 测试创建自评表 ===")
    
    url = f"{BASE_URL}/teaching-office/self-evaluation"
    
    # 新评分表数据结构
    data = {
        "teaching_office_id": "test-office-001",
        "evaluation_year": 2024,
        "content": {
            "regularTeaching": {
                "teachingPlan": {"score": 10, "evidence": "教学计划完整"},
                "teachingImplementation": {"score": 10, "evidence": "教学实施良好"},
                "teachingResearch": {"score": 10, "evidence": "教研活动积极"},
                "courseConstruction": {"score": 10, "evidence": "课程建设完善"},
                "teachingMaterials": {"score": 10, "evidence": "教材建设规范"},
                "practiceTeaching": {"score": 10, "evidence": "实践教学有效"},
                "assessmentReform": {"score": 10, "evidence": "考核改革创新"},
                "teachingAchievements": {"score": 10, "evidence": "教学成果显著"}
            },
            "highlights": {
                "honors": [
                    {"name": "优秀教学团队", "level": "省级", "score": 5}
                ],
                "competitions": [
                    {"name": "教学技能大赛", "level": "国家级", "score": 10}
                ],
                "innovations": [
                    {"name": "教学方法创新", "description": "翻转课堂", "score": 3}
                ],
                "reforms": [
                    {"name": "课程改革", "description": "混合式教学", "score": 4}
                ]
            },
            "negativeList": {
                "teachingAccidents": 0,
                "studentComplaints": 0,
                "violations": 0,
                "other": 0
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


def test_submit_self_evaluation(evaluation_id):
    """测试提交自评表"""
    print(f"\n=== 测试提交自评表 (ID: {evaluation_id}) ===")
    
    url = f"{BASE_URL}/teaching-office/self-evaluation/{evaluation_id}/submit"
    
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


def test_trigger_ai_scoring(evaluation_id):
    """测试触发AI评分"""
    print(f"\n=== 测试触发AI评分 (ID: {evaluation_id}) ===")
    
    url = f"{BASE_URL}/teaching-office/trigger-ai-scoring"
    data = {
        "evaluation_id": evaluation_id
    }
    
    try:
        response = requests.post(url, json=data, headers=headers)
        print(f"状态码: {response.status_code}")
        print(f"响应: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
        
        if response.status_code == 200:
            print("\nAI评分任务已启动")
            return True
        else:
            print(f"错误: {response.json()}")
            return False
    except Exception as e:
        print(f"请求失败: {str(e)}")
        return False


def main():
    """主测试流程"""
    print("=" * 60)
    print("自评表提交到手动评分流程测试")
    print("=" * 60)
    
    # 注意：需要先登录获取有效的token
    print("\n注意：此测试需要有效的JWT token")
    print("请先调用登录接口获取token，然后更新脚本中的TOKEN变量")
    
    # 测试1：获取待评分列表（不需要认证也可以测试端点是否存在）
    test_get_evaluations_for_scoring()
    
    # 以下测试需要有效的token
    # evaluation_id = test_create_self_evaluation()
    # if evaluation_id:
    #     if test_submit_self_evaluation(evaluation_id):
    #         test_trigger_ai_scoring(evaluation_id)
    
    print("\n" + "=" * 60)
    print("测试完成")
    print("=" * 60)


if __name__ == "__main__":
    main()
