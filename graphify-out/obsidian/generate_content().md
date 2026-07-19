---
source_file: "backend/app/api/content_generation.py"
type: "code"
community: "Content Generation"
location: "L89"
tags:
  - graphify/code
  - graphify/INFERRED
  - community/Content_Generation
---

# generate_content()

## Connections
- [[AsyncSession_16]] - `references` [EXTRACTED]
- [[ContentPlan]] - `calls` [INFERRED]
- [[ContentSlot]] - `calls` [INFERRED]
- [[ContentStrategy_1]] - `indirect_call` [INFERRED]
- [[GenerateRequest]] - `references` [EXTRACTED]
- [[User_15]] - `references` [EXTRACTED]
- [[content_generation.py]] - `contains` [EXTRACTED]
- [[ensure_system_workspace()]] - `calls` [INFERRED]
- [[get_best_times_for_workspace()]] - `calls` [INFERRED]
- [[timedelta]] - `calls` [INFERRED]

#graphify/code #graphify/INFERRED #community/Content_Generation