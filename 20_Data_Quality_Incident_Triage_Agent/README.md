# Data Quality Incident Triage Agent

Agentic triage example for data-quality incidents that can affect BI reporting, analytics products and downstream AI agents.

## Business Use Case

Data and AI teams need a controlled way to decide which incidents must be paused, escalated or monitored. A generic alert list is not enough when the same data feeds dashboards, RAG assistants, lead scoring, fraud models or executive reporting.

## What It Demonstrates

- OpenClaw-style agent reasoning for incident triage and escalation choices.
- n8n-style owner handoffs, notifications and follow-up tracking.
- Risk scoring across freshness, contract status, test pass rate, regulatory context and AI consumption.
- Operational outputs that a data owner, BI owner or AI product owner can review quickly.

## Outputs

- `incident_triage_report.md`
- `incident_action_queue.csv`
- `agent_decision_log.json`
- `escalation_playbook.md`

## Run Locally

```bash
python3 app.py
```
