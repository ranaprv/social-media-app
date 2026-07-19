# Social Media Manager — API Reference (AI-Optimized)

> Structured API documentation for AI coding assistants.

## Authentication

### Login
```http
POST /api/auth/login
Content-Type: application/json

{"email": "user@example.com", "password": "password"}

# Response 200
{"access_token": "eyJhbGci...", "token_type": "bearer"}
```

### Use Token
```http
GET /api/posts/{workspace_id}
Authorization: Bearer {access_token}
```

## Scheduling API

### Schedule Post to Platforms
```http
POST /api/scheduler/schedule
Authorization: Bearer {token}
Content-Type: application/json

{
  "post_id": "uuid",
  "platforms": [
    {"platform": "linkedin", "caption": "Custom text", "scheduled_at": "2026-07-20T10:00:00Z"},
    {"platform": "x", "caption": "Short version"}
  ],
  "default_scheduled_at": "2026-07-20T10:00:00Z"
}
```

### Get Queue
```http
GET /api/scheduler/queue?status=scheduled&platform=linkedin&limit=20

# Response 200
{
  "queue": [{"id": "...", "post_id": "...", "platform": "linkedin", "scheduled_at": "...", "status": "scheduled"}],
  "total": 45
}
```

### Retry Failed
```http
POST /api/scheduler/queue/{item_id}/retry
```

### Cancel
```http
DELETE /api/scheduler/queue/{item_id}
```

## AI Content API

### Generate Caption
```http
POST /api/scheduler/captions/generate
Content-Type: application/json

{"topic": "5 content marketing tips", "platform": "linkedin", "tone": "professional"}

# Response 200
{"caption": "...", "platform": "linkedin", "char_count": 245, "hashtags": ["#marketing"], "has_cta": true}
```

### Generate Hashtags
```http
POST /api/scheduler/hashtags/generate
Content-Type: application/json

{"topic": "SaaS growth", "platform": "instagram", "count": 10}

# Response 200
{"hashtags": [{"tag": "#saasgrowth", "category": "niche", "estimated_reach": "medium"}], "count": 10}
```

### Repurpose Content
```http
POST /api/scheduler/repurpose
Content-Type: application/json

{"content": "Blog post text...", "source_format": "blog", "target_formats": ["thread", "post", "carousel"]}
```

### Translate
```http
POST /api/scheduler/translate
Content-Type: application/json

{"caption": "Hello world", "target_language": "es", "platform": "linkedin"}
```

## Analytics API

### Cross-Platform Dashboard
```http
GET /api/scheduler/analytics/cross-platform?days=30

# Response 200
{
  "totals": {"impressions": 125000, "engagement": 8500, "reach": 45000},
  "by_platform": {"linkedin": {"impressions": 50000, "engagement_rate": 4.2}, ...},
  "platform_ranking": [{"rank": 1, "platform": "instagram", "engagement_rate": 5.5}],
  "best_platform": "instagram"
}
```

### Forecast
```http
POST /api/scheduler/forecast
Content-Type: application/json

{"platform": "linkedin", "content_length": 250, "has_media": true}

# Response 200
{
  "forecast": {"predicted_impressions": 1200, "predicted_engagement_rate": 4.8, "confidence": "medium"},
  "suggestions": ["Post on Tuesday at 10 AM"]
}
```

## Publishing API

### Health Check
```http
GET /api/scheduler/health

# Response 200
{
  "linkedin": {"status": "healthy", "message": "Connected as John", "latency_ms": 245},
  "x": {"status": "token_expired", "message": "Token expired"}
}
```

### Rate Limits
```http
GET /api/scheduler/rate-limits

# Response 200
{"linkedin": {"daily_limit": 100, "used_today": 15, "remaining": 85}}
```

## Content Library API

### Search Library
```http
GET /api/scheduler/library/search?query=growth&category=educational&platform=linkedin

# Response 200
{"items": [...], "total": 12, "categories": ["educational", "promotional"], "tags": ["growth", "tips"]}
```

### Save to Library
```http
POST /api/scheduler/library/save/{post_id}
Content-Type: application/json

{"tags": ["growth", "tips"], "category": "educational"}
```

## Error Format

All errors return:
```json
{
  "detail": "Human-readable error message",
  "status_code": 400
}
```

## Rate Limits

- **API:** 100 requests per 60 seconds per user
- **LinkedIn:** 100 posts/day
- **X/Twitter:** 50 tweets/day
- **Facebook:** 25 posts/page/day
- **Instagram:** 25 posts/day
- **YouTube:** 6 videos/day
