# Qualification Report - n8n Lead Enrichment Automation

## Workflow
AI Lead Enrichment and Qualification

Business goal: Turn inbound leads into structured qualification, offer-angle and routing actions that sales teams can act on immediately.

## Ranked Leads
### Alpine Payments
- Score: `84/100`
- Priority: `high`
- Offer angle: AI support automation and ticket routing
- Next step: Executive follow-up within 48 hours
- Signal: Looking for AI workflow automation and support efficiency improvements before a Q3 pilot.
- Score breakdown: industry 22, geography 16, scale 14, buying signal 32

### NordLedger Insurance
- Score: `82/100`
- Priority: `high`
- Offer angle: RAG knowledge assistant and internal copilot
- Next step: Executive follow-up within 48 hours
- Signal: Exploring LLM copilots for claims knowledge access and reporting automation.
- Score breakdown: industry 18, geography 14, scale 18, buying signal 32

### Machina Systems
- Score: `68/100`
- Priority: `medium`
- Offer angle: AI support automation and ticket routing
- Next step: Qualified discovery call
- Signal: Interested in AI support routing but without an immediate automation budget.
- Score breakdown: industry 16, geography 10, scale 10, buying signal 32

### TerraRetail
- Score: `58/100`
- Priority: `low`
- Offer angle: AI-assisted reporting and decision-support automation
- Next step: Nurture sequence with lightweight content
- Signal: Needs dashboard automation and better lead qualification from inbound campaigns.
- Score breakdown: industry 10, geography 14, scale 10, buying signal 24

## Workflow Nodes
- Webhook (n8n-nodes-base.webhook)
- Normalize Lead (n8n-nodes-base.set)
- AI Enrichment Prompt (n8n-nodes-base.openAi)
- Lead Scoring (n8n-nodes-base.code)
- Offer Angle Mapping (n8n-nodes-base.code)
- CRM Update (n8n-nodes-base.httpRequest)
- Slack Notification (n8n-nodes-base.slack)
- Sequence Trigger (n8n-nodes-base.httpRequest)

## What This Demonstrates
This example shows how an n8n-style workflow can turn inbound lead data into qualification, prioritization and concrete routing actions for business teams.
