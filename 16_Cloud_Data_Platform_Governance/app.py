import csv
import json
from pathlib import Path

BASE_DIR = Path(__file__).parent
SOURCES_PATH = BASE_DIR / "source_systems.json"
RULES_PATH = BASE_DIR / "quality_rules.json"
MANIFEST_PATH = BASE_DIR / "pipeline_manifest.json"
REPORT_PATH = BASE_DIR / "governance_report.md"
HEALTH_PATH = BASE_DIR / "dataset_health.csv"
CHECKLIST_PATH = BASE_DIR / "pipeline_release_checklist.md"
CONTRACTS_PATH = BASE_DIR / "contracts_registry.csv"


def load_json(path):
    return json.loads(path.read_text())


def clamp_score(value):
    return max(0.0, min(100.0, round(value, 1)))


def add_penalty(penalties, findings, actions, code, score, finding, action):
    penalties.append((code, score))
    findings.append(finding)
    actions.append(action)


def evaluate_dataset(dataset, rules, manifest_lookup):
    thresholds = rules["criticality_thresholds"][dataset["criticality"]]
    penalties = []
    findings = []
    actions = []

    freshness_gap = dataset["freshness_hours"] - thresholds["max_freshness_hours"]
    if freshness_gap > 0:
        add_penalty(
            penalties,
            findings,
            actions,
            "freshness_breach",
            10 + freshness_gap * 3,
            f"Freshness is `{dataset['freshness_hours']}h` versus an allowed `{thresholds['max_freshness_hours']}h`.",
            "Stabilize ingestion scheduling and alert on SLA breach before consumers are impacted.",
        )

    null_gap = dataset["null_rate_pct"] - thresholds["max_null_rate_pct"]
    if null_gap > 0:
        add_penalty(
            penalties,
            findings,
            actions,
            "null_rate_breach",
            8 + null_gap * 6,
            f"Null rate is `{dataset['null_rate_pct']}%` versus a maximum `{thresholds['max_null_rate_pct']}%`.",
            "Add source-side validation and a blocking data quality check for the affected fields.",
        )

    duplicate_gap = dataset["duplicate_rate_pct"] - thresholds["max_duplicate_rate_pct"]
    if duplicate_gap > 0:
        add_penalty(
            penalties,
            findings,
            actions,
            "duplicate_rate_breach",
            6 + duplicate_gap * 10,
            f"Duplicate rate is `{dataset['duplicate_rate_pct']}%` versus a maximum `{thresholds['max_duplicate_rate_pct']}%`.",
            "Introduce idempotency checks and business-key deduplication before publish.",
        )

    test_gap = rules["minimum_test_pass_rate"] - dataset["test_pass_rate"]
    if test_gap > 0:
        add_penalty(
            penalties,
            findings,
            actions,
            "test_pass_rate_below_minimum",
            12 + test_gap * 1.2,
            f"Test pass rate is `{dataset['test_pass_rate']}%`, below the `{rules['minimum_test_pass_rate']}%` floor.",
            "Fix failing tests and block release until the dataset clears the minimum coverage threshold.",
        )

    contract_gap = rules["minimum_contract_coverage_pct"] - dataset["contract_coverage_pct"]
    if contract_gap > 0:
        add_penalty(
            penalties,
            findings,
            actions,
            "contract_coverage_gap",
            6 + contract_gap * 0.5,
            f"Contract coverage is `{dataset['contract_coverage_pct']}%`, below the `{rules['minimum_contract_coverage_pct']}%` target.",
            "Complete schema contracts and publish field-level ownership for remaining unmanaged attributes.",
        )

    drift_gap = dataset["schema_drift_events"] - rules["maximum_schema_drift_events"]
    if drift_gap > 0:
        add_penalty(
            penalties,
            findings,
            actions,
            "schema_drift_excess",
            6 + drift_gap * 5,
            f"Schema drift events total `{dataset['schema_drift_events']}`, above the allowed `{rules['maximum_schema_drift_events']}`.",
            "Lock producer contracts and add pre-release schema diff checks.",
        )

    if dataset["documentation_status"] != rules["required_documentation_status"]:
        add_penalty(
            penalties,
            findings,
            actions,
            "documentation_stale",
            7,
            "Documentation is stale and no longer reflects current production behavior.",
            "Refresh operational runbooks, field definitions and known limitations before the next release.",
        )

    if dataset["lineage_status"] != rules["required_lineage_status"]:
        add_penalty(
            penalties,
            findings,
            actions,
            "lineage_incomplete",
            7,
            "Lineage is incomplete for a dataset consumed by BI, automation or AI workflows.",
            "Complete lineage mapping so downstream teams can trace data provenance and failure impact.",
        )

    if not dataset["owner"]:
        add_penalty(
            penalties,
            findings,
            actions,
            "missing_owner",
            14,
            "No accountable owner is assigned to the dataset.",
            "Assign a named data product owner before production release.",
        )

    if dataset["pii_classification"] != "internal_support_data" and not dataset["masking_in_non_prod"]:
        add_penalty(
            penalties,
            findings,
            actions,
            "non_prod_masking_missing",
            16,
            "Sensitive data is not masked in non-production environments.",
            "Enforce masking or tokenization in lower environments before the dataset is promoted.",
        )

    if dataset["open_incidents"] > 0:
        add_penalty(
            penalties,
            findings,
            actions,
            "open_incidents",
            4 + dataset["open_incidents"] * 3,
            f"There are `{dataset['open_incidents']}` open incidents affecting dataset reliability.",
            "Resolve outstanding incidents and document residual risk for consumers.",
        )

    job = manifest_lookup.get(dataset["dataset"], {})
    if job and job.get("last_release_status") == "warning":
        add_penalty(
            penalties,
            findings,
            actions,
            "release_warning",
            5,
            "The latest release already surfaced warnings for this dataset pipeline.",
            "Keep the next release behind an explicit approval gate and remediation check.",
        )

    score = clamp_score(100 - sum(score for _, score in penalties))
    primary_action = actions[0] if actions else "No immediate remediation required beyond routine monitoring."
    blocking_codes = set(rules["blocking_findings"])
    blockers = [code for code, _ in penalties if code in blocking_codes]

    if score >= 88 and not blockers:
        readiness = "ready"
    elif score >= 75 and len(blockers) <= 1:
        readiness = "ready_with_actions"
    else:
        readiness = "hold"

    return {
        "dataset": dataset["dataset"],
        "domain": dataset["domain"],
        "market_focus": dataset["market_focus"],
        "criticality": dataset["criticality"],
        "owner": dataset["owner"],
        "pii_classification": dataset["pii_classification"],
        "freshness_hours": dataset["freshness_hours"],
        "null_rate_pct": dataset["null_rate_pct"],
        "duplicate_rate_pct": dataset["duplicate_rate_pct"],
        "test_pass_rate": dataset["test_pass_rate"],
        "contract_coverage_pct": dataset["contract_coverage_pct"],
        "schema_drift_events": dataset["schema_drift_events"],
        "documentation_status": dataset["documentation_status"],
        "lineage_status": dataset["lineage_status"],
        "open_incidents": dataset["open_incidents"],
        "sla_hours": dataset["sla_hours"],
        "tables": dataset["tables"],
        "consumers": dataset["consumers"],
        "notes": dataset["notes"],
        "score": score,
        "readiness": readiness,
        "findings": findings,
        "actions": actions,
        "primary_action": primary_action,
        "blocking_codes": blockers,
    }


def build_manifest_lookup(manifest):
    return {job["dataset"]: job for job in manifest["jobs"]}


def write_dataset_health(evaluations):
    with HEALTH_PATH.open("w", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=[
                "dataset",
                "market_focus",
                "domain",
                "criticality",
                "score",
                "readiness",
                "freshness_hours",
                "test_pass_rate",
                "contract_coverage_pct",
                "null_rate_pct",
                "duplicate_rate_pct",
                "schema_drift_events",
                "owner",
                "pii_classification",
                "primary_action",
            ],
        )
        writer.writeheader()
        for item in evaluations:
            writer.writerow(
                {
                    "dataset": item["dataset"],
                    "market_focus": item["market_focus"],
                    "domain": item["domain"],
                    "criticality": item["criticality"],
                    "score": item["score"],
                    "readiness": item["readiness"],
                    "freshness_hours": item["freshness_hours"],
                    "test_pass_rate": item["test_pass_rate"],
                    "contract_coverage_pct": item["contract_coverage_pct"],
                    "null_rate_pct": item["null_rate_pct"],
                    "duplicate_rate_pct": item["duplicate_rate_pct"],
                    "schema_drift_events": item["schema_drift_events"],
                    "owner": item["owner"],
                    "pii_classification": item["pii_classification"],
                    "primary_action": item["primary_action"],
                }
            )


def write_contracts_registry(datasets):
    with CONTRACTS_PATH.open("w", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=[
                "dataset",
                "market_focus",
                "owner",
                "pii_classification",
                "contract_coverage_pct",
                "sla_hours",
                "consumers",
                "documentation_status",
                "lineage_status",
            ],
        )
        writer.writeheader()
        for dataset in datasets:
            writer.writerow(
                {
                    "dataset": dataset["dataset"],
                    "market_focus": dataset["market_focus"],
                    "owner": dataset["owner"],
                    "pii_classification": dataset["pii_classification"],
                    "contract_coverage_pct": dataset["contract_coverage_pct"],
                    "sla_hours": dataset["sla_hours"],
                    "consumers": " | ".join(dataset["consumers"]),
                    "documentation_status": dataset["documentation_status"],
                    "lineage_status": dataset["lineage_status"],
                }
            )


def release_decision(manifest, evaluations):
    control_statuses = [control["status"] for control in manifest["release_controls"]]
    blockers = [item for item in evaluations if item["readiness"] == "hold"]
    warnings = [item for item in evaluations if item["readiness"] == "ready_with_actions"]

    if blockers or "fail" in control_statuses:
        return "hold_release"
    if warnings or "warning" in control_statuses:
        return "release_with_named_actions"
    return "release_ready"


def build_release_checklist(manifest, evaluations):
    decision = release_decision(manifest, evaluations)
    lines = [
        "# Pipeline Release Checklist",
        "",
        f"- Platform: `{manifest['platform_name']}`",
        f"- Version: `{manifest['version']}`",
        f"- Release decision: `{decision}`",
        "",
        "## Platform Controls",
    ]

    for control in manifest["release_controls"]:
        lines.append(f"- `{control['status']}` {control['control']}: {control['detail']}")

    lines.extend(["", "## Dataset Readiness"])
    for item in evaluations:
        lines.append(
            f"- `{item['dataset']}`: `{item['readiness']}` with score `{item['score']}` and action `{item['primary_action']}`"
        )

    lines.extend(["", "## Release Actions"])
    ordered_actions = []
    for item in evaluations:
        if item["actions"]:
            ordered_actions.append((item["score"], item["dataset"], item["actions"][0]))
    for _, dataset, action in sorted(ordered_actions, key=lambda row: row[0]):
        lines.append(f"- `{dataset}`: {action}")

    return "\n".join(lines) + "\n"


def build_governance_report(manifest, evaluations):
    decision = release_decision(manifest, evaluations)
    average_score = round(sum(item["score"] for item in evaluations) / len(evaluations), 1)
    hold_count = sum(item["readiness"] == "hold" for item in evaluations)
    ready_count = sum(item["readiness"] == "ready" for item in evaluations)
    action_count = sum(item["readiness"] == "ready_with_actions" for item in evaluations)

    lines = [
        "# Governance Report - Cloud Data Platform Governance",
        "",
        "This report shows how a data platform can be assessed before trusted consumption by dashboards, analytical products and AI workflows.",
        "",
        "## Platform Snapshot",
        f"- Platform: `{manifest['platform_name']}`",
        f"- Version: `{manifest['version']}`",
        f"- Orchestrator: `{manifest['orchestrator']}`",
        f"- Cloud footprint: {', '.join(manifest['cloud_footprint'])}",
        f"- Average dataset health score: `{average_score}`",
        f"- Release decision: `{decision}`",
        f"- Ready datasets: `{ready_count}`",
        f"- Ready with actions: `{action_count}`",
        f"- Hold datasets: `{hold_count}`",
        "",
        "## Score Overview",
        "| dataset | market | score | readiness | contract_coverage | tests | freshness_hours |",
        "| --- | --- | --- | --- | --- | --- | --- |",
    ]

    for item in sorted(evaluations, key=lambda row: row["score"], reverse=True):
        lines.append(
            f"| {item['dataset']} | {item['market_focus']} | {item['score']} | {item['readiness']} | {item['contract_coverage_pct']}% | {item['test_pass_rate']}% | {item['freshness_hours']} |"
        )

    for item in sorted(evaluations, key=lambda row: row["score"]):
        lines.extend(
            [
                "",
                f"## {item['dataset']}",
                f"- Market focus: `{item['market_focus']}`",
                f"- Domain: `{item['domain']}`",
                f"- Owner: `{item['owner']}`",
                f"- Readiness: `{item['readiness']}`",
                f"- Primary action: {item['primary_action']}",
                f"- Consumers: {', '.join(item['consumers'])}",
                "",
                "### Findings",
            ]
        )
        if item["findings"]:
            lines.extend(f"- {finding}" for finding in item["findings"])
        else:
            lines.append("- No blocking governance issue detected.")

    lines.extend(
        [
            "",
            "## Why this matters",
            "- France: data platform, Power BI and analytics engineering environments increasingly expect cloud delivery discipline, not only modeling skills.",
            "- Switzerland: finance, insurance and regulated AI teams need trusted data products, release controls and clear ownership.",
            "- USA East: enterprise platform teams emphasize governance, permissible use, CI/CD and reliable data pipelines alongside GenAI initiatives.",
            "",
            "## What a recruiter should see quickly",
            "This example makes the repository look closer to real delivery work in cloud data and AI programs: ownership, data quality, release gates, platform controls and downstream business readiness.",
        ]
    )
    return "\n".join(lines) + "\n"


def main():
    datasets = load_json(SOURCES_PATH)
    rules = load_json(RULES_PATH)
    manifest = load_json(MANIFEST_PATH)
    manifest_lookup = build_manifest_lookup(manifest)

    evaluations = [
        evaluate_dataset(dataset, rules, manifest_lookup)
        for dataset in datasets
    ]
    evaluations.sort(key=lambda item: item["score"], reverse=True)

    write_dataset_health(evaluations)
    write_contracts_registry(datasets)
    CHECKLIST_PATH.write_text(build_release_checklist(manifest, evaluations))
    REPORT_PATH.write_text(build_governance_report(manifest, evaluations))

    print("cloud data platform governance demo")
    print("=" * 36)
    print(f"Platform: {manifest['platform_name']} {manifest['version']}")
    print(f"Release decision: {release_decision(manifest, evaluations)}")
    print("Dataset health summary:")
    for item in evaluations:
        print(
            f"- {item['dataset']}: {item['score']}/100 | {item['readiness']} | {item['primary_action']}"
        )
    print(
        f"Generated: {REPORT_PATH.name}, {HEALTH_PATH.name}, {CHECKLIST_PATH.name}, {CONTRACTS_PATH.name}"
    )


if __name__ == "__main__":
    main()
