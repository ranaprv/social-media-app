---
source_file: "backend/app/api/auth.py"
type: "code"
community: "Asyncsession"
location: "L83"
tags:
  - graphify/code
  - graphify/EXTRACTED
  - community/Asyncsession
---

# login()

## Connections
- [[AsyncSession_8]] - `references` [EXTRACTED]
- [[Request]] - `references` [EXTRACTED]
- [[User_32]] - `indirect_call` [INFERRED]
- [[UserLogin]] - `references` [EXTRACTED]
- [[_check_auth_rate_limit()]] - `calls` [EXTRACTED]
- [[auth.py]] - `contains` [EXTRACTED]
- [[create_access_token()]] - `calls` [INFERRED]
- [[timedelta]] - `calls` [INFERRED]
- [[verify_password()]] - `calls` [INFERRED]

#graphify/code #graphify/EXTRACTED #community/Asyncsession