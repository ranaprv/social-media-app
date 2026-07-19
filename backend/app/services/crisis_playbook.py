"""Crisis Playbook Builder — pre-written response templates for common issues.

Provides crisis communication frameworks and response templates.
"""
import logging
from typing import Any

logger = logging.getLogger(__name__)

# Crisis scenarios and response frameworks
CRISIS_SCENARIOS = {
    "negative_review": {
        "name": "Negative Review / Complaint",
        "severity": "medium",
        "response_framework": "ACKNOWLEDGE → EMPATHIZE → RESOLVE → FOLLOW_UP",
        "templates": [
            {
                "name": "Immediate Acknowledgment",
                "template": "We're sorry to hear about your experience, {name}. This isn't the standard we hold ourselves to. We've escalated this to our team and will follow up within 24 hours.",
                "timing": "within 1 hour",
            },
            {
                "name": "Resolution Update",
                "template": "Hi {name}, we've looked into your issue and here's what we're doing: {resolution}. We appreciate your patience.",
                "timing": "within 24 hours",
            },
        ],
        "do": [
            "Respond within 1 hour",
            "Acknowledge the issue publicly",
            "Move to private channel for details",
            "Follow up when resolved",
        ],
        "dont": [
            "Delete the complaint",
            "Get defensive or argumentative",
            "Make promises you can't keep",
            "Ignore it and hope it goes away",
        ],
    },
    "pr_security_breach": {
        "name": "PR / Security Issue",
        "severity": "high",
        "response_framework": "ASSESS → INFORM → ACT → UPDATE",
        "templates": [
            {
                "name": "Initial Statement",
                "template": "We're aware of {issue} and are actively investigating. We'll provide an update within {timeframe}. User safety is our top priority.",
                "timing": "within 2 hours",
            },
            {
                "name": "Status Update",
                "template": "Update on {issue}: {status}. {next_steps}. We'll continue to keep you informed.",
                "timing": "every 4-6 hours during active incident",
            },
        ],
        "do": [
            "Respond within 2 hours",
            "Be transparent about what you know",
            "Provide regular updates",
            "Have a single spokesperson",
        ],
        "dont": [
            "Speculate or guess",
            "Blame others",
            "Go silent",
            "Post unrelated content during crisis",
        ],
    },
    "viral_backlash": {
        "name": "Viral Backlash / Controversy",
        "severity": "high",
        "response_framework": "LISTEN → UNDERSTAND → RESPOND → ACT",
        "templates": [
            {
                "name": "Acknowledgment",
                "template": "We've heard your concerns about {topic}. We take this seriously and are reviewing our approach. We'll share our response soon.",
                "timing": "within 4 hours",
            },
            {
                "name": "Action Statement",
                "template": "After listening to your feedback, we're taking these steps: {actions}. We appreciate you holding us accountable.",
                "timing": "within 24-48 hours",
            },
        ],
        "do": [
            "Monitor sentiment in real-time",
            "Pause all scheduled content",
            "Assemble crisis response team",
            "Prepare holding statements",
        ],
        "dont": [
            "Delete posts or comments",
            "Use corporate jargon",
            "Promise immediate fixes",
            "Engage with trolls",
        ],
    },
    "service_outage": {
        "name": "Service Outage / Technical Issue",
        "severity": "medium",
        "response_framework": "DETECT → INFORM → RESOLVE → DEBRIEF",
        "templates": [
            {
                "name": "Outage Notice",
                "template": "We're experiencing {issue}. Our team is actively working on a fix. We'll update you every 30 minutes. Status page: {url}",
                "timing": "within 30 minutes of detection",
            },
            {
                "name": "Resolution Notice",
                "template": "✅ {issue} has been resolved. {duration} of downtime. {root_cause_summary}. We're implementing {prevention} to prevent recurrence.",
                "timing": "immediately after resolution",
            },
        ],
        "do": [
            "Update status page immediately",
            "Post on all channels",
            "Provide ETA if possible",
            "Send post-mortem after resolution",
        ],
        "dont": [
            "Stay silent",
            "Minimize the impact",
            "Blame third parties publicly",
            "Resume normal posting immediately",
        ],
    },
    "employee_misconduct": {
        "name": "Employee Misconduct",
        "severity": "high",
        "response_framework": "INVESTIGATE → STATE → ACT → PREVENT",
        "templates": [
            {
                "name": "Initial Response",
                "template": "We're aware of {incident} involving a team member. We're investigating and take this very seriously. Our values are {values}.",
                "timing": "within 4 hours",
            },
        ],
        "do": [
            "Investigate internally first",
            "Issue a clear, concise statement",
            "Take appropriate action",
            "Review policies to prevent recurrence",
        ],
        "dont": [
            "Name the employee publicly",
            "Make premature judgments",
            "Ignore the community's concerns",
            "Post unrelated positive content",
        ],
    },
}


async def get_crisis_playbook(
    scenario: str | None = None,
) -> dict[str, Any]:
    """Get crisis communication playbook."""
    if scenario and scenario in CRISIS_SCENARIOS:
        return CRISIS_SCENARIOS[scenario]

    return {
        "scenarios": list(CRISIS_SCENARIOS.keys()),
        "playbooks": CRISIS_SCENARIOS,
    }


def get_crisis_checklist() -> list[dict[str, str]]:
    """Get general crisis response checklist."""
    return [
        {"step": "Pause all scheduled content", "priority": "immediate"},
        {"step": "Assemble crisis response team", "priority": "immediate"},
        {"step": "Assess the situation and severity", "priority": "immediate"},
        {"step": "Prepare holding statement", "priority": "within 1 hour"},
        {"step": "Monitor sentiment across platforms", "priority": "ongoing"},
        {"step": "Issue public acknowledgment", "priority": "within 2 hours"},
        {"step": "Provide regular status updates", "priority": "every 4-6 hours"},
        {"step": "Document everything for post-mortem", "priority": "during"},
        {"step": "Resume normal content after resolution", "priority": "after"},
        {"step": "Conduct post-mortem and update playbook", "priority": "within 48 hours"},
    ]
