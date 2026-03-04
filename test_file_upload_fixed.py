"""
测试文件上传功能（修复后）

验证附件上传API是否正常工作
"""
import requests
import io

BASE_URL = "http://localhost:8000/api"

def test_file_upload():
    """测试文件上传"""
    print("=" * 60)
    print("文件上传功能测试")
    print("=" * 60)
    
    # 步骤1: 登录获取token
    print("\n[1/3] 登录系统...")
    login_data = {
        "username": "director1",
        "password": "password123"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/auth/login", json=login_data)
        response.raise_for_status()
        token = response.json()["token"]
        print("✅ 登录成功")
    except Exception as e:
        print(f"❌ 登录失败: {e}")
        return False
    
    # 步骤2: 创建测试自评表
    print("\n[2/3] 创建测试自评表...")
    eval_data = {
        "teaching_office_id": "00000000-0000-0000-0000-000000000001",
        "evaluation_year": 2026,
        "content": {"test": "测试数据"}
    }
    
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        response = requests.post(
            f"{BASE_URL}/teaching-office/self-evaluation",
            json=eval_data,
            headers=headers
        )
        response.raise_for_status()
        evaluation_id = response.json()["evaluation_id"]
        print(f"✅ 自评表已创建: {evaluation_id}")
    except Exception as e:
        print(f"❌ 创建自评表失败: {e}")
        return False
    
    # 步骤3: 上传文件
    print("\n[3/3] 上传测试文件...")
    
    # 创建测试文件
    test_file_content = b"This is a test file for attachment upload."
    test_file = io.BytesIO(test_file_content)
    test_file.name = "test_document.pdf"
    
    # 准备multipart/form-data
    files = {
        'files': ('test_document.pdf', test_file, 'application/pdf')
    }
    
    data = {
        'evaluation_id': evaluation_id,
        'indicator': 'teaching_process_management'
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/teaching-office/attachments",
            files=files,
            data=data,
            headers=headers
        )
        
        print(f"状态码: {response.status_code}")
        print(f"响应: {response.text[:500]}")
        
        if response.status_code == 201:
            result = response.json()
            print("✅ 文件上传成功")
            print(f"   上传数量: {result.get('uploaded_count')}")
            print(f"   附件ID: {result.get('attachment_ids')}")
            return True
        else:
            print(f"❌ 上传失败: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ 上传请求失败: {e}")
        return False

def main():
    print("\n" + "=" * 60)
    print("开始测试")
    print("=" * 60)
    
    success = test_file_upload()
    
    print("\n" + "=" * 60)
    if success:
        print("✅ 所有测试通过")
        print("\n文件上传功能正常工作！")
        print("现在可以在前端上传附件了。")
    else:
        print("❌ 测试失败")
        print("\n请检查：")
        print("1. 后端服务是否正常运行")
        print("2. MySQL数据库是否连接正常")
        print("3. uploads目录是否有写入权限")
    print("=" * 60)

if __name__ == "__main__":
    main()
