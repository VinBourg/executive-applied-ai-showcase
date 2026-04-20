# Orchestration Control Report - AI Tool Orchestration Control Layer

This report shows how multiple AI tools can be orchestrated with explicit policy, fallback and human-control rules.

## Routing Decisions

### Executive operating memo from internal finance and support signals
- Market: USA East
- Primary tool: `Local LLaMA stack`
- Fallback tool: `OpenAI GPT-5.4`
- Orchestration layer: `n8n + MCP gateway`
- Human gate: `mandatory`
- Why this route: Useful when confidentiality is high and the workflow can stay inside a restricted execution zone.
- Policy notes: Prefer for high-confidentiality internal workflows where local execution is required.

### Claims document review and reply preparation
- Market: Switzerland
- Primary tool: `Local LLaMA stack`
- Fallback tool: `n8n + MCP toolchain`
- Orchestration layer: `n8n + MCP gateway`
- Human gate: `mandatory`
- Why this route: Useful when confidentiality is high and the workflow can stay inside a restricted execution zone.
- Policy notes: Prefer for high-confidentiality internal workflows where local execution is required.

### Public market research brief with source gathering
- Market: France
- Primary tool: `Claude Enterprise`
- Fallback tool: `Gemini`
- Orchestration layer: `n8n + MCP gateway`
- Human gate: `sampled`
- Why this route: Strong long-context reasoning stack for synthesis, planning and enterprise review flows.
- Policy notes: Use when long-context synthesis and executive writing quality are primary concerns.

## What This Demonstrates

- AI tooling should be routed by policy, not by brand preference alone.
- Model selection, tool orchestration and human review must be explicit when systems touch business operations.
- A usable orchestration layer explains why a stack is chosen, when it falls back and where human approval remains necessary.
