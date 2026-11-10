"""Verification script to test live Uvicorn server, /docs, and end-to-end flow."""
import time
import threading
import httpx
import uvicorn
import sys
import os

# Ensure backend folder is on python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from app.main import app

PORT = 8765
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


def main():
    server_thread = ServerThread()
    server_thread.start()

    # Wait for server to start up
    time.sleep(1.5)

    try:
        with httpx.Client(base_url=BASE_URL, timeout=5.0) as client:
            print("1. Testing GET /docs...")
            res_docs = client.get("/docs")
            assert res_docs.status_code == 200, f"/docs failed: {res_docs.status_code}"
            print("   -> /docs responded 200 OK")

            print("2. Testing GET /health...")
            res_health = client.get("/health")
            assert res_health.status_code == 200, f"/health failed: {res_health.status_code}"
            assert res_health.json() == {"status": "ok"}
            print("   -> /health responded 200 OK:", res_health.json())

            print("3. Testing POST /auth/register...")
            user_data = {
                "email": f"live_test_{int(time.time())}@example.com",
                "username": f"live_user_{int(time.time())}"[:30],
                "password": "StrongPassword123!",
            }
            res_reg = client.post("/auth/register", json=user_data)
            assert res_reg.status_code == 201, f"/auth/register failed: {res_reg.text}"
            user_info = res_reg.json()
            print("   -> Registered user:", user_info["email"], f"(id={user_info['id']})")

            print("4. Testing POST /auth/login...")
            res_login = client.post(
                "/auth/login",
                data={"username": user_data["email"], "password": user_data["password"]},
            )
            assert res_login.status_code == 200, f"/auth/login failed: {res_login.text}"
            token = res_login.json()["access_token"]
            print("   -> Login successful! Token type:", res_login.json()["token_type"])

            headers = {"Authorization": f"Bearer {token}"}

            print("5. Testing GET /users/me...")
            res_me = client.get("/users/me", headers=headers)
            assert res_me.status_code == 200
            print("   -> /users/me returned:", res_me.json()["username"])

            print("6. Testing POST /tasks...")
            task_data = {
                "title": "Production Deployment Verification",
                "description": "Verify that live uvicorn server handles requests cleanly",
                "status": "in_progress",
                "priority": "high",
            }
            res_task = client.post("/tasks", json=task_data, headers=headers)
            assert res_task.status_code == 201, f"/tasks create failed: {res_task.text}"
            task = res_task.json()
            print("   -> Task created:", task["title"], f"(id={task['id']}, status={task['status']})")

            print("7. Testing GET /tasks...")
            res_tasks = client.get("/tasks", headers=headers)
            assert res_tasks.status_code == 200
            envelope = res_tasks.json()
            assert envelope["total"] >= 1
            print(f"   -> GET /tasks envelope verified: total={envelope['total']}, items count={len(envelope['items'])}")

        print("\nALL LIVE SERVER CHECKS PASSED SUCCESSFULLY!")
    finally:
        server_thread.stop()


if __name__ == "__main__":
    main()
