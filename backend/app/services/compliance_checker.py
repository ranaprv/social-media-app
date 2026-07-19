"""Platform compliance checker — validate content against platform ToS.

Checks content for potential violations, banned phrases, and
platform-specific compliance requirements.
"""
import logging
import re
from typing import Any

logger = logging.getLogger(__name__)

# Platform-specific compliance rules
COMPLIANCE_RULES = {
    "linkedin": {
        "max_caption_length": 3000,
        "max_hashtags": 5,
        "banned_patterns": [
            r"(?i)follow\s+for\s+follow",
            r"(?i)like\s+for\s+like",
            r"(?i)engagement\s+pod",
        ],
        "disclosure_required": ["ad", "sponsored", "partner", "affiliate"],
        "notes": "LinkedIn requires disclosure for sponsored content. No engagement pods.",
    },
    "x": {
        "max_caption_length": 280,
        "max_hashtags": 3,
        "banned_patterns": [
            r"(?i)follow\s+for\s+follow",
            r"(?i)buy\s+followers",
            r"(?i)spam",
        ],
        "disclosure_required": ["ad", "sponsored", "#ad", "#sponsored"],
        "notes": "X requires #ad or #sponsored for paid partnerships.",
    },
    "instagram": {
        "max_caption_length": 2200,
        "max_hashtags": 30,
        "banned_patterns": [
            r"(?i)follow\s+for\s+follow",
            r"(?i)like\s+for\s+like",
            r"(?i)engagement\s+pod",
            r"(?i)buy\s+followers",
        ],
        "disclosure_required": ["paid partnership", "ad", "sponsored"],
        "notes": "Instagram requires 'Paid partnership' label for brand deals. No engagement pods.",
    },
    "facebook": {
        "max_caption_length": 63206,
        "max_hashtags": 5,
        "banned_patterns": [
            r"(?i)engagement\s+bait",
            r"(?i)share\s+if\s+you",
            r"(?i)like\s+if\s+you",
            r"(?i)tag\s+someone\s+who",
        ],
        "disclosure_required": ["ad", "sponsored"],
        "notes": "Facebook penalizes engagement bait. No 'like if you agree' type posts.",
    },
    "youtube": {
        "max_title_length": 100,
        "max_description_length": 5000,
        "max_hashtags": 15,
        "banned_patterns": [
            r"(?i)clickbait",
            r"(?i)misleading\s+thumbnail",
        ],
        "disclosure_required": ["paid promotion", "ad", "sponsored"],
        "notes": "YouTube requires 'Includes paid promotion' checkbox for sponsored videos.",
    },
}


def check_compliance(
    content: str,
    platform: str,
    title: str | None = None,
    has_paid_partnership: bool = False,
) -> dict[str, Any]:
    """Check content for platform compliance issues."""
    rules = COMPLIANCE_RULES.get(platform, {})
    issues: list[dict[str, str]] = []
    warnings: list[dict[str, str]] = []

    # Length check
    max_len = rules.get("max_caption_length", 9999)
    if len(content) > max_len:
        issues.append({
            "type": "length",
            "severity": "error",
            "message": f"Content exceeds {platform} limit ({len(content)}/{max_len} chars)",
        })

    # Title length check (YouTube)
    if title and platform == "youtube":
        max_title = rules.get("max_title_length", 100)
        if len(title) > max_title:
            issues.append({
                "type": "title_length",
                "severity": "error",
                "message": f"Title exceeds YouTube limit ({len(title)}/{max_title} chars)",
            })

    # Hashtag check
    hashtags = re.findall(r"#\w+", content)
    max_hashtags = rules.get("max_hashtags", 10)
    if len(hashtags) > max_hashtags:
        warnings.append({
            "type": "hashtag_count",
            "severity": "warning",
            "message": f"Too many hashtags ({len(hashtags)}/{max_hashtags}). May reduce reach.",
        })

    # Banned pattern check
    for pattern in rules.get("banned_patterns", []):
        if re.search(pattern, content):
            issues.append({
                "type": "banned_content",
                "severity": "error",
                "message": f"Content contains banned pattern: {pattern}",
            })

    # Disclosure check
    if has_paid_partnership:
        disclosure_terms = rules.get("disclosure_required", [])
        has_disclosure = any(term.lower() in content.lower() for term in disclosure_terms)
        if not has_disclosure:
            warnings.append({
                "type": "disclosure_missing",
                "severity": "warning",
                "message": f"Paid partnership detected but no disclosure ({', '.join(disclosure_terms[:3])})",
            })

    # Platform-specific warnings
    if platform == "facebook":
        engagement_bait_patterns = [r"(?i)like\s+if", r"(?i)share\s+if", r"(?i)tag\s+a\s+friend"]
        for pattern in engagement_bait_patterns:
            if re.search(pattern, content):
                warnings.append({
                    "type": "engagement_bait",
                    "severity": "warning",
                    "message": "Engagement bait detected. Facebook penalizes this.",
                })

    if platform == "instagram" and len(content) > 125:
        warnings.append({
            "type": "caption_length",
            "severity": "info",
            "message": "Caption exceeds 125 chars. Key message may be hidden behind 'more'.",
        })

    # Score
    error_count = len(issues)
    warning_count = len(warnings)
    score = max(0, 100 - (error_count * 25) - (warning_count * 10))

    return {
        "platform": platform,
        "score": score,
        "status": "pass" if error_count == 0 else "fail",
        "issues": issues,
        "warnings": warnings,
        "rules_notes": rules.get("notes", ""),
    }


def check_all_platforms(
    content: str,
    platforms: list[str],
    title: str | None = None,
    has_paid_partnership: bool = False,
) -> dict[str, Any]:
    """Check content compliance across multiple platforms."""
    results = {}
    for platform in platforms:
        results[platform] = check_compliance(content, platform, title, has_paid_partnership)

    total_errors = sum(len(r["issues"]) for r in results.values())
    total_warnings = sum(len(r["warnings"]) for r in results.values())

    return {
        "by_platform": results,
        "total_errors": total_errors,
        "total_warnings": total_warnings,
        "all_pass": total_errors == 0,
    }
