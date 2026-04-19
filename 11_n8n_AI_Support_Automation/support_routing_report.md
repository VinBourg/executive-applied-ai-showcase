# Support Routing Report - n8n AI Support Automation

## Workflow
AI Support Intake and Routing

Business goal: Reduce manual intake time while improving ticket routing and response consistency.

## Ticket Snapshot
- Channel: email
- Customer: Northbank
- Subject: Urgent issue with repeated transfer failures

## Routing Decision
- Assigned team: `payments-support`
- Priority: `high`
- Priority score: `95`
- SLA target: `15 minutes`

## Signals
- payments: True
- access: False
- urgent: True
- repeated_issue: True
- cutoff_risk: True

## Draft Reply
Hello Northbank, your request has been routed to payments-support. The issue is currently classified as high priority and is being reviewed with a target first update within 15 minutes.

## Workflow Nodes
- Email Trigger (n8n-nodes-base.emailReadImap)
- Normalize Payload (n8n-nodes-base.set)
- AI Classification (n8n-nodes-base.openAi)
- Routing Logic (n8n-nodes-base.switch)
- Ticket Creation (n8n-nodes-base.httpRequest)
- Draft Reply (n8n-nodes-base.openAi)
- Ops Notification (n8n-nodes-base.slack)

## What This Demonstrates
This example shows a fuller support automation flow: signal detection, scoring, routing, SLA logic and business-readable payload generation.
