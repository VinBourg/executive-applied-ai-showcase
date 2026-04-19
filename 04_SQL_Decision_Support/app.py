import csv
import sqlite3
from pathlib import Path

BASE_DIR = Path(__file__).parent
REPORT_PATH = BASE_DIR / "decision_support_report.md"
QUEUE_PATH = BASE_DIR / "account_priority_queue.csv"

ACCOUNTS = [
    ("Northbank", "Banking", 42000, 8, 1, 58, 45),
    ("AgriNova", "AgriFood", 31000, 35, 3, 44, 18),
    ("FlowRetail", "Retail", 22000, 12, 0, 71, 27),
    ("AtlasPay", "Banking", 47000, 28, 2, 64, 55),
    ("PureFoods", "AgriFood", 26000, 6, 1, 68, 24),
    ("SwissAdvisory", "Insurance", 39000, 9, 1, 76, 61),
]

QUERY_SPECS = [
    {
        "title": "Revenue by segment",
        "sql": """
            select segment,
                   round(sum(monthly_revenue), 2) as total_revenue,
                   round(avg(adoption_score), 1) as avg_adoption_score
            from accounts
            group by segment
            order by total_revenue desc;
        """,
        "interpretation": "Shows where revenue concentration sits and whether adoption quality supports that value.",
    },
    {
        "title": "Accounts at risk",
        "sql": """
            select company_name,
                   segment,
                   usage_drop_pct,
                   open_support_tickets,
                   adoption_score,
                   renewal_window_days
            from accounts
            where usage_drop_pct >= 20
               or open_support_tickets >= 2
               or adoption_score <= 60
            order by usage_drop_pct desc, open_support_tickets desc, renewal_window_days asc;
        """,
        "interpretation": "Identifies accounts where usage decline, service pressure or weak adoption should trigger a coordinated review.",
    },
    {
        "title": "Priority follow-up queue",
        "sql": """
            select company_name,
                   segment,
                   case
                       when usage_drop_pct >= 25 and open_support_tickets >= 2 then 'urgent review'
                       when adoption_score <= 55 then 'adoption recovery'
                       when renewal_window_days <= 30 and usage_drop_pct >= 10 then 'renewal stabilization'
                       when open_support_tickets >= 2 then 'support stabilization'
                       else 'monitor'
                   end as recommendation,
                   renewal_window_days
            from accounts
            order by
                case
                    when usage_drop_pct >= 25 and open_support_tickets >= 2 then 1
                    when adoption_score <= 55 then 2
                    when renewal_window_days <= 30 and usage_drop_pct >= 10 then 3
                    when open_support_tickets >= 2 then 4
                    else 5
                end,
                renewal_window_days asc;
        """,
        "interpretation": "Turns raw account signals into an action queue a business team can immediately own.",
    },
]


def setup_database(connection):
    connection.row_factory = sqlite3.Row
    cursor = connection.cursor()
    cursor.executescript(
        """
        create table accounts (
            account_id integer primary key autoincrement,
            company_name text,
            segment text,
            monthly_revenue real,
            usage_drop_pct real,
            open_support_tickets integer,
            adoption_score integer,
            renewal_window_days integer
        );
        """
    )
    cursor.executemany(
        """
        insert into accounts (
            company_name,
            segment,
            monthly_revenue,
            usage_drop_pct,
            open_support_tickets,
            adoption_score,
            renewal_window_days
        ) values (?, ?, ?, ?, ?, ?, ?)
        """,
        ACCOUNTS,
    )
    connection.commit()


def fetch_rows(connection, sql):
    return [dict(row) for row in connection.execute(sql)]


def markdown_table(rows):
    if not rows:
        return "_No rows returned._"
    headers = list(rows[0].keys())
    lines = [
        "| " + " | ".join(headers) + " |",
        "| " + " | ".join("---" for _ in headers) + " |",
    ]
    for row in rows:
        lines.append("| " + " | ".join(str(row[header]) for header in headers) + " |")
    return "\n".join(lines)


def export_priority_queue(rows):
    with QUEUE_PATH.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=["company_name", "segment", "recommendation", "renewal_window_days"])
        writer.writeheader()
        writer.writerows(rows)


def build_report(query_results):
    lines = [
        "# SQL Decision Support Report",
        "",
        "This report shows how a compact SQL layer can produce segment visibility, account-risk reading and a business action queue.",
        "",
    ]
    for result in query_results:
        lines.extend(
            [
                f"## {result['title']}",
                result["interpretation"],
                "",
                "```sql",
                result["sql"].strip(),
                "```",
                "",
                markdown_table(result["rows"]),
                "",
            ]
        )
    lines.append("## What This Demonstrates")
    lines.append(
        "This example shows SQL used as a business decision tool: summarize value, detect risk and produce an actionable follow-up queue."
    )
    return "\n".join(lines) + "\n"


def main():
    connection = sqlite3.connect(":memory:")
    setup_database(connection)

    query_results = []
    for spec in QUERY_SPECS:
        rows = fetch_rows(connection, spec["sql"])
        query_results.append({**spec, "rows": rows})
        if spec["title"] == "Priority follow-up queue":
            export_priority_queue(rows)

    REPORT_PATH.write_text(build_report(query_results))

    print("SQL decision support demo")
    print("=" * 25)
    for result in query_results:
        print(f"- {result['title']}: {len(result['rows'])} rows")
    print(f"Generated: {REPORT_PATH.name}, {QUEUE_PATH.name}")


if __name__ == "__main__":
    main()
