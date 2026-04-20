import csv
import json
from pathlib import Path

BASE_DIR = Path(__file__).parent
BRIEFS_PATH = BASE_DIR / "workflow_briefs.json"
REPORT_PATH = BASE_DIR / "workflow_studio_report.md"
WORKFLOW_PATH = BASE_DIR / "studio_workflow.json"
HANDOFF_PATH = BASE_DIR / "handoff_matrix.csv"
BACKLOG_PATH = BASE_DIR / "builder_backlog.md"


def load_briefs():
    return json.loads(BRIEFS_PATH.read_text())


def build_nodes(brief):
    ai_tasks = brief["ai_tasks"]
    human_checks = brief["human_checks"]
    outputs = brief["outputs"]
    systems = brief["systems"]

    nodes = [
        {
            "name": "Inbound trigger",
            "type": "trigger",
            "owner": "workflow orchestration",
            "system": systems[0],
            "control_point": "Trigger schema validated before run.",
        },
        {
            "name": "Context fetch",
            "type": "tool",
            "owner": "knowledge layer",
            "system": systems[1],
            "control_point": "Only approved context sources are queried.",
        },
    ]

    for task in ai_tasks:
        nodes.append(
            {
                "name": task["name"],
                "type": "agentic_step",
                "owner": task["owner"],
                "system": task["system"],
                "control_point": task["control_point"],
            }
        )

    for check in human_checks:
        nodes.append(
            {
                "name": check["name"],
                "type": "human_gate",
                "owner": check["owner"],
                "system": check["system"],
                "control_point": check["control_point"],
            }
        )

    for output in outputs:
        nodes.append(
            {
                "name": output["name"],
                "type": "output",
                "owner": output["owner"],
                "system": output["system"],
                "control_point": output["control_point"],
            }
        )

    nodes.append(
        {
            "name": "Audit trail",
            "type": "logging",
            "owner": "operations control",
            "system": systems[-1],
            "control_point": "Every routing and approval event is logged.",
        }
    )
    return nodes


def build_workflow(brief):
    nodes = build_nodes(brief)
    return {
        "client": brief["client"],
        "market": brief["market"],
        "process_name": brief["process_name"],
        "trigger": brief["trigger"],
        "current_pain": brief["current_pain"],
        "delivery_style": "no-code first, agentic where it adds leverage, human review where risk rises",
        "implementation_mode": "n8n / low-code orchestration with reusable AI blocks",
        "estimated_nodes": len(nodes),
        "systems": brief["systems"],
        "outputs": brief["outputs"],
        "nodes": nodes,
    }


def write_workflow_json(workflows):
    WORKFLOW_PATH.write_text(json.dumps({"workflows": workflows}, indent=2))


def write_handoff_matrix(workflows):
    with HANDOFF_PATH.open("w", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=["process_name", "node_name", "node_type", "owner", "system", "control_point"],
        )
        writer.writeheader()
        for workflow in workflows:
            for node in workflow["nodes"]:
                writer.writerow(
                    {
                        "process_name": workflow["process_name"],
                        "node_name": node["name"],
                        "node_type": node["type"],
                        "owner": node["owner"],
                        "system": node["system"],
                        "control_point": node["control_point"],
                    }
                )


def write_builder_backlog(workflows):
    lines = [
        "# Builder Backlog - NoCode Agentic Workflow Studio",
        "",
        "This backlog translates the workflow designs into a practical implementation queue.",
        "",
    ]
    for workflow in workflows:
        lines.extend(
            [
                f"## {workflow['process_name']}",
                f"- Confirm trigger payload for `{workflow['trigger']}`.",
                "- Build the orchestration spine in n8n or an equivalent no-code tool.",
                "- Connect approved knowledge and system blocks only.",
                "- Add human checkpoints before external-facing or high-risk actions.",
                "- Instrument logs, alerts and run-level traceability.",
                "- Validate outputs with the business owner before wider deployment.",
                "",
            ]
        )
    BACKLOG_PATH.write_text("\n".join(lines))


def build_report(workflows):
    lines = [
        "# Workflow Studio Report - NoCode Agentic Workflow Studio",
        "",
        "This document shows how low-code / no-code orchestration can be combined with agentic steps and explicit human control points.",
        "",
        "## Executive Readout",
        "",
    ]
    for workflow in workflows:
        lines.extend(
            [
                f"### {workflow['process_name']}",
                f"- Client profile: {workflow['client']} ({workflow['market']})",
                f"- Trigger: {workflow['trigger']}",
                f"- Current pain: {workflow['current_pain']}",
                f"- Delivery style: {workflow['delivery_style']}",
                f"- Implementation mode: {workflow['implementation_mode']}",
                f"- Estimated nodes: {workflow['estimated_nodes']}",
                f"- Systems: {', '.join(workflow['systems'])}",
                "",
                "#### Node sequence",
            ]
        )
        for node in workflow["nodes"]:
            lines.append(
                f"- {node['name']} [{node['type']}] -> owner `{node['owner']}` via `{node['system']}`"
            )
        lines.append("")
    lines.extend(
        [
            "## What This Demonstrates",
            "",
            "- No-code and low-code automation can be packaged as an executive-readable delivery surface.",
            "- Agentic logic matters when it is tied to tool calls, approvals and auditability.",
            "- Human review remains explicit where operational or compliance risk rises.",
            "",
        ]
    )
    REPORT_PATH.write_text("\n".join(lines))


def main():
    briefs = load_briefs()
    workflows = [build_workflow(brief) for brief in briefs]
    write_workflow_json(workflows)
    write_handoff_matrix(workflows)
    write_builder_backlog(workflows)
    build_report(workflows)

    print("NoCode agentic workflow studio")
    print("=" * 29)
    for workflow in workflows:
        print(f"{workflow['process_name']} | {workflow['market']} | nodes: {workflow['estimated_nodes']}")
    print(f"Generated: {REPORT_PATH.name}, {WORKFLOW_PATH.name}, {HANDOFF_PATH.name}, {BACKLOG_PATH.name}")


if __name__ == "__main__":
    main()
