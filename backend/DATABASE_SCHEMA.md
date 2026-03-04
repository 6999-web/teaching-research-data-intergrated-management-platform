# Database Schema Documentation

## Overview

This document describes the database schema for the Teaching Office Evaluation System (教研室工作考评系统).

## Technology Stack

- **ORM**: SQLAlchemy 2.0.46
- **Database**: PostgreSQL
- **Migration Tool**: Alembic 1.13.1
- **Primary Key Type**: UUID (PostgreSQL UUID type)

## Table Structure

### 1. teaching_offices (教研室)

Stores information about teaching offices.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PRIMARY KEY | Unique identifier |
| name | VARCHAR(255) | NOT NULL | Teaching office name |
| code | VARCHAR(50) | UNIQUE, NOT NULL | Teaching office code |
| department | VARCHAR(255) | | Department name |
| created_at | TIMESTAMP | NOT NULL | Creation timestamp |
| updated_at | TIMESTAMP | NOT NULL | Last update timestamp |

**Indexes**: code

**Relationships**:
- One-to-many with self_evaluations
- One-to-many with users

---

### 2. users (用户)

Stores user accounts and authentication information.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PRIMARY KEY | Unique identifier |
| username | VARCHAR(100) | UNIQUE, NOT NULL | Login username |
| password_hash | VARCHAR(255) | NOT NULL | Hashed password |
| role | VARCHAR(50) | NOT NULL | User role (teaching_office, evaluation_team, evaluation_office, president_office) |
| teaching_office_id | UUID | FK → teaching_offices.id | Associated teaching office (nullable) |
| name | VARCHAR(255) | NOT NULL | User's full name |
| email | VARCHAR(255) | | Email address |
| created_at | TIMESTAMP | NOT NULL | Creation timestamp |
| updated_at | TIMESTAMP | NOT NULL | Last update timestamp |

**Indexes**: username

**Relationships**:
- Many-to-one with teaching_offices
- One-to-many with manual_scores (as reviewer)
- One-to-many with anomalies (as handler)
- One-to-many with final_scores (as determiner)
- One-to-many with approvals (as approver)
- One-to-many with publications (as publisher)
- One-to-many with operation_logs (as operator)

---

### 3. self_evaluations (自评表)

Stores self-evaluation forms submitted by teaching offices.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PRIMARY KEY | Unique identifier |
| teaching_office_id | UUID | FK → teaching_offices.id, NOT NULL | Teaching office that submitted |
| evaluation_year | INTEGER | NOT NULL | Evaluation year |
| content | JSONB | NOT NULL | Self-evaluation content (flexible structure) |
| status | VARCHAR(50) | NOT NULL | Status (draft, submitted, locked, ai_scored, manually_scored, finalized, published) |
| submitted_at | TIMESTAMP | | Submission timestamp |
| created_at | TIMESTAMP | NOT NULL | Creation timestamp |
| updated_at | TIMESTAMP | NOT NULL | Last update timestamp |

**Indexes**: teaching_office_id, evaluation_year

**Unique Constraints**: (teaching_office_id, evaluation_year)

**Relationships**:
- Many-to-one with teaching_offices
- One-to-many with attachments
- One-to-many with ai_scores
- One-to-many with anomalies
- One-to-many with manual_scores
- One-to-one with final_score
- One-to-one with insight_summary

---

### 4. attachments (附件)

Stores metadata for uploaded attachments.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PRIMARY KEY | Unique identifier |
| evaluation_id | UUID | FK → self_evaluations.id, NOT NULL | Associated evaluation |
| indicator | VARCHAR(255) | NOT NULL | Assessment indicator category |
| file_name | VARCHAR(255) | NOT NULL | Original file name |
| file_size | BIGINT | NOT NULL | File size in bytes |
| file_type | VARCHAR(100) | | MIME type |
| storage_path | VARCHAR(500) | NOT NULL | MinIO storage path |
| classified_by | VARCHAR(20) | NOT NULL | Classification source (user, ai) |
| uploaded_at | TIMESTAMP | NOT NULL | Upload timestamp |

**Indexes**: evaluation_id

**Relationships**:
- Many-to-one with self_evaluations

---

### 5. ai_scores (AI评分结果)

Stores AI scoring results from DeepSeek API.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PRIMARY KEY | Unique identifier |
| evaluation_id | UUID | FK → self_evaluations.id, NOT NULL | Associated evaluation |
| total_score | NUMERIC(5,2) | NOT NULL | Total AI score |
| indicator_scores | JSONB | NOT NULL | Detailed scores by indicator |
| parsed_reform_projects | INTEGER | NOT NULL | Number of reform projects parsed from attachments |
| parsed_honorary_awards | INTEGER | NOT NULL | Number of honorary awards parsed from attachments |
| scored_at | TIMESTAMP | NOT NULL | Scoring timestamp |

**Indexes**: evaluation_id

**Relationships**:
- Many-to-one with self_evaluations

---

### 6. anomalies (异常数据)

Stores detected anomalies in evaluations.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PRIMARY KEY | Unique identifier |
| evaluation_id | UUID | FK → self_evaluations.id, NOT NULL | Associated evaluation |
| type | VARCHAR(50) | NOT NULL | Anomaly type (count_mismatch, missing_attachment, invalid_data) |
| indicator | VARCHAR(255) | NOT NULL | Affected indicator |
| declared_count | INTEGER | | Count declared in self-evaluation |
| parsed_count | INTEGER | | Count parsed from attachments |
| description | TEXT | NOT NULL | Detailed description of anomaly |
| status | VARCHAR(20) | NOT NULL | Status (pending, handled) |
| handled_by | UUID | FK → users.id | User who handled the anomaly |
| handled_action | VARCHAR(20) | | Action taken (reject, correct) |
| handled_at | TIMESTAMP | | Handling timestamp |

**Indexes**: evaluation_id

**Relationships**:
- Many-to-one with self_evaluations
- Many-to-one with users (as handler)

---

### 7. manual_scores (手动评分记录)

Stores manual scoring records from reviewers.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PRIMARY KEY | Unique identifier |
| evaluation_id | UUID | FK → self_evaluations.id, NOT NULL | Associated evaluation |
| reviewer_id | UUID | FK → users.id, NOT NULL | Reviewer user |
| reviewer_name | VARCHAR(255) | NOT NULL | Reviewer's name |
| reviewer_role | VARCHAR(50) | NOT NULL | Reviewer's role (evaluation_team, evaluation_office) |
| weight | NUMERIC(3,2) | NOT NULL | Score weight |
| scores | JSONB | NOT NULL | Detailed scores by indicator |
| submitted_at | TIMESTAMP | NOT NULL | Submission timestamp |

**Indexes**: evaluation_id

**Relationships**:
- Many-to-one with self_evaluations
- Many-to-one with users (as reviewer)

---

### 8. final_scores (最终得分)

Stores final determined scores.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PRIMARY KEY | Unique identifier |
| evaluation_id | UUID | FK → self_evaluations.id, UNIQUE, NOT NULL | Associated evaluation |
| final_score | NUMERIC(5,2) | NOT NULL | Final determined score |
| summary | TEXT | | Summary explanation |
| determined_by | UUID | FK → users.id, NOT NULL | User who determined the score |
| determined_at | TIMESTAMP | NOT NULL | Determination timestamp |

**Unique Constraints**: evaluation_id

**Relationships**:
- One-to-one with self_evaluations
- Many-to-one with users (as determiner)

---

### 9. approvals (审定记录)

Stores approval decisions from president's office.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PRIMARY KEY | Unique identifier |
| evaluation_ids | UUID[] | NOT NULL | Array of evaluation IDs being approved |
| decision | VARCHAR(20) | NOT NULL | Decision (approve, reject) |
| reject_reason | TEXT | | Reason for rejection |
| approved_by | UUID | FK → users.id, NOT NULL | User who made the approval |
| approved_at | TIMESTAMP | NOT NULL | Approval timestamp |

**Relationships**:
- Many-to-one with users (as approver)

---

### 10. publications (公示记录)

Stores publication records.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PRIMARY KEY | Unique identifier |
| evaluation_ids | UUID[] | NOT NULL | Array of evaluation IDs being published |
| published_by | UUID | FK → users.id, NOT NULL | User who published |
| published_at | TIMESTAMP | NOT NULL | Publication timestamp |
| distributed_at | TIMESTAMP | | Distribution timestamp |

**Relationships**:
- Many-to-one with users (as publisher)

---

### 11. insight_summaries (感悟总结)

Stores auto-generated insight summaries.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PRIMARY KEY | Unique identifier |
| evaluation_id | UUID | FK → self_evaluations.id, UNIQUE, NOT NULL | Associated evaluation |
| summary | TEXT | NOT NULL | Generated summary text |
| generated_at | TIMESTAMP | NOT NULL | Generation timestamp |

**Unique Constraints**: evaluation_id

**Relationships**:
- One-to-one with self_evaluations

---

### 12. operation_logs (操作日志)

Stores all system operations for audit trail.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PRIMARY KEY | Unique identifier |
| operation_type | VARCHAR(50) | NOT NULL | Operation type (submit, ai_score, manual_score, handle_anomaly, sync, approve, publish, distribute) |
| operator_id | UUID | FK → users.id, NOT NULL | User who performed the operation |
| operator_name | VARCHAR(255) | NOT NULL | Operator's name |
| operator_role | VARCHAR(50) | NOT NULL | Operator's role |
| target_id | UUID | NOT NULL | ID of the target entity |
| target_type | VARCHAR(50) | NOT NULL | Type of the target entity |
| details | JSONB | | Additional operation details |
| operated_at | TIMESTAMP | NOT NULL | Operation timestamp |

**Indexes**: operator_id, target_id

**Relationships**:
- Many-to-one with users (as operator)

---

## Entity Relationship Diagram

```
teaching_offices (1) ──< (N) self_evaluations
teaching_offices (1) ──< (N) users

self_evaluations (1) ──< (N) attachments
self_evaluations (1) ──< (N) ai_scores
self_evaluations (1) ──< (N) anomalies
self_evaluations (1) ──< (N) manual_scores
self_evaluations (1) ──── (1) final_scores
self_evaluations (1) ──── (1) insight_summaries

users (1) ──< (N) manual_scores (as reviewer)
users (1) ──< (N) anomalies (as handler)
users (1) ──< (N) final_scores (as determiner)
users (1) ──< (N) approvals (as approver)
users (1) ──< (N) publications (as publisher)
users (1) ──< (N) operation_logs (as operator)
```

## JSONB Column Structures

### self_evaluations.content

```json
{
  "teachingProcessManagement": "string",
  "courseConstruction": "string",
  "teachingReformProjects": 0,
  "honoraryAwards": 0,
  // ... other evaluation fields
}
```

### ai_scores.indicator_scores

```json
[
  {
    "indicator": "string",
    "score": 0.00,
    "reasoning": "string"
  }
]
```

### manual_scores.scores

```json
[
  {
    "indicator": "string",
    "score": 0.00,
    "comment": "string"
  }
]
```

### operation_logs.details

```json
{
  // Flexible structure depending on operation_type
  "key": "value"
}
```

## Migration Files

- **001_initial_database_schema.py** - Initial schema creation with all 12 tables

## Notes

1. All timestamps are stored in UTC
2. UUID v4 is used for all primary keys
3. JSONB is used for flexible data structures
4. Indexes are created on foreign keys and frequently queried columns
5. Cascade deletes are handled at the ORM level, not database level
6. All tables include created_at/updated_at timestamps where applicable
