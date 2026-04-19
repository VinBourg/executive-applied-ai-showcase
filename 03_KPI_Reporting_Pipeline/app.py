import json
from pathlib import Path

from metrics import (
    ALERT_PATH,
    CATEGORY_PATH,
    DAILY_PATH,
    PRIORITY_PATH,
    SUMMARY_PATH,
    compute_metrics,
    load_rows,
    write_dashboard,
    write_outputs,
)

BASE_DIR = Path(__file__).parent
EXEC_SUMMARY_PATH = BASE_DIR / "executive_summary.md"
ACTION_PLAN_PATH = BASE_DIR / "operations_action_plan.md"


def build_executive_summary(summary, category_rows, daily_rows, priority_rows, alerts):
    top_category = next(row for row in category_rows if row["category"] == summary["top_category_by_volume"])
    worst_day = max(daily_rows, key=lambda row: row["sla_breach_count"])
    weakest_priority = min(priority_rows, key=lambda row: row["sla_compliance_rate"])
    lines = [
        "# Executive Summary - KPI Reporting Pipeline",
        "",
        "## Key Signals",
        f"- Ticket count: `{summary['ticket_count']}`",
        f"- Average resolution hours: `{summary['average_resolution_hours']}`",
        f"- SLA compliance rate: `{summary['sla_compliance_rate']:.0%}`",
        f"- Reopened rate: `{summary['reopened_rate']:.0%}`",
        f"- Operations health score: `{summary['operations_health_score']}`",
        f"- Active alerts: `{summary['alert_count']}`",
        "",
        "## Interpretation",
        f"- The highest-volume category is `{summary['top_category_by_volume']}` with `{top_category['ticket_count']}` tickets and risk level `{top_category['risk_level']}`.",
        f"- The heaviest SLA-breach day is `{worst_day['date']}` with `{worst_day['sla_breach_count']}` breaches.",
        f"- The weakest priority band is `{weakest_priority['priority']}` with SLA compliance `{weakest_priority['sla_compliance_rate']:.0%}`.",
        "",
        "## Alert Snapshot",
    ]
    lines.extend(f"- {alert['severity']}: {alert['signal']}" for alert in alerts)
    return "\n".join(lines) + "\n"


def build_action_plan(category_rows, priority_rows, alerts):
    highest_risk_category = next((row for row in category_rows if row["risk_level"] == "high"), None)
    weakest_priority = min(priority_rows, key=lambda row: row["sla_compliance_rate"])
    lines = [
        "# Operations Action Plan - KPI Reporting Pipeline",
        "",
        "## Immediate Actions",
    ]
    if highest_risk_category:
        lines.append(
            f"- Launch a focused review on `{highest_risk_category['category']}` because it shows high operational risk."
        )
    lines.append(
        f"- Reinforce the `{weakest_priority['priority']}` priority workflow where SLA performance is weakest."
    )
    for alert in alerts[:3]:
        lines.append(f"- {alert['recommended_action']}")
    lines.extend(
        [
            "",
            "## Review Rhythm",
            "- Use the alert digest in the weekly operations review.",
            "- Track category and priority tables together rather than in isolation.",
            "- Re-check the health score after each staffing or process adjustment.",
        ]
    )
    return "\n".join(lines) + "\n"


def main():
    rows = load_rows()
    summary, category_rows, daily_rows, priority_rows, alerts = compute_metrics(rows)
    write_outputs(summary, category_rows, daily_rows, priority_rows, alerts)
    write_dashboard(summary, category_rows, daily_rows, priority_rows, alerts)
    EXEC_SUMMARY_PATH.write_text(build_executive_summary(summary, category_rows, daily_rows, priority_rows, alerts))
    ACTION_PLAN_PATH.write_text(build_action_plan(category_rows, priority_rows, alerts))

    print("KPI pipeline completed")
    print(json.dumps(summary, indent=2))
    print(f"Top category detail: {summary['top_category_by_volume']}")
    print(
        f"Generated: {SUMMARY_PATH.name}, {CATEGORY_PATH.name}, {DAILY_PATH.name}, "
        f"{PRIORITY_PATH.name}, {ALERT_PATH.name}, dashboard.html, {EXEC_SUMMARY_PATH.name}, {ACTION_PLAN_PATH.name}"
    )


if __name__ == "__main__":
    main()
