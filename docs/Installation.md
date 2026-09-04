# Argus AI — Installation and Setup Guide

## Prerequisites
- **Python**: 3.10+ (Tested on Python 3.14)
- **Node.js**: 18+ (Tested on Node 22)
- **Neo4j**: 5.x (Optional for mock mode; required for live graph mode)
- **Docker & Docker Compose**: (Optional, for containerized deployment)

## Step-by-Step Local Setup

### 1. Attack Engine Setup
```bash
cd attack-engine
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
pytest tests/
```

### 2. Backend Setup
```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
pytest app/tests/
uvicorn app.main:app --reload --port 8000
```

### 3. Frontend Dashboard Setup
```bash
cd frontend
npm install
npm run dev
```

### 4. Running Target Chatbot
```bash
cd chatbot
python3 -m venv venv
source venv/bin/activate
pip install fastapi uvicorn pydantic
uvicorn main:app --reload --port 7003
```
