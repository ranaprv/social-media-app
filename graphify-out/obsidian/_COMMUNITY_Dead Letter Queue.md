---
type: community
cohesion: 0.18
members: 20
---

# Dead Letter Queue

**Cohesion:** 0.18 - loosely connected
**Members:** 20 nodes

## Members
- [[Any_61]] - code
- [[AsyncSession_71]] - code
- [[Bulk retry multiple failed items at once.]] - rationale - backend/app/services/dead_letter_queue.py
- [[Calculate what percentage of retried items eventually succeeded.]] - rationale - backend/app/services/dead_letter_queue.py
- [[Categorize an error message into a known category.]] - rationale - backend/app/services/dead_letter_queue.py
- [[Count failed items by error category.]] - rationale - backend/app/services/dead_letter_queue.py
- [[Dead-letter queue — manages failed publishes with full retry history.  Tracks ev]] - rationale - backend/app/services/dead_letter_queue.py
- [[Detailed error analytics for the dead-letter queue.]] - rationale - backend/app/services/dead_letter_queue.py
- [[Get a human-readable retry suggestion based on error category.]] - rationale - backend/app/services/dead_letter_queue.py
- [[Get failed publishes with full error context.      Returns detailed failure info]] - rationale - backend/app/services/dead_letter_queue.py
- [[Move a failed item back to the scheduled queue for retry.]] - rationale - backend/app/services/dead_letter_queue.py
- [[_calc_retry_success_rate()]] - code - backend/app/services/dead_letter_queue.py
- [[_categorize_error()]] - code - backend/app/services/dead_letter_queue.py
- [[_count_by_category()]] - code - backend/app/services/dead_letter_queue.py
- [[_get_retry_suggestion()]] - code - backend/app/services/dead_letter_queue.py
- [[bulk_retry_dead_letter()]] - code - backend/app/services/dead_letter_queue.py
- [[dead_letter_queue.py]] - code - backend/app/services/dead_letter_queue.py
- [[get_dead_letter_queue()]] - code - backend/app/services/dead_letter_queue.py
- [[get_error_analytics()]] - code - backend/app/services/dead_letter_queue.py
- [[retry_from_dead_letter()]] - code - backend/app/services/dead_letter_queue.py

## Live Query (requires Dataview plugin)

```dataview
TABLE source_file, type FROM #community/Dead_Letter_Queue
SORT file.name ASC
```

## Connections to other communities
- 4 edges to [[_COMMUNITY_Any_3]]
- 2 edges to [[_COMMUNITY_Any]]
- 1 edge to [[_COMMUNITY_Any_1]]

## Top bridge nodes
- [[get_error_analytics()]] - degree 8, connects to 2 communities
- [[bulk_retry_dead_letter()]] - degree 7, connects to 2 communities
- [[dead_letter_queue.py]] - degree 10, connects to 1 community
- [[get_dead_letter_queue()]] - degree 8, connects to 1 community
- [[retry_from_dead_letter()]] - degree 5, connects to 1 community