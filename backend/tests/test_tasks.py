from datetime import datetime, timezone
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.models.task import Task
from app.models.user import User


def test_create_task_success(client: TestClient, auth_headers: dict[str, str]):
    """Test creating a task returns 201 and TaskRead schema."""
    payload = {
        "title": "Write documentation",
        "description": "Comprehensive guides and OpenAPI docs",
        "status": "todo",
        "priority": "high",
        "due_date": "2026-12-31T23:59:59Z",
    }
    response = client.post("/tasks", json=payload, headers=auth_headers)
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == payload["title"]
    assert data["description"] == payload["description"]
    assert data["status"] == "todo"
    assert data["priority"] == "high"
    assert "id" in data
    assert "owner_id" in data
    assert "created_at" in data
    assert "updated_at" in data


def test_create_task_validation_failure(client: TestClient, auth_headers: dict[str, str]):
    """Test validation failure for empty title, title too long, invalid enums."""
    # Empty title
    res_empty = client.post("/tasks", json={"title": ""}, headers=auth_headers)
    assert res_empty.status_code == 422

    # Title exceeds 100 characters
    res_long = client.post("/tasks", json={"title": "A" * 101}, headers=auth_headers)
    assert res_long.status_code == 422

    # Invalid status
    res_status = client.post(
        "/tasks",
        json={"title": "Valid Title", "status": "invalid_status"},
        headers=auth_headers,
    )
    assert res_status.status_code == 422

    # Invalid priority
    res_prio = client.post(
        "/tasks",
        json={"title": "Valid Title", "priority": "urgent"},
        headers=auth_headers,
    )
    assert res_prio.status_code == 422


def test_list_tasks_pagination(client: TestClient, auth_headers: dict[str, str]):
    """Test listing tasks returns paginated envelope with skip, limit, total, items."""
    # Create 5 tasks
    for i in range(5):
        client.post(
            "/tasks",
            json={"title": f"Task {i+1}", "status": "todo"},
            headers=auth_headers,
        )

    # First page: skip=0, limit=2
    res = client.get("/tasks?skip=0&limit=2", headers=auth_headers)
    assert res.status_code == 200
    data = res.json()
    assert data["total"] == 5
    assert data["skip"] == 0
    assert data["limit"] == 2
    assert len(data["items"]) == 2

    # Second page: skip=2, limit=2
    res_page2 = client.get("/tasks?skip=2&limit=2", headers=auth_headers)
    assert res_page2.status_code == 200
    data2 = res_page2.json()
    assert data2["total"] == 5
    assert data2["skip"] == 2
    assert data2["limit"] == 2
    assert len(data2["items"]) == 2
    assert data2["items"][0]["id"] != data["items"][0]["id"]


def test_list_tasks_filtering(client: TestClient, auth_headers: dict[str, str]):
    """Test filtering tasks by status and priority."""
    client.post(
        "/tasks",
        json={"title": "Task 1", "status": "todo", "priority": "low"},
        headers=auth_headers,
    )
    client.post(
        "/tasks",
        json={"title": "Task 2", "status": "in_progress", "priority": "high"},
        headers=auth_headers,
    )
    client.post(
        "/tasks",
        json={"title": "Task 3", "status": "done", "priority": "high"},
        headers=auth_headers,
    )

    # Filter by status = in_progress
    res_status = client.get("/tasks?status=in_progress", headers=auth_headers)
    assert res_status.status_code == 200
    data_status = res_status.json()
    assert data_status["total"] == 1
    assert data_status["items"][0]["title"] == "Task 2"

    # Filter by priority = high
    res_prio = client.get("/tasks?priority=high", headers=auth_headers)
    assert res_prio.status_code == 200
    data_prio = res_prio.json()
    assert data_prio["total"] == 2

    # Filter by both status=done & priority=high
    res_both = client.get("/tasks?status=done&priority=high", headers=auth_headers)
    assert res_both.status_code == 200
    data_both = res_both.json()
    assert data_both["total"] == 1
    assert data_both["items"][0]["title"] == "Task 3"


def test_list_tasks_search(client: TestClient, auth_headers: dict[str, str]):
    """Test searching tasks by title substring (case-insensitive)."""
    client.post("/tasks", json={"title": "Buy groceries"}, headers=auth_headers)
    client.post("/tasks", json={"title": "Deploy API server"}, headers=auth_headers)
    client.post("/tasks", json={"title": "Review buy orders"}, headers=auth_headers)

    res = client.get("/tasks?search=buy", headers=auth_headers)
    assert res.status_code == 200
    data = res.json()
    assert data["total"] == 2
    titles = [item["title"] for item in data["items"]]
    assert "Buy groceries" in titles
    assert "Review buy orders" in titles
    assert "Deploy API server" not in titles


def test_list_tasks_sorting(client: TestClient, auth_headers: dict[str, str]):
    """Test sorting tasks by created_at, due_date, and priority in asc and desc."""
    client.post(
        "/tasks",
        json={
            "title": "Alpha Task",
            "priority": "low",
            "due_date": "2026-05-01T12:00:00Z",
        },
        headers=auth_headers,
    )
    client.post(
        "/tasks",
        json={
            "title": "Beta Task",
            "priority": "high",
            "due_date": "2026-10-01T12:00:00Z",
        },
        headers=auth_headers,
    )

    # Sort by created_at asc
    res_asc = client.get("/tasks?sort_by=created_at&order=asc", headers=auth_headers)
    assert res_asc.status_code == 200
    items_asc = res_asc.json()["items"]
    assert items_asc[0]["title"] == "Alpha Task"
    assert items_asc[1]["title"] == "Beta Task"

    # Sort by created_at desc
    res_desc = client.get("/tasks?sort_by=created_at&order=desc", headers=auth_headers)
    assert res_desc.status_code == 200
    items_desc = res_desc.json()["items"]
    assert items_desc[0]["title"] == "Beta Task"
    assert items_desc[1]["title"] == "Alpha Task"

    # Sort by due_date asc
    res_due = client.get("/tasks?sort_by=due_date&order=asc", headers=auth_headers)
    assert res_due.status_code == 200
    assert res_due.json()["items"][0]["title"] == "Alpha Task"

    # Sort by priority
    res_prio = client.get("/tasks?sort_by=priority&order=asc", headers=auth_headers)
    assert res_prio.status_code == 200


def test_get_own_task(client: TestClient, auth_headers: dict[str, str]):
    """Test retrieving an existing task owned by current user."""
    create_res = client.post("/tasks", json={"title": "My Task"}, headers=auth_headers)
    task_id = create_res.json()["id"]

    get_res = client.get(f"/tasks/{task_id}", headers=auth_headers)
    assert get_res.status_code == 200
    assert get_res.json()["id"] == task_id
    assert get_res.json()["title"] == "My Task"


def test_update_own_task(client: TestClient, auth_headers: dict[str, str]):
    """Test partial update (PATCH) of own task."""
    create_res = client.post(
        "/tasks",
        json={"title": "Original Title", "status": "todo", "priority": "low"},
        headers=auth_headers,
    )
    task_id = create_res.json()["id"]

    patch_res = client.patch(
        f"/tasks/{task_id}",
        json={"title": "Updated Title", "status": "in_progress"},
        headers=auth_headers,
    )
    assert patch_res.status_code == 200
    updated_data = patch_res.json()
    assert updated_data["title"] == "Updated Title"
    assert updated_data["status"] == "in_progress"
    assert updated_data["priority"] == "low"  # unchanged


def test_delete_own_task(client: TestClient, auth_headers: dict[str, str]):
    """Test deleting own task returns 204, subsequent GET returns 404."""
    create_res = client.post("/tasks", json={"title": "Task to delete"}, headers=auth_headers)
    task_id = create_res.json()["id"]

    delete_res = client.delete(f"/tasks/{task_id}", headers=auth_headers)
    assert delete_res.status_code == 204

    # Subsequent GET returns 404
    get_res = client.get(f"/tasks/{task_id}", headers=auth_headers)
    assert get_res.status_code == 404
    assert get_res.json()["detail"] == "Task not found"


def test_user_b_cannot_read_user_a_task(
    client: TestClient,
    auth_headers: dict[str, str],
    second_auth_headers: dict[str, str],
):
    """User B cannot read User A's task -> returns 404 (never 403)."""
    create_res = client.post("/tasks", json={"title": "User A Private Task"}, headers=auth_headers)
    task_id = create_res.json()["id"]

    # User B attempts to read User A's task
    response = client.get(f"/tasks/{task_id}", headers=second_auth_headers)
    assert response.status_code == 404
    assert response.json()["detail"] == "Task not found"


def test_user_b_cannot_update_user_a_task(
    client: TestClient,
    auth_headers: dict[str, str],
    second_auth_headers: dict[str, str],
):
    """User B cannot update User A's task -> returns 404 (never 403)."""
    create_res = client.post("/tasks", json={"title": "User A Private Task"}, headers=auth_headers)
    task_id = create_res.json()["id"]

    # User B attempts to update User A's task
    response = client.patch(
        f"/tasks/{task_id}",
        json={"title": "Malicious Tampering"},
        headers=second_auth_headers,
    )
    assert response.status_code == 404
    assert response.json()["detail"] == "Task not found"

    # Verify task title was unchanged
    verify_res = client.get(f"/tasks/{task_id}", headers=auth_headers)
    assert verify_res.json()["title"] == "User A Private Task"


def test_user_b_cannot_delete_user_a_task(
    client: TestClient,
    auth_headers: dict[str, str],
    second_auth_headers: dict[str, str],
):
    """User B cannot delete User A's task -> returns 404 (never 403)."""
    create_res = client.post("/tasks", json={"title": "User A Private Task"}, headers=auth_headers)
    task_id = create_res.json()["id"]

    # User B attempts to delete User A's task
    response = client.delete(f"/tasks/{task_id}", headers=second_auth_headers)
    assert response.status_code == 404
    assert response.json()["detail"] == "Task not found"

    # Verify task still exists for User A
    verify_res = client.get(f"/tasks/{task_id}", headers=auth_headers)
    assert verify_res.status_code == 200


def test_task_isolation_in_list(
    client: TestClient,
    auth_headers: dict[str, str],
    second_auth_headers: dict[str, str],
):
    """User B's task list must never include tasks created by User A."""
    client.post("/tasks", json={"title": "User A's Task"}, headers=auth_headers)
    client.post("/tasks", json={"title": "User B's Task"}, headers=second_auth_headers)

    res_a = client.get("/tasks", headers=auth_headers)
    assert res_a.status_code == 200
    assert res_a.json()["total"] == 1
    assert res_a.json()["items"][0]["title"] == "User A's Task"

    res_b = client.get("/tasks", headers=second_auth_headers)
    assert res_b.status_code == 200
    assert res_b.json()["total"] == 1
    assert res_b.json()["items"][0]["title"] == "User B's Task"


def test_cascade_delete_user_deletes_tasks(
    client: TestClient,
    db_session: Session,
    auth_headers: dict[str, str],
    test_user_data: dict[str, str],
):
    """Test that deleting a user deletes their associated tasks in cascade."""
    client.post("/tasks", json={"title": "Task 1 to be cascaded"}, headers=auth_headers)
    client.post("/tasks", json={"title": "Task 2 to be cascaded"}, headers=auth_headers)

    # Check tasks exist in DB
    tasks_count_before = db_session.query(Task).count()
    assert tasks_count_before == 2

    # Delete the user directly in DB
    user = db_session.query(User).filter(User.email == test_user_data["email"]).first()
    assert user is not None
    db_session.delete(user)
    db_session.commit()

    # Tasks should be deleted by cascade
    tasks_count_after = db_session.query(Task).count()
    assert tasks_count_after == 0
