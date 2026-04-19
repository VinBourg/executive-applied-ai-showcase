import csv
import json
import re
from pathlib import Path

BASE_DIR = Path(__file__).parent
CASES_PATH = BASE_DIR / "evaluation_cases.json"
RUBRIC_PATH = BASE_DIR / "rubric.json"
REPORT_PATH = BASE_DIR / "evaluation_report.md"
SCORECARD_PATH = BASE_DIR / "evaluation_scorecard.csv"

STOPWORDS = {
    "a", "an", "and", "are", "as", "at", "be", "because", "by", "for", "from",
    "in", "is", "it", "of", "on", "or", "that", "the", "this", "to", "we",
    "with", "will", "your", "once", "plus"
}


def load_json(path):
    return json.loads(path.read_text())


def tokenize(text):
    tokens = re.findall(r"[a-zA-Z0-9\-]+", text.lower())
    return [token for token in tokens if token not in STOPWORDS]


def split_sentences(text):
    parts = re.split(r"(?<=[.!?])\s+", text.strip())
    return [part.strip() for part in parts if part.strip()]


def sentence_supported(sentence, context_tokens):
    sentence_tokens = tokenize(sentence)
    if not sentence_tokens:
        return True, 1.0
    overlap = sum(token in context_tokens for token in sentence_tokens)
    coverage = overlap / len(sentence_tokens)
    action_only = any(verb in sentence.lower() for verb in ("review", "assign", "prepare", "confirm", "publish", "validate"))
    if action_only and coverage >= 0.1:
        return True, coverage
    return coverage >= 0.3, coverage


def evaluate_groundedness(case, rubric):
    context_tokens = set()
    for item in case["context"]:
        context_tokens.update(tokenize(item))

    unsupported = []
    weak = []
    overclaims = []

    for sentence in split_sentences(case["model_output"]):
        supported, coverage = sentence_supported(sentence, context_tokens)
        lowered = sentence.lower()
        has_overclaim = any(term in lowered for term in rubric["overclaim_terms"])
        has_numeric_claim = bool(re.search(r"\b\d+\b|\bpercent\b", lowered))
        if has_overclaim:
            overclaims.append(sentence)
        if has_overclaim and (coverage < 0.6 or has_numeric_claim):
            unsupported.append(sentence)
        elif not supported:
            unsupported.append(sentence)
        elif coverage < 0.45:
            weak.append(sentence)

    score = 100 - 35 * len(unsupported) - 10 * len(weak) - 15 * len(overclaims)
    return max(score, 0), unsupported, weak, overclaims


def evaluate_policy(case):
    output_lower = case["model_output"].lower()
    violations = [term for term in case["requirements"]["forbidden_terms"] if term.lower() in output_lower]
    critical = bool(violations)
    score = 100 - 45 * len(violations)
    return max(score, 0), violations, critical


def evaluate_format(case):
    output_lower = case["model_output"].lower()
    missing_required = [term for term in case["requirements"]["required_terms"] if term.lower() not in output_lower]
    sentence_count = len(split_sentences(case["model_output"]))
    excess_sentences = max(sentence_count - case["requirements"]["max_sentences"], 0)
    score = 100 - 20 * len(missing_required) - 10 * excess_sentences
    return max(score, 0), missing_required, sentence_count


def evaluate_actionability(case, rubric):
    if not case["requirements"]["needs_actions"]:
        return 100, []
    output_lower = case["model_output"].lower()
    hits = [verb for verb in rubric["action_verbs"] if verb in output_lower]
    score = min(100, len(set(hits)) * 35)
    return score, sorted(set(hits))


def overall_score(scores, weights):
    return round(
        scores["groundedness"] * weights["groundedness"]
        + scores["policy"] * weights["policy"]
        + scores["format"] * weights["format"]
        + scores["actionability"] * weights["actionability"],
        1,
    )


def decide(case_result, thresholds):
    if case_result["critical_policy_violation"]:
        return "block", "Use a safe fallback response and route to human approval."
    if case_result["groundedness"] < thresholds["groundedness_floor"] or case_result["unsupported_claims"]:
        return "fallback_to_human_review", "Do not send as-is. Ask for human review or regenerate from grounded context."
    if case_result["overall_score"] >= thresholds["approve"]:
        return "approve", "Safe to use with routine spot checks."
    if case_result["overall_score"] >= thresholds["approve_with_review"]:
        return "approve_with_review", "Usable after a quick reviewer check."
    return "fallback_to_human_review", "Regenerate or review manually before use."


def evaluate_case(case, rubric):
    groundedness, unsupported, weak, overclaims = evaluate_groundedness(case, rubric)
    policy, violations, critical = evaluate_policy(case)
    format_score, missing_required, sentence_count = evaluate_format(case)
    actionability, action_hits = evaluate_actionability(case, rubric)

    scores = {
        "groundedness": groundedness,
        "policy": policy,
        "format": format_score,
        "actionability": actionability,
    }

    result = {
        "case_id": case["case_id"],
        "use_case": case["use_case"],
        "scores": scores,
        "groundedness": groundedness,
        "policy": policy,
        "format": format_score,
        "actionability": actionability,
        "unsupported_claims": unsupported,
        "weak_claims": weak,
        "overclaims": overclaims,
        "policy_violations": violations,
        "critical_policy_violation": critical,
        "missing_required_terms": missing_required,
        "sentence_count": sentence_count,
        "action_hits": action_hits,
    }
    result["overall_score"] = overall_score(scores, rubric["weights"])
    result["decision"], result["fallback_action"] = decide(result, rubric["thresholds"])
    return result


def write_scorecard(results):
    with SCORECARD_PATH.open("w", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=[
                "case_id",
                "use_case",
                "overall_score",
                "decision",
                "groundedness",
                "policy",
                "format",
                "actionability",
                "unsupported_claims",
                "policy_violations",
                "missing_required_terms",
            ],
        )
        writer.writeheader()
        for result in results:
            writer.writerow(
                {
                    "case_id": result["case_id"],
                    "use_case": result["use_case"],
                    "overall_score": result["overall_score"],
                    "decision": result["decision"],
                    "groundedness": result["groundedness"],
                    "policy": result["policy"],
                    "format": result["format"],
                    "actionability": result["actionability"],
                    "unsupported_claims": len(result["unsupported_claims"]),
                    "policy_violations": len(result["policy_violations"]),
                    "missing_required_terms": len(result["missing_required_terms"]),
                }
            )


def build_summary(results):
    counts = {}
    for result in results:
        counts[result["decision"]] = counts.get(result["decision"], 0) + 1
    return counts


def build_report(cases, results, rubric):
    case_map = {case["case_id"]: case for case in cases}
    summary = build_summary(results)
    lines = [
        "# Evaluation Report - LLM Evaluation Guardrails",
        "",
        "This document shows how business-oriented LLM outputs can be scored, flagged and routed through explicit guardrails.",
        "",
        "## Decision Summary",
    ]
    for decision, count in sorted(summary.items()):
        lines.append(f"- `{decision}`: {count}")
    lines.extend(
        [
            "",
            "## Rubric Snapshot",
            f"- Approve threshold: `{rubric['thresholds']['approve']}`",
            f"- Review threshold: `{rubric['thresholds']['approve_with_review']}`",
            f"- Groundedness floor: `{rubric['thresholds']['groundedness_floor']}`",
            "",
            "## Score Overview",
            "| case_id | decision | overall_score | groundedness | policy | format | actionability |",
            "| --- | --- | --- | --- | --- | --- | --- |",
        ]
    )
    for result in results:
        lines.append(
            f"| {result['case_id']} | {result['decision']} | {result['overall_score']} | {result['groundedness']} | {result['policy']} | {result['format']} | {result['actionability']} |"
        )

    for result in results:
        case = case_map[result["case_id"]]
        lines.extend(
            [
                "",
                f"## {result['case_id']}",
                f"**Use case:** {result['use_case']}",
                f"**Prompt:** {case['prompt']}",
                f"**Decision:** `{result['decision']}`",
                f"**Fallback action:** {result['fallback_action']}",
                "",
                "### Context",
            ]
        )
        lines.extend(f"- {item}" for item in case["context"])
        lines.extend(
            [
                "",
                "### Model Output",
                case["model_output"],
                "",
                "### Findings",
                f"- Unsupported claims: {len(result['unsupported_claims'])}",
                f"- Policy violations: {len(result['policy_violations'])}",
                f"- Missing required terms: {len(result['missing_required_terms'])}",
                f"- Action verbs detected: {', '.join(result['action_hits']) if result['action_hits'] else 'none'}",
            ]
        )
        if result["unsupported_claims"]:
            lines.append("- Unsupported claim details:")
            lines.extend(f"  - {item}" for item in result["unsupported_claims"])
        if result["policy_violations"]:
            lines.append(f"- Policy violations: {', '.join(result['policy_violations'])}")
        if result["missing_required_terms"]:
            lines.append(f"- Missing required terms: {', '.join(result['missing_required_terms'])}")
        if result["overclaims"]:
            lines.append(f"- Overclaiming language: {'; '.join(result['overclaims'])}")
        lines.extend(
            [
                "",
                "### Scores",
                f"- Groundedness: `{result['groundedness']}`",
                f"- Policy: `{result['policy']}`",
                f"- Format: `{result['format']}`",
                f"- Actionability: `{result['actionability']}`",
                f"- Overall: `{result['overall_score']}`",
            ]
        )
    lines.extend(
        [
            "",
            "## What This Demonstrates",
            "This example shows how LLM delivery can be evaluated as a controlled system with explicit approval rules instead of relying on intuition alone.",
        ]
    )
    return "\n".join(lines) + "\n"


def main():
    cases = load_json(CASES_PATH)
    rubric = load_json(RUBRIC_PATH)
    results = [evaluate_case(case, rubric) for case in cases]
    write_scorecard(results)
    REPORT_PATH.write_text(build_report(cases, results, rubric))

    print("LLM evaluation guardrails demo")
    print("=" * 30)
    for result in results:
        print(
            f"- {result['case_id']}: {result['decision']} | overall {result['overall_score']} | "
            f"groundedness {result['groundedness']} | policy {result['policy']}"
        )
    print(f"Generated: {REPORT_PATH.name}, {SCORECARD_PATH.name}")


if __name__ == "__main__":
    main()
