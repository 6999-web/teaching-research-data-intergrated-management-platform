-- Create test users for the teaching office evaluation system
USE teaching_office_evaluation;

-- Create teaching office
INSERT INTO teaching_offices (id, name, description, created_at, updated_at)
VALUES ('test-office-001', '测试教研室', '用于测试', NOW(), NOW())
ON DUPLICATE KEY UPDATE name=name;

-- Create teaching office user (password: password123)
INSERT INTO users (id, username, name, email, hashed_password, role, teaching_office_id, created_at, updated_at)
VALUES (
    UUID(),
    'test_teaching_office',
    '测试教研室用户',
    'teaching@test.com',
    '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYzpLaEg7Iq',
    'teaching_office',
    'test-office-001',
    NOW(),
    NOW()
) ON DUPLICATE KEY UPDATE username=username;

-- Create evaluation team user (password: password123)
INSERT INTO users (id, username, name, email, hashed_password, role, created_at, updated_at)
VALUES (
    UUID(),
    'test_eval_team',
    '测试考评小组用户',
    'evalteam@test.com',
    '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYzpLaEg7Iq',
    'evaluation_team',
    NULL,
    NOW(),
    NOW()
) ON DUPLICATE KEY UPDATE username=username;

-- Verify users were created
SELECT username, name, role, teaching_office_id FROM users WHERE username LIKE 'test_%';
