import json
from pathlib import Path

BASE_DIR = Path(__file__).parent
TICKET_PATH = BASE_DIR / "sample_ticket.json"
WORKFLOW_PATH = BASE_DIR / "workflow.json"
REPORT_PATH = BASE_DIR / "support_routing_report.md"
PAYLOAD_PATH = BASE_DIR / "routing_payload.json"


def load_json(path):
    return json.loads(path.read_text())


def detect_signals(ticket):
    text = (ticket["subject"] + " " + ticket["message"]).lower()
    return {
        "payments": "transfer" in text or "payment" in text,
        "access": "login" in text or "access" in text,
        "urgent": ticket.get("priority_hint", "").lower() == "urgent" or "urgent" in text,
        "repeated_issue": "repeated" in text or "again" in text,
        "cutoff_risk": "cutoff" in text,
    }


def classify(signals):
    if signals["payments"]:
        return "payments-support"
    if signals["access"]:
        return "access-support"
    return "general-support"


def detect_priority(signals):
    score = 0
    score += 30 if signals["payments"] else 0
    score += 25 if signals["urgent"] else 0
    score += 20 if signals["repeated_issue"] else 0
    score += 20 if signals["cutoff_risk"] else 0
    if score >= 65:
        return "high", score
    if score >= 35:
        return "medium", score
    return "low", score


def build_sla_target(priority):
    if priority == "high":
        return "15 minutes"
    if priority == "medium":
        return "1 hour"
    return "4 hours"


def draft_reply(ticket, team, priority, sla_target):
    return (
        f"Hello {ticket['customer']}, your request has been routed to {team}. "
        f"The issue is currently classified as {priority} priority and is being reviewed with a target first update within {sla_target}."
    )


def build_payload(ticket, workflow, team, priority, score, sla_target, signals):
    return {
        "workflow": workflow["name"],
        "customer": ticket["customer"],
        "subject": ticket["subject"],
        "assigned_team": team,
        "priority": priority,
        "priority_score": score,
        "sla_target": sla_target,
        "signals": signals,
        "draft_reply": draft_reply(ticket, team, priority, sla_target),
    }


def build_report(ticket, workflow, payload):
    lines = [
        "# Support Routing Report - n8n AI Support Automation",
        "",
        f"## Workflow",
        workflow["name"],
        "",
        f"Business goal: {workflow['business_goal']}",
        "",
        "## Ticket Snapshot",
        f"- Channel: {ticket['channel']}",
        f"- Customer: {ticket['customer']}",
        f"- Subject: {ticket['subject']}",
        "",
        "## Routing Decision",
        f"- Assigned team: `{payload['assigned_team']}`",
        f"- Priority: `{payload['priority']}`",
        f"- Priority score: `{payload['priority_score']}`",
        f"- SLA target: `{payload['sla_target']}`",
        "",
        "## Signals",
    ]
    lines.extend(f"- {key}: {value}" for key, value in payload["signals"].items())
    lines.extend(
        [
            "",
            "## Draft Reply",
            payload["draft_reply"],
            "",
            "## Workflow Nodes",
        ]
    )
    lines.extend(f"- {node['name']} ({node['type']})" for node in workflow["nodes"])
    lines.extend(
        [
            "",
            "## What This Demonstrates",
            "This example shows a fuller support automation flow: signal detection, scoring, routing, SLA logic and business-readable payload generation.",
        ]
    )
    return "\n".join(lines) + "\n"


def main():
    ticket = load_json(TICKET_PATH)
    workflow = load_json(WORKFLOW_PATH)
    signals = detect_signals(ticket)
    team = classify(signals)
    priority, score = detect_priority(signals)
    sla_target = build_sla_target(priority)
    payload = build_payload(ticket, workflow, team, priority, score, sla_target, signals)

    PAYLOAD_PATH.write_text(json.dumps(payload, indent=2))
    REPORT_PATH.write_text(build_report(ticket, workflow, payload))

    print("n8n AI support automation demo")
    print("=" * 31)
    print(f"Workflow: {workflow['name']}")
    print(f"Assigned team: {team}")
    print(f"Detected priority: {priority} ({score})")
    print(f"SLA target: {sla_target}")
    print(f"Generated: {REPORT_PATH.name}, {PAYLOAD_PATH.name}")


if __name__ == "__main__":
    main()
