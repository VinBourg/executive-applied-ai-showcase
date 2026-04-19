import json
from pathlib import Path

BASE_DIR = Path(__file__).parent
INPUT_PATH = BASE_DIR / "product_brief.json"
BROCHURE_PATH = BASE_DIR / "brochure_draft.md"
PROMPT_PATH = BASE_DIR / "llm_prompt.txt"
PACKAGE_PATH = BASE_DIR / "content_package.md"

STYLE_GUIDE = {
    "tone": "executive, concrete, premium and business-oriented",
    "avoid": ["generic hype", "technical jargon overload", "claims without proof"],
    "structure": ["problem framing", "solution angle", "proof points", "call to action"],
}


def load_brief():
    return json.loads(INPUT_PATH.read_text())


def build_message_map(brief):
    return {
        "hero_line": f"{brief['product_name']} helps {brief['target_audience']} reduce repetitive reporting and knowledge-search effort.",
        "problem_statement": brief["problem"].capitalize() + ".",
        "solution_statement": brief["solution"].capitalize() + ".",
        "proof_points": brief["proof_points"],
        "call_to_action": "Start with a focused pilot on one reporting or knowledge workflow, then scale from proven usage.",
    }


def build_prompt(brief, message_map):
    lines = [
        "You are writing a concise executive brochure.",
        f"Product: {brief['product_name']}",
        f"Audience: {brief['target_audience']}",
        f"Tone: {STYLE_GUIDE['tone']}",
        f"Must include: {', '.join(STYLE_GUIDE['structure'])}",
        f"Avoid: {', '.join(STYLE_GUIDE['avoid'])}",
        f"Problem: {message_map['problem_statement']}",
        f"Solution: {message_map['solution_statement']}",
        f"Proof points: {', '.join(message_map['proof_points'])}",
        f"Call to action: {message_map['call_to_action']}",
        "Task: produce a premium one-page brochure draft with short sections and strong business readability.",
    ]
    return "\n".join(lines) + "\n"


def build_brochure(brief, message_map):
    proof_points = "\n".join(f"- {point}" for point in message_map["proof_points"])
    return f"""# {brief['product_name']}

## Executive Positioning
{message_map['hero_line']}

## Business Challenge
{message_map['problem_statement']}

## Solution
{message_map['solution_statement']}

## Why It Matters
{proof_points}

## Typical Use Cases
- internal knowledge assistant for operations teams
- faster reporting preparation for management reviews
- workflow automation for repetitive business tasks

## Recommended Call To Action
{message_map['call_to_action']}
"""


def build_content_package(brief, message_map):
    lines = [
        "# Content Package - Brochure Workflow",
        "",
        "## Editorial Intent",
        "- Keep the brochure concrete and commercially readable.",
        "- Position the product as an execution tool, not a generic AI promise.",
        "",
        "## Message Map",
        f"- Hero line: {message_map['hero_line']}",
        f"- Problem statement: {message_map['problem_statement']}",
        f"- Solution statement: {message_map['solution_statement']}",
        f"- Call to action: {message_map['call_to_action']}",
        "",
        "## Proof Points",
    ]
    lines.extend(f"- {point}" for point in brief["proof_points"])
    lines.extend(
        [
            "",
            "## Quality Checklist",
            "- Mentions the target audience clearly.",
            "- Avoids generic claims without proof points.",
            "- Ends with a concrete next step.",
        ]
    )
    return "\n".join(lines) + "\n"


def main():
    brief = load_brief()
    message_map = build_message_map(brief)
    brochure = build_brochure(brief, message_map)
    prompt = build_prompt(brief, message_map)
    package = build_content_package(brief, message_map)

    BROCHURE_PATH.write_text(brochure)
    PROMPT_PATH.write_text(prompt)
    PACKAGE_PATH.write_text(package)

    print("Brochure content workflow demo")
    print("=" * 29)
    print(f"Hero line: {message_map['hero_line']}")
    print(f"Call to action: {message_map['call_to_action']}")
    print(f"Generated: {BROCHURE_PATH.name}, {PROMPT_PATH.name}, {PACKAGE_PATH.name}")


if __name__ == "__main__":
    main()
