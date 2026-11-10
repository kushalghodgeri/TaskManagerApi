# Task Manager REST API

A production-style Task Manager REST API built with Python 3.11+, FastAPI, SQLite, SQLAlchemy 2.0 ORM, Pydantic v2, and JWT authentication.

Detailed documentation and setup guides are located in [`backend/README.md`](backend/README.md).

## Quick Start
```bash
cd backend
python -m venv venv
# Linux/macOS:
source venv/bin/activate
# Windows:
venv\Scripts\activate

pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --reload
```

## Running Tests
```bash
cd backend
pytest --cov=app --cov-report=term-missing
```
