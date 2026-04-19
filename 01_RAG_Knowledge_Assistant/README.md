# RAG Knowledge Assistant

A grounded business assistant that turns internal knowledge into a readable answer, an evidence trail and a reusable delivery pattern.

## Business problem

Business teams lose time when operational knowledge is spread across policies, checklists and support notes.
They do not need a generic chatbot. They need a usable answer with traceability.

## What the program does

- structures a small business knowledge base,
- detects the query intent,
- retrieves the strongest source matches before answering,
- produces a business-oriented answer with actions and grounding,
- writes trace files that make the retrieval logic reviewable.

## Operational outputs

- `demo_response.md`
  One grounded answer in a recruiter-friendly format.
- `retrieval_trace.json`
  Source scores and retrieval logic for the current query.
- `query_portfolio.md`
  Batch review of representative business questions.
- `query_scorecard.csv`
  Compact scorecard across the sample query set.

## Market fit

- France: internal copilots, support enablement, knowledge assistants and RAG-style enterprise use cases.
- Switzerland: regulated or operational environments where grounded answers and traceability matter.
- USA East: enterprise AI assistants that need evidence, usable outputs and an upgrade path toward API exposure.

## Run

```bash
python3 app.py
python3 app.py "How should we reduce backlog while keeping SLA performance visible?"
```

Optional API entry point:

```bash
uvicorn fastapi_app:app --reload
```

## Review in 60 seconds

Open `query_portfolio.md`, then `query_scorecard.csv`, then `retrieval_trace.json`.
That sequence shows the real value quickly:
- grounded answers,
- retrieval visibility,
- reusable assistant logic,
- business outputs instead of vague chat responses.
