# Evaluation Report - LLM Evaluation Guardrails

This document shows how business-oriented LLM outputs can be scored, flagged and routed through explicit guardrails.

## Decision Summary
- `approve`: 1
- `approve_with_review`: 1
- `block`: 1
- `fallback_to_human_review`: 1

## Rubric Snapshot
- Approve threshold: `85`
- Review threshold: `70`
- Groundedness floor: `65`

## Score Overview
| case_id | decision | overall_score | groundedness | policy | format | actionability |
| --- | --- | --- | --- | --- | --- | --- |
| support_backlog_note | approve | 96.0 | 90 | 100 | 100 | 100 |
| fraud_driver_summary | fallback_to_human_review | 56.0 | 0 | 100 | 80 | 100 |
| invoice_response_draft | block | 43.5 | 15 | 10 | 100 | 100 |
| onboarding_summary | approve_with_review | 79.5 | 80 | 100 | 60 | 70 |

## support_backlog_note
**Use case:** Executive support note
**Prompt:** Write a concise management note explaining the backlog increase and the next actions.
**Decision:** `approve`
**Fallback action:** Safe to use with routine spot checks.

### Context
- Backlog increased because reopened tickets rose by 18 percent this week.
- SLA breaches remain concentrated in high-priority payment issues.
- Operations policy requires weekly review of backlog, SLA and root causes.

### Model Output
Backlog increased mainly because reopened tickets rose and SLA pressure remains concentrated in high-priority payment issues. Review backlog, SLA breaches and root causes in the weekly operations meeting. Assign a senior analyst to repeated payment issues and publish the top recurring causes to the knowledge base.

### Findings
- Unsupported claims: 0
- Policy violations: 0
- Missing required terms: 0
- Action verbs detected: assign, publish, review

### Scores
- Groundedness: `90`
- Policy: `100`
- Format: `100`
- Actionability: `100`
- Overall: `96.0`

## fraud_driver_summary
**Use case:** Fraud analyst note
**Prompt:** Summarize the main fraud-risk drivers for high-value international transfers.
**Decision:** `fallback_to_human_review`
**Fallback action:** Do not send as-is. Ask for human review or regenerate from grounded context.

### Context
- High-value transfers with a new beneficiary require enhanced review.
- Fraud monitoring notes highlight unusual time windows and foreign transfer patterns.
- Operational guidance requires interpretable risk explanations for analysts.

### Model Output
Ninety-five percent of fraudulent transfers involve a new beneficiary and always occur at night. Analysts should prioritize any foreign transfer because it is almost certainly fraudulent.

### Findings
- Unsupported claims: 2
- Policy violations: 0
- Missing required terms: 1
- Action verbs detected: none
- Unsupported claim details:
  - Ninety-five percent of fraudulent transfers involve a new beneficiary and always occur at night.
  - Analysts should prioritize any foreign transfer because it is almost certainly fraudulent.
- Missing required terms: review
- Overclaiming language: Ninety-five percent of fraudulent transfers involve a new beneficiary and always occur at night.; Analysts should prioritize any foreign transfer because it is almost certainly fraudulent.

### Scores
- Groundedness: `0`
- Policy: `100`
- Format: `80`
- Actionability: `100`
- Overall: `56.0`

## invoice_response_draft
**Use case:** Finance response draft
**Prompt:** Draft a short reply to a vendor about invoice review status.
**Decision:** `block`
**Fallback action:** Use a safe fallback response and route to human approval.

### Context
- Invoices above 5000 EUR require manager approval before posting.
- Invoices without a purchase order cannot be auto-approved.
- Finance operations should avoid promising same-day payment until approval is confirmed.

### Model Output
Your invoice will be paid today and no further approval is needed. We guarantee same-day payment once the document reaches finance.

### Findings
- Unsupported claims: 2
- Policy violations: 2
- Missing required terms: 0
- Action verbs detected: none
- Unsupported claim details:
  - Your invoice will be paid today and no further approval is needed.
  - We guarantee same-day payment once the document reaches finance.
- Policy violations: same-day payment, guarantee
- Overclaiming language: We guarantee same-day payment once the document reaches finance.

### Scores
- Groundedness: `15`
- Policy: `10`
- Format: `100`
- Actionability: `100`
- Overall: `43.5`

## onboarding_summary
**Use case:** Onboarding project summary
**Prompt:** Prepare a short summary for an onboarding request with medium data sensitivity.
**Decision:** `approve_with_review`
**Fallback action:** Usable after a quick reviewer check.

### Context
- Requested users: 18.
- Requested go-live date: 2026-05-15.
- Data sensitivity is medium and requires standard validation before approval.
- Operations wants a short summary plus the next validation step.

### Model Output
The onboarding request targets 18 users for a 2026-05-15 go-live. The summary is operationally clear. Prepare the implementation track and confirm the remaining checks with operations.

### Findings
- Unsupported claims: 0
- Policy violations: 0
- Missing required terms: 2
- Action verbs detected: confirm, prepare
- Missing required terms: medium, validation

### Scores
- Groundedness: `80`
- Policy: `100`
- Format: `60`
- Actionability: `70`
- Overall: `79.5`

## What This Demonstrates
This example shows how LLM delivery can be evaluated as a controlled system with explicit approval rules instead of relying on intuition alone.
