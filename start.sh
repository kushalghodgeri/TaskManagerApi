#!/usr/bin/env bash
set -e

echo "Starting Task Manager Full-Stack Application..."

# Trap CTRL+C to kill background processes on exit
trap 'kill 0' SIGINT SIGTERM EXIT

# Start backend
cd backend
source venv/bin/activate || source venv/Scripts/activate
uvicorn app.main:app --reload --port 8000 &
BACKEND_PID=$!
cd ..

# Start frontend
cd frontend
npm run dev &
FRONTEND_PID=$!
cd ..

echo "Backend running on http://localhost:8000"
echo "Frontend running on http://localhost:5173"

wait
