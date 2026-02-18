-- 创建所有数据库表（MySQL版本）
-- 使用CHAR(36)存储UUID

USE teaching_office_evaluation;

-- 1. 教研室表
CREATE TABLE IF NOT EXISTS teaching_offices (
    id CHAR(36) NOT NULL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    code VARCHAR(50) NOT NULL UNIQUE,
    department VARCHAR(255),
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX ix_teaching_offices_code (code)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 2. 用户表
CREATE TABLE IF NOT EXISTS users (
    id CHAR(36) NOT NULL PRIMARY KEY,
    username VARCHAR(100) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    role VARCHAR(50) NOT NULL,
    teaching_office_id CHAR(36),
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255),
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (teaching_office_id) REFERENCES teaching_offices(id),
    INDEX ix_users_username (username),
    INDEX ix_users_role (role)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 3. 自评表
CREATE TABLE IF NOT EXISTS self_evaluations (
    id CHAR(36) NOT NULL PRIMARY KEY,
    teaching_office_id CHAR(36) NOT NULL,
    evaluation_year INT NOT NULL,
    content JSON NOT NULL,
    status VARCHAR(50) NOT NULL DEFAULT 'draft',
    submitted_at DATETIME,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    version INT NOT NULL DEFAULT 1,
    FOREIGN KEY (teaching_office_id) REFERENCES teaching_offices(id),
    INDEX ix_self_evaluations_teaching_office_id (teaching_office_id),
    INDEX ix_self_evaluations_year (evaluation_year),
    INDEX ix_self_evaluations_status (status),
    UNIQUE KEY unique_teaching_office_year (teaching_office_id, evaluation_year)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 4. 附件表
CREATE TABLE IF NOT EXISTS attachments (
    id CHAR(36) NOT NULL PRIMARY KEY,
    evaluation_id CHAR(36) NOT NULL,
    indicator VARCHAR(100) NOT NULL,
    file_name VARCHAR(255) NOT NULL,
    file_size BIGINT NOT NULL,
    file_type VARCHAR(100) NOT NULL,
    storage_path VARCHAR(500) NOT NULL,
    classified_by VARCHAR(50) NOT NULL DEFAULT 'user',
    uploaded_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    is_archived BOOLEAN NOT NULL DEFAULT FALSE,
    archived_at DATETIME,
    FOREIGN KEY (evaluation_id) REFERENCES self_evaluations(id),
    INDEX ix_attachments_evaluation_id (evaluation_id),
    INDEX ix_attachments_indicator (indicator)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 5. AI评分表
CREATE TABLE IF NOT EXISTS ai_scores (
    id CHAR(36) NOT NULL PRIMARY KEY,
    evaluation_id CHAR(36) NOT NULL UNIQUE,
    total_score DECIMAL(5,2) NOT NULL,
    scores JSON NOT NULL,
    analysis TEXT,
    scored_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    version INT NOT NULL DEFAULT 1,
    FOREIGN KEY (evaluation_id) REFERENCES self_evaluations(id),
    INDEX ix_ai_scores_evaluation_id (evaluation_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 6. 异常记录表
CREATE TABLE IF NOT EXISTS anomalies (
    id CHAR(36) NOT NULL PRIMARY KEY,
    evaluation_id CHAR(36) NOT NULL,
    anomaly_type VARCHAR(50) NOT NULL,
    description TEXT NOT NULL,
    severity VARCHAR(20) NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'pending',
    detected_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    resolved_at DATETIME,
    resolution_notes TEXT,
    FOREIGN KEY (evaluation_id) REFERENCES self_evaluations(id),
    INDEX ix_anomalies_evaluation_id (evaluation_id),
    INDEX ix_anomalies_status (status)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 7. 手动评分表
CREATE TABLE IF NOT EXISTS manual_scores (
    id CHAR(36) NOT NULL PRIMARY KEY,
    evaluation_id CHAR(36) NOT NULL UNIQUE,
    scorer_id CHAR(36) NOT NULL,
    total_score DECIMAL(5,2) NOT NULL,
    scores JSON NOT NULL,
    comments TEXT,
    scored_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    version INT NOT NULL DEFAULT 1,
    FOREIGN KEY (evaluation_id) REFERENCES self_evaluations(id),
    FOREIGN KEY (scorer_id) REFERENCES users(id),
    INDEX ix_manual_scores_evaluation_id (evaluation_id),
    INDEX ix_manual_scores_scorer_id (scorer_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 8. 最终评分表
CREATE TABLE IF NOT EXISTS final_scores (
    id CHAR(36) NOT NULL PRIMARY KEY,
    evaluation_id CHAR(36) NOT NULL UNIQUE,
    ai_score DECIMAL(5,2),
    manual_score DECIMAL(5,2),
    final_score DECIMAL(5,2) NOT NULL,
    weight_ai DECIMAL(3,2) NOT NULL DEFAULT 0.50,
    weight_manual DECIMAL(3,2) NOT NULL DEFAULT 0.50,
    finalized_by CHAR(36) NOT NULL,
    finalized_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    comments TEXT,
    version INT NOT NULL DEFAULT 1,
    FOREIGN KEY (evaluation_id) REFERENCES self_evaluations(id),
    FOREIGN KEY (finalized_by) REFERENCES users(id),
    INDEX ix_final_scores_evaluation_id (evaluation_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 9. 审批表
CREATE TABLE IF NOT EXISTS approvals (
    id CHAR(36) NOT NULL PRIMARY KEY,
    evaluation_id CHAR(36) NOT NULL,
    approver_id CHAR(36) NOT NULL,
    approval_type VARCHAR(50) NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'pending',
    comments TEXT,
    approved_at DATETIME,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (evaluation_id) REFERENCES self_evaluations(id),
    FOREIGN KEY (approver_id) REFERENCES users(id),
    INDEX ix_approvals_evaluation_id (evaluation_id),
    INDEX ix_approvals_status (status)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 10. 发布表
CREATE TABLE IF NOT EXISTS publications (
    id CHAR(36) NOT NULL PRIMARY KEY,
    evaluation_id CHAR(36) NOT NULL,
    published_by CHAR(36) NOT NULL,
    published_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    distribution_status VARCHAR(50) NOT NULL DEFAULT 'pending',
    distributed_at DATETIME,
    FOREIGN KEY (evaluation_id) REFERENCES self_evaluations(id),
    FOREIGN KEY (published_by) REFERENCES users(id),
    INDEX ix_publications_evaluation_id (evaluation_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 11. 洞察摘要表
CREATE TABLE IF NOT EXISTS insight_summaries (
    id CHAR(36) NOT NULL PRIMARY KEY,
    evaluation_year INT NOT NULL,
    summary_type VARCHAR(50) NOT NULL,
    content JSON NOT NULL,
    generated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    INDEX ix_insight_summaries_year (evaluation_year)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 12. 操作日志表
CREATE TABLE IF NOT EXISTS operation_logs (
    id CHAR(36) NOT NULL PRIMARY KEY,
    operation_type VARCHAR(50) NOT NULL,
    operator_id CHAR(36) NOT NULL,
    operator_name VARCHAR(255) NOT NULL,
    operator_role VARCHAR(50) NOT NULL,
    target_id CHAR(36),
    target_type VARCHAR(50),
    details JSON,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (operator_id) REFERENCES users(id),
    INDEX ix_operation_logs_operator_id (operator_id),
    INDEX ix_operation_logs_type (operation_type),
    INDEX ix_operation_logs_created_at (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 13. 同步任务表
CREATE TABLE IF NOT EXISTS sync_tasks (
    id CHAR(36) NOT NULL PRIMARY KEY,
    evaluation_ids JSON NOT NULL,
    sync_type VARCHAR(50) NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'pending',
    initiated_by CHAR(36) NOT NULL,
    initiated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    completed_at DATETIME,
    error_message TEXT,
    FOREIGN KEY (initiated_by) REFERENCES users(id),
    INDEX ix_sync_tasks_status (status)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 14. 学院表
CREATE TABLE IF NOT EXISTS colleges (
    id CHAR(36) NOT NULL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    code VARCHAR(50) NOT NULL UNIQUE,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX ix_colleges_code (code)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 15. 改进计划表
CREATE TABLE IF NOT EXISTS improvement_plans (
    id CHAR(36) NOT NULL PRIMARY KEY,
    evaluation_id CHAR(36) NOT NULL,
    teaching_office_id CHAR(36) NOT NULL,
    plan_content TEXT NOT NULL,
    target_date DATE,
    status VARCHAR(20) NOT NULL DEFAULT 'draft',
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (evaluation_id) REFERENCES self_evaluations(id),
    FOREIGN KEY (teaching_office_id) REFERENCES teaching_offices(id),
    INDEX ix_improvement_plans_evaluation_id (evaluation_id),
    INDEX ix_improvement_plans_teaching_office_id (teaching_office_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 16. Alembic版本表
CREATE TABLE IF NOT EXISTS alembic_version (
    version_num VARCHAR(32) NOT NULL PRIMARY KEY
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 插入初始版本号
INSERT INTO alembic_version (version_num) VALUES ('001') ON DUPLICATE KEY UPDATE version_num='001';
