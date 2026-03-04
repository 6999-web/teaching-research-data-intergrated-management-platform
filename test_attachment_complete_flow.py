"""
完整的附件上传下载流程测试
测试：教研室端上传附件 -> 考评小组端查看附件 -> 考评小组端提交评分
"""
import requests
import json
import os
from datetime import datetime

# API基础URL
BASE_URL = "http://localhost:8000/api"

# 测试账号
DIRECTOR_CREDENTIALS = {
    "username": "director1",
    "password": "password123"
}

EVALUATOR_CREDENTIALS = {
    "username": "evaluator1", 
    "password": "password123"
}

# 颜色输出
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    END = '\033[0m'

def print_success(msg):
    print(f"{Colors.GREEN}[OK] {msg}{Colors.END}")

def print_error(msg):
    print(f"{Colors.RED}[ERROR] {msg}{Colors.END}")

def print_info(msg):
    print(f"{Colors.BLUE}[INFO] {msg}{Colors.END}")

def print_warning(msg):
    print(f"{Colors.YELLOW}[WARN] {msg}{Colors.END}")

def print_section(title):
    print(f"\n{Colors.BLUE}{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}{Colors.END}\n")

# 1. 登录获取token
def login(credentials):
    """登录并获取token"""
    print_info(f"正在登录用户: {credentials['username']}")
    
    response = requests.post(
        f"{BASE_URL}/auth/login",
        json={
            "username": credentials["username"],
            "password": credentials["password"]
        }
    )
    
    if response.status_code == 200:
        data = response.json()
        # 使用正确的字段名
        token = data.get("token")
        user_id = data.get("userId")
        role = data.get("role")
        teaching_office_id = data.get("teachingOfficeId")
        
        print_success(f"登录成功: {credentials['username']} ({role})")
        if token:
            print_info(f"Token: {token[:20]}...")
        if teaching_office_id:
            print_info(f"教研室ID: {teaching_office_id}")
        
        return {
            "token": token,
            "user_id": user_id,
            "role": role,
            "teaching_office_id": teaching_office_id
        }
    else:
        print_error(f"登录失败: {response.status_code} - {response.text}")
        return None

# 2. 创建自评表
def create_self_evaluation(token, teaching_office_id=None):
    """创建自评表"""
    print_info("正在创建自评表...")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # 如果没有提供teaching_office_id，先获取当前用户信息
    if not teaching_office_id:
        user_response = requests.get(f"{BASE_URL}/auth/me", headers=headers)
        if user_response.status_code == 200:
            user_data = user_response.json()
            teaching_office_id = user_data.get("teaching_office_id")
            print_info(f"获取到教研室ID: {teaching_office_id}")
    
    # 自评表内容
    content = {
        "teachingProcessManagement": {
            "content": "教学过程管理工作内容",
            "selfScore": 8.5
        },
        "teachingQualityManagement": {
            "content": "教学质量管理工作内容", 
            "selfScore": 9.0
        },
        "courseAssessment": {
            "content": "课程考核工作内容",
            "selfScore": 8.0
        }
    }
    
    data = {
        "teaching_office_id": teaching_office_id,
        "evaluation_year": 2026,
        "content": content
    }
    
    response = requests.post(
        f"{BASE_URL}/teaching-office/self-evaluation",
        headers=headers,
        json=data
    )
    
    if response.status_code in [200, 201]:
        result = response.json()
        # 尝试不同的ID字段名
        evaluation_id = result.get("id") or result.get("evaluation_id")
        
        # 调试输出
        if not evaluation_id:
            print_warning(f"响应数据: {json.dumps(result, ensure_ascii=False, indent=2)}")
        
        print_success(f"自评表创建成功，ID: {evaluation_id}")
        return evaluation_id
    else:
        print_error(f"创建自评表失败: {response.status_code} - {response.text}")
        return None

# 3. 上传附件
def upload_attachment(token, evaluation_id, indicator, file_path):
    """上传附件"""
    print_info(f"正在上传附件到 {indicator}...")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # 创建测试文件
    if not os.path.exists(file_path):
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(f"测试附件内容 - {indicator}\n")
            f.write(f"创建时间: {datetime.now()}\n")
    
    files = {
        'files': (os.path.basename(file_path), open(file_path, 'rb'), 'text/plain')
    }
    
    data = {
        'evaluation_id': evaluation_id,
        'indicator': indicator
    }
    
    response = requests.post(
        f"{BASE_URL}/teaching-office/attachments",
        headers=headers,
        data=data,
        files=files
    )
    
    if response.status_code in [200, 201]:
        result = response.json()
        attachment_ids = result.get("attachment_ids", [])
        print_success(f"附件上传成功，ID: {attachment_ids}")
        return attachment_ids[0] if attachment_ids else None
    else:
        print_error(f"上传附件失败: {response.status_code} - {response.text}")
        return None

# 4. 提交自评表
def submit_self_evaluation(token, evaluation_id):
    """提交自评表到考评小组"""
    print_info("正在提交自评表到考评小组...")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    response = requests.post(
        f"{BASE_URL}/teaching-office/self-evaluation/{evaluation_id}/submit",
        headers=headers
    )
    
    if response.status_code == 200:
        print_success("自评表提交成功")
        return True
    else:
        print_error(f"提交自评表失败: {response.status_code} - {response.text}")
        return False

# 5. 触发AI评分
def trigger_ai_scoring(token, evaluation_id):
    """触发AI评分"""
    print_info("正在触发AI评分...")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    response = requests.post(
        f"{BASE_URL}/teaching-office/trigger-ai-scoring",
        headers=headers,
        json={"evaluation_id": evaluation_id}
    )
    
    if response.status_code == 200:
        print_success("AI评分触发成功")
        return True
    else:
        print_warning(f"AI评分触发失败: {response.status_code} - {response.text}")
        return False

# 6. 查询附件列表（考评小组端）
def get_attachments(token, evaluation_id):
    """查询自评表的附件列表"""
    print_info(f"正在查询自评表 {evaluation_id} 的附件...")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    response = requests.get(
        f"{BASE_URL}/teaching-office/attachments/{evaluation_id}",
        headers=headers
    )
    
    if response.status_code == 200:
        attachments = response.json()
        print_success(f"查询到 {len(attachments)} 个附件")
        
        for att in attachments:
            print(f"  - {att['file_name']} ({att['indicator']}) - {att['file_size']} bytes")
        
        return attachments
    else:
        print_error(f"查询附件失败: {response.status_code} - {response.text}")
        return []

# 7. 下载附件
def download_attachment(token, attachment_id, save_path):
    """下载附件"""
    print_info(f"正在下载附件 {attachment_id}...")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    response = requests.get(
        f"{BASE_URL}/teaching-office/attachments/{attachment_id}/download",
        headers=headers
    )
    
    if response.status_code == 200:
        with open(save_path, 'wb') as f:
            f.write(response.content)
        print_success(f"附件下载成功，保存到: {save_path}")
        return True
    else:
        print_error(f"下载附件失败: {response.status_code} - {response.text}")
        return False

# 8. 提交手动评分
def submit_manual_score(token, evaluation_id):
    """提交手动评分"""
    print_info("正在提交手动评分...")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    scores = [
        {
            "indicator": "教学过程管理",
            "score": 8.5,
            "comment": "教学过程管理工作扎实，文档齐全"
        },
        {
            "indicator": "教学质量管理",
            "score": 9.0,
            "comment": "教学质量管理制度完善，执行到位"
        },
        {
            "indicator": "课程考核",
            "score": 8.0,
            "comment": "课程考核方式多样，评价合理"
        }
    ]
    
    data = {
        "evaluation_id": evaluation_id,
        "scores": scores
    }
    
    response = requests.post(
        f"{BASE_URL}/scoring/manual-score",
        headers=headers,
        json=data
    )
    
    if response.status_code in [200, 201]:
        result = response.json()
        print_success(f"手动评分提交成功，记录ID: {result.get('score_record_id')}")
        return True
    else:
        print_error(f"提交手动评分失败: {response.status_code} - {response.text}")
        return False

# 9. 查询所有评分
def get_all_scores(token, evaluation_id):
    """查询所有评分记录"""
    print_info("正在查询所有评分记录...")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    response = requests.get(
        f"{BASE_URL}/scoring/all-scores/{evaluation_id}",
        headers=headers
    )
    
    if response.status_code == 200:
        scores = response.json()
        print_success("评分记录查询成功")
        
        if scores.get("ai_score"):
            print(f"  AI评分: {scores['ai_score']['total_score']} 分")
        
        if scores.get("manual_scores"):
            print(f"  手动评分记录数: {len(scores['manual_scores'])}")
            for ms in scores['manual_scores']:
                total = sum(s['score'] for s in ms['scores'])
                print(f"    - {ms['reviewer_name']}: {total} 分")
        
        return scores
    else:
        print_error(f"查询评分记录失败: {response.status_code} - {response.text}")
        return None

# 主测试流程
def main():
    print_section("附件上传下载完整流程测试")
    
    # 测试结果统计
    results = {
        "total": 0,
        "passed": 0,
        "failed": 0
    }
    
    def test_step(name, func):
        results["total"] += 1
        print(f"\n{Colors.YELLOW}[测试 {results['total']}] {name}{Colors.END}")
        try:
            result = func()
            if result:
                results["passed"] += 1
                return result
            else:
                results["failed"] += 1
                return None
        except Exception as e:
            print_error(f"测试异常: {str(e)}")
            results["failed"] += 1
            return None
    
    # ========== 教研室端测试 ==========
    print_section("第一部分：教研室端操作")
    
    # 1. 教研室端登录
    director_auth = test_step(
        "教研室端登录",
        lambda: login(DIRECTOR_CREDENTIALS)
    )
    if not director_auth or not director_auth.get("token"):
        print_error("教研室端登录失败，测试终止")
        return
    
    director_token = director_auth["token"]
    teaching_office_id = director_auth.get("teaching_office_id")
    
    # 2. 创建自评表
    evaluation_id = test_step(
        "创建自评表",
        lambda: create_self_evaluation(director_token, teaching_office_id)
    )
    if not evaluation_id:
        print_error("创建自评表失败，测试终止")
        return
    
    # 3. 上传附件
    test_files = [
        ("teachingProcessManagement", "test_teaching_process.txt"),
        ("teachingQualityManagement", "test_teaching_quality.txt"),
        ("courseAssessment", "test_course_assessment.txt")
    ]
    
    attachment_ids = []
    for indicator, filename in test_files:
        att_id = test_step(
            f"上传附件到 {indicator}",
            lambda i=indicator, f=filename: upload_attachment(
                director_token, evaluation_id, i, f
            )
        )
        if att_id:
            attachment_ids.append(att_id)
    
    # 4. 提交自评表
    test_step(
        "提交自评表到考评小组",
        lambda: submit_self_evaluation(director_token, evaluation_id)
    )
    
    # 5. 触发AI评分（可选）
    test_step(
        "触发AI评分",
        lambda: trigger_ai_scoring(director_token, evaluation_id)
    )
    
    # ========== 考评小组端测试 ==========
    print_section("第二部分：考评小组端操作")
    
    # 6. 考评小组端登录
    evaluator_auth = test_step(
        "考评小组端登录",
        lambda: login(EVALUATOR_CREDENTIALS)
    )
    if not evaluator_auth or not evaluator_auth.get("token"):
        print_error("考评小组端登录失败，测试终止")
        return
    
    evaluator_token = evaluator_auth["token"]
    
    # 7. 查询附件列表
    attachments = test_step(
        "查询附件列表",
        lambda: get_attachments(evaluator_token, evaluation_id)
    )
    
    if attachments and len(attachments) > 0:
        print_success(f"✓ 考评小组端可以看到 {len(attachments)} 个附件")
    else:
        print_error("✗ 考评小组端无法看到附件")
    
    # 8. 下载附件
    if attachments and len(attachments) > 0:
        test_attachment = attachments[0]
        test_step(
            f"下载附件 {test_attachment['file_name']}",
            lambda: download_attachment(
                evaluator_token,
                test_attachment['id'],
                f"downloaded_{test_attachment['file_name']}"
            )
        )
    
    # 9. 提交手动评分
    test_step(
        "提交手动评分",
        lambda: submit_manual_score(evaluator_token, evaluation_id)
    )
    
    # 10. 查询所有评分
    test_step(
        "查询所有评分记录",
        lambda: get_all_scores(evaluator_token, evaluation_id)
    )
    
    # ========== 测试结果汇总 ==========
    print_section("测试结果汇总")
    
    print(f"总测试数: {results['total']}")
    print_success(f"通过: {results['passed']}")
    print_error(f"失败: {results['failed']}")
    
    success_rate = (results['passed'] / results['total'] * 100) if results['total'] > 0 else 0
    print(f"\n成功率: {success_rate:.1f}%")
    
    if results['failed'] == 0:
        print_success("\n[SUCCESS] 所有测试通过！")
    else:
        print_warning(f"\n[WARN] 有 {results['failed']} 个测试失败")
    
    # 清理测试文件
    print_info("\n清理测试文件...")
    for _, filename in test_files:
        if os.path.exists(filename):
            os.remove(filename)
            print(f"  删除: {filename}")
    
    # 清理下载的文件
    for att in attachments:
        download_path = f"downloaded_{att['file_name']}"
        if os.path.exists(download_path):
            os.remove(download_path)
            print(f"  删除: {download_path}")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print_warning("\n\n测试被用户中断")
    except Exception as e:
        print_error(f"\n\n测试过程中发生错误: {str(e)}")
        import traceback
        traceback.print_exc()
