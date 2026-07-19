---
type: community
cohesion: 0.22
members: 9
---

# Test Security

**Cohesion:** 0.22 - loosely connected
**Members:** 9 nodes

## Members
- [[Tests for security endpoints.]] - rationale - backend/tests/test_security.py
- [[test_encryption_status()]] - code - backend/tests/test_security.py
- [[test_gdpr_status()]] - code - backend/tests/test_security.py
- [[test_get_audit_logs()]] - code - backend/tests/test_security.py
- [[test_get_roles()]] - code - backend/tests/test_security.py
- [[test_oauth_connections()]] - code - backend/tests/test_security.py
- [[test_rate_limit_status()]] - code - backend/tests/test_security.py
- [[test_rbac_check()]] - code - backend/tests/test_security.py
- [[test_security.py]] - code - backend/tests/test_security.py

## Live Query (requires Dataview plugin)

```dataview
TABLE source_file, type FROM #community/Test_Security
SORT file.name ASC
```
