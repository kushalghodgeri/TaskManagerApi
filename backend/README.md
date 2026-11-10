# Task Manager REST API

A production-grade, secure, asynchronous REST API for personal and team task management built with **FastAPI**, **SQLAlchemy 2.0 ORM**, **SQLite**, **Pydantic v2**, and **JWT Authentication**.

---

## Architecture

```
                       +----------------------------------+
                       |          HTTP Clients            |
                       |    (Web, Mobile, cURL, etc.)     |
                       +----------------+-----------------+
                                        | HTTP / JSON / Bearer JWT
                                        v
                       +----------------------------------+
                       |        FastAPI Application       |
                       |    - CORS Middleware             |
                       |    - OpenAPI / Swagger Docs      |
                       +----------------+-----------------+
                                        |
                 +----------------------+----------------------+
                 |                      |                      |
                 v                      v                      v
       +-------------------+  +-------------------+  +-------------------+
       |   /auth Router    |  |   /users Router   |  |   /tasks Router   |
       |  - /register      |  |  - /me            |  |  - CRUD           |
       |  - /login         |  |                   |  |  - Filter & Sort  |
       +---------+---------+  +---------+---------+  +---------+---------+
                 |                      |                      |
                 +----------------------+----------------------+
                                        |
                                        v
                       +----------------------------------+
                       |        Dependency Injection      |
                       |  - get_db (SessionLocal)         |
                       |  - get_current_user (JWT Auth)   |
                       +----------------+-----------------+
                                        |
                 +----------------------+----------------------+
                 |                                             |
                 v                                             v
       +-------------------+                         +-------------------+
       |     CRUD Layer    |                         |  Security Module  |
       |  - crud/user.py   |                         |  - bcrypt hash/pw |
       |  - crud/task.py   |                         |  - PyJWT encode/dec|
       +---------+---------+                         +-------------------+
                 |
                 v
       +----------------------------------+
       |       SQLAlchemy 2.0 ORM         |
       |  - User Model (users table)      |
       |  - Task Model (tasks table)      |
       |  - Cascade Deletion & Foreign Keys|
       +----------------+-----------------+
                        |
                        v
       +----------------------------------+
       |         SQLite Database          |
       |       (tasks.db / :memory:)      |
       +----------------------------------+
```

---

## Features

- **Layered Clean Architecture**: Modular separation across configuration, security, database session, ORM models, Pydantic v2 schemas, CRUD operations, dependency injection, and API route handlers.
- **Secure Authentication**:
  - Direct `bcrypt` password hashing (no deprecated wrappers).
  - Standard OAuth2 password bearer flow with PyJWT token signing (`sub` = user ID, `exp` expiration).
  - Strict 401 response with `WWW-Authenticate: Bearer` on invalid/expired credentials.
- **Robust Multi-Tenant Task Isolation**:
  - Every task query is scoped to the authenticated user's ID (`owner_id == current_user.id`).
  - Accessing, modifying, or deleting another user's task returns `404 Not Found` (never leaks existence via `403`).
- **Rich Task Filtering, Searching, and Pagination**:
  - Filter by `status` (`todo`, `in_progress`, `done`) and `priority` (`low`, `medium`, `high`).
  - Substring search on task title.
  - Pagination envelope with `items`, `total`, `skip`, and `limit`.
  - Dynamic sorting by `created_at`, `due_date`, or `priority` in `asc` or `desc` order.
- **Interactive OpenAPI Documentation**: Auto-generated Swagger documentation at `/docs` and ReDoc at `/redoc` with comprehensive response schemas, descriptions, and examples.
- **100% Test Coverage**: Complete Pytest test suite with in-memory SQLite and `StaticPool`.

---

## Directory Structure

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py                # FastAPI app, CORS, router registration, table creation
│   ├── core/
│   │   ├── config.py          # pydantic-settings configuration
│   │   └── security.py        # bcrypt hashing, JWT issuance and decoding
│   ├── db/
│   │   ├── base.py            # SQLAlchemy 2.0 DeclarativeBase
│   │   └── session.py         # Engine (check_same_thread=False), SessionLocal, get_db
│   ├── models/
│   │   ├── __init__.py
│   │   ├── user.py            # User ORM model
│   │   └── task.py            # Task ORM model & Enums (TaskStatus, TaskPriority)
│   ├── schemas/
│   │   ├── __init__.py
│   │   ├── token.py           # Token & TokenPayload schemas
│   │   ├── user.py            # UserCreate, UserRead schemas
│   │   └── task.py            # TaskCreate, TaskUpdate, TaskRead, TaskPagination
│   ├── crud/
│   │   ├── __init__.py
│   │   ├── user.py            # User CRUD operations
│   │   └── task.py            # Task CRUD, filtering, search, pagination, sorting
│   └── api/
│       ├── __init__.py
│       ├── deps.py            # Dependency injection: get_db, get_current_user
│       └── routes/
│           ├── __init__.py
│           ├── auth.py        # /auth/register, /auth/login
│           ├── users.py       # /users/me
│           └── tasks.py       # /tasks CRUD & query endpoints
├── tests/
│   ├── conftest.py            # SQLite in-memory fixtures, TestClient, user auth fixtures
│   ├── test_auth.py           # Auth, user profile, and token tests
│   ├── test_tasks.py          # Task CRUD, isolation, pagination, sorting, cascading tests
│   └── test_core.py           # Config parsing and session generator tests
├── scripts/
│   └── verify_live.py         # End-to-end live server validation script
├── .env.example
├── .gitignore
├── pytest.ini
├── requirements.txt
└── README.md
```

---

## Environment Variables

Configuration is loaded from environment variables or a `.env` file via `pydantic-settings`:

| Variable | Type | Default | Description |
| :--- | :--- | :--- | :--- |
| `SECRET_KEY` | `str` | `default-dev-secret-key-...` | Secret cryptographic key for JWT signing. |
| `ALGORITHM` | `str` | `HS256` | JWT signing algorithm. |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | `int` | `30` | JWT token validity window in minutes. |
| `DATABASE_URL` | `str` | `sqlite:///./tasks.db` | SQLAlchemy database connection string. |
| `CORS_ORIGINS` | `list[str]` | `["http://localhost:5173"]` | Allowed CORS origins (JSON array or comma-separated). |

---

## Setup & Installation

### 1. Prerequisites
- Python 3.11+
- Git

### 2. Clone and navigate to backend directory
```bash
git clone <repo-url>
cd "backend"
```

### 3. Create a virtual environment & install dependencies
```bash
# On Linux/macOS:
python3 -m venv venv
source venv/bin/activate

# On Windows:
python -m venv venv
venv\Scripts\activate

# Install requirements:
pip install -r requirements.txt
```

### 4. Configure environment variables
```bash
cp .env.example .env
```

---

## Running the Application

Start the development server with Uvicorn:

```bash
uvicorn app.main:app --reload
```

The API will be accessible at:
- **API Base**: `http://localhost:8000`
- **Interactive Swagger Docs**: `http://localhost:8000/docs`
- **ReDoc Documentation**: `http://localhost:8000/redoc`
- **Health Check**: `http://localhost:8000/health`

---

## API Endpoints

| Method | Endpoint | Auth | Description | Status Codes |
| :--- | :--- | :---: | :--- | :--- |
| `GET` | `/health` | No | Service health check | `200` |
| `POST` | `/auth/register` | No | Register a new user | `201`, `409`, `422` |
| `POST` | `/auth/login` | No | Authenticate & get bearer JWT | `200`, `401` |
| `GET` | `/users/me` | Bearer | Get authenticated user profile | `200`, `401` |
| `POST` | `/tasks` | Bearer | Create a new task | `201`, `401`, `422` |
| `GET` | `/tasks` | Bearer | List tasks with filters, search, pagination, and sorting | `200`, `401` |
| `GET` | `/tasks/{id}` | Bearer | Get task by ID (own tasks only) | `200`, `401`, `404` |
| `PATCH` | `/tasks/{id}` | Bearer | Partially update a task (own tasks only) | `200`, `401`, `404`, `422` |
| `DELETE` | `/tasks/{id}` | Bearer | Delete a task (own tasks only) | `204`, `401`, `404` |

---

## Example cURL Commands

### 1. Register a new user
```bash
curl -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "alice@example.com",
    "username": "alice_dev",
    "password": "Password123!"
  }'
```

### 2. Login to receive JWT access token
```bash
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=alice@example.com&password=Password123!"
```
*Response:*
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

### 3. Get current user profile
```bash
curl -X GET http://localhost:8000/users/me \
  -H "Authorization: Bearer <TOKEN>"
```

### 4. Create a new task
```bash
curl -X POST http://localhost:8000/tasks \
  -H "Authorization: Bearer <TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Build REST API",
    "description": "Implement authentication and CRUD endpoints",
    "status": "in_progress",
    "priority": "high",
    "due_date": "2026-12-31T23:59:59Z"
  }'
```

### 5. List tasks with filtering, search, and pagination
```bash
curl -X GET "http://localhost:8000/tasks?status=in_progress&priority=high&search=API&skip=0&limit=10&sort_by=due_date&order=asc" \
  -H "Authorization: Bearer <TOKEN>"
```

### 6. Partially update a task
```bash
curl -X PATCH http://localhost:8000/tasks/1 \
  -H "Authorization: Bearer <TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{
    "status": "done"
  }'
```

### 7. Delete a task
```bash
curl -X DELETE http://localhost:8000/tasks/1 \
  -H "Authorization: Bearer <TOKEN>"
```

---

## Running the Test Suite

The test suite runs with an isolated in-memory SQLite database (`StaticPool`) ensuring no leftover state.

```bash
# Run pytest with code coverage:
pytest --cov=app --cov-report=term-missing
```

Coverage report output:
```
Name                              Stmts   Miss  Cover   Missing
-------------------------------------------------------------
backend\app\__init__.py             0      0   100%
backend\app\api\__init__.py         0      0   100%
backend\app\api\deps.py            28      0   100%
backend\app\api\routes\auth.py     22      0   100%
backend\app\api\routes\tasks.py    38      0   100%
backend\app\api\routes\users.py     8      0   100%
backend\app\core\config.py         23      0   100%
backend\app\core\security.py       23      0   100%
backend\app\crud\__init__.py        3      0   100%
backend\app\crud\task.py           34      0   100%
backend\app\crud\user.py           21      0   100%
backend\app\db\base.py              3      0   100%
backend\app\db\session.py          12      0   100%
backend\app\models\__init__.py      3      0   100%
backend\app\models\task.py         24      0   100%
backend\app\models\user.py         12      0   100%
backend\app\schemas\__init__.py     4      0   100%
backend\app\schemas\task.py        27      0   100%
backend\app\schemas\token.py        8      0   100%
backend\app\schemas\user.py        13      0   100%
-------------------------------------------------------------
TOTAL                             302      0   100%
```
