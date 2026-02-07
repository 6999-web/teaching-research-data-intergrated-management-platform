# Database Migrations

This directory contains Alembic database migrations for the Teaching Office Evaluation System.

## Database Schema

The system uses the following tables:

### Core Tables

1. **teaching_offices** - 教研室信息
   - Stores teaching office information
   - Indexed on: code

2. **users** - 用户信息
   - Stores user accounts and authentication
   - Indexed on: username
   - Foreign key: teaching_office_id → teaching_offices.id

3. **self_evaluations** - 自评表
   - Stores self-evaluation forms submitted by teaching offices
   - Indexed on: teaching_office_id, evaluation_year
   - Unique constraint: (teaching_office_id, evaluation_year)
   - Foreign key: teaching_office_id → teaching_offices.id

### Evaluation Data Tables

4. **attachments** - 附件
   - Stores uploaded attachment metadata
   - Indexed on: evaluation_id
   - Foreign key: evaluation_id → self_evaluations.id

5. **ai_scores** - AI评分结果
   - Stores AI scoring results from DeepSeek API
   - Indexed on: evaluation_id
   - Foreign key: evaluation_id → self_evaluations.id

6. **anomalies** - 异常数据
   - Stores detected anomalies in evaluations
   - Indexed on: evaluation_id
   - Foreign keys: evaluation_id → self_evaluations.id, handled_by → users.id

7. **manual_scores** - 手动评分记录
   - Stores manual scoring records from reviewers
   - Indexed on: evaluation_id
   - Foreign keys: evaluation_id → self_evaluations.id, reviewer_id → users.id

8. **final_scores** - 最终得分
   - Stores final determined scores
   - Unique constraint: evaluation_id
   - Foreign keys: evaluation_id → self_evaluations.id, determined_by → users.id

### Workflow Tables

9. **approvals** - 审定记录
   - Stores approval decisions from president's office
   - Foreign key: approved_by → users.id

10. **publications** - 公示记录
    - Stores publication records
    - Foreign key: published_by → users.id

11. **insight_summaries** - 感悟总结
    - Stores auto-generated insight summaries
    - Unique constraint: evaluation_id
    - Foreign key: evaluation_id → self_evaluations.id

12. **operation_logs** - 操作日志
    - Stores all system operations for audit trail
    - Indexed on: operator_id, target_id
    - Foreign key: operator_id → users.id

## Running Migrations

### Prerequisites

1. Ensure PostgreSQL is running
2. Update database connection settings in `.env` file or `app/core/config.py`

### Apply Migrations

To apply all pending migrations:

```bash
cd backend
alembic upgrade head
```

### Rollback Migrations

To rollback the last migration:

```bash
alembic downgrade -1
```

To rollback all migrations:

```bash
alembic downgrade base
```

### Check Current Version

```bash
alembic current
```

### View Migration History

```bash
alembic history
```

## Creating New Migrations

When you modify the models, create a new migration:

```bash
alembic revision --autogenerate -m "Description of changes"
```

Review the generated migration file before applying it.

## Migration Files

- `001_initial_database_schema.py` - Initial database schema with all tables

## Notes

- All tables use UUID as primary keys
- JSONB columns are used for flexible data storage (content, scores, details)
- Timestamps are stored in UTC
- Indexes are created on foreign keys and frequently queried columns
- Cascade delete is configured in SQLAlchemy models, not in database constraints
