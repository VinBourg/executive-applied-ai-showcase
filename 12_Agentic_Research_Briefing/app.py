import csv
import json
from pathlib import Path

BASE_DIR = Path(__file__).parent
PROFILE_PATH = BASE_DIR / "company_profile.json"
SIGNALS_PATH = BASE_DIR / "signals.json"
BRIEF_PATH = BASE_DIR / "research_brief.md"
MAP_PATH = BASE_DIR / "opportunity_map.csv"


def load_payloads():
    profile = json.loads(PROFILE_PATH.read_text())
    signals = json.loads(SIGNALS_PATH.read_text())
    return profile, signals


def build_opportunity_map(profile, signal_payload):
    signal_values = signal_payload["signals"]
    opportunities = [
        {
            "opportunity": "Support intelligence cockpit",
            "fit_score": 82 if signal_values["backlog_growth_pct"] >= 15 else 60,
            "why_now": "Backlog and SLA pressure justify fast operational visibility.",
        },
        {
            "opportunity": "Knowledge assistant for operations teams",
            "fit_score": 78 if signal_values["reopened_rate"] >= 0.25 else 62,
            "why_now": "Reopened issues suggest missing or weak knowledge reuse.",
        },
        {
            "opportunity": "Workflow automation for management reporting",
            "fit_score": 80 if signal_values["high_priority_ticket_growth_pct"] >= 20 else 64,
            "why_now": "Growing high-priority load makes reporting automation valuable.",
        },
    ]
    opportunities.sort(key=lambda item: item["fit_score"], reverse=True)
    return opportunities


def write_opportunity_map(opportunities):
    with MAP_PATH.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=["opportunity", "fit_score", "why_now"])
        writer.writeheader()
        writer.writerows(opportunities)


def build_brief(profile, signal_payload, opportunities):
    signal_values = signal_payload["signals"]
    lines = [
        "# Agentic Research Brief",
        "",
        "## Target Account",
        f"{profile['company']} ({profile['industry']}, {profile['country']})",
        "",
        "## Objective",
        profile["objective"],
        "",
        "## Context",
        f"- Review context: {signal_payload['context']}",
        f"- SLA compliance rate: {signal_values['sla_compliance_rate']}",
        f"- Reopened rate: {signal_values['reopened_rate']}",
        f"- Backlog growth pct: {signal_values['backlog_growth_pct']}",
        f"- High-priority ticket growth pct: {signal_values['high_priority_ticket_growth_pct']}",
        f"- Most affected team: {signal_values['most_affected_team']}",
        "",
        "## Agentic Workflow",
        "- Planner: define the decision-oriented research angle",
        "- Researcher: gather company and operational signals",
        "- Analyzer: prioritize AI and automation opportunity areas",
        "- Synthesizer: prepare an advisory note and next-step agenda",
        "",
        "## Ranked Opportunity Areas",
    ]
    for item in opportunities:
        lines.extend(
            [
                f"### {item['opportunity']}",
                f"- Fit score: `{item['fit_score']}`",
                f"- Why now: {item['why_now']}",
                "",
            ]
        )
    lines.extend(
        [
            "## Recommended Advisory Angle",
            "Focus first on operational use cases with measurable impact on backlog visibility, escalation quality and management reporting speed.",
            "",
            "## Suggested Meeting Agenda",
            "- Confirm the most painful operational bottlenecks.",
            "- Validate which reporting and support steps are still too manual.",
            "- Align on one short pilot with measurable success criteria.",
        ]
    )
    return "\n".join(lines) + "\n"


def main():
    profile, signal_payload = load_payloads()
    opportunities = build_opportunity_map(profile, signal_payload)
    write_opportunity_map(opportunities)
    BRIEF_PATH.write_text(build_brief(profile, signal_payload, opportunities))

    print("Agentic research briefing demo")
    print("=" * 31)
    print(f"Target account: {profile['company']}")
    for item in opportunities:
        print(f"- {item['opportunity']}: fit_score={item['fit_score']}")
    print(f"Generated: {BRIEF_PATH.name}, {MAP_PATH.name}")


if __name__ == "__main__":
    main()
