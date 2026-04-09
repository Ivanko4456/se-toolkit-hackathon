# 🔗 LinkSaver — Telegram Bookmark Manager

Save links with tags via Telegram — and find and view them on the web dashboard with analytics.

## Demo

### Web Dashboard

![Web Dashboard - Links List](docs/screenshots/dashboard.png)
*Main dashboard showing saved links with clickable tag filters*

![Web Dashboard - Statistics](docs/screenshots/stats.png)
*Statistics page with tag cloud and timeline chart*

### Telegram Bot

![Telegram Bot - Save Link](docs/screenshots/bot_save.png)
*Saving a link via Telegram with hashtags as tags*

![Telegram Bot - My Links](docs/screenshots/bot_mylinks.png)
*Viewing saved links with /mylinks command*

---

## Product Context

### End Users

Developers, students, researchers, and anyone who frequently browses the web and wants to **save interesting links for later** without losing them in browser bookmarks or dozens of open tabs.

### Problem

When browsing the web, you often find useful articles, tutorials, or resources that you want to save — but browser bookmarks are hard to organize, and open tabs get lost. You need a **quick, frictionless way to save links with contextual tags** and find them later from any device.

### Our Solution

LinkSaver lets you save links by simply sending them to a **Telegram bot** with hashtags as tags (e.g., `https://example.com #python #tutorial`). All saved links are instantly available on a **web dashboard** where you can search by tag, view statistics, and browse your collection — no browser extension needed.

---

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

---

## Features

### ✅ Implemented

| Feature | Description |
|---------|-------------|
| **Save links via Telegram** | Send any message containing a URL — the bot auto-extracts the link and tags |
| **Hashtag-based tagging** | Use `#tag` syntax in your message (e.g., `#python #tutorial`) |
| **Web dashboard** | View all saved links in a clean, responsive single-page app |
| **Tag-based search** | Filter links by tag — click any tag or type it in the search bar |
| **Clickable tags** | Click a tag on any link card to instantly filter by it |
| **Tag cloud & statistics** | See your most-used tags with frequency charts and a tag cloud |
| **Timeline chart** | Visualize how many links you saved each day |
| **/mylinks command** | View your links directly in Telegram, with optional tag filter |
| **REST API** | Full CRUD API for links with pagination and filtering |
| **Docker Compose** | One-command deployment with PostgreSQL, backend, bot, and Caddy |
| **Automated tests** | 11 pytest tests covering all API endpoints |

### ❌ Not Yet Implemented

| Feature | Priority |
|---------|----------|
| Link editing (change URL/tags after saving) | Medium |
| Delete links from web dashboard | Medium |
| Full-text search across link content | Low |
| Share links with other users | Low |
| Browser extension as alternative save method | Low |
| Import bookmarks from browser | Low |
| Link preview (fetch title/description automatically) | Medium |
| Export links to CSV/Markdown | Low |

---

## Usage

### Step 1: Get a Telegram Bot Token

1. Open Telegram and search for [@BotFather](https://t.me/BotFather)
2. Send `/newbot` and follow the instructions
3. Copy the token (looks like: `123456789:ABCdefGHIjklMNOpqrsTUVwxyz`)

### Step 2: Deploy the Application

```bash
# Clone the repository
git clone https://github.com/<your-username>/se-toolkit-hackathon.git
cd se-toolkit-hackathon

# Configure environment
cp .env.example .env
nano .env   # or any editor, set your TELEGRAM_BOT_TOKEN

# Start all services
docker compose up -d
```

Wait ~30 seconds for PostgreSQL to be healthy. Check: `docker compose ps`

### Step 3: Save Your First Link

Open Telegram, find your bot, and send:

```
https://docs.python.org/3/tutorial/ #python #tutorial #docs
```

You'll get a confirmation that the link was saved.

### Step 4: View Your Links

**In Telegram:** Send `/mylinks` or `/mylinks python` to filter by tag.

**In browser:** Open http://localhost:8000/ to see the web dashboard.

### Step 5: Search and Browse

- Click any **tag** on a link card to filter by it
- Type a tag name in the **search bar** and press Enter
- Click **✕ Clear** to reset the filter
- Visit http://localhost:8000/stats.html for statistics

---

## Deployment

### Target OS: Ubuntu 24.04

### Prerequisites

Install Docker and Docker Compose:

```bash
# Update package index
sudo apt update

# Install prerequisites
sudo apt install -y ca-certificates curl gnupg

# Add Docker official GPG key
sudo install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
sudo chmod a+r /etc/apt/keyrings/docker.gpg

# Add Docker repository
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
  $(. /etc/os-release && echo "$VERSION_CODENAME") stable" | \
  sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

# Install Docker
sudo apt update
sudo apt install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin

# Add your user to docker group (optional, to run without sudo)
sudo usermod -aG docker $USER
newgrp docker
```

### Step-by-Step Deployment

```bash
# 1. Clone the repository
git clone https://github.com/<your-username>/se-toolkit-hackathon.git
cd se-toolkit-hackathon

# 2. Configure environment
cp .env.example .env
nano .env
```

Edit `.env` and set:

```
TELEGRAM_BOT_TOKEN=your_actual_bot_token_here
DATABASE_URL=postgresql+asyncpg://linksaver:linksaver@postgres:5432/linksaver
API_BASE_URL=http://backend:8000
```

```bash
# 3. Start all services
docker compose up -d --build

# 4. Wait for PostgreSQL to be healthy (~10 seconds)
docker compose ps

# 5. Check backend is running
curl http://localhost:8000/health
# Expected: {"status":"ok"}

# 6. View logs if something goes wrong
docker compose logs -f backend
docker compose logs -f bot
```

### Services and Ports

| Service | URL | Description |
|---------|-----|-------------|
| Backend API | http://localhost:8000 | FastAPI REST API |
| Web Dashboard | http://localhost:8000/ | Main UI |
| Statistics | http://localhost:8000/stats.html | Analytics dashboard |
| Health Check | http://localhost:8000/health | Service health |
| PostgreSQL | localhost:5432 | Database (internal) |

### Production Deployment (with HTTPS)

The project includes a Caddy reverse proxy. To enable HTTPS:

1. Edit `caddy/Caddyfile` and replace `localhost` with your domain
2. Set `DOMAIN=your-domain.com` in `.env`
3. Open ports 80 and 443 in your firewall
4. Caddy will auto-provision Let's Encrypt certificates

### Stopping the Application

```bash
docker compose down

# To also remove data (WARNING: deletes all data):
docker compose down -v
```

---

## Local Development (no Docker)

```bash
# Start backend with SQLite (for quick testing)
cd backend
# Linux/Mac:
DATABASE_URL=sqlite+aiosqlite:///./linksaver.db uvicorn app.main:app --reload
# Windows (cmd):
set DATABASE_URL=sqlite+aiosqlite:///./linksaver.db
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
| `DATABASE_URL` | Database connection string | `postgresql+asyncpg://linksaver:linksaver@postgres:5432/linksaver` |
| `TELEGRAM_BOT_TOKEN` | Telegram bot token | *(required)* |
| `API_BASE_URL` | Backend URL (for bot) | `http://backend:8000` |

## License

MIT
