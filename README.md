# Full-Stack Task Manager REST API & Web Application

A complete, production-grade Task Management application with an asynchronous **FastAPI** backend and a responsive **React 18 + Vite** frontend.

---

## Architecture Overview

```
                                      +------------------------------------+
                                      |         React 18 Frontend          |
                                      |    (Vite, Tailwind CSS, TS)        |
                                      |     http://localhost:5173          |
                                      +-----------------+------------------+
                                                        |
                                                        | REST API Requests (Axios)
                                                        | Bearer JWT Authentication
                                                        v
                                      +------------------------------------+
                                      |         FastAPI Backend            |
                                      |   (Python 3.11+, SQLAlchemy 2.0)   |
                                      |     http://localhost:8000          |
                                      +-----------------+------------------+
                                                        |
                                                        v
                                      +------------------------------------+
                                      |         SQLite Database            |
                                      |           (tasks.db)               |
                                      +------------------------------------+
```

---

## Quick Start Guide

### 1. Start the Backend API
In a terminal window:
```bash
cd backend

# Create and activate virtual environment
# Windows:
python -m venv venv
.\venv\Scripts\activate

# Linux/macOS:
python3 -m venv venv
source venv/bin/activate

# Install dependencies and start server
pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --reload
```
- **Backend API**: `http://localhost:8000`
- **Swagger Documentation**: `http://localhost:8000/docs`
- **Health Check**: `http://localhost:8000/health`

### 2. Start the Frontend Application
In a separate terminal window:
```bash
cd frontend

# Install dependencies and run development server
npm install
npm run dev
```
- **Web Application**: `http://localhost:5173`

---

## Running Automated Tests

```bash
# Run backend test suite with coverage report (100% coverage target)
cd backend
pytest --cov=app --cov-report=term-missing

# Build frontend and verify TypeScript types
cd ../frontend
npm run build
```

---

## Detailed Documentation
- [Backend Documentation (`backend/README.md`)](backend/README.md)
- [Frontend Documentation (`frontend/README.md`)](frontend/README.md)
