---
type: community
cohesion: 0.29
members: 8
---

# Link Shortener

**Cohesion:** 0.29 - loosely connected
**Members:** 8 nodes

## Members
- [[Generate a short ID from URL hash.]] - rationale - backend/app/services/link_shortener.py
- [[Get click statistics for a short link.]] - rationale - backend/app/services/link_shortener.py
- [[Link shortening service — Bitly API + TinyURL fallback.]] - rationale - backend/app/services/link_shortener.py
- [[Shorten a URL using Bitly or TinyURL fallback.]] - rationale - backend/app/services/link_shortener.py
- [[_short_id()]] - code - backend/app/services/link_shortener.py
- [[get_click_stats()]] - code - backend/app/services/link_shortener.py
- [[link_shortener.py]] - code - backend/app/services/link_shortener.py
- [[shorten_url()]] - code - backend/app/services/link_shortener.py

## Live Query (requires Dataview plugin)

```dataview
TABLE source_file, type FROM #community/Link_Shortener
SORT file.name ASC
```

## Connections to other communities
- 1 edge to [[_COMMUNITY_Asyncsession_3]]
- 1 edge to [[_COMMUNITY_Any_1]]

## Top bridge nodes
- [[link_shortener.py]] - degree 5, connects to 1 community
- [[shorten_url()]] - degree 4, connects to 1 community