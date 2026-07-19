---
type: community
cohesion: 0.17
members: 19
---

# Notifications

**Cohesion:** 0.17 - loosely connected
**Members:** 19 nodes

## Members
- [[Any_71]] - code
- [[Create a Slack notification channel config.]] - rationale - backend/app/services/notifications.py
- [[Create a generic webhook notification channel config.]] - rationale - backend/app/services/notifications.py
- [[Create an email notification channel config.]] - rationale - backend/app/services/notifications.py
- [[Load notification config for a workspace.      Returns default config if none is]] - rationale - backend/app/services/notifications.py
- [[Send a notification through configured channels.      Args         notification]] - rationale - backend/app/services/notifications.py
- [[Send notification to Slack via incoming webhook.]] - rationale - backend/app/services/notifications.py
- [[Send notification to a generic webhook URL.]] - rationale - backend/app/services/notifications.py
- [[Send notification via email.]] - rationale - backend/app/services/notifications.py
- [[Webhook notification service — notify on publish successfailure.  Supports   -]] - rationale - backend/app/services/notifications.py
- [[_load_workspace_notification_config()]] - code - backend/app/services/notifications.py
- [[_send_email()]] - code - backend/app/services/notifications.py
- [[_send_slack()]] - code - backend/app/services/notifications.py
- [[_send_webhook()]] - code - backend/app/services/notifications.py
- [[configure_email_notification()]] - code - backend/app/services/notifications.py
- [[configure_slack_notification()]] - code - backend/app/services/notifications.py
- [[configure_webhook_notification()]] - code - backend/app/services/notifications.py
- [[notifications.py]] - code - backend/app/services/notifications.py
- [[send_notification()]] - code - backend/app/services/notifications.py

## Live Query (requires Dataview plugin)

```dataview
TABLE source_file, type FROM #community/Notifications
SORT file.name ASC
```

## Connections to other communities
- 2 edges to [[_COMMUNITY_Asyncsession_3]]
- 1 edge to [[_COMMUNITY_Any_1]]

## Top bridge nodes
- [[notifications.py]] - degree 10, connects to 1 community
- [[_send_email()]] - degree 6, connects to 1 community