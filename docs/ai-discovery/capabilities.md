# Social Media Manager — AI Feature Catalog

> Machine-readable feature documentation for AI crawlers and coding assistants.

## Feature Matrix

### Publishing Features

| Feature | Description | API Endpoint | Platform Support |
|---------|-------------|-------------|-----------------|
| Multi-platform scheduling | Schedule one post to multiple platforms | `POST /api/scheduler/schedule` | All 5 |
| Platform-specific captions | Custom caption per platform | `POST /api/scheduler/schedule` | All 5 |
| Recurring posts | Automated daily/weekly/monthly patterns | `POST /api/scheduler/recurring/create` | All 5 |
| Content dependencies | Post A before post B | `POST /api/scheduler/dependencies/add` | All 5 |
| Native YouTube scheduling | `publishAt` parameter for deferred publish | YouTube publisher | YouTube only |
| Bulk scheduling | Schedule multiple posts at once | `POST /api/scheduler/bulk/schedule` | All 5 |
| Drag-and-drop reschedule | Move posts on calendar | `POST /api/scheduler/calendar/reschedule/{id}` | All 5 |

### AI Features

| Feature | Description | API Endpoint |
|---------|-------------|-------------|
| AI caption generation | Platform-specific captions with tone | `POST /api/scheduler/captions/generate` |
| AI content adaptation | Rewrite content per platform | `POST /api/scheduler/adapt-content` |
| AI calendar generation | Full month content plans | `POST /api/scheduler/calendar/generate` |
| Content repurposing | Blog → thread → carousel → reel | `POST /api/scheduler/repurpose` |
| Multi-language translation | 20 languages | `POST /api/scheduler/translate` |
| Hashtag strategy | AI hashtag research | `POST /api/scheduler/hashtags/generate` |
| Content scoring | Predict engagement 0-100 | `POST /api/scheduler/score-content` |
| Content forecasting | Predict performance from history | `POST /api/scheduler/forecast` |

### Analytics Features

| Feature | Description | API Endpoint |
|---------|-------------|-------------|
| Cross-platform analytics | Unified metrics view | `GET /api/scheduler/analytics/cross-platform` |
| Cohort analysis | Group by platform/time/type | `GET /api/scheduler/analytics/cohorts` |
| Audience growth tracking | Follower/reach trends | `GET /api/scheduler/analytics/audience-growth` |
| Content gap analysis | Missing topics identification | `POST /api/scheduler/analytics/content-gaps` |
| Industry benchmarking | Compare to 5 industries | `GET /api/scheduler/benchmarks/{industry}` |
| Best time recommendations | Data-driven scheduling | `GET /api/scheduler/recommendations/best-times` |

### Quality Features

| Feature | Description | API Endpoint |
|---------|-------------|-------------|
| 10-dimension quality rubric | Content scoring | `POST /api/scheduler/quality/score` |
| Compliance checking | Platform ToS validation | `POST /api/scheduler/compliance/check` |
| Brand voice checking | Consistency scoring | `POST /api/scheduler/brand-voice/check` |
| Post preview | Platform-specific preview | `POST /api/scheduler/preview` |
| UTM builder | Auto-tag links | `POST /api/scheduler/utm/build` |

### Operations Features

| Feature | Description | API Endpoint |
|---------|-------------|-------------|
| Approval workflow | Request → approve → publish | `POST /api/scheduler/approval/request` |
| A/B testing | Variant testing + auto winner | `POST /api/scheduler/ab-test/create` |
| Dead-letter queue | Failed publish management | `GET /api/scheduler/dead-letter` |
| Content versioning | Snapshot + rollback | `POST /api/scheduler/versions/snapshot/{id}` |
| Content library | Save + reuse content | `GET /api/scheduler/library/search` |
| Automation rules | If-then scheduling | `GET /api/scheduler/automation/rules` |

### Enterprise Features

| Feature | Description | API Endpoint |
|---------|-------------|-------------|
| API key management | Generate/revoke keys | `POST /api/scheduler/api-keys/create` |
| Bulk import/export | CSV import/export | `POST /api/scheduler/import/csv` |
| Report generation | HTML/JSON reports | `GET /api/scheduler/reports/analytics` |
| Team workload balancing | Distribute posts | `GET /api/scheduler/team/workload` |
| Audit logging | 17 action types | `GET /api/scheduler/audit` |
| Social listening | Brand mention monitoring | `POST /api/scheduler/listening/scan` |

## Platform Publishers

| Platform | API | Auth | Status |
|----------|-----|------|--------|
| LinkedIn | REST API v2 | OAuth 2.0 | Production-ready |
| X/Twitter | API v2 + v1.1 | OAuth 2.0 PKCE | Production-ready |
| Facebook | Graph API v19 | Page token | Production-ready |
| Instagram | Content Publishing API | FB Page token | Production-ready |
| YouTube | Data API v3 | OAuth 2.0 | Production-ready |

## AI Providers

| Provider | Models | Use Case |
|----------|--------|----------|
| OpenAI | GPT-4o, GPT-4o Mini | Primary content generation |
| Anthropic | Claude Sonnet 4, Haiku | Alternative, high quality |
| Google Gemini | Gemini 2.0/2.5 Flash | Fast, cost-effective |
| OpenRouter | 200+ models | Model routing |
| DeepSeek | V3, R1 | Cost-effective reasoning |
