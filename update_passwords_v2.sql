-- 更新测试账号，账号和密码都改为 123
USE teaching_office_evaluation;

-- 先删除旧的测试账号
DELETE FROM users WHERE username IN ('test_teaching_office', 'test_eval_team', '123', 'admin');

-- 创建教研室端账号: 用户名和密码都是 123
INSERT INTO users (id, username, name, email, password_hash, role, teaching_office_id, created_at, updated_at)
VALUES (
    'a1b2c3d4-e5f6-4a5b-8c9d-0e1f2a3b4c5d',
    '123',
    '教研室用户',
    'teaching123@test.com',
    '$2b$12$fsGArgXk2SbWTHHcH6sLZefVnvyPSFmn5Sy7AqG1DeR1gNjqRGxiO',
    'teaching_office',
    NULL,
    NOW(),
    NOW()
);

-- 创建考评小组账号: 用户名 admin，密码 123
INSERT INTO users (id, username, name, email, password_hash, role, teaching_office_id, created_at, updated_at)
VALUES (
    'b2c3d4e5-f6a7-4b5c-9d0e-1f2a3b4c5d6e',
    'admin',
    '考评小组用户',
    'admin123@test.com',
    '$2b$12$fsGArgXk2SbWTHHcH6sLZefVnvyPSFmn5Sy7AqG1DeR1gNjqRGxiO',
    'evaluation_team',
    NULL,
    NOW(),
    NOW()
);

-- 验证创建结果
SELECT username, name, role FROM users WHERE username IN ('123', 'admin');
