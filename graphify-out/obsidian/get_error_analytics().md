---
source_file: "backend/app/services/dead_letter_queue.py"
type: "code"
community: "Dead Letter Queue"
location: "L163"
tags:
  - graphify/code
  - graphify/EXTRACTED
  - community/Dead_Letter_Queue
---

# get_error_analytics()

## Connections
- [[Any_61]] - `references` [EXTRACTED]
- [[AsyncSession_71]] - `references` [EXTRACTED]
- [[Detailed error analytics for the dead-letter queue.]] - `rationale_for` [EXTRACTED]
- [[PostPlatform]] - `indirect_call` [INFERRED]
- [[_calc_retry_success_rate()]] - `calls` [EXTRACTED]
- [[_categorize_error()]] - `calls` [EXTRACTED]
- [[dead_letter_queue.py]] - `contains` [EXTRACTED]
- [[timedelta]] - `calls` [INFERRED]

#graphify/code #graphify/EXTRACTED #community/Dead_Letter_Queue