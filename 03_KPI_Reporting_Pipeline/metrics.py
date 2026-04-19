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
DASHBOARD_PATH = BASE_DIR / "dashboard.html"


def parse_datetime(value):
    return datetime.fromisoformat(value)


def load_rows():
    with INPUT_PATH.open() as handle:
        return list(csv.DictReader(handle))


def resolution_hours(row):
    created = parse_datetime(row["created_at"])
    resolved = parse_datetime(row["resolved_at"])
    return (resolved - created).total_seconds() / 3600


def compute_metrics(rows):
    total = len(rows)
    reopened = sum(int(row["reopened"]) for row in rows)
    durations = [resolution_hours(row) for row in rows]
    sla_met = sum(duration <= float(row["sla_hours"]) for row, duration in zip(rows, durations))

    per_category = defaultdict(list)
    per_day = defaultdict(list)
    for row, duration in zip(rows, durations):
        per_category[row["category"]].append(duration)
        per_day[row["created_at"][:10]].append({"duration": duration, "reopened": int(row["reopened"])})

    summary = {
        "ticket_count": total,
        "average_resolution_hours": round(sum(durations) / total, 2),
        "sla_compliance_rate": round(sla_met / total, 4),
        "reopened_rate": round(reopened / total, 4),
        "top_category_by_volume": max(per_category, key=lambda category: len(per_category[category])),
    }

    category_rows = []
    for category, values in sorted(per_category.items()):
        category_rows.append({
            "category": category,
            "ticket_count": len(values),
            "average_resolution_hours": round(sum(values) / len(values), 2),
        })

    daily_rows = []
    for day, values in sorted(per_day.items()):
        average_resolution = sum(item["duration"] for item in values) / len(values)
        reopened_count = sum(item["reopened"] for item in values)
        daily_rows.append({
            "date": day,
            "ticket_count": len(values),
            "average_resolution_hours": round(average_resolution, 2),
            "reopened_count": reopened_count,
        })

    return summary, category_rows, daily_rows


def write_outputs(summary, category_rows, daily_rows):
    SUMMARY_PATH.write_text(json.dumps(summary, indent=2))

    with CATEGORY_PATH.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=["category", "ticket_count", "average_resolution_hours"])
        writer.writeheader()
        writer.writerows(category_rows)

    with DAILY_PATH.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=["date", "ticket_count", "average_resolution_hours", "reopened_count"])
        writer.writeheader()
        writer.writerows(daily_rows)


def build_dashboard_html(summary, category_rows, daily_rows):
    category_items = "".join(
        f"<tr><td>{row['category']}</td><td>{row['ticket_count']}</td><td>{row['average_resolution_hours']}</td></tr>"
        for row in category_rows
    )
    daily_items = "".join(
        f"<tr><td>{row['date']}</td><td>{row['ticket_count']}</td><td>{row['average_resolution_hours']}</td><td>{row['reopened_count']}</td></tr>"
        for row in daily_rows
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
    .shell {{
      max-width: 1080px;
      margin: 0 auto;
    }}
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
      grid-template-columns: repeat(4, 1fr);
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
    th, td {{ padding: 12px; border-bottom: 1px solid var(--line); text-align: left; }}
    th {{ background: #fbfaf7; }}
    @media (max-width: 900px) {{ .grid {{ grid-template-columns: repeat(2, 1fr); }} }}
    @media (max-width: 560px) {{ .grid {{ grid-template-columns: 1fr; }} body {{ padding: 16px; }} }}
  </style>
</head>
<body>
  <div class="shell">
    <section class="hero">
      <h1>Executive KPI Reporting Dashboard</h1>
      <p>Compact decision-support view generated from raw support operations data.</p>
      <div class="grid">
        <div class="card"><div>Tickets</div><div class="metric">{summary['ticket_count']}</div></div>
        <div class="card"><div>Avg. Resolution</div><div class="metric">{summary['average_resolution_hours']}h</div></div>
        <div class="card"><div>SLA Compliance</div><div class="metric">{summary['sla_compliance_rate']:.0%}</div></div>
        <div class="card"><div>Reopened Rate</div><div class="metric">{summary['reopened_rate']:.0%}</div></div>
      </div>
      <h2>Performance by Category</h2>
      <table>
        <thead><tr><th>Category</th><th>Ticket Count</th><th>Average Resolution Hours</th></tr></thead>
        <tbody>{category_items}</tbody>
      </table>
      <h2>Daily Operations View</h2>
      <table>
        <thead><tr><th>Date</th><th>Ticket Count</th><th>Average Resolution Hours</th><th>Reopened Count</th></tr></thead>
        <tbody>{daily_items}</tbody>
      </table>
    </section>
  </div>
</body>
</html>
"""


def write_dashboard(summary, category_rows, daily_rows):
    DASHBOARD_PATH.write_text(build_dashboard_html(summary, category_rows, daily_rows))
