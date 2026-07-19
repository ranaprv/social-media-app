---
source_file: "backend/app/services/dead_letter_queue.py"
type: "rationale"
community: "Dead Letter Queue"
location: "L271"
tags:
  - graphify/rationale
  - graphify/EXTRACTED
  - community/Dead_Letter_Queue
---

# Calculate what percentage of retried items eventually succeeded.

## Connections
- [[_calc_retry_success_rate()]] - `rationale_for` [EXTRACTED]

#graphify/rationale #graphify/EXTRACTED #community/Dead_Letter_Queue