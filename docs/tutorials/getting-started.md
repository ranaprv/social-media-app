# Tutorial: Get Your First AI-Generated Post Live

This tutorial walks you from a fresh clone to publishing your first AI-generated social media post. By the end, you'll have the app running, a workspace configured, a connected social platform, and a published post.

**Time:** ~20 minutes
**What you'll build:** A working social media management setup with one connected platform and one AI-generated post.

---

## What you'll need

- Node.js 18+ and Python 3.11+
- PostgreSQL (local or Docker)
- Redis (local or Docker)
- At least one LLM API key (OpenAI, Anthropic, or Google AI)

---

## Step 1: Clone and start the backend

```bash
git clone https://github.com/ranaprv/social-media-app.git
cd social-media-app/backend
```

Create your environment file:

```bash
cp .env.example .env
```

Edit `.env` and set at least:

```env
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/socialmediamanager
REDIS_URL=redis://localhost:6379/0
SECRET_KEY=dev-secret-key-change-in-production
OPENAI_API_KEY=sk-your-key-here
```

Start the database (if using Docker):

```bash
docker run -d --name smm-postgres -p 5432:5432 \
  -e POSTGRES_USER=postgres \
  -e POSTGRES_PASSWORD=postgres \
  -e POSTGRES_DB=socialmediamanager \
  postgres:16-alpine

docker run -d --name smm-redis -p 6379:6379 redis:alpine
```

Run the backend:

```bash
pip install -r requirements.txt
alembic upgrade head
uvicorn app.main:app --reload --port 8000
```

Verify it's running:

```bash
curl http://localhost:8000/api/health
```

You should see `{"status": "healthy"}`.

---

## Step 2: Start the frontend

```bash
cd ../frontend
npm install
cp .env.local.example .env.local
```

Edit `.env.local`:

```env
NEXTAUTH_URL=http://localhost:3000
NEXTAUTH_SECRET=dev-secret
NEXT_PUBLIC_API_URL=http://localhost:8000/api
AUTH_API_URL=http://localhost:8000/api
```

Start the dev server:

```bash
npm run dev
```

Open [http://localhost:3000](http://localhost:3000). You'll see the landing page with "Get Started" and "Log in" buttons.

---

## Step 3: Create your account

1. Click **Get Started**
2. Enter your name, email, and password
3. Click **Create Account**

You'll be redirected to the dashboard. It starts empty — that's expected.

---

## Step 4: Connect a social platform

1. In the sidebar, click **Accounts** (or navigate to `/dashboard/connections`)
2. Click **Connect** next to the platform you want (e.g., LinkedIn)
3. Authorize the app in the platform's OAuth flow
4. You'll see the connection appear as "Connected"

If you don't have OAuth credentials yet, you can still generate content — just skip publishing and copy the output manually.

---

## Step 5: Generate your first AI post

1. Click **Content Studio** in the sidebar
2. In the **AI Content Generator**, type a topic: `"5 tips for remote team productivity"`
3. Select your target platform (e.g., LinkedIn)
4. Choose a tone: **Professional**
5. Click **Generate**

The AI produces a post with a hook, body, and CTA. You can:
- Click **Rewrite** to get a different version
- Edit the text directly
- Click **Copy** to grab it

---

## Step 6: Schedule or publish

1. From the Content Studio, click **Schedule** or **Publish Now**
2. If scheduling: pick a date and time from the calendar
3. If publishing: the app sends it directly to your connected platform

Check your connected platform — the post should appear.

---

## What you built

You now have:
- A running backend + frontend
- A registered account with a workspace
- One connected social platform
- One AI-generated post published to that platform

**Next steps:**
- [How to: Connect Social Platforms](../how-to/connect-social-platforms.md) — OAuth setup, multiple accounts
- [How to: Generate AI Content](../how-to/generate-ai-content.md) — all generation options, writing tools
- [How to: Configure Brand Voice](../how-to/configure-brand-voice.md) — train the AI on your style
- [How to: Use Analytics](../how-to/use-analytics-dashboard.md) — track performance
- [Architecture](../ARCHITECTURE.md) — how the system is built
