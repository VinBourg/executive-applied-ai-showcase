import csv
import json
from pathlib import Path

BASE_DIR = Path(__file__).parent
INCIDENTS_PATH = BASE_DIR / "incident_feed.json"
REPORT_PATH = BASE_DIR / "incident_triage_report.md"
ACTION_QUEUE_PATH = BASE_DIR / "incident_action_queue.csv"
DECISION_LOG_PATH = BASE_DIR / "agent_decision_log.json"
PLAYBOOK_PATH = BASE_DIR / "escalation_playbook.md"

SEVERITY_POINTS = {"critical": 42, "high": 30, "medium": 18, "low": 8}
CUSTOMER_IMPACT_POINTS = {"high": 14, "medium": 8, "low": 3}


def load_incidents():
    return json.loads(INCIDENTS_PATH.read_text())["incidents"]


def risk_score(incident):
    score = SEVERITY_POINTS[incident["severity"]]
    if incident["freshness_delay_hours"] > incident["freshness_sla_hours"]:
        score += 10
    if incident["contract_status"] == "watch":
        score += 8
    if incident["contract_status"] == "breached":
        score += 16
    if incident["tests_pass_rate"] < 0.9:
        score += 10
    elif incident["tests_pass_rate"] < 0.95:
        score += 6
    if incident["ai_consumer"]:
        score += 10
    if incident["regulatory_context"]:
        score += 8
    if incident["recurring"]:
        score += 5
    return min(score + CUSTOMER_IMPACT_POINTS[incident["customer_impact"]], 100)


def risk_band(score):
    if score >= 78:
        return "critical"
    if score >= 60:
        return "high"
    if score >= 42:
        return "medium"
    return "low"


def recommended_agent_path(incident, score):
    steps = ["openclaw_summarize_signal", "attach_lineage_context"]
    if incident["contract_status"] in {"watch", "breached"}:
        steps.append("open_contract_review")
    if incident["freshness_delay_hours"] > incident["freshness_sla_hours"]:
        steps.append("trigger_freshness_check")
    if incident["ai_consumer"]:
        steps.append("pause_or_flag_downstream_ai_output")
    steps.append("n8n_owner_handoff")
    steps.append("mandatory_human_approval" if incident["regulatory_context"] or score >= 78 else "owner_review")
    return steps


def next_action(incident, score):
    if score >= 78:
        return "stop downstream publication, open executive incident bridge and require owner sign-off"
    if incident["ai_consumer"] and incident["contract_status"] != "active":
        return "flag AI consumer, route to data owner through n8n and rerun validation before release"
    if incident["freshness_delay_hours"] > incident["freshness_sla_hours"]:
        return "run freshness remediation and notify consumers of delayed publication"
    return "assign owner review and monitor the next load cycle"


def enrich_incidents(incidents):
    rows = []
    for incident in incidents:
        score = risk_score(incident)
        rows.append(
            {
                **incident,
                "risk_score": score,
                "risk_band": risk_band(score),
                "agent_path": recommended_agent_path(incident, score),
                "next_action": next_action(incident, score),
            }
        )
    return sorted(rows, key=lambda row: row["risk_score"], reverse=True)


def write_action_queue(rows):
    with ACTION_QUEUE_PATH.open("w", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=[
                "incident_id",
                "market",
                "system",
                "owner",
                "risk_score",
                "risk_band",
                "ai_consumer",
                "contract_status",
                "next_action",
            ],
            lineterminator="\n",
        )
        writer.writeheader()
        for row in rows:
            writer.writerow({field: row[field] for field in writer.fieldnames})


def write_decision_log(rows):
    payload = {
        "agentic_runtime": "OpenClaw for controlled agent reasoning, n8n for operational handoffs",
        "control_objective": "prioritize data-quality incidents before they contaminate analytics, AI agents or executive reporting",
        "routing_policy": "critical and regulated incidents require human approval; AI-consuming pipelines are flagged before downstream reuse",
        "decisions": [
            {
                "incident_id": row["incident_id"],
                "risk_score": row["risk_score"],
                "risk_band": row["risk_band"],
                "agent_path": row["agent_path"],
                "next_action": row["next_action"],
            }
            for row in rows
        ],
    }
    DECISION_LOG_PATH.write_text(json.dumps(payload, indent=2))


def write_report(rows):
    critical = [row for row in rows if row["risk_band"] == "critical"]
    ai_consumers = [row for row in rows if row["ai_consumer"]]
    lines = [
        "# Data Quality Incident Triage Agent",
        "",
        "This example shows how an OpenClaw-style agentic control layer can prioritize data-quality incidents before they impact AI assistants, BI reporting or operational decisions.",
        "",
        "## Executive Snapshot",
        "",
        f"- Incidents reviewed: {len(rows)}",
        f"- Critical incidents: {len(critical)}",
        f"- Incidents touching AI consumers: {len(ai_consumers)}",
        f"- Highest-risk system: `{rows[0]['system']}` with score {rows[0]['risk_score']}",
        "",
        "## Priority Queue",
        "",
    ]
    for row in rows:
        lines.extend(
            [
                f"### {row['incident_id']} - {row['system']}",
                f"- Market: {row['market']}",
                f"- Owner: {row['owner']}",
                f"- Risk: {row['risk_band']} ({row['risk_score']}/100)",
                f"- Signal: {row['signal']}",
                f"- Agent path: {', '.join(row['agent_path'])}",
                f"- Next action: {row['next_action']}",
                "",
            ]
        )
    lines.extend(
        [
            "## Why This Matters",
            "",
            "- AI systems inherit data-quality issues from upstream platforms.",
            "- A useful agentic workflow does not only answer; it routes, pauses, escalates and documents.",
            "- OpenClaw can hold the controlled reasoning layer while n8n handles notifications, approvals and owner handoffs.",
            "",
        ]
    )
    REPORT_PATH.write_text("\n".join(lines))


def write_playbook(rows):
    lines = [
        "# Escalation Playbook - Data Quality Incident Triage Agent",
        "",
        "## Control Rules",
        "",
        "- Stop downstream publication when risk is critical.",
        "- Flag AI consumers when an upstream contract is on watch or breached.",
        "- Require human approval for regulated or high-impact contexts.",
        "- Use OpenClaw for reasoned triage and n8n for owner notification, ticket creation and follow-up tracking.",
        "",
        "## Owner Handoff",
        "",
    ]
    owners = {}
    for row in rows:
        owners.setdefault(row["owner"], []).append(row["incident_id"])
    for owner, incidents in owners.items():
        lines.append(f"- {owner}: {', '.join(incidents)}")
    PLAYBOOK_PATH.write_text("\n".join(lines) + "\n")


def main():
    rows = enrich_incidents(load_incidents())
    write_action_queue(rows)
    write_decision_log(rows)
    write_report(rows)
    write_playbook(rows)

    print("Data quality incident triage agent")
    print("=" * 35)
    for row in rows[:3]:
        print(f"{row['incident_id']} -> {row['risk_band']} | {row['owner']}")
    print(f"Generated: {REPORT_PATH.name}, {ACTION_QUEUE_PATH.name}, {DECISION_LOG_PATH.name}, {PLAYBOOK_PATH.name}")


if __name__ == "__main__":
    main()
