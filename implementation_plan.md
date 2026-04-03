# Implementation Plan: LinkSaver

## 📋 Project Overview
**LinkSaver** is a lightweight bookmark management tool that lets users save links with tags via a Telegram bot and search/view them on a simple web dashboard.  
- **End User:** Students, researchers, and developers who collect resources across devices.  
- **Core Problem:** Browser bookmarks are device-bound, hard to search, and lack consistent tagging.  
- **One-Liner:** Save links with tags via Telegram—and find and view them on the web dashboard.

---

## 🛠️ Technology Stack
| Layer | Technology |
|-------|------------|
| **Backend** | Python 3.12, FastAPI, Pydantic v2, SQLAlchemy (async), Alembic |
| **Database** | PostgreSQL 16 (Docker official image) |
| **Agent** | Telegram Bot (`aiogram 3.x`), `httpx` for async LLM calls |
| **Web Client** | Vanilla JS + HTMX + Tailwind CSS (no build step) |
| **Infrastructure** | Docker Compose, Caddy (reverse proxy), Ubuntu 24.04 VM |
| **Testing** | `pytest`, `httpx` async client, `aiogram` test dispatcher |
| **LLM** | Ollama-compatible endpoint (mockable for dev/testing) |

---

## 🚀 Version 1: Core MVP

### 🎯 Goal
Deliver a fully functional product that reliably saves links with tags via Telegram and displays them on a web dashboard. **One core feature:** structured link storage & retrieval.

### 📦 Implementation Phases

| Phase | Tasks | Deliverables |
|-------|-------|--------------|
| **1. Project Setup** | - Initialize Git repo with `main` & `dev` branches<br>- Create `.gitignore`, `LICENSE` (MIT), `.env.example`<br>- Write `docker-compose.yml` (backend, postgres, bot, web) | Working Docker skeleton, env template |
| **2. Database & Backend** | - Define `Link` SQLAlchemy model (`id`, `url`, `title`, `tags[]`, `user_id`, `created_at`)<br>- Configure Alembic migrations<br>- Implement endpoints:<br>  `POST /api/links`<br>  `GET /api/links?tag=...`<br>  `GET /api/links/{id}`<br>  `DELETE /api/links/{id}`<br>- Add CORS, `GET /health`, Pydantic schemas | Functional REST API, DB migrations, OpenAPI docs at `/docs` |
| **3. Telegram Bot (Regex)** | - Setup `aiogram` dispatcher & bot token config<br>- Implement `/start`, `/help`<br>- Parse `/save <url> #tag1 #tag2` using regex<br>- Implement `/mylinks [tag]` → fetch from backend API<br>- Add error handling for missing URLs/invalid formats | Working bot, message → DB flow, tag filtering |
| **4. Web Client** | - Single `index.html` with HTMX/vanilla JS<br>- Fetch `GET /api/links`, render cards<br>- Add tag filter input + search button<br>- Responsive layout, basic styling | Static web dashboard, filterable link list |
| **5. Testing & TA Demo** | - Write 3–4 `pytest` tests for backend endpoints<br>- Manual end-to-end test (bot → DB → web)<br>- Prepare 2-min demo script & feedback checklist | TA-ready build, test coverage, demo plan |


## 🚀 Version 2: LLM-Powered Enhancement

### 🎯 Goal
Upgrade V1 by adding natural language understanding via LLM.

### 📦 Implementation

| Phase | Tasks | Deliverables |
|-------|-------|--------------|
| **LLM Integration** | - Create `llm_client.py` with prompt template & JSON parser<br>- Implement fallback: if LLM fails → regex + tag confirmation<br>- Replace `/save` with free-text handling (any message containing `http`)<br>- Add `--test` flag for mocking LLM responses | Robust LLM pipeline|
