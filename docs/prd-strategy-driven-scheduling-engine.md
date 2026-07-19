# PRD: Strategy-Driven Content Scheduling Engine

**Status**: Draft  
**Author**: Product Manager  
**Last Updated**: 2026-07-18  
**Version**: 1.0  
**Stakeholders**: Eng Lead, Design Lead, AI/ML Lead, Marketing Lead, Customer Success

---

## 1. Problem Statement

Today, users manually create individual posts, pick platforms, and schedule them one at a time. The scheduler, AI content adapter, and approval workflow all work — but they're disconnected from any strategic intent. There's no way to say "I want to grow my LinkedIn presence with thought-leadership content 3x/week and my Instagram with behind-the-scenes content 5x/week" and have the system automatically generate and schedule an entire week's content aligned to that strategy.

**The gap**: Strategy and execution are decoupled. Users define what they want (growth goals) but do all the tactical work themselves — deciding what to post, when to post it, adapting it per platform, and manually filling the calendar.

**Who experiences this**:
- **Content creators** (1-3 person teams): Spend 8-12 hours/week on content ideation + scheduling instead of creating
- **Social media managers** (agencies/brands): Managing 5-15 client accounts, each with different strategies — the manual overhead doesn't scale
- **Team leads**: Can't see whether the team's publishing cadence actually aligns with stated growth goals

**Cost of not solving it**:
- Users churn to competitors with "strategy-to-schedule" automation (Buffer's AI Assistant, Hootsuite's OwlyWriter, Sprout's AI publishing)
- Platform analytics show inconsistent posting — the #1 predictor of poor social growth
- Support tickets: "How do I plan a week of content?" is a top-10 support theme

**Evidence**:
- User interviews (n=18): 14/18 said "I know what I want to post about but I don't have time to create and schedule everything"
- Behavioral data: 62% of workspaces have <10 posts/month despite having 3+ connected platforms
- Support signal: "content planning" and "posting schedule" appear in 23% of feature-request tickets
- Competitive signal: Buffer, Hootsuite, and Sprout Social all shipped AI content planning in Q1-Q2 2026

---

## 2. Goals & Success Metrics

| Goal | Metric | Current Baseline | Target | Measurement Window |
|------|--------|-----------------|--------|--------------------|
| Increase content output | Avg posts/workspace/month | 8.2 | 22 | 90 days post-launch |
| Reduce time-to-publish | Minutes from idea to scheduled | ~45 min | <5 min | 60 days post-launch |
| Improve strategy adherence | % posts aligned to defined pillars | 0% (no strategy) | ≥80% | 90 days post-launch |
| Drive feature adoption | % active workspaces using strategy engine | 0% | 30% | 90 days post-launch |
| Reduce content creation churn | Monthly churn rate (content-focused users) | 6.8% | 4.5% | 90 days post-launch |

---

## 3. Non-Goals

- **Not a full social listening tool.** We won't monitor competitor strategies or trending topics in v1. That's a separate initiative.
- **Not redesigning the existing manual post creation flow.** The existing Post → PostPlatform → schedule pipeline stays. Strategy engine is additive.
- **Not supporting paid/ad content.** Organic content only. Paid promotion is a separate capability.
- **Not multi-account/agency mode for v1.** Strategy engine works per-workspace. Multi-client strategy templates are Phase 2.
- **Not real-time content optimization.** The engine won't dynamically rewrite posts based on mid-day performance signals. Feedback loop is weekly, not real-time.

---

## 4. User Personas & Stories

### Primary Persona: Solo Content Creator ("Priya")
- Runs a personal brand on LinkedIn + Instagram
- Posts inconsistently (2-4x/week when inspired, 0x/week when busy)
- Knows her content pillars (career advice, tech insights, personal stories) but can't maintain consistency

**Story 1**: As Priya, I want to define my content strategy (goals, pillars, posting frequency) once, so the system automatically generates and schedules a week of content aligned to my brand.

**Acceptance Criteria**:
- [ ] Given I'm on the strategy setup page, when I define goals + pillars + frequency + platforms, then a content calendar is generated within 60 seconds
- [ ] Given the calendar is generated, when I review each post, I can approve, edit, or skip individual posts
- [ ] Given I approve posts, when the scheduled time arrives, they publish to the correct platforms with platform-optimized content
- [ ] Performance: Calendar generation completes in <60s for a 7-day, 5-platform plan

**Story 2**: As Priya, I want the AI to generate platform-specific content from my strategy (LinkedIn long-form, Instagram captions with hashtags, X threads), so I don't have to manually adapt content for each network.

**Acceptance Criteria**:
- [ ] Given a strategy with "thought leadership" pillar, when AI generates LinkedIn content, it produces 300-2000 char posts with hooks and CTAs
- [ ] Given the same pillar, when AI generates Instagram content, it includes 3-5 hashtags, emoji, and stays under 2200 chars
- [ ] Given the same pillar, when AI generates X content, it produces 280-char tweets, optionally as threads (3-5 tweets)
- [ ] Given a YouTube pillar, AI generates SEO-optimized titles + descriptions with timestamps and CTAs

### Secondary Persona: Social Media Manager ("Marcus")
- Manages 3 brand accounts across LinkedIn, X, Instagram, Facebook
- Needs to maintain consistent posting schedules across all accounts
- Uses approval workflows for client content

**Story 3**: As Marcus, I want to create a content strategy for each client workspace and have the engine auto-generate content I can review in bulk, so I can scale from 3 to 10 clients without hiring.

**Acceptance Criteria**:
- [ ] Given I manage multiple workspaces, when I set up strategies for each, they operate independently
- [ ] Given generated content is ready, when I open the review queue, I see all pending posts grouped by workspace with approve/reject/skip actions
- [ ] Given I reject a post, when I provide feedback ("too formal", "missing CTA"), the AI uses that signal for regeneration
- [ ] Given approval workflow is enabled, posts don't publish until explicitly approved

### Tertiary Persona: Team Lead ("Aisha")
- Leads a 4-person content team
- Sets quarterly growth goals and needs visibility into whether publishing cadence aligns

**Story 4**: As Aisha, I want to see a dashboard showing strategy adherence (posts published vs. planned, pillar distribution, platform coverage), so I can course-correct weekly.

**Acceptance Criteria**:
- [ ] Given a defined strategy, when I open the strategy dashboard, I see: posts/week vs. target, pillar distribution pie chart, platform coverage bar
- [ ] Given it's mid-week and we're behind target, when I view the dashboard, I see a "catch-up" suggestion (extra posts to fill gaps)
- [ ] Given I click "adjust strategy", when I change frequency or pillars, the upcoming calendar regenerates

---

## 5. Core Capabilities

### 5.1 Strategy Definition

Users define a `ContentStrategy` per workspace with:

```json
{
  "id": "str_abc123",
  "workspace_id": "ws_xyz",
  "name": "Q3 LinkedIn Growth",
  "goals": [
    {
      "type": "engagement_rate",
      "target": 4.5,
      "platform": "linkedin",
      "baseline": 2.1
    },
    {
      "type": "follower_growth",
      "target": 500,
      "platform": "all",
      "period": "quarterly"
    }
  ],
  "content_pillars": [
    {
      "name": "Thought Leadership",
      "description": "Industry insights, trend analysis, professional opinions",
      "weight": 0.4,
      "platforms": ["linkedin", "x"],
      "tone": "authoritative",
      "example_hooks": ["Here's what most people get wrong about...", "I spent 5 years learning this the hard way..."]
    },
    {
      "name": "Behind the Scenes",
      "description": "Team culture, process reveals, day-in-the-life",
      "weight": 0.3,
      "platforms": ["instagram", "facebook"],
      "tone": "casual",
      "example_hooks": ["What our Tuesday mornings actually look like...", "The messy middle of building X..."]
    },
    {
      "name": "Educational",
      "description": "How-tos, tutorials, tips and tricks",
      "weight": 0.3,
      "platforms": ["linkedin", "instagram", "youtube", "x"],
      "tone": "friendly-expert",
      "example_hooks": ["3 things I wish I knew before...", "The one tool that changed everything..."]
    }
  ],
  "audience_personas": [
    {
      "name": "Tech Startup Founders",
      "demographics": "25-40, startup founders, Series A-B",
      "pain_points": ["scaling challenges", "hiring", "product-market fit"],
      "content_preferences": ["data-driven", "actionable", "no fluff"]
    }
  ],
  "posting_frequency": {
    "linkedin": { "posts_per_week": 3, "preferred_days": [1, 2, 3], "preferred_hours": [8, 12, 17] },
    "x": { "posts_per_week": 5, "preferred_days": [0, 1, 2, 3, 4], "preferred_hours": [9, 12, 17] },
    "instagram": { "posts_per_week": 4, "preferred_days": [1, 3, 5, 6], "preferred_hours": [11, 19] },
    "facebook": { "posts_per_week": 2, "preferred_days": [1, 3], "preferred_hours": [13, 15] },
    "youtube": { "posts_per_week": 1, "preferred_days": [5], "preferred_hours": [15] }
  },
  "status": "active",
  "auto_generate": true,
  "generate_ahead_days": 7,
  "approval_required": true,
  "created_at": "2026-07-18T10:00:00Z",
  "updated_at": "2026-07-18T10:00:00Z"
}
```

**Strategy Setup Flow**:
1. User selects platforms to activate
2. System shows a guided wizard: Goals → Content Pillars → Audience → Frequency → Review
3. AI suggests pillar templates based on industry and platform defaults (user can customize)
4. User confirms → system generates first week of content immediately
5. Strategy activates — engine regenerates content weekly, 7 days ahead

### 5.2 AI Content Generation Pipeline

When a strategy is active, the engine runs a weekly content generation cycle:

```
Strategy Config
      │
      ▼
┌─────────────────────┐
│  1. SLOT PLANNER    │  Determine what to generate:
│  (Strategy Engine)  │  - Which pillars need coverage this week
│                     │  - Which platforms need content
│                     │  - How many posts per slot
└─────────┬───────────┘
          │
          ▼
┌─────────────────────┐
│  2. TOPIC RESEARCH  │  For each slot:
│  (AI + Web Search)  │  - Pull trending topics in pillar area
│                     │  - Reference brand voice + past top performers
│                     │  - Generate 3 topic options
└─────────┬───────────┘
          │
          ▼
┌─────────────────────┐
│  3. CONTENT DRAFT   │  For each topic × platform:
│  (LLM Generation)   │  - Generate platform-optimized content
│                     │  - Apply brand voice from BrandVoice model
│                     │  - Respect character limits + format rules
└─────────┬───────────┘
          │
          ▼
┌─────────────────────┐
│  4. QUALITY GATE    │  Automated checks:
│  (Validator)        │  - Platform format compliance
│                     │  - Brand voice consistency score
│                     │  - Duplicate detection
│                     │  - Content safety / moderation
└─────────┬───────────┘
          │
          ▼
┌─────────────────────┐
│  5. SCHEDULE PLACEMENT│  Smart scheduling:
│  (Scheduler)        │  - Best times from BEST_TIMES + workspace analytics
│                     │  - Frequency caps per platform
│                     │  - Content spacing (no back-to-back same pillar)
│                     │  - Create Post + PostPlatform rows
└─────────┬───────────┘
          │
          ▼
┌─────────────────────┐
│  6. APPROVAL QUEUE  │  If approval_required:
│  (HITL)            │  - Posts enter pending_approval status
│                     │  - User reviews, edits, approves/rejects
│                     │  - Rejected posts → regenerate with feedback
└─────────┬───────────┘
          │
          ▼
┌─────────────────────┐
│  7. PUBLISH         │  Existing Celery scheduler picks up:
│  (Existing Engine)  │  - PostPlatform rows with scheduled_at <= now
│                     │  - publish_post task handles API submission
│                     │  - Platform-specific formatting applied
└─────────────────────┘
```

### 5.3 Platform-Specific Content Optimization

The engine reuses and extends the existing `ai_content_adapter.py` with strategy-aware generation:

| Platform | Format | Char Limit | Special Requirements |
|----------|--------|-----------|---------------------|
| **LinkedIn** | Long-form post | 3,000 | Hook → Line breaks → CTA. No hashtags in first line. Article mode for >1,500 chars. |
| **X/Twitter** | Tweet or thread | 280/tweet | Single tweet or 3-5 tweet thread. 1-2 hashtags. No line breaks in single tweet. |
| **Instagram** | Caption + media | 2,200 | Hook in first 125 chars. 3-5 hashtags. Emoji. Always requires media. Carousel support. |
| **Facebook** | Short post | 63,206 (optimal 80-250) | Question-driven. Conversational. Link posts get less reach. |
| **YouTube** | Title + Description | Title: 100 / Desc: 5,000 | SEO keywords in title. Timestamps. Subscribe CTA. Chapters. |

**Platform constraints enforced by `content_validator.py`** (existing) — extended with strategy-specific rules:
- LinkedIn: No hashtags in the first sentence
- Instagram: Minimum 3 hashtags, must have media attached
- X: Thread continuity check (each tweet must flow from previous)
- YouTube: Description must include at least one keyword from the video topic

### 5.4 Smart Scheduling

The scheduling component extends the existing `scheduler_api.py` `BEST_TIMES` with workspace-specific analytics:

**Scheduling algorithm**:
```
For each post to schedule:
  1. Get platform preferred times from strategy config
  2. Cross-reference with workspace analytics (best_time_recommender)
  3. Check frequency caps: no more than N posts/day per platform
  4. Check content spacing: minimum 4-hour gap between posts on same platform
  5. Check pillar diversity: no more than 2 consecutive posts from same pillar
  6. Check for conflicts with manually scheduled posts
  7. Assign optimal slot → create Post + PostPlatform rows
```

**Frequency caps** (defaults, configurable):
- LinkedIn: max 3/day
- X: max 5/day
- Instagram: max 3/day (feed + stories counted separately)
- Facebook: max 2/day
- YouTube: max 1/day

### 5.5 Content Approval Workflow

Extends existing approval system (`approval_workflow.py`) with strategy-specific enhancements:

- **Auto-approve threshold**: If generated content scores ≥0.85 on brand voice consistency AND passes all quality gates, it can skip approval (configurable)
- **Bulk review UI**: All pending posts shown in a calendar or list view with inline editing
- **Feedback loop**: When user edits a generated post, the edit is recorded as training signal for future generations in that pillar
- **Rejection with reason**: User selects from common reasons ("too formal", "off-brand", "wrong pillar", "needs hook", "custom") → AI regenerates with that constraint

### 5.6 Performance Feedback Loop

Weekly analytics feed back into strategy adjustments:

```
Published Post Analytics (from analytics collector)
      │
      ▼
┌─────────────────────────┐
│ PERFORMANCE AGGREGATOR  │  Per pillar, per platform:
│                         │  - Avg engagement rate
│ (runs weekly)           │  - Avg reach
│                         │  - Top performing hooks/formats
└─────────┬───────────────┘
          │
          ▼
┌─────────────────────────┐
│ STRATEGY ADVISOR        │  Recommendations:
│ (AI)                    │  - "Pillar X outperforms by 2.3x — increase weight"
│                         │  - "LinkedIn posts at 8AM get 40% more engagement"
│                         │  - "Instagram carousels outperform single images 3:1"
└─────────┬───────────────┘
          │
          ▼
┌─────────────────────────┐
│ STRATEGY UPDATE         │  Optional auto-adjustments:
│ (User Approval)         │  - Adjust pillar weights
│                         │  - Adjust posting times
│                         │  - Adjust frequency
│                         │  All require user confirmation in v1
└─────────────────────────┘
```

---

## 6. Technical Requirements

### 6.1 New Data Models

```python
# backend/app/models/strategy.py

class ContentStrategy(Base):
    __tablename__ = "content_strategies"

    id = Column(String, primary_key=True)
    workspace_id = Column(String, ForeignKey("workspaces.id"), nullable=False, index=True)
    name = Column(String(200), nullable=False)
    goals = Column(JSON, default=list)            # [{type, target, platform, period}]
    content_pillars = Column(JSON, default=list)   # [{name, description, weight, platforms, tone}]
    audience_personas = Column(JSON, default=list) # [{name, demographics, pain_points}]
    posting_frequency = Column(JSON, default=dict)  # {platform: {posts_per_week, preferred_days, preferred_hours}}
    status = Column(String(16), default="draft", index=True)  # draft | active | paused | archived
    auto_generate = Column(Boolean, default=True)
    generate_ahead_days = Column(Integer, default=7)
    approval_required = Column(Boolean, default=True)
    last_generated_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    workspace = relationship("Workspace", back_populates="strategies")


class ContentPlan(Base):
    __tablename__ = "content_plans"

    id = Column(String, primary_key=True)
    strategy_id = Column(String, ForeignKey("content_strategies.id"), nullable=False, index=True)
    workspace_id = Column(String, ForeignKey("workspaces.id"), nullable=False, index=True)
    week_start = Column(DateTime, nullable=False)   # Monday of the planned week
    status = Column(String(16), default="draft", index=True)  # draft | generating | ready | in_progress | completed
    generated_at = Column(DateTime)
    slot_count = Column(Integer, default=0)
    approved_count = Column(Integer, default=0)
    published_count = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)

    strategy = relationship("ContentStrategy")
    slots = relationship("ContentSlot", back_populates="plan", cascade="all, delete-orphan")


class ContentSlot(Base):
    __tablename__ = "content_slots"

    id = Column(String, primary_key=True)
    plan_id = Column(String, ForeignKey("content_plans.id"), nullable=False, index=True)
    workspace_id = Column(String, ForeignKey("workspaces.id"), nullable=False)
    pillar_name = Column(String(100), nullable=False)
    platform = Column(String(32), nullable=False, index=True)
    scheduled_date = Column(DateTime, nullable=False)
    scheduled_time = Column(String(5))  # "08:00"
    status = Column(String(16), default="empty")  # empty | generating | generated | approved | rejected | published

    # Generated content
    topic = Column(String(500))
    generated_content = Column(Text)
    generated_variants = Column(JSON, default=list)  # [{content, score}]
    selected_variant_index = Column(Integer, default=0)
    media_requirements = Column(JSON, default=dict)  # {type: "image", aspect_ratio: "1:1"}

    # Linked to actual post
    post_id = Column(String, ForeignKey("posts.id"), nullable=True)
    post_platform_id = Column(String, ForeignKey("post_platforms.id"), nullable=True)

    # Approval
    approved_by = Column(String, ForeignKey("users.id"))
    approved_at = Column(DateTime)
    rejection_reason = Column(String(200))
    user_edit_history = Column(JSON, default=list)  # [{before, after, timestamp}]

    created_at = Column(DateTime, default=datetime.utcnow)

    plan = relationship("ContentPlan", back_populates="slots")
```

### 6.2 API Endpoints

```
Strategy Management:
  POST   /api/strategies                    — Create strategy
  GET    /api/strategies                    — List workspace strategies
  GET    /api/strategies/{id}               — Get strategy detail
  PUT    /api/strategies/{id}               — Update strategy
  DELETE /api/strategies/{id}               — Archive strategy
  POST   /api/strategies/{id}/activate      — Activate strategy
  POST   /api/strategies/{id}/pause         — Pause strategy

Content Generation:
  POST   /api/strategies/{id}/generate      — Generate content plan for next N days
  GET    /api/strategies/{id}/plans         — List generated plans
  GET    /api/strategies/{id}/plans/{pid}   — Get plan detail with slots
  POST   /api/strategies/{id}/plans/{pid}/regenerate — Regenerate a plan

Slot Management:
  GET    /api/slots/{id}                    — Get slot detail
  PUT    /api/slots/{id}                    — Edit slot content
  POST   /api/slots/{id}/approve            — Approve slot → creates Post + PostPlatform
  POST   /api/slots/{id}/reject             — Reject slot → triggers regeneration
  POST   /api/slots/{id}/skip               — Skip slot (no post this time)
  POST   /api/slots/{id}/regenerate         — Regenerate content for this slot

Dashboard:
  GET    /api/strategies/{id}/dashboard     — Strategy adherence metrics
  GET    /api/strategies/{id}/performance   — Performance feedback (pillar × platform)
  GET    /api/strategies/{id}/recommendations — AI recommendations for adjustments
```

### 6.3 Integration Points

| System | Integration | Direction | Notes |
|--------|------------|-----------|-------|
| **BrandVoice** | Read tone/style config | Inbound | Strategy generation reads brand voice per workspace |
| **AI Content Adapter** | Generate platform content | Outbound | Extends existing `adapt_content_ai()` with strategy context |
| **Content Validator** | Validate generated posts | Outbound | Uses existing `validate_post()` per platform |
| **Scheduler (Celery)** | Auto-generate weekly | Trigger | New Celery beat task: `generate_strategy_content` runs daily at 6 AM UTC |
| **Post / PostPlatform** | Create publishable posts | Outbound | Approved slots create Post + PostPlatform rows |
| **Approval Workflow** | Route for human review | Outbound | If `approval_required`, slots enter existing approval queue |
| **Analytics Collector** | Feed performance data | Inbound | Existing `collect_all_analytics` feeds strategy dashboard |
| **Content Recycler** | Identify top performers | Inbound | Top performers inform pillar weight adjustments |
| **Best Time Recommender** | Optimize scheduling | Inbound | Workspace analytics improve posting time selection |

### 6.4 Celery Tasks (New)

```python
# New beat schedule entry
"generate-strategy-content": {
    "task": "app.tasks.strategy.generate_weekly_content",
    "schedule": crontab(hour=6, minute=0),  # Daily at 6 AM UTC
}

"strategy-performance-report": {
    "task": "app.tasks.strategy.compute_performance_report",
    "schedule": crontab(hour=8, minute=0, day_of_week=1),  # Weekly Monday 8 AM
}
```

### 6.5 Frontend Components (Next.js)

| Component | Description | Phase |
|-----------|-------------|-------|
| `StrategyWizard` | 4-step setup: Goals → Pillars → Audience → Frequency | P1 |
| `StrategyDashboard` | Adherence metrics, pillar distribution, platform coverage | P1 |
| `ContentPlanView` | Weekly calendar with generated slots, inline edit/approve | P1 |
| `SlotReviewCard` | Individual post preview with approve/reject/edit actions | P1 |
| `PerformanceInsights` | AI-generated recommendations based on analytics | P2 |
| `StrategyTemplates` | Pre-built strategy templates by industry/goal | P2 |
| `BulkApproval` | Approve/reject multiple slots at once | P2 |

---

## 7. Success Metrics

### Primary (North Star)
- **Content Velocity**: Average posts/workspace/month (target: 22, up from 8.2)

### Secondary
| Metric | Target | Measurement |
|--------|--------|-------------|
| Strategy setup completion rate | ≥70% of started setups are activated | Funnel analytics |
| Content plan generation → approval rate | ≥60% of generated slots approved | Slot status tracking |
| Time from strategy definition to first scheduled post | <5 minutes | Timestamp diff |
| Weekly content plan coverage | ≥80% of planned slots publish successfully | Slot publish rate |
| Feature retention (30-day) | ≥50% of strategy users still active at 30 days | Cohort analysis |
| Platform-specific content quality score | ≥0.75 avg brand voice score | BrandVoice scoring |

### Guardrail Metrics (must not regress)
| Metric | Current | Must Not Drop Below |
|--------|---------|-------------------|
| Manual post scheduling success rate | 94% | 90% |
| Platform API error rate | 2.1% | 3% |
| Average page load (calendar view) | 1.2s | 2s |

---

## 8. Risks and Mitigations

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| **AI-generated content feels generic / off-brand** | High | High | BrandVoice integration mandatory. All generated posts scored against brand voice before scheduling. User feedback loop improves quality over time. Allow per-pillar example posts for training. |
| **Platform API rate limits hit during batch generation** | Medium | High | Generate content in staggered batches (max 5 concurrent LLM calls). Cache generated content before scheduling. Respect existing `rate_limit_tracker`. |
| **Users auto-approve everything → poor content damages brand** | Medium | Medium | Default to `approval_required = true`. Auto-approve only if brand voice score ≥0.85 AND passes all quality gates. Show warning if auto-approve is enabled. |
| **Strategy setup wizard has high drop-off** | Medium | Medium | Pre-fill with smart defaults based on connected platforms. Allow "quick start" that generates a strategy from minimal input (3 pillars, 1 goal). Show preview before activation. |
| **Content plan generated but never reviewed (zombie plans)** | High | Low | Nudge notification after 48h if plan has unreviewed slots. Auto-archive plans older than 14 days with no activity. Dashboard shows unreviewed count. |
| **LLM cost spiral from high-volume generation** | Medium | Medium | Track token usage per workspace. Set monthly generation quotas by plan tier. Use cheaper models (GPT-4o-mini) for initial drafts, premium for final polish. |
| **Feedback loop creates echo chamber (same content repeated)** | Low | Medium | Inject diversity constraints: no repeated hooks within 30 days, minimum 3 unique topics per pillar per month, random trending topic injection. |

---

## 9. Phase 1 vs Phase 2 Scope

### Phase 1 — Core Strategy Engine (6 weeks)

**In scope**:
- ContentStrategy CRUD (goals, pillars, audience, frequency)
- Strategy setup wizard (4-step guided flow)
- Weekly content plan generation (AI-powered)
- Platform-specific content optimization (all 5 platforms)
- Smart scheduling with frequency caps
- ContentSlot approval workflow (approve/reject/edit per slot)
- Strategy adherence dashboard (basic metrics)
- Celery task for auto-generation

**Out of scope (Phase 2)**:
- Performance feedback loop (AI recommendations)
- Strategy templates by industry
- Bulk approval UI
- Auto-adjust strategy based on analytics
- Content recycling tied to strategy
- A/B testing for generated content
- Multi-workspace strategy management (agency mode)

### Phase 2 — Intelligence & Optimization (4 weeks, after P1 stabilizes)

**In scope**:
- Performance insights dashboard (pillar × platform performance)
- AI strategy recommendations ("increase pillar X weight")
- Strategy templates (pre-built by industry: SaaS, e-commerce, personal brand, agency)
- Bulk approval (approve/reject entire day/week)
- Auto-adjust strategy (with user confirmation)
- Feedback loop: user edits train future generation
- Content recycling integrated with strategy pillars
- A/B testing: generate 2 variants per slot, pick winner based on performance

### Phase 3 — Advanced (Future Quarter)

- Multi-workspace strategy (agency mode)
- Competitor content gap analysis
- Real-time content optimization (mid-day adjustments)
- Paid content strategy integration
- Team workload balancing (distribute slots across team members)
- Content brief sharing (client → agency workflow)

---

## 10. Open Questions

| Question | Owner | Deadline | Decision |
|----------|-------|----------|----------|
| Should strategy generation be async (background task) or sync (wait for response)? | Eng Lead | Week 1 | Async preferred — LLM calls take 10-30s per post, a full week plan = 20+ posts. Show progress bar, notify when ready. |
| Which LLM provider for bulk generation? Cost model? | AI/ML Lead | Week 1 | Use workspace's configured provider (from `PlatformProviderConfig`). Fall back to default (openai/gpt-4o-mini) for cost efficiency. |
| How many content variants per slot? (1 vs 2-3 options) | Design Lead | Week 2 | Phase 1: 1 variant with edit capability. Phase 2: 2-3 variants with A/B testing. |
| Should the strategy wizard be a modal or a full page? | Design Lead | Week 2 | Full page with sidebar progress indicator. Too complex for a modal. |
| What happens to existing `content_planner` endpoint? | Eng Lead | Week 1 | Deprecate. Replace with strategy-backed plans. Migration: existing plans become read-only. |
| Rate limiting: how many workspaces can generate simultaneously? | Eng Lead | Week 1 | Max 10 concurrent generation tasks globally. Queue overflow → retry with backoff. |

---

## 11. Dependencies

| Dependency | Type | Owner | Risk |
|-----------|------|-------|------|
| BrandVoice model exists | ✅ Ready | — | — |
| AI content adapter exists | ✅ Ready | — | — |
| Content validator exists | ✅ Ready | — | — |
| Celery scheduler running | ✅ Ready | — | — |
| Post + PostPlatform models | ✅ Ready | — | — |
| Approval workflow exists | ✅ Ready | — | — |
| Best time recommender exists | ✅ Ready | — | — |
| Content recycler exists | ✅ Ready | — | — |
| Strategy UI (Next.js) | 🔨 New | Frontend Eng | Medium — 4-week frontend build |
| Strategy DB migration | 🔨 New | Backend Eng | Low — standard Alembic migration |
| Celery beat schedule update | 🔨 New | Backend Eng | Low |

---

## 12. Rollout Plan

| Phase | Date | Audience | Success Gate |
|-------|------|----------|-------------|
| Internal alpha | Week 1-2 | Team + 5 design partners | Strategy wizard completes, content generates, posts schedule |
| Closed beta | Week 3-4 | 25 opted-in customers | ≥50% of generated posts approved, <5% error rate |
| GA rollout | Week 5-6 | All workspaces with 2+ connected platforms | Feature adoption ≥15% in first 30 days |

**Rollback Criteria**: If post publish error rate exceeds 5% or brand voice consistency drops below 0.6 avg score, pause auto-generation and notify affected workspaces.

---

## Appendix A: Platform Content Format Reference

```
LinkedIn:
  - Max chars: 3,000 (post), 210,000 (article)
  - Media: Images (1200x627), Videos (10min max), PDFs (carousel)
  - Hashtags: 3-5, not in first line
  - Best practice: Hook → Line breaks → Value → CTA

X/Twitter:
  - Max chars: 280 (tweet), 25,000 (Blue subscribers)
  - Media: Images (16:9), Videos (2:20 max), GIFs
  - Hashtags: 1-2 max
  - Threads: Each tweet separate, max 25 tweets
  - Best practice: Punchy opener → Value → Engagement ask

Instagram:
  - Max chars: 2,200 (caption)
  - Media: Photos (1:1, 4:5, 1.91:1), Reels (9:16, 90s), Carousels (10 slides)
  - Hashtags: 3-5 (algorithm prefers quality over quantity)
  - First 125 chars visible before "more"
  - Best practice: Visual-first → Caption supports image → Hashtags → CTA

Facebook:
  - Max chars: 63,206 (but 80-250 optimal for engagement)
  - Media: Images (1200x630), Videos (unlimited length), Links
  - No character limit penalty for shorter posts
  - Best practice: Question → Short value → Link (if applicable)

YouTube:
  - Title: 100 chars (60-70 optimal)
  - Description: 5,000 chars (first 150 visible in search)
  - Tags: 500 chars total
  - Best practice: SEO keyword in title → Hook in description → Timestamps → CTA
```

## Appendix B: Content Pillar Templates (AI-Suggested)

| Industry | Suggested Pillars | Example |
|----------|------------------|---------|
| SaaS / Tech | Thought Leadership, Product Updates, Customer Stories, Industry Trends, How-To/Tutorials | — |
| E-commerce | Product Showcases, Behind the Scenes, User-Generated Content, Promotions, Lifestyle | — |
| Personal Brand | Career Insights, Lessons Learned, Hot Takes, Book/Tool Reviews, Community Engagement | — |
| Agency / Services | Case Studies, Team Culture, Industry Commentary, Educational, Client Wins | — |
| Non-Profit | Impact Stories, Volunteer Spotlights, Campaign Updates, Education, Call to Action | — |
