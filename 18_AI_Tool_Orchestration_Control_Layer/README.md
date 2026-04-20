# AI Tool Orchestration Control Layer

A control-layer example showing how to route business use cases across multiple AI tools with explicit policy, fallback and human-review logic.

## Business problem

Teams rarely need a single AI model.
They need a disciplined way to choose between tools depending on confidentiality, cost, reasoning depth, document grounding, web access and the operational risk of the task.

## What the program does

- scores multiple AI tools against real business-routing criteria,
- selects a primary stack, a fallback stack and an orchestration layer,
- writes a routing table, a policy matrix and a fallback playbook,
- frames orchestration as a business-control problem, not just a technical preference.

## Operational outputs

- `orchestration_control_report.md`
  Executive summary of the routing logic and policy rationale.
- `routing_decisions.csv`
  Use-case level routing table with primary and fallback tools.
- `tool_policy_matrix.csv`
  Compact policy view across available AI tools.
- `fallback_playbook.md`
  Fallback logic when the preferred tool is not the right tool at run time.

## Market fit

- France: multi-tool GenAI delivery, orchestration and AI workflow design.
- Switzerland: confidentiality-aware routing, controlled AI adoption and policy-minded deployment.
- USA East: enterprise AI operations, tool orchestration and explicit control-layer thinking.

## Run

```bash
python3 app.py
```

## Review in 60 seconds

Open `orchestration_control_report.md`, then `routing_decisions.csv`, then `tool_policy_matrix.csv`.
That sequence shows the signal quickly:
- multi-tool reasoning beyond a single model,
- explicit routing and fallback logic,
- orchestration discipline that maps to enterprise AI operations.
