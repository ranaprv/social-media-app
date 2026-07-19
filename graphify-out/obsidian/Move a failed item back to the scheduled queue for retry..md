---
source_file: "backend/app/services/dead_letter_queue.py"
type: "rationale"
community: "Dead Letter Queue"
location: "L91"
tags:
  - graphify/rationale
  - graphify/EXTRACTED
  - community/Dead_Letter_Queue
---

# Move a failed item back to the scheduled queue for retry.

## Connections
- [[retry_from_dead_letter()]] - `rationale_for` [EXTRACTED]

#graphify/rationale #graphify/EXTRACTED #community/Dead_Letter_Queue