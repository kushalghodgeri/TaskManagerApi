from collections.abc import Generator
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.api.deps import get_db
from app.db.base import Base
from app.main import app

# In-memory SQLite engine using StaticPool for thread-safe test isolation
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

test_engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)


@pytest.fixture(scope="function")
def db_session() -> Generator[Session, None, None]:
    """Create fresh database tables for each test and provide a session."""
    Base.metadata.create_all(bind=test_engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=test_engine)


@pytest.fixture(scope="function")
def client(db_session: Session) -> Generator[TestClient, None, None]:
    """TestClient with overridden get_db dependency."""
    def override_get_db() -> Generator[Session, None, None]:
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture
def test_user_data() -> dict[str, str]:
    """Sample user data for the primary test user."""
    return {
        "email": "user1@example.com",
        "username": "userone",
        "password": "Password123!",
    }


@pytest.fixture
def second_user_data() -> dict[str, str]:
    """Sample user data for a second test user."""
    return {
        "email": "user2@example.com",
        "username": "usertwo",
        "password": "Password456!",
    }


@pytest.fixture
def auth_headers(client: TestClient, test_user_data: dict[str, str]) -> dict[str, str]:
    """Register primary user, authenticate, and return authorization headers."""
    reg_res = client.post("/auth/register", json=test_user_data)
    assert reg_res.status_code == 201

    login_res = client.post(
        "/auth/login",
        data={"username": test_user_data["email"], "password": test_user_data["password"]},
    )
    assert login_res.status_code == 200
    token = login_res.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def second_auth_headers(client: TestClient, second_user_data: dict[str, str]) -> dict[str, str]:
    """Register second user, authenticate, and return authorization headers."""
    reg_res = client.post("/auth/register", json=second_user_data)
    assert reg_res.status_code == 201

    login_res = client.post(
        "/auth/login",
        data={"username": second_user_data["email"], "password": second_user_data["password"]},
    )
    assert login_res.status_code == 200
    token = login_res.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}
