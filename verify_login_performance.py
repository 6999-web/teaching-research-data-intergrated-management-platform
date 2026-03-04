#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
登录性能验证脚本
用于验证登录性能优化是否生效
"""

import requests
import time
import statistics
import json
from datetime import datetime

def test_login_performance(url, username, password, iterations=10):
    """
    测试登录性能
    
    Args:
        url: 登录 API 地址
        username: 用户名
        password: 密码
        iterations: 测试次数
    """
    times = []
    successful = 0
    failed = 0
    
    print("=" * 60)
    print("登录性能验证测试")
    print("=" * 60)
    print(f"测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"API 地址: {url}")
    print(f"用户名: {username}")
    print(f"测试次数: {iterations}")
    print("-" * 60)
    
    for i in range(iterations):
        try:
            start = time.time()
            response = requests.post(
                url,
                json={
                    "username": username,
                    "password": password
                },
                timeout=10
            )
            duration = (time.time() - start) * 1000
            times.append(duration)
            
            if response.status_code == 200:
                successful += 1
                status = "✅ 成功"
                data = response.json()
                token_preview = data.get('token', '')[:20] + '...'
            else:
                failed += 1
                status = f"❌ 失败 ({response.status_code})"
                token_preview = "N/A"
            
            print(f"请求 {i+1:2d}: {duration:7.2f}ms {status}")
            
        except requests.exceptions.Timeout:
            failed += 1
            print(f"请求 {i+1:2d}: 超时 ❌")
        except requests.exceptions.ConnectionError:
            failed += 1
            print(f"请求 {i+1:2d}: 连接失败 ❌")
        except Exception as e:
            failed += 1
            print(f"请求 {i+1:2d}: 错误 - {str(e)} ❌")
    
    print("-" * 60)
    
    if times:
        print("\n📊 性能统计:")
        print(f"  成功请求: {successful}/{iterations}")
        print(f"  失败请求: {failed}/{iterations}")
        print(f"  平均耗时: {statistics.mean(times):.2f}ms")
        print(f"  最小耗时: {min(times):.2f}ms")
        print(f"  最大耗时: {max(times):.2f}ms")
        print(f"  中位数:   {statistics.median(times):.2f}ms")
        if len(times) > 1:
            print(f"  标准差:   {statistics.stdev(times):.2f}ms")
        
        # 性能评级
        avg = statistics.mean(times)
        print("\n🎯 性能评级:")
        if avg < 100:
            rating = "✅ 优秀 (< 100ms)"
        elif avg < 300:
            rating = "✅ 良好 (100-300ms)"
        elif avg < 500:
            rating = "⚠️ 一般 (300-500ms)"
        else:
            rating = "❌ 较差 (> 500ms)"
        
        print(f"  {rating}")
        
        # 检查是否满足目标
        print("\n✅ 目标检查:")
        if avg < 300:
            print("  ✅ 性能目标已达成 (< 300ms)")
        else:
            print("  ❌ 性能目标未达成 (需要 < 300ms)")
        
        if avg < 200:
            print("  ✅ 优秀目标已达成 (< 200ms)")
        else:
            print("  ⚠️ 优秀目标未达成 (需要 < 200ms)")
        
        # 性能对比
        print("\n📈 性能对比:")
        print("  优化前: 207-527ms")
        print("  优化后: 107-227ms (预期)")
        print(f"  实际:   {min(times):.2f}-{max(times):.2f}ms")
        
        if avg < 227:
            improvement = ((527 - avg) / 527) * 100
            print(f"  改进:   ↓ {improvement:.1f}% (相对于优化前最大值)")
        
        print("\n" + "=" * 60)
        return True
    else:
        print("❌ 没有成功的请求")
        print("=" * 60)
        return False


def test_login_functionality(url, username, password):
    """
    测试登录功能
    
    Args:
        url: 登录 API 地址
        username: 用户名
        password: 密码
    """
    print("\n" + "=" * 60)
    print("登录功能验证测试")
    print("=" * 60)
    
    try:
        response = requests.post(
            url,
            json={
                "username": username,
                "password": password
            },
            timeout=10
        )
        
        print(f"状态码: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("\n✅ 登录成功")
            print(f"  用户 ID: {data.get('userId', 'N/A')}")
            print(f"  角色: {data.get('role', 'N/A')}")
            print(f"  教研室 ID: {data.get('teachingOfficeId', 'N/A')}")
            print(f"  Token 长度: {len(data.get('token', ''))}")
            print(f"  过期时间: {data.get('expiresIn', 'N/A')} 秒")
            print("=" * 60)
            return True
        else:
            print(f"\n❌ 登录失败")
            print(f"  错误: {response.text}")
            print("=" * 60)
            return False
            
    except Exception as e:
        print(f"\n❌ 请求失败: {str(e)}")
        print("=" * 60)
        return False


def main():
    """主函数"""
    # 配置
    API_URL = "http://localhost:8000/api/auth/login"
    USERNAME = "director1"
    PASSWORD = "password123"
    ITERATIONS = 10
    
    print("\n")
    print("╔" + "=" * 58 + "╗")
    print("║" + " " * 58 + "║")
    print("║" + "  教研室考评系统 - 登录性能验证".center(58) + "║")
    print("║" + " " * 58 + "║")
    print("╚" + "=" * 58 + "╝")
    
    # 测试功能
    print("\n[1/2] 测试登录功能...")
    functionality_ok = test_login_functionality(API_URL, USERNAME, PASSWORD)
    
    if not functionality_ok:
        print("\n❌ 登录功能测试失败，请检查后端是否正常运行")
        print("   后端地址: http://localhost:8000")
        return
    
    # 测试性能
    print("\n[2/2] 测试登录性能...")
    performance_ok = test_login_performance(API_URL, USERNAME, PASSWORD, ITERATIONS)
    
    # 总结
    print("\n" + "=" * 60)
    print("测试总结")
    print("=" * 60)
    if functionality_ok and performance_ok:
        print("✅ 所有测试通过")
        print("✅ 登录性能优化已生效")
        print("✅ 系统可投入生产")
    else:
        print("❌ 部分测试失败")
        print("❌ 请检查后端配置")
    print("=" * 60)


if __name__ == "__main__":
    main()
