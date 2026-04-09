# 🔗 LinkSaver — Telegram Bookmark Manager

Save links with tags via Telegram — and find and view them on the web dashboard with analytics.

## Architecture

```
┌─────────────┐     ┌──────────┐     ┌──────────┐     ┌──────────┐
│  Telegram   │────▶│   Bot    │────▶│ Backend  │────▶│PostgreSQL│
│   Client    │     │(aiogram) │     │(FastAPI) │     │          │
└─────────────┘     └──────────┘     └──────────┘     └──────────┘
                                       │
                                       ▼
                                 ┌──────────┐
                                 │ Frontend │
                                 │  (HTML)  │
                                 └──────────┘
```

## Quick Start

### 1. Clone and configure

```bash
git clone <repo-url> && cd se-toolkit-hackathon
cp .env.example .env
# Edit .env and set TELEGRAM_BOT_TOKEN
```

### 2. Run with Docker Compose

```bash
docker compose up -d
```

Services:
- **Backend API**: http://localhost:8000
- **Web Dashboard**: http://localhost:8000/
- **Stats Dashboard**: http://localhost:8000/stats.html
- **Health Check**: http://localhost:8000/health

### 3. Use the bot

1. Get a bot token from [@BotFather](https://t.me/BotFather)
2. Set `TELEGRAM_BOT_TOKEN` in `.env`
3. Send a message with a URL: `https://example.com #python #tutorial`
4. Use `/mylinks` to view your saved links

## Local Development (no Docker)

```bash
# Start backend with SQLite (for quick testing)
cd backend
set DATABASE_URL=sqlite+aiosqlite:///./linksaver.db   # Windows
# DATABASE_URL=sqlite+aiosqlite:///./linksaver.db     # Linux/Mac
uvicorn app.main:app --reload
```

Then open http://localhost:8000

## Project Structure

```
se-toolkit-hackathon/
├── docker-compose.yml
├── .env.example
├── README.md
│
├── backend/
│   ├── Dockerfile
│   ├── pyproject.toml
│   └── app/
│       ├── main.py           # FastAPI app + CORS + static files
│       ├── database.py       # Async SQLAlchemy engine & session
│       ├── models.py         # SQLAlchemy Link model
│       ├── schemas.py        # Pydantic v2 request/response schemas
│       └── api/
│           ├── links.py      # CRUD endpoints
│           └── stats.py      # Statistics & analytics endpoints
│
├── bot/
│   ├── Dockerfile
│   ├── pyproject.toml
│   ├── main.py               # aiogram bot entry point
│   └── handlers/
│       ├── commands.py       # /start, /help, /mylinks
│       └── save_link.py      # Link save flow
│
├── frontend/
│   ├── index.html            # Single-page web dashboard
│   ├── stats.html            # Statistics dashboard with Chart.js
│   └── static/css/style.css  # Responsive styles
│
├── caddy/
│   └── Caddyfile             # Reverse proxy config
│
├── alembic/
│   ├── env.py
│   └── versions/
│       └── 001_create_links_table.py
│
└── tests/
    ├── conftest.py           # Test fixtures (SQLite)
    └── test_api.py           # API endpoint tests
```

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/links` | Save a link |
| `GET` | `/api/links` | List links (`?tag=python&user_id=123`) |
| `GET` | `/api/links/{id}` | Get single link |
| `DELETE` | `/api/links/{id}` | Delete a link (`?user_id=...`) |
| `GET` | `/api/stats` | Get aggregated statistics |
| `GET` | `/api/stats/timeline` | Get daily link creation timeline |
| `GET` | `/health` | Health check |

## Bot Commands

| Command | Description |
|---------|-------------|
| `/start` | Welcome message + tutorial |
| `/help` | Usage examples |
| `/mylinks [tag]` | View your links (optionally filtered by tag) |
| *any message with http* | Auto-save link with regex extraction |

## Running Tests

```bash
cd backend
pip install -e ".[test]"
cd ..
pytest tests/ -v
```

Tests use SQLite in-memory database, no PostgreSQL required.

## Alembic Migrations

```bash
# Generate a new migration
alembic revision --autogenerate -m "description"

# Apply migrations
alembic upgrade head
```

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `DATABASE_URL` | PostgreSQL connection string | `postgresql+asyncpg://linksaver:linksaver@postgres:5432/linksaver` |
| `TELEGRAM_BOT_TOKEN` | Telegram bot token | *(required)* |
| `API_BASE_URL` | Backend URL (for bot) | `http://backend:8000` |

## License

MIT
