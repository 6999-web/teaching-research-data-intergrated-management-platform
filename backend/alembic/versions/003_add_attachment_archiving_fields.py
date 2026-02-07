"""add attachment archiving fields

Revision ID: 003
Revises: 002
Create Date: 2024-01-20 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from datetime import datetime


# revision identifiers, used by Alembic.
revision = '003'
down_revision = '002'
branch_labels = None
depends_on = None


def upgrade():
    # Add archiving fields to attachments table
    op.add_column('attachments', sa.Column('is_archived', sa.Boolean(), nullable=False, server_default='true'))
    op.add_column('attachments', sa.Column('archived_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')))
    
    # Add index on indicator for faster queries
    op.create_index('ix_attachments_indicator', 'attachments', ['indicator'])
    
    # Add unique constraint on storage_path to prevent duplicates
    op.create_unique_constraint('uq_attachments_storage_path', 'attachments', ['storage_path'])


def downgrade():
    # Remove unique constraint
    op.drop_constraint('uq_attachments_storage_path', 'attachments', type_='unique')
    
    # Remove index
    op.drop_index('ix_attachments_indicator', 'attachments')
    
    # Remove archiving fields
    op.drop_column('attachments', 'archived_at')
    op.drop_column('attachments', 'is_archived')
