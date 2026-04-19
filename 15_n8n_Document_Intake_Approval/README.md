# n8n Document Intake Approval

A compact n8n-oriented workflow that turns inbound documents into classified, validated and approval-ready records with a clear human-in-the-loop decision path.

## Why it matters

This example demonstrates:
- document intake automation,
- AI-style classification and field extraction logic,
- validation and approval routing,
- human review where automation should stop.

## Business relevance

- finance and operations document intake,
- human-in-the-loop approval workflows,
- compliance-friendly automation,
- pragmatic AI automation for internal teams.

## Files

- `app.py`
  Runs the document intake workflow and generates recruiter-friendly outputs.
- `incoming_documents.json`
  Sample inbound documents aligned with invoice, onboarding and contract workflows.
- `workflow.json`
  Compact n8n-style workflow definition.
- `intake_approval_report.md`
  Generated report with classification, validation and approval decisions.
- `approval_queue.csv`
  Generated queue file that could be handed to operations or approvers.

## Run

```bash
python3 app.py
```

## What a recruiter should see quickly

This folder shows how a business document workflow can become:
- structured intake,
- clean classification,
- clear validation rules,
- automatic versus human approval logic,
- readable operational outputs.
