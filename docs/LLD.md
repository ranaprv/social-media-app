# Low-Level Design — ContentPilot AI

**Version:** 1.0.0
**Date:** 2026-07-16

---

## 1. Backend Module Structure

```
backend/
├── app/
│   ├── main.py                    # FastAPI app, CORS, router registration
│   ├── core/
│   │   ├── config.py              # Pydantic Settings (env vars)
│   │   ├── database.py            # SQLAlchemy async engine, session factory, Base
│   │   └── security.py            # JWT, bcrypt, OAuth2 bearer, get_current_user
│   ├── models/
│   │   ├── user.py                # User, Account, Session models
│   │   ├── workspace.py           # Workspace, WorkspaceMember models
│   │   ├── content.py             # Post, PostVersion, PlatformConnection,
│   │   │                          #   ContentCalendar, AnalyticsMetric,
│   │   │                          #   BrandVoice, Asset, Activity models
│   │   └── team.py                # Team-related models
│   ├── schemas/
│   │   └── __init__.py            # All Pydantic request/response schemas
│   ├── api/
│   │   ├── auth.py                # Registration, login, MFA, password reset
│   │   ├── workspaces.py          # Workspace CRUD, members, brand voice, assets
│   │   ├── posts.py               # Post CRUD with workspace access verification
│   │   ├── dashboard.py           # Dashboard statistics aggregation
│   │   ├── connections.py         # Platform OAuth connection management
│   │   ├── ai_content.py          # AI content generation, rewrite, repurpose
│   │   ├── ai_ideas.py            # AI idea generation with OpenAI integration
│   │   ├── ai_writing_tools.py    # 10 writing tools (rewrite, expand, etc.)
│   │   ├── ai_brand_voice.py      # Brand voice analysis and training
│   │   ├── ai_media.py            # Image, video, voiceover, caption generation
│   │   ├── recommendations.py     # Content analysis and improvement suggestions
│   │   ├── analytics.py           # Analytics dashboard, trends, comparisons
│   │   ├── billing.py             # Plans, subscription, usage, invoices, checkout
│   │   ├── security_api.py        # Audit logs, RBAC, rate limiting, OAuth, GDPR
│   │   ├── calendar.py            # Calendar events, campaigns
│   │   ├── scheduler_api.py       # Publishing queue, best times, config
│   │   ├── team.py                # Members, comments, reviews, notifications
│   │   ├── media.py               # Media library management
│   │   └── repurpose.py           # Content repurposing engine
│   ├── services/                  # (Empty — business logic inline in API modules)
│   └── utils/                     # (Empty — utilities inline)
├── tests/                         # (Empty — no test suite yet)
├── Dockerfile                     # Multi-stage Python build
├── requirements.txt               # 20 Python dependencies
└── .env / .env.example            # Environment configuration
```

---

## 2. Frontend Module Structure

```
frontend/
├── src/
│   ├── app/
│   │   ├── layout.tsx             # Root layout: fonts, ThemeProvider
│   │   ├── globals.css            # CSS variables, dark mode, glassmorphism
│   │   ├── page.tsx               # Landing/redirect page
│   │   ├── auth/
│   │   │   ├── login/page.tsx     # Login form
│   │   │   └── register/page.tsx  # Registration form
│   │   ├── dashboard/
│   │   │   ├── page.tsx           # Main dashboard with stats, recent posts
│   │   │   ├── content-studio/    # AI content creation workspace
│   │   │   ├── analytics/         # Charts, KPIs, platform comparison
│   │   │   ├── recommendations/   # AI content scoring and suggestions
│   │   │   ├── ai-assistant/      # Image/video/voiceover/caption generation
│   │   │   ├── billing/           # Plans, usage, invoices, Stripe
│   │   │   ├── security/          # RBAC, audit logs, rate limits, GDPR
│   │   │   ├── calendar/          # Content calendar views
│   │   │   ├── media/             # Media library
│   │   │   ├── repurpose/         # Content repurposing engine
│   │   │   └── team/              # Team collaboration
│   │   └── api/
│   │       └── auth/[...nextauth]/route.ts  # NextAuth handler
│   ├── components/
│   │   ├── layout/
│   │   │   ├── sidebar.tsx        # Navigation sidebar with collapse
│   │   │   ├── header.tsx         # Top bar: search, theme toggle, user menu
│   │   │   └── dashboard-layout.tsx  # Sidebar + header + content wrapper
│   │   ├── providers/
│   │   │   └── theme-provider.tsx # Dark/light/system theme context
│   │   ├── ui/
│   │   │   ├── button.tsx         # Button component (CVA variants)
│   │   │   ├── card.tsx           # Card, CardHeader, CardContent, CardTitle
│   │   │   ├── input.tsx          # Input component
│   │   │   └── dropdown-menu.tsx  # Radix dropdown menu
│   │   ├── content-studio/        # IdeaGenerator, ContentGenerator,
│   │   │                          #   WritingTools, BrandVoice
│   │   ├── calendar/              # CalendarView
│   │   ├── media/                 # MediaLibrary
│   │   ├── repurpose/             # RepurposeEngine
│   │   └── team/                  # TeamCollaboration
│   ├── stores/
│   │   └── app-store.ts           # Zustand: user, workspace, posts, filters,
│   │                              #   UI state, content studio state
│   ├── lib/
│   │   ├── auth.ts                # NextAuth configuration
│   │   └── utils.ts               # cn() helper (clsx + tailwind-merge)
│   └── types/
│       └── index.ts               # All TypeScript interfaces (470+ lines)
├── Dockerfile                     # Multi-stage Node.js build
├── next.config.ts                 # Next.js configuration
├── tsconfig.json                  # TypeScript configuration
├── prisma.config.ts               # Prisma configuration
└── package.json                   # 29 dependencies
```

---

## 3. API Endpoint Catalog

### Auth (`/api/auth`)
| Method | Path | Description |
|--------|------|-------------|
| POST | `/register` | Create user account |
| POST | `/login` | Authenticate, return JWT |
| GET | `/me` | Get current user profile |
| POST | `/forgot-password` | Request password reset |
| POST | `/reset-password` | Reset password with token |
| GET | `/mfa/setup` | Generate TOTP secret + QR |
| POST | `/mfa/verify` | Verify MFA code |
| POST | `/mfa/toggle` | Enable/disable MFA |

### Workspaces (`/api/workspaces`)
| Method | Path | Description |
|--------|------|-------------|
| POST | `/` | Create workspace |
| GET | `/` | List user's workspaces |
| GET | `/{id}` | Get workspace details |
| GET | `/{id}/members` | List workspace members |
| POST | `/{id}/members` | Invite member |
| PUT | `/{id}/members/{mid}` | Update member role |
| DELETE | `/{id}/members/{mid}` | Remove member |
| GET | `/{id}/brand-voice` | Get brand voice config |
| POST | `/{id}/brand-voice` | Update brand voice |
| GET | `/{id}/assets` | List workspace assets |
| POST | `/{id}/assets` | Create workspace asset |

### Posts (`/api/posts`)
| Method | Path | Description |
|--------|------|-------------|
| POST | `/{wid}` | Create post |
| GET | `/{wid}` | List posts (filter by platform/status) |
| GET | `/{wid}/{pid}` | Get post details |
| PUT | `/{wid}/{pid}` | Update post |
| DELETE | `/{wid}/{pid}` | Delete post |

### Dashboard (`/api/dashboard`)
| Method | Path | Description |
|--------|------|-------------|
| GET | `/{wid}/stats` | Get dashboard statistics |

### Connections (`/api/connections`)
| Method | Path | Description |
|--------|------|-------------|
| POST | `/{wid}` | Connect platform |
| GET | `/{wid}` | List connections |
| DELETE | `/{wid}/{cid}` | Disconnect platform |

### AI Content (`/api/ai`)
| Method | Path | Description |
|--------|------|-------------|
| POST | `/generate` | Generate AI content |
| POST | `/rewrite` | Rewrite for platform |
| POST | `/repurpose` | Multi-platform repurpose |

### AI Ideas (`/api/ai/ideas`)
| Method | Path | Description |
|--------|------|-------------|
| POST | `/generate` | Generate content ideas |

### AI Writing Tools (`/api/ai/writing-tools`)
| Method | Path | Description |
|--------|------|-------------|
| POST | `/process` | Process with writing tool |

### AI Brand Voice (`/api/ai/brand-voice`)
| Method | Path | Description |
|--------|------|-------------|
| POST | `/analyze` | Analyze brand voice |
| POST | `/train` | Train brand voice |

### AI Media (`/api/ai/media`)
| Method | Path | Description |
|--------|------|-------------|
| GET | `/asset-types` | Get asset types, styles, voices |
| POST | `/generate-image` | Generate AI image |
| POST | `/generate-video` | Generate AI video |
| POST | `/generate-voiceover` | Generate TTS voiceover |
| POST | `/generate-caption` | Generate platform caption |

### AI Recommendations (`/api/ai/recommendations`)
| Method | Path | Description |
|--------|------|-------------|
| GET | `/analyze` | Analyze content, get recommendations |
| POST | `/rewrite-suggestion` | Get AI rewrite suggestion |

### Analytics (`/api/analytics`)
| Method | Path | Description |
|--------|------|-------------|
| GET | `/dashboard` | Dashboard summary + trends |
| GET | `/platform-comparison` | Cross-platform metrics |
| GET | `/top-posts` | Top performing posts |
| GET | `/best-times` | Best posting times heatmap |
| GET | `/content-trends` | Content performance trends |

### Billing (`/api/billing`)
| Method | Path | Description |
|--------|------|-------------|
| GET | `/plans` | List subscription plans |
| GET | `/subscription` | Get current subscription |
| GET | `/usage` | Get usage stats |
| GET | `/invoices` | Get billing history |
| POST | `/checkout` | Create Stripe checkout session |
| POST | `/cancel` | Cancel subscription |

### Security (`/api/security`)
| Method | Path | Description |
|--------|------|-------------|
| GET | `/audit-logs` | Get audit logs (filterable) |
| GET | `/roles` | Get RBAC roles |
| GET | `/rbac/check` | Check permission |
| GET | `/rate-limit/status` | Rate limit status |
| GET | `/oauth/connections` | OAuth provider status |
| GET | `/encryption/status` | Encryption status |
| GET | `/gdpr/status` | GDPR compliance status |

### Calendar (`/api/calendar`)
| Method | Path | Description |
|--------|------|-------------|
| GET | `/events` | Get calendar events |
| POST | `/events` | Create calendar event |
| PUT | `/events/{id}` | Update event |
| DELETE | `/events/{id}` | Delete event |
| GET | `/campaigns` | List campaigns |
| POST | `/campaigns` | Create campaign |

### Scheduler (`/api/scheduler`)
| Method | Path | Description |
|--------|------|-------------|
| GET | `/config` | Get scheduler config |
| PUT | `/config` | Update config |
| GET | `/queue` | Get publishing queue |
| GET | `/best-times` | Best posting times |
| POST | `/queue/{id}/retry` | Retry failed item |
| DELETE | `/queue/{id}` | Remove from queue |

### Team (`/api/team`)
| Method | Path | Description |
|--------|------|-------------|
| GET | `/members` | List team members |
| GET | `/comments` | Get post comments |
| POST | `/comments` | Add comment |
| GET | `/reviews` | Get review requests |
| POST | `/reviews/{id}/approve` | Approve review |
| POST | `/reviews/{id}/reject` | Reject/request changes |
| GET | `/version-history` | Post version history |
| GET | `/notifications` | Get notifications |
| PUT | `/notifications/{id}/read` | Mark read |
| PUT | `/notifications/read-all` | Mark all read |

### Media (`/api/media`)
| Method | Path | Description |
|--------|------|-------------|
| GET | `/` | List media assets |
| POST | `/upload` | Upload media |
| GET | `/folders` | List folders |
| POST | `/folders` | Create folder |

---

## 4. Database Models Detail

### User
| Column | Type | Constraints |
|--------|------|-------------|
| id | String (UUID) | PK |
| email | String | UNIQUE, NOT NULL, INDEXED |
| name | String | Nullable |
| image | String | Nullable |
| hashed_password | String | Nullable |
| is_active | Boolean | Default: true |
| created_at | DateTime | Default: now |
| updated_at | DateTime | Default: now, auto-update |

### Workspace
| Column | Type | Constraints |
|--------|------|-------------|
| id | String (UUID) | PK |
| name | String | NOT NULL |
| slug | String | UNIQUE, NOT NULL |
| owner_id | String | FK → users.id, NOT NULL |
| created_at | DateTime | Default: now |
| updated_at | DateTime | Default: now, auto-update |

### Post
| Column | Type | Constraints |
|--------|------|-------------|
| id | String (UUID) | PK |
| workspace_id | String | FK → workspaces.id, NOT NULL |
| author_id | String | FK → users.id, NOT NULL |
| title | String | Nullable |
| content | String | NOT NULL |
| media_urls | ARRAY(String) | Default: [] |
| platform | String | NOT NULL |
| status | String | Default: "draft" |
| scheduled_at | DateTime | Nullable |
| published_at | DateTime | Nullable |
| platform_post_id | String | Nullable |
| metadata | JSON | Default: {} |
| created_at | DateTime | Default: now |
| updated_at | DateTime | Default: now, auto-update |

### PlatformConnection
| Column | Type | Constraints |
|--------|------|-------------|
| id | String (UUID) | PK |
| workspace_id | String | FK → workspaces.id, NOT NULL |
| platform | String | NOT NULL |
| platform_user_id | String | NOT NULL |
| platform_username | String | NOT NULL |
| access_token | String | NOT NULL |
| refresh_token | String | Nullable |
| expires_at | DateTime | Nullable |
| metadata | JSON | Default: {} |

### AnalyticsMetric
| Column | Type | Constraints |
|--------|------|-------------|
| id | String (UUID) | PK |
| post_id | String | FK → posts.id, NOT NULL |
| platform | String | NOT NULL |
| impressions | Integer | Default: 0 |
| reach | Integer | Default: 0 |
| engagement | Integer | Default: 0 |
| likes | Integer | Default: 0 |
| comments | Integer | Default: 0 |
| shares | Integer | Default: 0 |
| clicks | Integer | Default: 0 |
| watch_time | Integer | Nullable |
| subscribers | Integer | Nullable |
| recorded_at | DateTime | Default: now |

### BrandVoice
| Column | Type | Constraints |
|--------|------|-------------|
| id | String (UUID) | PK |
| workspace_id | String | FK → workspaces.id, UNIQUE, NOT NULL |
| tone | String | Nullable |
| writing_style | String | Nullable |
| cta_style | String | Nullable |
| emoji_usage | String | Nullable |
| formatting | String | Nullable |
| vocabulary | String | Nullable |
| technical_depth | String | Nullable |
| sample_posts | ARRAY(String) | Default: [] |
| training_sources | JSON | Default: [] |
| approval_history | JSON | Default: [] |

---

## 5. State Management (Zustand Store)

```typescript
interface AppState {
  // Auth
  user: User | null
  setUser(user)

  // Workspace
  currentWorkspace: Workspace | null
  workspaces: Workspace[]
  setCurrentWorkspace(workspace)
  setWorkspaces(workspaces)

  // Posts
  posts: Post[]
  setPosts(posts) / addPost(post) / updatePost(id, updates) / deletePost(id)

  // Filters
  selectedPlatform: Platform | "all"
  selectedStatus: PostStatus | "all"

  // UI
  sidebarOpen: boolean
  toggleSidebar()

  // Content Studio
  activeStudioTab: "ideas" | "generate" | "tools" | "brand-voice"
  generatedIdeas: GeneratedIdea[]
  activeWritingTool: WritingTool
  brandVoice: BrandVoiceConfig | null
  contentStudioLoading: boolean
}
```

---

## 6. Theme System

```
ThemeProvider (React Context)
  ├── theme: "light" | "dark" | "system"
  ├── resolvedTheme: "light" | "dark"
  └── setTheme(theme)

Storage: localStorage["contentpilot-theme"]

CSS Strategy:
  :root { /* light variables */ }
  .dark { /* dark variables */ }

Application:
  document.documentElement.classList.toggle("dark")

Header Toggle:
  Sun icon → Light
  Moon icon → Dark
  Monitor icon → System
```

---

## 7. AI Integration Patterns

### OpenAI Integration
```python
async def _call_ai(prompt: str, system_prompt: str = "") -> str:
    settings = get_settings()
    if settings.OPENAI_API_KEY:
        client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        response = await client.chat.completions.create(
            model="gpt-4o", messages=messages,
            temperature=0.7, max_tokens=3000,
        )
        return response.choices[0].message.content or ""
    return ""
```

### Fallback Pattern
Every AI endpoint follows:
1. Check if API key is configured
2. If yes → call AI provider
3. If no or error → return placeholder/mock response
4. Frontend always displays result (real or placeholder)

---

## 8. Frontend Route Map

| Route | Page | Layout |
|-------|------|--------|
| `/` | Landing page | None |
| `/auth/login` | Login form | Auth layout |
| `/auth/register` | Registration form | Auth layout |
| `/dashboard` | Main dashboard | DashboardLayout |
| `/dashboard/content-studio` | Content creation | DashboardLayout |
| `/dashboard/analytics` | Analytics dashboard | DashboardLayout |
| `/dashboard/recommendations` | AI recommendations | DashboardLayout |
| `/dashboard/ai-assistant` | AI media generation | DashboardLayout |
| `/dashboard/billing` | Billing & subscription | DashboardLayout |
| `/dashboard/security` | Security settings | DashboardLayout |
| `/dashboard/calendar` | Content calendar | DashboardLayout |
| `/dashboard/media` | Media library | DashboardLayout |
| `/dashboard/repurpose` | Content repurposing | DashboardLayout |
| `/dashboard/team` | Team collaboration | DashboardLayout |

---

## 9. Error Handling Strategy

### Backend
- Pydantic validation → 422 with field errors
- Auth failures → 401 with WWW-Authenticate header
- Not found → 404 with detail message
- Forbidden → 403 with permission detail
- Bad request → 400 with specific error
- Rate limited → 429 (planned)

### Frontend
- API fetch errors → fall back to mock data
- Render errors → React error boundaries (planned)
- Loading states → Skeleton/spinner per page
