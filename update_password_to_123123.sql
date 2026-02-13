USE teaching_office_evaluation;

-- 更新两个账号的密码为 123123
UPDATE users 
SET password_hash = '$2b$12$nLH0zB7FinrufX8NxQe7kOB5HldkwEKApt26dT9VC/.Fz.ff9U9ka',
    updated_at = NOW()
WHERE username IN ('123', 'admin');

-- 验证更新结果
SELECT username, name, role, 
       SUBSTRING(password_hash, 1, 20) as password_hash_preview,
       updated_at
FROM users 
WHERE username IN ('123', 'admin');
