#!/bin/bash
# ============================================================
# Smart Stadium — Local Development Startup
# Starts backend (port 8000) and frontend (port 8501) locally
# ============================================================

set -e

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$PROJECT_DIR"

GREEN='\033[0;32m'; YELLOW='\033[1;33m'; RED='\033[0;31m'; NC='\033[0m'

echo ""
echo "------------------------------------------"
echo "     Smart Stadium System — Local Dev Startup"
echo "------------------------------------------"
echo ""

# —— Virtual environment ——
if [ ! -d ".venv" ]; then
    echo -e "${YELLOW}Creating virtual environment...${NC}"
    python3 -m venv .venv
fi
source .venv/bin/activate
echo -e "${GREEN}✔ Virtual environment active${NC}"

# —— Install dependencies ——
pip install -q --upgrade pip
pip install -q -r requirements.backend.txt
pip install -q -r requirements.frontend.txt

# —— Check .env ——
if [ ! -f ".env" ]; then
    echo -e "${RED}✘ .env file not found. Copy .env.example and fill in your values.${NC}"
    exit 1
fi
echo -e "${GREEN}✔ .env file found${NC}"

# —— Start backend ——
echo ""
echo "[2/3] Starting Backend on http://localhost:8000 ..."
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload \
    > /tmp/stadium_backend.log 2>&1 &
BACKEND_PID=$!
echo "      PID: $BACKEND_PID"

sleep 4
if ! ps -p $BACKEND_PID > /dev/null 2>&1; then
    echo -e "${RED}✘ Backend failed to start. Last log lines:${NC}"
    tail -20 /tmp/stadium_backend.log
    exit 1
fi
echo -e "${GREEN}✔ Backend running${NC}"

# —— Start frontend ——
echo ""
echo "[3/3] Starting Frontend on http://localhost:8501 ..."
export API_BASE_URL="http://localhost:8000"
streamlit run streamlit_app/app.py \
    --server.port 8501 \
    --server.address 127.0.0.1 \
    --server.headless false

# —— Cleanup ——
trap "echo 'Stopping backend...'; kill $BACKEND_PID 2>/dev/null" EXIT

echo ""
echo "------------------------------------------"
echo "              Services Stopped"
echo "------------------------------------------"
