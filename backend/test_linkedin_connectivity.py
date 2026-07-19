"""LinkedIn Platform Connectivity Test

Tests:
1. OAuth URL generation with valid client_id
2. LinkedIn API v2 endpoint reachability
3. OAuth token exchange endpoint response
4. .env credential validation
"""
import httpx
import os
import sys
from urllib.parse import urlencode

# Load .env manually
def load_env():
    env = {}
    with open(".env") as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                env[k.strip()] = v.strip()
    return env

def run_tests():
    env = load_env()
    client_id = env.get("LINKEDIN_CLIENT_ID", "")
    client_secret = env.get("LINKEDIN_CLIENT_SECRET", "")
    
    results = []
    
    # ═══════════════════════════════════════════════════════════════════
    # TEST 1: Validate .env credentials
    # ═══════════════════════════════════════════════════════════════════
    print("=" * 60)
    print("TEST 1: LinkedIn .env Credential Validation")
    print("=" * 60)
    
    if client_id:
        print(f"  ✅ LINKEDIN_CLIENT_ID loaded: {client_id[:8]}...")
    else:
        print("  ❌ LINKEDIN_CLIENT_ID is empty")
        results.append(("env_client_id", False))
    
    if client_secret:
        print(f"  ✅ LINKEDIN_CLIENT_SECRET loaded: {client_secret[:8]}...")
    else:
        print("  ❌ LINKEDIN_CLIENT_SECRET is empty")
        results.append(("env_client_secret", False))
    
    results.append(("env_credentials", bool(client_id and client_secret)))
    
    # ═══════════════════════════════════════════════════════════════════
    # TEST 2: Generate LinkedIn OAuth 2.0 Authorization URL
    # ═══════════════════════════════════════════════════════════════════
    print("\n" + "=" * 60)
    print("TEST 2: LinkedIn OAuth URL Generation")
    print("=" * 60)
    
    redirect_uri = "http://localhost:8000/api/connections/linkedin/callback"
    scopes = ["r_liteprofile", "r_emailaddress", "w_member_social"]
    state = "test_connectivity_state"
    
    oauth_params = {
        "response_type": "code",
        "client_id": client_id or "MISSING_CLIENT_ID",
        "redirect_uri": redirect_uri,
        "scope": " ".join(scopes),
        "state": state,
    }
    
    oauth_url = f"https://www.linkedin.com/oauth/v2/authorization?{urlencode(oauth_params)}"
    print(f"  ✅ OAuth URL generated:")
    print(f"  📎 {oauth_url}")
    print(f"\n  Scopes requested: {', '.join(scopes)}")
    print(f"  Redirect URI: {redirect_uri}")
    results.append(("oauth_url_generation", True))
    
    # ═══════════════════════════════════════════════════════════════════
    # TEST 3: LinkedIn API v2 Endpoint Reachability
    # ═══════════════════════════════════════════════════════════════════
    print("\n" + "=" * 60)
    print("TEST 3: LinkedIn API v2 Reachability")
    print("=" * 60)
    
    try:
        with httpx.Client(timeout=10) as client:
            # Test main API endpoint (should return 401 without auth)
            r = client.get(
                "https://api.linkedin.com/v2/me",
                headers={"Authorization": "Bearer INVALID_TOKEN"},
            )
            if r.status_code == 401:
                print(f"  ✅ API v2 reachable — got 401 (expected without valid token)")
                print(f"     Response: {r.text[:200]}")
                results.append(("api_reachable", True))
            elif r.status_code == 403:
                print(f"  ✅ API v2 reachable — got 403 (token invalid, but endpoint live)")
                results.append(("api_reachable", True))
            else:
                print(f"  ⚠️  API v2 responded with {r.status_code}")
                print(f"     Response: {r.text[:200]}")
                results.append(("api_reachable", True))
    except httpx.ConnectError as e:
        print(f"  ❌ Cannot reach api.linkedin.com — {e}")
        results.append(("api_reachable", False))
    except httpx.TimeoutException:
        print(f"  ❌ Timeout connecting to api.linkedin.com")
        results.append(("api_reachable", False))
    except Exception as e:
        print(f"  ❌ Error: {e}")
        results.append(("api_reachable", False))
    
    # ═══════════════════════════════════════════════════════════════════
    # TEST 4: LinkedIn OAuth Token Exchange Endpoint
    # ═══════════════════════════════════════════════════════════════════
    print("\n" + "=" * 60)
    print("TEST 4: LinkedIn OAuth Token Endpoint")
    print("=" * 60)
    
    try:
        with httpx.Client(timeout=10) as client:
            r = client.post(
                "https://www.linkedin.com/oauth/v2/accessToken",
                data={
                    "grant_type": "authorization_code",
                    "code": "INVALID_AUTH_CODE",
                    "redirect_uri": redirect_uri,
                    "client_id": client_id or "invalid",
                    "client_secret": client_secret or "invalid",
                },
            )
            data = r.json()
            if "error" in data:
                print(f"  ✅ Token endpoint reachable — returned error (expected)")
                print(f"     Error: {data.get('error', 'unknown')}")
                print(f"     Description: {data.get('error_description', 'N/A')}")
                results.append(("token_endpoint", True))
            elif r.status_code == 400:
                print(f"  ✅ Token endpoint reachable — 400 Bad Request (expected)")
                results.append(("token_endpoint", True))
            elif r.status_code == 200:
                print(f"  ⚠️  Token endpoint returned 200 with test code? Unexpected.")
                results.append(("token_endpoint", True))
            else:
                print(f"  ⚠️  Token endpoint: {r.status_code}")
                print(f"     Body: {r.text[:200]}")
                results.append(("token_endpoint", True))
    except httpx.ConnectError as e:
        print(f"  ❌ Cannot reach token endpoint — {e}")
        results.append(("token_endpoint", False))
    except httpx.TimeoutException:
        print(f"  ❌ Timeout on token endpoint")
        results.append(("token_endpoint", False))
    except Exception as e:
        print(f"  ❌ Error: {e}")
        results.append(("token_endpoint", False))
    
    # ═══════════════════════════════════════════════════════════════════
    # TEST 5: LinkedIn OpenID Connect Endpoint (v2/profile)
    # ═══════════════════════════════════════════════════════════════════
    print("\n" + "=" * 60)
    print("TEST 5: LinkedIn OpenID Connect / Subs Endpoint")
    print("=" * 60)
    
    try:
        with httpx.Client(timeout=10) as client:
            r = client.get(
                "https://api.linkedin.com/v2/userinfo",
                headers={"Authorization": "Bearer INVALID_TOKEN"},
            )
            if r.status_code in (401, 403):
                print(f"  ✅ /v2/userinfo reachable — {r.status_code}")
                results.append(("userinfo_endpoint", True))
            else:
                print(f"  ⚠️  /v2/userinfo responded {r.status_code}")
                results.append(("userinfo_endpoint", True))
    except Exception as e:
        print(f"  ❌ /v2/userinfo error: {e}")
        results.append(("userinfo_endpoint", False))
    
    # ═══════════════════════════════════════════════════════════════════
    # SUMMARY
    # ═══════════════════════════════════════════════════════════════════
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    
    passed = sum(1 for _, ok in results if ok)
    total = len(results)
    
    for name, ok in results:
        icon = "✅" if ok else "❌"
        print(f"  {icon} {name}")
    
    print(f"\n  Result: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n  🎉 LinkedIn platform connectivity: ALL GOOD")
        print(f"  📎 OAuth URL ready for user authorization:")
        print(f"     {oauth_url}")
    else:
        print("\n  ⚠️  Some tests failed — check above for details")
    
    return 0 if passed == total else 1


if __name__ == "__main__":
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    sys.exit(run_tests())
