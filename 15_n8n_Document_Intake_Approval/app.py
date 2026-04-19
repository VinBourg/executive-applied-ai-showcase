import csv
import json
import re
from pathlib import Path

BASE_DIR = Path(__file__).parent
DOCUMENTS_PATH = BASE_DIR / "incoming_documents.json"
WORKFLOW_PATH = BASE_DIR / "workflow.json"
REPORT_PATH = BASE_DIR / "intake_approval_report.md"
QUEUE_PATH = BASE_DIR / "approval_queue.csv"

REQUIRED_FIELDS = {
    "invoice": ["vendor", "invoice_id", "amount_eur", "due_date"],
    "onboarding_request": ["company", "requested_go_live", "requested_users", "sponsor", "scope"],
    "contract_change": ["counterparty", "effective_date", "change_summary", "business_owner"],
}

ROUTE_BY_TYPE = {
    "invoice": "finance-operations",
    "onboarding_request": "customer-operations",
    "contract_change": "legal-operations",
}


def load_json(path):
    return json.loads(path.read_text())


def extract_value(text, label):
    pattern = rf"{re.escape(label)}:\s*(.+)"
    match = re.search(pattern, text, flags=re.IGNORECASE)
    return match.group(1).strip() if match else ""


def classify_document(text):
    lowered = text.lower()
    if "invoice" in lowered:
        return "invoice"
    if "onboarding request" in lowered:
        return "onboarding_request"
    if "contract change" in lowered:
        return "contract_change"
    return "unknown"


def extract_fields(document_type, text):
    if document_type == "invoice":
        return {
            "vendor": extract_value(text, "Vendor"),
            "invoice_id": extract_value(text, "Invoice ID"),
            "amount_eur": extract_value(text, "Amount EUR"),
            "due_date": extract_value(text, "Due Date"),
            "purchase_order": extract_value(text, "Purchase Order"),
            "cost_center": extract_value(text, "Cost Center"),
            "summary": extract_value(text, "Summary"),
        }
    if document_type == "onboarding_request":
        return {
            "company": extract_value(text, "Company"),
            "requested_go_live": extract_value(text, "Requested Go-Live"),
            "requested_users": extract_value(text, "Requested Users"),
            "sponsor": extract_value(text, "Sponsor"),
            "scope": extract_value(text, "Scope"),
            "data_sensitivity": extract_value(text, "Data Sensitivity"),
        }
    if document_type == "contract_change":
        return {
            "counterparty": extract_value(text, "Counterparty"),
            "effective_date": extract_value(text, "Effective Date"),
            "change_summary": extract_value(text, "Change Summary"),
            "business_owner": extract_value(text, "Business Owner"),
            "value_impact_eur": extract_value(text, "Value Impact EUR"),
        }
    return {}


def numeric_value(raw_value):
    if raw_value is None:
        return 0.0
    cleaned = str(raw_value).replace(",", "").strip()
    return float(cleaned) if cleaned else 0.0


def missing_fields(document_type, fields):
    required = REQUIRED_FIELDS.get(document_type, [])
    return [field for field in required if not fields.get(field)]


def determine_decision(document_type, fields, missing):
    if document_type == "unknown":
        return "hold_for_classification", "document-control", "Unknown document type, route for manual triage."
    if missing:
        return "hold_missing_data", "document-control", "Missing required fields before approval routing."

    if document_type == "invoice":
        amount = numeric_value(fields["amount_eur"])
        if amount <= 5000 and fields.get("purchase_order"):
            return "auto_approved", "finance-operations", "Low-value invoice with purchase order, ready for automatic posting."
        if amount > 5000 and fields.get("purchase_order"):
            return "manager_approval", "finance-manager", "High-value invoice requires manager approval before posting."
        return "manual_review", "finance-operations", "Invoice missing purchase order evidence, route for finance review."

    if document_type == "onboarding_request":
        users = int(numeric_value(fields["requested_users"]))
        sensitivity = fields.get("data_sensitivity", "").lower()
        if users <= 20 and sensitivity in {"low", "medium"}:
            return "operations_approval", "customer-operations", "Scoped onboarding request ready for operations approval."
        return "manual_review", "solution-operations", "Onboarding request requires additional scoping before approval."

    if document_type == "contract_change":
        impact = numeric_value(fields.get("value_impact_eur"))
        if impact >= 100000:
            return "legal_and_business_approval", "legal-operations", "High-value contract change requires legal and business approval."
        return "legal_review", "legal-operations", "Contract change requires legal review before acceptance."

    return "manual_review", "document-control", "Fallback manual review path."


def evaluate_document(document):
    document_type = classify_document(document["raw_text"])
    fields = extract_fields(document_type, document["raw_text"])
    missing = missing_fields(document_type, fields)
    decision, route_team, reason = determine_decision(document_type, fields, missing)
    return {
        "document_name": document["document_name"],
        "source": document["source"],
        "sender": document["sender"],
        "received_at": document["received_at"],
        "document_type": document_type,
        "route_team": route_team,
        "decision": decision,
        "missing_fields": missing,
        "reason": reason,
        "fields": fields,
    }


def write_queue(results):
    with QUEUE_PATH.open("w", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=[
                "document_name",
                "document_type",
                "decision",
                "route_team",
                "sender",
                "received_at",
                "missing_fields",
            ],
        )
        writer.writeheader()
        for result in results:
            writer.writerow(
                {
                    "document_name": result["document_name"],
                    "document_type": result["document_type"],
                    "decision": result["decision"],
                    "route_team": result["route_team"],
                    "sender": result["sender"],
                    "received_at": result["received_at"],
                    "missing_fields": ", ".join(result["missing_fields"]),
                }
            )


def build_summary(results):
    summary = {}
    for result in results:
        summary[result["decision"]] = summary.get(result["decision"], 0) + 1
    return summary


def build_report(workflow, results):
    summary = build_summary(results)
    lines = [
        "# Intake Approval Report - n8n Document Intake Approval",
        "",
        f"## Workflow",
        workflow["name"],
        "",
        f"Business goal: {workflow['business_goal']}",
        "",
        "## Decision Summary",
    ]
    for decision, count in sorted(summary.items()):
        lines.append(f"- `{decision}`: {count}")
    lines.append("")
    lines.append("## Processed Documents")
    lines.append("| document_name | type | decision | route_team | missing_fields |")
    lines.append("| --- | --- | --- | --- | --- |")
    for result in results:
        missing = ", ".join(result["missing_fields"]) if result["missing_fields"] else "-"
        lines.append(
            f"| {result['document_name']} | {result['document_type']} | {result['decision']} | {result['route_team']} | {missing} |"
        )
    lines.append("")
    for result in results:
        lines.extend(
            [
                f"## {result['document_name']}",
                f"- Source: {result['source']}",
                f"- Sender: {result['sender']}",
                f"- Received at: {result['received_at']}",
                f"- Type: `{result['document_type']}`",
                f"- Decision: `{result['decision']}`",
                f"- Route team: `{result['route_team']}`",
                f"- Reason: {result['reason']}",
                "",
                "### Extracted Fields",
            ]
        )
        for key, value in result["fields"].items():
            lines.append(f"- {key}: {value or '[missing]'}")
        lines.append("")
    lines.append("## Workflow Nodes")
    lines.extend(f"- {node['name']} ({node['type']})" for node in workflow["nodes"])
    lines.append("")
    lines.append("## What This Demonstrates")
    lines.append(
        "This example shows how an n8n-style workflow can combine document classification, field extraction, rule-based validation and human approval without pretending that every document should be auto-approved."
    )
    return "\n".join(lines) + "\n"


def main():
    documents = load_json(DOCUMENTS_PATH)
    workflow = load_json(WORKFLOW_PATH)
    results = [evaluate_document(document) for document in documents]
    write_queue(results)
    REPORT_PATH.write_text(build_report(workflow, results))

    print("n8n document intake approval demo")
    print("=" * 33)
    print(f"Workflow: {workflow['name']}")
    for result in results:
        missing = ", ".join(result["missing_fields"]) if result["missing_fields"] else "none"
        print(
            f"- {result['document_name']}: {result['decision']} | route {result['route_team']} | missing {missing}"
        )
    print(f"Generated: {REPORT_PATH.name}, {QUEUE_PATH.name}")


if __name__ == "__main__":
    main()
