# RAG Knowledge Assistant

A compact retrieval-augmented assistant over a small business knowledge base, designed to show how a grounded AI assistant can produce a usable business answer rather than a generic response.

## Why it matters

This example demonstrates:
- business knowledge structuring,
- retrieval before generation,
- decision-oriented answer construction,
- a clean path from local prototype to API exposure.

## Business relevance

- internal knowledge assistant,
- support enablement,
- onboarding and FAQ acceleration,
- document-grounded business assistance.

## Files

- `app.py`
  CLI prototype that runs with standard Python and writes a recruiter-friendly output file.
- `core.py`
  Shared retrieval, intent detection and answer-building logic.
- `fastapi_app.py`
  Optional API version for a more premium GitHub showcase.
- `knowledge_base.json`
  Small business-oriented source set.
- `sample_queries.json`
  Example questions aligned with support, fraud and enablement use cases.
- `demo_response.md`
  Generated sample output showing the style of answer the assistant produces.
- `retrieval_trace.json`
  Generated trace showing source scores and retrieval breakdown.
- `query_portfolio.md`
  Batch review of multiple representative questions.
- `query_scorecard.csv`
  Compact scorecard for the sample query set.

## Run the local CLI demo

```bash
python3 app.py
python3 app.py "How should we reduce backlog while keeping SLA performance visible?"
```

## Optional FastAPI version

```bash
uvicorn fastapi_app:app --reload
```

Example request:

```bash
curl -X POST http://127.0.0.1:8000/query \
  -H "Content-Type: application/json" \
  -d '{"query": "How can we improve support efficiency while keeping knowledge accessible?"}'
```

## What a recruiter should see quickly

This folder shows a simple but credible assistant pattern:
- grounded sources,
- retrieval logic,
- readable business answer,
- explicit actions and follow-up questions,
- source scoring and traceability,
- a mini portfolio of representative query types.
