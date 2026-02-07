"""Initial database schema with all models

Revision ID: 001
Revises: 
Create Date: 2026-02-06 12:25:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '001'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create teaching_offices table
    op.create_table(
        'teaching_offices',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('code', sa.String(length=50), nullable=False),
        sa.Column('department', sa.String(length=255), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('code')
    )
    op.create_index('ix_teaching_offices_code', 'teaching_offices', ['code'], unique=False)

    # Create users table
    op.create_table(
        'users',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('username', sa.String(length=100), nullable=False),
        sa.Column('password_hash', sa.String(length=255), nullable=False),
        sa.Column('role', sa.String(length=50), nullable=False),
        sa.Column('teaching_office_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('email', sa.String(length=255), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['teaching_office_id'], ['teaching_offices.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('username')
    )
    op.create_index('ix_users_username', 'users', ['username'], unique=False)

    # Create self_evaluations table
    op.create_table(
        'self_evaluations',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('teaching_office_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('evaluation_year', sa.Integer(), nullable=False),
        sa.Column('content', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column('status', sa.String(length=50), nullable=False),
        sa.Column('submitted_at', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['teaching_office_id'], ['teaching_offices.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('teaching_office_id', 'evaluation_year', name='uq_teaching_office_year')
    )
    op.create_index('ix_self_evaluations_teaching_office_id', 'self_evaluations', ['teaching_office_id'], unique=False)
    op.create_index('ix_self_evaluations_evaluation_year', 'self_evaluations', ['evaluation_year'], unique=False)

    # Create attachments table
    op.create_table(
        'attachments',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('evaluation_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('indicator', sa.String(length=255), nullable=False),
        sa.Column('file_name', sa.String(length=255), nullable=False),
        sa.Column('file_size', sa.BigInteger(), nullable=False),
        sa.Column('file_type', sa.String(length=100), nullable=True),
        sa.Column('storage_path', sa.String(length=500), nullable=False),
        sa.Column('classified_by', sa.String(length=20), nullable=False),
        sa.Column('uploaded_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['evaluation_id'], ['self_evaluations.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_attachments_evaluation_id', 'attachments', ['evaluation_id'], unique=False)

    # Create ai_scores table
    op.create_table(
        'ai_scores',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('evaluation_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('total_score', sa.Numeric(precision=5, scale=2), nullable=False),
        sa.Column('indicator_scores', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column('parsed_reform_projects', sa.Integer(), nullable=False),
        sa.Column('parsed_honorary_awards', sa.Integer(), nullable=False),
        sa.Column('scored_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['evaluation_id'], ['self_evaluations.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_ai_scores_evaluation_id', 'ai_scores', ['evaluation_id'], unique=False)

    # Create anomalies table
    op.create_table(
        'anomalies',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('evaluation_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('type', sa.String(length=50), nullable=False),
        sa.Column('indicator', sa.String(length=255), nullable=False),
        sa.Column('declared_count', sa.Integer(), nullable=True),
        sa.Column('parsed_count', sa.Integer(), nullable=True),
        sa.Column('description', sa.Text(), nullable=False),
        sa.Column('status', sa.String(length=20), nullable=False),
        sa.Column('handled_by', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('handled_action', sa.String(length=20), nullable=True),
        sa.Column('handled_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['evaluation_id'], ['self_evaluations.id'], ),
        sa.ForeignKeyConstraint(['handled_by'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_anomalies_evaluation_id', 'anomalies', ['evaluation_id'], unique=False)

    # Create manual_scores table
    op.create_table(
        'manual_scores',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('evaluation_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('reviewer_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('reviewer_name', sa.String(length=255), nullable=False),
        sa.Column('reviewer_role', sa.String(length=50), nullable=False),
        sa.Column('weight', sa.Numeric(precision=3, scale=2), nullable=False),
        sa.Column('scores', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column('submitted_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['evaluation_id'], ['self_evaluations.id'], ),
        sa.ForeignKeyConstraint(['reviewer_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_manual_scores_evaluation_id', 'manual_scores', ['evaluation_id'], unique=False)

    # Create final_scores table
    op.create_table(
        'final_scores',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('evaluation_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('final_score', sa.Numeric(precision=5, scale=2), nullable=False),
        sa.Column('summary', sa.Text(), nullable=True),
        sa.Column('determined_by', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('determined_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['determined_by'], ['users.id'], ),
        sa.ForeignKeyConstraint(['evaluation_id'], ['self_evaluations.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('evaluation_id')
    )

    # Create approvals table
    op.create_table(
        'approvals',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('evaluation_ids', postgresql.ARRAY(postgresql.UUID(as_uuid=True)), nullable=False),
        sa.Column('decision', sa.String(length=20), nullable=False),
        sa.Column('reject_reason', sa.Text(), nullable=True),
        sa.Column('approved_by', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('approved_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['approved_by'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

    # Create publications table
    op.create_table(
        'publications',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('evaluation_ids', postgresql.ARRAY(postgresql.UUID(as_uuid=True)), nullable=False),
        sa.Column('published_by', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('published_at', sa.DateTime(), nullable=False),
        sa.Column('distributed_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['published_by'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

    # Create insight_summaries table
    op.create_table(
        'insight_summaries',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('evaluation_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('summary', sa.Text(), nullable=False),
        sa.Column('generated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['evaluation_id'], ['self_evaluations.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('evaluation_id')
    )

    # Create operation_logs table
    op.create_table(
        'operation_logs',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('operation_type', sa.String(length=50), nullable=False),
        sa.Column('operator_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('operator_name', sa.String(length=255), nullable=False),
        sa.Column('operator_role', sa.String(length=50), nullable=False),
        sa.Column('target_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('target_type', sa.String(length=50), nullable=False),
        sa.Column('details', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('operated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['operator_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_operation_logs_operator_id', 'operation_logs', ['operator_id'], unique=False)
    op.create_index('ix_operation_logs_target_id', 'operation_logs', ['target_id'], unique=False)


def downgrade() -> None:
    # Drop tables in reverse order
    op.drop_index('ix_operation_logs_target_id', table_name='operation_logs')
    op.drop_index('ix_operation_logs_operator_id', table_name='operation_logs')
    op.drop_table('operation_logs')
    op.drop_table('insight_summaries')
    op.drop_table('publications')
    op.drop_table('approvals')
    op.drop_table('final_scores')
    op.drop_index('ix_manual_scores_evaluation_id', table_name='manual_scores')
    op.drop_table('manual_scores')
    op.drop_index('ix_anomalies_evaluation_id', table_name='anomalies')
    op.drop_table('anomalies')
    op.drop_index('ix_ai_scores_evaluation_id', table_name='ai_scores')
    op.drop_table('ai_scores')
    op.drop_index('ix_attachments_evaluation_id', table_name='attachments')
    op.drop_table('attachments')
    op.drop_index('ix_self_evaluations_evaluation_year', table_name='self_evaluations')
    op.drop_index('ix_self_evaluations_teaching_office_id', table_name='self_evaluations')
    op.drop_table('self_evaluations')
    op.drop_index('ix_users_username', table_name='users')
    op.drop_table('users')
    op.drop_index('ix_teaching_offices_code', table_name='teaching_offices')
    op.drop_table('teaching_offices')
