#!/usr/bin/env python3
"""测试常见的MySQL密码"""

import pymysql

# 常见密码列表
passwords = [
    "",           # 空密码
    "123456",
    "root",
    "password",
    "admin",
    "123123",
    "mysql",
    "your_password"
]

print("正在测试 MySQL 连接...")
print("=" * 60)

for pwd in passwords:
    try:
        conn = pymysql.connect(
            host="localhost",
            port=3306,
            user="root",
            password=pwd
        )
        print(f"✓ 成功! MySQL root 密码是: '{pwd}'")
        
        # 检查数据库
        cursor = conn.cursor()
        cursor.execute("SHOW DATABASES")
        databases = [db[0] for db in cursor.fetchall()]
        
        if "teaching_office_evaluation" in databases:
            print(f"  ✓ 找到数据库: teaching_office_evaluation")
        else:
            print(f"  ⚠ 未找到数据库: teaching_office_evaluation")
            print(f"  现有数据库: {', '.join(databases[:5])}")
        
        conn.close()
        break
        
    except pymysql.err.OperationalError as e:
        if "Access denied" in str(e):
            continue
        else:
            print(f"✗ 连接错误: {e}")
            break
    except Exception as e:
        print(f"✗ 未知错误: {e}")
        break
else:
    print("✗ 所有常见密码都失败了")
    print("\n请手动输入 MySQL root 密码:")
    manual_pwd = input("密码: ")
    
    try:
        conn = pymysql.connect(
            host="localhost",
            port=3306,
            user="root",
            password=manual_pwd
        )
        print(f"✓ 成功! 密码是: '{manual_pwd}'")
        conn.close()
    except Exception as e:
        print(f"✗ 仍然失败: {e}")

print("=" * 60)
