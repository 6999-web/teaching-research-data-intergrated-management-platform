"""
检查特定自评表的附件
"""
import requests
import sys

BASE_URL = "http://localhost:8000/api"

def login(username, password):
    """登录"""
    response = requests.post(
        f"{BASE_URL}/auth/login",
        json={"username": username, "password": password}
    )
    if response.status_code == 200:
        data = response.json()
        return data.get("token")
    return None

def get_evaluations(token):
    """获取待评分的自评表列表"""
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(
        f"{BASE_URL}/scoring/evaluations-for-scoring",
        headers=headers
    )
    if response.status_code == 200:
        return response.json()
    return []

def get_attachments(token, evaluation_id):
    """获取自评表的附件"""
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(
        f"{BASE_URL}/teaching-office/attachments/{evaluation_id}",
        headers=headers
    )
    print(f"\n请求URL: {BASE_URL}/teaching-office/attachments/{evaluation_id}")
    print(f"状态码: {response.status_code}")
    
    if response.status_code == 200:
        return response.json()
    else:
        print(f"错误: {response.text}")
        return []

def main():
    print("=" * 60)
    print("检查自评表附件")
    print("=" * 60)
    
    # 登录
    print("\n1. 登录考评小组账号...")
    token = login("evaluator1", "password123")
    if not token:
        print("登录失败！")
        return
    print(f"登录成功，Token: {token[:20]}...")
    
    # 获取自评表列表
    print("\n2. 获取待评分的自评表列表...")
    evaluations = get_evaluations(token)
    print(f"找到 {len(evaluations)} 个待评分的自评表")
    
    if len(evaluations) == 0:
        print("\n没有待评分的自评表！")
        return
    
    # 显示所有自评表
    print("\n自评表列表：")
    for i, ev in enumerate(evaluations):
        print(f"\n[{i+1}] 自评表ID: {ev.get('id')}")
        print(f"    教研室: {ev.get('teaching_office_name')}")
        print(f"    年度: {ev.get('evaluation_year')}")
        print(f"    状态: {ev.get('status')}")
        print(f"    提交时间: {ev.get('submitted_at', 'N/A')}")
    
    # 检查每个自评表的附件
    print("\n" + "=" * 60)
    print("3. 检查每个自评表的附件...")
    print("=" * 60)
    
    for i, ev in enumerate(evaluations):
        evaluation_id = ev.get('id')
        print(f"\n[{i+1}] 检查自评表: {ev.get('teaching_office_name')}")
        print(f"    ID: {evaluation_id}")
        
        attachments = get_attachments(token, evaluation_id)
        
        if len(attachments) > 0:
            print(f"    ✓ 找到 {len(attachments)} 个附件:")
            for att in attachments:
                print(f"      - {att['file_name']} ({att['indicator']}) - {att['file_size']} bytes")
        else:
            print(f"    ✗ 没有附件")
    
    print("\n" + "=" * 60)
    print("检查完成")
    print("=" * 60)

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\n错误: {str(e)}")
        import traceback
        traceback.print_exc()
