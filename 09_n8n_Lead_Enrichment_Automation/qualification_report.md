# Qualification Report - n8n Lead Enrichment Automation

## Workflow
AI Lead Enrichment and Qualification

Business goal: Turn inbound leads from France, Switzerland and the US East Coast into qualified opportunities, CRM-ready actions and immediate outreach guidance.
Markets covered: France, Switzerland, USA East
Estimated opportunity pool: `1030k`
High-priority leads: `2`

## Ranked Leads
### Hudson Capital Ops
- Score: `93.8/100`
- Priority: `high`
- Market: `USA East (New York)`
- Offer angle: AI SQL analytics copilot and executive reporting
- Recommended owner: Decision-support consultant
- Next step: Partner-led discovery within 48 hours
- Sequence theme: Decision support, KPI review and executive operating rhythm
- Signal: Looking for agentic workflow automation, SQL analytics copilot support and governance-ready rollout for East Coast operations.
- Score breakdown: industry 22, geography 24, department 14, scale 18, revenue 18, buying signal 34, urgency 4

### Helvetic Claims Network
- Score: `91.7/100`
- Priority: `high`
- Market: `Switzerland (Geneva)`
- Offer angle: Document intake automation with approvals
- Recommended owner: Automation and operations consultant
- Next step: Partner-led discovery within 48 hours
- Sequence theme: Document workflow, auditability and human-in-the-loop controls
- Signal: Exploring LLM copilots for claims knowledge access, document intake automation and reporting controls before renewal season.
- Score breakdown: industry 20, geography 21, department 13, scale 15, revenue 18, buying signal 34, urgency 10

### Alpine Payments
- Score: `87.5/100`
- Priority: `medium`
- Market: `Switzerland (Zurich)`
- Offer angle: AI support automation and ticket routing
- Recommended owner: Automation consultant
- Next step: Qualified discovery call with tailored walkthrough
- Sequence theme: Support routing, backlog control and service efficiency
- Signal: Looking for AI workflow automation, support efficiency and a knowledge assistant before a Q3 pilot.
- Score breakdown: industry 22, geography 21, department 12, scale 12, revenue 14, buying signal 34, urgency 10

### Boston Service Grid
- Score: `81.2/100`
- Priority: `medium`
- Market: `USA East (Boston)`
- Offer angle: AI support automation and ticket routing
- Recommended owner: Automation consultant
- Next step: Qualified discovery call with tailored walkthrough
- Sequence theme: Support routing, backlog control and service efficiency
- Signal: Evaluating AI support automation, RAG knowledge assistants and field-service reporting before budget lock.
- Score breakdown: industry 18, geography 24, department 11, scale 12, revenue 10, buying signal 34, urgency 7

### Lyon Industrial Services
- Score: `74.2/100`
- Priority: `medium`
- Market: `France (Lyon)`
- Offer angle: Document intake automation with approvals
- Recommended owner: Automation and operations consultant
- Next step: Qualified discovery call with tailored walkthrough
- Sequence theme: Document workflow, auditability and human-in-the-loop controls
- Signal: Interested in AI support routing, document approvals and service KPI reporting with a clear pilot scope.
- Score breakdown: industry 18, geography 18, department 10, scale 12, revenue 10, buying signal 34, urgency 4

### Paris Retail Systems
- Score: `58.1/100`
- Priority: `low`
- Market: `France (Paris)`
- Offer angle: AI-assisted reporting and decision-support automation
- Recommended owner: Analytics and AI consultant
- Next step: Nurture with focused use-case brief
- Sequence theme: Reporting automation and business workflow acceleration
- Signal: Needs dashboard automation, lead qualification and inbound campaign routing before the summer launch.
- Score breakdown: industry 14, geography 19, department 11, scale 9, revenue 6, buying signal 20, urgency 4

## Workflow Nodes
- Webhook (n8n-nodes-base.webhook)
- Normalize Lead (n8n-nodes-base.set)
- Firmographic Enrichment (n8n-nodes-base.httpRequest)
- Buying Signal Parser (n8n-nodes-base.openAi)
- Offer Angle Mapping (n8n-nodes-base.code)
- Qualification Scoring (n8n-nodes-base.code)
- CRM Task Builder (n8n-nodes-base.code)
- CRM Update (n8n-nodes-base.httpRequest)
- Slack Notification (n8n-nodes-base.slack)
- Sequence Trigger (n8n-nodes-base.httpRequest)
- Account Owner Queue (n8n-nodes-base.googleSheets)

## Operational Outputs
- `lead_scorecard.csv` for full scoring and ownership review.
- `crm_sync_payload.json` for top-priority lead sync into a CRM or orchestration layer.
- `sequence_plan.md` for immediate outreach planning.

## What This Demonstrates
This example shows how an n8n-style workflow can turn inbound lead data into qualification, prioritization, CRM payloads and concrete routing actions for business teams.
