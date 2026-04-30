# OpenClaw + n8n Runbook

## Operating Principles

- Keep OpenClaw responsible for traceable agent reasoning and controlled execution proposals.
- Keep n8n responsible for approvals, notifications, CRM/task updates and workflow handoffs.
- Do not let restricted or policy-blocked actions execute without a human approval gate.

## Priority Actions

- OPS-005: notify owner, create incident ticket and freeze downstream automation via n8n alert and ticket.
- OPS-003: pause execution, preserve trace, request owner sign-off via n8n approval task.
- OPS-001: send extracted context to reviewer and wait before external action via n8n approval task.
- OPS-004: send draft output to owner for sampled review via n8n reviewer notification.
- OPS-002: sync payload when confidence and sensitivity gates are satisfied via n8n CRM update.
