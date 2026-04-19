import csv
import json
import sys
from pathlib import Path

from core import answer_query, load_sample_queries

BASE_DIR = Path(__file__).parent
OUTPUT_PATH = BASE_DIR / "demo_response.md"
TRACE_PATH = BASE_DIR / "retrieval_trace.json"
PORTFOLIO_PATH = BASE_DIR / "query_portfolio.md"
SCORECARD_PATH = BASE_DIR / "query_scorecard.csv"


def build_cli_output(result):
    lines = [
        "RAG knowledge assistant demo",
        "=" * 28,
        f"Question: {result['query']}",
        f"Intent: {result['intent']}",
        f"Confidence: {result['confidence']} ({result['confidence_score']})",
        f"Stakeholder: {result['analysis']['stakeholder']}",
        f"Deliverable: {result['analysis']['requested_deliverable']}",
        "",
        "Suggested answer:",
        result["answer"],
        "",
        "Grounding note:",
        result["grounding_note"],
        "",
        "Recommended actions:",
    ]
    lines.extend(f"- {action}" for action in result["recommended_actions"])
    lines.append("")
    lines.append("Top evidence:")
    lines.extend(f"- {point['source']} (score {point['score']}): {point['evidence']}" for point in result["evidence_points"])
    return "\n".join(lines)


def build_markdown_output(result):
    lines = [
        "# Demo Response - RAG Knowledge Assistant",
        "",
        "## Question",
        result["query"],
        "",
        "## Query Analysis",
        f"- Intent: `{result['intent']}`",
        f"- Confidence: `{result['confidence']}` (`{result['confidence_score']}`)",
        f"- Stakeholder: `{result['analysis']['stakeholder']}`",
        f"- Urgency: `{result['analysis']['urgency']}`",
        f"- Deliverable: `{result['analysis']['requested_deliverable']}`",
        "",
        "## Suggested Answer",
        result["answer"],
        "",
        "## Grounding Note",
        result["grounding_note"],
        "",
        "## Evidence Points",
    ]
    for point in result["evidence_points"]:
        matched_terms = ", ".join(point["matched_terms"]) if point["matched_terms"] else "none"
        lines.extend(
            [
                f"### {point['source']}",
                f"- Evidence: {point['evidence']}",
                f"- Matched terms: {matched_terms}",
                f"- Score: `{point['score']}`",
                "",
            ]
        )
    lines.append("## Recommended Actions")
    lines.extend(f"- {action}" for action in result["recommended_actions"])
    lines.append("")
    lines.append("## Follow-up Questions")
    lines.extend(f"- {question}" for question in result["follow_up_questions"])
    lines.append("")
    lines.append("## Retrieval Trace")
    for match in result["matches"]:
        breakdown = match["score_breakdown"]
        lines.extend(
            [
                f"- `{match['title']}` score `{match['score']}`",
                f"  title terms: {', '.join(breakdown['title_terms']) or 'none'}",
                f"  tag terms: {', '.join(breakdown['tag_terms']) or 'none'}",
                f"  content overlap: {', '.join(breakdown['overlap_terms']) or 'none'}",
            ]
        )
    lines.append("")
    lines.append("## Why This Matters")
    lines.append(
        "This output shows a more complete RAG workflow: query analysis, retrieval trace, grounded answer and a business-oriented deliverable."
    )
    return "\n".join(lines) + "\n"


def build_portfolio(results):
    lines = [
        "# Query Portfolio - RAG Knowledge Assistant",
        "",
        "This document shows how the assistant handles several business-oriented query types.",
        "",
    ]
    for result in results:
        lines.extend(
            [
                f"## {result['query']}",
                f"- Intent: `{result['intent']}`",
                f"- Confidence: `{result['confidence']}` (`{result['confidence_score']}`)",
                f"- Deliverable: {result['analysis']['requested_deliverable']}",
                f"- Grounding note: {result['grounding_note']}",
                f"- Top source: {result['sources'][0] if result['sources'] else 'none'}",
                "",
            ]
        )
    return "\n".join(lines) + "\n"


def write_scorecard(results):
    with SCORECARD_PATH.open("w", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=["query", "intent", "confidence", "confidence_score", "stakeholder", "deliverable", "top_source"],
        )
        writer.writeheader()
        for result in results:
            writer.writerow(
                {
                    "query": result["query"],
                    "intent": result["intent"],
                    "confidence": result["confidence"],
                    "confidence_score": result["confidence_score"],
                    "stakeholder": result["analysis"]["stakeholder"],
                    "deliverable": result["analysis"]["requested_deliverable"],
                    "top_source": result["sources"][0] if result["sources"] else "",
                }
            )


def main():
    query = " ".join(sys.argv[1:]).strip()
    sample_queries = load_sample_queries()
    if not query:
        query = sample_queries[0]["query"]

    result = answer_query(query)
    batch_results = [answer_query(item["query"]) for item in sample_queries]

    print(build_cli_output(result))
    OUTPUT_PATH.write_text(build_markdown_output(result))
    TRACE_PATH.write_text(json.dumps(result["retrieval_trace"], indent=2))
    PORTFOLIO_PATH.write_text(build_portfolio(batch_results))
    write_scorecard(batch_results)
    print(f"\nGenerated: {OUTPUT_PATH.name}, {TRACE_PATH.name}, {PORTFOLIO_PATH.name}, {SCORECARD_PATH.name}")


if __name__ == "__main__":
    main()
