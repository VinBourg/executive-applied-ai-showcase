import csv
import json
import sqlite3
from pathlib import Path

BASE_DIR = Path(__file__).parent
DATA_PATH = BASE_DIR / "account_metrics.csv"
QUESTIONS_PATH = BASE_DIR / "business_questions.json"
REPORT_PATH = BASE_DIR / "copilot_report.md"


def load_rows():
    rows = []
    with DATA_PATH.open(newline="") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            rows.append(
                {
                    "company_name": row["company_name"],
                    "industry": row["industry"],
                    "country": row["country"],
                    "monthly_revenue_k": float(row["monthly_revenue_k"]),
                    "revenue_growth_pct": float(row["revenue_growth_pct"]),
                    "product_adoption_pct": float(row["product_adoption_pct"]),
                    "open_tickets": int(row["open_tickets"]),
                    "nps": float(row["nps"]),
                    "pipeline_value_k": float(row["pipeline_value_k"]),
                }
            )
    return rows


def load_questions():
    return json.loads(QUESTIONS_PATH.read_text())


def setup_database(connection, rows):
    connection.row_factory = sqlite3.Row
    cursor = connection.cursor()
    cursor.executescript(
        """
        create table account_metrics (
            company_name text,
            industry text,
            country text,
            monthly_revenue_k real,
            revenue_growth_pct real,
            product_adoption_pct real,
            open_tickets integer,
            nps real,
            pipeline_value_k real
        );
        """
    )
    cursor.executemany(
        """
        insert into account_metrics values (
            :company_name,
            :industry,
            :country,
            :monthly_revenue_k,
            :revenue_growth_pct,
            :product_adoption_pct,
            :open_tickets,
            :nps,
            :pipeline_value_k
        )
        """,
        rows,
    )
    connection.commit()


def detect_intent(question):
    lowered = question.lower()
    if "industries" in lowered or "generate the most revenue" in lowered:
        return "segment_pressure"
    if "expansion" in lowered or "pipeline strength" in lowered or "adoption" in lowered:
        return "growth_focus"
    if "immediate review" in lowered or "contracting" in lowered or "support pressure" in lowered:
        return "risk_review"
    return "overview"


def build_query_spec(intent):
    if intent == "risk_review":
        return {
            "title": "Accounts requiring immediate review",
            "sql": """
                select company_name,
                       industry,
                       revenue_growth_pct,
                       open_tickets,
                       product_adoption_pct,
                       case
                           when revenue_growth_pct <= -10 and open_tickets >= 3 then 'urgent retention review'
                           when revenue_growth_pct < 0 and open_tickets >= 2 then 'stabilize account'
                           when product_adoption_pct < 60 then 'adoption recovery plan'
                           else 'monitor'
                       end as recommendation
                from account_metrics
                where revenue_growth_pct < 0
                   or open_tickets >= 3
                   or product_adoption_pct < 60
                order by revenue_growth_pct asc, open_tickets desc;
            """,
            "interpretation": "The copilot should isolate accounts combining contraction, operational friction and weak adoption because these are the accounts most likely to need coordinated action.",
            "actions": [
                "Launch retention reviews first on accounts with both negative growth and high ticket volume.",
                "Separate support stabilization from adoption recovery so the action plan stays clear.",
            ],
        }
    if intent == "segment_pressure":
        return {
            "title": "Revenue concentration versus support pressure by industry",
            "sql": """
                select industry,
                       round(sum(monthly_revenue_k), 1) as total_revenue_k,
                       round(avg(open_tickets), 1) as avg_open_tickets,
                       round(avg(revenue_growth_pct), 1) as avg_growth_pct,
                       round(avg(nps), 1) as avg_nps,
                       sum(case when open_tickets >= 3 then 1 else 0 end) as stressed_accounts
                from account_metrics
                group by industry
                order by total_revenue_k desc, avg_open_tickets desc;
            """,
            "interpretation": "The copilot should show where revenue concentration and support strain overlap, because this is where operational pressure can threaten the most value.",
            "actions": [
                "Protect high-revenue industries first when support pressure rises.",
                "Use stressed-account counts to prioritize targeted service reviews by segment.",
            ],
        }
    if intent == "growth_focus":
        return {
            "title": "Expansion priorities from adoption and pipeline strength",
            "sql": """
                select company_name,
                       industry,
                       pipeline_value_k,
                       product_adoption_pct,
                       revenue_growth_pct,
                       nps,
                       case
                           when pipeline_value_k >= 120 and product_adoption_pct >= 75 and nps >= 60 then 'prioritize expansion'
                           when pipeline_value_k >= 90 and product_adoption_pct >= 70 then 'qualified growth opportunity'
                           else 'prepare before expansion'
                       end as recommendation
                from account_metrics
                order by pipeline_value_k desc, product_adoption_pct desc, nps desc;
            """,
            "interpretation": "The copilot should identify expansion candidates with both commercial headroom and strong product footing, rather than relying on pipeline alone.",
            "actions": [
                "Focus growth effort on accounts combining strong pipeline, adoption and sentiment.",
                "Keep weaker-adoption accounts in enablement mode before pushing expansion motions.",
            ],
        }
    return {
        "title": "Portfolio overview",
        "sql": """
            select industry,
                   round(sum(monthly_revenue_k), 1) as total_revenue_k,
                   round(avg(revenue_growth_pct), 1) as avg_growth_pct
            from account_metrics
            group by industry
            order by total_revenue_k desc;
        """,
        "interpretation": "The copilot should first provide a readable portfolio summary before going deeper.",
        "actions": ["Use this overview to decide which business question should be investigated next."],
    }


def fetch_rows(connection, sql):
    cursor = connection.execute(sql)
    return [dict(row) for row in cursor.fetchall()]


def to_markdown_table(rows):
    if not rows:
        return "_No rows returned._"
    headers = list(rows[0].keys())
    header_line = "| " + " | ".join(headers) + " |"
    separator_line = "| " + " | ".join("---" for _ in headers) + " |"
    data_lines = []
    for row in rows:
        data_lines.append("| " + " | ".join(str(row[header]) for header in headers) + " |")
    return "\n".join([header_line, separator_line, *data_lines])


def business_summary(intent, rows):
    if intent == "risk_review" and rows:
        urgent = [row["company_name"] for row in rows if row["recommendation"] == "urgent retention review"]
        return f"Immediate attention should start with {', '.join(urgent) if urgent else 'the highest-friction accounts'}, where revenue contraction and ticket pressure overlap."
    if intent == "segment_pressure" and rows:
        top = rows[0]
        return (
            f"{top['industry']} is the largest revenue segment in this sample while still showing "
            f"{top['avg_open_tickets']} average open tickets, which makes it the first segment to protect operationally."
        )
    if intent == "growth_focus" and rows:
        focus = [row["company_name"] for row in rows if row["recommendation"] == "prioritize expansion"]
        return f"Expansion effort should concentrate first on {', '.join(focus) if focus else 'the accounts with the strongest combined adoption and pipeline signals'}."
    return "The portfolio view is readable, but the next step should be to move from overview to a sharper management question."


def build_report(entries):
    lines = [
        "# Copilot Report - AI SQL Analytics Copilot",
        "",
        "This document shows how a compact copilot can translate business questions into SQL and decision-oriented answers.",
        "",
    ]
    for index, entry in enumerate(entries, start=1):
        lines.extend(
            [
                f"## Question {index}",
                entry["question"],
                "",
                f"**Intent:** `{entry['intent']}`",
                f"**View:** {entry['title']}",
                "",
                "### Generated SQL",
                "```sql",
                entry["sql"].strip(),
                "```",
                "",
                "### Result",
                to_markdown_table(entry["rows"]),
                "",
                "### Business Interpretation",
                entry["interpretation"],
                "",
                "### Copilot Summary",
                entry["summary"],
                "",
                "### Recommended Actions",
            ]
        )
        lines.extend(f"- {action}" for action in entry["actions"])
        lines.append("")
    return "\n".join(lines) + "\n"


def main():
    rows = load_rows()
    questions = load_questions()
    connection = sqlite3.connect(":memory:")
    setup_database(connection, rows)

    report_entries = []
    print("AI SQL analytics copilot demo")
    print("=" * 29)
    for item in questions:
        question = item["question"]
        intent = detect_intent(question)
        spec = build_query_spec(intent)
        result_rows = fetch_rows(connection, spec["sql"])
        summary = business_summary(intent, result_rows)
        report_entries.append(
            {
                "question": question,
                "intent": intent,
                "title": spec["title"],
                "sql": spec["sql"],
                "rows": result_rows,
                "interpretation": spec["interpretation"],
                "summary": summary,
                "actions": spec["actions"],
            }
        )
        print(f"Question: {question}")
        print(f"  Intent: {intent}")
        print(f"  View: {spec['title']}")
        print(f"  Rows returned: {len(result_rows)}")
        print(f"  Summary: {summary}")
        print()

    REPORT_PATH.write_text(build_report(report_entries))
    print(f"Generated: {REPORT_PATH.name}")


if __name__ == "__main__":
    main()
