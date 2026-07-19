---
type: community
cohesion: 0.22
members: 9
---

# Webhooks

**Cohesion:** 0.22 - loosely connected
**Members:** 9 nodes

## Members
- [[TODO Mark subscription as cancelled]] - rationale - backend/app/api/webhooks.py
- [[TODO Notify user, mark subscription as past_due]] - rationale - backend/app/api/webhooks.py
- [[TODO Update subscription in database]] - rationale - backend/app/api/webhooks.py
- [[TODO Update subscription status]] - rationale - backend/app/api/webhooks.py
- [[Handle Stripe webhook events.]] - rationale - backend/app/api/webhooks.py
- [[Request_2]] - code
- [[Stripe webhook handler.]] - rationale - backend/app/api/webhooks.py
- [[stripe_webhook()]] - code - backend/app/api/webhooks.py
- [[webhooks.py]] - code - backend/app/api/webhooks.py

## Live Query (requires Dataview plugin)

```dataview
TABLE source_file, type FROM #community/Webhooks
SORT file.name ASC
```

## Connections to other communities
- 1 edge to [[_COMMUNITY_Any_1]]
- 1 edge to [[_COMMUNITY_Asyncsession_3]]

## Top bridge nodes
- [[webhooks.py]] - degree 7, connects to 1 community
- [[stripe_webhook()]] - degree 4, connects to 1 community