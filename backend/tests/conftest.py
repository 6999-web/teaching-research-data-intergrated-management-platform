import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.db.base import Base
from app.core.deps import get_db  # Import from deps, not db.base
from app.models.user import User
from app.core.security import get_password_hash, create_access_token

# Test database URL
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="function")
def db():
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="function")
def client(db):
    def override_get_db():
        try:
            yield db
        finally:
            pass
    
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()

@pytest.fixture(scope="function")
def teaching_office_user(db):
    """Create a teaching office user for testing."""
    user = User(
        username="teaching_office_user",
        password_hash=get_password_hash("password123"),
        role="teaching_office",
        name="Teaching Office User",
        email="teaching@test.com"
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

@pytest.fixture(scope="function")
def evaluation_team_user(db):
    """Create an evaluation team user for testing."""
    user = User(
        username="evaluation_team_user",
        password_hash=get_password_hash("password123"),
        role="evaluation_team",
        name="Evaluation Team User",
        email="team@test.com"
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

@pytest.fixture(scope="function")
def evaluation_office_user(db):
    """Create an evaluation office user for testing."""
    user = User(
        username="evaluation_office_user",
        password_hash=get_password_hash("password123"),
        role="evaluation_office",
        name="Evaluation Office User",
        email="office@test.com"
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

@pytest.fixture(scope="function")
def president_office_user(db):
    """Create a president office user for testing."""
    user = User(
        username="president_office_user",
        password_hash=get_password_hash("password123"),
        role="president_office",
        name="President Office User",
        email="president@test.com"
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

@pytest.fixture(scope="function")
def teaching_office_token(teaching_office_user):
    """Create a JWT token for teaching office user."""
    return create_access_token({
        "sub": teaching_office_user.username,
        "user_id": str(teaching_office_user.id),
        "role": teaching_office_user.role
    })

@pytest.fixture(scope="function")
def evaluation_team_token(evaluation_team_user):
    """Create a JWT token for evaluation team user."""
    return create_access_token({
        "sub": evaluation_team_user.username,
        "user_id": str(evaluation_team_user.id),
        "role": evaluation_team_user.role
    })

@pytest.fixture(scope="function")
def evaluation_office_token(evaluation_office_user):
    """Create a JWT token for evaluation office user."""
    return create_access_token({
        "sub": evaluation_office_user.username,
        "user_id": str(evaluation_office_user.id),
        "role": evaluation_office_user.role
    })

@pytest.fixture(scope="function")
def president_office_token(president_office_user):
    """Create a JWT token for president office user."""
    return create_access_token({
        "sub": president_office_user.username,
        "user_id": str(president_office_user.id),
        "role": president_office_user.role
    })

@pytest.fixture(scope="function")
def test_teaching_office(db):
    """Create a test teaching office."""
    from app.models.teaching_office import TeachingOffice
    office = TeachingOffice(
        name="Test Teaching Office",
        code="TEST001",
        department="Computer Science"
    )
    db.add(office)
    db.commit()
    db.refresh(office)
    return office

@pytest.fixture(scope="function")
def test_evaluation(db, test_teaching_office):
    """Create a test self evaluation."""
    from app.models.self_evaluation import SelfEvaluation
    evaluation = SelfEvaluation(
        teaching_office_id=test_teaching_office.id,
        evaluation_year=2024,
        content={
            "teaching_process_management": "Good management",
            "course_construction": "Excellent courses",
            "teaching_reform_projects": 3,
            "honorary_awards": 2
        },
        status="submitted"
    )
    db.add(evaluation)
    db.commit()
    db.refresh(evaluation)
    return evaluation

@pytest.fixture(scope="function")
def test_reviewer(db):
    """Create a test reviewer user."""
    user = User(
        username="test_reviewer",
        password_hash=get_password_hash("password123"),
        role="evaluation_team",
        name="Test Reviewer",
        email="reviewer@test.com"
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user
