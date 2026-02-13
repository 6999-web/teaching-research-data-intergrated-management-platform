-- 修复数据库问题的SQL脚本
USE teaching_office_evaluation;

-- 1. 确保teaching_offices表有数据
INSERT INTO teaching_offices (id, name, code, department, created_at, updated_at)
VALUES ('test-office-001', 'Test Teaching Office', 'TEST001', 'Test Department', NOW(), NOW())
ON DUPLICATE KEY UPDATE name=name;

-- 2. 确保测试用户存在
INSERT INTO users (id, username, name, email, password_hash, role, teaching_office_id, created_at, updated_at)
VALUES (
    UUID(),
    'test_teaching_office',
    'Test Teaching Office User',
    'teaching@test.com',
    '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYzpLaEg7Iq',
    'teaching_office',
    'test-office-001',
    NOW(),
    NOW()
) ON DUPLICATE KEY UPDATE username=username;

INSERT INTO users (id, username, name, email, password_hash, role, teaching_office_id, created_at, updated_at)
VALUES (
    UUID(),
    'test_eval_team',
    'Test Evaluation Team User',
    'evalteam@test.com',
    '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYzpLaEg7Iq',
    'evaluation_team',
    NULL,
    NOW(),
    NOW()
) ON DUPLICATE KEY UPDATE username=username;

-- 3. 查看现有数据
SELECT '=== Teaching Offices ===' as info;
SELECT * FROM teaching_offices;

SELECT '=== Users ===' as info;
SELECT username, name, role FROM users WHERE username LIKE 'test_%';

SELECT '=== Self Evaluations ===' as info;
SELECT 
    se.id,
    toff.name as teaching_office_name,
    se.evaluation_year,
    se.status,
    se.submitted_at
FROM self_evaluations se
LEFT JOIN teaching_offices toff ON se.teaching_office_id = toff.id
ORDER BY se.created_at DESC
LIMIT 10;

-- 4. 查看待评分的自评表
SELECT '=== Evaluations for Scoring ===' as info;
SELECT 
    se.id,
    toff.name as teaching_office_name,
    se.status
FROM self_evaluations se
LEFT JOIN teaching_offices toff ON se.teaching_office_id = toff.id
WHERE se.status IN ('locked', 'ai_scored');
