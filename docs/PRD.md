# Product Requirements Document — ContentPilot AI

**Version:** 1.0.0
**Date:** 2026-07-16
**Status:** Implemented

---

## 1. Product Overview

ContentPilot AI is an AI-powered social media content management platform that enables individuals, creators, and teams to generate, schedule, manage, and analyze content across LinkedIn, X (Twitter), Instagram, Facebook, and YouTube from a single dashboard.

---

## 2. Target Users

| Persona | Description |
|---------|-------------|
| Solo Creator | Independent content creator managing 1-3 social accounts |
| Marketing Team | Small team (2-10) collaborating on brand content across platforms |
| Agency | Multi-client management with workspace isolation |
| Enterprise | Large org with SSO, custom AI models, dedicated support |

---

## 3. Core Features

### 3.1 Authentication & User Management
- Email/password registration and login
- JWT-based session management (30-minute expiry)
- OAuth providers: Google, GitHub
- MFA setup via TOTP (QR code generation)
- Forgot/reset password flow
- Password hashing with bcrypt

### 3.2 Workspace System
- Multi-workspace support per user
- Role-based access: Owner, Admin, Editor, Viewer
- Workspace members: invite, update role, remove
- Slug-based workspace identification
- Per-workspace brand voice configuration
- Per-workspace asset management

### 3.3 Content Creation & Management
- CRUD operations for posts (draft → review → scheduled → publishing → published → failed)
- Platform-specific content generation (LinkedIn, X, Instagram, Facebook, YouTube)
- Content types: posts, threads, carousels, reels, shorts, newsletters, emails
- Media attachment support (images, videos)
- Post version history tracking
- Content repurposing across platforms

### 3.4 AI Content Studio
- **Idea Generator:** Industry-aware content idea generation with category filtering
- **Content Generator:** Platform-specific post generation with tone/length/keyword controls
- **Writing Tools:** Rewrite, expand, summarize, translate, grammar check, hook/CTA/hashtag generation, SEO optimization, tone adjustment
- **Brand Voice Training:** Tone, writing style, CTA style, emoji usage, formatting, vocabulary configuration with sample posts and approval history

### 3.5 AI Media Assistant
- **Image Generator:** Social graphics, carousels, infographics, quote cards, YouTube thumbnails with 10 style presets
- **Video Generator:** Reels and YouTube Shorts with duration control (5-60s)
- **Voiceover Generator:** TTS with 6 voice options (Alloy, Echo, Fable, Onyx, Nova, Shimmer), speed control (0.5x-2x)
- **Caption Generator:** Platform-optimized captions with emoji/hashtag toggles

### 3.6 AI Recommendations
- Content score analysis (0-100 gauge)
- 6-dimension content analysis: readability, emotional impact, specificity, originality, CTA strength, hook power
- Prioritized recommendations (high/medium/low) with impact estimates
- Headline, hook, CTA, posting time, hashtag, viral potential, engagement prediction suggestions
- One-click apply/dismiss per recommendation
- Rewrite suggestion endpoint

### 3.7 Content Calendar
- Daily/weekly/monthly calendar views
- Drag-and-drop event scheduling
- Campaign management (color-coded, date ranges)
- Recurring post support (daily/weekly/monthly)
- Platform and status filtering
- Best posting times per platform

### 3.8 Publishing Scheduler
- Queue-based publishing system with retry logic (max 3 retries)
- Platform-specific best posting times (researched data per platform)
- Timezone support (12 timezones)
- Auto-publish toggle per platform
- Queue management: retry, remove, view

### 3.9 Analytics Dashboard
- KPI cards: reach, impressions, engagement, followers, subscribers, watch time, clicks, CTR, leads, conversions
- Trend charts: reach, impressions, engagement over time (line charts)
- Platform comparison (bar chart)
- Content type distribution (pie chart)
- Best posting times heatmap (7-day × 17-hour grid)
- Top performing posts table with engagement rates
- Period filtering: 7 days, 30 days, 90 days

### 3.10 Team Collaboration
- Team member management with roles
- Comment threads on posts with replies
- Review request workflow (pending → approved/changes-requested/rejected)
- Version history per post with change notes
- Notification system (review requests, comments, approvals, mentions, assignments)
- Mark read/unread, mark all read

### 3.11 Media Library
- Asset management (images, videos, PDFs, brand assets, logos, templates)
- Folder organization
- Search with type/tag filtering
- Sort by name/date/size
- Upload tracking

### 3.12 Platform Connections
- OAuth connection to LinkedIn, X, Instagram, Facebook, YouTube
- Access token and refresh token storage
- Connect/disconnect per platform
- Connection status tracking

### 3.13 Billing & Subscription
- 4 subscription tiers:
  - **Free:** 50 AI credits/mo, 3 platforms, 1 workspace
  - **Pro ($29/mo):** 500 credits, all platforms, 5 workspaces, brand voice, calendar, repurposing
  - **Business ($99/mo):** 2,000 credits, unlimited workspaces, team collab, media library, custom integrations
  - **Enterprise ($299/mo):** Unlimited everything, SSO/SAML, SLA, custom AI models, API access
- Stripe checkout integration
- Usage tracking: credits, workspaces, team members, media storage, scheduled posts, platforms
- Invoice history with download
- Subscription management: upgrade, downgrade, cancel at period end

### 3.14 Security & Compliance
- **RBAC:** Owner (level 4, all permissions), Admin (level 3), Editor (level 2), Viewer (level 1)
- **Audit Logs:** Action tracking with user, resource, details, timestamp, IP
- **Rate Limiting:** 100 requests per 60-second window per user
- **OAuth Connections:** Google, GitHub, LinkedIn, Twitter, Facebook, YouTube status
- **Encryption:** AES-256-GCM for API keys and OAuth tokens, key rotation enabled
- **GDPR:** DPA, consent recording, right to erasure, data portability, DPO contact

### 3.15 Dark/Light Mode
- Theme toggle: Light, Dark, System (follows OS preference)
- Persisted to localStorage
- CSS class-based switching (`.dark` selector)
- Smooth transition animations

---

## 4. Non-Functional Requirements

| Requirement | Target |
|-------------|--------|
| API Response Time | < 200ms (p95) |
| Frontend Load Time | < 3s (LCP) |
| Availability | 99.9% uptime |
| Data Encryption | AES-256 at rest, TLS 1.3 in transit |
| Auth Token Expiry | 30 minutes |
| Rate Limit | 100 req/60s per user |
| Browser Support | Chrome, Firefox, Safari, Edge (latest 2 versions) |
| Responsive | Mobile, tablet, desktop |

---

## 5. AI Provider Integration

| Provider | Use Case | Fallback |
|----------|----------|----------|
| OpenAI (GPT-4o) | Content generation, recommendations, captions, repurposing | Placeholder responses |
| OpenAI (TTS-1) | Voiceover generation | Placeholder audio |
| OpenAI (DALL-E) | Image generation | Placeholder images |
| Anthropic | Alternative content generation | — |
| Google Gemini | Alternative content generation | — |

All AI features gracefully degrade to placeholder/mock responses when API keys are not configured.

---

## 6. Supported Platforms

| Platform | Content Types | API Integration |
|----------|---------------|-----------------|
| LinkedIn | Posts, carousels, polls, articles | OAuth 2.0 |
| X (Twitter) | Tweets, threads | OAuth 2.0 |
| Instagram | Reels, carousels, captions | OAuth 2.0 |
| Facebook | Posts, stories | Graph API |
| YouTube | Shorts, long-form scripts, descriptions | OAuth 2.0 |

---

## 7. Success Metrics

| Metric | Target |
|--------|--------|
| User Registration | 1,000 signups/month |
| DAU/MAU Ratio | > 30% |
| Content Created | 10,000 posts/month |
| AI Credits Used | 500K/month |
| Paid Conversion (Free → Pro) | > 5% |
| Net Revenue Retention | > 110% |
