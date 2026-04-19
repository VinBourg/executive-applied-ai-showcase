import csv
import json
import sqlite3
from pathlib import Path

BASE_DIR = Path(__file__).parent
DATA_PATH = BASE_DIR / "account_metrics.csv"
QUESTIONS_PATH = BASE_DIR / "business_questions.json"
REPORT_PATH = BASE_DIR / "copilot_report.md"
EXECUTIVE_MEMO_PATH = BASE_DIR / "executive_memo.md"
ROUTE_LOG_PATH = BASE_DIR / "copilot_route_log.csv"
ACTION_QUEUE_PATH = BASE_DIR / "portfolio_action_queue.csv"


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
            "decision_owner": "Customer success and operations lead",
            "next_step": "Run a joint retention and service review on the flagged accounts.",
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
            "decision_owner": "Segment operations director",
            "next_step": "Protect the most exposed segment with targeted service and account coverage actions.",
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
            "decision_owner": "Growth and account expansion lead",
            "next_step": "Prioritize the best expansion candidates and keep weaker adoption accounts in enablement mode.",
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
        "decision_owner": "Portfolio manager",
        "next_step": "Use the overview to pick the next management question.",
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


def entry_priority(intent, rows):
    if intent == "risk_review":
        return "high"
    if intent == "segment_pressure":
        top = rows[0] if rows else {}
        return "high" if top.get("stressed_accounts", 0) else "medium"
    if intent == "growth_focus":
        return "medium"
    return "low"


def top_signal(intent, rows):
    if not rows:
        return "No result rows returned."
    if intent == "risk_review":
        row = rows[0]
        return f"{row['company_name']} combines {row['revenue_growth_pct']}% growth with {row['open_tickets']} open tickets."
    if intent == "segment_pressure":
        row = rows[0]
        return f"{row['industry']} concentrates {row['total_revenue_k']}k revenue with {row['avg_open_tickets']} average open tickets."
    if intent == "growth_focus":
        row = rows[0]
        return f"{row['company_name']} leads with {row['pipeline_value_k']}k pipeline and {row['product_adoption_pct']}% adoption."
    return "Portfolio overview generated."


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
                f"**Decision owner:** {entry['decision_owner']}",
                f"**Priority:** `{entry['priority']}`",
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
        lines.extend(
            [
                "",
                "### Operating Note",
                f"- Next step: {entry['next_step']}",
                f"- Top signal: {entry['top_signal']}",
                "",
            ]
        )
    return "\n".join(lines) + "\n"


def write_route_log(entries):
    with ROUTE_LOG_PATH.open("w", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=[
                "question",
                "intent",
                "view",
                "decision_owner",
                "priority",
                "row_count",
                "top_signal",
                "next_step",
            ],
        )
        writer.writeheader()
        for entry in entries:
            writer.writerow(
                {
                    "question": entry["question"],
                    "intent": entry["intent"],
                    "view": entry["title"],
                    "decision_owner": entry["decision_owner"],
                    "priority": entry["priority"],
                    "row_count": len(entry["rows"]),
                    "top_signal": entry["top_signal"],
                    "next_step": entry["next_step"],
                }
            )


def build_action_queue(entries, row_lookup):
    actions = []
    for entry in entries:
        if entry["intent"] == "risk_review":
            for row in entry["rows"]:
                account = row_lookup[row["company_name"]]
                actions.append(
                    {
                        "intent": entry["intent"],
                        "entity_type": "account",
                        "entity_name": row["company_name"],
                        "market": account["country"],
                        "workstream": row["recommendation"],
                        "priority": "high" if row["recommendation"] != "monitor" else "medium",
                        "decision_owner": entry["decision_owner"],
                        "business_case": f"{account['monthly_revenue_k']}k revenue, {row['open_tickets']} open tickets, {row['revenue_growth_pct']}% growth",
                    }
                )
        elif entry["intent"] == "segment_pressure":
            for row in entry["rows"][:3]:
                actions.append(
                    {
                        "intent": entry["intent"],
                        "entity_type": "segment",
                        "entity_name": row["industry"],
                        "market": "Cross-market",
                        "workstream": "segment protection plan" if row["stressed_accounts"] else "maintain service quality",
                        "priority": "high" if row["stressed_accounts"] else "medium",
                        "decision_owner": entry["decision_owner"],
                        "business_case": f"{row['total_revenue_k']}k revenue with {row['stressed_accounts']} stressed accounts",
                    }
                )
        elif entry["intent"] == "growth_focus":
            for row in entry["rows"]:
                if row["recommendation"] == "prepare before expansion":
                    continue
                account = row_lookup[row["company_name"]]
                actions.append(
                    {
                        "intent": entry["intent"],
                        "entity_type": "account",
                        "entity_name": row["company_name"],
                        "market": account["country"],
                        "workstream": row["recommendation"],
                        "priority": "medium",
                        "decision_owner": entry["decision_owner"],
                        "business_case": f"{row['pipeline_value_k']}k pipeline, {row['product_adoption_pct']}% adoption, NPS {row['nps']}",
                    }
                )
    return actions


def write_action_queue(actions):
    with ACTION_QUEUE_PATH.open("w", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=[
                "intent",
                "entity_type",
                "entity_name",
                "market",
                "workstream",
                "priority",
                "decision_owner",
                "business_case",
            ],
        )
        writer.writeheader()
        writer.writerows(actions)


def build_executive_memo(entries, row_lookup):
    risk_entry = next(entry for entry in entries if entry["intent"] == "risk_review")
    segment_entry = next(entry for entry in entries if entry["intent"] == "segment_pressure")
    growth_entry = next(entry for entry in entries if entry["intent"] == "growth_focus")

    risk_accounts = [row["company_name"] for row in risk_entry["rows"]]
    revenue_under_watch = round(sum(row_lookup[name]["monthly_revenue_k"] for name in risk_accounts), 1)
    segment_row = segment_entry["rows"][0]
    growth_accounts = [row["company_name"] for row in growth_entry["rows"] if row["recommendation"] == "prioritize expansion"]
    expansion_pipeline = round(
        sum(row_lookup[name]["pipeline_value_k"] for name in growth_accounts),
        1,
    )

    lines = [
        "# Executive Memo - AI SQL Analytics Copilot",
        "",
        "This memo condenses the portfolio questions into a short leadership-ready briefing.",
        "",
        "## Headline Signals",
        f"- Revenue under watch: `{revenue_under_watch}k` across {', '.join(risk_accounts)}.",
        f"- Segment to protect: `{segment_row['industry']}` with `{segment_row['total_revenue_k']}k` revenue and `{segment_row['avg_open_tickets']}` average open tickets.",
        f"- Expansion pipeline to prioritize: `{expansion_pipeline}k` across {', '.join(growth_accounts)}.",
        "",
        "## Recommended Agenda",
        "- Run an immediate retention and service review on the flagged accounts before the next portfolio meeting.",
        "- Protect the top revenue segment with a focused service-capacity and customer-success plan.",
        "- Keep expansion resources concentrated on accounts with strong adoption and sentiment, not pipeline alone.",
        "",
        "## Delivery Value",
        "- Turns business questions into SQL and management-ready outputs.",
        "- Produces a readable route log and action queue for follow-up.",
        "- Makes analytics usable by decision-makers without exposing raw database work.",
    ]
    return "\n".join(lines) + "\n"


def run_copilot():
    rows = load_rows()
    questions = load_questions()
    row_lookup = {row["company_name"]: row for row in rows}

    connection = sqlite3.connect(":memory:")
    setup_database(connection, rows)

    entries = []
    for item in questions:
        question = item["question"]
        intent = detect_intent(question)
        spec = build_query_spec(intent)
        result_rows = fetch_rows(connection, spec["sql"])
        entry = {
            "question": question,
            "intent": intent,
            "title": spec["title"],
            "decision_owner": spec["decision_owner"],
            "next_step": spec["next_step"],
            "sql": spec["sql"],
            "rows": result_rows,
            "interpretation": spec["interpretation"],
            "summary": business_summary(intent, result_rows),
            "actions": spec["actions"],
        }
        entry["priority"] = entry_priority(intent, result_rows)
        entry["top_signal"] = top_signal(intent, result_rows)
        entries.append(entry)

    REPORT_PATH.write_text(build_report(entries))
    EXECUTIVE_MEMO_PATH.write_text(build_executive_memo(entries, row_lookup))
    write_route_log(entries)
    write_action_queue(build_action_queue(entries, row_lookup))
    connection.close()
    return entries


def main():
    entries = run_copilot()

    print("AI SQL analytics copilot demo")
    print("=" * 29)
    for entry in entries:
        print(f"Question: {entry['question']}")
        print(f"  Intent: {entry['intent']}")
        print(f"  View: {entry['title']}")
        print(f"  Priority: {entry['priority']}")
        print(f"  Decision owner: {entry['decision_owner']}")
        print(f"  Rows returned: {len(entry['rows'])}")
        print(f"  Summary: {entry['summary']}")
        print()

    print(
        "Generated: "
        f"{REPORT_PATH.name}, {EXECUTIVE_MEMO_PATH.name}, {ROUTE_LOG_PATH.name}, {ACTION_QUEUE_PATH.name}"
    )


if __name__ == "__main__":
    main()
