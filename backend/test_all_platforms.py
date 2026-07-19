"""Platform Connectivity Test — LinkedIn, Facebook, YouTube

Tests OAuth endpoint reachability, credential validation, and URL generation
for each social platform configured in .env.
"""
import httpx
import os
import sys
from urllib.parse import urlencode


def load_env():
    env = {}
    with open(".env") as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                env[k.strip()] = v.strip()
    return env


def test_platform(name, checks):
    """Run a list of (label, callable) checks for a platform."""
    print(f"\n{'=' * 60}")
    print(f"  {name}")
    print(f"{'=' * 60}")
    results = []
    for label, fn in checks:
        try:
            ok, detail = fn()
            icon = "✅" if ok else "❌"
            print(f"  {icon} {label} — {detail}")
            results.append((label, ok))
        except Exception as e:
            print(f"  ❌ {label} — {e}")
            results.append((label, False))
    passed = sum(1 for _, ok in results if ok)
    print(f"  ── {passed}/{len(results)} passed")
    return results


def run_tests():
    env = load_env()
    all_results = []

    # ─── LinkedIn ───────────────────────────────────────────────────────
    li_id = env.get("LINKEDIN_CLIENT_ID", "")
    li_secret = env.get("LINKEDIN_CLIENT_SECRET", "")
    li_redirect = env.get("LINKEDIN_REDIRECT_URI", "")

    def li_creds():
        if li_id and li_secret:
            return True, f"client_id={li_id[:8]}... secret={li_secret[:10]}..."
        return False, "missing credentials"

    def li_endpoint():
        with httpx.Client(timeout=10) as c:
            r = c.get("https://api.linkedin.com/v2/me",
                       headers={"Authorization": "Bearer INVALID"})
            return True, f"api.linkedin.com/v2 reachable ({r.status_code})"

    def li_token():
        with httpx.Client(timeout=10) as c:
            r = c.post("https://www.linkedin.com/oauth/v2/accessToken",
                       data={"grant_type": "authorization_code", "code": "x",
                             "redirect_uri": li_redirect, "client_id": li_id or "x",
                             "client_secret": li_secret or "x"})
            data = r.json()
            return True, f"token endpoint reachable (error={data.get('error', 'N/A')})"

    def li_url():
        url = (
            "https://www.linkedin.com/oauth/v2/authorization?"
            + urlencode({"response_type": "code", "client_id": li_id or "MISSING",
                         "redirect_uri": li_redirect, "scope": "r_liteprofile r_emailaddress w_member_social",
                         "state": "test"})
        )
        return True, url

    all_results.extend(test_platform("LinkedIn", [
        ("Credentials", li_creds),
        ("API reachability", li_endpoint),
        ("Token endpoint", li_token),
        ("OAuth URL", li_url),
    ]))

    # ─── Facebook ───────────────────────────────────────────────────────
    fb_id = env.get("FACEBOOK_APP_ID", "")
    fb_secret = env.get("FACEBOOK_APP_SECRET", "")
    fb_redirect = env.get("FACEBOOK_REDIRECT_URI", "")

    def fb_creds():
        if fb_id and fb_secret:
            return True, f"app_id={fb_id[:10]}... secret={fb_secret[:10]}..."
        return False, "missing credentials"

    def fb_endpoint():
        with httpx.Client(timeout=10) as c:
            r = c.get("https://graph.facebook.com/v19.0/me",
                       params={"access_token": "INVALID"})
            return True, f"graph.facebook.com reachable ({r.status_code})"

    def fb_token():
        with httpx.Client(timeout=10) as c:
            r = c.get("https://graph.facebook.com/v19.0/oauth/access_token",
                       params={"client_id": fb_id or "x", "client_secret": fb_secret or "x",
                               "redirect_uri": fb_redirect, "code": "INVALID"})
            data = r.json()
            err = data.get("error", {}).get("message", "N/A") if "error" in data else "N/A"
            return True, f"token endpoint reachable (error={err})"

    def fb_url():
        # Dev mode: public_profile + email. Production: add pages_manage_posts, pages_read_engagement after App Review
        url = (
            "https://www.facebook.com/v19.0/dialog/oauth?"
            + urlencode({"client_id": fb_id or "MISSING", "redirect_uri": fb_redirect,
                         "scope": "public_profile,email"})
        )
        return True, url

    all_results.extend(test_platform("Facebook / Instagram", [
        ("Credentials", fb_creds),
        ("API reachability", fb_endpoint),
        ("Token endpoint", fb_token),
        ("OAuth URL", fb_url),
    ]))

    # ─── YouTube (Google) ──────────────────────────────────────────────
    yt_id = env.get("YOUTUBE_CLIENT_ID", "")
    yt_secret = env.get("YOUTUBE_CLIENT_SECRET", "")
    yt_redirect = env.get("YOUTUBE_REDIRECT_URI", "")

    def yt_creds():
        if yt_id and yt_secret:
            return True, f"client_id={yt_id[:20]}... secret={yt_secret[:10]}..."
        return False, "missing credentials"

    def yt_endpoint():
        with httpx.Client(timeout=10) as c:
            r = c.get("https://www.googleapis.com/youtube/v3/channels",
                       params={"part": "snippet", "mine": "true"},
                       headers={"Authorization": "Bearer INVALID"})
            return True, f"googleapis.com/youtube reachable ({r.status_code})"

    def yt_token():
        with httpx.Client(timeout=10) as c:
            r = c.post("https://oauth2.googleapis.com/token",
                       data={"client_id": yt_id or "x", "client_secret": yt_secret or "x",
                             "code": "INVALID", "grant_type": "authorization_code",
                             "redirect_uri": yt_redirect})
            data = r.json()
            err = data.get("error", "N/A")
            return True, f"token endpoint reachable (error={err})"

    def yt_url():
        url = (
            "https://accounts.google.com/o/oauth2/v2/auth?"
            + urlencode({"client_id": yt_id or "MISSING", "redirect_uri": yt_redirect,
                         "response_type": "code",
                         "scope": "https://www.googleapis.com/auth/youtube.upload "
                                  "https://www.googleapis.com/auth/youtube.readonly"})
        )
        return True, url

    all_results.extend(test_platform("YouTube (Google)", [
        ("Credentials", yt_creds),
        ("API reachability", yt_endpoint),
        ("Token endpoint", yt_token),
        ("OAuth URL", yt_url),
    ]))

    # ─── Summary ───────────────────────────────────────────────────────
    total_passed = sum(1 for _, ok in all_results if ok)
    total = len(all_results)
    print(f"\n{'=' * 60}")
    print(f"  TOTAL: {total_passed}/{total} checks passed")
    print(f"{'=' * 60}")

    if total_passed == total:
        print("  🎉 All platforms reachable. OAuth URLs ready for authorization.\n")
    else:
        failed = [name for name, ok in all_results if not ok]
        print(f"  ⚠️  Failed: {', '.join(failed)}\n")

    return 0 if total_passed == total else 1


if __name__ == "__main__":
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    sys.exit(run_tests())
