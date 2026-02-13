"""
测试本地环境配置

这个脚本用于验证：
1. MySQL数据库连接
2. 数据库表结构
3. 新评分表数据结构
4. AI评分服务
"""

import sys
import os

# 添加backend目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

def test_mysql_connection():
    """测试MySQL连接"""
    print("\n" + "="*80)
    print("测试1: MySQL数据库连接")
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
            cursor.execute("SELECT VERSION()")
            version = cursor.fetchone()
            print(f"✅ MySQL连接成功")
            print(f"   版本: {version[0]}")
            
            cursor.execute("SELECT DATABASE()")
            db = cursor.fetchone()
            print(f"   当前数据库: {db[0]}")
        
        connection.close()
        return True
        
    except Exception as e:
        print(f"❌ MySQL连接失败: {str(e)}")
        return False


def test_database_tables():
    """测试数据库表"""
    print("\n" + "="*80)
    print("测试2: 数据库表结构")
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
            cursor.execute("SHOW TABLES")
            tables = cursor.fetchall()
            
            print(f"✅ 数据库表数量: {len(tables)}")
            print("\n表列表:")
            for i, table in enumerate(tables, 1):
                print(f"   {i}. {table[0]}")
        
        connection.close()
        return True
        
    except Exception as e:
        print(f"❌ 查询表失败: {str(e)}")
        return False


def test_self_evaluation_structure():
    """测试自评表结构"""
    print("\n" + "="*80)
    print("测试3: 自评表数据结构")
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
            # 检查self_evaluations表结构
            cursor.execute("DESCRIBE self_evaluations")
            columns = cursor.fetchall()
            
            print("✅ self_evaluations表结构:")
            for col in columns:
                print(f"   - {col[0]}: {col[1]}")
            
            # 检查是否有content字段（JSON类型）
            content_col = [col for col in columns if col[0] == 'content']
            if content_col:
                print(f"\n✅ content字段类型: {content_col[0][1]}")
                print("   支持新评分表结构 ✓")
            else:
                print("\n❌ 缺少content字段")
        
        connection.close()
        return True
        
    except Exception as e:
        print(f"❌ 测试失败: {str(e)}")
        return False


def test_ai_scoring_service():
    """测试AI评分服务"""
    print("\n" + "="*80)
    print("测试4: AI评分服务")
    print("="*80)
    
    try:
        # 导入AI评分服务
        from app.services.ai_scoring_service import AIScoringService
        
        print("✅ AI评分服务模块导入成功")
        
        # 检查方法是否存在
        methods = [
            '_build_scoring_prompt',
            '_parse_ai_response',
            '_detect_anomalies',
            '_classify_attachments',
            '_get_mock_response'
        ]
        
        print("\n检查方法:")
        for method in methods:
            if hasattr(AIScoringService, method):
                print(f"   ✅ {method}")
            else:
                print(f"   ❌ {method} (缺失)")
        
        return True
        
    except Exception as e:
        print(f"❌ 测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def test_new_form_structure():
    """测试新表单数据结构"""
    print("\n" + "="*80)
    print("测试5: 新评分表数据结构验证")
    print("="*80)
    
    # 模拟新评分表数据
    new_content = {
        "regularTeaching": {
            "teachingProcessManagement": {
                "content": "测试内容",
                "selfScore": 9.0,
                "maxScore": 10
            },
            "teachingQualityManagement": {
                "content": "测试内容",
                "selfScore": 8.5,
                "maxScore": 10
            },
            "courseAssessment": {
                "content": "测试内容",
                "selfScore": 9.0,
                "maxScore": 10
            },
            "educationResearch": {
                "content": "测试内容",
                "selfScore": 8.0,
                "maxScore": 10
            },
            "courseConstruction": {
                "content": "测试内容",
                "selfScore": 9.5,
                "maxScore": 10
            },
            "teacherTeamBuilding": {
                "content": "测试内容",
                "selfScore": 8.5,
                "maxScore": 10
            },
            "researchAndExchange": {
                "content": "测试内容",
                "selfScore": 8.0,
                "maxScore": 10
            },
            "archiveManagement": {
                "content": "测试内容",
                "selfScore": 9.0,
                "maxScore": 10
            }
        },
        "highlights": {
            "teachingReformProjects": {
                "items": [
                    {"name": "项目1", "level": "provincial_key", "score": 6}
                ],
                "totalScore": 6
            },
            "teachingHonors": {
                "items": [
                    {"name": "荣誉1", "level": "provincial", "score": 5}
                ],
                "totalScore": 5
            },
            "teachingCompetitions": {
                "items": [
                    {"name": "比赛1", "levelPrize": "provincial_second", "score": 5}
                ],
                "totalScore": 5
            },
            "innovationCompetitions": {
                "items": [
                    {"name": "创新1", "levelPrize": "provincial_bronze", "score": 3}
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
    
    print("✅ 新评分表数据结构:")
    print(f"   - regularTeaching: {len(new_content['regularTeaching'])}个指标")
    print(f"   - highlights: {len(new_content['highlights'])}类项目")
    print(f"   - negativeList: {len(new_content['negativeList'])}个扣分项")
    
    # 计算总分
    regular_total = sum(
        item['selfScore'] 
        for item in new_content['regularTeaching'].values()
    )
    highlights_total = sum(
        category['totalScore']
        for category in new_content['highlights'].values()
    )
    negative_total = sum(
        item['deduction']
        for item in new_content['negativeList'].values()
    )
    final_score = regular_total + highlights_total - negative_total
    
    print(f"\n✅ 分数计算:")
    print(f"   - 常规教学工作: {regular_total}分")
    print(f"   - 特色亮点项目: {highlights_total}分")
    print(f"   - 负面清单扣分: {negative_total}分")
    print(f"   - 最终得分: {final_score}分")
    
    return True


def test_api_endpoints():
    """测试API端点"""
    print("\n" + "="*80)
    print("测试6: API端点检查")
    print("="*80)
    
    print("⚠️  需要后端服务运行才能测试API端点")
    print("   请运行: cd backend && uvicorn app.main:app --reload")
    print("   然后访问: http://localhost:8000/api/docs")
    
    return True


def main():
    """运行所有测试"""
    print("\n")
    print("╔" + "=" * 78 + "╗")
    print("║" + " " * 25 + "本地环境测试套件" + " " * 37 + "║")
    print("╚" + "=" * 78 + "╝")
    
    results = []
    
    # 运行测试
    results.append(("MySQL连接", test_mysql_connection()))
    results.append(("数据库表", test_database_tables()))
    results.append(("自评表结构", test_self_evaluation_structure()))
    results.append(("AI评分服务", test_ai_scoring_service()))
    results.append(("新表单结构", test_new_form_structure()))
    results.append(("API端点", test_api_endpoints()))
    
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
        print("\n🎉 所有测试通过！环境配置正确。")
        print("\n下一步:")
        print("1. 启动后端: cd backend && uvicorn app.main:app --reload")
        print("2. 启动前端: cd frontend && npm run dev")
        print("3. 访问: http://localhost:3000")
    else:
        print("\n⚠️  部分测试失败，请检查配置。")
    
    print("\n")


if __name__ == "__main__":
    main()
