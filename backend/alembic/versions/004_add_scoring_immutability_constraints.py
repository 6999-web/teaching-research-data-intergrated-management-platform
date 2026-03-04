"""Add immutability constraints for scoring records

Revision ID: 004
Revises: 003
Create Date: 2026-02-06 14:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '004'
down_revision: Union[str, None] = '003'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """
    Add immutability constraints for scoring records.
    
    需求 19.1, 19.2, 19.3, 19.4:
    - 永久保留所有评审人打分记录
    - 永久保留AI评分记录
    - 永久保留管理端最终得分
    - 禁止篡改评分记录
    
    Implementation:
    - Add triggers to prevent UPDATE and DELETE on ai_scores, manual_scores, final_scores
    - These triggers will raise exceptions if any attempt is made to modify or delete records
    """
    
    # For SQLite (development/testing), we'll use application-level checks
    # For PostgreSQL (production), we can add database triggers
    
    # Check if we're using PostgreSQL
    conn = op.get_bind()
    if conn.dialect.name == 'postgresql':
        # Create trigger function to prevent updates
        op.execute("""
            CREATE OR REPLACE FUNCTION prevent_scoring_record_modification()
            RETURNS TRIGGER AS $$
            BEGIN
                RAISE EXCEPTION 'Scoring records are immutable and cannot be modified or deleted. Record type: %, ID: %', 
                    TG_TABLE_NAME, COALESCE(OLD.id, NEW.id);
                RETURN NULL;
            END;
            $$ LANGUAGE plpgsql;
        """)
        
        # Add triggers to ai_scores table
        op.execute("""
            CREATE TRIGGER prevent_ai_scores_update
            BEFORE UPDATE ON ai_scores
            FOR EACH ROW
            EXECUTE FUNCTION prevent_scoring_record_modification();
        """)
        
        op.execute("""
            CREATE TRIGGER prevent_ai_scores_delete
            BEFORE DELETE ON ai_scores
            FOR EACH ROW
            EXECUTE FUNCTION prevent_scoring_record_modification();
        """)
        
        # Add triggers to manual_scores table
        op.execute("""
            CREATE TRIGGER prevent_manual_scores_update
            BEFORE UPDATE ON manual_scores
            FOR EACH ROW
            EXECUTE FUNCTION prevent_scoring_record_modification();
        """)
        
        op.execute("""
            CREATE TRIGGER prevent_manual_scores_delete
            BEFORE DELETE ON manual_scores
            FOR EACH ROW
            EXECUTE FUNCTION prevent_scoring_record_modification();
        """)
        
        # Add triggers to final_scores table
        op.execute("""
            CREATE TRIGGER prevent_final_scores_update
            BEFORE UPDATE ON final_scores
            FOR EACH ROW
            EXECUTE FUNCTION prevent_scoring_record_modification();
        """)
        
        op.execute("""
            CREATE TRIGGER prevent_final_scores_delete
            BEFORE DELETE ON final_scores
            FOR EACH ROW
            EXECUTE FUNCTION prevent_scoring_record_modification();
        """)


def downgrade() -> None:
    """Remove immutability constraints."""
    
    conn = op.get_bind()
    if conn.dialect.name == 'postgresql':
        # Drop triggers
        op.execute("DROP TRIGGER IF EXISTS prevent_ai_scores_update ON ai_scores;")
        op.execute("DROP TRIGGER IF EXISTS prevent_ai_scores_delete ON ai_scores;")
        op.execute("DROP TRIGGER IF EXISTS prevent_manual_scores_update ON manual_scores;")
        op.execute("DROP TRIGGER IF EXISTS prevent_manual_scores_delete ON manual_scores;")
        op.execute("DROP TRIGGER IF EXISTS prevent_final_scores_update ON final_scores;")
        op.execute("DROP TRIGGER IF EXISTS prevent_final_scores_delete ON final_scores;")
        
        # Drop trigger function
        op.execute("DROP FUNCTION IF EXISTS prevent_scoring_record_modification();")
