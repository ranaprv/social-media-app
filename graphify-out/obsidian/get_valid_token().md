---
source_file: "backend/app/services/token_refresh.py"
type: "code"
community: "Asyncsession"
location: "L160"
tags:
  - graphify/code
  - graphify/EXTRACTED
  - community/Asyncsession
---

# get_valid_token()

## Connections
- [[AsyncSession_89]] - `references` [EXTRACTED]
- [[Get a valid access token, refreshing if necessary.]] - `rationale_for` [EXTRACTED]
- [[PlatformConnection_2]] - `references` [EXTRACTED]
- [[connection_health_check()]] - `calls` [INFERRED]
- [[get_fresh_token()]] - `calls` [EXTRACTED]
- [[refresh_all_tokens()]] - `calls` [EXTRACTED]
- [[refresh_expiring_tokens()]] - `calls` [EXTRACTED]
- [[refresh_facebook_token()]] - `indirect_call` [INFERRED]
- [[refresh_linkedin_token()]] - `indirect_call` [INFERRED]
- [[refresh_youtube_token()]] - `indirect_call` [INFERRED]
- [[token_refresh.py]] - `contains` [EXTRACTED]

#graphify/code #graphify/EXTRACTED #community/Asyncsession