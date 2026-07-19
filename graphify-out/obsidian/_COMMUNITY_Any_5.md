---
type: community
cohesion: 0.17
members: 16
---

# Any

**Cohesion:** 0.17 - loosely connected
**Members:** 16 nodes

## Members
- [[AI Content Adapter — rewrites content for each platform using LLM.  Takes a base]] - rationale - backend/app/services/ai_content_adapter.py
- [[Adapt content for multiple platforms in one call.      Returns all adapted versi]] - rationale - backend/app/services/ai_content_adapter.py
- [[Adapt content from one platform format to another.      Returns adapted content]] - rationale - backend/app/services/cross_post_templates.py
- [[Any_7]] - code
- [[Any_59]] - code
- [[Cross-posting templates — adapt content for each platform.  Templates define how]] - rationale - backend/app/services/cross_post_templates.py
- [[Get the content adaptation template for a platform.]] - rationale - backend/app/services/cross_post_templates.py
- [[Suggest how to adapt a post for all other platforms.]] - rationale - backend/app/services/cross_post_templates.py
- [[Use AI to rewrite content for a specific platform.      Falls back to rule-based]] - rationale - backend/app/services/ai_content_adapter.py
- [[adapt_content_ai()]] - code - backend/app/services/ai_content_adapter.py
- [[adapt_content_for_platform()]] - code - backend/app/services/cross_post_templates.py
- [[ai_content_adapter.py]] - code - backend/app/services/ai_content_adapter.py
- [[batch_adapt_content()]] - code - backend/app/services/ai_content_adapter.py
- [[cross_post_templates.py]] - code - backend/app/services/cross_post_templates.py
- [[get_cross_post_suggestions()]] - code - backend/app/services/cross_post_templates.py
- [[get_template()]] - code - backend/app/services/cross_post_templates.py

## Live Query (requires Dataview plugin)

```dataview
TABLE source_file, type FROM #community/Any
SORT file.name ASC
```

## Connections to other communities
- 2 edges to [[_COMMUNITY_Any_1]]
- 1 edge to [[_COMMUNITY_Any_2]]

## Top bridge nodes
- [[adapt_content_ai()]] - degree 6, connects to 1 community
- [[cross_post_templates.py]] - degree 5, connects to 1 community
- [[ai_content_adapter.py]] - degree 4, connects to 1 community