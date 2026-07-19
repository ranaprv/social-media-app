---
source_file: "backend/app/api/auth.py"
type: "code"
community: "Asyncsession"
location: "L49"
tags:
  - graphify/code
  - graphify/EXTRACTED
  - community/Asyncsession
---

# register()

## Connections
- [[AsyncSession_8]] - `references` [EXTRACTED]
- [[Request]] - `references` [EXTRACTED]
- [[User_8]] - `calls` [EXTRACTED]
- [[User_32]] - `indirect_call` [INFERRED]
- [[UserCreate]] - `references` [EXTRACTED]
- [[UserResponse]] - `calls` [INFERRED]
- [[_check_auth_rate_limit()]] - `calls` [EXTRACTED]
- [[auth.py]] - `contains` [EXTRACTED]
- [[get_password_hash()]] - `calls` [INFERRED]

#graphify/code #graphify/EXTRACTED #community/Asyncsession