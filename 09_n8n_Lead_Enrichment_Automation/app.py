import json
from pathlib import Path

BASE_DIR = Path(__file__).parent
LEAD_PATH = BASE_DIR / "sample_lead.json"
WORKFLOW_PATH = BASE_DIR / "workflow.json"


def load_json(path):
    return json.loads(path.read_text())


def score_lead(lead):
    score = 0
    if lead["industry"].lower() in {"banking", "insurance", "industry"}:
        score += 35
    if lead["country"].lower() in {"switzerland", "france", "germany"}:
        score += 20
    if lead["employees"] >= 500:
        score += 20
    if "ai" in lead["signal"].lower() or "automation" in lead["signal"].lower():
        score += 25
    return score


def recommendation(score):
    if score >= 80:
        return "High-priority sales follow-up with tailored AI automation angle."
    if score >= 60:
        return "Qualified lead for discovery call."
    return "Nurture sequence before direct engagement."


def main():
    workflow = load_json(WORKFLOW_PATH)
    lead = load_json(LEAD_PATH)
    score = score_lead(lead)
    print("n8n lead enrichment automation demo")
    print("=" * 34)
    print(f"Workflow: {workflow['name']}")
    print(f"Lead: {lead['company']} | {lead['industry']} | {lead['country']}")
    print(f"Signal: {lead['signal']}")
    print(f"Qualification score: {score}/100")
    print(f"Recommended action: {recommendation(score)}")
    print(f"Workflow nodes: {', '.join(node['name'] for node in workflow['nodes'])}")


if __name__ == "__main__":
    main()
