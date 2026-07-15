# ContentPilot AI

AI-Powered Social Media Research, Content Creation & Scheduling Platform

## Tech Stack

- **Frontend:** Next.js 14+, React, TypeScript, Tailwind CSS
- **Backend:** FastAPI, Python 3.12
- **Database:** PostgreSQL 16
- **Cache:** Redis 7
- **Queue:** Celery (planned)
- **AI:** OpenAI, Anthropic, Google Gemini
- **Auth:** NextAuth.js with Google, GitHub, Email
- **Payments:** Stripe (planned)

## Quick Start

### Prerequisites

- Node.js 20+
- Python 3.12+
- PostgreSQL 16
- Redis 7

### Development

1. **Clone and install dependencies:**

```bash
# Frontend
cd frontend
npm install

# Backend
cd ../backend
pip install -r requirements.txt
```

2. **Set up environment:**

```bash
# Backend
cp .env.example .env
# Edit .env with your credentials
```

3. **Start databases with Docker:**

```bash
docker-compose up -d postgres redis
```

4. **Run migrations:**

```bash
cd frontend
npx prisma migrate dev
```

5. **Start development servers:**

```bash
# Terminal 1 - Frontend
cd frontend
npm run dev

# Terminal 2 - Backend
cd backend
uvicorn app.main:app --reload --port 8000
```

6. **Open:** http://localhost:3000

## Project Structure

```
social-media-app/
├── frontend/           # Next.js 14+ app
│   ├── src/
│   │   ├── app/        # App Router pages
│   │   ├── components/ # React components
│   │   ├── lib/        # Utilities
│   │   ├── stores/     # Zustand state
│   │   └── types/      # TypeScript types
│   └── prisma/         # Database schema
├── backend/            # FastAPI app
│   ├── app/
│   │   ├── api/        # API routes
│   │   ├── core/       # Config, DB, auth
│   │   ├── models/     # SQLAlchemy models
│   │   └── schemas/    # Pydantic schemas
│   └── requirements.txt
├── docker-compose.yml
└── README.md
```

## API Documentation

Once running, visit: http://localhost:8000/api/docs

## Environment Variables

See `.env.example` in the backend directory for all required variables.

## License

MIT
