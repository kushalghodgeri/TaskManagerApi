from datetime import timedelta
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.core.security import create_access_token
from app.crud.user import get_user_by_email


def test_health_check(client: TestClient):
    """Test health check endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_register_success(client: TestClient, test_user_data: dict[str, str]):
    """Test registering a new user returns 201 and UserRead model."""
    response = client.post("/auth/register", json=test_user_data)
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == test_user_data["email"]
    assert data["username"] == test_user_data["username"]
    assert data["is_active"] is True
    assert "id" in data
    assert "created_at" in data
    assert "password" not in data
    assert "hashed_password" not in data


def test_register_duplicate_email(client: TestClient, test_user_data: dict[str, str]):
    """Test registering with an existing email returns 409 Conflict."""
    client.post("/auth/register", json=test_user_data)
    dup_payload = {
        "email": test_user_data["email"],
        "username": "different_username",
        "password": "Password123!",
    }
    response = client.post("/auth/register", json=dup_payload)
    assert response.status_code == 409
    assert response.json()["detail"] == "Email already registered"


def test_register_duplicate_username(client: TestClient, test_user_data: dict[str, str]):
    """Test registering with an existing username returns 409 Conflict."""
    client.post("/auth/register", json=test_user_data)
    dup_payload = {
        "email": "different@example.com",
        "username": test_user_data["username"],
        "password": "Password123!",
    }
    response = client.post("/auth/register", json=dup_payload)
    assert response.status_code == 409
    assert response.json()["detail"] == "Username already taken"


def test_register_invalid_email(client: TestClient):
    """Test registering with an invalid email returns 422 Unprocessable Entity."""
    payload = {
        "email": "not-an-email",
        "username": "valid_user",
        "password": "ValidPassword123!",
    }
    response = client.post("/auth/register", json=payload)
    assert response.status_code == 422


def test_register_short_password(client: TestClient):
    """Test registering with a password shorter than 8 chars returns 422."""
    payload = {
        "email": "shortpass@example.com",
        "username": "shortpass_user",
        "password": "short",
    }
    response = client.post("/auth/register", json=payload)
    assert response.status_code == 422


def test_register_invalid_username(client: TestClient):
    """Test registering with invalid username formats returns 422."""
    # Too short (< 3 chars)
    res_short = client.post(
        "/auth/register",
        json={"email": "u1@example.com", "username": "ab", "password": "Password123!"},
    )
    assert res_short.status_code == 422

    # Disallowed characters (e.g. spaces, symbols)
    res_symbols = client.post(
        "/auth/register",
        json={"email": "u2@example.com", "username": "bad user!", "password": "Password123!"},
    )
    assert res_symbols.status_code == 422


def test_login_success_with_email(client: TestClient, test_user_data: dict[str, str]):
    """Test login with email returns access token."""
    client.post("/auth/register", json=test_user_data)
    response = client.post(
        "/auth/login",
        data={"username": test_user_data["email"], "password": test_user_data["password"]},
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_login_success_with_username(client: TestClient, test_user_data: dict[str, str]):
    """Test login with username also works."""
    client.post("/auth/register", json=test_user_data)
    response = client.post(
        "/auth/login",
        data={"username": test_user_data["username"], "password": test_user_data["password"]},
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_login_wrong_password(client: TestClient, test_user_data: dict[str, str]):
    """Test login with incorrect password returns 401 with WWW-Authenticate header."""
    client.post("/auth/register", json=test_user_data)
    response = client.post(
        "/auth/login",
        data={"username": test_user_data["email"], "password": "WrongPassword!"},
    )
    assert response.status_code == 401
    assert "WWW-Authenticate" in response.headers
    assert response.json()["detail"] == "Incorrect email or password"


def test_login_nonexistent_user(client: TestClient):
    """Test login with non-existent user returns 401."""
    response = client.post(
        "/auth/login",
        data={"username": "unknown@example.com", "password": "Password123!"},
    )
    assert response.status_code == 401


def test_get_current_user_success(
    client: TestClient,
    test_user_data: dict[str, str],
    auth_headers: dict[str, str],
):
    """Test getting /users/me with valid bearer token returns user profile."""
    response = client.get("/users/me", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == test_user_data["email"]
    assert data["username"] == test_user_data["username"]


def test_get_current_user_missing_token(client: TestClient):
    """Test accessing /users/me without token returns 401."""
    response = client.get("/users/me")
    assert response.status_code == 401


def test_get_current_user_invalid_token(client: TestClient):
    """Test accessing /users/me with malformed token returns 401."""
    response = client.get("/users/me", headers={"Authorization": "Bearer invalid.token.value"})
    assert response.status_code == 401
    assert "WWW-Authenticate" in response.headers


def test_get_current_user_expired_token(client: TestClient):
    """Test accessing /users/me with an expired token returns 401."""
    expired_token = create_access_token(
        subject="1",
        expires_delta=timedelta(seconds=-10),
    )
    response = client.get("/users/me", headers={"Authorization": f"Bearer {expired_token}"})
    assert response.status_code == 401


def test_get_current_user_nonexistent_id_in_token(client: TestClient):
    """Test token pointing to non-existent user ID returns 401."""
    token = create_access_token(subject="99999")
    response = client.get("/users/me", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 401
    assert response.json()["detail"] == "User not found"


def test_get_current_user_invalid_sub_format(client: TestClient):
    """Test token with non-integer subject string returns 401."""
    token = create_access_token(subject="not-an-int")
    response = client.get("/users/me", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 401


def test_get_current_user_inactive_account(
    client: TestClient,
    db_session: Session,
    auth_headers: dict[str, str],
    test_user_data: dict[str, str],
):
    """Test that an inactive user cannot access protected routes."""
    user = get_user_by_email(db_session, email=test_user_data["email"])
    assert user is not None
    user.is_active = False
    db_session.add(user)
    db_session.commit()

    response = client.get("/users/me", headers=auth_headers)
    assert response.status_code == 401
    assert response.json()["detail"] == "Inactive user account"
