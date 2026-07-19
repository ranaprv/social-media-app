# Social Media Manager — Getting Started (AI Assistant Guide)

> Quick reference for AI coding assistants helping developers integrate with this platform.

## Prerequisites

1. Running instance of Social Media Manager (Docker or manual)
2. API access at `http://localhost:8000/api`
3. User account with valid JWT token

## Step 1: Authenticate

```bash
# Register (if needed)
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email": "dev@example.com", "password": "password123", "name": "Developer"}'

# Login
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "dev@example.com", "password": "password123"}'
# Save access_token from response
```

## Step 2: Connect a Platform

```bash
# Connect LinkedIn (requires OAuth — use the UI for initial auth)
# After connecting via OAuth, the token is stored automatically
curl http://localhost:8000/api/connections/ \
  -H "Authorization: Bearer {token}"
# Returns list of connected platforms
```

## Step 3: Create a Post

```bash
# Create a draft post
curl -X POST http://localhost:8000/api/posts/{workspace_id} \
  -H "Authorization: Bearer {token}" \
  -H "Content-Type: application/json" \
  -d '{"content": "Hello world!", "platform": "linkedin", "status": "draft"}'
```

## Step 4: Schedule to Multiple Platforms

```bash
# Schedule to LinkedIn and X with custom captions
curl -X POST http://localhost:8000/api/scheduler/schedule \
  -H "Authorization: Bearer {token}" \
  -H "Content-Type: application/json" \
  -d '{
    "post_id": "{post_id}",
    "platforms": [
      {"platform": "linkedin", "caption": "Professional version"},
      {"platform": "x", "caption": "Short X version"}
    ],
    "default_scheduled_at": "2026-07-20T10:00:00Z"
  }'
```

## Step 5: Generate AI Captions

```bash
# Generate platform-specific caption
curl -X POST http://localhost:8000/api/scheduler/captions/generate \
  -H "Authorization: Bearer {token}" \
  -H "Content-Type: application/json" \
  -d '{"topic": "5 tips for social media", "platform": "linkedin", "tone": "professional"}'
```

## Step 6: Check Queue Status

```bash
# See scheduled posts
curl http://localhost:8000/api/scheduler/queue \
  -H "Authorization: Bearer {token}"

# Check platform health
curl http://localhost:8000/api/scheduler/health \
  -H "Authorization: Bearer {token}"
```

## Step 7: View Analytics

```bash
# Cross-platform analytics
curl http://localhost:8000/api/scheduler/analytics/cross-platform?days=30 \
  -H "Authorization: Bearer {token}"

# Predict engagement
curl -X POST http://localhost:8000/api/scheduler/forecast \
  -H "Authorization: Bearer {token}" \
  -H "Content-Type: application/json" \
  -d '{"platform": "linkedin", "content_length": 200, "has_media": true}'
```

## Quick Reference

| Action | Endpoint | Method |
|--------|----------|--------|
| Login | `/api/auth/login` | POST |
| Create post | `/api/posts/{ws_id}` | POST |
| Schedule | `/api/scheduler/schedule` | POST |
| Queue | `/api/scheduler/queue` | GET |
| AI caption | `/api/scheduler/captions/generate` | POST |
| Hashtags | `/api/scheduler/hashtags/generate` | POST |
| Analytics | `/api/scheduler/analytics/cross-platform` | GET |
| Health | `/api/scheduler/health` | GET |
| Repurpose | `/api/scheduler/repurpose` | POST |
| Translate | `/api/scheduler/translate` | POST |

## Common Workflows

### Publish-Ready Workflow
1. Generate caption: `POST /captions/generate`
2. Generate hashtags: `POST /hashtags/generate`
3. Create post: `POST /posts/{ws_id}`
4. Schedule to platforms: `POST /scheduler/schedule`
5. Monitor queue: `GET /scheduler/queue`
6. View results: `GET /analytics/cross-platform`

### Content Recycling Workflow
1. Find top performers: `GET /recycle/top-performers`
2. Get best time: `GET /recommendations/next-slot?platform=linkedin`
3. Schedule recycle: `POST /recycle/schedule`

### A/B Testing Workflow
1. Create variants: `POST /ab-test/create`
2. Wait for results: (time passes)
3. Check results: `GET /ab-test/{id}/results`
4. Auto-select winner: `POST /ab-test/{id}/auto-winner`
