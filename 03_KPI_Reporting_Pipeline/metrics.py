import csv
import json
from collections import defaultdict
from datetime import datetime
from pathlib import Path

BASE_DIR = Path(__file__).parent
INPUT_PATH = BASE_DIR / "tickets.csv"
SUMMARY_PATH = BASE_DIR / "kpi_summary.json"
CATEGORY_PATH = BASE_DIR / "kpi_by_category.csv"
DAILY_PATH = BASE_DIR / "kpi_by_day.csv"
PRIORITY_PATH = BASE_DIR / "kpi_by_priority.csv"
ALERT_PATH = BASE_DIR / "alert_digest.csv"
DASHBOARD_PATH = BASE_DIR / "dashboard.html"


def parse_datetime(value):
    return datetime.fromisoformat(value)


def resolution_hours(row):
    created = parse_datetime(row["created_at"])
    resolved = parse_datetime(row["resolved_at"])
    return round((resolved - created).total_seconds() / 3600, 2)


def load_rows():
    rows = []
    with INPUT_PATH.open() as handle:
        for row in csv.DictReader(handle):
            duration = resolution_hours(row)
            rows.append(
                {
                    **row,
                    "reopened": int(row["reopened"]),
                    "sla_hours": float(row["sla_hours"]),
                    "resolution_hours": duration,
                    "sla_met": duration <= float(row["sla_hours"]),
                }
            )
    return rows


def risk_level(sla_compliance_rate, reopened_rate):
    if sla_compliance_rate < 0.7 or reopened_rate > 0.3:
        return "high"
    if sla_compliance_rate < 0.85 or reopened_rate > 0.2:
        return "medium"
    return "low"


def compute_operations_health(summary):
    score = 100
    score -= (1 - summary["sla_compliance_rate"]) * 45
    score -= summary["reopened_rate"] * 35
    score -= max(summary["average_resolution_hours"] - 4, 0) * 3
    return round(max(score, 0), 1)


def summarize_by_category(rows):
    grouped = defaultdict(list)
    for row in rows:
        grouped[row["category"]].append(row)

    category_rows = []
    for category, items in sorted(grouped.items()):
        average_resolution = sum(item["resolution_hours"] for item in items) / len(items)
        reopened_rate = sum(item["reopened"] for item in items) / len(items)
        sla_compliance_rate = sum(item["sla_met"] for item in items) / len(items)
        category_rows.append(
            {
                "category": category,
                "ticket_count": len(items),
                "average_resolution_hours": round(average_resolution, 2),
                "sla_compliance_rate": round(sla_compliance_rate, 4),
                "reopened_rate": round(reopened_rate, 4),
                "risk_level": risk_level(sla_compliance_rate, reopened_rate),
            }
        )
    return category_rows


def summarize_by_day(rows):
    grouped = defaultdict(list)
    for row in rows:
        grouped[row["created_at"][:10]].append(row)

    daily_rows = []
    for day, items in sorted(grouped.items()):
        average_resolution = sum(item["resolution_hours"] for item in items) / len(items)
        reopened_count = sum(item["reopened"] for item in items)
        sla_breach_count = sum(not item["sla_met"] for item in items)
        daily_rows.append(
            {
                "date": day,
                "ticket_count": len(items),
                "average_resolution_hours": round(average_resolution, 2),
                "reopened_count": reopened_count,
                "sla_breach_count": sla_breach_count,
            }
        )
    return daily_rows


def summarize_by_priority(rows):
    grouped = defaultdict(list)
    for row in rows:
        grouped[row["priority"]].append(row)

    priority_rows = []
    for priority, items in sorted(grouped.items()):
        average_resolution = sum(item["resolution_hours"] for item in items) / len(items)
        sla_compliance_rate = sum(item["sla_met"] for item in items) / len(items)
        reopened_rate = sum(item["reopened"] for item in items) / len(items)
        priority_rows.append(
            {
                "priority": priority,
                "ticket_count": len(items),
                "average_resolution_hours": round(average_resolution, 2),
                "sla_compliance_rate": round(sla_compliance_rate, 4),
                "reopened_rate": round(reopened_rate, 4),
            }
        )
    return priority_rows


def build_alerts(summary, category_rows, daily_rows, priority_rows):
    alerts = []
    if summary["sla_compliance_rate"] < 0.85:
        alerts.append(
            {
                "severity": "high",
                "owner": "support manager",
                "signal": "Overall SLA compliance is below target.",
                "recommended_action": "Review breached tickets and reinforce the most affected queue.",
            }
        )
    if summary["reopened_rate"] > 0.25:
        alerts.append(
            {
                "severity": "high",
                "owner": "quality lead",
                "signal": "Reopened ticket rate is elevated.",
                "recommended_action": "Audit recurring root causes and improve fix quality on repeated issues.",
            }
        )

    for row in category_rows:
        if row["risk_level"] == "high":
            alerts.append(
                {
                    "severity": "medium",
                    "owner": "category lead",
                    "signal": f"{row['category']} category shows high operational risk.",
                    "recommended_action": "Review SLA and reopened drivers for this category first.",
                }
            )

    if daily_rows:
        worst_day = max(daily_rows, key=lambda row: row["sla_breach_count"])
        if worst_day["sla_breach_count"] > 0:
            alerts.append(
                {
                    "severity": "medium",
                    "owner": "operations lead",
                    "signal": f"{worst_day['date']} had the highest number of SLA breaches.",
                    "recommended_action": "Check staffing, escalation load and ticket mix for that day.",
                }
            )

    if priority_rows:
        weakest_priority = min(priority_rows, key=lambda row: row["sla_compliance_rate"])
        if weakest_priority["sla_compliance_rate"] < 0.8:
            alerts.append(
                {
                    "severity": "medium",
                    "owner": "priority queue owner",
                    "signal": f"{weakest_priority['priority']} priority tickets underperform on SLA.",
                    "recommended_action": "Review staffing and escalation path for this priority band.",
                }
            )
    return alerts


def compute_metrics(rows):
    total = len(rows)
    reopened = sum(row["reopened"] for row in rows)
    durations = [row["resolution_hours"] for row in rows]
    sla_met = sum(row["sla_met"] for row in rows)

    category_rows = summarize_by_category(rows)
    daily_rows = summarize_by_day(rows)
    priority_rows = summarize_by_priority(rows)

    summary = {
        "ticket_count": total,
        "average_resolution_hours": round(sum(durations) / total, 2),
        "sla_compliance_rate": round(sla_met / total, 4),
        "reopened_rate": round(reopened / total, 4),
        "top_category_by_volume": max(category_rows, key=lambda row: row["ticket_count"])["category"],
    }
    summary["operations_health_score"] = compute_operations_health(summary)
    alerts = build_alerts(summary, category_rows, daily_rows, priority_rows)
    summary["alert_count"] = len(alerts)

    return summary, category_rows, daily_rows, priority_rows, alerts


def write_csv(path, rows, fieldnames):
    with path.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def write_outputs(summary, category_rows, daily_rows, priority_rows, alerts):
    SUMMARY_PATH.write_text(json.dumps(summary, indent=2))
    write_csv(CATEGORY_PATH, category_rows, ["category", "ticket_count", "average_resolution_hours", "sla_compliance_rate", "reopened_rate", "risk_level"])
    write_csv(DAILY_PATH, daily_rows, ["date", "ticket_count", "average_resolution_hours", "reopened_count", "sla_breach_count"])
    write_csv(PRIORITY_PATH, priority_rows, ["priority", "ticket_count", "average_resolution_hours", "sla_compliance_rate", "reopened_rate"])
    write_csv(ALERT_PATH, alerts, ["severity", "owner", "signal", "recommended_action"])


def build_dashboard_html(summary, category_rows, daily_rows, priority_rows, alerts):
    category_items = "".join(
        f"<tr><td>{row['category']}</td><td>{row['ticket_count']}</td><td>{row['average_resolution_hours']}</td><td>{row['sla_compliance_rate']:.0%}</td><td>{row['risk_level']}</td></tr>"
        for row in category_rows
    )
    daily_items = "".join(
        f"<tr><td>{row['date']}</td><td>{row['ticket_count']}</td><td>{row['average_resolution_hours']}</td><td>{row['reopened_count']}</td><td>{row['sla_breach_count']}</td></tr>"
        for row in daily_rows
    )
    priority_items = "".join(
        f"<tr><td>{row['priority']}</td><td>{row['ticket_count']}</td><td>{row['average_resolution_hours']}</td><td>{row['sla_compliance_rate']:.0%}</td><td>{row['reopened_rate']:.0%}</td></tr>"
        for row in priority_rows
    )
    alert_items = "".join(
        f"<tr><td>{row['severity']}</td><td>{row['owner']}</td><td>{row['signal']}</td><td>{row['recommended_action']}</td></tr>"
        for row in alerts
    )
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>KPI Reporting Dashboard</title>
  <style>
    :root {{
      --ink: #12324A;
      --muted: #5c6b76;
      --bg: #f4f1ea;
      --card: #ffffff;
      --line: #d9d2c3;
      --accent: #c46b2d;
    }}
    body {{
      font-family: Georgia, "Times New Roman", serif;
      background: linear-gradient(180deg, #f7f4ee 0%, #efe7d8 100%);
      color: var(--ink);
      margin: 0;
      padding: 32px;
    }}
    .shell {{ max-width: 1080px; margin: 0 auto; }}
    .hero {{
      background: var(--card);
      border: 1px solid var(--line);
      padding: 28px;
      box-shadow: 0 12px 30px rgba(18, 50, 74, 0.08);
    }}
    h1, h2 {{ margin: 0 0 12px; }}
    p {{ color: var(--muted); }}
    .grid {{
      display: grid;
      grid-template-columns: repeat(5, 1fr);
      gap: 14px;
      margin: 20px 0 28px;
    }}
    .card {{
      background: var(--card);
      border: 1px solid var(--line);
      padding: 16px;
    }}
    .metric {{ font-size: 28px; font-weight: 700; color: var(--accent); }}
    table {{
      width: 100%;
      border-collapse: collapse;
      background: var(--card);
      border: 1px solid var(--line);
      margin-bottom: 20px;
    }}
    th, td {{ padding: 12px; border-bottom: 1px solid var(--line); text-align: left; vertical-align: top; }}
    th {{ background: #fbfaf7; }}
    @media (max-width: 900px) {{ .grid {{ grid-template-columns: repeat(2, 1fr); }} }}
    @media (max-width: 560px) {{ .grid {{ grid-template-columns: 1fr; }} body {{ padding: 16px; }} }}
  </style>
</head>
<body>
  <div class="shell">
    <section class="hero">
      <h1>Executive KPI Reporting Dashboard</h1>
      <p>Decision-support view generated from raw support operations data, including alerting and priority pressure.</p>
      <div class="grid">
        <div class="card"><div>Tickets</div><div class="metric">{summary['ticket_count']}</div></div>
        <div class="card"><div>Avg. Resolution</div><div class="metric">{summary['average_resolution_hours']}h</div></div>
        <div class="card"><div>SLA Compliance</div><div class="metric">{summary['sla_compliance_rate']:.0%}</div></div>
        <div class="card"><div>Reopened Rate</div><div class="metric">{summary['reopened_rate']:.0%}</div></div>
        <div class="card"><div>Health Score</div><div class="metric">{summary['operations_health_score']}</div></div>
      </div>
      <h2>Category Performance</h2>
      <table>
        <thead><tr><th>Category</th><th>Ticket Count</th><th>Average Resolution Hours</th><th>SLA Compliance</th><th>Risk Level</th></tr></thead>
        <tbody>{category_items}</tbody>
      </table>
      <h2>Priority Performance</h2>
      <table>
        <thead><tr><th>Priority</th><th>Ticket Count</th><th>Average Resolution Hours</th><th>SLA Compliance</th><th>Reopened Rate</th></tr></thead>
        <tbody>{priority_items}</tbody>
      </table>
      <h2>Daily Operations View</h2>
      <table>
        <thead><tr><th>Date</th><th>Ticket Count</th><th>Average Resolution Hours</th><th>Reopened Count</th><th>SLA Breach Count</th></tr></thead>
        <tbody>{daily_items}</tbody>
      </table>
      <h2>Alert Digest</h2>
      <table>
        <thead><tr><th>Severity</th><th>Owner</th><th>Signal</th><th>Recommended Action</th></tr></thead>
        <tbody>{alert_items}</tbody>
      </table>
    </section>
  </div>
</body>
</html>
"""


def write_dashboard(summary, category_rows, daily_rows, priority_rows, alerts):
    DASHBOARD_PATH.write_text(build_dashboard_html(summary, category_rows, daily_rows, priority_rows, alerts))
