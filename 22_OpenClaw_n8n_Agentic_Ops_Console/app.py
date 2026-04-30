import csv
import json
from pathlib import Path

BASE_DIR = Path(__file__).parent
EVENTS_PATH = BASE_DIR / "ops_events.json"
POLICY_PATH = BASE_DIR / "agent_tool_policy.json"
REPORT_PATH = BASE_DIR / "ops_console_report.md"
HANDOFF_PATH = BASE_DIR / "handoff_queue.csv"
TRACE_PATH = BASE_DIR / "agent_execution_trace.json"
RUNBOOK_PATH = BASE_DIR / "openclaw_n8n_runbook.md"


IMPACT_POINTS = {"high": 30, "medium": 18, "low": 8}
SENSITIVITY_POINTS = {"restricted": 18, "managed": 8, "public": 2}


def load_json(path):
    return json.loads(path.read_text())


def urgency_score(event):
    score = IMPACT_POINTS[event["business_impact"]] + SENSITIVITY_POINTS[event["data_sensitivity"]]
    score += max(0, 20 - int(event["sla_minutes_remaining"] / 10))
    if event["status"] in {"blocked_by_policy", "escalated"}:
        score += 22
    if event["confidence"] < 0.8:
        score += 10
    return min(score, 100)


def urgency_band(score):
    if score >= 70:
        return "critical"
    if score >= 54:
        return "high"
    if score >= 36:
        return "medium"
    return "low"


def policy_lookup(policies):
    return {policy["status"]: policy for policy in policies}


def build_queue(events, policies):
    lookup = policy_lookup(policies)
    queue = []
    for event in events:
        score = urgency_score(event)
        policy = lookup[event["status"]]
        queue.append(
            {
                **event,
                "urgency_score": score,
                "urgency_band": urgency_band(score),
                "required_action": policy["required_action"],
                "handoff": policy["handoff"],
                "runbook": policy["runbook"],
            }
        )
    return sorted(queue, key=lambda item: item["urgency_score"], reverse=True)


def write_handoff_queue(queue):
    with HANDOFF_PATH.open("w", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=[
                "event_id",
                "workflow",
                "market",
                "agent",
                "status",
                "urgency_score",
                "urgency_band",
                "required_action",
                "handoff",
            ],
            lineterminator="\n",
        )
        writer.writeheader()
        for item in queue:
            writer.writerow({field: item[field] for field in writer.fieldnames})


def write_trace(queue):
    payload = {
        "operating_model": "OpenClaw handles controlled agent reasoning; n8n handles workflow orchestration, notifications and system handoffs.",
        "trace_policy": "Every agent decision keeps status, confidence, sensitivity, SLA pressure and human-control requirement.",
        "events": [
            {
                "event_id": item["event_id"],
                "agent": item["agent"],
                "last_action": item["last_action"],
                "status": item["status"],
                "confidence": item["confidence"],
                "required_action": item["required_action"],
                "handoff": item["handoff"],
                "urgency_score": item["urgency_score"],
            }
            for item in queue
        ],
    }
    TRACE_PATH.write_text(json.dumps(payload, indent=2))


def write_report(queue):
    critical = [item for item in queue if item["urgency_band"] == "critical"]
    blocked = [item for item in queue if item["status"] == "blocked_by_policy"]
    lines = [
        "# OpenClaw n8n Agentic Ops Console",
        "",
        "This example shows a lightweight operating console for agentic workflows where OpenClaw handles controlled reasoning and n8n handles orchestration, approvals and system handoffs.",
        "",
        "## Executive Snapshot",
        "",
        f"- Active agentic events: {len(queue)}",
        f"- Critical events: {len(critical)}",
        f"- Policy-blocked events: {len(blocked)}",
        f"- Highest-priority workflow: `{queue[0]['workflow']}`",
        "",
        "## Agentic Operations Queue",
        "",
    ]
    for item in queue:
        lines.extend(
            [
                f"### {item['event_id']} - {item['workflow']}",
                f"- Market: {item['market']}",
                f"- Agent: {item['agent']}",
                f"- Status: {item['status']}",
                f"- Urgency: {item['urgency_band']} ({item['urgency_score']}/100)",
                f"- Required action: {item['required_action']}",
                f"- Handoff: {item['handoff']}",
                f"- Runbook: {item['runbook']}",
                "",
            ]
        )
    lines.extend(
        [
            "## Why This Matters",
            "",
            "- Agentic AI becomes useful when execution state, confidence, sensitivity and owner handoff are visible.",
            "- OpenClaw and n8n play complementary roles: reasoning control on one side, operational orchestration on the other.",
            "- This pattern is close to what clients need before scaling agentic workflows beyond isolated demos.",
            "",
        ]
    )
    REPORT_PATH.write_text("\n".join(lines))


def write_runbook(queue):
    lines = [
        "# OpenClaw + n8n Runbook",
        "",
        "## Operating Principles",
        "",
        "- Keep OpenClaw responsible for traceable agent reasoning and controlled execution proposals.",
        "- Keep n8n responsible for approvals, notifications, CRM/task updates and workflow handoffs.",
        "- Do not let restricted or policy-blocked actions execute without a human approval gate.",
        "",
        "## Priority Actions",
        "",
    ]
    for item in queue:
        lines.append(f"- {item['event_id']}: {item['runbook']} via {item['handoff']}.")
    RUNBOOK_PATH.write_text("\n".join(lines) + "\n")


def main():
    events = load_json(EVENTS_PATH)["events"]
    policies = load_json(POLICY_PATH)["policies"]
    queue = build_queue(events, policies)
    write_handoff_queue(queue)
    write_trace(queue)
    write_report(queue)
    write_runbook(queue)

    print("OpenClaw n8n agentic ops console")
    print("=" * 35)
    for item in queue[:3]:
        print(f"{item['event_id']} -> {item['urgency_band']} | {item['required_action']}")
    print(f"Generated: {REPORT_PATH.name}, {HANDOFF_PATH.name}, {TRACE_PATH.name}, {RUNBOOK_PATH.name}")


if __name__ == "__main__":
    main()
