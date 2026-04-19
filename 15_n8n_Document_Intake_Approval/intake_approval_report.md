# Intake Approval Report - n8n Document Intake Approval

## Workflow
AI Document Intake and Approval Routing

Business goal: Convert inbound operational documents into classified, validated and approval-ready records with a clear human-in-the-loop path.

## Decision Summary
- `auto_approved`: 1
- `legal_and_business_approval`: 1
- `manual_review`: 1
- `operations_approval`: 1

## Processed Documents
| document_name | type | decision | route_team | missing_fields |
| --- | --- | --- | --- | --- |
| INV_AlpinePayments_2048.pdf | invoice | auto_approved | finance-operations | - |
| Invoice_MachinaSystems_991.pdf | invoice | manual_review | finance-operations | - |
| SwissAdvisory_Onboarding_Request.docx | onboarding_request | operations_approval | customer-operations | - |
| NordLedger_Contract_Change_Request.pdf | contract_change | legal_and_business_approval | legal-operations | - |

## INV_AlpinePayments_2048.pdf
- Source: email
- Sender: billing@alpine-payments.com
- Received at: 2026-04-18T09:20:00
- Type: `invoice`
- Decision: `auto_approved`
- Route team: `finance-operations`
- Reason: Low-value invoice with purchase order, ready for automatic posting.

### Extracted Fields
- vendor: Alpine Payments
- invoice_id: INV-2048
- amount_eur: 4800
- due_date: 2026-05-05
- purchase_order: PO-7711
- cost_center: OPS-21
- summary: Automation workshop and support setup

## Invoice_MachinaSystems_991.pdf
- Source: email
- Sender: accounts@machina-systems.com
- Received at: 2026-04-18T10:05:00
- Type: `invoice`
- Decision: `manual_review`
- Route team: `finance-operations`
- Reason: Invoice missing purchase order evidence, route for finance review.

### Extracted Fields
- vendor: Machina Systems
- invoice_id: INV-991
- amount_eur: 12800
- due_date: 2026-05-10
- purchase_order: [missing]
- cost_center: IT-44
- summary: Deployment support and process configuration

## SwissAdvisory_Onboarding_Request.docx
- Source: form
- Sender: ops@swissadvisorytech.com
- Received at: 2026-04-18T11:15:00
- Type: `onboarding_request`
- Decision: `operations_approval`
- Route team: `customer-operations`
- Reason: Scoped onboarding request ready for operations approval.

### Extracted Fields
- company: Swiss Advisory Tech
- requested_go_live: 2026-05-15
- requested_users: 18
- sponsor: Head of Operations
- scope: AI workflow automation pilot
- data_sensitivity: Medium

## NordLedger_Contract_Change_Request.pdf
- Source: email
- Sender: legal@nordledger-insurance.com
- Received at: 2026-04-18T14:40:00
- Type: `contract_change`
- Decision: `legal_and_business_approval`
- Route team: `legal-operations`
- Reason: High-value contract change requires legal and business approval.

### Extracted Fields
- counterparty: NordLedger Insurance
- effective_date: 2026-05-01
- change_summary: Extend the pilot scope to document intake automation and approval routing.
- business_owner: Chief Operating Officer
- value_impact_eur: 185000

## Workflow Nodes
- Email or Form Trigger (n8n-nodes-base.emailReadImap)
- Attachment Intake (n8n-nodes-base.moveBinaryData)
- OCR or Text Extraction (n8n-nodes-base.httpRequest)
- AI Document Classification (n8n-nodes-base.openAi)
- AI Field Extraction (n8n-nodes-base.code)
- Validation Rules (n8n-nodes-base.if)
- Approval Decision (n8n-nodes-base.switch)
- Human Approval (n8n-nodes-base.form)
- ERP or CRM Update (n8n-nodes-base.httpRequest)
- Slack Notification (n8n-nodes-base.slack)
- Archive and Audit Log (n8n-nodes-base.googleDrive)

## What This Demonstrates
This example shows how an n8n-style workflow can combine document classification, field extraction, rule-based validation and human approval without pretending that every document should be auto-approved.
