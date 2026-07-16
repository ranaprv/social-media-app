# Contributing to Social Media Manager

## Development Setup

1. Clone the repo
2. `docker compose up -d` — starts PostgreSQL, Redis, backend, frontend
3. Backend: `cd backend && pip install -r requirements.txt`
4. Frontend: `cd frontend && npm install`
5. Access: http://localhost:3001

## Code Standards

### Backend (Python/FastAPI)
- Async functions for all DB and API calls
- Pydantic schemas for request/response validation
- SQLAlchemy async ORM (never sync)
- Type hints on all functions
- Tests in `backend/tests/` with pytest

### Frontend (TypeScript/React)
- TypeScript strict mode — no `any` types
- Functional components with hooks
- Zustand for global state
- Tailwind CSS for styling
- Tests in `frontend/src/__tests__/` with Vitest

### Commits
- `feat:` — new feature
- `fix:` — bug fix
- `docs:` — documentation
- `refactor:` — code restructuring
- `test:` — adding tests
- `chore:` — maintenance

### PR Process
1. Create feature branch from `main`
2. Implement changes
3. Add/update tests
4. Run `npm run build` (frontend) and `pytest` (backend)
5. Create PR with description
6. Get 1 approval before merge

## Architecture

- **Backend:** FastAPI + SQLAlchemy async + PostgreSQL + Redis
- **Frontend:** Next.js 16 + React 19 + TypeScript + Tailwind
- **Auth:** NextAuth.js (JWT) + backend JWT
- **AI:** Multi-LLM (OpenAI, Anthropic, Gemini) via unified service
- **Queue:** Celery + Redis for background tasks
- **Storage:** AWS S3 + Google Drive
