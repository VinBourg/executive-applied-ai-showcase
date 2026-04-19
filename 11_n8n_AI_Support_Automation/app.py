import json
from pathlib import Path

BASE_DIR = Path(__file__).parent
TICKET_PATH = BASE_DIR / "sample_ticket.json"
WORKFLOW_PATH = BASE_DIR / "workflow.json"


def load_json(path):
    return json.loads(path.read_text())


def classify(ticket):
    text = (ticket["subject"] + " " + ticket["message"]).lower()
    if "transfer" in text or "payment" in text:
        return "payments-support", "high"
    if "login" in text or "access" in text:
        return "access-support", "medium"
    return "general-support", "medium"


def draft_reply(ticket, team):
    return (
        f"Hello {ticket['customer']}, we have routed your request to {team}. "
        "A specialist will review the issue and revert with the next action plan shortly."
    )


def main():
    ticket = load_json(TICKET_PATH)
    workflow = load_json(WORKFLOW_PATH)
    team, priority = classify(ticket)
    print("n8n AI support automation demo")
    print("=" * 31)
    print(f"Workflow: {workflow['name']}")
    print(f"Subject: {ticket['subject']}")
    print(f"Assigned team: {team}")
    print(f"Detected priority: {priority}")
    print(f"Draft reply: {draft_reply(ticket, team)}")
    print(f"Workflow nodes: {', '.join(node['name'] for node in workflow['nodes'])}")


if __name__ == "__main__":
    main()
