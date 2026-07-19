---
source_file: "backend/app/api/approvals.py"
type: "code"
community: "Approvals"
location: "L147"
tags:
  - graphify/code
  - graphify/EXTRACTED
  - community/Approvals
---

# approve_slot()

## Connections
- [[Approve a pending ContentSlot and create Post + PostPlatform rows.]] - `rationale_for` [EXTRACTED]
- [[ApproveRequest]] - `references` [EXTRACTED]
- [[AsyncSession_7]] - `references` [EXTRACTED]
- [[ContentSlot]] - `indirect_call` [INFERRED]
- [[Post]] - `calls` [INFERRED]
- [[PostPlatform]] - `calls` [INFERRED]
- [[User_7]] - `references` [EXTRACTED]
- [[approvals.py]] - `contains` [EXTRACTED]
- [[ensure_system_workspace()]] - `calls` [INFERRED]

#graphify/code #graphify/EXTRACTED #community/Approvals