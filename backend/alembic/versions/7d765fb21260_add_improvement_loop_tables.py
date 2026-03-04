"""add_improvement_loop_tables

Revision ID: 7d765fb21260
Revises: 005
Create Date: 2026-02-07 21:01:54.167194

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '7d765fb21260'
down_revision = '005'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create colleges table
    op.create_table(
        'colleges',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('dean_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name')
    )
    # Use explicit name for FK to avoid ambiguity during downgrade
    op.create_foreign_key('fk_colleges_users_dean_id', 'colleges', 'users', ['dean_id'], ['id'])

    # Add columns to users
    op.add_column('users', sa.Column('college_id', postgresql.UUID(as_uuid=True), nullable=True))
    op.create_foreign_key('fk_users_colleges_college_id', 'users', 'colleges', ['college_id'], ['id'])

    # Add columns to teaching_offices
    op.add_column('teaching_offices', sa.Column('college_id', postgresql.UUID(as_uuid=True), nullable=True))
    op.create_foreign_key('fk_teaching_offices_colleges_college_id', 'teaching_offices', 'colleges', ['college_id'], ['id'])

    # Create improvement_plans table
    op.create_table(
        'improvement_plans',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('evaluation_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('indicator_item_id', sa.Integer(), nullable=False),
        sa.Column('target', sa.Text(), nullable=False),
        sa.Column('measures', sa.Text(), nullable=False),
        sa.Column('charger_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('deadline', sa.DateTime(), nullable=False),
        sa.Column('status', sa.Enum('PENDING', 'APPROVED', 'REJECTED', 'COMPLETED', name='improvementplanstatus'), nullable=False),
        sa.Column('supervisor_comment', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['evaluation_id'], ['self_evaluations.id'], ),
        sa.ForeignKeyConstraint(['charger_id'], ['users.id'], )
    )


def downgrade() -> None:
    op.drop_table('improvement_plans')
    op.drop_constraint('fk_teaching_offices_colleges_college_id', 'teaching_offices', type_='foreignkey')
    op.drop_column('teaching_offices', 'college_id')
    op.drop_constraint('fk_users_colleges_college_id', 'users', type_='foreignkey')
    op.drop_column('users', 'college_id')
    op.drop_constraint('fk_colleges_users_dean_id', 'colleges', type_='foreignkey')
    op.drop_table('colleges')
