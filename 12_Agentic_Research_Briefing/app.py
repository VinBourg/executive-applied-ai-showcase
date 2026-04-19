import json
from pathlib import Path

BASE_DIR = Path(__file__).parent
INPUT_PATH = BASE_DIR / "company_profile.json"
OUTPUT_PATH = BASE_DIR / "research_brief.md"


def load_payload():
    return json.loads(INPUT_PATH.read_text())


def build_brief(payload):
    signals = "\n".join(f"- {signal}" for signal in payload["signals"])
    return f"""# Agentic Research Brief

## Target Account
{payload['company']} ({payload['industry']}, {payload['country']})

## Objective
{payload['objective']}

## Signals Collected
{signals}

## Agentic Workflow
- Planner: define the decision-oriented research angle
- Researcher: gather company and operational signals
- Analyzer: identify Applied AI and automation opportunities
- Synthesizer: prepare a concise advisory note

## Potential Opportunity Areas
- AI assistants for internal knowledge access
- workflow automation for support and reporting
- decision-support dashboards for operations visibility
- targeted AI enablement for business teams

## Advisory Angle
Focus on fast, pragmatic use cases with measurable operational value rather than broad transformation language.
"""


def main():
    payload = load_payload()
    brief = build_brief(payload)
    OUTPUT_PATH.write_text(brief)
    print(brief)
    print(f"Generated: {OUTPUT_PATH.name}")


if __name__ == "__main__":
    main()
