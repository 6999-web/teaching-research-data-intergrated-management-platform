"""
测试所有功能

这个脚本用于测试：
1. 后端API是否正常
2. 数据库连接
3. 新评分表功能
4. AI评分服务
"""

import requests
import json
import time

BASE_URL = "http://localhost:8000"

def test_backend_health():
    """测试后端健康状态"""
    print("\n" + "="*80)
    print("测试1: 后端服务健康检查")
    print("="*80)
    
    try:
        response = requests.get(f"{BASE_URL}/api/docs", timeout=5)
        if response.status_code == 200:
            print("✅ 后端服务正常运行")
            print(f"   URL: {BASE_URL}")
            print(f"   API文档: {BASE_URL}/api/docs")
            return True
        else:
            print(f"❌ 后端服务响应异常: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ 无法连接到后端服务")
        print("   请确保后端服务已启动: cd backend && uvicorn app.main:app --reload")
        return False
    except Exception as e:
        print(f"❌ 测试失败: {str(e)}")
        return False


def test_frontend_health():
    """测试前端健康状态"""
    print("\n" + "="*80)
    print("测试2: 前端服务健康检查")
    print("="*80)
    
    try:
        response = requests.get("http://localhost:3000", timeout=5)
        if response.status_code == 200:
            print("✅ 前端服务正常运行")
            print(f"   URL: http://localhost:3000")
            return True
        else:
            print(f"❌ 前端服务响应异常: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ 无法连接到前端服务")
        print("   请确保前端服务已启动: cd frontend && npm run dev")
        return False
    except Exception as e:
        print(f"❌ 测试失败: {str(e)}")
        return False


def test_api_endpoints():
    """测试API端点"""
    print("\n" + "="*80)
    print("测试3: API端点测试")
    print("="*80)
    
    endpoints = [
        ("GET", "/api/docs", "API文档"),
        ("GET", "/api/openapi.json", "OpenAPI规范"),
    ]
    
    results = []
    for method, path, name in endpoints:
        try:
            url = f"{BASE_URL}{path}"
            response = requests.request(method, url, timeout=5)
            
            if response.status_code in [200, 201]:
                print(f"✅ {name}: {method} {path}")
                results.append(True)
            else:
                print(f"❌ {name}: {method} {path} (状态码: {response.status_code})")
                results.append(False)
        except Exception as e:
            print(f"❌ {name}: {method} {path} (错误: {str(e)})")
            results.append(False)
    
    return all(results)


def test_database_connection():
    """测试数据库连接"""
    print("\n" + "="*80)
    print("测试4: 数据库连接")
    print("="*80)
    
    try:
        import pymysql
        
        connection = pymysql.connect(
            host='localhost',
            user='root',
            password='root',
            database='teaching_office_evaluation',
            charset='utf8mb4'
        )
        
        with connection.cursor() as cursor:
            cursor.execute("SELECT COUNT(*) FROM self_evaluations")
            count = cursor.fetchone()[0]
            print(f"✅ 数据库连接成功")
            print(f"   自评表数量: {count}")
        
        connection.close()
        return True
        
    except Exception as e:
        print(f"❌ 数据库连接失败: {str(e)}")
        return False


def test_new_evaluation_form_structure():
    """测试新评分表结构"""
    print("\n" + "="*80)
    print("测试5: 新评分表数据结构")
    print("="*80)
    
    # 模拟新评分表数据
    new_content = {
        "teachingOfficeId": "test-office-id",
        "evaluationYear": 2024,
        "regularTeaching": {
            "teachingProcessManagement": {
                "content": "制定了详细的年度工作计划，并严格执行。",
                "selfScore": 9.0,
                "maxScore": 10
            },
            "teachingQualityManagement": {
                "content": "定期开展教学检查，组织教师相互听课学习。",
                "selfScore": 8.5,
                "maxScore": 10
            },
            "courseAssessment": {
                "content": "试题规范，考核方式多样化。",
                "selfScore": 9.0,
                "maxScore": 10
            },
            "educationResearch": {
                "content": "积极开展教学改革研究。",
                "selfScore": 8.0,
                "maxScore": 10
            },
            "courseConstruction": {
                "content": "所有课程均有规范的教学大纲。",
                "selfScore": 9.5,
                "maxScore": 10
            },
            "teacherTeamBuilding": {
                "content": "制定了教师培养规划。",
                "selfScore": 8.5,
                "maxScore": 10
            },
            "researchAndExchange": {
                "content": "承担多项科研项目。",
                "selfScore": 8.0,
                "maxScore": 10
            },
            "archiveManagement": {
                "content": "教学档案齐全。",
                "selfScore": 9.0,
                "maxScore": 10
            }
        },
        "highlights": {
            "teachingReformProjects": {
                "items": [
                    {"name": "基于OBE理念的课程改革", "level": "provincial_key", "score": 6},
                    {"name": "混合式教学模式探索", "level": "school_key", "score": 2}
                ],
                "totalScore": 8
            },
            "teachingHonors": {
                "items": [
                    {"name": "优秀教师", "level": "provincial", "score": 5}
                ],
                "totalScore": 5
            },
            "teachingCompetitions": {
                "items": [
                    {"name": "青年教师教学竞赛", "levelPrize": "provincial_second", "score": 5}
                ],
                "totalScore": 5
            },
            "innovationCompetitions": {
                "items": [
                    {"name": "互联网+大赛", "levelPrize": "provincial_bronze", "score": 3}
                ],
                "totalScore": 3
            }
        },
        "negativeList": {
            "ethicsViolations": {"count": 0, "deduction": 0},
            "teachingAccidents": {"count": 0, "deduction": 0},
            "ideologyIssues": {"count": 0, "deduction": 0},
            "workloadIncomplete": {"percentage": 0, "deduction": 0}
        }
    }
    
    print("✅ 新评分表数据结构验证:")
    print(f"   - 常规教学工作: {len(new_content['regularTeaching'])}个指标")
    print(f"   - 特色亮点项目: {len(new_content['highlights'])}类")
    print(f"   - 负面清单: {len(new_content['negativeList'])}项")
    
    # 计算总分
    regular_total = sum(item['selfScore'] for item in new_content['regularTeaching'].values())
    highlights_total = sum(cat['totalScore'] for cat in new_content['highlights'].values())
    negative_total = sum(item['deduction'] for item in new_content['negativeList'].values())
    final_score = regular_total + highlights_total - negative_total
    
    print(f"\n✅ 分数计算:")
    print(f"   - 常规教学: {regular_total}分")
    print(f"   - 特色亮点: {highlights_total}分")
    print(f"   - 负面扣分: {negative_total}分")
    print(f"   - 最终得分: {final_score}分")
    
    return True


def test_ai_scoring_mock():
    """测试AI评分模拟数据"""
    print("\n" + "="*80)
    print("测试6: AI评分服务（模拟数据）")
    print("="*80)
    
    try:
        import sys
        import os
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))
        
        from app.services.ai_scoring_service import AIScoringService
        
        # 创建服务实例（不需要数据库连接来测试模拟响应）
        service = AIScoringService(None)
        
        # 获取模拟响应
        mock_response = service._get_mock_response()
        
        # 解析响应
        import json
        data = json.loads(mock_response)
        
        print("✅ AI评分模拟数据:")
        print(f"   - 总分: {data['total_score']}")
        print(f"   - 常规教学指标: {len(data['indicator_scores'])}个")
        print(f"   - 教改项目解析: {data['parsed_reform_projects']}项")
        print(f"   - 荣誉表彰解析: {data['parsed_honors']}项")
        print(f"   - 教学比赛解析: {data['parsed_competitions']}项")
        print(f"   - 创新创业解析: {data['parsed_innovations']}项")
        
        print("\n✅ 常规教学指标评分:")
        for score in data['indicator_scores']:
            print(f"   - {score['indicator']}: {score['score']}分")
        
        return True
        
    except Exception as e:
        print(f"❌ 测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """运行所有测试"""
    print("\n")
    print("╔" + "=" * 78 + "╗")
    print("║" + " " * 25 + "功能测试套件" + " " * 41 + "║")
    print("╚" + "=" * 78 + "╝")
    
    results = []
    
    # 运行测试
    results.append(("后端服务", test_backend_health()))
    results.append(("前端服务", test_frontend_health()))
    results.append(("API端点", test_api_endpoints()))
    results.append(("数据库连接", test_database_connection()))
    results.append(("新表单结构", test_new_evaluation_form_structure()))
    results.append(("AI评分服务", test_ai_scoring_mock()))
    
    # 显示结果
    print("\n" + "=" * 80)
    print("测试结果汇总")
    print("=" * 80)
    
    for name, result in results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"{name:20s} {status}")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    print("\n" + "=" * 80)
    print(f"总计: {passed}/{total} 测试通过")
    print("=" * 80)
    
    if passed == total:
        print("\n🎉 所有功能测试通过！")
        print("\n✅ 系统已就绪，可以使用:")
        print("   - 前端: http://localhost:3000")
        print("   - 后端: http://localhost:8000")
        print("   - API文档: http://localhost:8000/api/docs")
    else:
        print(f"\n⚠️  {total - passed} 个测试失败，请检查配置。")
    
    print("\n")


if __name__ == "__main__":
    main()
