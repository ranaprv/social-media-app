# Feature Specifications — Strategy-Driven Content Scheduling Engine (Phase 1)

**Status**: Draft  
**Author**: Product Manager  
**Version**: 1.0  
**Date**: 2026-07-18  
**PRD Reference**: `docs/prd-strategy-driven-scheduling-engine.md`

---

## TABLE OF CONTENTS

1. [Feature 1: Strategy Wizard](#feature-1-strategy-wizard)
2. [Feature 2: AI Content Generation](#feature-2-ai-content-generation)
3. [Feature 3: Smart Scheduling](#feature-3-smart-scheduling)
4. [Feature 4: Approval Flow](#feature-4-approval-flow)
5. [Feature 5: Adherence Dashboard](#feature-5-adherence-dashboard)

---

## Feature 1: Strategy Wizard

### 1.1 UI/UX Wireframe Description

**Full-page wizard with sidebar progress indicator** (decided in PRD open questions — too complex for a modal).

**Layout:**
```
┌─────────────────────────────────────────────────────────────────┐
│  ← Back to Dashboard          Strategy Setup              [X]  │
├──────────┬──────────────────────────────────────────────────────┤
│          │                                                      │
│ Progress │  Step Content Area                                   │
│ Sidebar  │                                                      │
│          │  ┌────────────────────────────────────────────────┐  │
│ ● Goals  │  │  [Dynamic content based on active step]        │  │
│ ○ Pillars│  │                                                │  │
│ ○ Audienc│  │                                                │  │
│ ○ Freq.  │  │                                                │  │
│ ○ Brand  │  │                                                │  │
│ ○ Review │  │                                                │  │
│          │  └────────────────────────────────────────────────┘  │
│          │                                                      │
│          │  ┌──────────┐  ┌──────────┐  ┌─────────────────┐   │
│          │  │  ← Back  │  │  Next →  │  │ Quick Start ⚡  │   │
│          │  └──────────┘  └──────────┘  └─────────────────┘   │
├──────────┴──────────────────────────────────────────────────────┤
│  Connected: LinkedIn ✓  Instagram ✓  X ✓  Facebook ○  YT ○   │
└─────────────────────────────────────────────────────────────────┘
```

**Step 1 — Goals:**
- Multi-select goal cards: `Grow Followers`, `Increase Engagement`, `Generate Leads`, `Build Brand Awareness`
- Each selected goal reveals fields: target metric, numeric target, time period (weekly/monthly/quarterly)
- Platform scope: "All platforms" or select specific ones
- Default targets auto-filled based on workspace analytics baseline (fetched from `AnalyticsMetric`)

**Step 2 — Content Pillars:**
- Default 3 pillars pre-loaded based on workspace industry (from `BrandVoice` or workspace metadata)
- Each pillar is a card with: name, description, weight slider (0-100%, auto-normalized), platform checkboxes, tone dropdown
- "+ Add Pillar" button (max 5)
- AI-suggest button: "Suggest pillars for my industry" → calls LLM with workspace context
- Example hooks text area per pillar (comma-separated)

**Step 3 — Audience:**
- Audience persona cards (add up to 3)
- Each card: persona name, demographics (age range dropdown, location, role), pain points (tag input), content preferences (tag input)
- AI-assisted: "Analyze my connected audiences" → infers from platform connection metadata

**Step 4 — Frequency:**
- Per-platform grid: platform icon × rows for Mon-Sun × time slot pickers
- Each platform row shows: posts/week slider (1-14), preferred days (checkboxes), preferred hours (time pickers)
- Auto-fill button: "Use optimal times" → populates from `BEST_TIMES` in `scheduler_api.py`
- Visual indicator: total weekly posts count and estimated monthly output

**Step 5 — Brand Voice (optional, skip if BrandVoice already configured):**
- Link to existing `BrandVoice` config
- Per-pillar tone override: dropdown (professional, casual, authoritative, friendly, witty)
- Content do's and don'ts: tag input

**Step 6 — Review & Activate:**
- Strategy summary card: all config in read-only format
- Preview: "What your first week looks like" — calendar grid showing planned posts by pillar color
- Action buttons: `Save as Draft` | `Activate Strategy → Generate Content`
- Warning if no BrandVoice configured: "Content quality improves with a defined brand voice"

### 1.2 Data Model

**New table: `content_strategies`**

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `id` | `String(36)` | PK | UUID primary key |
| `workspace_id` | `String(36)` | FK → `workspaces.id`, NOT NULL, INDEX | Owning workspace |
| `name` | `String(200)` | NOT NULL | Strategy name (e.g., "Q3 LinkedIn Growth") |
| `goals` | `JSON` | NOT NULL, DEFAULT `[]` | Array of goal objects (see schema below) |
| `content_pillars` | `JSON` | NOT NULL, DEFAULT `[]` | Array of pillar objects (see schema below) |
| `audience_personas` | `JSON` | NOT NULL, DEFAULT `[]` | Array of persona objects (see schema below) |
| `posting_frequency` | `JSON` | NOT NULL, DEFAULT `{}` | Per-platform frequency config (see schema below) |
| `brand_voice_overrides` | `JSON` | DEFAULT `{}` | Per-pillar tone overrides |
| `status` | `String(16)` | NOT NULL, DEFAULT `"draft"`, INDEX | `draft` \| `active` \| `paused` \| `archived` |
| `auto_generate` | `Boolean` | NOT NULL, DEFAULT `true` | Auto-generate weekly content |
| `generate_ahead_days` | `Integer` | NOT NULL, DEFAULT `7` | Days ahead to generate |
| `approval_required` | `Boolean` | NOT NULL, DEFAULT `true` | Require human approval |
| `auto_approve_threshold` | `Float` | DEFAULT `0.85` | Brand voice score threshold for auto-approve |
| `last_generated_at` | `DateTime` | NULLABLE | Last content generation timestamp |
| `created_by` | `String(36)` | FK → `users.id`, NOT NULL | Creator |
| `created_at` | `DateTime` | NOT NULL, DEFAULT `now()` | Creation timestamp |
| `updated_at` | `DateTime` | NOT NULL, DEFAULT `now()` | Last update timestamp |

**JSON Schema: `goals` array element**

```json
{
  "type": "follower_growth | engagement_rate | lead_generation | brand_awareness",
  "target": 500,
  "platform": "all | linkedin | x | instagram | facebook | youtube",
  "period": "weekly | monthly | quarterly",
  "baseline": 200
}
```

**JSON Schema: `content_pillars` array element**

```json
{
  "name": "Thought Leadership",
  "description": "Industry insights, trend analysis, professional opinions",
  "weight": 0.4,
  "platforms": ["linkedin", "x"],
  "tone": "authoritative",
  "example_hooks": [
    "Here's what most people get wrong about...",
    "I spent 5 years learning this the hard way..."
  ],
  "content_types": ["text_post", "article", "thread"]
}
```

**JSON Schema: `audience_personas` array element**

```json
{
  "name": "Tech Startup Founders",
  "demographics": {
    "age_min": 25,
    "age_max": 40,
    "roles": ["founder", "CEO", "CTO"],
    "industries": ["SaaS", "tech"],
    "company_size": "10-200"
  },
  "pain_points": ["scaling challenges", "hiring", "product-market fit"],
  "content_preferences": ["data-driven", "actionable", "no fluff"]
}
```

**JSON Schema: `posting_frequency` object**

```json
{
  "linkedin": {
    "posts_per_week": 3,
    "preferred_days": [1, 2, 3],
    "preferred_hours": [8, 12, 17]
  }
}
```

**New table: `strategy_audit_log`**

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `id` | `String(36)` | PK | UUID |
| `strategy_id` | `String(36)` | FK → `content_strategies.id`, NOT NULL, INDEX | Strategy reference |
| `workspace_id` | `String(36)` | FK → `workspaces.id`, NOT NULL | Workspace |
| `user_id` | `String(36)` | FK → `users.id`, NOT NULL | Actor |
| `action` | `String(32)` | NOT NULL | `created` \| `activated` \| `paused` \| `updated` \| `archived` |
| `changes` | `JSON` | NULLABLE | Diff of changed fields |
| `created_at` | `DateTime` | NOT NULL, DEFAULT `now()` | Timestamp |

### 1.3 API Endpoints

**Strategy Management**

| Method | Path | Description | Request Body | Response |
|--------|------|-------------|-------------|----------|
| `POST` | `/api/strategies` | Create strategy | StrategyCreate schema | Strategy object |
| `GET` | `/api/strategies` | List workspace strategies | Query: `?status=active&page=1&limit=20` | `{strategies: [], total: int}` |
| `GET` | `/api/strategies/{id}` | Get strategy detail | — | Full strategy + computed stats |
| `PUT` | `/api/strategies/{id}` | Update strategy | Partial strategy fields | Updated strategy |
| `DELETE` | `/api/strategies/{id}` | Archive strategy | — | `{message: "Archived"}` |
| `POST` | `/api/strategies/{id}/activate` | Activate → trigger first generation | — | `{strategy, generation_task_id}` |
| `POST` | `/api/strategies/{id}/pause` | Pause auto-generation | — | Updated strategy |
| `GET` | `/api/strategies/{id}/audit-log` | Get audit history | Query: `?limit=50` | `{entries: []}` |

**Wizard-Specific Endpoints**

| Method | Path | Description | Request Body | Response |
|--------|------|-------------|-------------|----------|
| `POST` | `/api/strategies/suggest-pillars` | AI suggest pillars | `{industry?: string, platforms: string[]}` | `{pillars: [{name, description, weight, platforms}]}` |
| `POST` | `/api/strategies/suggest-frequency` | AI suggest posting frequency | `{platforms: string[]}` | `{frequency: {platform: {...}}}` |
| `POST` | `/api/strategies/preview-week` | Preview first week calendar | Strategy config (not saved) | `{slots: [{day, time, pillar, platform, topic_preview}]}` |
| `GET` | `/api/strategies/defaults` | Get workspace defaults | — | `{connected_platforms, analytics_baseline, brand_voice_status}` |

**Request Schema: `StrategyCreate`**

```json
{
  "name": "Q3 LinkedIn Growth",
  "goals": [
    {
      "type": "engagement_rate",
      "target": 4.5,
      "platform": "linkedin",
      "period": "quarterly",
      "baseline": 2.1
    }
  ],
  "content_pillars": [
    {
      "name": "Thought Leadership",
      "description": "Industry insights and trends",
      "weight": 0.4,
      "platforms": ["linkedin", "x"],
      "tone": "authoritative",
      "example_hooks": ["Here's what most people get wrong about..."],
      "content_types": ["text_post", "article"]
    }
  ],
  "audience_personas": [
    {
      "name": "Tech Startup Founders",
      "demographics": {"age_min": 25, "age_max": 40, "roles": ["founder"]},
      "pain_points": ["scaling", "hiring"],
      "content_preferences": ["data-driven", "actionable"]
    }
  ],
  "posting_frequency": {
    "linkedin": {"posts_per_week": 3, "preferred_days": [1, 2, 3], "preferred_hours": [8, 12, 17]}
  },
  "auto_generate": true,
  "generate_ahead_days": 7,
  "approval_required": true
}
```

**Response Schema: `Strategy` (full)**

```json
{
  "id": "str_abc123",
  "workspace_id": "ws_xyz",
  "name": "Q3 LinkedIn Growth",
  "goals": ["..."],
  "content_pillars": ["..."],
  "audience_personas": ["..."],
  "posting_frequency": {"..."},
  "status": "active",
  "auto_generate": true,
  "generate_ahead_days": 7,
  "approval_required": true,
  "auto_approve_threshold": 0.85,
  "last_generated_at": "2026-07-18T06:00:00Z",
  "computed_stats": {
    "total_posts_per_week": 13,
    "total_posts_per_month": 56,
    "platforms_active": ["linkedin", "x", "instagram"],
    "pillar_balance": {"Thought Leadership": 0.4, "BTS": 0.3, "Educational": 0.3}
  },
  "created_by": "user_123",
  "created_at": "2026-07-18T10:00:00Z",
  "updated_at": "2026-07-18T10:00:00Z"
}
```

### 1.4 Business Logic

**Pillar Weight Normalization:**
```
On save: if sum(pillar.weight) != 1.0:
  normalize all weights: pillar.weight = pillar.weight / sum(all_weights)
  Round to 2 decimal places
  Ensure minimum weight per pillar = 0.05 (no pillar gets zero)
```

**Goal Baseline Auto-Detection:**
```
For each goal with type "engagement_rate":
  Query AnalyticsMetric for workspace
  Filter by platform, last 30 days
  baseline = avg(engagement / impressions) for that platform
  If no data: baseline = 0, show "No data yet" indicator
```

**Strategy Activation:**
```
On activate:
  1. Validate: at least 1 goal, 1 pillar, 1 platform with frequency > 0
  2. Validate: sum of pillar weights = 1.0 (auto-normalize if close)
  3. Validate: BrandVoice exists for workspace (warn but allow)
  4. Set status = "active"
  5. Log audit entry: action="activated"
  6. If auto_generate=true: trigger Celery task `generate_weekly_content(strategy_id)`
  7. Return strategy + task_id
```

**Quick Start Logic:**
```
When user clicks "Quick Start":
  1. Detect connected platforms from PlatformConnection
  2. Pull analytics baseline for each
  3. Generate 3 default pillars based on most common industry patterns
  4. Set frequency to platform defaults (LinkedIn=3/wk, X=5/wk, etc.)
  5. Pre-fill goal as "Increase engagement by 20% this quarter"
  6. Show pre-filled wizard, user reviews and customizes
```

**Validation Rules:**
- Strategy name: 3-200 characters, alphanumeric + spaces + hyphens
- Minimum 1 pillar, maximum 5
- Pillar weights must sum to 1.0 (±0.01 tolerance, auto-corrected)
- Platform in pillar must be connected (warning if not)
- Posting frequency: at least 1 platform with posts_per_week ≥ 1
- Each platform posts_per_week max: LinkedIn=7, X=14, Instagram=7, Facebook=7, YouTube=3
- Preferred days: array of 0-6 (Sun-Sat)
- Preferred hours: array of 0-23

### 1.5 Integration Points

| Existing Service | Integration | Direction | How Used |
|-----------------|-------------|-----------|----------|
| `BrandVoice` model | Read tone/style | Inbound | Wizard pre-fills brand voice section. Strategy `brand_voice_overrides` merges with `BrandVoice` during generation. |
| `AnalyticsMetric` model | Read baseline data | Inbound | `GET /api/strategies/defaults` queries last 30 days of analytics for goal baseline auto-detection. |
| `PlatformConnection` model | Detect connected platforms | Inbound | Wizard shows connected platforms, validates pillar platform selections. |
| `BEST_TIMES` (scheduler_api) | Pre-fill frequency | Inbound | "Use optimal times" button populates preferred_hours from static best times. |
| `get_best_times_for_workspace` | Workspace-specific times | Inbound | Fallback if workspace has 30+ days of analytics data. |
| Celery beat | Trigger generation | Outbound | Activation queues `generate_weekly_content` task. |
| `StrategyAuditLog` | Record all changes | Outbound | Every create/update/activate/pause/archived writes audit entry. |

---

## Feature 2: AI Content Generation

### 2.1 UI/UX Wireframe Description

**Generation is async. User triggers it and monitors via progress indicator.**

**Trigger Points:**
1. Strategy activation → auto-generates immediately
2. Manual "Generate This Week" button on strategy detail page
3. Daily Celery beat at 6 AM UTC for active strategies

**Progress UI (shown after trigger):**
```
┌─────────────────────────────────────────────────────────┐
│  ⏳ Generating Your Content Plan                        │
│                                                         │
│  Strategy: Q3 LinkedIn Growth                           │
│  Week: Jul 21 – Jul 27, 2026                            │
│                                                         │
│  Progress: [████████████░░░░░░░░] 60%                   │
│                                                         │
│  ✅ Slot Planning (14 slots identified)                 │
│  ✅ LinkedIn content (3 posts generated)                │
│  🔄 X/Twitter content (generating thread 2/5)          │
│  ⬜ Instagram content                                   │
│  ⬜ Facebook content                                    │
│  ⬜ Quality validation                                  │
│  ⬜ Schedule placement                                  │
│                                                         │
│  Estimated time: ~45 seconds remaining                  │
│                                                         │
│  [View completed slots]    [Cancel generation]          │
└─────────────────────────────────────────────────────────┘
```

**Post-Generation — Content Plan View:**
```
┌──────────────────────────────────────────────────────────────────┐
│  Content Plan: Jul 21–27  Strategy: Q3 LinkedIn Growth           │
│                                                                  │
│  Filters: [All Platforms ▾] [All Pillars ▾] [Status ▾]         │
│                                                                  │
│  ┌────────────────────────────────────────────────────────────┐  │
│  │ MONDAY, JUL 21                                             │  │
│  │                                                            │  │
│  │ ┌──────────────┐ ┌──────────────┐ ┌──────────────┐       │  │
│  │ │ 💼 LinkedIn  │ │ 🐦 X/Twitter │ │ 📸 Instagram │       │  │
│  │ │ 8:00 AM      │ │ 12:00 PM     │ │ 11:00 AM     │       │  │
│  │ │ ──────────── │ │ ──────────── │ │ ──────────── │       │  │
│  │ │ 🔵 Thought   │ │ 🔵 Thought  │ │ 🟢 Behind   │       │  │
│  │ │    Leadership│ │    Leadership│ │    the Scenes│       │  │
│  │ │              │ │              │ │              │       │  │
│  │ │ "Here's what │ │ "3 things I  │ │ "What our    │       │  │
│  │ │  most people │ │  wish I knew │ │  mornings    │       │  │
│  │ │  get wrong   │ │  before..."  │ │  look like"  │       │  │
│  │ │  about..."   │ │              │ │              │       │  │
│  │ │              │ │ [Thread 3/5] │ │              │       │  │
│  │ │ [👁 Preview] │ │ [👁 Preview] │ │ [👁 Preview] │       │  │
│  │ │ [✏️ Edit]    │ │ [✏️ Edit]    │ │ [✏️ Edit]    │       │  │
│  │ │ [✅ Approve] │ │ [✅ Approve] │ │ [✅ Approve] │       │  │
│  │ └──────────────┘ └──────────────┘ └──────────────┘       │  │
│  └────────────────────────────────────────────────────────────┘  │
│                                                                  │
│  [📋 Approve All]  [🔄 Regenerate Week]  [📊 Strategy Stats]   │
└──────────────────────────────────────────────────────────────────┘
```

**Platform Preview Modal (click "Preview"):**
```
┌───────────────────────────────────────────┐
│  LinkedIn Post Preview            [×]     │
│  ┌─────────────────────────────────────┐  │
│  │ [Mock LinkedIn feed card]           │  │
│  │                                     │  │
│  │ Here's what most people get wrong   │  │
│  │ about content strategy...           │  │
│  │                                     │  │
│  │ [Full post content rendered here]   │  │
│  │                                     │  │
│  │ #ThoughtLeadership #ContentStrategy │  │
│  │                                     │  │
│  │ 👍 💬 ↗️                           │  │
│  └─────────────────────────────────────┘  │
│                                           │
│  Brand Voice Score: 0.87 ✅               │
│  Char count: 1,247 / 3,000               │
│  Pillar: Thought Leadership              │
│  Status: Pending approval                 │
│                                           │
│  [✏️ Edit] [✅ Approve] [❌ Reject]      │
└───────────────────────────────────────────┘
```

### 2.2 Data Model

**Existing table: `content_plans`** (new — referenced in PRD)

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `id` | `String(36)` | PK | UUID |
| `strategy_id` | `String(36)` | FK → `content_strategies.id`, NOT NULL, INDEX | Parent strategy |
| `workspace_id` | `String(36)` | FK → `workspaces.id`, NOT NULL, INDEX | Workspace |
| `week_start` | `DateTime` | NOT NULL | Monday of the planned week (UTC) |
| `status` | `String(16)` | NOT NULL, DEFAULT `"draft"`, INDEX | `draft` \| `generating` \| `ready` \| `in_progress` \| `completed` |
| `generation_task_id` | `String(64)` | NULLABLE | Celery task ID for async tracking |
| `generation_progress` | `JSON` | DEFAULT `{}` | `{total_slots: 14, completed: 9, current_step: "instagram"}` |
| `generated_at` | `DateTime` | NULLABLE | When generation completed |
| `slot_count` | `Integer` | DEFAULT `0` | Total slots in plan |
| `approved_count` | `Integer` | DEFAULT `0` | Slots approved |
| `published_count` | `Integer` | DEFAULT `0` | Slots published |
| `rejected_count` | `Integer` | DEFAULT `0` | Slots rejected |
| `created_at` | `DateTime` | NOT NULL, DEFAULT `now()` | |
| `updated_at` | `DateTime` | NOT NULL, DEFAULT `now()` | |

**Existing table: `content_slots`** (new — referenced in PRD)

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `id` | `String(36)` | PK | UUID |
| `plan_id` | `String(36)` | FK → `content_plans.id`, NOT NULL, INDEX | Parent plan |
| `workspace_id` | `String(36)` | FK → `workspaces.id`, NOT NULL, INDEX | Workspace |
| `strategy_id` | `String(36)` | FK → `content_strategies.id`, NOT NULL | Strategy reference |
| `pillar_name` | `String(100)` | NOT NULL | Which content pillar |
| `platform` | `String(32)` | NOT NULL, INDEX | Target platform |
| `scheduled_date` | `Date` | NOT NULL | Day of the week (date) |
| `scheduled_time` | `String(5)` | NOT NULL | Time as `"HH:MM"` (UTC) |
| `scheduled_datetime` | `DateTime` | NOT NULL, INDEX | Combined UTC datetime for queries |
| `status` | `String(16)` | NOT NULL, DEFAULT `"empty"`, INDEX | `empty` \| `generating` \| `generated` \| `pending_approval` \| `approved` \| `rejected` \| `skipped` \| `published` \| `failed` |
| `topic` | `String(500)` | NULLABLE | AI-selected topic |
| `topic_sources` | `JSON` | DEFAULT `[]` | `["trending", "pillar_default", "user_example"]` |
| `generated_content` | `Text` | NULLABLE | Final AI-generated content |
| `generated_variants` | `JSON` | DEFAULT `[]` | `[{content: "...", score: 0.87, brand_voice_score: 0.85}]` |
| `selected_variant_index` | `Integer` | DEFAULT `0` | Which variant was selected |
| `media_requirements` | `JSON` | DEFAULT `{}` | `{type: "image", aspect_ratio: "1:1", description: "..."}` |
| `platform_metadata` | `JSON` | DEFAULT `{}` | Platform-specific: `{hashtags: [...], thread_count: 3, seo_keywords: [...]}` |
| `brand_voice_score` | `Float` | NULLABLE | Score 0.0–1.0 from voice validation |
| `generation_prompt_used` | `Text` | NULLABLE | The prompt sent to LLM (for debugging) |
| `generation_model` | `String(64)` | NULLABLE | Which model was used |
| `generation_tokens` | `Integer` | NULLABLE | Token count for cost tracking |
| `post_id` | `String(36)` | FK → `posts.id`, NULLABLE | Created on approval |
| `post_platform_id` | `String(36)` | FK → `post_platforms.id`, NULLABLE | Created on approval |
| `approved_by` | `String(36)` | FK → `users.id`, NULLABLE | Who approved |
| `approved_at` | `DateTime` | NULLABLE | Approval timestamp |
| `rejection_reason` | `String(200)` | NULLABLE | Why rejected |
| `rejection_category` | `String(32)` | NULLABLE | `too_formal` \| `off_brand` \| `wrong_pillar` \| `needs_hook` \| `custom` |
| `user_edit_history` | `JSON` | DEFAULT `[]` | `[{before: "...", after: "...", edited_by: "user_id", timestamp: "..."}]` |
| `auto_approved` | `Boolean` | DEFAULT `false` | Was auto-approved by threshold |
| `created_at` | `DateTime` | NOT NULL, DEFAULT `now()` | |
| `updated_at` | `DateTime` | NOT NULL, DEFAULT `now()` | |

### 2.3 API Endpoints

**Content Generation**

| Method | Path | Description | Request Body | Response |
|--------|------|-------------|-------------|----------|
| `POST` | `/api/strategies/{id}/generate` | Trigger content generation | `{days_ahead: 7, platforms?: string[]}` | `{task_id, plan_id, status: "generating"}` |
| `GET` | `/api/strategies/{id}/plans` | List plans for strategy | Query: `?status=ready&page=1` | `{plans: [{id, week_start, status, slot_count, approved_count}], total}` |
| `GET` | `/api/strategies/{id}/plans/{pid}` | Get plan with all slots | — | Full plan + slots array |
| `POST` | `/api/strategies/{id}/plans/{pid}/regenerate` | Regenerate entire plan | `{keep_approved: true}` | `{task_id, plan_id}` |
| `GET` | `/api/strategies/{id}/plans/{pid}/progress` | Poll generation progress | — | `{status, progress: {total, completed, current_step}, slots_done: []}` |
| `POST` | `/api/strategies/{id}/plans/{pid}/auto-approve` | Auto-approve eligible slots | — | `{approved: int, skipped: int}` |

**Slot Management**

| Method | Path | Description | Request Body | Response |
|--------|------|-------------|-------------|----------|
| `GET` | `/api/slots/{id}` | Get slot detail | — | Full slot object |
| `PUT` | `/api/slots/{id}` | Edit slot content | `{generated_content: "...", topic?: "..."}` | Updated slot |
| `POST` | `/api/slots/{id}/approve` | Approve → creates Post + PostPlatform | `{comment?: "..."}` | Created post + platform IDs |
| `POST` | `/api/slots/{id}/reject` | Reject with reason | `{reason: "...", category: "too_formal"}` | Updated slot |
| `POST` | `/api/slots/{id}/skip` | Skip this slot | — | Updated slot |
| `POST` | `/api/slots/{id}/regenerate` | Regenerate this specific slot | `{hint?: "make it more casual"}` | `{task_id}` |
| `POST` | `/api/slots/{id}/select-variant` | Choose a different variant | `{variant_index: 1}` | Updated slot |
| `GET` | `/api/slots/{id}/preview/{platform}` | Get platform-specific preview | — | Rendered preview HTML/object |

**Bulk Operations**

| Method | Path | Description | Request Body | Response |
|--------|------|-------------|-------------|----------|
| `POST` | `/api/slots/bulk-approve` | Approve multiple slots | `{slot_ids: [], comment?: ""}` | `{approved: int, failed: int}` |
| `POST` | `/api/slots/bulk-reject` | Reject multiple slots | `{slot_ids: [], reason: "", category: ""}` | `{rejected: int}` |
| `POST` | `/api/slots/bulk-regenerate` | Regenerate multiple slots | `{slot_ids: []}` | `{task_id, count: int}` |

### 2.4 Business Logic

**Slot Planning Algorithm:**
```
For each active strategy:
  1. Calculate total_posts_needed = sum(platform.posts_per_week) × generate_ahead_days / 7
  2. For each platform in posting_frequency:
     a. Determine days to generate for (next N days from today)
     b. For each day: check if day is in preferred_days
     c. If yes: create slot_count = ceil(posts_per_week / preferred_days.length) for that day
     d. Assign time from preferred_hours (rotate if multiple)
  3. Assign pillars to slots using round-robin weighted by pillar.weight:
     - Sort pillars by weight descending
     - For each slot: assign next pillar, ensuring no more than 2 consecutive same pillar
     - Ensure each pillar gets its proportional share per platform
  4. Validate: no more than MAX_DAILY_POSTS per platform per day
  5. Return slot list sorted by scheduled_datetime
```

**Content Generation Pipeline (per slot):**
```
1. SLOT CONTEXT BUILDER
   - pillar: {name, description, tone, example_hooks}
   - platform: {format_rules, char_limit, special_requirements}
   - audience: {demographics, pain_points, preferences}
   - brand_voice: BrandVoice fields merged with pillar overrides
   - recent_posts: last 10 posts in same pillar (for diversity)
   - topic: AI-selected from pillar context or trending

2. LLM PROMPT CONSTRUCTION
   System prompt = platform-specific base (from ai_content_adapter.PLATFORM_SYSTEM_PROMPTS)
     + pillar tone instructions
     + brand voice description
     + audience context
     + format constraints (char limit, hashtag rules, etc.)
   
   User prompt = "Create a [platform] post for the [pillar_name] pillar.
     Topic: [topic]
     Audience: [persona description]
     Include: [content_types for this pillar]
     Example hook: [random from example_hooks]
     Tone: [tone]
     " + any additional constraints

3. LLM CALL
   - Provider: workspace's configured LLM (from PlatformProviderConfig or default openai/gpt-4o-mini)
   - Temperature: 0.75 (creativity) for text, 0.3 for titles/SEO
   - Max tokens: platform-dependent (1500 for most, 500 for X single tweet)
   - For X threads: generate as single LLM call with explicit thread structure

4. POST-PROCESSING
   a. Platform validation: enforce char limits via content_validator.validate_post()
   b. Brand voice scoring: call LLM to score 0-1 against brand voice description
   c. Diversity check: compare against last 30 days of content in same pillar
      - If hook is >80% similar to a recent post: regenerate
      - If topic overlaps >70% with recent posts: flag as warning
   d. Hashtag generation (Instagram/LinkedIn): append relevant hashtags
   e. Thread splitting (X): split content into individual tweets at natural breaks

5. VARIANT GENERATION (Phase 1: single variant)
   - Store as single-element generated_variants array
   - Phase 2 will generate 2-3 variants for A/B testing
```

**Platform-Specific Generation Rules:**

| Platform | Content Type | Char Limit | Special Rules |
|----------|-------------|-----------|---------------|
| LinkedIn | Text post | 3,000 | Hook → line breaks → value → CTA. No hashtags in first sentence. 3-5 hashtags at end. |
| LinkedIn | Article | 210,000 | Title + subtitle + body. Use for pillar weight > 0.5 topics. |
| X | Single tweet | 280 | Punchy, 1-2 hashtags. No line breaks. |
| X | Thread | 280 × N | First tweet = hook. 3-5 tweets. Each flows from previous. Last = CTA. |
| Instagram | Caption | 2,200 | Hook in first 125 chars. 3-5 hashtags. Emoji. Visual-first language. |
| Instagram | Carousel text | 2,200 × 10 | Each slide = short text (50-100 chars). Story arc across slides. |
| Facebook | Post | 250 (optimal) | Question-driven. Conversational. Short paragraphs. |
| YouTube | Title + Desc | Title: 100 / Desc: 5,000 | SEO keywords in title. Timestamps in desc. Subscribe CTA. |

**Auto-Approve Logic:**
```
On generation complete for each slot:
  if strategy.approval_required == false:
    auto-approve slot → create Post + PostPlatform immediately
  
  if strategy.approval_required == true:
    if slot.brand_voice_score >= strategy.auto_approve_threshold
       AND slot passed all quality gates
       AND strategy.auto_generate == true:
      slot.status = "approved"
      slot.auto_approved = true
      → create Post + PostPlatform
    else:
      slot.status = "pending_approval"
```

**Quality Gates:**
```
For each generated content:
  1. Platform format compliance (content_validator.validate_post)
  2. Brand voice score >= 0.5 (minimum threshold, reject below)
  3. No exact duplicate of last 90 days of workspace content
  4. Character count within platform limits
  5. Required elements present (hashtags for Instagram, timestamps for YouTube)
  6. Content safety: no profanity, hate speech, or controversial terms (basic filter)
  
  If any gate fails:
    Retry generation once with strengthened constraints
    If still fails: mark slot as "generating" → "generated" with warning flag
    Log failure reason in platform_metadata
```

### 2.5 Integration Points

| Existing Service | Integration | Direction | How Used |
|-----------------|-------------|-----------|----------|
| `ai_content_adapter.py` (`adapt_content_ai`) | Platform content generation | Outbound | Extended with strategy-aware system prompts. New function `generate_strategy_content()` wraps existing adapter with pillar/brand context. |
| `content_validator.py` (`validate_post`) | Validate generated content | Outbound | Called on every generated piece before storing. Catches char limit violations, format issues. |
| `BrandVoice` model | Voice config for generation | Inbound | Read tone, writing_style, cta_style, emoji_usage, vocabulary. Merged into LLM system prompt. |
| `llm.py` (`call_llm`) | LLM provider calls | Outbound | Core LLM interface. All generation goes through this with workspace provider config. |
| `Post` + `PostPlatform` models | Create publishable posts | Outbound | On slot approval: create Post row (content, author_id=system) + PostPlatform row (platform-specific caption, scheduled_at). |
| `best_time_recommender.py` | Workspace-specific times | Inbound | Slot scheduling picks optimal time from workspace analytics if available. |
| `Celery` (generate_weekly_content) | Async generation trigger | Outbound | Strategy activation → queue task. Daily beat runs at 6 AM UTC. |
| `AnalyticsMetric` model | Past performance data | Inbound | Diversity check: read last 10 posts' content in same pillar to avoid repetition. |

---

## Feature 3: Smart Scheduling

### 3.1 UI/UX Wireframe Description

**Content Calendar View (default view after generation):**

```
┌──────────────────────────────────────────────────────────────────────────┐
│  📅 Content Calendar          Week of Jul 21  [←] [Today] [→]          │
│  View: [Weekly ▾]  Strategy: [Q3 LinkedIn Growth ▾]  [Month View]      │
│                                                                          │
│  ┌──────────┬──────────┬──────────┬──────────┬──────────┬──────┬──────┐ │
│  │ MON 21   │ TUE 22   │ WED 23   │ THU 24   │ FRI 25   │ SAT  │ SUN  │ │
│  ├──────────┼──────────┼──────────┼──────────┼──────────┼──────┼──────┤ │
│  │          │          │          │          │          │      │      │ │
│  │ 💼 8:00  │ 💼 8:00  │ 💼 12:00 │          │ 💼 8:00  │      │      │ │
│  │ Thought  │ Educat.  │ Thought  │          │ BTS      │      │      │ │
│  │ Lead.    │          │ Lead.    │          │          │      │      │ │
│  │ ──────── │ ──────── │ ──────── │          │ ──────── │      │      │ │
│  │ 🐦 12:00 │ 🐦 9:00  │ 🐦 12:00 │ 🐦 9:00  │ 🐦 14:00 │      │      │ │
│  │ Thought  │ Educat.  │ Educat.  │ Thought  │ BTS      │      │      │ │
│  │ Lead.    │          │          │ Lead.    │          │      │      │ │
│  │ ──────── │ ──────── │ ──────── │ ──────── │ ──────── │      │      │ │
│  │ 📸 11:00 │          │ 📸 19:00 │          │ 📸 11:00 │      │      │ │
│  │ BTS      │          │ Educat.  │          │ Educat.  │      │      │ │
│  │          │          │          │          │          │      │      │ │
│  │          │          │          │          │ 📺 15:00 │      │      │ │
│  │          │          │          │          │ Educat.  │      │      │ │
│  └──────────┴──────────┴──────────┴──────────┴──────────┴──────┴──────┘ │
│                                                                          │
│  Legend: 💼 LinkedIn  🐦 X  📸 Instagram  📘 Facebook  📺 YouTube      │
│  Colors: 🔵 Thought Lead.  🟢 Behind Scenes  🟡 Educational            │
│                                                                          │
│  ┌────────────────────────────────────────────────────────────────────┐  │
│  │ Daily Summary: Mon=3 posts  Tue=2  Wed=3  Thu=1  Fri=4  Total:13 │  │
│  │ Platform cap status: LinkedIn ✅ (3/3)  X ✅ (5/5)  IG ✅ (3/3)  │  │
│  └────────────────────────────────────────────────────────────────────┘  │
└──────────────────────────────────────────────────────────────────────────┘
```

**Drag-and-Drop Behavior:**
- Drag a slot card to a different day/time → calls `PUT /api/slots/{id}` with new `scheduled_date` + `scheduled_time`
- Drop validation: check frequency caps, minimum spacing, same-pillar rules
- Invalid drop → toast error: "Cannot move here: would exceed LinkedIn daily limit (3/day)"
- Valid drop → optimistic UI update, then confirm from server

**Month View:**
```
┌────────────────────────────────────────────────────────────────┐
│  📅 July 2026                          [Weekly View]          │
│                                                                │
│  Mo  Tu  We  Th  Fr  Sa  Su                                   │
│      1   2   3   4   5   6                                    │
│  7●  8●  9●  10● 11●                                         │
│  12  13● 14● 15● 16● 17  18                                  │
│  19  20  21● 22● 23● 24● 25●                                 │
│  26  27  28● 29● 30● 31●                                     │
│                                                                │
│  ● = has scheduled posts                                       │
│  Click day → expand to daily detail                            │
│  [Legend: Coverage — Green=full  Yellow=partial  Red=gap]       │
└────────────────────────────────────────────────────────────────┘
```

**Bulk Schedule Panel (from content queue):**
```
┌───────────────────────────────────────────────────────────┐
│  Bulk Schedule from Queue                                 │
│                                                           │
│  Selected: 8 items from content queue                     │
│                                                           │
│  Scheduling strategy:                                     │
│  ○ Smart (use optimal times)    ← selected                │
│  ○ Manual (I'll pick times)                              │
│  ○ Fill gaps (only schedule where calendar has space)     │
│                                                           │
│  Start date: [Jul 21 ▾]    End date: [Jul 27 ▾]         │
│                                                           │
│  Preview:                                                 │
│  Mon 21: 💼 8:00  🐦 12:00  📸 19:00                     │
│  Tue 22: 💼 10:00  🐦 9:00                                │
│  Wed 23: 💼 12:00  🐦 17:00  📸 11:00                     │
│  ...                                                      │
│                                                           │
│  ⚠️ 2 items conflict with existing schedule               │
│                                                           │
│  [Cancel]  [Schedule 6 items →]                           │
└───────────────────────────────────────────────────────────┘
```

### 3.2 Data Model

No new tables. Scheduling operates on existing `content_slots` and `PostPlatform` tables.

**Modified field on `content_slots`:**
- `scheduled_datetime` (DateTime, NOT NULL, INDEX): Combined UTC datetime for efficient range queries and sorting.

**Redis Cache Keys (new):**

| Key Pattern | TTL | Description |
|-------------|-----|-------------|
| `schedule:cap:{workspace_id}:{platform}:{date}` | 24h | Daily post count for frequency cap enforcement |
| `schedule:slots:{workspace_id}:{week_start}` | 1h | Cached weekly slot list for calendar rendering |
| `schedule:conflicts:{workspace_id}:{datetime}` | 1h | Conflict check cache |

### 3.3 API Endpoints

| Method | Path | Description | Request Body | Response |
|--------|------|-------------|-------------|----------|
| `GET` | `/api/strategies/{id}/calendar` | Get calendar view | Query: `?week=2026-07-21&view=weekly` | `{slots: [], week_start, week_end, stats: {}}` |
| `GET` | `/api/strategies/{id}/calendar/month` | Get month view | Query: `?month=2026-07` | `{days: [{date, slot_count, platforms: []}], total_slots}` |
| `PUT` | `/api/slots/{id}/reschedule` | Move slot to new time | `{scheduled_date: "2026-07-22", scheduled_time: "10:00"}` | Updated slot + validation |
| `GET` | `/api/slots/check-conflicts` | Check scheduling conflicts | Query: `?workspace_id=...&platform=linkedin&date=2026-07-21&exclude_slot=...` | `{conflicts: [], caps: {current: 2, max: 3}}` |
| `POST` | `/api/strategies/{id}/bulk-schedule` | Bulk schedule from queue | `{slot_ids: [], strategy: "smart", start_date, end_date}` | `{scheduled: int, skipped: int, errors: []}` |
| `GET` | `/api/strategies/{id}/frequency-status` | Current frequency vs target | — | `{platforms: {linkedin: {target: 3, scheduled: 2, remaining: 1}}, week: "..."}` |
| `POST` | `/api/strategies/{id}/optimize-times` | Re-optimize all slot times | — | `{changed: int, slots: [{id, old_time, new_time}]}` |

### 3.4 Business Logic

**Smart Scheduling Algorithm (per slot):**
```
function get_optimal_time(slot, strategy, workspace_id):
  1. platform = slot.platform
  
  2. Get candidate times:
     a. Strategy preferred_hours for this platform
     b. BEST_TIMES[platform] from scheduler_api (static)
     c. Workspace analytics from get_best_times_for_workspace (if 30+ days data)
     d. Merge and deduplicate, ranking by: workspace_data > strategy_pref > static
  
  3. For each candidate time (sorted by rank):
     a. datetime = slot.scheduled_date + candidate_hour
     b. Check frequency cap:
        - Count existing posts for workspace+platform on this date
        - If count >= MAX_DAILY_POSTS[platform]: skip
     c. Check minimum spacing:
        - Get all posts for this platform within ±4 hours
        - If any exist: skip
     d. Check pillar diversity:
        - Get last 2 scheduled posts for this platform
        - If both are same pillar_name as this slot: skip
     e. Check conflicts with manual posts:
        - Query PostPlatform for workspace+platform at this datetime
        - If any: skip
     f. If all checks pass: return datetime
  
  4. If no candidate passes: use next available slot (iterate forward day by day)
  5. If still no slot in 7 days: flag as "needs manual scheduling"
```

**Frequency Caps (defaults, configurable per strategy):**

| Platform | Max/Day | Min Spacing (hours) | Notes |
|----------|---------|---------------------|-------|
| LinkedIn | 3 | 4 | Feed + articles counted together |
| X | 5 | 2 | Tweets + threads counted as 1 each |
| Instagram | 3 | 4 | Feed posts + reels. Stories separate (unlimited). |
| Facebook | 2 | 6 | Posts + link shares |
| YouTube | 1 | 24 | Videos only. Community posts separate. |

**Drag-and-Drop Validation:**
```
On PUT /api/slots/{id}/reschedule:
  1. Parse new scheduled_date + scheduled_time → new_datetime
  2. Validate platform frequency cap: count posts on new date
  3. Validate minimum spacing: check ±4h window
  4. Validate pillar diversity: check adjacent slots
  5. If validation fails: return 422 with specific error + suggested alternatives
  6. If passes: update slot.scheduled_datetime, return updated slot
  7. Invalidate Redis cache for that week
```

**Timezone Handling:**
```
All storage and scheduling in UTC.
User's timezone stored in workspace settings (default: workspace owner's browser TZ).
Calendar view: convert UTC → workspace timezone for display.
Scheduling: user picks local time → convert to UTC using workspace timezone.
DST transitions: use pytz for accurate conversion. If ambiguous (fall-back), prefer earlier time.
```

**Bulk Schedule Algorithm:**
```
function bulk_schedule(slot_ids, strategy, start_date, end_date):
  1. Load all existing slots + manually scheduled posts in date range
  2. Sort slot_ids by pillar weight (higher weight = earlier scheduling)
  3. For each slot:
     a. Find optimal time using get_optimal_time()
     b. If "fill gaps" mode: only place in time slots not yet occupied
     c. Update slot.scheduled_datetime
  4. Return summary: scheduled count, skipped (conflicts), errors
```

### 3.5 Integration Points

| Existing Service | Integration | Direction | How Used |
|-----------------|-------------|-----------|----------|
| `BEST_TIMES` (scheduler_api.py) | Static best times | Inbound | Fallback scheduling times when no workspace analytics available. |
| `get_best_times_for_workspace` (best_time_recommender.py) | Workspace analytics | Inbound | Primary scheduling optimization when 30+ days data exists. |
| `suggest_audience_aware_time` (timezone_scheduler.py) | Audience timezone | Inbound | Multi-region audience posting optimization. |
| `validate_post` (content_validator.py) | Pre-schedule validation | Outbound | Validate content before placing in schedule. |
| `PostPlatform` model | Conflict detection | Inbound | Check existing scheduled posts for conflict/cap enforcement. |
| `ContentCalendar` model | Calendar entries | Outbound | On slot approval, create ContentCalendar entry for existing calendar view. |
| Redis | Cap tracking + cache | Outbound | Increment daily counters on schedule, invalidate on reschedule. |
| Existing Celery `publish_post` task | Publish at scheduled time | Outbound | Approved slots create PostPlatform rows with `status="scheduled"` → existing publisher picks up. |

---

## Feature 4: Approval Flow

### 4.1 UI/UX Wireframe Description

**Approval Queue (main view):**

```
┌──────────────────────────────────────────────────────────────────────┐
│  ✅ Approval Queue                    [Filter ▾]  [Bulk Actions]   │
│                                                                      │
│  Pending: 8 items  |  Today: 3  |  This week: 8                     │
│                                                                      │
│  Strategy: [Q3 LinkedIn Growth ▾]  Platform: [All ▾]                │
│                                                                      │
│  ┌──────────────────────────────────────────────────────────────┐    │
│  │ 💼 LinkedIn  —  Thought Leadership  —  Mon Jul 21, 8:00 AM  │    │
│  │                                                              │    │
│  │ "Here's what most people get wrong about content strategy    │    │
│  │  in 2026. I've spent the last 3 years analyzing over 10,000 │    │
│  │  posts and the data tells a clear story..."                  │    │
│  │                                                              │    │
│  │ [👁 Preview] [✏️ Edit] [📋 Copy]                             │    │
│  │                                                              │    │
│  │ Brand Voice: 0.87 ✅    Char: 1,247/3,000                   │    │
│  │ Pillar: Thought Leadership    Assigned: Sarah Chen           │    │
│  │                                                              │    │
│  │ [❌ Reject]  [🔄 Regenerate]  [✅ Approve]                   │    │
│  └──────────────────────────────────────────────────────────────┘    │
│                                                                      │
│  ┌──────────────────────────────────────────────────────────────┐    │
│  │ 📸 Instagram  —  Behind the Scenes  —  Mon Jul 21, 11:00 AM │    │
│  │                                                              │    │
│  │ "What our Tuesday mornings actually look like 🎬✨            │    │
│  │  The reality of building a startup isn't always glamorous    │    │
│  │  but it's always real..."                                    │    │
│  │                                                              │    │
│  │ [👁 Preview] [✏️ Edit] [📋 Copy]                             │    │
│  │                                                              │    │
│  │ Brand Voice: 0.72 ⚠️    Char: 312/2,200                     │    │
│  │ Pillar: Behind the Scenes    Assigned: Marcus J.             │    │
│  │                                                              │    │
│  │ [❌ Reject]  [🔄 Regenerate]  [✅ Approve]                   │    │
│  └──────────────────────────────────────────────────────────────┘    │
│                                                                      │
│  ... more items ...                                                   │
│                                                                      │
│  ┌──────────────────────────────────────────────────────────────┐    │
│  │ [📋 Approve All (6)]  [❌ Reject All (2)]  [⏭ Skip All]      │    │
│  └──────────────────────────────────────────────────────────────┘    │
└──────────────────────────────────────────────────────────────────────┘
```

**Reject Modal:**
```
┌──────────────────────────────────────────┐
│  Reject Content                    [×]   │
│                                          │
│  Post: "What our Tuesday mornings..."    │
│  Platform: Instagram                     │
│                                          │
│  Reason:                                 │
│  ○ Too formal                            │
│  ○ Off-brand                             │
│  ○ Wrong pillar content                  │
│  ○ Needs a stronger hook                 │
│  ○ Custom reason  → [text input]         │
│                                          │
│  Feedback for AI (optional):             │
│  ┌──────────────────────────────────┐    │
│  │ Make it more casual, use more    │    │
│  │ emojis, shorter sentences.       │    │
│  └──────────────────────────────────┘    │
│                                          │
│  [Cancel]  [Reject & Flag for Re-gen]    │
└──────────────────────────────────────────┘
```

**Edit Inline (click "Edit"):**
```
┌──────────────────────────────────────────────────────────────┐
│  ✏️ Editing: LinkedIn Post — Thought Leadership               │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐    │
│  │ Here's what most people get wrong about content      │    │
│  │ strategy in 2026. I've spent the last 3 years        │    │
│  │ analyzing over 10,000 posts and the data tells       │    │
│  │ a clear story...                                    │    │
│  │                                                      │    │
│  │ [cursor here]                                        │    │
│  │                                                      │    │
│  │ #ContentStrategy #Marketing #2026                    │    │
│  └──────────────────────────────────────────────────────┘    │
│                                                              │
│  Char: 1,247/3,000 ✅   Brand Voice: 0.87 (unchanged)      │
│                                                              │
│  [Cancel]  [Save Edit → Approve]  [Save Edit Only]          │
└──────────────────────────────────────────────────────────────┘
```

**Platform Preview Split View (from PRD: "side-by-side preview"):**
```
┌─────────────────────────────────────────────────────────────────┐
│  Platform Preview — "Here's what most people get wrong..."      │
│                                                                 │
│  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────┐  │
│  │  💼 LinkedIn     │  │  🐦 X/Twitter    │  │  📸 Instagram│  │
│  │  ────────────    │  │  ────────────    │  │  ──────────  │  │
│  │  ┌────────────┐  │  │  ┌────────────┐  │  │  ┌────────┐ │  │
│  │  │ LinkedIn   │  │  │  │ Tweet card │  │  │  │ IG Post│ │  │
│  │  │ post card  │  │  │  │ 280 chars  │  │  │  │ +hash  │ │  │
│  │  │ (full)     │  │  │  │            │  │  │  │ tags   │ │  │
│  │  │            │  │  │  │            │  │  │  │        │ │  │
│  │  │ 1,247/3000 │  │  │  │ 267/280    │  │  │  │312/2200│ │  │
│  │  └────────────┘  │  │  └────────────┘  │  │  └────────┘ │  │
│  └──────────────────┘  └──────────────────┘  └──────────────┘  │
│                                                                 │
│  [✅ Approve All Platforms]  [✏️ Edit per platform]              │
└─────────────────────────────────────────────────────────────────┘
```

### 4.2 Data Model

Approval state is tracked on the `content_slots` table (Feature 2). Additional model:

**New table: `approval_audit_log`**

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `id` | `String(36)` | PK | UUID |
| `slot_id` | `String(36)` | FK → `content_slots.id`, NOT NULL, INDEX | Slot reference |
| `workspace_id` | `String(36)` | FK → `workspaces.id`, NOT NULL | Workspace |
| `action` | `String(32)` | NOT NULL | `submitted` \| `approved` \| `rejected` \| `edited` \| `auto_approved` \| `regenerated` \| `skipped` |
| `actor_id` | `String(36)` | FK → `users.id`, NULLABLE | Who performed action (null for system/auto) |
| `actor_type` | `String(16)` | NOT NULL, DEFAULT `"user"` | `user` \| `system` |
| `details` | `JSON` | DEFAULT `{}` | `{reason: "...", category: "...", comment: "...", edit_diff: {...}}` |
| `brand_voice_score_before` | `Float` | NULLABLE | Score before action |
| `brand_voice_score_after` | `Float` | NULLABLE | Score after edit (if applicable) |
| `created_at` | `DateTime` | NOT NULL, DEFAULT `now()` | Timestamp |

### 4.3 API Endpoints

| Method | Path | Description | Request Body | Response |
|--------|------|-------------|-------------|----------|
| `GET` | `/api/strategies/{id}/approval-queue` | Get pending approvals for strategy | Query: `?platform=&pillar=&assignee=&page=1&limit=20` | `{slots: [{slot, preview}], total, stats: {pending, approved_today, rejected_today}}` |
| `POST` | `/api/slots/{id}/approve` | Approve single slot | `{comment?: "", assign_next?: true}` | `{slot, post_id, post_platform_id}` |
| `POST` | `/api/slots/{id}/reject` | Reject with reason | `{reason: "...", category: "too_formal", feedback_for_ai: "..."}` | Updated slot |
| `POST` | `/api/slots/{id}/edit` | Edit content inline | `{generated_content: "...", edited_by: "user_id"}` | Updated slot + brand_voice_recheck |
| `POST` | `/api/slots/{id}/skip` | Skip slot entirely | — | Updated slot |
| `POST` | `/api/slots/{id}/regenerate` | Regenerate with feedback | `{hint: "make it more casual", reuse_rejection_feedback: true}` | `{task_id}` |
| `POST` | `/api/slots/bulk-approve` | Approve multiple | `{slot_ids: [], comment?: ""}` | `{approved: int, failed: int, results: []}` |
| `POST` | `/api/slots/bulk-reject` | Reject multiple | `{slot_ids: [], reason: "", category: ""}` | `{rejected: int}` |
| `POST` | `/api/slots/{id}/assign` | Assign to team member | `{assignee_id: "user_id"}` | Updated slot |
| `GET` | `/api/slots/{id}/audit` | Get approval history for slot | — | `{entries: [{action, actor, details, created_at}]}` |
| `GET` | `/api/strategies/{id}/approval-stats` | Approval workflow metrics | Query: `?days=30` | `{approval_rate, avg_time_to_approve, by_platform: {}, by_pillar: {}}` |
| `GET` | `/api/slots/{id}/platform-previews` | Get all platform previews | — | `{linkedin: {rendered, char_count, ...}, x: {...}, instagram: {...}}` |

**Request Schema: `SlotEdit`**

```json
{
  "generated_content": "Edited content here...",
  "platform_metadata_override": {
    "hashtags": ["#custom", "#edited"]
  },
  "media_requirements_override": {
    "type": "carousel",
    "slide_count": 5
  }
}
```

**Response Schema: `ApprovalQueueItem`**

```json
{
  "slot_id": "slot_abc",
  "pillar_name": "Thought Leadership",
  "platform": "linkedin",
  "scheduled_datetime": "2026-07-21T12:00:00Z",
  "status": "pending_approval",
  "generated_content": "Here's what most people get wrong...",
  "brand_voice_score": 0.87,
  "char_count": 1247,
  "char_limit": 3000,
  "media_requirements": {"type": "image", "aspect_ratio": "1:1"},
  "assigned_to": {"id": "user_456", "name": "Sarah Chen"},
  "platform_previews": {
    "linkedin": {"char_count": 1247, "hashtags": 3, "has_hook": true}
  },
  "rejection_count": 0,
  "created_at": "2026-07-21T06:00:00Z"
}
```

### 4.4 Business Logic

**Approval Workflow State Machine:**
```
                         ┌──────────────┐
                         │  generating  │
                         └──────┬───────┘
                                │ generation complete
                                ▼
                    ┌───────────────────────┐
                    │   Quality Gate Check   │
                    └───────┬───────┬───────┘
                            │       │
                 passes all │       │ fails threshold
                            ▼       ▼
                    ┌──────────┐  ┌──────────┐
                    │ auto     │  │ pending  │
                    │ approved │  │ _approval│
                    └────┬─────┘  └──┬───┬───┘
                         │           │   │
                    create Post      │   │
                    + PostPlatform   │   │
                         │           │   │
                         ▼           │   │
                    ┌──────────┐     │   │
                    │ approved │     │   │
                    └──────────┘     │   │
                                     │   │
                    ┌────────────────┘   │
                    │                    │
              approve│              reject│
                    ▼                    ▼
              ┌──────────┐        ┌──────────┐
              │ approved │        │ rejected │
              └────┬─────┘        └────┬─────┘
                   │                    │
              create Post          regenerate with
              + PostPlatform       feedback → loop
                                   back to generating
```

**Approve Action:**
```
On POST /api/slots/{id}/approve:
  1. Verify slot.status == "pending_approval" (or "generated" for auto-approve)
  2. Verify user has permission (editor or admin role)
  3. Run final validation: content_validator.validate_post()
  4. Create Post row:
     - content = slot.generated_content
     - author_id = approving user (or "system" for auto-approve)
     - workspace_id = slot.workspace_id
     - platform = slot.platform
     - status = "scheduled"
     - scheduled_at = slot.scheduled_datetime
  5. Create PostPlatform row:
     - caption = slot.generated_content (or platform-specific override)
     - platform = slot.platform
     - scheduled_at = slot.scheduled_datetime
     - status = "scheduled"
     - media_asset_ids = slot.media_requirements.asset_ids (if provided)
  6. Update slot:
     - status = "approved"
     - post_id = new post ID
     - post_platform_id = new PP ID
     - approved_by = user.id
     - approved_at = now()
  7. Write approval_audit_log entry
  8. Update plan.approved_count++
  9. Create ContentCalendar entry
  10. Return {slot, post_id, post_platform_id}
```

**Reject Action:**
```
On POST /api/slots/{id}/reject:
  1. Verify slot.status == "pending_approval"
  2. Update slot:
     - status = "rejected"
     - rejection_reason = request.reason
     - rejection_category = request.category
  3. Write approval_audit_log entry with details
  4. Update plan.rejected_count++
  5. Store feedback in slot.platform_metadata.rejection_feedback
  6. Return updated slot
```

**Regenerate with Feedback:**
```
On POST /api/slots/{id}/regenerate:
  1. Collect feedback sources:
     a. Direct hint from request.hint
     b. Previous rejection feedback (if slot was rejected)
     c. User edit patterns (if slot was edited then re-rejected)
  2. Build enhanced prompt:
     - Original generation prompt
     - + "DO NOT: [rejection category description]"
     - + "User feedback: [hint/feedback]"
     - + "Previous content was rejected because: [reason]"
  3. Re-run generation pipeline (Feature 2, step 2-5)
  4. Update slot with new content
  5. Reset status to "pending_approval" (or auto-approve if meets threshold)
  6. Log regeneration event
```

**Edit Tracking:**
```
On POST /api/slots/{id}/edit:
  1. Capture before state: slot.generated_content
  2. Apply edit
  3. Re-run brand voice scoring on edited content
  4. Store in user_edit_history:
     {
       "before": "original content...",
       "after": "edited content...",
       "edited_by": "user_id",
       "timestamp": "2026-07-21T14:30:00Z",
       "brand_voice_score_before": 0.87,
       "brand_voice_score_after": 0.82
     }
  5. Write approval_audit_log entry
  6. Feed edit signal to BrandVoice training pipeline (Phase 2)
```

**Auto-Approve Evaluation:**
```
On generation complete:
  if NOT strategy.approval_required:
    → auto-approve immediately
    
  if strategy.approval_required AND slot.brand_voice_score >= strategy.auto_approve_threshold:
    AND slot passed all quality gates:
    AND no rejection history in last 3 regenerations:
    → auto-approve
    → set slot.auto_approved = True
    → log: "Auto-approved: brand_voice_score={score} >= threshold={threshold}"
    
  else:
    → pending_approval
```

**Team Assignment:**
```
When strategy has multiple team members (from WorkspaceMember):
  Distribute slots round-robin among members with role in [editor, admin, owner]
  Respect existing assignments: don't reassign slots already assigned
  Unassigned slots visible to all editors
  
  On assign:
    - slot.assigned_to = user_id (stored in platform_metadata)
    - Notify assigned user (Phase 2: email/notification)
```

### 4.5 Integration Points

| Existing Service | Integration | Direction | How Used |
|-----------------|-------------|-----------|----------|
| `approval_workflow.py` (existing) | Approval state management | Outbound | Extended with strategy-specific fields. Existing approve/reject functions called with enhanced context. |
| `approvals.py` (multi-tier) | Workflow routing | Outbound | Strategy approval can use existing multi-tier workflows. Slot approval follows the workflow stages. |
| `content_validator.py` | Final validation on approve | Outbound | Double-check content before creating Post + PostPlatform rows. |
| `Post` + `PostPlatform` models | Create publishable posts | Outbound | Approval creates actual Post and PostPlatform rows for publishing. |
| `ContentCalendar` model | Calendar integration | Outbound | Approved slot creates ContentCalendar entry. |
| `BrandVoice` model | Voice scoring | Inbound | Re-score edited content against brand voice. |
| `ai_brand_voice.py` (`train_from_approvals`) | Learn from edits | Outbound | User edits feed into brand voice training pipeline. |
| `Activity` model | Activity logging | Outbound | Log approval/rejection events in workspace activity feed. |
| Celery (`publish_post`) | Publishing trigger | Outbound | Approved PostPlatform rows picked up by existing publisher at scheduled time. |

---

## Feature 5: Adherence Dashboard

### 5.1 UI/UX Wireframe Description

**Full-page dashboard under Strategy section:**

```
┌──────────────────────────────────────────────────────────────────────────┐
│  📊 Strategy Adherence Dashboard                                         │
│  Strategy: Q3 LinkedIn Growth  |  Period: [This Week ▾] [This Month ▾]  │
│                                                                          │
│  ┌────────────────────────────────────────────────────────────────────┐  │
│  │  STRATEGY ADHERENCE SCORE                                          │  │
│  │                                                                    │  │
│  │        ┌────────┐                                                  │  │
│  │        │   76   │  /100                                           │  │
│  │        │  ●●●●  │  Good — room to improve                         │  │
│  │        └────────┘                                                  │  │
│  │                                                                    │  │
│  │  ↑ +8 from last week                                               │  │
│  │                                                                    │  │
│  │  Breakdown:                                                        │  │
│  │  • Pillar coverage: 85%  ██████████████████░░░░                   │  │
│  │  • Platform coverage: 92%  ███████████████████░░                   │  │
│  │  • Frequency adherence: 68%  █████████████░░░░░░                   │  │
│  │  • Timing adherence: 71%  ██████████████░░░░░░                     │  │
│  └────────────────────────────────────────────────────────────────────┘  │
│                                                                          │
│  ┌─────────────────────────────┐  ┌─────────────────────────────────┐   │
│  │  PUBLISHED vs PLANNED       │  │  CONTENT BY PILLAR              │   │
│  │                             │  │                                 │   │
│  │  Bar chart:                 │  │  Pie chart:                     │   │
│  │  Planned: ████████████ 13   │  │  🔵 Thought Leadership  38%    │   │
│  │  Published: ████████ 10     │  │  🟢 Behind the Scenes  31%     │   │
│  │  Pending: ██ 3              │  │  🟡 Educational  31%            │   │
│  │                             │  │                                 │   │
│  │  Coverage: 77%              │  │  Target: 40/30/30               │   │
│  └─────────────────────────────┘  └─────────────────────────────────┘   │
│                                                                          │
│  ┌────────────────────────────────────────────────────────────────────┐  │
│  │  PLATFORM COVERAGE                                                 │  │
│  │                                                                    │  │
│  │  LinkedIn  ████████████████████  100%  (3/3 planned, 3 published) │  │
│  │  X/Twitter █████████████████░░░   80%  (4/5 planned, 4 published) │  │
│  │  Instagram ███████████████░░░░░   75%  (3/4 planned, 2 published) │  │
│  │  Facebook  ████████████░░░░░░░░   60%  (1/2 planned, 1 published) │  │
│  │  YouTube   ████████████████████  100%  (1/1 planned, 1 published) │  │
│  └────────────────────────────────────────────────────────────────────┘  │
│                                                                          │
│  ┌─────────────────────────────┐  ┌─────────────────────────────────┐   │
│  │  PERFORMANCE BY PILLAR      │  │  GAP ANALYSIS                   │   │
│  │                             │  │                                 │   │
│  │  Table:                     │  │  ⚠️ Missing This Week:          │   │
│  │  Pillar      | Eng | Reach │  │  • Facebook: 1 post behind      │   │
│  │  ─────────── │─────│───────│  │  • Instagram Reels: 0 posted    │   │
│  │  Thought Lead| 4.2%| 12.3K │  │  • YouTube: no video this week  │   │
│  │  BTS         | 5.8%|  8.1K │  │                                 │   │
│  │  Educational | 3.1%| 15.7K │  │  🔴 Underrepresented:           │   │
│  │                             │  │  • Educational pillar only has  │   │
│  │  Best: BTS (+48% vs avg)    │  │    2 posts vs target of 4       │   │
│  └─────────────────────────────┘  └─────────────────────────────────┘   │
│                                                                          │
│  ┌────────────────────────────────────────────────────────────────────┐  │
│  │  💡 RECOMMENDATIONS                                                │  │
│  │                                                                    │  │
│  │  1. 📈 Behind the Scenes gets 48% more engagement —               │  │
│  │     consider increasing weight from 30% to 35%                     │  │
│  │                                                                    │  │
│  │  2. ⏰ LinkedIn posts at 8 AM get 40% more impressions than       │  │
│  │     12 PM posts — shift 2 posts to morning slots                   │  │
│  │                                                                    │  │
│  │  3. 📊 Instagram carousel posts outperform single images 3:1 —   │  │
│  │     enable carousel generation for visual pillars                  │  │
│  │                                                                    │  │
│  │  [Apply Recommendations →]  [Dismiss]  [View Details]             │  │
│  └────────────────────────────────────────────────────────────────────┘  │
│                                                                          │
│  ┌────────────────────────────────────────────────────────────────────┐  │
│  │  UPCOMING SCHEDULED CONTENT                                        │  │
│  │                                                                    │  │
│  │  Next 7 days: 11 posts scheduled                                  │  │
│  │                                                                    │  │
│  │  Jul 21: 💼 8:00  🐦 12:00  📸 19:00                             │  │
│  │  Jul 22: 💼 10:00  🐦 9:00                                        │  │
│  │  Jul 23: 💼 12:00  🐦 12:00  📸 11:00                             │  │
│  │  Jul 24: 🐦 9:00                                                   │  │
│  │  Jul 25: 💼 8:00  🐦 14:00  📸 11:00  📺 15:00                    │  │
│  │                                                                    │  │
│  │  ⚠️ 2 slots pending approval                                      │  │
│  │  ⚠️ 3 days with gaps below target                                 │  │
│  │                                                                    │  │
│  │  [View Full Calendar]  [Generate More Content]                     │  │
│  └────────────────────────────────────────────────────────────────────┘  │
└──────────────────────────────────────────────────────────────────────────┘
```

### 5.2 Data Model

No new tables. Dashboard computed from existing data.

**Materialized view / cache (Redis):**

| Key Pattern | TTL | Description |
|-------------|-----|-------------|
| `adherence:{strategy_id}:{period}` | 15 min | Cached adherence score + breakdown |
| `adherence:performance:{strategy_id}:{period}` | 1 hour | Cached pillar × platform performance |

**Computed fields (not stored, calculated on demand):**

| Field | Source | Calculation |
|-------|--------|-------------|
| `adherence_score` | Computed | Weighted average of pillar_coverage, platform_coverage, frequency_adherence, timing_adherence |
| `pillar_coverage` | `content_slots` vs strategy | `% of pillar targets met` |
| `platform_coverage` | `content_slots` vs strategy | `% of platform targets met` |
| `frequency_adherence` | `content_slots` vs `posting_frequency` | `actual_posts / target_posts` |
| `timing_adherence` | `content_slots.scheduled_datetime` vs `preferred_hours` | `% of posts within preferred hour ±1` |

### 5.3 API Endpoints

| Method | Path | Description | Query Params | Response |
|--------|------|-------------|-------------|----------|
| `GET` | `/api/strategies/{id}/dashboard` | Full adherence dashboard | `?period=week\|month&date=2026-07-21` | Full dashboard payload (see schema) |
| `GET` | `/api/strategies/{id}/adherence-score` | Just the score + breakdown | `?period=week\|month` | `{score, breakdown: {}, trend: []}` |
| `GET` | `/api/strategies/{id}/pillar-performance` | Performance by pillar | `?period=30d&platform=` | `{pillars: [{name, posts, avg_engagement, avg_reach, top_post_id}]}` |
| `GET` | `/api/strategies/{id}/platform-coverage` | Platform coverage stats | `?period=week` | `{platforms: {linkedin: {target, actual, coverage_pct, published, pending}}}` |
| `GET` | `/api/strategies/{id}/gap-analysis` | Missing content gaps | `?period=week` | `{gaps: [{type: "missing_pillar", pillar: "...", platform: "...", expected: 2, actual: 0}]}` |
| `GET` | `/api/strategies/{id}/recommendations` | AI recommendations | — | `{recommendations: [{type, title, description, impact, action_label}]}` |
| `GET` | `/api/strategies/{id}/upcoming` | Upcoming scheduled content | `?days=7` | `{days: [{date, slots: [{time, pillar, platform, status}]}], summary: {}}` |
| `GET` | `/api/strategies/{id}/history` | Adherence over time | `?period=90d&granularity=week` | `{data_points: [{week, score, published, planned}]}` |

**Response Schema: `Dashboard` (full)**

```json
{
  "strategy_id": "str_abc",
  "strategy_name": "Q3 LinkedIn Growth",
  "period": "week",
  "period_start": "2026-07-21",
  "period_end": "2026-07-27",

  "adherence_score": 76,
  "score_trend": "+8 from last week",
  "score_history": [
    {"week": "2026-07-07", "score": 62},
    {"week": "2026-07-14", "score": 68},
    {"week": "2026-07-21", "score": 76}
  ],

  "breakdown": {
    "pillar_coverage": {"score": 85, "target": 100},
    "platform_coverage": {"score": 92, "target": 100},
    "frequency_adherence": {"score": 68, "target": 100},
    "timing_adherence": {"score": 71, "target": 100}
  },

  "published_vs_planned": {
    "planned": 13,
    "published": 10,
    "pending_approval": 2,
    "generating": 1,
    "rejected": 0,
    "skipped": 0,
    "coverage_pct": 77
  },

  "pillar_distribution": {
    "target": {"Thought Leadership": 0.4, "Behind the Scenes": 0.3, "Educational": 0.3},
    "actual": {"Thought Leadership": 0.38, "Behind the Scenes": 0.31, "Educational": 0.31}
  },

  "platform_coverage": {
    "linkedin": {"target_posts": 3, "actual_posts": 3, "coverage_pct": 100, "published": 3, "pending": 0},
    "x": {"target_posts": 5, "actual_posts": 4, "coverage_pct": 80, "published": 4, "pending": 0},
    "instagram": {"target_posts": 4, "actual_posts": 3, "coverage_pct": 75, "published": 2, "pending": 1},
    "facebook": {"target_posts": 2, "actual_posts": 1, "coverage_pct": 50, "published": 1, "pending": 0},
    "youtube": {"target_posts": 1, "actual_posts": 1, "coverage_pct": 100, "published": 1, "pending": 0}
  },

  "pillar_performance": [
    {
      "pillar": "Behind the Scenes",
      "posts_published": 3,
      "avg_engagement_rate": 0.058,
      "avg_reach": 8100,
      "top_post_id": "post_xyz"
    },
    {
      "pillar": "Thought Leadership",
      "posts_published": 4,
      "avg_engagement_rate": 0.042,
      "avg_reach": 12300,
      "top_post_id": "post_abc"
    }
  ],

  "gap_analysis": [
    {
      "type": "platform_deficit",
      "platform": "facebook",
      "message": "Facebook: 1 post behind target",
      "severity": "warning"
    },
    {
      "type": "format_gap",
      "platform": "instagram",
      "message": "Instagram Reels: 0 posted (target: 2)",
      "severity": "critical"
    },
    {
      "type": "pillar_deficit",
      "pillar": "Educational",
      "message": "Educational pillar has 2 posts vs target of 4",
      "severity": "warning"
    }
  ],

  "recommendations": [
    {
      "id": "rec_1",
      "type": "pillar_weight_adjustment",
      "title": "Increase Behind the Scenes weight",
      "description": "Behind the Scenes gets 48% more engagement than average. Consider increasing weight from 30% to 35%.",
      "impact": "high",
      "action_label": "Apply to Strategy",
      "auto_applicable": true
    },
    {
      "id": "rec_2",
      "type": "timing_optimization",
      "title": "Shift LinkedIn posts to morning slots",
      "description": "LinkedIn posts at 8 AM get 40% more impressions than 12 PM posts.",
      "impact": "medium",
      "action_label": "Reschedule",
      "auto_applicable": true
    },
    {
      "id": "rec_3",
      "type": "format_optimization",
      "title": "Enable Instagram carousel generation",
      "description": "Instagram carousel posts outperform single images 3:1 in your analytics.",
      "impact": "medium",
      "action_label": "Update Strategy",
      "auto_applicable": false
    }
  ],

  "upcoming_schedule": {
    "next_7_days": 11,
    "pending_approval": 2,
    "days_with_gaps": 3,
    "daily_breakdown": [
      {"date": "2026-07-21", "slots": [
        {"time": "08:00", "platform": "linkedin", "pillar": "Thought Leadership", "status": "published"},
        {"time": "12:00", "platform": "x", "pillar": "Thought Leadership", "status": "published"},
        {"time": "19:00", "platform": "instagram", "pillar": "Behind the Scenes", "status": "published"}
      ]}
    ]
  }
}
```

### 5.4 Business Logic

**Adherence Score Calculation:**
```
function calculate_adherence_score(strategy, period_start, period_end):
  1. Get all slots for strategy in period
  2. Get published posts (status = "published" or PostPlatform published)
  
  pillar_coverage = calculate_pillar_coverage(strategy, published_posts)
  platform_coverage = calculate_platform_coverage(strategy, published_posts)
  frequency_adherence = calculate_frequency_adherence(strategy, published_posts, period)
  timing_adherence = calculate_timing_adherence(strategy, published_posts)
  
  // Weighted average (weights are configurable, defaults below)
  score = (
    pillar_coverage   * 0.30 +
    platform_coverage * 0.25 +
    frequency_adherence * 0.25 +
    timing_adherence  * 0.20
  ) * 100
  
  return clamp(round(score), 0, 100)
```

**Pillar Coverage Calculation:**
```
function calculate_pillar_coverage(strategy, posts):
  pillar_targets = {}
  for pillar in strategy.content_pillars:
    total_weekly = sum(strategy.posting_frequency[p]["posts_per_week"] 
                       for p in pillar.platforms)
    pillar_targets[pillar.name] = total_weekly * pillar.weight
  
  pillar_actual = count posts per pillar_name
  
  coverage_scores = []
  for pillar_name, target in pillar_targets.items():
    actual = pillar_actual.get(pillar_name, 0)
    coverage_scores.append(min(actual / max(target, 1), 1.0))
  
  return average(coverage_scores)
```

**Gap Analysis Algorithm:**
```
function analyze_gaps(strategy, period_start, period_end):
  gaps = []
  
  // Platform deficit
  for platform, freq in strategy.posting_frequency:
    expected = freq.posts_per_week * (period_days / 7)
    actual = count published posts for platform in period
    if actual < expected * 0.8:  // 20% tolerance
      gaps.append({
        type: "platform_deficit",
        platform: platform,
        message: f"{platform}: {expected - actual} posts behind target",
        severity: "critical" if actual < expected * 0.5 else "warning"
      })
  
  // Pillar deficit
  for pillar in strategy.content_pillars:
    expected = calculate_expected_posts(pillar, strategy, period_days)
    actual = count published posts in pillar
    if actual < expected * 0.7:  // 30% tolerance
      gaps.append({
        type: "pillar_deficit",
        pillar: pillar.name,
        message: f"{pillar.name}: {actual} posts vs target of {expected}",
        severity: "warning"
      })
  
  // Format gaps (Instagram Reels, YouTube videos)
  for platform in ["instagram", "youtube"]:
    expected_formats = get_expected_formats(strategy, platform)
    for format_type, expected_count in expected_formats:
      actual = count published in format_type
      if actual == 0 and expected_count > 0:
        gaps.append({
          type: "format_gap",
          platform: platform,
          message: f"{platform} {format_type}: 0 posted (target: {expected_count})",
          severity: "critical"
        })
  
  // Timing deviation
  for post in published_posts:
    if post.scheduled_hour not in preferred_hours ± 1:
      timing_deviations += 1
  if timing_deviations > len(published_posts) * 0.3:
    gaps.append({
      type: "timing_deviation",
      message: f"{timing_deviations} posts outside preferred time slots",
      severity: "info"
    })
  
  return gaps
```

**Recommendation Engine:**
```
function generate_recommendations(strategy, dashboard_data):
  recommendations = []
  
  // 1. Pillar weight optimization
  for pillar_perf in dashboard_data.pillar_performance:
    avg_engagement = mean(all pillars engagement)
    if pillar_perf.avg_engagement > avg_engagement * 1.3:
      recommendations.append({
        type: "pillar_weight_adjustment",
        title: f"Increase {pillar_perf.pillar} weight",
        description: f"{pillar_perf.pillar} gets {percentage_above} more engagement",
        impact: "high" if percentage_above > 50% else "medium"
      })
  
  // 2. Timing optimization
  for platform in connected_platforms:
    best_times = get_best_times_for_workspace(platform)
    current_avg_hour = mean(strategy.posting_frequency[platform].preferred_hours)
    optimal_hour = best_times[0].hour if best_times else null
    if optimal_hour and abs(current_avg_hour - optimal_hour) >= 2:
      recommendations.append({
        type: "timing_optimization",
        title: f"Shift {platform} posts to {optimal_hour}:00",
        description: f"{platform} posts at {optimal_hour} AM get X% more engagement"
      })
  
  // 3. Format optimization
  for platform, format_perf in analytics:
    if format_perf.carousels.avg_engagement > format_perf.singles.avg_engagement * 2:
      recommendations.append({
        type: "format_optimization",
        title: f"Enable {platform} carousel generation",
        description: f"Carousels outperform singles {format_perf.ratio}:1"
      })
  
  // 4. Frequency adjustment
  for platform, freq_data in analytics:
    if freq_data.posts_per_week < strategy.target and freq_data.missed_opportunity > 0:
      recommendations.append({
        type: "frequency_increase",
        title: f"Increase {platform} posting frequency",
        description: f"Adding {freq_data.missed_opportunity} more posts/week could reach {estimated} more users"
      })
  
  return sorted(recommendations, key=lambda r: impact_score(r.impact), reverse=True)
```

**Score Trend Calculation:**
```
function calculate_score_trend(strategy, current_period):
  history = []
  for week in last_12_weeks:
    score = calculate_adherence_score(strategy, week.start, week.end)
    history.append({week: week.start, score: score})
  
  trend_direction = "up" if history[-1].score > history[-2].score 
                    else "down" if history[-1].score < history[-2].score
                    else "flat"
  
  delta = history[-1].score - history[-2].score
  return {history, trend_direction, delta}
```

**Performance Data Aggregation:**
```
function aggregate_pillar_performance(strategy, period):
  For each pillar in strategy.content_pillars:
    posts = published posts with this pillar_name in period
    
    For each post:
      metrics = AnalyticsMetric where post_id = post.id
      
    pillar_stats = {
      pillar: pillar.name,
      posts_published: len(posts),
      avg_engagement_rate: mean(m.engagement / m.impressions for m in metrics),
      avg_reach: mean(m.reach for m in metrics),
      total_clicks: sum(m.clicks for m in metrics),
      top_post_id: post with max engagement
    }
    
  return pillar_stats sorted by avg_engagement_rate descending
```

### 5.5 Integration Points

| Existing Service | Integration | Direction | How Used |
|-----------------|-------------|-----------|----------|
| `AnalyticsMetric` model | Performance data | Inbound | Core data source for pillar/platform performance metrics. Queried for engagement, reach, clicks per post. |
| `content_slots` model | Plan vs actual | Inbound | Slot status distribution drives adherence calculations (planned, published, pending, etc.). |
| `content_strategies` model | Target configuration | Inbound | Strategy's posting_frequency and content_pillars define targets for adherence calculation. |
| `get_best_times_for_workspace` (best_time_recommender) | Timing insights | Inbound | Recommendations engine uses workspace analytics to suggest optimal timing adjustments. |
| `PostPlatform` model | Published status | Inbound | Verified publish status for accurate published_vs_planned calculation. |
| `Post` model | Post metadata | Inbound | Join with AnalyticsMetric for performance aggregation. |
| Celery (`compute_performance_report`) | Weekly computation | Trigger | Weekly task computes and caches adherence scores. Dashboard reads from cache. |
| Redis | Score caching | Outbound | Adherence scores cached for 15 min, performance data for 1 hour to avoid recomputation. |

---

## Cross-Cutting Concerns

### Migration Files Required

| Migration | Tables | Purpose |
|-----------|--------|---------|
| `004_add_content_strategies.py` | `content_strategies`, `strategy_audit_log` | Strategy definition + audit trail |
| `005_add_content_plans.py` | `content_plans` | Weekly content plans |
| `006_add_content_slots.py` | `content_slots` | Individual content slots within plans |
| `007_add_approval_audit_log.py` | `approval_audit_log` | Approval action history |

### Celery Beat Schedule Additions

```python
# Daily content generation
"generate-strategy-content": {
    "task": "app.tasks.strategy.generate_weekly_content",
    "schedule": crontab(hour=6, minute=0),  # 6 AM UTC daily
}

# Weekly performance report
"strategy-performance-report": {
    "task": "app.tasks.strategy.compute_performance_report", 
    "schedule": crontab(hour=8, minute=0, day_of_week=1),  # Monday 8 AM UTC
}

# Daily adherence score update
"strategy-adherence-update": {
    "task": "app.tasks.strategy.update_adherence_scores",
    "schedule": crontab(hour=7, minute=30),  # 7:30 AM UTC daily
}
```

### Feature Flag Requirements

| Flag | Default | Purpose |
|------|---------|---------|
| `strategy_engine_enabled` | `false` | Master toggle for strategy engine features |
| `auto_approve_enabled` | `false` | Allow auto-approve behavior (per-workspace) |
| `ai_generation_enabled` | `false` | Toggle AI content generation (disable to save costs) |
| `dashboard_recommendations` | `false` | Toggle AI recommendations on dashboard |

### Estimated Effort

| Feature | Backend | Frontend | Total |
|---------|---------|----------|-------|
| Strategy Wizard | 5 days | 5 days | 10 days |
| AI Content Generation | 8 days | 3 days | 11 days |
| Smart Scheduling | 4 days | 4 days | 8 days |
| Approval Flow | 4 days | 4 days | 8 days |
| Adherence Dashboard | 3 days | 4 days | 7 days |
| **Total** | **24 days** | **20 days** | **44 days** |

*Note: Assumes 2 backend engineers + 2 frontend engineers working in parallel. Sequential dependency: Feature 1 → Feature 2 → Feature 3/4 (parallel) → Feature 5.*
