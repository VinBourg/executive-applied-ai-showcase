# Data Quality Incident Triage Agent

This example shows how an OpenClaw-style agentic control layer can prioritize data-quality incidents before they impact AI assistants, BI reporting or operational decisions.

## Executive Snapshot

- Incidents reviewed: 6
- Critical incidents: 2
- Incidents touching AI consumers: 5
- Highest-risk system: `portfolio_metrics` with score 100

## Priority Queue

### DQ-2026-044 - portfolio_metrics
- Market: Switzerland
- Owner: BI Product Owner
- Risk: critical (100/100)
- Signal: Semantic metric definition changed without release approval.
- Agent path: openclaw_summarize_signal, attach_lineage_context, open_contract_review, pause_or_flag_downstream_ai_output, n8n_owner_handoff, mandatory_human_approval
- Next action: stop downstream publication, open executive incident bridge and require owner sign-off

### DQ-2026-046 - payment_risk
- Market: France
- Owner: Risk Analytics Lead
- Risk: critical (91/100)
- Signal: Fraud-score feature distribution drift detected after upstream schema change.
- Agent path: openclaw_summarize_signal, attach_lineage_context, open_contract_review, trigger_freshness_check, pause_or_flag_downstream_ai_output, n8n_owner_handoff, mandatory_human_approval
- Next action: stop downstream publication, open executive incident bridge and require owner sign-off

### DQ-2026-041 - claims_intake
- Market: Switzerland
- Owner: Data Platform Lead
- Risk: high (77/100)
- Signal: Document classification labels dropped below the accepted quality threshold.
- Agent path: openclaw_summarize_signal, attach_lineage_context, trigger_freshness_check, pause_or_flag_downstream_ai_output, n8n_owner_handoff, mandatory_human_approval
- Next action: run freshness remediation and notify consumers of delayed publication

### DQ-2026-042 - support_events
- Market: USA East
- Owner: Support Operations Manager
- Risk: high (60/100)
- Signal: Ticket category values changed after a CRM workflow update.
- Agent path: openclaw_summarize_signal, attach_lineage_context, open_contract_review, pause_or_flag_downstream_ai_output, n8n_owner_handoff, owner_review
- Next action: flag AI consumer, route to data owner through n8n and rerun validation before release

### DQ-2026-043 - commercial_activity
- Market: France
- Owner: Revenue Analytics Owner
- Risk: medium (59/100)
- Signal: Daily gross revenue is missing for one source channel.
- Agent path: openclaw_summarize_signal, attach_lineage_context, trigger_freshness_check, n8n_owner_handoff, owner_review
- Next action: run freshness remediation and notify consumers of delayed publication

### DQ-2026-045 - lead_enrichment
- Market: USA East
- Owner: Growth Operations Lead
- Risk: low (36/100)
- Signal: Lead industry enrichment confidence is unstable across two providers.
- Agent path: openclaw_summarize_signal, attach_lineage_context, pause_or_flag_downstream_ai_output, n8n_owner_handoff, owner_review
- Next action: assign owner review and monitor the next load cycle

## Why This Matters

- AI systems inherit data-quality issues from upstream platforms.
- A useful agentic workflow does not only answer; it routes, pauses, escalates and documents.
- OpenClaw can hold the controlled reasoning layer while n8n handles notifications, approvals and owner handoffs.
