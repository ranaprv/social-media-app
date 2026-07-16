# Production Deployment Guide

## Prerequisites

- Docker 24+ and Docker Compose v2
- Domain name with SSL (for production)
- Stripe account (for billing)
- OpenAI/Anthropic/Gemini API key (for AI features)
- Google Drive service account (for Drive integration)

## 1. Environment Setup

```bash
cp backend/.env.example backend/.env
cp frontend/.env.example frontend/.env
```

Edit `backend/.env` with production values:

```env
DATABASE_URL=postgresql+asyncpg://user:password@db-host:5432/socialmediamanager
REDIS_URL=redis://redis-host:6379/0
SECRET_KEY=<random-64-char-string>
ENVIRONMENT=production
ALLOWED_ORIGINS=https://yourdomain.com

# AI (at least one)
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
GOOGLE_AI_API_KEY=...

# Stripe
STRIPE_SECRET_KEY=sk_live_...
STRIPE_WEBHOOK_SECRET=whsec_...
STRIPE_PUBLISHABLE_KEY=pk_live_...

# Google Drive (optional)
GOOGLE_DRIVE_CREDENTIALS_FILE=/app/credentials/service-account.json

# Email
SENDGRID_API_KEY=SG...
FROM_EMAIL=noreply@yourdomain.com
```

Edit `frontend/.env`:

```env
NEXTAUTH_URL=https://yourdomain.com
NEXTAUTH_SECRET=<random-64-char-string>
NEXT_PUBLIC_API_URL=https://api.yourdomain.com/api
```

## 2. Docker Compose (Production)

```yaml
# Add to docker-compose.yml for production:
services:
  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./certs:/etc/nginx/certs
    depends_on:
      - frontend
      - backend
```

## 3. SSL Setup

```bash
# Using Let's Encrypt
certbot certonly --standalone -d yourdomain.com -d api.yourdomain.com
```

## 4. Deploy

```bash
docker compose -f docker-compose.yml up -d --build
```

## 5. Database Migration

```bash
docker compose exec backend python -c "
import asyncio
from app.core.database import Base
from app.core.database import engine
from app.models import user, workspace, content, team
asyncio.run(Base.metadata.create_all(engine))
"
```

## 6. Verify

```bash
# Health check
curl https://api.yourdomain.com/api/health

# Frontend
curl -o /dev/null -w "%{http_code}" https://yourdomain.com
```

## 7. Monitoring

- Health endpoint: `GET /api/health`
- Logs: `docker compose logs -f backend`
- Metrics: Check Celery worker status

## Environment Variables Reference

| Variable | Required | Description |
|----------|----------|-------------|
| `DATABASE_URL` | Yes | PostgreSQL connection string |
| `REDIS_URL` | Yes | Redis connection string |
| `SECRET_KEY` | Yes | JWT signing key (random 64 chars) |
| `OPENAI_API_KEY` | For AI | OpenAI API access |
| `STRIPE_SECRET_KEY` | For billing | Stripe API key |
| `GOOGLE_DRIVE_CREDENTIALS_FILE` | For Drive | Service account JSON |
| `SENDGRID_API_KEY` | For email | SendGrid API key |
| `ALLOWED_ORIGINS` | Yes | Comma-separated CORS origins |
| `ENVIRONMENT` | Yes | `development` or `production` |
