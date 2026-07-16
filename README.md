# Social Media Manager

**AI-Powered Social Media Content Management Platform**

Social Media Manager is a full-stack platform for creating, scheduling, managing, and analyzing social media content across LinkedIn, X (Twitter), Instagram, Facebook, and YouTube — powered by AI.

---

## Features

### Content Creation
- **AI Content Generator** — Generate platform-specific posts (LinkedIn articles, X threads, Instagram captions, YouTube scripts) with tone, length, and keyword controls
- **AI Idea Generator** — Get content ideas by industry, keywords, audience, and category (educational, tutorials, case studies, tips, etc.)
- **Writing Tools** — 10 AI-powered tools: rewrite, expand, summarize, translate, grammar check, generate hooks/CTAs/hashtags, SEO optimize, tone adjust
- **Brand Voice Training** — Configure tone, writing style, CTA style, emoji usage, formatting, vocabulary, and train on sample posts

### AI Media Assistant
- **Image Generator** — Create social graphics, carousels, infographics, quote cards, YouTube thumbnails in 10 style presets
- **Video Generator** — Generate Reels and YouTube Shorts (5-60 seconds)
- **Voiceover Generator** — Text-to-speech with 6 voices (Alloy, Echo, Fable, Onyx, Nova, Shimmer) and speed control
- **Caption Generator** — Platform-optimized captions with emoji and hashtag toggles

### Content Repurposing
- Repurpose any content (blog posts, videos, podcasts, PDFs) into 9+ formats: LinkedIn posts, X threads, Facebook posts, Instagram captions, carousel copy, newsletters, YouTube Shorts scripts, Reel scripts, emails

### Content Calendar & Scheduling
- **Calendar Views** — Daily, weekly, monthly views with drag-and-drop scheduling
- **Campaign Management** — Color-coded campaigns with date ranges
- **Publishing Queue** — Automated queue with retry logic and platform-specific best posting times
- **Recurring Posts** — Daily, weekly, monthly recurrence patterns

### AI Recommendations
- **Content Score** — 0-100 gauge with 6-dimension analysis (readability, emotional impact, specificity, originality, CTA strength, hook power)
- **Prioritized Suggestions** — High/medium/low priority recommendations with impact estimates
- **One-Click Apply** — Apply headline, hook, CTA, posting time, hashtag, and viral potential improvements

### Analytics Dashboard
- **KPI Cards** — Reach, impressions, engagement, followers, subscribers, watch time, clicks, CTR, leads, conversions
- **Trend Charts** — Line charts for reach, impressions, engagement over time
- **Platform Comparison** — Bar chart comparing performance across all connected platforms
- **Content Distribution** — Pie chart of content types
- **Best Posting Times** — Heatmap showing optimal posting windows (7-day × 17-hour)
- **Top Posts** — Table with impressions, engagement rate, clicks

### Team Collaboration
- **Team Members** — Invite members with roles (Owner, Admin, Editor, Viewer)
- **Comments & Threads** — Discuss posts with threaded comments
- **Review Workflow** — Request reviews, approve, or request changes
- **Version History** — Track post edits with change notes
- **Notifications** — Review requests, comments, approvals, mentions, assignments

### Media Library
- Upload and organize images, videos, PDFs, brand assets, logos, templates
- Folder organization with search by type and tags

### Billing & Subscription
- **4 Plans** — Free ($0), Pro ($29/mo), Business ($99/mo), Enterprise ($299/mo)
- **Usage Tracking** — AI credits, workspaces, team members, media storage, scheduled posts, platforms
- **Stripe Integration** — Checkout, invoices, payment method management
- **Plan Management** — Upgrade, downgrade, cancel at period end

### Security
- **RBAC** — 4-tier role system: Owner, Admin, Editor, Viewer with granular permissions
- **Audit Logs** — Track all actions with user, resource, details, timestamp, IP
- **Rate Limiting** — 100 requests per 60-second window per user
- **OAuth Connections** — Google, GitHub, LinkedIn, Twitter, Facebook, YouTube
- **Encryption** — AES-256-GCM for API keys and tokens with key rotation
- **GDPR Compliance** — Data processing agreement, consent recording, right to erasure, data portability

### Dark/Light Mode
- Toggle between Light, Dark, and System (follows OS preference)
- Persisted to localStorage

---

## Tech Stack

| Layer | Technology | Version |
|-------|-----------|---------|
| **Frontend** | Next.js (App Router) | 16.2.10 |
| **UI Library** | React | 19.2.4 |
| **Language** | TypeScript | 5.x |
| **Styling** | Tailwind CSS | 4.x |
| **Charts** | Recharts | 3.9.2 |
| **State** | Zustand | 5.0.14 |
| **Icons** | Lucide React | 1.24.0 |
| **Auth (FE)** | NextAuth.js | 4.24.14 |
| **ORM (FE)** | Prisma | 7.8.0 |
| **Backend** | FastAPI | 0.115.0 |
| **Language** | Python | 3.12 |
| **ORM (BE)** | SQLAlchemy | 2.0.35 |
| **Database** | PostgreSQL | 16 |
| **Cache** | Redis | 7 |
| **AI** | OpenAI SDK | 1.50.0 |
| **AI** | Anthropic SDK | 0.34.0 |
| **AI** | Google GenAI | 1.0.0 |
| **Payments** | Stripe SDK | ≥7.0.0 |
| **Queue** | Celery | 5.4.0 |
| **Storage** | AWS S3 (boto3) | 1.35.0 |
| **Containers** | Docker Compose | v3.8 |

---

## Project Structure

```
social-media-app/
├── frontend/                    # Next.js 16 application
│   ├── src/
│   │   ├── app/                 # App Router pages
│   │   │   ├── layout.tsx       # Root layout with ThemeProvider
│   │   │   ├── globals.css      # CSS variables, dark mode
│   │   │   ├── page.tsx         # Landing page
│   │   │   ├── auth/            # Login, Register
│   │   │   └── dashboard/       # All dashboard pages
│   │   │       ├── page.tsx           # Main dashboard
│   │   │       ├── analytics/         # Analytics with charts
│   │   │       ├── billing/           # Subscription & billing
│   │   │       ├── security/          # Security settings
│   │   │       ├── recommendations/   # AI recommendations
│   │   │       ├── ai-assistant/      # Image/video/voice/caption
│   │   │       ├── content-studio/    # Content creation
│   │   │       ├── calendar/          # Content calendar
│   │   │       ├── media/             # Media library
│   │   │       ├── repurpose/         # Content repurposing
│   │   │       └── team/              # Team collaboration
│   │   ├── components/
│   │   │   ├── layout/          # Sidebar, Header, DashboardLayout
│   │   │   ├── providers/       # ThemeProvider
│   │   │   ├── ui/              # Button, Card, Input, Dropdown
│   │   │   ├── content-studio/  # IdeaGenerator, ContentGenerator, etc.
│   │   │   ├── calendar/        # CalendarView
│   │   │   ├── media/           # MediaLibrary
│   │   │   ├── repurpose/       # RepurposeEngine
│   │   │   └── team/            # TeamCollaboration
│   │   ├── stores/              # Zustand state management
│   │   ├── lib/                 # Auth config, utilities
│   │   └── types/               # TypeScript interfaces
│   ├── Dockerfile               # Multi-stage production build
│   └── package.json
│
├── backend/                     # FastAPI application
│   ├── app/
│   │   ├── main.py              # FastAPI app, CORS, routers
│   │   ├── core/
│   │   │   ├── config.py        # Environment configuration
│   │   │   ├── database.py      # SQLAlchemy async engine
│   │   │   └── security.py      # JWT, bcrypt, auth middleware
│   │   ├── models/              # SQLAlchemy ORM models
│   │   │   ├── user.py          # User, Account, Session
│   │   │   ├── workspace.py     # Workspace, WorkspaceMember
│   │   │   └── content.py       # Post, Analytics, BrandVoice, etc.
│   │   ├── schemas/             # Pydantic request/response schemas
│   │   └── api/                 # API route handlers (20 routers)
│   │       ├── auth.py          # Authentication endpoints
│   │       ├── workspaces.py    # Workspace management
│   │       ├── posts.py         # Post CRUD
│   │       ├── analytics.py     # Analytics data
│   │       ├── billing.py       # Subscription & billing
│   │       ├── security_api.py  # Security & compliance
│   │       ├── ai_content.py    # AI content generation
│   │       ├── ai_ideas.py      # AI idea generation
│   │       ├── ai_media.py      # AI image/video/voice/caption
│   │       ├── recommendations.py # AI recommendations
│   │       └── ...              # 10 more API modules
│   ├── Dockerfile               # Multi-stage production build
│   └── requirements.txt
│
├── docs/                        # Documentation
│   ├── PRD.md                   # Product Requirements Document
│   ├── HLD.md                   # High-Level Design
│   ├── LLD.md                   # Low-Level Design
│   ├── SPEC.md                  # Technical Specification
│   └── ARCHITECTURE.md          # Architecture Document
│
├── docker-compose.yml           # Container orchestration
├── scripts/                     # Utility scripts
└── shared/                      # Shared code (placeholder)
```

---

## Prerequisites

| Requirement | Version | Purpose |
|-------------|---------|---------|
| Node.js | 20+ | Frontend runtime |
| npm | 10+ | Frontend package manager |
| Python | 3.12+ | Backend runtime |
| PostgreSQL | 16 | Primary database |
| Redis | 7 | Cache and queue |
| Docker | 24+ | Containerization (optional) |
| Docker Compose | v2+ | Multi-container orchestration (optional) |

---

## Installation

### Option 1: Docker Compose (Recommended)

This sets up everything — database, cache, backend, and frontend — in one command.

```bash
# Clone the repository
git clone https://github.com/ranaprv/social-media-app.git
cd social-media-app

# Start all services
docker compose up --build
```

Services will be available at:
- **Frontend:** http://localhost:3001
- **Backend API:** http://localhost:8001
- **API Documentation:** http://localhost:8001/api/docs
- **PostgreSQL:** localhost:5432
- **Redis:** localhost:6380

To run in detached mode:
```bash
docker compose up -d
```

To stop all services:
```bash
docker compose down
```

### Option 2: Manual Setup

#### 1. Clone the repository

```bash
git clone https://github.com/ranaprv/social-media-app.git
cd social-media-app
```

#### 2. Set up the database and cache

Start PostgreSQL and Redis using Docker:

```bash
docker compose up -d postgres redis
```

Or install them natively on your machine.

#### 3. Set up the backend

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your configuration (see Configuration section below)

# Start the backend server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

#### 4. Set up the frontend

```bash
cd frontend

# Install dependencies
npm install

# Start the development server
npm run dev
```

The frontend will be available at http://localhost:3000.

---

## Configuration

### Environment Variables

Create a `.env` file in the `backend/` directory:

```bash
cp backend/.env.example backend/.env
```

#### Required

```env
# Database
DATABASE_URL=postgresql+asyncpg://socialmediamanager:socialmediamanager_dev@localhost:5432/socialmediamanager

# Redis
REDIS_URL=redis://localhost:6379/0

# Authentication
SECRET_KEY=your-secret-key-change-in-production
```

#### AI Providers (at least one recommended)

```env
# OpenAI (recommended — powers most AI features)
OPENAI_API_KEY=sk-...

# Anthropic (alternative)
ANTHROPIC_API_KEY=sk-ant-...

# Google Gemini (alternative)
GOOGLE_AI_API_KEY=...
```

Without API keys, AI features return placeholder responses. The app still functions for all non-AI features.

#### Social Platform OAuth (for publishing)

```env
# LinkedIn
LINKEDIN_CLIENT_ID=
LINKEDIN_CLIENT_SECRET=

# X (Twitter)
TWITTER_CLIENT_ID=
TWITTER_CLIENT_SECRET=

# Instagram
INSTAGRAM_CLIENT_ID=
INSTAGRAM_CLIENT_SECRET=

# Facebook
FACEBOOK_APP_ID=
FACEBOOK_APP_SECRET=

# YouTube
YOUTUBE_CLIENT_ID=
YOUTUBE_CLIENT_SECRET=
```

#### Billing (Stripe)

```env
STRIPE_SECRET_KEY=sk_...
STRIPE_WEBHOOK_SECRET=whsec_...
STRIPE_PUBLISHABLE_KEY=pk_...
```

#### File Storage (AWS S3)

```env
AWS_ACCESS_KEY_ID=
AWS_SECRET_ACCESS_KEY=
AWS_BUCKET_NAME=your-bucket
AWS_REGION=us-east-1
```

#### OAuth Login Providers

```env
# Google
GOOGLE_CLIENT_ID=
GOOGLE_CLIENT_SECRET=

# GitHub
GITHUB_CLIENT_ID=
GITHUB_CLIENT_SECRET=
```

### Frontend Configuration

The frontend uses the environment variable `NEXT_PUBLIC_API_URL` to connect to the backend:

```env
NEXT_PUBLIC_API_URL=http://localhost:8000/api
```

When running via Docker Compose, this is automatically configured.

### Docker Compose Configuration

The `docker-compose.yml` configures all services with sensible defaults. Key settings:

| Service | Port | Notes |
|---------|------|-------|
| Frontend | 3001 → 3000 | Hot reload in development |
| Backend | 8001 → 8000 | Hot reload in development |
| PostgreSQL | 5432 | Data persisted in `postgres_data` volume |
| Redis | 6380 | Data persisted in `redis_data` volume |

Environment variables can be passed to the backend via the `docker-compose.yml` environment section or a `.env` file in the project root.

---

## Usage

### Register & Login

1. Navigate to http://localhost:3000 (or :3001 in Docker)
2. Create an account with email and password
3. Log in to access the dashboard

### Create Content

1. Go to **Content Studio** from the sidebar
2. Use **Idea Generator** to get content ideas for your industry
3. Use **Content Generator** to create platform-specific posts
4. Use **Writing Tools** to refine and optimize your content

### Generate Media

1. Go to **AI Assistant** from the sidebar
2. Choose a tab: Image, Video, Voiceover, or Caption
3. Configure your request (prompt, style, dimensions)
4. Click Generate and view the result

### Schedule Posts

1. Go to **Calendar** from the sidebar
2. Create events by clicking on a date
3. Assign posts to specific time slots
4. Use **Scheduler** for queue management and best posting times

### View Analytics

1. Go to **Analytics** from the sidebar
2. Select a time period (7, 30, or 90 days)
3. View KPIs, trend charts, platform comparison, and top posts

### Manage Billing

1. Go to **Billing** from the sidebar
2. View current plan, usage, and upgrade options
3. Select a plan and complete Stripe checkout

### Security Settings

1. Go to **Security** from the sidebar
2. View audit logs, RBAC roles, rate limit status
3. Manage OAuth connections and check GDPR compliance

---

## API Documentation

Once the backend is running, interactive API documentation is available at:

- **Swagger UI:** http://localhost:8001/api/docs
- **ReDoc:** http://localhost:8001/api/redoc

### Key API Endpoints

| Category | Endpoint | Method | Description |
|----------|----------|--------|-------------|
| Auth | `/api/auth/register` | POST | Create account |
| Auth | `/api/auth/login` | POST | Get JWT token |
| Posts | `/api/posts/{workspace_id}` | GET/POST | List or create posts |
| Analytics | `/api/analytics/dashboard` | GET | Dashboard metrics |
| Billing | `/api/billing/plans` | GET | List subscription plans |
| AI | `/api/ai/generate` | POST | Generate content |
| AI Media | `/api/ai/media/generate-image` | POST | Generate AI image |
| Security | `/api/security/audit-logs` | GET | View audit logs |
| Calendar | `/api/calendar/events` | GET | List calendar events |
| Team | `/api/team/members` | GET | List team members |

All endpoints (except auth) require a Bearer JWT token in the Authorization header.

---

## Subscription Plans

| Feature | Free | Pro ($29/mo) | Business ($99/mo) | Enterprise ($299/mo) |
|---------|------|-------------|-------------------|---------------------|
| AI Credits/month | 50 | 500 | 2,000 | Unlimited |
| Platforms | 3 | 5 | 5 | Unlimited |
| Workspaces | 1 | 5 | Unlimited | Unlimited |
| Team Members | 1 | 5 | 20 | Unlimited |
| Media Storage | 100 MB | 5 GB | 50 GB | Unlimited |
| Scheduled Posts | 10 | 100 | Unlimited | Unlimited |
| Analytics | Basic | Advanced | Full Suite | Enterprise |
| Brand Voice | — | ✅ | ✅ | ✅ |
| AI Repurposing | — | ✅ | ✅ | ✅ |
| Team Collaboration | — | — | ✅ | ✅ |
| SSO/SAML | — | — | — | ✅ |
| API Access | — | — | — | ✅ |

---

## Docker Commands

```bash
# Start all services (build if needed)
docker compose up --build

# Start in background
docker compose up -d

# Stop all services
docker compose down

# View logs
docker compose logs -f backend
docker compose logs -f frontend

# Rebuild a specific service
docker compose up --build backend

# Access a running container
docker compose exec backend bash
docker compose exec frontend sh

# Database access
docker compose exec postgres psql -U socialmediamanager -d socialmediamanager

# Redis CLI
docker compose exec redis redis-cli
```

---

## Supported Platforms

| Platform | Content Types | Status |
|----------|---------------|--------|
| LinkedIn | Posts, articles, carousels, polls | ✅ Connected |
| X (Twitter) | Tweets, threads | ✅ Connected |
| Instagram | Captions, Reels, carousels | ✅ Connected |
| Facebook | Posts, stories | ✅ Connected |
| YouTube | Shorts scripts, long-form scripts, descriptions | ✅ Connected |

---

## Development

### Running Tests

```bash
# Frontend
cd frontend
npm run lint

# Backend (when test suite is added)
cd backend
pytest
```

### Building for Production

```bash
# Frontend
cd frontend
npm run build
npm start

# Backend
cd backend
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### Database Migrations

```bash
# Generate migration
cd frontend
npx prisma migrate dev --name migration_name

# Apply migrations
npx prisma migrate deploy
```

---

## Architecture

The application follows a clean separation between frontend and backend:

- **Frontend** (Next.js 16) handles UI rendering, client-side state (Zustand), and user interactions
- **Backend** (FastAPI) handles business logic, database operations, AI integrations, and external API calls
- **PostgreSQL** stores all persistent data (users, workspaces, posts, analytics)
- **Redis** provides caching, rate limiting, and background job queuing
- **AI Providers** (OpenAI, Anthropic, Gemini) power content generation, recommendations, and media creation

For detailed architecture documentation, see:
- [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)
- [docs/HLD.md](docs/HLD.md)
- [docs/LLD.md](docs/LLD.md)

---

## Troubleshooting

### Backend won't start
- Verify PostgreSQL is running: `docker compose ps postgres`
- Check `DATABASE_URL` in `.env` matches your PostgreSQL config
- Ensure all Python dependencies are installed: `pip install -r requirements.txt`

### Frontend can't connect to API
- Verify backend is running: `curl http://localhost:8000/api/health`
- Check `NEXT_PUBLIC_API_URL` in your frontend environment
- Ensure CORS allows your frontend origin (configured in `main.py`)

### AI features return placeholders
- Add your OpenAI API key to `backend/.env`: `OPENAI_API_KEY=sk-...`
- Restart the backend after changing environment variables

### Docker build fails
- Ensure Docker and Docker Compose are installed and running
- Try a clean build: `docker compose down && docker compose up --build`

### Database connection refused
- Check PostgreSQL container is healthy: `docker compose ps`
- Verify the `DATABASE_URL` format: `postgresql+asyncpg://user:password@host:port/dbname`

---

## License

MIT

---

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## Links

- **Repository:** https://github.com/ranaprv/social-media-app
- **API Docs:** http://localhost:8001/api/docs (when running)
- **Frontend:** http://localhost:3000 (manual) or http://localhost:3001 (Docker)
