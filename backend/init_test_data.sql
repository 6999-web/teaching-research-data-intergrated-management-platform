-- 初始化测试数据
USE teaching_office_evaluation;

-- 1. 创建教研室
INSERT INTO teaching_offices (id, name, code, department, created_at, updated_at) VALUES
('00000000-0000-0000-0000-000000000001', '计算机科学教研室', 'CS001', '计算机学院', NOW(), NOW()),
('00000000-0000-0000-0000-000000000002', '数学教研室', 'MATH001', '数学学院', NOW(), NOW()),
('00000000-0000-0000-0000-000000000003', '物理教研室', 'PHY001', '物理学院', NOW(), NOW())
ON DUPLICATE KEY UPDATE name=VALUES(name);

-- 2. 创建用户
-- 密码都是 'password123' 的bcrypt哈希值
-- $2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYIr.oPfHiq

INSERT INTO users (id, username, password_hash, role, teaching_office_id, name, email, created_at, updated_at) VALUES
-- 教研室用户
('10000000-0000-0000-0000-000000000001', 'director1', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYIr.oPfHiq', 'teaching_office', '00000000-0000-0000-0000-000000000001', '张主任', 'director1@example.com', NOW(), NOW()),
('10000000-0000-0000-0000-000000000002', 'director2', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYIr.oPfHiq', 'teaching_office', '00000000-0000-0000-0000-000000000002', '李主任', 'director2@example.com', NOW(), NOW()),
('10000000-0000-0000-0000-000000000003', 'director3', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYIr.oPfHiq', 'teaching_office', '00000000-0000-0000-0000-000000000003', '王主任', 'director3@example.com', NOW(), NOW()),

-- 评教小组用户
('20000000-0000-0000-0000-000000000001', 'evaluator1', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYIr.oPfHiq', 'evaluation_team', NULL, '评委张老师', 'evaluator1@example.com', NOW(), NOW()),
('20000000-0000-0000-0000-000000000002', 'evaluator2', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYIr.oPfHiq', 'evaluation_team', NULL, '评委李老师', 'evaluator2@example.com', NOW(), NOW()),

-- 评教小组办公室用户
('30000000-0000-0000-0000-000000000001', 'office1', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYIr.oPfHiq', 'evaluation_office', NULL, '办公室主任', 'office1@example.com', NOW(), NOW()),

-- 校长办公会用户
('40000000-0000-0000-0000-000000000001', 'president1', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYIr.oPfHiq', 'president_office', NULL, '校长', 'president1@example.com', NOW(), NOW())
ON DUPLICATE KEY UPDATE name=VALUES(name);

SELECT '✅ 测试数据初始化完成' AS status;
SELECT '用户名: director1, director2, director3, evaluator1, evaluator2, office1, president1' AS users;
SELECT '密码: password123' AS password;
