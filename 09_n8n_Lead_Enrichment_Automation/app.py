import json
from pathlib import Path

BASE_DIR = Path(__file__).parent
LEADS_PATH = BASE_DIR / "sample_leads.json"
WORKFLOW_PATH = BASE_DIR / "workflow.json"
REPORT_PATH = BASE_DIR / "qualification_report.md"

INDUSTRY_SCORES = {
    "banking": 22,
    "insurance": 18,
    "industry": 16,
    "retail": 10,
}

COUNTRY_SCORES = {
    "switzerland": 16,
    "france": 14,
    "germany": 14,
    "belgium": 10,
}

SIGNAL_WEIGHTS = {
    "ai": 12,
    "automation": 12,
    "llm": 12,
    "copilot": 10,
    "support": 9,
    "knowledge": 9,
    "reporting": 8,
    "pilot": 8,
    "urgent": 8,
}


def load_json(path):
    return json.loads(path.read_text())


def company_scale_score(employees):
    if employees >= 1000:
        return 18
    if employees >= 500:
        return 14
    if employees >= 200:
        return 10
    return 6


def text_keyword_score(text):
    lowered = text.lower()
    hits = [keyword for keyword in SIGNAL_WEIGHTS if keyword in lowered]
    score = sum(SIGNAL_WEIGHTS[keyword] for keyword in hits)
    return min(score, 32), hits


def infer_offer_angle(signal):
    lowered = signal.lower()
    if "support" in lowered:
        return "AI support automation and ticket routing"
    if "knowledge" in lowered or "faq" in lowered:
        return "RAG knowledge assistant and internal copilot"
    if "reporting" in lowered or "dashboard" in lowered:
        return "AI-assisted reporting and decision-support automation"
    return "Lead enrichment and workflow automation"


def route_recommendation(score):
    if score >= 78:
        return "Executive follow-up within 48 hours"
    if score >= 60:
        return "Qualified discovery call"
    return "Nurture sequence with lightweight content"


def evaluate_lead(lead):
    industry_score = INDUSTRY_SCORES.get(lead["industry"].lower(), 8)
    country_score = COUNTRY_SCORES.get(lead["country"].lower(), 6)
    scale_score = company_scale_score(lead["employees"])
    signal_score, matched_signals = text_keyword_score(lead["signal"])
    total = min(industry_score + country_score + scale_score + signal_score, 100)

    return {
        "company": lead["company"],
        "industry": lead["industry"],
        "country": lead["country"],
        "employees": lead["employees"],
        "signal": lead["signal"],
        "score": total,
        "matched_signals": matched_signals,
        "offer_angle": infer_offer_angle(lead["signal"]),
        "next_step": route_recommendation(total),
        "priority": "high" if total >= 78 else "medium" if total >= 60 else "low",
        "score_breakdown": {
            "industry_fit": industry_score,
            "geography_fit": country_score,
            "company_scale": scale_score,
            "buying_signal": signal_score,
        },
    }


def build_report(workflow, evaluated_leads):
    lines = [
        "# Qualification Report - n8n Lead Enrichment Automation",
        "",
        f"## Workflow",
        workflow["name"],
        "",
        f"Business goal: {workflow['business_goal']}",
        "",
        "## Ranked Leads",
    ]
    for lead in evaluated_leads:
        lines.extend(
            [
                f"### {lead['company']}",
                f"- Score: `{lead['score']}/100`",
                f"- Priority: `{lead['priority']}`",
                f"- Offer angle: {lead['offer_angle']}",
                f"- Next step: {lead['next_step']}",
                f"- Signal: {lead['signal']}",
                f"- Score breakdown: industry {lead['score_breakdown']['industry_fit']}, geography {lead['score_breakdown']['geography_fit']}, scale {lead['score_breakdown']['company_scale']}, buying signal {lead['score_breakdown']['buying_signal']}",
                "",
            ]
        )
    lines.append("## Workflow Nodes")
    lines.extend(f"- {node['name']} ({node['type']})" for node in workflow["nodes"])
    lines.append("")
    lines.append("## What This Demonstrates")
    lines.append(
        "This example shows how an n8n-style workflow can turn inbound lead data into qualification, prioritization and concrete routing actions for business teams."
    )
    return "\n".join(lines) + "\n"


def main():
    workflow = load_json(WORKFLOW_PATH)
    leads = load_json(LEADS_PATH)
    evaluated_leads = sorted((evaluate_lead(lead) for lead in leads), key=lambda item: item["score"], reverse=True)
    REPORT_PATH.write_text(build_report(workflow, evaluated_leads))

    print("n8n lead enrichment automation demo")
    print("=" * 34)
    print(f"Workflow: {workflow['name']}")
    print(f"Business goal: {workflow['business_goal']}")
    print("Top qualified leads:")
    for lead in evaluated_leads:
        print(f"- {lead['company']}: {lead['score']}/100 | {lead['priority']} priority | {lead['offer_angle']}")
    print(f"Workflow nodes: {', '.join(node['name'] for node in workflow['nodes'])}")
    print(f"Generated: {REPORT_PATH.name}")


if __name__ == "__main__":
    main()
