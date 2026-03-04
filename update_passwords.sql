
-- 更新测试账号密码为 123
USE teaching_office_evaluation;

-- 更新教研室端账号
UPDATE users 
SET password_hash = '$2b$12$fsGArgXk2SbWTHHcH6sLZefVnvyPSFmn5Sy7AqG1DeR1gNjqRGxiO',
    username = '123'
WHERE username = 'test_teaching_office';

-- 更新考评小组账号
UPDATE users 
SET password_hash = '$2b$12$fsGArgXk2SbWTHHcH6sLZefVnvyPSFmn5Sy7AqG1DeR1gNjqRGxiO',
    username = '123'
WHERE username = 'test_eval_team';

-- 验证更新
SELECT username, name, role FROM users WHERE username = '123';
