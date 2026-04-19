# Execution Plan Report - Agentic Knowledge Routing

This document shows how the workflow turns business requests into explainable agentic execution plans.

## Task 1
**Request:** Prepare a short answer for a client asking why support backlog increased this week and what actions should be taken.
**Context:** Operations manager needs a response by end of day.
**Deliverable:** Client-facing management note
**Deadline:** End of day
**Priority:** high
**Execution style:** planner -> retriever -> analyzer -> synthesizer -> reviewer
**Agents:** planner, ops_analyst, kpi_retriever, synthesizer, reviewer
**Tools:** kpi_reporter, knowledge_base, memo_writer
**Estimated runtime:** 18 minutes

### Steps
- Clarify the decision to support and the management audience.
- Retrieve backlog, SLA and reopened-ticket signals from trusted KPI sources.
- Identify the main operational drivers and split structural versus temporary issues.
- Draft a concise management response with action points and ownership.
- Review tone, clarity and business usefulness before delivery.

### Validation checks
- Backlog and SLA readings are consistent with the KPI source.
- Action points have named owners or clear follow-up areas.

### Success criteria
- A manager can read the note in under two minutes.
- The answer ends with concrete operational actions.

## Task 2
**Request:** Build a short internal note summarizing fraud-risk drivers for high-value international transfers.
**Context:** Fraud operations lead wants an interpretable summary for analysts.
**Deliverable:** Analyst-facing summary note
**Deadline:** Tomorrow morning
**Priority:** high
**Execution style:** planner -> retriever -> analyzer -> synthesizer -> reviewer
**Agents:** planner, risk_analyst, pattern_retriever, synthesizer, reviewer
**Tools:** fraud_patterns, risk_scorer, summary_writer
**Estimated runtime:** 20 minutes

### Steps
- Clarify the target analyst audience and expected operational use.
- Retrieve historical fraud patterns and interpretable risk drivers.
- Separate high-risk combinations from weaker contextual signals.
- Draft an analyst-facing summary with explicit escalation logic.
- Review for interpretability and operational clarity.

### Validation checks
- Risk drivers are interpretable and not stated as black-box output.
- Escalation guidance is explicit for analysts.

### Success criteria
- Analysts can reuse the summary during review workflows.
- The note makes risk combinations easy to scan.

## Task 3
**Request:** Outline an n8n-style automation note for inbound leads asking about AI workflow automation and support efficiency.
**Context:** A business lead wants a concise scoping note before a discovery call.
**Deliverable:** Pre-sales workflow briefing
**Deadline:** Within 24 hours
**Priority:** medium
**Execution style:** planner -> retriever -> analyzer -> synthesizer -> reviewer
**Agents:** planner, workflow_designer, business_analyst, synthesizer, reviewer
**Tools:** workflow_mapper, crm_rules, brief_writer
**Estimated runtime:** 16 minutes

### Steps
- Clarify the automation objective, trigger and target business owner.
- Map the workflow path from inbound event to qualification and routing.
- Define the minimum data fields, decision points and notifications.
- Draft a business-readable workflow note with expected outcomes.
- Review for operational simplicity and implementation readiness.

### Validation checks
- The workflow can be understood without deep technical context.
- The routing logic maps to a clear business outcome.

### Success criteria
- A stakeholder can approve the workflow scope quickly.
- The note is implementation-friendly for an automation builder.

