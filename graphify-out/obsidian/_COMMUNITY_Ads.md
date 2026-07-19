---
type: community
cohesion: 0.33
members: 9
---

# Ads

**Cohesion:** 0.33 - loosely connected
**Members:** 9 nodes

## Members
- [[AsyncSession]] - code
- [[Compare paid vs organic performance.]] - rationale - backend/app/api/ads.py
- [[Get detailed campaign metrics.]] - rationale - backend/app/api/ads.py
- [[Paid Campaign Tracking — Facebook Ads, LinkedIn Ads, paid vs organic.]] - rationale - backend/app/api/ads.py
- [[User]] - code
- [[ads.py]] - code - backend/app/api/ads.py
- [[get_campaign_details()]] - code - backend/app/api/ads.py
- [[list_campaigns()]] - code - backend/app/api/ads.py
- [[paid_vs_organic()]] - code - backend/app/api/ads.py

## Live Query (requires Dataview plugin)

```dataview
TABLE source_file, type FROM #community/Ads
SORT file.name ASC
```

## Connections to other communities
- 1 edge to [[_COMMUNITY_Any]]

## Top bridge nodes
- [[get_campaign_details()]] - degree 5, connects to 1 community