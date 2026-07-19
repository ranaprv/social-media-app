---
type: community
cohesion: 0.06
members: 44
---

# Any

**Cohesion:** 0.06 - loosely connected
**Members:** 44 nodes

## Members
- [[API key management — generate, rotate, revoke keys.  Manages API access keys for]] - rationale - backend/app/services/api_key_management.py
- [[Activity]] - code - backend/app/models/content.py
- [[Any_15]] - code
- [[Any_19]] - code
- [[Any_32]] - code
- [[Any_48]] - code
- [[AsyncSession_41]] - code
- [[AsyncSession_44]] - code
- [[AsyncSession_53]] - code
- [[AsyncSession_64]] - code
- [[Audit log — track who did what when for scheduling operations.  Logs all schedul]] - rationale - backend/app/services/audit_log.py
- [[Auto-approve a slot if brand_voice_score meets threshold.          Creates Post]] - rationale - backend/app/tasks/content_generation.py
- [[Campaign Calendar — cross-platform content calendar with campaign arcs.  Manages]] - rationale - backend/app/services/campaign_calendar.py
- [[Content pipeline orchestrator — draft→approve→schedule→publish→track.  Manages t]] - rationale - backend/app/services/content_pipeline.py
- [[Create a campaign with coordinated content schedule.]] - rationale - backend/app/services/campaign_calendar.py
- [[Create a new API key for a workspace.]] - rationale - backend/app/services/api_key_management.py
- [[Generate a new API key pair.]] - rationale - backend/app/services/api_key_management.py
- [[Get all pipeline stages.]] - rationale - backend/app/services/content_pipeline.py
- [[Get audit log entries with filtering.]] - rationale - backend/app/services/audit_log.py
- [[Get audit statistics.]] - rationale - backend/app/services/audit_log.py
- [[Get available API key permission scopes.]] - rationale - backend/app/services/api_key_management.py
- [[Get available campaign type templates.]] - rationale - backend/app/services/campaign_calendar.py
- [[Get the current pipeline status for a workspace.]] - rationale - backend/app/services/content_pipeline.py
- [[Get valid status transitions from current status.]] - rationale - backend/app/services/content_pipeline.py
- [[Log a scheduling action to the audit trail.]] - rationale - backend/app/services/audit_log.py
- [[Transition a post or platform entry to a new status.]] - rationale - backend/app/services/content_pipeline.py
- [[_auto_approve_slot()]] - code - backend/app/tasks/content_generation.py
- [[api_key_management.py]] - code - backend/app/services/api_key_management.py
- [[audit_log.py]] - code - backend/app/services/audit_log.py
- [[campaign_calendar.py]] - code - backend/app/services/campaign_calendar.py
- [[content_pipeline.py]] - code - backend/app/services/content_pipeline.py
- [[create_api_key()]] - code - backend/app/services/api_key_management.py
- [[create_campaign()_1]] - code - backend/app/services/campaign_calendar.py
- [[generate_api_key()]] - code - backend/app/services/api_key_management.py
- [[get_audit_log()_1]] - code - backend/app/services/audit_log.py
- [[get_audit_stats()]] - code - backend/app/services/audit_log.py
- [[get_campaign_types()]] - code - backend/app/services/campaign_calendar.py
- [[get_key_scopes()]] - code - backend/app/services/api_key_management.py
- [[get_pipeline_stages()]] - code - backend/app/services/content_pipeline.py
- [[get_pipeline_status()]] - code - backend/app/services/content_pipeline.py
- [[get_valid_transitions()]] - code - backend/app/services/content_pipeline.py
- [[log_scheduling_action()]] - code - backend/app/services/audit_log.py
- [[revoke_api_key()]] - code - backend/app/services/api_key_management.py
- [[transition_status()]] - code - backend/app/services/content_pipeline.py

## Live Query (requires Dataview plugin)

```dataview
TABLE source_file, type FROM #community/Any
SORT file.name ASC
```

## Connections to other communities
- 5 edges to [[_COMMUNITY_Any]]
- 5 edges to [[_COMMUNITY_Any_1]]
- 4 edges to [[_COMMUNITY_Asyncsession_2]]
- 2 edges to [[_COMMUNITY_Any_3]]
- 1 edge to [[_COMMUNITY_Database]]
- 1 edge to [[_COMMUNITY_Asyncsession]]
- 1 edge to [[_COMMUNITY_Competitor Tracking]]
- 1 edge to [[_COMMUNITY_Content Brief]]
- 1 edge to [[_COMMUNITY_Content Series]]
- 1 edge to [[_COMMUNITY_Reply Queue]]
- 1 edge to [[_COMMUNITY_Social Listening]]
- 1 edge to [[_COMMUNITY_Social Proof]]
- 1 edge to [[_COMMUNITY_Ugc Campaigns]]

## Top bridge nodes
- [[Activity]] - degree 16, connects to 10 communities
- [[_auto_approve_slot()]] - degree 5, connects to 3 communities
- [[transition_status()]] - degree 7, connects to 2 communities
- [[create_api_key()]] - degree 7, connects to 1 community
- [[api_key_management.py]] - degree 6, connects to 1 community