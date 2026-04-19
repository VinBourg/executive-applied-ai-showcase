import json
from pathlib import Path

BASE_DIR = Path(__file__).parent
INPUT_PATH = BASE_DIR / "client_brief.json"
OUTPUT_PATH = BASE_DIR / "dashboard_spec.md"


def load_brief():
    return json.loads(INPUT_PATH.read_text())


def build_spec(brief):
    filters = ", ".join(brief["preferred_filters"])
    users = ", ".join(brief["users"])
    pain_points = "\n".join(f"- {item}" for item in brief["pain_points"])
    questions = "\n".join(f"- {item}" for item in brief["key_questions"])
    kpis = [
        "Backlog volume",
        "SLA compliance rate",
        "Reopened ticket rate",
        "Average resolution time",
        "Tickets by category and team",
    ]
    kpi_lines = "\n".join(f"- {kpi}" for kpi in kpis)
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
- Executive overview
- Backlog and SLA analysis
- Team performance view
- Category and root-cause analysis

## Delivery Note
This dashboard should be designed for fast management review and clear operational follow-up rather than decorative reporting.
"""


def main():
    brief = load_brief()
    spec = build_spec(brief)
    OUTPUT_PATH.write_text(spec)
    print(spec)
    print(f"Generated: {OUTPUT_PATH.name}")


if __name__ == "__main__":
    main()
