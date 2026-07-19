import { NextResponse } from "next/server"

/**
 * Dynamic /llms.txt endpoint — serves the AI-optimized platform guide.
 * This route provides a machine-readable overview for AI crawlers
 * and coding assistants.
 */
export async function GET() {
  const llmsContent = `# Social Media Manager — AI-Optimized Platform Guide

> AI-powered social media scheduling platform.
> 5 platforms: LinkedIn, X/Twitter, Facebook, Instagram, YouTube.
> 152 API endpoints | 73 services | 27 frontend components.

## What This Platform Does

Schedule posts across 5 social media platforms from one dashboard. Generate content with AI, A/B test variations, track analytics, and manage your entire social presence.

## Key Features

- **Multi-platform scheduling** — One post → 5 platforms
- **AI content generation** — Captions, hashtags, calendars per platform
- **A/B testing** — Test variants, auto-select winners
- **Analytics** — Cross-platform engagement tracking
- **Approval workflows** — Multi-stage review
- **Content recycling** — Auto-reshare top performers
- **Social listening** — Brand mention monitoring
- **Bulk operations** — Schedule, cancel, update in batch
- **Dead-letter queue** — Failed publish management
- **Content versioning** — Snapshot and rollback

## API

Base: /api | Auth: Bearer JWT | Docs: /api/docs

### Quick Start Endpoints
- POST /api/auth/login — Get JWT token
- POST /api/scheduler/schedule — Schedule to platforms
- GET /api/scheduler/queue — View scheduled posts
- POST /api/scheduler/captions/generate — AI caption
- POST /api/scheduler/hashtags/generate — AI hashtags
- GET /api/scheduler/analytics/cross-platform — Analytics
- GET /api/scheduler/health — Platform health

## Platforms

| Platform | Publishing | Scheduling | Analytics |
|----------|-----------|-----------|-----------|
| LinkedIn | Real API v2 | ✅ | ✅ |
| X/Twitter | Real API v2 | ✅ | ✅ |
| Facebook | Graph API v19 | ✅ | ✅ |
| Instagram | Content Publishing | ✅ | ✅ |
| YouTube | Data API v3 | Native scheduling | ✅ |

## Documentation

- /llms-full.txt — Extended API reference
- /api/docs — Swagger UI
- /docs/ARCHITECTURE.md — System architecture
- /docs/ai-discovery/capabilities.md — Feature catalog
- /docs/ai-discovery/api-reference.md — API reference
- /docs/ai-discovery/getting-started.md — Integration guide
- /.well-known/ai-plugin.json — AI agent discovery

## Links

- Repository: https://github.com/ranaprv/social-media-app
- API Docs: /api/docs
`

  return new NextResponse(llmsContent, {
    headers: {
      "Content-Type": "text/plain; charset=utf-8",
      "Cache-Control": "public, max-age=86400",
      "X-Robots-Tag": "index, follow",
    },
  })
}
