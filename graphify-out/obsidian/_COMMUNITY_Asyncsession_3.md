---
type: community
cohesion: 0.06
members: 50
---

# Asyncsession

**Cohesion:** 0.06 - loosely connected
**Members:** 50 nodes

## Members
- [[AsyncSession_5]] - code
- [[AsyncSession_89]] - code
- [[BaseSettings]] - code
- [[Basic liveness check — is the service running]] - rationale - backend/app/api/health.py
- [[Call OpenAI or return placeholder._1]] - rationale - backend/app/api/ai_writing_tools.py
- [[Config]] - code - backend/app/core/config.py
- [[Deep health check — comprehensive system status.      Includes connection pool s]] - rationale - backend/app/api/health.py
- [[Email service abstraction. Console in dev, SendGridSES in prod.]] - rationale - backend/app/services/email.py
- [[Find PostPlatform rows where scheduled_at = now and status == 'scheduled',]] - rationale - backend/app/tasks/scheduler.py
- [[Get a fresh access token for the given platform and workspace.          This is]] - rationale - backend/app/services/token_refresh.py
- [[Get a valid access token, refreshing if necessary.]] - rationale - backend/app/services/token_refresh.py
- [[Health check endpoints — liveness and readiness probes.  Provides Kubernetes-com]] - rationale - backend/app/api/health.py
- [[Periodic scheduler — checks PostPlatform rows for posts due to publish.  Runs ev]] - rationale - backend/app/tasks/scheduler.py
- [[Periodic task to refresh expiring platform OAuth tokens.]] - rationale - backend/app/tasks/scheduler.py
- [[PlatformConnection_2]] - code
- [[Readiness check — is the service ready to accept traffic      Checks PostgreSQL]] - rationale - backend/app/api/health.py
- [[Refresh Facebook OAuth access token using long-lived token exchange.]] - rationale - backend/app/services/token_refresh.py
- [[Refresh LinkedIn OAuth 2.0 access token using refresh token.]] - rationale - backend/app/services/token_refresh.py
- [[Refresh YouTubeGoogle OAuth 2.0 access token using refresh token.]] - rationale - backend/app/services/token_refresh.py
- [[Refresh tokens for all connected platforms.]] - rationale - backend/app/services/token_refresh.py
- [[Refresh tokens that are about to expire (within 10 minutes).]] - rationale - backend/app/services/token_refresh.py
- [[Send an email. Returns True if sent successfully.]] - rationale - backend/app/services/email.py
- [[Send via SendGrid API.]] - rationale - backend/app/services/email.py
- [[Settings]] - code - backend/app/core/config.py
- [[Token refresh service — automatically refreshes expired OAuth tokens for all pla]] - rationale - backend/app/services/token_refresh.py
- [[Use an AI writing tool on content.]] - rationale - backend/app/api/ai_writing_tools.py
- [[User_5]] - code
- [[_call_ai()_1]] - code - backend/app/api/ai_writing_tools.py
- [[_send_via_sendgrid()]] - code - backend/app/services/email.py
- [[ai_writing_tools.py]] - code - backend/app/api/ai_writing_tools.py
- [[check_scheduled_posts()]] - code - backend/app/tasks/scheduler.py
- [[config.py]] - code - backend/app/core/config.py
- [[deep_health_check()]] - code - backend/app/api/health.py
- [[email.py]] - code - backend/app/services/email.py
- [[get_fresh_token()]] - code - backend/app/services/token_refresh.py
- [[get_settings()]] - code - backend/app/core/config.py
- [[get_valid_token()]] - code - backend/app/services/token_refresh.py
- [[health.py]] - code - backend/app/api/health.py
- [[health_check()]] - code - backend/app/api/health.py
- [[readiness_check()]] - code - backend/app/api/health.py
- [[refresh_all_tokens()]] - code - backend/app/services/token_refresh.py
- [[refresh_expiring_tokens()]] - code - backend/app/services/token_refresh.py
- [[refresh_facebook_token()]] - code - backend/app/services/token_refresh.py
- [[refresh_linkedin_token()]] - code - backend/app/services/token_refresh.py
- [[refresh_platform_tokens()]] - code - backend/app/tasks/scheduler.py
- [[refresh_youtube_token()]] - code - backend/app/services/token_refresh.py
- [[scheduler.py]] - code - backend/app/tasks/scheduler.py
- [[send_email()]] - code - backend/app/services/email.py
- [[token_refresh.py]] - code - backend/app/services/token_refresh.py
- [[use_writing_tool()]] - code - backend/app/api/ai_writing_tools.py

## Live Query (requires Dataview plugin)

```dataview
TABLE source_file, type FROM #community/Asyncsession
SORT file.name ASC
```

## Connections to other communities
- 4 edges to [[_COMMUNITY_Connections Callback]]
- 4 edges to [[_COMMUNITY_Any_1]]
- 3 edges to [[_COMMUNITY_unnamed_5]]
- 3 edges to [[_COMMUNITY_unnamed_25]]
- 3 edges to [[_COMMUNITY_unnamed_74]]
- 3 edges to [[_COMMUNITY_Asyncsession_1]]
- 2 edges to [[_COMMUNITY_Ai Media]]
- 2 edges to [[_COMMUNITY_Any_2]]
- 2 edges to [[_COMMUNITY_Notifications]]
- 2 edges to [[_COMMUNITY_unnamed_81]]
- 1 edge to [[_COMMUNITY_Ai Brand Voice]]
- 1 edge to [[_COMMUNITY_Ai Models]]
- 1 edge to [[_COMMUNITY_unnamed_55]]
- 1 edge to [[_COMMUNITY_Recommendations]]
- 1 edge to [[_COMMUNITY_Repurpose]]
- 1 edge to [[_COMMUNITY_Webhooks]]
- 1 edge to [[_COMMUNITY_unnamed_83]]
- 1 edge to [[_COMMUNITY_Link Shortener]]
- 1 edge to [[_COMMUNITY_unnamed_72]]
- 1 edge to [[_COMMUNITY_unnamed_84]]
- 1 edge to [[_COMMUNITY_unnamed_95]]
- 1 edge to [[_COMMUNITY_Any]]

## Top bridge nodes
- [[get_settings()]] - degree 35, connects to 18 communities
- [[refresh_expiring_tokens()]] - degree 6, connects to 2 communities
- [[get_valid_token()]] - degree 11, connects to 1 community
- [[token_refresh.py]] - degree 9, connects to 1 community
- [[refresh_youtube_token()]] - degree 8, connects to 1 community