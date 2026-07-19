---
type: community
cohesion: 0.08
members: 66
---

# Asyncsession

**Cohesion:** 0.08 - loosely connected
**Members:** 66 nodes

## Members
- [[Adherence Score Calculation]] - code - docs/feature-specs-phase1.md
- [[AnalyticsMetric]] - code - backend/app/models/content.py
- [[Any_16]] - code
- [[Approval workflow — DB-backed request → approvereject → publish.  Replaces the]] - rationale - backend/app/services/approval_workflow.py
- [[Approve a post (or specific platform entry) for publishing.      If platform is]] - rationale - backend/app/services/approval_workflow.py
- [[AsyncSession_14]] - code
- [[AsyncSession_28]] - code
- [[AsyncSession_35]] - code
- [[AsyncSession_42]] - code
- [[BaseModel_4]] - code
- [[Compare strategy goals against actual analytics performance.      For each goal]] - rationale - backend/app/api/strategies.py
- [[Connect a social media account.]] - rationale - backend/app/api/connections.py
- [[ContentStrategy_1]] - code - backend/app/models/strategy.py
- [[ContentStrategy]] - code
- [[Disconnect a social media account.]] - rationale - backend/app/api/connections.py
- [[Ensure the system workspace exists. Returns its ID.      Uses a deterministic sl]] - rationale - backend/app/core/workspace.py
- [[Fetch analytics from connected platforms and store in database.]] - rationale - backend/app/services/analytics_collector.py
- [[FrequencyConfig]] - code - backend/app/api/strategies.py
- [[Gap Analysis Algorithm]] - code - docs/feature-specs-phase1.md
- [[Get all posts awaiting approval in a workspace.]] - rationale - backend/app/services/approval_workflow.py
- [[Get approval workflow statistics.]] - rationale - backend/app/services/approval_workflow.py
- [[GoalCreate]] - code - backend/app/api/strategies.py
- [[List all connected accounts for the current user.]] - rationale - backend/app/api/connections.py
- [[PersonaCreate]] - code - backend/app/api/strategies.py
- [[PillarCreate]] - code - backend/app/api/strategies.py
- [[Platform connections — connect social media accounts.]] - rationale - backend/app/api/connections.py
- [[PlatformConnection]] - code - backend/app/models/content.py
- [[Reject a post and return it to draft status.]] - rationale - backend/app/services/approval_workflow.py
- [[Request approval for a post before it can be published.      Sets all PostPlatfo]] - rationale - backend/app/services/approval_workflow.py
- [[Shared workspace utility — ensures the system workspace exists.  Extracted to av]] - rationale - backend/app/core/workspace.py
- [[Strategy CRUD + Wizard API endpoints.]] - rationale - backend/app/api/strategies.py
- [[Strategy-Driven Content Scheduling Engine PRD]] - document - docs/prd-strategy-driven-scheduling-engine.md
- [[StrategyAuditLog]] - code - backend/app/models/strategy.py
- [[StrategyCreate]] - code - backend/app/api/strategies.py
- [[StrategyUpdate]] - code - backend/app/api/strategies.py
- [[User_14]] - code
- [[User_27]] - code
- [[User_32]] - code - backend/app/models/user.py
- [[activate_strategy()]] - code - backend/app/api/strategies.py
- [[approval_workflow.py]] - code - backend/app/services/approval_workflow.py
- [[approve_post()_1]] - code - backend/app/services/approval_workflow.py
- [[archive_strategy()]] - code - backend/app/api/strategies.py
- [[collect_analytics_for_workspace()]] - code - backend/app/services/analytics_collector.py
- [[compute_stats()]] - code - backend/app/api/strategies.py
- [[connect_platform()]] - code - backend/app/api/connections.py
- [[connections.py]] - code - backend/app/api/connections.py
- [[create_strategy()]] - code - backend/app/api/strategies.py
- [[disconnect_platform()]] - code - backend/app/api/connections.py
- [[ensure_system_workspace()]] - code - backend/app/core/workspace.py
- [[get_approval_stats()_1]] - code - backend/app/services/approval_workflow.py
- [[get_audit_log()]] - code - backend/app/api/strategies.py
- [[get_defaults()]] - code - backend/app/api/strategies.py
- [[get_goal_tracking()]] - code - backend/app/api/strategies.py
- [[get_pending_approvals()]] - code - backend/app/services/approval_workflow.py
- [[get_strategy()]] - code - backend/app/api/strategies.py
- [[list_connections()]] - code - backend/app/api/connections.py
- [[list_strategies()]] - code - backend/app/api/strategies.py
- [[log_audit()_1]] - code - backend/app/api/strategies.py
- [[normalize_pillars()]] - code - backend/app/api/strategies.py
- [[pause_strategy()]] - code - backend/app/api/strategies.py
- [[quick_start()]] - code - backend/app/api/strategies.py
- [[reject_post()]] - code - backend/app/services/approval_workflow.py
- [[request_approval()]] - code - backend/app/services/approval_workflow.py
- [[strategies.py]] - code - backend/app/api/strategies.py
- [[update_strategy()]] - code - backend/app/api/strategies.py
- [[workspace.py]] - code - backend/app/core/workspace.py

## Live Query (requires Dataview plugin)

```dataview
TABLE source_file, type FROM #community/Asyncsession
SORT file.name ASC
```

## Connections to other communities
- 22 edges to [[_COMMUNITY_Content Generation]]
- 12 edges to [[_COMMUNITY_Asyncsession]]
- 11 edges to [[_COMMUNITY_Asyncsession_2]]
- 10 edges to [[_COMMUNITY_Any]]
- 6 edges to [[_COMMUNITY_Approvals]]
- 6 edges to [[_COMMUNITY_Database]]
- 4 edges to [[_COMMUNITY_Connections Callback]]
- 4 edges to [[_COMMUNITY_Any_3]]
- 3 edges to [[_COMMUNITY_Asyncsession_3]]
- 2 edges to [[_COMMUNITY_Media]]
- 2 edges to [[_COMMUNITY_Analytics Feedback]]
- 2 edges to [[_COMMUNITY_Hashtag Performance]]
- 2 edges to [[_COMMUNITY_Analytics Collector]]
- 1 edge to [[_COMMUNITY_Ai Keys]]
- 1 edge to [[_COMMUNITY_Any_1]]
- 1 edge to [[_COMMUNITY_Content Forecast]]
- 1 edge to [[_COMMUNITY_Content Performance Engine]]
- 1 edge to [[_COMMUNITY_Content Pillar Manager]]
- 1 edge to [[_COMMUNITY_Report Generator]]

## Top bridge nodes
- [[AnalyticsMetric]] - degree 26, connects to 9 communities
- [[User_32]] - degree 29, connects to 5 communities
- [[ensure_system_workspace()]] - degree 29, connects to 4 communities
- [[PlatformConnection]] - degree 21, connects to 4 communities
- [[ContentStrategy_1]] - degree 27, connects to 2 communities