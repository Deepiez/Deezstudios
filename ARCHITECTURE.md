# System Architecture - AI Content Automation Studio

## High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         NGINX (HTTPS)                            │
└──────────────────────────┬──────────────────────────────────────┘
                           │
          ┌────────────────┼────────────────┐
          │                │                │
          ▼                ▼                ▼
┌──────────────┐  ┌──────────────┐  ┌──────────────┐
│   Next.js    │  │   FastAPI    │  │   MinIO/S3   │
│  Frontend    │  │   Backend    │  │   Storage    │
│  :3000       │  │   :8000      │  │   :9000      │
└──────────────┘  └──────┬───────┘  └──────────────┘
                         │
          ┌──────────────┼──────────────┐
          │              │              │
          ▼              ▼              ▼
┌──────────────┐  ┌──────────┐  ┌──────────────┐
│  PostgreSQL  │  │  Redis   │  │   Celery     │
│  :5432       │  │  :6379   │  │   Workers    │
└──────────────┘  └──────────┘  └──────────────┘
                                       │
                         ┌─────────────┼─────────────┐
                         │             │             │
                         ▼             ▼             ▼
                  ┌──────────┐  ┌──────────┐  ┌──────────┐
                  │  OpenAI  │  │ Anthropic│  │  Gemini  │
                  └──────────┘  └──────────┘  └──────────┘
```

## Project Structure

```
Deezstudios/
├── backend/
│   ├── app/
│   │   ├── api/v1/endpoints/    # API route handlers
│   │   ├── core/                # Config, DB, security
│   │   ├── models/              # SQLAlchemy ORM models
│   │   ├── schemas/             # Pydantic request/response schemas
│   │   ├── services/            # Business logic
│   │   │   ├── ai_providers/    # Multi-provider AI abstraction
│   │   │   └── integrations/    # YouTube, TikTok, X integrations
│   │   ├── workers/             # Celery tasks
│   │   └── utils/               # Shared utilities
│   ├── migrations/              # Alembic database migrations
│   ├── tests/                   # Backend tests
│   ├── alembic.ini
│   └── requirements.txt
├── frontend/                    # Next.js + TypeScript + Tailwind
├── docker/                      # Docker-related configs
├── scripts/                     # Setup and utility scripts
├── docker-compose.yml           # Development services
├── .env.example                 # Environment template
└── ai-content-automation-studio-prd.md
```

## Data Model (Entity Relationship)

```
users
  │
  ├── brands (1:N)
  │     ├── campaigns (1:N)
  │     │     ├── content_items (1:N)
  │     │     │     ├── content_versions (1:N)
  │     │     │     ├── generation_runs (1:N)
  │     │     │     └── publish_jobs (1:N)
  │     │     │           └── publish_logs (1:N)
  │     │     ├── style_guides (N:1)
  │     │     └── cta_patterns (N:1)
  │     ├── style_guides (N:1)
  │     ├── cta_patterns (N:1)
  │     └── platform_accounts (1:N)
  │           └── oauth_tokens (1:N)
  └── audit_logs (1:N)

analytics_daily_snapshots (standalone, generated daily)
```

## Content Workflow State Machine

```
                    ┌──────────┐
                    │  DRAFT   │◄──── Create / Generate
                    └────┬─────┘
                         │ Submit for review
                         ▼
                    ┌──────────┐
              ┌─────│IN_REVIEW │
              │     └────┬─────┘
              │          │ Approve
              │          ▼
              │     ┌──────────┐
              │     │ APPROVED │
              │     └────┬─────┘
              │          │ Schedule
              │          ▼
              │     ┌──────────┐
              │     │SCHEDULED │
              │     └────┬─────┘
              │          │ Publish trigger
              │          ▼
              │     ┌───────────┐
              │     │PUBLISHING │
              │     └─────┬─────┘
              │       ┌───┴───┐
              │       ▼       ▼
              │  ┌─────────┐ ┌────────┐
              │  │PUBLISHED│ │ FAILED │──► Retry
              │  └─────────┘ └────────┘
              │
              │ Reject (revision needed)
              └──────► Back to DRAFT (new version)
```

## AI Provider Layer

The multi-provider abstraction supports:
- **OpenAI**: GPT-4o, GPT-4o-mini, GPT-4-turbo
- **Anthropic**: Claude 3.5 Sonnet, Claude 3.5 Haiku, Claude 3 Opus
- **Google Gemini**: Gemini 2.0 Flash, Gemini 1.5 Pro, Gemini 1.5 Flash

Features:
- Provider selection per generation run
- Automatic cost tracking per request
- Latency and token usage logging
- Manual fallback on failure
- Configurable default provider per task type

## Background Jobs (Celery)

| Task | Schedule | Description |
|------|----------|-------------|
| process_scheduled_publishes | Every 1 min | Check and execute due publish jobs |
| generate_daily_analytics | Every 24h | Aggregate daily metrics snapshot |
| run_content_generation | On-demand | Execute AI generation for content |
| publish_to_youtube | On-demand | Upload and publish to YouTube |
| refresh_oauth_token | On-demand | Refresh expired OAuth tokens |

## API Modules

| Module | Prefix | Responsibility |
|--------|--------|----------------|
| Auth | /auth | Login, logout, session management |
| Brands | /brands | Brand CRUD |
| Campaigns | /campaigns | Campaign CRUD |
| Content | /content | Content items, versions, approval |
| Generation | /generation | AI generation runs |
| Style Guides | /style-guides | Style guides + CTA patterns |
| Calendar | /calendar | Content calendar, scheduling |
| Integrations | /integrations | YouTube OAuth, platform accounts |
| Analytics | /analytics | Operational dashboard data |

## Security

- Password hashing: bcrypt via passlib
- Session: JWT tokens (HS256)
- Token expiry: 24 hours (configurable)
- HTTPS: Nginx reverse proxy (production)
- OAuth tokens: Stored encrypted in database
- Rate limiting: To be implemented at Nginx/app level

## Development Commands

```bash
# Start services
docker compose up -d

# Backend
cd backend
source venv/bin/activate
uvicorn app.main:app --reload --port 8000

# Run migrations
alembic upgrade head

# Create new migration
alembic revision --autogenerate -m "description"

# Celery worker
celery -A app.workers.celery_app worker --loglevel=info

# Celery beat (scheduler)
celery -A app.workers.celery_app beat --loglevel=info

# Frontend
cd frontend
npm run dev
```
