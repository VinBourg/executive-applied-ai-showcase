# OpenClaw n8n Agentic Ops Console

This example shows a lightweight operating console for agentic workflows where OpenClaw handles controlled reasoning and n8n handles orchestration, approvals and system handoffs.

## Executive Snapshot

- Active agentic events: 5
- Critical events: 2
- Policy-blocked events: 1
- Highest-priority workflow: `data_quality_incident_triage`

## Agentic Operations Queue

### OPS-005 - data_quality_incident_triage
- Market: France
- Agent: OpenClaw data quality triage agent
- Status: escalated
- Urgency: critical (99/100)
- Required action: incident_bridge
- Handoff: n8n alert and ticket
- Runbook: notify owner, create incident ticket and freeze downstream automation

### OPS-003 - sql_decision_support
- Market: USA East
- Agent: OpenClaw SQL copilot
- Status: blocked_by_policy
- Urgency: critical (98/100)
- Required action: owner_approval
- Handoff: n8n approval task
- Runbook: pause execution, preserve trace, request owner sign-off

### OPS-001 - client_document_intake
- Market: Switzerland
- Agent: OpenClaw document analyst
- Status: needs_human_approval
- Urgency: high (64/100)
- Required action: human_validation
- Handoff: n8n approval task
- Runbook: send extracted context to reviewer and wait before external action

### OPS-004 - kpi_narrative_generation
- Market: France
- Agent: OpenClaw reporting assistant
- Status: ready_for_review
- Urgency: medium (37/100)
- Required action: business_review
- Handoff: n8n reviewer notification
- Runbook: send draft output to owner for sampled review

### OPS-002 - lead_enrichment
- Market: USA East
- Agent: OpenClaw growth research agent
- Status: ready_to_sync
- Urgency: low (30/100)
- Required action: crm_sync
- Handoff: n8n CRM update
- Runbook: sync payload when confidence and sensitivity gates are satisfied

## Why This Matters

- Agentic AI becomes useful when execution state, confidence, sensitivity and owner handoff are visible.
- OpenClaw and n8n play complementary roles: reasoning control on one side, operational orchestration on the other.
- This pattern is close to what clients need before scaling agentic workflows beyond isolated demos.
