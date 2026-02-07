"""add version fields for optimistic locking

Revision ID: 005
Revises: 004
Create Date: 2026-02-06

任务 22.1: 添加版本字段用于乐观锁并发控制
"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '005'
down_revision = '004'
branch_labels = None
depends_on = None


def upgrade():
    """添加版本字段到需要并发控制的表"""
    
    # 为 self_evaluations 表添加 version 字段
    op.add_column('self_evaluations', 
        sa.Column('version', sa.Integer(), nullable=False, server_default='1')
    )
    
    # 为 final_scores 表添加 version 字段
    op.add_column('final_scores', 
        sa.Column('version', sa.Integer(), nullable=False, server_default='1')
    )


def downgrade():
    """移除版本字段"""
    
    op.drop_column('final_scores', 'version')
    op.drop_column('self_evaluations', 'version')
