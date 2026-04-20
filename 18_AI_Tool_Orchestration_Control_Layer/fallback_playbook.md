# Fallback Playbook - AI Tool Orchestration Control Layer

This playbook explains how the orchestration layer should degrade gracefully when the preferred tool is not the right tool at run time.

## Executive operating memo from internal finance and support signals
- Primary tool: `Local LLaMA stack`
- Fallback tool: `OpenAI GPT-5.4`
- Orchestration layer: `n8n + MCP gateway`
- Human gate: `mandatory`
- Fallback rule: if confidence, latency or policy constraints are not met, route to the fallback stack and retain the full decision trace.

## Claims document review and reply preparation
- Primary tool: `Local LLaMA stack`
- Fallback tool: `n8n + MCP toolchain`
- Orchestration layer: `n8n + MCP gateway`
- Human gate: `mandatory`
- Fallback rule: if confidence, latency or policy constraints are not met, route to the fallback stack and retain the full decision trace.

## Public market research brief with source gathering
- Primary tool: `Claude Enterprise`
- Fallback tool: `Gemini`
- Orchestration layer: `n8n + MCP gateway`
- Human gate: `sampled`
- Fallback rule: if confidence, latency or policy constraints are not met, route to the fallback stack and retain the full decision trace.
