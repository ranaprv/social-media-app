---
source_file: "backend/app/models/strategy.py"
type: "code"
community: "Content Generation"
location: "L35"
tags:
  - graphify/code
  - graphify/INFERRED
  - community/Content_Generation
---

# ContentPlan

## Connections
- [[Base]] - `uses` [INFERRED]
- [[BulkApprove]] - `uses` [INFERRED]
- [[BulkReject]] - `uses` [INFERRED]
- [[ContentSlot]] - `references` [EXTRACTED]
- [[ContentStrategy_1]] - `references` [EXTRACTED]
- [[GenerateRequest]] - `uses` [INFERRED]
- [[SlotApprove]] - `uses` [INFERRED]
- [[SlotReject]] - `uses` [INFERRED]
- [[SlotUpdate]] - `uses` [INFERRED]
- [[generate_content()]] - `calls` [INFERRED]
- [[get_adherence()]] - `indirect_call` [INFERRED]
- [[get_plan()]] - `indirect_call` [INFERRED]
- [[get_plan_progress()]] - `indirect_call` [INFERRED]
- [[list_plans()]] - `indirect_call` [INFERRED]
- [[strategy.py]] - `contains` [EXTRACTED]

#graphify/code #graphify/INFERRED #community/Content_Generation