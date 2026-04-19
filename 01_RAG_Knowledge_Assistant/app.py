import sys
from pathlib import Path

from core import answer_query, load_sample_queries

BASE_DIR = Path(__file__).parent
OUTPUT_PATH = BASE_DIR / "demo_response.md"


def build_cli_output(result):
    lines = [
        "RAG knowledge assistant demo",
        "=" * 28,
        f"Question: {result['query']}",
        f"Intent: {result['intent']}",
        f"Confidence: {result['confidence']}",
        "",
        "Suggested answer:",
        result["answer"],
        "",
        "Recommended actions:",
    ]
    lines.extend(f"- {action}" for action in result["recommended_actions"])
    lines.append("")
    lines.append("Sources:")
    lines.extend(f"- {match['title']} (score: {match['score']})" for match in result["matches"])
    return "\n".join(lines)


def build_markdown_output(result):
    lines = [
        "# Demo Response - RAG Knowledge Assistant",
        "",
        f"## Question",
        result["query"],
        "",
        "## Assistant Positioning",
        f"- Intent: `{result['intent']}`",
        f"- Confidence: `{result['confidence']}`",
        "",
        "## Suggested Answer",
        result["answer"],
        "",
        "## Recommended Actions",
    ]
    lines.extend(f"- {action}" for action in result["recommended_actions"])
    lines.append("")
    lines.append("## Follow-up Questions")
    lines.extend(f"- {question}" for question in result["follow_up_questions"])
    lines.append("")
    lines.append("## Sources Used")
    lines.extend(f"- `{match['title']}`: {match['content']}" for match in result["matches"])
    lines.append("")
    lines.append("## Why This Matters")
    lines.append(
        "This output shows how a compact RAG assistant can move from retrieval to a decision-oriented answer that remains readable for business users."
    )
    return "\n".join(lines) + "\n"


def main():
    query = " ".join(sys.argv[1:]).strip()
    if not query:
        query = load_sample_queries()[0]["query"]
    result = answer_query(query)
    print(build_cli_output(result))
    OUTPUT_PATH.write_text(build_markdown_output(result))
    print(f"\nGenerated: {OUTPUT_PATH.name}")


if __name__ == "__main__":
    main()
