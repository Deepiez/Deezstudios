# AI Content Automation Studio

Internal tool self-hosted untuk produksi dan distribusi konten pribadi. Mengotomatisasi alur kerja dari ide, brief, drafting, review, approval, scheduling, hingga autopost ke beberapa channel.

## Overview

AI Content Automation Studio adalah satu workflow terpusat untuk:
- Perencanaan konten (brand, campaign, brief)
- Generasi konten multi-format menggunakan AI (OpenAI, Anthropic, Google Gemini)
- Review dan approval workflow
- Penjadwalan dan auto-publish ke YouTube
- Analytics operasional

### Supported Content Types

| Type | Output |
|------|--------|
| YouTube Shorts | Script, title, hook, thumbnail prompt, description, tags |
| YouTube Long-form | Outline, full script, description, thumbnail prompt |
| TikTok Short Video | Hook, script, caption, visual cues |
| Blog Article | Title, outline, full article, CTA placement, SEO keywords |
| X (Twitter) Post | Single posts, thread, CTA variants |

### Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | Next.js 14 + TypeScript + Tailwind CSS |
| Backend | FastAPI (Python 3.12) |
| Database | PostgreSQL 16 |
| Queue/Jobs | Redis + Celery |
| Storage | MinIO (S3-compatible) |
| Reverse Proxy | Nginx |
| AI Providers | OpenAI, Anthropic, Google Gemini |

---

## Quick Start (Development)

### Prerequisites

- Docker & Docker Compose
- Python 3.12+
- Node.js 20+

### 1. Clone & Setup Environment

```bash
git clone <repository-url>
cd Deezstudios

# Copy environment file
cp .env.example .env

# Edit .env - minimal yang perlu diisi:
# - SECRET_KEY (random string)
# - Minimal 1 AI provider key (OPENAI_API_KEY / ANTHROPIC_API_KEY / GOOGLE_GEMINI_API_KEY)
```

### 2. Start Infrastructure (Docker)

```bash
docker compose up -d
```

Ini akan menjalankan:
- PostgreSQL di `localhost:5432`
- Redis di `localhost:6379`
- MinIO di `localhost:9000` (console: `localhost:9001`)

### 3. Setup Backend

```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Run database migrations
alembic revision --autogenerate -m "initial schema"
alembic upgrade head

# Seed admin user
cd ..
python scripts/seed.py
```

Default credentials: `admin` / `admin123`

### 4. Run Backend

```bash
cd backend
source venv/bin/activate
uvicorn app.main:app --reload --port 8000
```

API docs tersedia di: http://localhost:8000/docs

### 5. Setup & Run Frontend

```bash
cd frontend
npm install
npm run dev
```

Frontend tersedia di: http://localhost:3000

### 6. Run Celery Worker (untuk background jobs)

```bash
cd backend
source venv/bin/activate

# Worker
celery -A app.workers.celery_app worker --loglevel=info

# Beat scheduler (di terminal terpisah)
celery -A app.workers.celery_app beat --loglevel=info
```

---

## Production Deployment (VPS)

### One-Command Deploy

```bash
# Di VPS
git clone <repository-url>
cd Deezstudios
cp .env.production .env
nano .env  # Isi semua values

./scripts/deploy.sh
```

Script ini akan:
1. Build Docker images (backend + frontend)
2. Start semua services (8 containers)
3. Run database migrations
4. Create admin user jika belum ada

### SSL Setup

```bash
./scripts/setup-ssl.sh your-domain.com
```

### Architecture (Production)

```
Internet → Nginx (:80/:443)
              ├── /api/* → Backend (FastAPI :8000)
              └── /* → Frontend (Next.js :3000)

Backend → PostgreSQL, Redis, MinIO
Celery Worker → Background generation & publish jobs
Celery Beat → Scheduled publish checker (every 1 min)
```

### Useful Commands

```bash
# Logs
docker compose -f docker-compose.prod.yml logs -f

# Restart specific service
docker compose -f docker-compose.prod.yml restart backend

# Database backup
./scripts/backup.sh

# Stop all
docker compose -f docker-compose.prod.yml down
```

---

## User Guide

### Workflow Utama

```
1. Login → Dashboard
2. Buat Brand & Campaign (Brands page)
3. Setup Style Guide & CTA Patterns (Style Guides page)
4. Buat Content baru dengan Brief (Content → New)
5. Generate content dengan AI (Content detail → Generation Panel)
6. Review output, regenerate jika perlu
7. Submit for Review → Approve
8. Schedule di Calendar → Auto-publish ke YouTube
```

### Content Generation

1. **Buat Content Item** - Isi brief (topik, audience, objective, tone, dll)
2. **Pilih Provider & Model** - System akan suggest default berdasarkan content type:
   - YouTube Shorts → OpenAI GPT-4o
   - YouTube Long-form → Anthropic Claude 3.5 Sonnet
   - TikTok → OpenAI GPT-4o Mini
   - Blog → Anthropic Claude 3.5 Sonnet
   - X Post → OpenAI GPT-4o Mini
3. **Generate** - AI akan menghasilkan output terstruktur (titles, hooks, script, dll)
4. **Regenerate** - Jika tidak puas, tambahkan revision notes dan regenerate
5. **Clone** - Duplikasi brief untuk membuat variasi

### Style Guide & CTA

Style Guide dan CTA Pattern yang aktif akan otomatis di-inject ke prompt generation:
- **Style Guide**: Tone of voice, writing rules, preferred/banned phrases
- **CTA Pattern**: Library CTA yang bisa dipakai per placement (intro/mid/outro) dan per platform

### Approval Workflow

```
Draft → In Review → Approved → Scheduled → Published
                  ↘ Rejected (back to Draft with revision notes)
```

- Content tanpa approval **tidak bisa** dijadwalkan
- Setiap approve/reject tercatat di audit log

### YouTube Integration

1. Buka **Settings** → YouTube section
2. Klik **Connect YouTube** (perlu Brand ID)
3. Authorize di Google OAuth consent screen
4. Channel terhubung → bisa schedule publish

Fitur YouTube:
- Upload video dengan metadata (title, description, tags)
- Scheduled publish (upload private, auto-publish di waktu tertentu)
- Token auto-refresh

### Calendar

- **Month view** - Overview bulanan semua scheduled content
- **Week view** - Detail mingguan
- Color-coded per platform (YouTube=merah, TikTok=pink, X=abu, Blog=biru)
- Klik event untuk lihat detail atau navigate ke content

### Analytics

Dashboard menampilkan:
- Content pipeline (draft → published funnel)
- Provider usage (cost, tokens, latency per provider)
- Model breakdown (usage per model)
- Publishing stats (success rate)
- Recent activity feed

---

## Project Structure

```
Deezstudios/
├── backend/
│   ├── app/
│   │   ├── api/v1/endpoints/   # 9 API modules
│   │   ├── core/               # Config, DB, auth, security, rate limit, encryption
│   │   ├── models/             # 9 SQLAlchemy models (14 tables)
│   │   ├── schemas/            # Pydantic request/response schemas
│   │   ├── services/
│   │   │   ├── ai_providers/   # OpenAI, Anthropic, Gemini + ProviderManager
│   │   │   ├── generation/     # Prompt templates, builder, parser, service
│   │   │   └── integrations/   # YouTube OAuth + upload service
│   │   └── workers/            # Celery tasks (generation, publish, analytics)
│   ├── migrations/             # Alembic
│   ├── tests/                  # pytest
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── app/                # 11 pages (Next.js App Router)
│   │   ├── components/         # UI, layout, generation, calendar
│   │   ├── hooks/              # API hooks (auth, content, generation, calendar, analytics)
│   │   ├── stores/             # Zustand state management
│   │   ├── lib/                # API client, utilities
│   │   └── types/              # TypeScript types
│   ├── Dockerfile
│   └── package.json
├── docker/
│   └── nginx/                  # Nginx config (reverse proxy, rate limit, SSL-ready)
├── scripts/
│   ├── setup.sh                # Development setup
│   ├── deploy.sh               # Production deployment
│   ├── backup.sh               # Database backup
│   └── setup-ssl.sh            # Let's Encrypt SSL
├── docker-compose.yml          # Development (DB + Redis + MinIO)
├── docker-compose.prod.yml     # Production (all 8 services)
├── .env.example                # Development env template
├── .env.production             # Production env template
└── ARCHITECTURE.md             # System architecture documentation
```

---

## API Reference

Base URL: `http://localhost:8000/api/v1`

### Authentication
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/auth/login` | Login (form-data) |
| POST | `/auth/login/json` | Login (JSON body) |
| GET | `/auth/me` | Get current user |
| POST | `/auth/change-password` | Change password |

### Brands & Campaigns
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET/POST | `/brands/` | List/Create brands |
| GET/PUT/DELETE | `/brands/{id}` | Get/Update/Delete brand |
| GET/POST | `/campaigns/` | List/Create campaigns |
| GET/PUT/DELETE | `/campaigns/{id}` | Get/Update/Delete campaign |

### Content
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET/POST | `/content/` | List/Create content items |
| GET/PUT | `/content/{id}` | Get/Update content |
| POST | `/content/{id}/submit-review` | Submit for review |
| POST | `/content/{id}/approve` | Approve content |
| POST | `/content/{id}/reject` | Reject with notes |
| POST | `/content/{id}/clone` | Clone/duplicate content |
| GET | `/content/{id}/versions` | List versions |

### Generation
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/generation/run` | Run generation (sync) |
| POST | `/generation/regenerate` | Regenerate with revision notes |
| POST | `/generation/run-async` | Run generation (background) |
| GET | `/generation/runs` | List generation runs |
| POST | `/generation/runs/{id}/retry` | Retry failed run |
| GET | `/generation/providers` | List AI providers |
| GET | `/generation/defaults` | Get default provider configs |
| GET | `/generation/defaults/{type}` | Get default for content type |

### Style Guides & CTA
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET/POST | `/style-guides/` | List/Create style guides |
| PUT/DELETE | `/style-guides/{id}` | Update/Delete |
| PATCH | `/style-guides/{id}/toggle` | Toggle active |
| GET/POST | `/style-guides/cta-patterns` | List/Create CTA patterns |
| PUT/DELETE | `/style-guides/cta-patterns/{id}` | Update/Delete |
| PATCH | `/style-guides/cta-patterns/{id}/toggle` | Toggle active |

### Calendar & Scheduling
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/calendar/` | Get calendar events |
| POST | `/calendar/schedule` | Schedule content |
| PUT | `/calendar/schedule/{id}` | Reschedule |
| DELETE | `/calendar/schedule/{id}` | Cancel schedule |
| POST | `/calendar/publish/{id}/run` | Publish now |

### Integrations
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/integrations/accounts` | List platform accounts |
| GET | `/integrations/youtube/connect` | Start YouTube OAuth |
| GET | `/integrations/youtube/callback` | OAuth callback |
| POST | `/integrations/youtube/disconnect/{id}` | Disconnect |
| GET | `/integrations/youtube/channel/{id}` | Channel info |
| GET | `/integrations/youtube/status` | Integration status |

### Analytics
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/analytics/overview` | Dashboard overview |
| GET | `/analytics/content-stats` | Content statistics |
| GET | `/analytics/publish-stats` | Publish statistics |
| GET | `/analytics/provider-usage` | AI provider usage |
| GET | `/analytics/recent-activity` | Activity feed |
| GET | `/analytics/daily-snapshots` | Historical trends |

---

## Security

- **Authentication**: JWT (HS256) with configurable expiry
- **Password**: bcrypt hashing
- **Rate Limiting**: Redis-based sliding window (5/min login, 100/min API)
- **Token Encryption**: Fernet (AES-128-CBC) for OAuth tokens at rest
- **HTTPS**: Nginx reverse proxy with Let's Encrypt
- **Headers**: X-Frame-Options, X-Content-Type-Options, X-XSS-Protection
- **Audit**: Login attempts, approve/reject actions logged

---

## Configuration

### Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `SECRET_KEY` | Yes | Random string for JWT signing + token encryption |
| `POSTGRES_*` | Yes | Database connection |
| `REDIS_*` | Yes | Redis connection |
| `OPENAI_API_KEY` | No* | OpenAI API key |
| `ANTHROPIC_API_KEY` | No* | Anthropic API key |
| `GOOGLE_GEMINI_API_KEY` | No* | Google Gemini API key |
| `YOUTUBE_CLIENT_ID` | No | YouTube OAuth client ID |
| `YOUTUBE_CLIENT_SECRET` | No | YouTube OAuth client secret |
| `YOUTUBE_REDIRECT_URI` | No | OAuth callback URL |
| `S3_*` | No | S3-compatible storage config |
| `DEFAULT_TIMEZONE` | No | Default: `Asia/Jakarta` |

*Minimal 1 AI provider key harus diisi untuk generation.

---

## Roadmap (Post-MVP)

- [ ] AI Image Generation (thumbnail, cover art)
- [ ] AI Video Generation (short clips, B-roll)
- [ ] Deep analytics per channel performance
- [ ] Advanced retrieval memory (pgvector/Qdrant)
- [ ] TikTok autopost (pending API validation)
- [ ] X autopost (pending API cost/policy validation)
- [ ] Drag-and-drop calendar reschedule
- [ ] Multi-language UI

---

## License

Internal tool - private use only.
