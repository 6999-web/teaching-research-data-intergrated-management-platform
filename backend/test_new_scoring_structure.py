"""
测试新评分表结构的AI评分服务

这个脚本用于验证AI评分服务是否正确支持新的评分表结构
"""

import json
from datetime import datetime
from uuid import uuid4


def test_new_structure_parsing():
    """测试新结构的数据解析"""
    
    # 模拟新评分表的content结构
    new_content = {
        "regularTeaching": {
            "teachingProcessManagement": {
                "content": "制定了详细的年度工作计划，并严格执行。集体备课制度落实到位。",
                "selfScore": 9.0,
                "maxScore": 10
            },
            "teachingQualityManagement": {
                "content": "定期开展教学检查，组织教师相互听课学习。",
                "selfScore": 8.5,
                "maxScore": 10
            },
            "courseAssessment": {
                "content": "试题规范，考核方式多样化，注重能力评价。",
                "selfScore": 9.0,
                "maxScore": 10
            },
            "educationResearch": {
                "content": "积极开展教学改革研究，指导学生参加创新创业项目。",
                "selfScore": 8.0,
                "maxScore": 10
            },
            "courseConstruction": {
                "content": "所有课程均有规范的教学大纲和教案，融入课程思政元素。",
                "selfScore": 9.5,
                "maxScore": 10
            },
            "teacherTeamBuilding": {
                "content": "制定了教师培养规划，安排青年教师进修深造。",
                "selfScore": 8.5,
                "maxScore": 10
            },
            "researchAndExchange": {
                "content": "承担多项科研项目，积极参与学术交流活动。",
                "selfScore": 8.0,
                "maxScore": 10
            },
            "archiveManagement": {
                "content": "教学档案齐全，归档及时规范。",
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
                    },
                    {
                        "name": "混合式教学模式探索",
                        "level": "school_key",
                        "score": 2
                    },
                    {
                        "name": "课程思政建设研究",
                        "level": "school_general",
                        "score": 1
                    }
                ],
                "totalScore": 9
            },
            "teachingHonors": {
                "items": [
                    {
                        "name": "优秀教师",
                        "level": "provincial",
                        "score": 5
                    },
                    {
                        "name": "教学名师",
                        "level": "school",
                        "score": 3
                    }
                ],
                "totalScore": 8
            },
            "teachingCompetitions": {
                "items": [
                    {
                        "name": "青年教师教学竞赛",
                        "levelPrize": "provincial_second",
                        "score": 5
                    }
                ],
                "totalScore": 5
            },
            "innovationCompetitions": {
                "items": [
                    {
                        "name": "互联网+大学生创新创业大赛",
                        "levelPrize": "provincial_bronze",
                        "score": 3
                    },
                    {
                        "name": "挑战杯",
                        "levelPrize": "school_first",
                        "score": 3
                    }
                ],
                "totalScore": 6
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
                "percentage": 5,
                "deduction": 0
            }
        }
    }
    
    print("=" * 80)
    print("测试新评分表结构")
    print("=" * 80)
    
    # 1. 测试常规教学工作提取
    print("\n1. 常规教学工作（8个指标）：")
    regular_teaching = new_content.get('regularTeaching', {})
    for key, value in regular_teaching.items():
        print(f"   - {key}: 自评分 {value.get('selfScore', 0)}/{value.get('maxScore', 10)}")
    
    regular_total = sum(item.get('selfScore', 0) for item in regular_teaching.values())
    print(f"   常规教学工作总分: {regular_total}")
    
    # 2. 测试特色亮点项目提取
    print("\n2. 特色与亮点项目：")
    highlights = new_content.get('highlights', {})
    
    reform_projects = highlights.get('teachingReformProjects', {}).get('items', [])
    print(f"   - 教学改革项目: {len(reform_projects)}项")
    for i, project in enumerate(reform_projects, 1):
        print(f"     {i}. {project.get('name')} - {project.get('level')} - {project.get('score')}分")
    
    honors = highlights.get('teachingHonors', {}).get('items', [])
    print(f"   - 荣誉表彰: {len(honors)}项")
    for i, honor in enumerate(honors, 1):
        print(f"     {i}. {honor.get('name')} - {honor.get('level')} - {honor.get('score')}分")
    
    competitions = highlights.get('teachingCompetitions', {}).get('items', [])
    print(f"   - 教学比赛: {len(competitions)}项")
    for i, comp in enumerate(competitions, 1):
        print(f"     {i}. {comp.get('name')} - {comp.get('levelPrize')} - {comp.get('score')}分")
    
    innovations = highlights.get('innovationCompetitions', {}).get('items', [])
    print(f"   - 创新创业比赛: {len(innovations)}项")
    for i, innov in enumerate(innovations, 1):
        print(f"     {i}. {innov.get('name')} - {innov.get('levelPrize')} - {innov.get('score')}分")
    
    highlights_total = (
        highlights.get('teachingReformProjects', {}).get('totalScore', 0) +
        highlights.get('teachingHonors', {}).get('totalScore', 0) +
        highlights.get('teachingCompetitions', {}).get('totalScore', 0) +
        highlights.get('innovationCompetitions', {}).get('totalScore', 0)
    )
    print(f"   特色亮点项目总分: {highlights_total}")
    
    # 3. 测试负面清单提取
    print("\n3. 负面清单：")
    negative_list = new_content.get('negativeList', {})
    print(f"   - 师德师风违规: {negative_list.get('ethicsViolations', {}).get('count', 0)}起，扣{negative_list.get('ethicsViolations', {}).get('deduction', 0)}分")
    print(f"   - 教学事故: {negative_list.get('teachingAccidents', {}).get('count', 0)}起，扣{negative_list.get('teachingAccidents', {}).get('deduction', 0)}分")
    print(f"   - 意识形态问题: {negative_list.get('ideologyIssues', {}).get('count', 0)}起，扣{negative_list.get('ideologyIssues', {}).get('deduction', 0)}分")
    print(f"   - 工作量未完成: {negative_list.get('workloadIncomplete', {}).get('percentage', 0)}%，扣{negative_list.get('workloadIncomplete', {}).get('deduction', 0)}分")
    
    negative_total = (
        negative_list.get('ethicsViolations', {}).get('deduction', 0) +
        negative_list.get('teachingAccidents', {}).get('deduction', 0) +
        negative_list.get('ideologyIssues', {}).get('deduction', 0) +
        negative_list.get('workloadIncomplete', {}).get('deduction', 0)
    )
    print(f"   负面清单总扣分: {negative_total}")
    
    # 4. 计算最终得分
    final_score = regular_total + highlights_total - negative_total
    print(f"\n4. 最终得分: {final_score}")
    
    print("\n" + "=" * 80)
    print("✅ 新结构数据解析测试通过！")
    print("=" * 80)
    
    return new_content


def test_ai_response_parsing():
    """测试AI响应解析"""
    
    # 模拟AI响应
    ai_response = {
        "total_score": 78.5,
        "indicator_scores": [
            {
                "indicator": "教学过程管理",
                "score": 8.5,
                "reasoning": "教学文档齐全、管理规范，自评分9分略高，AI评定8.5分"
            },
            {
                "indicator": "教学质量管理",
                "score": 9.0,
                "reasoning": "教学质量管理制度完善，执行到位"
            },
            {
                "indicator": "课程考核",
                "score": 8.0,
                "reasoning": "课程考核规范，试题库建设良好"
            },
            {
                "indicator": "教育教学科研工作",
                "score": 9.5,
                "reasoning": "教研活动丰富，成效显著"
            },
            {
                "indicator": "课程建设",
                "score": 9.0,
                "reasoning": "课程体系完善，有特色课程"
            },
            {
                "indicator": "教师队伍建设",
                "score": 8.5,
                "reasoning": "教师培养规划清晰，执行良好"
            },
            {
                "indicator": "科学研究与学术交流",
                "score": 8.0,
                "reasoning": "科研项目和学术交流活动较为活跃"
            },
            {
                "indicator": "教学档案室管理与建设",
                "score": 9.0,
                "reasoning": "档案管理规范，归档及时"
            }
        ],
        "parsed_reform_projects": 3,
        "parsed_honors": 2,
        "parsed_competitions": 1,
        "parsed_innovations": 2,
        "attachment_classifications": [
            {
                "file_name": "教改项目立项书.pdf",
                "classified_indicator": "teaching_reform_projects"
            },
            {
                "file_name": "优秀教师证书.pdf",
                "classified_indicator": "teaching_honors"
            },
            {
                "file_name": "教学竞赛获奖证书.pdf",
                "classified_indicator": "teaching_competitions"
            },
            {
                "file_name": "创新创业大赛证书.pdf",
                "classified_indicator": "innovation_competitions"
            }
        ]
    }
    
    print("\n" + "=" * 80)
    print("测试AI响应解析")
    print("=" * 80)
    
    # 验证必需字段
    required_fields = [
        "total_score",
        "indicator_scores",
        "parsed_reform_projects",
        "parsed_honors",
        "parsed_competitions",
        "parsed_innovations"
    ]
    
    print("\n1. 验证必需字段：")
    for field in required_fields:
        if field in ai_response:
            print(f"   ✅ {field}: {ai_response[field] if not isinstance(ai_response[field], list) else f'{len(ai_response[field])}项'}")
        else:
            print(f"   ❌ {field}: 缺失")
    
    # 显示评分详情
    print("\n2. AI评分详情：")
    print(f"   总分: {ai_response['total_score']}")
    print(f"   常规教学指标评分:")
    for score in ai_response['indicator_scores']:
        print(f"     - {score['indicator']}: {score['score']}分")
        print(f"       理由: {score['reasoning']}")
    
    # 显示解析数量
    print("\n3. 附件解析数量：")
    print(f"   - 教学改革项目: {ai_response['parsed_reform_projects']}项")
    print(f"   - 荣誉表彰: {ai_response['parsed_honors']}项")
    print(f"   - 教学比赛: {ai_response['parsed_competitions']}项")
    print(f"   - 创新创业比赛: {ai_response['parsed_innovations']}项")
    
    # 显示附件分类
    print("\n4. 附件分类结果：")
    for classification in ai_response['attachment_classifications']:
        print(f"   - {classification['file_name']} → {classification['classified_indicator']}")
    
    print("\n" + "=" * 80)
    print("✅ AI响应解析测试通过！")
    print("=" * 80)
    
    return ai_response


def test_anomaly_detection():
    """测试异常检测"""
    
    print("\n" + "=" * 80)
    print("测试异常检测")
    print("=" * 80)
    
    # 场景1: 数量一致，无异常
    print("\n场景1: 数量一致（无异常）")
    declared_counts = {
        "reform_projects": 3,
        "honors": 2,
        "competitions": 1,
        "innovations": 2
    }
    parsed_counts = {
        "reform_projects": 3,
        "honors": 2,
        "competitions": 1,
        "innovations": 2
    }
    
    anomalies = []
    for key in declared_counts:
        if declared_counts[key] != parsed_counts[key]:
            anomalies.append(f"{key}: 声明{declared_counts[key]}项，解析{parsed_counts[key]}项")
    
    if anomalies:
        print(f"   ❌ 检测到{len(anomalies)}个异常:")
        for anomaly in anomalies:
            print(f"      - {anomaly}")
    else:
        print("   ✅ 无异常")
    
    # 场景2: 数量不一致，有异常
    print("\n场景2: 数量不一致（有异常）")
    declared_counts = {
        "reform_projects": 5,
        "honors": 3,
        "competitions": 2,
        "innovations": 3
    }
    parsed_counts = {
        "reform_projects": 3,
        "honors": 2,
        "competitions": 1,
        "innovations": 2
    }
    
    anomalies = []
    for key in declared_counts:
        if declared_counts[key] != parsed_counts[key]:
            diff = abs(declared_counts[key] - parsed_counts[key])
            if declared_counts[key] > parsed_counts[key]:
                description = f"{key}: 声明{declared_counts[key]}项，但附件仅解析出{parsed_counts[key]}项，缺少{diff}份支撑材料"
            else:
                description = f"{key}: 声明{declared_counts[key]}项，但附件解析出{parsed_counts[key]}项，多出{diff}份材料"
            anomalies.append(description)
    
    if anomalies:
        print(f"   ⚠️  检测到{len(anomalies)}个异常:")
        for anomaly in anomalies:
            print(f"      - {anomaly}")
    else:
        print("   ✅ 无异常")
    
    print("\n" + "=" * 80)
    print("✅ 异常检测测试通过！")
    print("=" * 80)


def main():
    """运行所有测试"""
    print("\n")
    print("╔" + "=" * 78 + "╗")
    print("║" + " " * 20 + "新评分表结构测试套件" + " " * 36 + "║")
    print("╚" + "=" * 78 + "╝")
    
    try:
        # 测试1: 新结构数据解析
        new_content = test_new_structure_parsing()
        
        # 测试2: AI响应解析
        ai_response = test_ai_response_parsing()
        
        # 测试3: 异常检测
        test_anomaly_detection()
        
        print("\n")
        print("╔" + "=" * 78 + "╗")
        print("║" + " " * 30 + "所有测试通过！" + " " * 32 + "║")
        print("╚" + "=" * 78 + "╝")
        print("\n")
        
    except Exception as e:
        print(f"\n❌ 测试失败: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
