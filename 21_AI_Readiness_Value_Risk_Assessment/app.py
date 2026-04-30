import csv
import json
from pathlib import Path

BASE_DIR = Path(__file__).parent
USE_CASES_PATH = BASE_DIR / "use_case_candidates.json"
REPORT_PATH = BASE_DIR / "readiness_assessment_report.md"
PORTFOLIO_PATH = BASE_DIR / "use_case_portfolio.csv"
ROADMAP_PATH = BASE_DIR / "thirty_day_pilot_roadmap.md"
CONTROL_MATRIX_PATH = BASE_DIR / "control_matrix.csv"


def load_use_cases():
    return json.loads(USE_CASES_PATH.read_text())["use_cases"]


def readiness_score(use_case):
    value = use_case["value_potential"] * 0.34
    data = use_case["data_readiness"] * 0.2
    process = use_case["process_clarity"] * 0.16
    adoption = use_case["adoption_readiness"] * 0.14
    complexity_penalty = use_case["integration_complexity"] * 0.08
    risk_penalty = use_case["risk_level"] * 0.08
    return round(value + data + process + adoption - complexity_penalty - risk_penalty, 1)


def recommendation(use_case, score):
    if score >= 60 and use_case["risk_level"] <= 55:
        return "start pilot now"
    if score >= 58 and use_case["risk_level"] <= 75:
        return "pilot with controls"
    if use_case["value_potential"] >= 82 and use_case["risk_level"] > 75:
        return "frame controls before pilot"
    return "keep in discovery backlog"


def primary_control(use_case):
    if use_case["risk_level"] >= 75:
        return "mandatory human approval and legal/compliance review"
    if use_case["integration_complexity"] >= 65:
        return "technical integration gate and rollback plan"
    if use_case["data_readiness"] < 65:
        return "data-quality remediation before automation"
    return "standard evaluation and owner sign-off"


def enrich(use_cases):
    rows = []
    for use_case in use_cases:
        score = readiness_score(use_case)
        rows.append(
            {
                **use_case,
                "readiness_score": score,
                "recommendation": recommendation(use_case, score),
                "primary_control": primary_control(use_case),
            }
        )
    return sorted(rows, key=lambda row: row["readiness_score"], reverse=True)


def write_portfolio(rows):
    with PORTFOLIO_PATH.open("w", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=[
                "use_case",
                "market",
                "business_owner",
                "readiness_score",
                "recommendation",
                "value_potential",
                "data_readiness",
                "risk_level",
                "target_stack",
                "primary_control",
            ],
            lineterminator="\n",
        )
        writer.writeheader()
        for row in rows:
            writer.writerow({field: row[field] for field in writer.fieldnames})


def write_control_matrix(rows):
    with CONTROL_MATRIX_PATH.open("w", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=["use_case", "risk_level", "integration_complexity", "control_required", "decision_gate", "target_stack"],
            lineterminator="\n",
        )
        writer.writeheader()
        for row in rows:
            writer.writerow(
                {
                    "use_case": row["use_case"],
                    "risk_level": row["risk_level"],
                    "integration_complexity": row["integration_complexity"],
                    "control_required": row["primary_control"],
                    "decision_gate": "governed pilot review" if "pilot" in row["recommendation"] else "framing review",
                    "target_stack": row["target_stack"],
                }
            )


def write_report(rows):
    top = rows[0]
    pilot_ready = [row for row in rows if row["recommendation"] in {"start pilot now", "pilot with controls"}]
    lines = [
        "# AI Readiness Value Risk Assessment",
        "",
        "This example scores agentic AI opportunities by value, data readiness, process clarity, adoption readiness, risk and integration complexity.",
        "",
        "## Executive Decision",
        "",
        f"- Use cases reviewed: {len(rows)}",
        f"- Pilot-ready candidates: {len(pilot_ready)}",
        f"- Highest-priority candidate: `{top['use_case']}` ({top['readiness_score']}/100)",
        f"- Recommended action: {top['recommendation']}",
        f"- Suggested stack: {top['target_stack']}",
        "",
        "## Portfolio View",
        "",
    ]
    for row in rows:
        lines.extend(
            [
                f"### {row['use_case']}",
                f"- Market: {row['market']}",
                f"- Owner: {row['business_owner']}",
                f"- Readiness score: {row['readiness_score']}/100",
                f"- Recommendation: {row['recommendation']}",
                f"- Suggested stack: {row['target_stack']}",
                f"- Main control: {row['primary_control']}",
                f"- Evidence: {row['evidence']}",
                "",
            ]
        )
    lines.extend(
        [
            "## Why This Matters",
            "",
            "- It prevents agentic AI initiatives from being selected only because they sound attractive.",
            "- It makes risk, data readiness and adoption constraints visible before build effort starts.",
            "- OpenClaw and n8n are positioned as operational components only when the value/risk profile justifies them.",
            "",
        ]
    )
    REPORT_PATH.write_text("\n".join(lines))


def write_roadmap(rows):
    selected = [row for row in rows if row["recommendation"] in {"start pilot now", "pilot with controls"}][:3]
    lines = [
        "# 30-Day Pilot Roadmap - AI Readiness Assessment",
        "",
        "## Week 1 - Framing",
        "",
        "- Confirm owner, users, business decision and expected output.",
        "- Validate data sources, access constraints and success metrics.",
        "",
        "## Week 2 - Prototype",
        "",
    ]
    for row in selected:
        lines.append(f"- Build first controlled prototype for `{row['use_case']}` using {row['target_stack']}.")
    lines.extend(
        [
            "",
            "## Week 3 - Evaluation",
            "",
            "- Run user review, output scoring, risk review and adoption feedback.",
            "",
            "## Week 4 - Decision",
            "",
            "- Decide whether to stop, extend, industrialize or reframe the pilot.",
            "- Produce executive memo, action queue and ownership map.",
        ]
    )
    ROADMAP_PATH.write_text("\n".join(lines) + "\n")


def main():
    rows = enrich(load_use_cases())
    write_portfolio(rows)
    write_control_matrix(rows)
    write_report(rows)
    write_roadmap(rows)

    print("AI readiness value risk assessment")
    print("=" * 35)
    for row in rows[:3]:
        print(f"{row['use_case']} -> {row['readiness_score']} | {row['recommendation']}")
    print(f"Generated: {REPORT_PATH.name}, {PORTFOLIO_PATH.name}, {CONTROL_MATRIX_PATH.name}, {ROADMAP_PATH.name}")


if __name__ == "__main__":
    main()
