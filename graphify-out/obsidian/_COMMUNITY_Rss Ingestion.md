---
type: community
cohesion: 0.24
members: 10
---

# Rss Ingestion

**Cohesion:** 0.24 - loosely connected
**Members:** 10 nodes

## Members
- [[Any_89]] - code
- [[AsyncSession_84]] - code
- [[Fetch and parse an RSS feed, creating draft posts for new items.      Returns su]] - rationale - backend/app/services/rss_ingestion.py
- [[RSS content ingestion — auto-create posts from RSS feeds.  Monitors RSSAtom fee]] - rationale - backend/app/services/rss_ingestion.py
- [[Remove XML tags and decode entities.]] - rationale - backend/app/services/rss_ingestion.py
- [[Simple RSSAtom feed parser.      For production, use a proper XML parser like f]] - rationale - backend/app/services/rss_ingestion.py
- [[_clean_xml()]] - code - backend/app/services/rss_ingestion.py
- [[_parse_feed()]] - code - backend/app/services/rss_ingestion.py
- [[ingest_rss_feed()]] - code - backend/app/services/rss_ingestion.py
- [[rss_ingestion.py]] - code - backend/app/services/rss_ingestion.py

## Live Query (requires Dataview plugin)

```dataview
TABLE source_file, type FROM #community/Rss_Ingestion
SORT file.name ASC
```

## Connections to other communities
- 1 edge to [[_COMMUNITY_Any_1]]
- 1 edge to [[_COMMUNITY_Asyncsession_2]]
- 1 edge to [[_COMMUNITY_Any_3]]

## Top bridge nodes
- [[ingest_rss_feed()]] - degree 7, connects to 2 communities
- [[rss_ingestion.py]] - degree 5, connects to 1 community