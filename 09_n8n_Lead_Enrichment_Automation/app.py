import csv
import json
from pathlib import Path

BASE_DIR = Path(__file__).parent
LEADS_PATH = BASE_DIR / "sample_leads.json"
SINGLE_LEAD_PATH = BASE_DIR / "sample_lead.json"
WORKFLOW_PATH = BASE_DIR / "workflow.json"
REPORT_PATH = BASE_DIR / "qualification_report.md"
SCORECARD_PATH = BASE_DIR / "lead_scorecard.csv"
CRM_PAYLOAD_PATH = BASE_DIR / "crm_sync_payload.json"
SEQUENCE_PLAN_PATH = BASE_DIR / "sequence_plan.md"

INDUSTRY_SCORES = {
    "banking": 22,
    "insurance": 20,
    "industry": 18,
    "retail": 14,
}

COUNTRY_SCORES = {
    "switzerland": 18,
    "france": 16,
    "united states": 18,
}

REGION_BONUS = {
    "new york": 6,
    "boston": 6,
    "zurich": 3,
    "geneva": 3,
    "paris": 3,
    "lyon": 2,
}

DEPARTMENT_SCORES = {
    "operations transformation": 14,
    "claims operations": 13,
    "coo office": 12,
    "revenue operations": 11,
    "shared services": 10,
    "service excellence": 11,
}

SIGNAL_WEIGHTS = {
    "ai": 10,
    "automation": 10,
    "llm": 10,
    "copilot": 9,
    "support": 9,
    "knowledge": 8,
    "reporting": 8,
    "document": 9,
    "sql": 8,
    "agentic": 8,
    "governance": 7,
    "pilot": 7,
    "budget": 6,
    "workflow": 8,
}

OWNER_BY_ANGLE = {
    "AI support automation and ticket routing": "Automation consultant",
    "RAG knowledge assistant and internal copilot": "Applied AI consultant",
    "AI-assisted reporting and decision-support automation": "Analytics and AI consultant",
    "Document intake automation with approvals": "Automation and operations consultant",
    "AI SQL analytics copilot and executive reporting": "Decision-support consultant",
}


def load_json(path):
    return json.loads(path.read_text())


def company_scale_score(employees):
    if employees >= 1500:
        return 18
    if employees >= 900:
        return 15
    if employees >= 500:
        return 12
    if employees >= 250:
        return 9
    return 6


def revenue_potential_score(arr_k):
    if arr_k >= 220:
        return 18
    if arr_k >= 150:
        return 14
    if arr_k >= 100:
        return 10
    return 6


def text_keyword_score(text):
    lowered = text.lower()
    hits = [keyword for keyword in SIGNAL_WEIGHTS if keyword in lowered]
    score = sum(SIGNAL_WEIGHTS[keyword] for keyword in hits)
    return min(score, 34), hits


def urgency_score(text):
    lowered = text.lower()
    score = 0
    if "before" in lowered:
        score += 4
    if "pilot" in lowered:
        score += 4
    if "budget" in lowered:
        score += 3
    if "q3" in lowered or "renewal" in lowered:
        score += 3
    return min(score, 10)


def infer_offer_angle(signal):
    lowered = signal.lower()
    if "document" in lowered or "approval" in lowered:
        return "Document intake automation with approvals"
    if "sql" in lowered or "executive reporting" in lowered:
        return "AI SQL analytics copilot and executive reporting"
    if "support" in lowered:
        return "AI support automation and ticket routing"
    if "knowledge" in lowered or "claims" in lowered or "copilot" in lowered:
        return "RAG knowledge assistant and internal copilot"
    if "reporting" in lowered or "dashboard" in lowered:
        return "AI-assisted reporting and decision-support automation"
    return "AI-assisted reporting and decision-support automation"


def market_label(lead):
    if lead["country"].lower() == "united states":
        return f"USA East ({lead['region']})"
    return f"{lead['country']} ({lead['region']})"


def route_recommendation(score):
    if score >= 88:
        return "Partner-led discovery within 48 hours"
    if score >= 74:
        return "Qualified discovery call with tailored walkthrough"
    return "Nurture with focused use-case brief"


def sequence_theme(angle):
    if angle == "Document intake automation with approvals":
        return "Document workflow, auditability and human-in-the-loop controls"
    if angle == "AI SQL analytics copilot and executive reporting":
        return "Decision support, KPI review and executive operating rhythm"
    if angle == "RAG knowledge assistant and internal copilot":
        return "Internal knowledge access, support enablement and grounded copilots"
    if angle == "AI support automation and ticket routing":
        return "Support routing, backlog control and service efficiency"
    return "Reporting automation and business workflow acceleration"


def evaluate_lead(lead):
    country = lead["country"].lower()
    region = lead["region"].lower()
    department = lead["department"].lower()
    industry_score = INDUSTRY_SCORES.get(lead["industry"].lower(), 10)
    country_score = COUNTRY_SCORES.get(country, 8)
    region_bonus = REGION_BONUS.get(region, 0)
    department_score = DEPARTMENT_SCORES.get(department, 8)
    scale_score = company_scale_score(lead["employees"])
    revenue_score = revenue_potential_score(lead["estimated_arr_k"])
    signal_score, matched_signals = text_keyword_score(lead["signal"])
    urgency = urgency_score(lead["signal"])
    raw_total = (
        industry_score
        + country_score
        + region_bonus
        + department_score
        + scale_score
        + revenue_score
        + signal_score
        + urgency
    )
    total = min(round(raw_total * 0.7, 1), 100)

    angle = infer_offer_angle(lead["signal"])
    owner = OWNER_BY_ANGLE[angle]
    return {
        "company": lead["company"],
        "industry": lead["industry"],
        "country": lead["country"],
        "region": lead["region"],
        "market_label": market_label(lead),
        "employees": lead["employees"],
        "department": lead["department"],
        "estimated_arr_k": lead["estimated_arr_k"],
        "signal": lead["signal"],
        "score": total,
        "matched_signals": matched_signals,
        "offer_angle": angle,
        "recommended_owner": owner,
        "sequence_theme": sequence_theme(angle),
        "next_step": route_recommendation(total),
        "priority": "high" if total >= 88 else "medium" if total >= 74 else "low",
        "score_breakdown": {
            "industry_fit": industry_score,
            "geography_fit": country_score + region_bonus,
            "department_fit": department_score,
            "company_scale": scale_score,
            "revenue_potential": revenue_score,
            "buying_signal": signal_score,
            "urgency": urgency,
        },
    }


def write_scorecard(evaluated_leads):
    with SCORECARD_PATH.open("w", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=[
                "company",
                "market_label",
                "industry",
                "department",
                "score",
                "priority",
                "offer_angle",
                "recommended_owner",
                "next_step",
                "industry_fit",
                "geography_fit",
                "department_fit",
                "company_scale",
                "revenue_potential",
                "buying_signal",
                "urgency",
            ],
        )
        writer.writeheader()
        for lead in evaluated_leads:
            writer.writerow(
                {
                    "company": lead["company"],
                    "market_label": lead["market_label"],
                    "industry": lead["industry"],
                    "department": lead["department"],
                    "score": lead["score"],
                    "priority": lead["priority"],
                    "offer_angle": lead["offer_angle"],
                    "recommended_owner": lead["recommended_owner"],
                    "next_step": lead["next_step"],
                    "industry_fit": lead["score_breakdown"]["industry_fit"],
                    "geography_fit": lead["score_breakdown"]["geography_fit"],
                    "department_fit": lead["score_breakdown"]["department_fit"],
                    "company_scale": lead["score_breakdown"]["company_scale"],
                    "revenue_potential": lead["score_breakdown"]["revenue_potential"],
                    "buying_signal": lead["score_breakdown"]["buying_signal"],
                    "urgency": lead["score_breakdown"]["urgency"],
                }
            )


def write_crm_payload(workflow, evaluated_leads):
    top_leads = evaluated_leads[:3]
    payload = {
        "workflow_name": workflow["name"],
        "business_goal": workflow["business_goal"],
        "sync_batch": [
            {
                "company": lead["company"],
                "market": lead["market_label"],
                "priority": lead["priority"],
                "score": lead["score"],
                "offer_angle": lead["offer_angle"],
                "owner": lead["recommended_owner"],
                "next_step": lead["next_step"],
                "sequence_theme": lead["sequence_theme"],
                "tags": [
                    lead["industry"].lower(),
                    lead["country"].lower().replace(" ", "-"),
                    lead["priority"],
                    "ai-automation",
                ],
            }
            for lead in top_leads
        ],
    }
    CRM_PAYLOAD_PATH.write_text(json.dumps(payload, indent=2))


def write_sequence_plan(evaluated_leads):
    lines = [
        "# Sequence Plan - n8n Lead Enrichment Automation",
        "",
        "This sequence plan turns the qualified lead set into immediate outreach guidance.",
        "",
        "## High-Priority Outreach",
    ]
    high_priority = [lead for lead in evaluated_leads if lead["priority"] == "high"]
    medium_priority = [lead for lead in evaluated_leads if lead["priority"] == "medium"]
    low_priority = [lead for lead in evaluated_leads if lead["priority"] == "low"]

    for lead in high_priority:
        lines.extend(
            [
                f"### {lead['company']}",
                f"- Market: `{lead['market_label']}`",
                f"- Owner: {lead['recommended_owner']}",
                f"- Offer angle: {lead['offer_angle']}",
                f"- First message theme: {lead['sequence_theme']}",
                f"- Immediate next step: {lead['next_step']}",
                "",
            ]
        )

    lines.append("## Medium-Priority Outreach")
    for lead in medium_priority:
        lines.append(
            f"- `{lead['company']}`: send a tailored brief on {lead['sequence_theme'].lower()} and route to {lead['recommended_owner']}."
        )

    lines.append("")
    lines.append("## Low-Priority Outreach")
    for lead in low_priority:
        lines.append(
            f"- `{lead['company']}`: keep in nurture with a lightweight use-case note focused on {lead['offer_angle'].lower()}."
        )

    SEQUENCE_PLAN_PATH.write_text("\n".join(lines) + "\n")


def build_report(workflow, evaluated_leads):
    total_pipeline = round(sum(lead["estimated_arr_k"] for lead in evaluated_leads), 1)
    high_priority = [lead for lead in evaluated_leads if lead["priority"] == "high"]
    lines = [
        "# Qualification Report - n8n Lead Enrichment Automation",
        "",
        "## Workflow",
        workflow["name"],
        "",
        f"Business goal: {workflow['business_goal']}",
        f"Markets covered: {workflow['markets']}",
        f"Estimated opportunity pool: `{total_pipeline}k`",
        f"High-priority leads: `{len(high_priority)}`",
        "",
        "## Ranked Leads",
    ]
    for lead in evaluated_leads:
        lines.extend(
            [
                f"### {lead['company']}",
                f"- Score: `{lead['score']}/100`",
                f"- Priority: `{lead['priority']}`",
                f"- Market: `{lead['market_label']}`",
                f"- Offer angle: {lead['offer_angle']}",
                f"- Recommended owner: {lead['recommended_owner']}",
                f"- Next step: {lead['next_step']}",
                f"- Sequence theme: {lead['sequence_theme']}",
                f"- Signal: {lead['signal']}",
                (
                    "- Score breakdown: "
                    f"industry {lead['score_breakdown']['industry_fit']}, "
                    f"geography {lead['score_breakdown']['geography_fit']}, "
                    f"department {lead['score_breakdown']['department_fit']}, "
                    f"scale {lead['score_breakdown']['company_scale']}, "
                    f"revenue {lead['score_breakdown']['revenue_potential']}, "
                    f"buying signal {lead['score_breakdown']['buying_signal']}, "
                    f"urgency {lead['score_breakdown']['urgency']}"
                ),
                "",
            ]
        )
    lines.append("## Workflow Nodes")
    lines.extend(f"- {node['name']} ({node['type']})" for node in workflow["nodes"])
    lines.extend(
        [
            "",
            "## Operational Outputs",
            "- `lead_scorecard.csv` for full scoring and ownership review.",
            "- `crm_sync_payload.json` for top-priority lead sync into a CRM or orchestration layer.",
            "- `sequence_plan.md` for immediate outreach planning.",
            "",
            "## What This Demonstrates",
            "This example shows how an n8n-style workflow can turn inbound lead data into qualification, prioritization, CRM payloads and concrete routing actions for business teams.",
        ]
    )
    return "\n".join(lines) + "\n"


def run_workflow():
    workflow = load_json(WORKFLOW_PATH)
    leads = load_json(LEADS_PATH)
    evaluated_leads = sorted((evaluate_lead(lead) for lead in leads), key=lambda item: item["score"], reverse=True)
    REPORT_PATH.write_text(build_report(workflow, evaluated_leads))
    write_scorecard(evaluated_leads)
    write_crm_payload(workflow, evaluated_leads)
    write_sequence_plan(evaluated_leads)
    return workflow, evaluated_leads


def main():
    workflow, evaluated_leads = run_workflow()

    print("n8n lead enrichment automation demo")
    print("=" * 34)
    print(f"Workflow: {workflow['name']}")
    print(f"Business goal: {workflow['business_goal']}")
    print("Top qualified leads:")
    for lead in evaluated_leads:
        print(
            f"- {lead['company']}: {lead['score']}/100 | {lead['priority']} priority | "
            f"{lead['offer_angle']} | {lead['recommended_owner']}"
        )
    print(f"Workflow nodes: {', '.join(node['name'] for node in workflow['nodes'])}")
    print(
        "Generated: "
        f"{REPORT_PATH.name}, {SCORECARD_PATH.name}, {CRM_PAYLOAD_PATH.name}, {SEQUENCE_PLAN_PATH.name}"
    )


if __name__ == "__main__":
    main()
