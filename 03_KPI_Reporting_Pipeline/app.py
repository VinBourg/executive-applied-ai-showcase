import json
from pathlib import Path

from metrics import CATEGORY_PATH, DAILY_PATH, SUMMARY_PATH, compute_metrics, load_rows, write_dashboard, write_outputs

BASE_DIR = Path(__file__).parent
EXEC_SUMMARY_PATH = BASE_DIR / "executive_summary.md"


def build_executive_summary(summary, category_rows, daily_rows):
    top_category = next(row for row in category_rows if row["category"] == summary["top_category_by_volume"])
    worst_day = max(daily_rows, key=lambda row: row["reopened_count"])
    lines = [
        "# Executive Summary - KPI Reporting Pipeline",
        "",
        "## Key Signals",
        f"- Ticket count: `{summary['ticket_count']}`",
        f"- Average resolution hours: `{summary['average_resolution_hours']}`",
        f"- SLA compliance rate: `{summary['sla_compliance_rate']:.0%}`",
        f"- Reopened rate: `{summary['reopened_rate']:.0%}`",
        "",
        "## Interpretation",
        f"- The highest-volume category is `{summary['top_category_by_volume']}` with `{top_category['ticket_count']}` tickets.",
        f"- The heaviest reopened-ticket day is `{worst_day['date']}` with `{worst_day['reopened_count']}` reopened cases.",
        "",
        "## Management Follow-Up",
        "- Review the dominant category first to understand whether the issue is operational or structural.",
        "- Compare reopened-ticket spikes with SLA pressure and staffing coverage.",
        "- Use the dashboard as the operational view and the summary as the management note.",
    ]
    return "\n".join(lines) + "\n"


def main():
    rows = load_rows()
    summary, category_rows, daily_rows = compute_metrics(rows)
    write_outputs(summary, category_rows, daily_rows)
    write_dashboard(summary, category_rows, daily_rows)
    EXEC_SUMMARY_PATH.write_text(build_executive_summary(summary, category_rows, daily_rows))

    print("KPI pipeline completed")
    print(json.dumps(summary, indent=2))
    print(f"Top category detail: {summary['top_category_by_volume']}")
    print(f"Generated: {SUMMARY_PATH.name}, {CATEGORY_PATH.name}, {DAILY_PATH.name}, dashboard.html, {EXEC_SUMMARY_PATH.name}")


if __name__ == "__main__":
    main()
