# AI Readiness Value Risk Assessment

This example scores agentic AI opportunities by value, data readiness, process clarity, adoption readiness, risk and integration complexity.

## Executive Decision

- Use cases reviewed: 6
- Pilot-ready candidates: 3
- Highest-priority candidate: `AI SQL portfolio copilot` (62.3/100)
- Recommended action: start pilot now
- Suggested stack: OpenClaw analyst agent + SQL review workflow

## Portfolio View

### AI SQL portfolio copilot
- Market: USA East
- Owner: Revenue Operations Lead
- Readiness score: 62.3/100
- Recommendation: start pilot now
- Suggested stack: OpenClaw analyst agent + SQL review workflow
- Main control: standard evaluation and owner sign-off
- Evidence: Recurring portfolio reviews need faster query-to-memo cycles.

### Claims document intake agent
- Market: Switzerland
- Owner: Claims Operations Director
- Readiness score: 61.4/100
- Recommendation: pilot with controls
- Suggested stack: OpenClaw reasoning layer + n8n approval workflow
- Main control: standard evaluation and owner sign-off
- Evidence: High document volume, manual classification and visible approval bottlenecks.

### KPI narrative generation
- Market: France
- Owner: Performance Manager
- Readiness score: 60.6/100
- Recommendation: start pilot now
- Suggested stack: n8n scheduled reporting + LLM narrative review
- Main control: standard evaluation and owner sign-off
- Evidence: Weekly reporting cycle is repetitive and already has trusted source tables.

### Internal policy RAG assistant
- Market: France
- Owner: Operations Excellence Lead
- Readiness score: 56.2/100
- Recommendation: keep in discovery backlog
- Suggested stack: RAG assistant + n8n feedback capture
- Main control: standard evaluation and owner sign-off
- Evidence: Knowledge is scattered across procedures, FAQs and support notes.

### Regulated client onboarding copilot
- Market: Switzerland
- Owner: Client Operations Head
- Readiness score: 49.7/100
- Recommendation: frame controls before pilot
- Suggested stack: OpenClaw guided copilot + n8n compliance gate
- Main control: mandatory human approval and legal/compliance review
- Evidence: Strong operational pain, but controls and validation gates must be designed first.

### Autonomous customer outreach agent
- Market: USA East
- Owner: Growth Lead
- Readiness score: 44.6/100
- Recommendation: frame controls before pilot
- Suggested stack: OpenClaw agent with strict n8n human approval gate
- Main control: mandatory human approval and legal/compliance review
- Evidence: Revenue upside exists, but approval, brand and CRM controls are not mature.

## Why This Matters

- It prevents agentic AI initiatives from being selected only because they sound attractive.
- It makes risk, data readiness and adoption constraints visible before build effort starts.
- OpenClaw and n8n are positioned as operational components only when the value/risk profile justifies them.
