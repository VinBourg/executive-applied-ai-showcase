# OpenClaw n8n Agentic Ops Console

Lightweight operating-console example for supervising agentic workflows where OpenClaw manages controlled agent reasoning and n8n manages approvals, notifications and system handoffs.

## Business Use Case

Once several AI agents or LLM workflows run across operations, the client needs to know what is blocked, what is ready, what needs human approval and what should be escalated. This item turns agentic execution state into an operations-ready queue.

## What It Demonstrates

- OpenClaw positioned as the controlled reasoning and trace layer.
- n8n positioned as the orchestration and handoff layer.
- Explicit policy gates for restricted data, blocked actions and human approval.
- A practical operating surface for moving from agentic demos to supervised execution.

## Outputs

- `ops_console_report.md`
- `handoff_queue.csv`
- `agent_execution_trace.json`
- `openclaw_n8n_runbook.md`

## Run Locally

```bash
python3 app.py
```
