"""Simulate and verify the complete frontend user journey against the live backend API."""
import os
import sys
import threading
import time
import httpx
import uvicorn

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from app.main import app

PORT = 8999
BASE_URL = f"http://127.0.0.1:{PORT}"


class ServerThread(threading.Thread):
    def __init__(self):
        super().__init__(daemon=True)
        config = uvicorn.Config(app=app, host="127.0.0.1", port=PORT, log_level="warning")
        self.server = uvicorn.Server(config=config)

    def run(self):
        self.server.run()

    def stop(self):
        self.server.should_exit = True


def test_frontend_flow():
    server = ServerThread()
    server.start()
    time.sleep(1.5)

    try:
        with httpx.Client(base_url=BASE_URL, timeout=5.0) as client:
            timestamp = int(time.time())
            email = f"frontend_user_{timestamp}@example.com"
            username = f"fe_user_{timestamp}"[:30]
            password = "SecurePassword123!"

            # 1. Register
            print("Step 1: Registering user via POST /auth/register...")
            res_reg = client.post(
                "/auth/register",
                json={"email": email, "username": username, "password": password},
            )
            assert res_reg.status_code == 201, f"Register failed: {res_reg.text}"
            print("   -> Registered successfully:", res_reg.json()["username"])

            # 2. Login (URL-encoded form per frontend auth.ts)
            print("Step 2: Logging in via POST /auth/login with x-www-form-urlencoded...")
            res_login = client.post(
                "/auth/login",
                data={"username": email, "password": password},
                headers={"Content-Type": "application/x-www-form-urlencoded"},
            )
            assert res_login.status_code == 200, f"Login failed: {res_login.text}"
            token = res_login.json()["access_token"]
            assert token, "No token returned"
            headers = {"Authorization": f"Bearer {token}"}
            print("   -> Login successful! Token received.")

            # 3. GET /users/me
            print("Step 3: Fetching user profile via GET /users/me...")
            res_me = client.get("/users/me", headers=headers)
            assert res_me.status_code == 200
            assert res_me.json()["email"] == email
            print("   -> Profile verified:", res_me.json()["email"])

            # 4. Create task
            print("Step 4: Creating task via POST /tasks...")
            res_task = client.post(
                "/tasks",
                json={
                    "title": "Design System Implementation",
                    "description": "Build Tailwind responsive components",
                    "status": "todo",
                    "priority": "high",
                    "due_date": "2026-12-31T18:00:00Z",
                },
                headers=headers,
            )
            assert res_task.status_code == 201
            task = res_task.json()
            task_id = task["id"]
            print(f"   -> Task created! (id={task_id}, status={task['status']})")

            # 5. Partial update via PATCH /tasks/{id}
            print(f"Step 5: Updating task via PATCH /tasks/{task_id}...")
            res_patch = client.patch(
                f"/tasks/{task_id}",
                json={"description": "Updated description with subtasks"},
                headers=headers,
            )
            assert res_patch.status_code == 200
            assert res_patch.json()["description"] == "Updated description with subtasks"
            print("   -> Task updated successfully!")

            # 6. Cycle status: todo -> in_progress -> done
            print(f"Step 6: Quick-cycling task status...")
            res_cycle1 = client.patch(
                f"/tasks/{task_id}",
                json={"status": "in_progress"},
                headers=headers,
            )
            assert res_cycle1.status_code == 200 and res_cycle1.json()["status"] == "in_progress"

            res_cycle2 = client.patch(
                f"/tasks/{task_id}",
                json={"status": "done"},
                headers=headers,
            )
            assert res_cycle2.status_code == 200 and res_cycle2.json()["status"] == "done"
            print("   -> Status cycled to in_progress and then done!")

            # 7. List and filter tasks
            print("Step 7: Testing filters, search, and pagination via GET /tasks...")
            res_list = client.get(
                "/tasks?status=done&search=Design&skip=0&limit=10&sort_by=priority&order=desc",
                headers=headers,
            )
            assert res_list.status_code == 200
            envelope = res_list.json()
            assert envelope["total"] >= 1
            assert any(t["id"] == task_id for t in envelope["items"])
            print(f"   -> Filter returned {envelope['total']} task(s), verified item match!")

            # 8. Delete task
            print(f"Step 8: Deleting task via DELETE /tasks/{task_id}...")
            res_del = client.delete(f"/tasks/{task_id}", headers=headers)
            assert res_del.status_code == 204
            print("   -> Task deleted (204 No Content)")

            # 9. Confirm deletion
            res_get_del = client.get(f"/tasks/{task_id}", headers=headers)
            assert res_get_del.status_code == 404
            print("   -> Confirmed deletion: GET returned 404 Not Found")

            # 10. Logout simulation: missing/cleared token returns 401
            print("Step 10: Simulating logout (unauthenticated request)...")
            res_unauth = client.get("/tasks")
            assert res_unauth.status_code == 401
            print("   -> Unauthorized request properly rejected with 401.")

        print("\n=== ALL FRONTEND INTEGRATION FLOW STEPS PASSED SUCCESSFULLY! ===")
    finally:
        server.stop()


if __name__ == "__main__":
    test_frontend_flow()
