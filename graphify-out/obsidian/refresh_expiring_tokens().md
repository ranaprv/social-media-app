---
source_file: "backend/app/services/token_refresh.py"
type: "code"
community: "Asyncsession"
location: "L220"
tags:
  - graphify/code
  - graphify/INFERRED
  - community/Asyncsession
---

# refresh_expiring_tokens()

## Connections
- [[PlatformConnection]] - `indirect_call` [INFERRED]
- [[Refresh tokens that are about to expire (within 10 minutes).]] - `rationale_for` [EXTRACTED]
- [[get_valid_token()]] - `calls` [EXTRACTED]
- [[refresh_platform_tokens()]] - `calls` [INFERRED]
- [[timedelta]] - `calls` [INFERRED]
- [[token_refresh.py]] - `contains` [EXTRACTED]

#graphify/code #graphify/INFERRED #community/Asyncsession