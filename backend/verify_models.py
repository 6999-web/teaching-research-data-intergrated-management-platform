"""
Verification script for database models
Checks that all models are properly defined and can be imported
"""

import sys
from app.models import (
    TeachingOffice,
    SelfEvaluation,
    Attachment,
    AIScore,
    Anomaly,
    ManualScore,
    FinalScore,
    Approval,
    Publication,
    InsightSummary,
    OperationLog,
    User,
)
from app.db.base import Base

def verify_models():
    """Verify all models are properly defined"""
    
    models = [
        TeachingOffice,
        SelfEvaluation,
        Attachment,
        AIScore,
        Anomaly,
        ManualScore,
        FinalScore,
        Approval,
        Publication,
        InsightSummary,
        OperationLog,
        User,
    ]
    
    print("=" * 60)
    print("Database Models Verification")
    print("=" * 60)
    print()
    
    print(f"Total models defined: {len(models)}")
    print()
    
    print("Models and their tables:")
    print("-" * 60)
    for model in models:
        print(f"  {model.__name__:25} -> {model.__tablename__}")
    print()
    
    print("Checking Base.metadata:")
    print("-" * 60)
    print(f"  Total tables in metadata: {len(Base.metadata.tables)}")
    print(f"  Tables: {', '.join(Base.metadata.tables.keys())}")
    print()
    
    print("Checking relationships:")
    print("-" * 60)
    for model in models:
        relationships = []
        for attr_name in dir(model):
            attr = getattr(model, attr_name)
            if hasattr(attr, 'property') and hasattr(attr.property, 'mapper'):
                relationships.append(attr_name)
        if relationships:
            print(f"  {model.__name__}: {', '.join(relationships)}")
    print()
    
    print("✓ All models verified successfully!")
    print("=" * 60)
    
    return True

if __name__ == "__main__":
    try:
        verify_models()
        sys.exit(0)
    except Exception as e:
        print(f"✗ Verification failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
