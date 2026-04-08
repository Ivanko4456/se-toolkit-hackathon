# Project: LinkSaver v1 — LLM-Powered Telegram Bookmark Manager

You are an expert Python developer. Help me build **Version 1 (MVP)** of a product called **LinkSaver**.

## 🎯 Product Goal
A simple tool where users save links with tags via Telegram, then search/view them on a web dashboard.  
**One-liner**: "Save links with tags via Telegram—and find and view them on the web dashboard."

## 🧩 Core Requirements (MVP Scope)

### 1. Backend (FastAPI)
- Python 3.12, FastAPI, SQLAlchemy (async), PostgreSQL
- Endpoints:
  - `POST /api/links` — save a link (fields: `url`, `title`, `tags: list[str]`, `user_id`)
  - `GET /api/links` — list links, optional query param `?tag=python` for filtering
  - `GET /api/links/{id}` — get single link
  - `DELETE /api/links/{id}` — delete a link (protected by user_id)
- Use Pydantic v2 for request/response models
- Enable CORS for web frontend
- Health check endpoint: `GET /health`

### 2. Database (PostgreSQL)
- Single table `links`:
  - id (UUID, PK), url (TEXT), title (TEXT), tags (TEXT array), user_id (TEXT, indexed), created_at (TIMESTAMP)
- Use Alembic for migrations (provide basic `env.py` config)
- Connection via environment variable `DATABASE_URL`

### 3. Telegram Bot with LLM Integration ⭐
- Use `aiogram 3.x` + `httpx` for async requests
- **LLM Integration Pattern** (like se-toolkit-lab-7):
  - Bot receives a message with a URL (and optional natural language tags)
  - Send the message to a local LLM endpoint (e.g., `POST http://llm:11434/api/generate` for Ollama)
  - Prompt template for LLM:
    ```
    Extract structured data from this user message:
    - URL: [detect or ask if missing]
    - Title: [suggest from URL or leave empty]
    - Tags: [extract keywords, format as comma-separated list]
    
    User message: "{user_input}"
    
    Respond ONLY in valid JSON: {"url": "...", "title": "...", "tags": ["tag1", "tag2"]}
    ```
  - Parse LLM JSON response → validate → save via backend API
  - If LLM fails or returns invalid JSON: fallback to simple regex URL extraction + ask user for tags
- Bot commands:
  - `/start` — welcome + short tutorial
  - `/help` — usage examples
  - `/mylinks [tag]` — fetch user's links from backend, display as formatted list
  - Any message containing `http` → trigger save flow
- Store `telegram_user_id` as `user_id` in backend (no auth system needed for MVP)

### 4. Web Client (Simple)
- Single `index.html` with:
  - Input field for tag filter + "Search" button
  - List of cards: each shows title (linkified), URL, tags, created date
  - Fetch data from `GET /api/links` via vanilla JS or HTMX
  - Responsive design (mobile-friendly)
- No build step — serve static files via FastAPI `StaticFiles` or separate lightweight service

### 5. Infrastructure
- `docker-compose.yml` with services:
  - `backend` (FastAPI app)
  - `postgres` (official image, persistent volume)
  - `bot` (aiogram service, depends_on backend)
  - `llm` (optional: placeholder for Ollama; if skipped, use mock LLM response in dev)
  - `caddy` or `nginx` (reverse proxy, serve frontend + route /api to backend)
- `.env.example` with required vars:
  ```
  DATABASE_URL=postgresql+asyncpg://user:pass@postgres:5432/linksaver
  TELEGRAM_BOT_TOKEN=your_token_here
  LLM_API_URL=http://llm:11434/api/generate
  API_BASE_URL=http://backend:8000
  ```

## 📁 Expected Project Structure
```
se-toolkit-hackathon/
├── docker-compose.yml
├── .env.example
├── README.md
│
├── backend/
│   ├── Dockerfile
│   ├── pyproject.toml (fastapi, sqlalchemy, alembic, pydantic, uvicorn)
│   └── app/
│       ├── main.py
│       ├── database.py
│       ├── models.py
│       ├── schemas.py
│       └── api/links.py
│
├── bot/
│   ├── Dockerfile
│   ├── pyproject.toml (aiogram, httpx, pydantic)
│   └── bot/
│       ├── main.py
│       ├── llm_client.py  # LLM request + fallback logic
│       └── handlers/
│           ├── commands.py
│           └── save_link.py
│
├── frontend/
│   ├── Dockerfile (optional, or serve via backend)
│   └── index.html + static/
│
└── caddy/
    └── Caddyfile
```

## ✅ MVP Acceptance Criteria
1. User sends `https://example.com #python #tutorial` to bot → LLM parses → link saved to DB
2. User sends `/mylinks python` → bot shows filtered list from backend
3. Web page at `/` shows same links, filterable by tag
4. All services start with `docker compose up`
5. Code follows async best practices, type hints, and basic error handling

## 🧪 Testing Notes
- Provide 2-3 pytest tests for backend endpoints (use `httpx` async client)
- Bot: include a `--test` mode flag to mock LLM and backend calls (like lab-7)
- Document how to run tests in README

## 🚫 Out of Scope for v1
- User authentication beyond telegram_id
- Link preview/scraping
- Inline keyboards (use text commands only)
- Advanced search (exact tag match only)
- Mobile app (web is enough)

## 📤 Deliverables
Please generate:
1. Complete code for all files listed in the structure above
2. Working `docker-compose.yml` that starts all services
3. Sample `.env.example` and README snippet for deployment
4. Brief comments explaining LLM integration fallback logic

Start with the backend (`models.py`, `main.py`), then bot LLM client, then wire everything together.