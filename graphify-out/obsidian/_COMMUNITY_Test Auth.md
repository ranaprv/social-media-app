---
type: community
cohesion: 0.22
members: 9
---

# Test Auth

**Cohesion:** 0.22 - loosely connected
**Members:** 9 nodes

## Members
- [[Tests for auth endpoints.]] - rationale - backend/tests/test_auth.py
- [[test_auth.py]] - code - backend/tests/test_auth.py
- [[test_get_me()]] - code - backend/tests/test_auth.py
- [[test_get_me_no_token()]] - code - backend/tests/test_auth.py
- [[test_login_nonexistent_user()]] - code - backend/tests/test_auth.py
- [[test_login_success()]] - code - backend/tests/test_auth.py
- [[test_login_wrong_password()]] - code - backend/tests/test_auth.py
- [[test_register_duplicate_email()]] - code - backend/tests/test_auth.py
- [[test_register_success()]] - code - backend/tests/test_auth.py

## Live Query (requires Dataview plugin)

```dataview
TABLE source_file, type FROM #community/Test_Auth
SORT file.name ASC
```
