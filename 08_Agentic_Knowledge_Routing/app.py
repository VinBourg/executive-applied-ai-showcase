import json
from pathlib import Path

BASE_DIR = Path(__file__).parent
INPUT_PATH = BASE_DIR / "task_briefs.json"
REPORT_PATH = BASE_DIR / "execution_plan_report.md"


def load_tasks():
    return json.loads(INPUT_PATH.read_text())


def build_plan(task):
    request = task["request"].lower()
    deliverable = task["deliverable"]
    base_plan = {
        "request": task["request"],
        "context": task["context"],
        "deliverable": deliverable,
        "deadline": task["deadline"],
        "priority": task["priority"],
        "execution_style": "planner -> retriever -> analyzer -> synthesizer -> reviewer",
    }

    if "lead" in request or "n8n" in request or "automation" in request:
        base_plan.update(
            {
                "agents": ["planner", "workflow_designer", "business_analyst", "synthesizer", "reviewer"],
                "tools": ["workflow_mapper", "crm_rules", "brief_writer"],
                "steps": [
                    "Clarify the automation objective, trigger and target business owner.",
                    "Map the workflow path from inbound event to qualification and routing.",
                    "Define the minimum data fields, decision points and notifications.",
                    "Draft a business-readable workflow note with expected outcomes.",
                    "Review for operational simplicity and implementation readiness.",
                ],
                "validation_checks": [
                    "The workflow can be understood without deep technical context.",
                    "The routing logic maps to a clear business outcome.",
                ],
                "success_criteria": [
                    "A stakeholder can approve the workflow scope quickly.",
                    "The note is implementation-friendly for an automation builder.",
                ],
                "estimated_runtime_minutes": 16,
            }
        )
        return base_plan

    if "backlog" in request or "support" in request:
        base_plan.update(
            {
                "agents": ["planner", "ops_analyst", "kpi_retriever", "synthesizer", "reviewer"],
                "tools": ["kpi_reporter", "knowledge_base", "memo_writer"],
                "steps": [
                    "Clarify the decision to support and the management audience.",
                    "Retrieve backlog, SLA and reopened-ticket signals from trusted KPI sources.",
                    "Identify the main operational drivers and split structural versus temporary issues.",
                    "Draft a concise management response with action points and ownership.",
                    "Review tone, clarity and business usefulness before delivery.",
                ],
                "validation_checks": [
                    "Backlog and SLA readings are consistent with the KPI source.",
                    "Action points have named owners or clear follow-up areas.",
                ],
                "success_criteria": [
                    "A manager can read the note in under two minutes.",
                    "The answer ends with concrete operational actions.",
                ],
                "estimated_runtime_minutes": 18,
            }
        )
        return base_plan

    if "fraud" in request or "transfer" in request:
        base_plan.update(
            {
                "agents": ["planner", "risk_analyst", "pattern_retriever", "synthesizer", "reviewer"],
                "tools": ["fraud_patterns", "risk_scorer", "summary_writer"],
                "steps": [
                    "Clarify the target analyst audience and expected operational use.",
                    "Retrieve historical fraud patterns and interpretable risk drivers.",
                    "Separate high-risk combinations from weaker contextual signals.",
                    "Draft an analyst-facing summary with explicit escalation logic.",
                    "Review for interpretability and operational clarity.",
                ],
                "validation_checks": [
                    "Risk drivers are interpretable and not stated as black-box output.",
                    "Escalation guidance is explicit for analysts.",
                ],
                "success_criteria": [
                    "Analysts can reuse the summary during review workflows.",
                    "The note makes risk combinations easy to scan.",
                ],
                "estimated_runtime_minutes": 20,
            }
        )
        return base_plan

    base_plan.update(
        {
            "agents": ["planner", "researcher", "synthesizer", "reviewer"],
            "tools": ["knowledge_base", "summary_writer"],
            "steps": [
                "Clarify the expected business output.",
                "Retrieve the most relevant context.",
                "Draft a concise answer.",
                "Review for clarity and actionability.",
            ],
            "validation_checks": ["The answer remains grounded in retrieved context."],
            "success_criteria": ["The output is concise and business-usable."],
            "estimated_runtime_minutes": 10,
        }
    )
    return base_plan


def build_report(plans):
    lines = [
        "# Execution Plan Report - Agentic Knowledge Routing",
        "",
        "This document shows how the workflow turns business requests into explainable agentic execution plans.",
        "",
    ]
    for index, plan in enumerate(plans, start=1):
        lines.extend(
            [
                f"## Task {index}",
                f"**Request:** {plan['request']}",
                f"**Context:** {plan['context']}",
                f"**Deliverable:** {plan['deliverable']}",
                f"**Deadline:** {plan['deadline']}",
                f"**Priority:** {plan['priority']}",
                f"**Execution style:** {plan['execution_style']}",
                f"**Agents:** {', '.join(plan['agents'])}",
                f"**Tools:** {', '.join(plan['tools'])}",
                f"**Estimated runtime:** {plan['estimated_runtime_minutes']} minutes",
                "",
                "### Steps",
            ]
        )
        lines.extend(f"- {step}" for step in plan["steps"])
        lines.append("")
        lines.append("### Validation checks")
        lines.extend(f"- {check}" for check in plan["validation_checks"])
        lines.append("")
        lines.append("### Success criteria")
        lines.extend(f"- {criterion}" for criterion in plan["success_criteria"])
        lines.append("")
    return "\n".join(lines) + "\n"


def main():
    tasks = load_tasks()
    plans = [build_plan(task) for task in tasks]
    REPORT_PATH.write_text(build_report(plans))

    print("Agentic knowledge routing demo")
    print("=" * 29)
    for index, plan in enumerate(plans, start=1):
        print(f"Task {index}: {plan['request']}")
        print(f"  Deliverable: {plan['deliverable']}")
        print(f"  Priority: {plan['priority']}")
        print(f"  Agents: {', '.join(plan['agents'])}")
        print(f"  Tools: {', '.join(plan['tools'])}")
        print(f"  Runtime: {plan['estimated_runtime_minutes']} min")
        print()
    print(f"Generated: {REPORT_PATH.name}")


if __name__ == "__main__":
    main()
