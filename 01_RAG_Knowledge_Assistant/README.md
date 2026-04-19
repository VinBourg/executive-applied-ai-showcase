# RAG Knowledge Assistant

A compact retrieval-augmented assistant over a small business knowledge base.

## Why it matters

This example demonstrates:
- business knowledge structuring
- retrieval before generation
- assistant design for support and internal enablement
- a clean path from local prototype to API exposure

## Files

- `app.py`
  CLI prototype that runs with standard Python.
- `core.py`
  Shared retrieval and answer-building logic.
- `fastapi_app.py`
  Optional API version for a more premium GitHub showcase.
- `knowledge_base.json`
  Small business-oriented source set.

## Run the local CLI demo

```bash
python3 app.py
python3 app.py "How should we handle high-priority support tickets?"
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
