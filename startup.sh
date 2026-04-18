#!/bin/bash

# Smart Stadium System - Automated Startup Script (Linux/Mac)
# Starts both backend and frontend services

set -e

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo ""
echo "╔════════════════════════════════════════════════════════════════╗"
echo "║       Smart Stadium System - Automated Startup                 ║"
echo "║       Backend + Frontend Services                              ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""

# Get project directory
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$PROJECT_DIR"

# Check Python
echo "[1/3] Checking Python environment..."
if [ ! -d ".venv" ]; then
    echo -e "${YELLOW}Creating virtual environment...${NC}"
    python3 -m venv .venv
fi

source .venv/bin/activate

echo -e "${GREEN}✓ Virtual environment activated${NC}"

# Install dependencies
if [ ! -f "requirements_frontend.txt" ]; then
    echo -e "${YELLOW}Installing dependencies...${NC}"
    pip install --upgrade pip > /dev/null 2>&1
    pip install streamlit streamlit-option-menu plotly requests > /dev/null 2>&1
fi

echo ""
echo "[2/3] Starting Backend Server (Port 8000)..."
echo -e "${BLUE}Command: python -m uvicorn app.main:app --host 127.0.0.1 --port 8000${NC}"

# Start backend in background
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 > /tmp/backend.log 2>&1 &
BACKEND_PID=$!
echo "Backend PID: $BACKEND_PID"

# Wait for backend to initialize
echo -e "${YELLOW}⏳ Waiting for backend to initialize (5 seconds)...${NC}"
sleep 5

# Check if backend started successfully
if ! ps -p $BACKEND_PID > /dev/null 2>&1; then
    echo -e "${RED}✗ Backend failed to start${NC}"
    cat /tmp/backend.log
    exit 1
fi

echo -e "${GREEN}✓ Backend started successfully${NC}"

echo ""
echo "[3/3] Starting Frontend (Streamlit on Port 8501)..."
echo -e "${BLUE}Command: streamlit run frontend.py${NC}"

# Start frontend
streamlit run frontend.py

# Cleanup on exit
trap "kill $BACKEND_PID 2>/dev/null" EXIT

echo ""
echo "╔════════════════════════════════════════════════════════════════╗"
echo "║                 Services Stopped                               ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""
