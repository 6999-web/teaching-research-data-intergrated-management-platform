#!/usr/bin/env python3
"""
测试附件上传和下载流程
"""
import requests
import json
import os

BASE_URL = "http://localhost:8000/api"

def login(username, password):
    """登录获取token"""
    response = requests.post(
        f"{BASE_URL}/auth/login",
        json={"username": username, "password": password}
    )
    if response.status_code == 200:
        data = response.json()
        return data.get("access_token")
    else:
        print(f"登录失败: {response.status_code}")
        print(response.text)
        return None

def get_evaluations(token):
    """获取自评表列表"""
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(
        f"{BASE_URL}/teaching-office/self-evaluations",
        headers=headers
    )
    if response.status_code == 200:
        return response.json()
    else:
        print(f"获取自评表失败: {response.status_code}")
        print(response.text)
        return []

def get_attachments(token, evaluation_id):
    """获取附件列表"""
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(
        f"{BASE_URL}/teaching-office/attachments/{evaluation_id}",
        headers=headers
    )
    print(f"\n获取附件列表:")
    print(f"URL: {BASE_URL}/teaching-office/attachments/{evaluation_id}")
    print(f"状态码: {response.status_code}")
    
    if response.status_code == 200:
        return response.json()
    else:
        print(f"响应内容: {response.text}")
        return []

def main():
    print("=" * 60)
    print("测试附件上传和下载流程")
    print("=" * 60)
    
    # 测试1: 教研室端上传
    print("\n【测试1】教研室端上传附件")
    print("-" * 60)
    
    teaching_token = login("director1", "password123")
    if not teaching_token:
        print("❌ 教研室账号登录失败")
        return
    print("✓ 教研室账号登录成功")
    
    # 获取自评表
    evaluations = get_evaluations(teaching_token)
    if not evaluations:
        print("❌ 没有找到自评表")
        return
    
    evaluation_id = evaluations[0].get("id")
    print(f"✓ 找到自评表: {evaluation_id}")
    
    # 获取附件列表
    attachments = get_attachments(teaching_token, evaluation_id)
    print(f"✓ 教研室端可以看到 {len(attachments)} 个附件")
    
    if attachments:
        print("\n附件列表:")
        for att in attachments:
            print(f"  - {att.get('file_name')} ({att.get('indicator')})")
    
    # 测试2: 考评小组端查看
    print("\n【测试2】考评小组端查看附件")
    print("-" * 60)
    
    eval_token = login("evaluator1", "password123")
    if not eval_token:
        print("❌ 考评小组账号登录失败")
        return
    print("✓ 考评小组账号登录成功")
    
    # 获取附件列表
    attachments = get_attachments(eval_token, evaluation_id)
    print(f"✓ 考评小组端可以看到 {len(attachments)} 个附件")
    
    if attachments:
        print("\n附件列表:")
        for att in attachments:
            print(f"  - {att.get('file_name')} ({att.get('indicator')})")
    else:
        print("⚠️  考评小组端看不到附件！")
    
    # 测试3: 下载附件
    if attachments:
        print("\n【测试3】下载附件")
        print("-" * 60)
        
        attachment_id = attachments[0].get("id")
        headers = {"Authorization": f"Bearer {eval_token}"}
        response = requests.get(
            f"{BASE_URL}/teaching-office/attachments/{attachment_id}/download",
            headers=headers
        )
        
        print(f"下载请求状态码: {response.status_code}")
        if response.status_code == 200:
            print(f"✓ 文件下载成功，大小: {len(response.content)} 字节")
        else:
            print(f"❌ 文件下载失败")
            print(f"响应: {response.text}")
    
    print("\n" + "=" * 60)
    print("测试完成")
    print("=" * 60)

if __name__ == "__main__":
    main()
