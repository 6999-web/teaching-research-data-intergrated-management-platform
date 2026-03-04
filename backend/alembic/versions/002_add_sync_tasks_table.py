"""Add sync_tasks table

Revision ID: 002
Revises: 001
Create Date: 2026-02-06 14:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '002'
down_revision: Union[str, None] = '001'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create sync_tasks table
    op.create_table(
        'sync_tasks',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('evaluation_ids', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column('status', sa.String(length=20), nullable=False),
        sa.Column('synced_count', sa.Integer(), nullable=False),
        sa.Column('failed_count', sa.Integer(), nullable=False),
        sa.Column('total_count', sa.Integer(), nullable=False),
        sa.Column('started_at', sa.DateTime(), nullable=False),
        sa.Column('completed_at', sa.DateTime(), nullable=True),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('retry_count', sa.Integer(), nullable=False),
        sa.Column('checksum', sa.String(length=64), nullable=True),
        sa.Column('sync_data', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_sync_tasks_status', 'sync_tasks', ['status'], unique=False)
    op.create_index('ix_sync_tasks_started_at', 'sync_tasks', ['started_at'], unique=False)


def downgrade() -> None:
    op.drop_index('ix_sync_tasks_started_at', table_name='sync_tasks')
    op.drop_index('ix_sync_tasks_status', table_name='sync_tasks')
    op.drop_table('sync_tasks')
