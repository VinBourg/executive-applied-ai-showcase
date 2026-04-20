import csv
import json
from pathlib import Path

BASE_DIR = Path(__file__).parent
REQUESTS_PATH = BASE_DIR / "orchestration_requests.json"
TOOLS_PATH = BASE_DIR / "tool_registry.json"
REPORT_PATH = BASE_DIR / "orchestration_control_report.md"
ROUTING_PATH = BASE_DIR / "routing_decisions.csv"
POLICY_PATH = BASE_DIR / "tool_policy_matrix.csv"
PLAYBOOK_PATH = BASE_DIR / "fallback_playbook.md"


def load_json(path):
    return json.loads(path.read_text())


def score_tool(request, tool):
    score = 0
    if request["confidentiality"] == "high" and tool["data_zone"] == "restricted":
        score += 28
    if request["confidentiality"] != "high" and tool["data_zone"] == "managed":
        score += 10
    if request["reasoning_depth"] == "high" and tool["reasoning_depth"] == "high":
        score += 18
    if request["needs_multimodal"] and tool["multimodal"]:
        score += 12
    if request["needs_tools"] and tool["tool_use"]:
        score += 15
    if request["needs_document_grounding"] and tool["document_grounding"]:
        score += 12
    if request["cost_sensitivity"] == "high" and tool["cost_band"] == "low":
        score += 12
    if request["latency"] == "low" and tool["latency_profile"] == "fast":
        score += 10
    if request["needs_web"] and tool["web_connected"]:
        score += 8
    if request["action_type"] in tool["best_for"]:
        score += 15
    return score


def choose_stack(request, tools):
    scored = []
    for tool in tools:
        scored.append({"tool": tool, "score": score_tool(request, tool)})
    ranked = sorted(scored, key=lambda entry: entry["score"], reverse=True)

    primary = ranked[0]["tool"]
    fallback = ranked[1]["tool"]
    orchestration_layer = "n8n + MCP gateway" if request["needs_tools"] else "direct model routing layer"
    human_gate = (
        "mandatory" if request["confidentiality"] == "high" or request["action_type"] == "external_action" else "sampled"
    )
    return {
        "use_case": request["use_case"],
        "market": request["market"],
        "primary_tool": primary["name"],
        "fallback_tool": fallback["name"],
        "orchestration_layer": orchestration_layer,
        "human_gate": human_gate,
        "reason": primary["reason"],
        "primary_score": ranked[0]["score"],
        "fallback_score": ranked[1]["score"],
        "policy_notes": primary["policy_notes"],
    }


def write_routing(decisions):
    with ROUTING_PATH.open("w", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=[
                "use_case",
                "market",
                "primary_tool",
                "fallback_tool",
                "orchestration_layer",
                "human_gate",
                "primary_score",
                "fallback_score",
                "reason",
                "policy_notes",
            ],
        )
        writer.writeheader()
        writer.writerows(decisions)


def write_policy_matrix(tools):
    with POLICY_PATH.open("w", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=[
                "name",
                "data_zone",
                "reasoning_depth",
                "multimodal",
                "tool_use",
                "document_grounding",
                "web_connected",
                "cost_band",
                "latency_profile",
                "best_for",
            ],
        )
        writer.writeheader()
        for tool in tools:
            writer.writerow(
                {
                    "name": tool["name"],
                    "data_zone": tool["data_zone"],
                    "reasoning_depth": tool["reasoning_depth"],
                    "multimodal": tool["multimodal"],
                    "tool_use": tool["tool_use"],
                    "document_grounding": tool["document_grounding"],
                    "web_connected": tool["web_connected"],
                    "cost_band": tool["cost_band"],
                    "latency_profile": tool["latency_profile"],
                    "best_for": ", ".join(tool["best_for"]),
                }
            )


def write_playbook(decisions):
    lines = [
        "# Fallback Playbook - AI Tool Orchestration Control Layer",
        "",
        "This playbook explains how the orchestration layer should degrade gracefully when the preferred tool is not the right tool at run time.",
        "",
    ]
    for decision in decisions:
        lines.extend(
            [
                f"## {decision['use_case']}",
                f"- Primary tool: `{decision['primary_tool']}`",
                f"- Fallback tool: `{decision['fallback_tool']}`",
                f"- Orchestration layer: `{decision['orchestration_layer']}`",
                f"- Human gate: `{decision['human_gate']}`",
                "- Fallback rule: if confidence, latency or policy constraints are not met, route to the fallback stack and retain the full decision trace.",
                "",
            ]
        )
    PLAYBOOK_PATH.write_text("\n".join(lines))


def build_report(decisions):
    lines = [
        "# Orchestration Control Report - AI Tool Orchestration Control Layer",
        "",
        "This report shows how multiple AI tools can be orchestrated with explicit policy, fallback and human-control rules.",
        "",
        "## Routing Decisions",
        "",
    ]
    for decision in decisions:
        lines.extend(
            [
                f"### {decision['use_case']}",
                f"- Market: {decision['market']}",
                f"- Primary tool: `{decision['primary_tool']}`",
                f"- Fallback tool: `{decision['fallback_tool']}`",
                f"- Orchestration layer: `{decision['orchestration_layer']}`",
                f"- Human gate: `{decision['human_gate']}`",
                f"- Why this route: {decision['reason']}",
                f"- Policy notes: {decision['policy_notes']}",
                "",
            ]
        )
    lines.extend(
        [
            "## What This Demonstrates",
            "",
            "- AI tooling should be routed by policy, not by brand preference alone.",
            "- Model selection, tool orchestration and human review must be explicit when systems touch business operations.",
            "- A usable orchestration layer explains why a stack is chosen, when it falls back and where human approval remains necessary.",
            "",
        ]
    )
    REPORT_PATH.write_text("\n".join(lines))


def main():
    requests = load_json(REQUESTS_PATH)["requests"]
    tools = load_json(TOOLS_PATH)["tools"]
    decisions = [choose_stack(request, tools) for request in requests]
    write_routing(decisions)
    write_policy_matrix(tools)
    write_playbook(decisions)
    build_report(decisions)

    print("AI tool orchestration control layer")
    print("=" * 33)
    for decision in decisions:
        print(f"{decision['use_case']} -> {decision['primary_tool']} | fallback {decision['fallback_tool']}")
    print(f"Generated: {REPORT_PATH.name}, {ROUTING_PATH.name}, {POLICY_PATH.name}, {PLAYBOOK_PATH.name}")


if __name__ == "__main__":
    main()
