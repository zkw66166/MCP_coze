#!/bin/bash

# Start Script for Dev Environment
# Run from project root: ./start_dev.sh

PROJECT_DIR="/var/www/MCP_coze"
cd "$PROJECT_DIR"

echo "Stopping existing services..."
pkill -f "uvicorn server.main:app" || true
pkill -f "vite" || true
sleep 2

echo "Starting deployment services..."

# 1. Start Backend
echo "Starting FastAPI Backend..."
source venv/bin/activate
export PYTHONPATH=$PROJECT_DIR
# Run in background, logging to backend.log
nohup uvicorn server.main:app --host 0.0.0.0 --port 8000 --reload > backend.log 2>&1 &
BACKEND_PID=$!
echo "Backend started with PID $BACKEND_PID (Logs: backend.log)"

# 2. Start Frontend
echo "Starting Vite Frontend..."
cd frontend
# Run in background, host 0.0.0.0 to allow external access
nohup npm run dev -- --host 0.0.0.0 --port 3000 > frontend.log 2>&1 &
FRONTEND_PID=$!
echo "Frontend started with PID $FRONTEND_PID (Logs: frontend/frontend.log)"

echo "=========================================="
echo "Services are running!"
echo "Backend: http://<YOUR_SERVER_IP>:8000"
echo "Frontend: http://<YOUR_SERVER_IP>:3000"
echo "To stop services, run: kill $BACKEND_PID $FRONTEND_PID"
echo "=========================================="
