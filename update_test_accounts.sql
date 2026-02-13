USE teaching_office_evaluation;

DELETE FROM users WHERE username IN ('test_teaching_office', 'test_eval_team', '123', 'admin');

INSERT INTO users (id, username, name, email, password_hash, role, teaching_office_id, created_at, updated_at)
VALUES 
('a1b2c3d4-e5f6-4a5b-8c9d-0e1f2a3b4c5d', '123', 'Teaching Office User', 'teaching123@test.com', '$2b$12$fsGArgXk2SbWTHHcH6sLZefVnvyPSFmn5Sy7AqG1DeR1gNjqRGxiO', 'teaching_office', NULL, NOW(), NOW()),
('b2c3d4e5-f6a7-4b5c-9d0e-1f2a3b4c5d6e', 'admin', 'Evaluation Team User', 'admin123@test.com', '$2b$12$fsGArgXk2SbWTHHcH6sLZefVnvyPSFmn5Sy7AqG1DeR1gNjqRGxiO', 'evaluation_team', NULL, NOW(), NOW());

SELECT username, name, role FROM users WHERE username IN ('123', 'admin');
