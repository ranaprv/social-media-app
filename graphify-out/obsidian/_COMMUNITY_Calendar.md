---
type: community
cohesion: 0.25
members: 14
---

# Calendar

**Cohesion:** 0.25 - loosely connected
**Members:** 14 nodes

## Members
- [[AsyncSession_12]] - code
- [[Create a new calendar event.]] - rationale - backend/app/api/calendar.py
- [[Create a new campaign.]] - rationale - backend/app/api/calendar.py
- [[Delete a calendar event.]] - rationale - backend/app/api/calendar.py
- [[Get calendar events within a date range.]] - rationale - backend/app/api/calendar.py
- [[Update a calendar event (drag & drop, status change).]] - rationale - backend/app/api/calendar.py
- [[User_12]] - code
- [[calendar.py]] - code - backend/app/api/calendar.py
- [[create_calendar_event()]] - code - backend/app/api/calendar.py
- [[create_campaign()]] - code - backend/app/api/calendar.py
- [[delete_calendar_event()]] - code - backend/app/api/calendar.py
- [[get_calendar_events()]] - code - backend/app/api/calendar.py
- [[get_campaigns()]] - code - backend/app/api/calendar.py
- [[update_calendar_event()]] - code - backend/app/api/calendar.py

## Live Query (requires Dataview plugin)

```dataview
TABLE source_file, type FROM #community/Calendar
SORT file.name ASC
```

## Connections to other communities
- 1 edge to [[_COMMUNITY_Any]]

## Top bridge nodes
- [[get_calendar_events()]] - degree 5, connects to 1 community