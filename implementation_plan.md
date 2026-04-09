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
| **Agent** | Telegram Bot (`aiogram 3.x`) |
| **Web Client** | Vanilla JS + Chart.js (no build step) |
| **Infrastructure** | Docker Compose, Caddy (reverse proxy), Ubuntu 24.04 VM |
| **Testing** | `pytest`, `httpx` async client |

---

## 🚀 Version 1: Core MVP

### 🎯 Goal
Deliver a fully functional product that reliably saves links with tags via Telegram and displays them on a web dashboard. **One core feature:** structured link storage & retrieval.

### 📦 Implementation Phases

| Phase | Tasks | Deliverables |
|-------|-------|--------------|
| **1. Project Setup** | - Initialize Git repo with `main` & `dev` branches<br>- Create `.gitignore`, `LICENSE` (MIT), `.env.example`<br>- Write `docker-compose.yml` (backend, postgres, bot, web) | Working Docker skeleton, env template |
| **2. Database & Backend** | - Define `Link` SQLAlchemy model (`id`, `url`, `title`, `tags[]`, `user_id`, `created_at`)<br>- Configure Alembic migrations<br>- Implement endpoints:<br>  `POST /api/links`<br>  `GET /api/links?tag=...`<br>  `GET /api/links/{id}`<br>  `DELETE /api/links/{id}`<br>- Add CORS, `GET /health`, Pydantic schemas | Functional REST API, DB migrations, OpenAPI docs at `/docs` |
| **3. Telegram Bot** | - Setup `aiogram` dispatcher & bot token config<br>- Implement `/start`, `/help`<br>- Parse messages with URLs and `#hashtags` using regex<br>- Implement `/mylinks [tag]` → fetch from backend API<br>- Add error handling for missing URLs/invalid formats | Working bot, message → DB flow, tag filtering |
| **4. Web Client** | - Single `index.html` with vanilla JS<br>- Fetch `GET /api/links`, render cards<br>- Add tag filter input + search button<br>- Responsive layout, basic styling | Static web dashboard, filterable link list |
| **5. Testing & TA Demo** | - Write 3–4 `pytest` tests for backend endpoints<br>- Manual end-to-end test (bot → DB → web)<br>- Prepare 2-min demo script & feedback checklist | TA-ready build, test coverage, demo plan |


## 🚀 Version 2: Analytics Dashboard

### 🎯 Goal
Add a comprehensive statistics and analytics dashboard to give users insights into their bookmark collection.

### 📦 Implementation

| Phase | Tasks | Deliverables |
|-------|-------|--------------|
| **Stats API** | - Create `GET /api/stats` endpoint with aggregated data (total links, users, top tags, time-based counts)<br>- Create `GET /api/stats/timeline` for daily link creation data<br>- Add Pydantic schemas for stats responses | Functional stats API with optimized SQL queries |
| **Stats Dashboard** | - Create `stats.html` with Chart.js integration<br>- Render metric cards (total links, users, activity)<br>- Line chart: link saving timeline<br>- Bar chart: top 10 tags<br>- Tag cloud visualization<br>- "Forgotten links" section (older than 30 days) | Full analytics dashboard with interactive charts |
| **Navigation & UX** | - Add navigation bar to both pages (Home ↔ Stats)<br>- Responsive design for mobile<br>- Consistent styling across pages | Unified navigation and polished UI |
| **Testing** | - Add tests for stats endpoints (empty DB, populated DB, timeline)<br>- Verify chart data format | 3 new passing tests |
