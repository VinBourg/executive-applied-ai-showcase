# LLM Evaluation Guardrails

A compact evaluation and guardrail workflow that scores business-oriented LLM outputs, flags risky answers and routes weak generations to fallback or human review.

## Why it matters

This example demonstrates:
- prompt and output evaluation logic,
- groundedness and policy checks,
- practical fallback decisions,
- LLM quality control beyond a simple demo.

## Business relevance

- LLM evaluation,
- AI guardrails,
- output quality assurance,
- production-minded GenAI delivery.

## Files

- `app.py`
  Runs the evaluation workflow and generates a scorecard plus a readable report.
- `evaluation_cases.json`
  Test cases covering support, fraud, finance and onboarding scenarios.
- `rubric.json`
  Thresholds and weights used to make evaluation decisions.
- `evaluation_scorecard.csv`
  Generated score table for each case.
- `evaluation_report.md`
  Generated report showing findings, decisions and fallback actions.

## Run

```bash
python3 app.py
```

## What a recruiter should see quickly

This folder shows that LLM work is treated as a controlled system:
- business prompt in,
- scored output out,
- explicit risk findings,
- clear approve, review or block decision.
