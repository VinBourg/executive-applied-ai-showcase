# Workflow Studio Report - NoCode Agentic Workflow Studio

This document shows how low-code / no-code orchestration can be combined with agentic steps and explicit human control points.

## Executive Readout

### Claims triage and document follow-up
- Client profile: European insurance operations team (Switzerland)
- Trigger: Inbound email with claim form or missing document notice
- Current pain: Manual triage delays high-value claims and creates inconsistent follow-up paths.
- Delivery style: no-code first, agentic where it adds leverage, human review where risk rises
- Implementation mode: n8n / low-code orchestration with reusable AI blocks
- Estimated nodes: 7
- Systems: shared inbox, policy knowledge base, n8n orchestration, approval register

#### Node sequence
- Inbound trigger [trigger] -> owner `workflow orchestration` via `shared inbox`
- Context fetch [tool] -> owner `knowledge layer` via `policy knowledge base`
- Classify claim intent [agentic_step] -> owner `triage agent` via `LLM classification block`
- Draft document request [agentic_step] -> owner `communications agent` via `template + LLM drafting block`
- Escalation validation [human_gate] -> owner `claims supervisor` via `approval queue`
- Claims routing payload [output] -> owner `operations team` via `claims tracker`
- Audit trail [logging] -> owner `operations control` via `approval register`

### Vendor intake and approval workflow
- Client profile: Shared-services transformation team (France)
- Trigger: Supplier form submitted through portal
- Current pain: Vendor onboarding is slowed down by duplicate checks, missing data and fragmented approvals.
- Delivery style: no-code first, agentic where it adds leverage, human review where risk rises
- Implementation mode: n8n / low-code orchestration with reusable AI blocks
- Estimated nodes: 7
- Systems: form portal, ERP reference tables, n8n orchestration, audit log

#### Node sequence
- Inbound trigger [trigger] -> owner `workflow orchestration` via `form portal`
- Context fetch [tool] -> owner `knowledge layer` via `ERP reference tables`
- Check completeness and risk flags [agentic_step] -> owner `validation agent` via `rules + LLM explanation block`
- Prepare approval summary [agentic_step] -> owner `approval agent` via `summary generation block`
- Finance approval gate [human_gate] -> owner `finance operations lead` via `approval queue`
- Onboarding decision packet [output] -> owner `procurement team` via `vendor register`
- Audit trail [logging] -> owner `operations control` via `audit log`

## What This Demonstrates

- No-code and low-code automation can be packaged as an executive-readable delivery surface.
- Agentic logic matters when it is tied to tool calls, approvals and auditability.
- Human review remains explicit where operational or compliance risk rises.
