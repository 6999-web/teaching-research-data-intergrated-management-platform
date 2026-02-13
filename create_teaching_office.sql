USE teaching_office_evaluation;

-- 删除旧的测试教研室
DELETE FROM teaching_offices WHERE id = 'test-office-001';

-- 创建新的教研室，使用UUID格式的ID
INSERT INTO teaching_offices (id, name, college_id, created_at, updated_at)
VALUES (
    'a1b2c3d4-e5f6-4a5b-8c9d-111111111111',
    '测试教研室',
    NULL,
    NOW(),
    NOW()
);

-- 更新用户的teaching_office_id
UPDATE users 
SET teaching_office_id = 'a1b2c3d4-e5f6-4a5b-8c9d-111111111111'
WHERE username = '123';

-- 验证结果
SELECT id, name FROM teaching_offices;
SELECT username, name, teaching_office_id FROM users WHERE username = '123';
