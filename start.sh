#!/usr/bin/env bash

# ==============================================================================
# Argus AI — Quickstart One-Click Runner
# ==============================================================================

set -e

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$ROOT_DIR"

echo "======================================================================"
echo "🛡️  ARGUS AI — AUTONOMOUS LLM APPLICATION SECURITY ASSESSMENT PLATFORM"
echo "======================================================================"
echo ""

# Function to stop background processes on exit
cleanup() {
    echo ""
    echo "Shutting down Argus AI services..."
    kill $(jobs -p) 2>/dev/null || true
    exit 0
}
trap cleanup SIGINT SIGTERM EXIT

# 1. Target Enterprise Chatbot (Port 7003)
echo "🚀 [1/4] Starting Target Chatbot on http://localhost:7003 ..."
cd "$ROOT_DIR/chatbot"
PYTHONPATH=. "$ROOT_DIR/attack-engine/venv/bin/python3" main.py > /dev/null 2>&1 &
CHATBOT_PID=$!
cd "$ROOT_DIR"

# 2. Attack Engine Microservice (Port 7002)
echo "⚔️  [2/4] Starting Attack Engine on http://localhost:7002 ..."
cd "$ROOT_DIR/attack-engine"
"$ROOT_DIR/attack-engine/venv/bin/uvicorn" main:app --port 7002 > /dev/null 2>&1 &
ATTACK_PID=$!
cd "$ROOT_DIR"

# 3. Backend Gateway & Network Inspector (Port 8000)
echo "🌐 [3/4] Starting Backend Gateway on http://localhost:8000 ..."
cd "$ROOT_DIR/backend"
"$ROOT_DIR/backend/venv/bin/uvicorn" main:app --port 8000 > /dev/null 2>&1 &
BACKEND_PID=$!
cd "$ROOT_DIR"

# 4. Frontend SOC Dashboard (Port 5173)
echo "📊 [4/4] Starting Frontend SOC Dashboard on http://localhost:5173 ..."
cd "$ROOT_DIR/frontend"
npm run dev -- --port 5173 > /dev/null 2>&1 &
FRONTEND_PID=$!
cd "$ROOT_DIR"

sleep 3

echo ""
echo "======================================================================"
echo "✅ ALL ARGUS AI SERVICES ARE LIVE AND RUNNING!"
echo "======================================================================"
echo "  📊 Frontend SOC Dashboard : http://localhost:5173"
echo "  🌐 Backend API Gateway     : http://localhost:8000/docs"
echo "  🤖 Target Dummy Chatbot   : http://localhost:7003"
echo "  ⚔️  Attack Engine API      : http://localhost:7002/docs"
echo "======================================================================"
echo "Press [Ctrl+C] at any time to stop all services."
echo ""

wait



#cd /home/cybobug/Downloads/argus-llm_security-main
#./start.sh