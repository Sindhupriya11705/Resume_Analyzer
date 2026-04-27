# SkillForge – AI Powered Project Learning Platform

Production-ready monorepo scaffold for a real-time project-based learning platform.

## Stack

- **Frontend**: Next.js (App Router) + React + TypeScript, TailwindCSS, Framer Motion, React Three Fiber (Three.js), Chart.js
- **Backend**: FastAPI (REST) + JWT Auth + SQLAlchemy (PostgreSQL) + Motor (MongoDB analytics)
- **WebSockets**: Separate FastAPI WebSocket service for real-time leaderboard, rankings, notifications
- **AI Engine**: Python module for project scoring + skill recommendations (heuristic baseline; pluggable LLM later)
- **Infra**: Docker + Docker Compose

## Folder structure

```
/frontend
/backend
/database
/ai-engine
/websocket-server
docker-compose.yml
.env.example
```

## Quickstart (Docker)

1) Create env file:

```bash
cp .env.example .env
```

2) Start:

```bash
docker compose up --build
```

3) URLs:

- **Frontend**: `http://localhost:3000`
- **Backend API docs**: `http://localhost:8000/docs`
- **WebSocket server**:
  - WS endpoint: `ws://localhost:8001/ws`
  - Health: `http://localhost:8001/health`

## Local dev (without Docker)

### Backend

```bash
cd backend
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

### WebSocket server

```bash
cd websocket-server
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8001
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

## Notes

- **JWT**: Backend issues access tokens; frontend stores them in memory and (optionally) `localStorage` for dev.
- **Uploads**: Resume uploads are stored on disk in `backend/storage/` by default (configurable).
- **AI**: Baseline scoring/recommendations are deterministic; you can later plug in an LLM provider via env vars.

