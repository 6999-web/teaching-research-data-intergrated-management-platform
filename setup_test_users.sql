USE teaching_office_evaluation;

INSERT INTO teaching_offices (id, name, code, department, created_at, updated_at)
VALUES ('test-office-001', 'Test Teaching Office', 'TEST001', 'Test Department', NOW(), NOW())
ON DUPLICATE KEY UPDATE name=name;

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

SELECT username, name, role FROM users WHERE username LIKE 'test_%';
