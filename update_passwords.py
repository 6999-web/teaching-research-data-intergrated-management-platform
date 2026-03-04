#!/usr/bin/env python3
"""
更新测试账号的密码为 123
"""

from passlib.context import CryptContext

# 创建密码上下文
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# 生成密码 "123" 的hash
password = "123"
password_hash = pwd_context.hash(password)

print("密码 '123' 的hash值:")
print(password_hash)
print("\n")

# 生成SQL更新语句
sql = f"""
-- 更新测试账号密码为 123
USE teaching_office_evaluation;

-- 更新教研室端账号
UPDATE users 
SET password_hash = '{password_hash}',
    username = '123'
WHERE username = 'test_teaching_office';

-- 更新考评小组账号
UPDATE users 
SET password_hash = '{password_hash}',
    username = '123'
WHERE username = 'test_eval_team';

-- 验证更新
SELECT username, name, role FROM users WHERE username = '123';
"""

print("SQL更新语句:")
print(sql)

# 保存到文件
with open('update_passwords.sql', 'w', encoding='utf-8') as f:
    f.write(sql)

print("\nSQL语句已保存到 update_passwords.sql")
