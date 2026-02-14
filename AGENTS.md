# AGENTS.md

This file provides guidance to coding agents when working with code in this repository.

## Project Overview

This is a white-labeled fork of Open WebUI, rebranded as **Cognitia** - an enterprise AI platform for Colombian SMEs. The project is a full-stack application with a SvelteKit frontend and FastAPI Python backend that provides a web interface for interacting with LLMs (Ollama, OpenAI-compatible APIs).

## Development Commands

### Frontend (SvelteKit + Tailwind v4)
```bash
npm run dev              # Start dev server with HMR (port 5173)
npm run dev:5050         # Dev server on port 5050
npm run build            # Production build
npm run check            # TypeScript/Svelte type checking
npm run lint             # Run all linters (frontend + types + backend)
npm run lint:frontend    # ESLint for frontend
npm run format           # Prettier formatting
npm run test:frontend    # Vitest unit tests
```

### Backend (FastAPI + Python 3.11)
```bash
cd backend && ./dev.sh   # Start backend with hot reload (port 8080)
# OR directly:
cd backend && uvicorn open_webui.main:app --port 8080 --host 0.0.0.0 --reload

# Linting
./scripts/lint-backend.sh  # Runs pylint on backend/

# Tests (requires pytest)
cd backend && pytest
```

### Docker
```bash
# Standard build
docker build -t cognitia .

# White-label build
docker build -f Dockerfile.whitelabel -t cognitia .
./scripts/build-whitelabel.sh

# Docker Compose variants
docker-compose up                                    # Standard
docker-compose -f docker-compose.gpu.yaml up         # NVIDIA GPU
docker-compose -f docker-compose.whitelabel.yaml up  # White-label
```

### Branding Compliance
```bash
./scripts/verify_compliance.sh  # Check for "Open WebUI" references
```

## Architecture

### Frontend (`src/`)
- **Framework**: SvelteKit 2.x with Svelte 5
- **Styling**: Tailwind CSS v4 with custom brand colors
- **State**: Svelte stores (`src/lib/stores/`)
- **API Layer**: `src/lib/apis/` - typed API clients for each backend service
- **Routing**: File-based in `src/routes/`
  - `(app)/` - authenticated routes (chat, admin, settings)
  - `auth/` - login/signup flows
  - `s/[id]` - shared chat viewing

### Brand Identity (`src/lib/constants/identity.ts`)
Centralized branding configuration with APP_NAME, colors, and URLs. All UI components import from here for dynamic branding.

### Backend (`backend/open_webui/`)
- **Framework**: FastAPI with uvicorn
- **Entry**: `main.py` - FastAPI app with middleware, CORS, routes
- **Routers**: `routers/` - one file per domain (auth, chats, models, etc.)
- **Models**: `models/` - SQLAlchemy ORM models
- **Config**: `config.py` - runtime configuration, `env.py` - environment variables
- **Database**: SQLAlchemy + Alembic migrations (`migrations/`)
- **Vector DBs**: `retrieval/vector/dbs/` - ChromaDB, PGVector, Qdrant, Milvus, etc.

### Key Integrations
- **LLM Providers**: Ollama (`routers/ollama.py`), OpenAI (`routers/openai.py`)
- **RAG**: `routers/retrieval.py` with 9 vector DB backends
- **MCP**: Model Context Protocol support (`mcp==1.25.0`)
- **Real-time**: Socket.IO for chat streaming (`socket/main.py`)

### Static Assets
- `static/static/` - favicons, splash screens, PWA icons
- `static/manifest.json` - PWA manifest
- `backend/open_webui/static/` - backend static files

## Styling System

Tailwind v4 with CSS variables for theming:
- Brand colors: `brand-50` through `brand-900` (blue palette)
- Surface colors: `surface-base`, `surface-elevated`, `surface-overlay`
- Primary scale: `primary-50` through `primary-950`

CSS variables defined in `src/app.css`, extended in `tailwind.config.js`.

## i18n

Translation files in `src/lib/i18n/locales/`. To add new translation keys:
```bash
npm run i18n:parse  # Extract keys and format files
```

## Environment Variables

Key variables (see `backend/open_webui/env.py` for full list):
- `WEBUI_NAME` - App display name (default: from identity.ts)
- `OLLAMA_BASE_URL` - Ollama server URL
- `OPENAI_API_KEY` / `OPENAI_API_BASE_URL` - OpenAI config
- `DATABASE_URL` - SQLite or PostgreSQL connection
- `REDIS_URL` - Optional Redis for sessions/caching

## Database Migrations

Using Alembic for SQLAlchemy migrations:
```bash
cd backend
alembic revision -m "description"  # Create migration
alembic upgrade head               # Apply migrations
```

Migrations auto-run on startup when `ENABLE_DB_MIGRATIONS=true`.

## White-Label Context

This fork implements the Cognitia brand transformation (see `planning/agentic_master_plan.md`):
- All "Open WebUI" references replaced with dynamic `APP_NAME`
- Custom blue color palette (#3b82f6 primary)
- Custom favicon/splash assets
- Spanish-language enterprise positioning

When modifying UI text, use i18n templates with `{name: APP_NAME}` interpolation.
