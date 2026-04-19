import csv
import json
from pathlib import Path

BASE_DIR = Path(__file__).parent
INPUT_PATH = BASE_DIR / "client_brief.json"
SPEC_PATH = BASE_DIR / "dashboard_spec.md"
CATALOG_PATH = BASE_DIR / "metric_catalog.csv"
WIREFRAME_PATH = BASE_DIR / "wireframe_notes.md"

METRIC_CATALOG = [
    {"metric_name": "Backlog volume", "definition": "Open tickets not yet resolved", "business_value": "Tracks workload accumulation"},
    {"metric_name": "SLA compliance rate", "definition": "Share of tickets handled within SLA", "business_value": "Shows service discipline"},
    {"metric_name": "Reopened ticket rate", "definition": "Share of tickets reopened after closure", "business_value": "Highlights quality issues"},
    {"metric_name": "Average resolution time", "definition": "Average time from open to close", "business_value": "Measures delivery speed"},
    {"metric_name": "Tickets by category", "definition": "Distribution of tickets by problem type", "business_value": "Identifies main drivers"},
]


def load_brief():
    return json.loads(INPUT_PATH.read_text())


def build_pages(brief):
    return [
        {
            "page": "Executive overview",
            "purpose": "Give management a one-screen summary of backlog, SLA and risk signals.",
            "widgets": ["Backlog KPI card", "SLA KPI card", "Trend chart", "Top risk categories"],
        },
        {
            "page": "Backlog and SLA analysis",
            "purpose": "Explain where the backlog is concentrated and where SLA pressure is rising.",
            "widgets": ["Category heatmap", "SLA by team", "Priority breakdown", "Reopened rate trend"],
        },
        {
            "page": "Team performance view",
            "purpose": "Help team leads identify stabilization needs and staffing gaps.",
            "widgets": ["Resolution time by team", "Open tickets by team", "Escalation volume", "Shift load view"],
        },
    ]


def build_spec(brief, pages):
    filters = ", ".join(brief["preferred_filters"])
    users = ", ".join(brief["users"])
    pain_points = "\n".join(f"- {item}" for item in brief["pain_points"])
    questions = "\n".join(f"- {item}" for item in brief["key_questions"])
    kpi_lines = "\n".join(f"- {row['metric_name']}" for row in METRIC_CATALOG)
    page_lines = []
    for page in pages:
        page_lines.append(f"### {page['page']}")
        page_lines.append(f"- Purpose: {page['purpose']}")
        page_lines.extend(f"- Widget: {widget}" for widget in page["widgets"])
        page_lines.append("")
    return f"""# Dashboard Specification - {brief['client']}

## Objective
{brief['objective']}

## Primary Users
{users}

## Pain Points
{pain_points}

## Key Business Questions
{questions}

## Recommended KPIs
{kpi_lines}

## Recommended Filters
- {filters}

## Suggested Pages
{chr(10).join(page_lines).strip()}

## Delivery Note
This dashboard should be designed for fast management review and clear operational follow-up rather than decorative reporting.
"""


def write_metric_catalog():
    with CATALOG_PATH.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=["metric_name", "definition", "business_value"])
        writer.writeheader()
        writer.writerows(METRIC_CATALOG)


def build_wireframe_notes(pages):
    lines = [
        "# Wireframe Notes - Dashboard Brief Generator",
        "",
        "The goal is to help an analytics team move quickly from business brief to page structure.",
        "",
    ]
    for page in pages:
        lines.extend(
            [
                f"## {page['page']}",
                f"- Purpose: {page['purpose']}",
                "- Widget stack:",
            ]
        )
        lines.extend(f"  - {widget}" for widget in page["widgets"])
        lines.append("")
    return "\n".join(lines) + "\n"


def main():
    brief = load_brief()
    pages = build_pages(brief)
    spec = build_spec(brief, pages)
    SPEC_PATH.write_text(spec)
    write_metric_catalog()
    WIREFRAME_PATH.write_text(build_wireframe_notes(pages))

    print("Dashboard brief generator demo")
    print("=" * 30)
    print(f"Client: {brief['client']}")
    print(f"Pages planned: {len(pages)}")
    for page in pages:
        print(f"- {page['page']}: {len(page['widgets'])} widgets")
    print(f"Generated: {SPEC_PATH.name}, {CATALOG_PATH.name}, {WIREFRAME_PATH.name}")


if __name__ == "__main__":
    main()
