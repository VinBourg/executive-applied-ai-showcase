import csv
import json
from collections import defaultdict
from pathlib import Path

BASE_DIR = Path(__file__).parent
ACTIVITY_PATH = BASE_DIR / "daily_sales_activity.csv"
SOURCE_REGISTRY_PATH = BASE_DIR / "source_registry.json"
METRIC_CATALOG_PATH = BASE_DIR / "metric_catalog.json"

REPORT_PATH = BASE_DIR / "analytics_engineering_report.md"
TRUSTED_METRICS_PATH = BASE_DIR / "trusted_metrics.csv"
SEMANTIC_LAYER_PATH = BASE_DIR / "semantic_layer_spec.json"
CONTRACT_STATUS_PATH = BASE_DIR / "data_contract_status.csv"
RELEASE_BRIEF_PATH = BASE_DIR / "bi_release_brief.md"


def load_activity():
    rows = []
    with ACTIVITY_PATH.open(newline="") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            rows.append(
                {
                    "business_date": row["business_date"],
                    "market": row["market"],
                    "channel": row["channel"],
                    "customer_segment": row["customer_segment"],
                    "orders_created": int(row["orders_created"]),
                    "orders_fulfilled": int(row["orders_fulfilled"]),
                    "gross_revenue_k": float(row["gross_revenue_k"]),
                    "refunds_k": float(row["refunds_k"]),
                    "active_customers": int(row["active_customers"]),
                    "support_cases": int(row["support_cases"]),
                }
            )
    return rows


def load_sources():
    return json.loads(SOURCE_REGISTRY_PATH.read_text())


def load_metric_catalog():
    return json.loads(METRIC_CATALOG_PATH.read_text())


def accumulate(target, row):
    for field in (
        "orders_created",
        "orders_fulfilled",
        "gross_revenue_k",
        "refunds_k",
        "active_customers",
        "support_cases",
    ):
        target[field] += row[field]


def summarise_group(values):
    net_revenue_k = round(values["gross_revenue_k"] - values["refunds_k"], 1)
    fulfillment_rate_pct = round((values["orders_fulfilled"] / values["orders_created"]) * 100, 1)
    revenue_per_active_customer_k = round(net_revenue_k / values["active_customers"], 2)
    support_case_rate_pct = round((values["support_cases"] / values["orders_fulfilled"]) * 100, 1)
    return {
        "orders_created": values["orders_created"],
        "orders_fulfilled": values["orders_fulfilled"],
        "gross_revenue_k": round(values["gross_revenue_k"], 1),
        "refunds_k": round(values["refunds_k"], 1),
        "net_revenue_k": net_revenue_k,
        "active_customers": values["active_customers"],
        "support_cases": values["support_cases"],
        "fulfillment_rate_pct": fulfillment_rate_pct,
        "revenue_per_active_customer_k": revenue_per_active_customer_k,
        "support_case_rate_pct": support_case_rate_pct,
    }


def build_metric_views(activity_rows):
    overall_accumulator = defaultdict(float)
    by_market_accumulator = defaultdict(lambda: defaultdict(float))

    for row in activity_rows:
        accumulate(overall_accumulator, row)
        accumulate(by_market_accumulator[row["market"]], row)

    overall = summarise_group(overall_accumulator)
    by_market = {market: summarise_group(values) for market, values in by_market_accumulator.items()}
    return overall, by_market


def source_signal(source):
    freshness_ratio = source["freshness_hours"] / source["freshness_sla_hours"]
    if source["contract_status"] != "active":
        return "watch"
    if source["tests_pass_rate"] < 0.95:
        return "watch"
    if freshness_ratio > 1.25:
        return "watch"
    return "trusted"


def describe_source_issue(source):
    issues = []
    if source["contract_status"] != "active":
        issues.append(f"contract status is {source['contract_status']}")
    if source["tests_pass_rate"] < 0.95:
        issues.append(f"tests pass rate is {source['tests_pass_rate']:.2f}")
    if source["freshness_hours"] > source["freshness_sla_hours"]:
        issues.append(f"freshness is {source['freshness_hours']}h for a {source['freshness_sla_hours']}h SLA")
    return ", ".join(issues) if issues else "no issue"


def metric_value(summary, metric_name):
    return summary[metric_name]


def metric_trust(metric, source_lookup):
    statuses = [source_signal(source_lookup[name]) for name in metric["dependencies"]]
    return "trusted" if all(status == "trusted" for status in statuses) else "watch"


def build_trusted_metrics(metric_catalog, source_lookup, overall, by_market):
    rows = []
    for metric in metric_catalog["metrics"]:
        trust = metric_trust(metric, source_lookup)
        rows.append(
            {
                "metric_name": metric["name"],
                "label": metric["label"],
                "grain": "portfolio",
                "segment": "all_markets",
                "value": metric_value(overall, metric["name"]),
                "unit": metric["unit"],
                "owner": metric["owner"],
                "trust_status": trust,
                "primary_use": metric["primary_use"],
            }
        )
        if metric.get("publish_by_market"):
            for market, summary in by_market.items():
                rows.append(
                    {
                        "metric_name": metric["name"],
                        "label": metric["label"],
                        "grain": "market",
                        "segment": market,
                        "value": metric_value(summary, metric["name"]),
                        "unit": metric["unit"],
                        "owner": metric["owner"],
                        "trust_status": trust,
                        "primary_use": metric["primary_use"],
                    }
                )
    return rows


def write_trusted_metrics(rows):
    with TRUSTED_METRICS_PATH.open("w", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=[
                "metric_name",
                "label",
                "grain",
                "segment",
                "value",
                "unit",
                "owner",
                "trust_status",
                "primary_use",
            ],
        )
        writer.writeheader()
        writer.writerows(rows)


def build_contract_status_rows(sources):
    rows = []
    for source in sources:
        rows.append(
            {
                "source_name": source["source_name"],
                "owner": source["owner"],
                "contract_status": source["contract_status"],
                "freshness_hours": source["freshness_hours"],
                "freshness_sla_hours": source["freshness_sla_hours"],
                "tests_pass_rate": source["tests_pass_rate"],
                "downstream_consumers": ", ".join(source["downstream_consumers"]),
                "release_signal": source_signal(source),
                "issue_summary": describe_source_issue(source),
            }
        )
    return rows


def write_contract_status(rows):
    with CONTRACT_STATUS_PATH.open("w", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=[
                "source_name",
                "owner",
                "contract_status",
                "freshness_hours",
                "freshness_sla_hours",
                "tests_pass_rate",
                "downstream_consumers",
                "release_signal",
                "issue_summary",
            ],
        )
        writer.writeheader()
        writer.writerows(rows)


def release_decision(metric_rows):
    watched_metrics = [row for row in metric_rows if row["grain"] == "portfolio" and row["trust_status"] == "watch"]
    return "conditional release" if watched_metrics else "ready for release"


def build_semantic_layer(metric_catalog, sources, metric_rows, overall):
    trust_lookup = {
        row["metric_name"]: row["trust_status"]
        for row in metric_rows
        if row["grain"] == "portfolio"
    }
    return {
        "domain": "Commercial performance and service quality",
        "semantic_layer_style": "dbt-ready metric layer with BI and AI consumption notes",
        "grain": ["day", "market", "channel", "customer_segment"],
        "dimensions": [
            {"name": "business_date", "type": "date"},
            {"name": "market", "type": "string"},
            {"name": "channel", "type": "string"},
            {"name": "customer_segment", "type": "string"},
        ],
        "metrics": [
            {
                "name": metric["name"],
                "label": metric["label"],
                "formula": metric["formula"],
                "unit": metric["unit"],
                "owner": metric["owner"],
                "dependencies": metric["dependencies"],
                "primary_use": metric["primary_use"],
                "publication_grains": ["portfolio", "market"] if metric.get("publish_by_market") else ["portfolio"],
                "trust_status": trust_lookup[metric["name"]],
            }
            for metric in metric_catalog["metrics"]
        ],
        "source_contracts": [
            {
                "source_name": source["source_name"],
                "owner": source["owner"],
                "contract_status": source["contract_status"],
                "tests_pass_rate": source["tests_pass_rate"],
                "freshness_hours": source["freshness_hours"],
                "freshness_sla_hours": source["freshness_sla_hours"],
                "release_signal": source_signal(source),
            }
            for source in sources
        ],
        "current_portfolio_snapshot": overall,
    }


def build_report(metric_catalog, overall, by_market, contract_rows, metric_rows):
    trusted = [row for row in metric_rows if row["grain"] == "portfolio" and row["trust_status"] == "trusted"]
    watch = [row for row in metric_rows if row["grain"] == "portfolio" and row["trust_status"] == "watch"]
    watched_sources = [row for row in contract_rows if row["release_signal"] == "watch"]
    top_market = max(by_market.items(), key=lambda item: item[1]["net_revenue_k"])

    lines = [
        "# Analytics Engineering Report - Modern Data Stack Readiness",
        "",
        "This example shows how an analytics-engineering layer can turn raw commercial activity into trusted metrics, semantic definitions and BI-ready release notes.",
        "",
        "## Executive View",
        f"- Release status: `{release_decision(metric_rows)}`",
        f"- Portfolio net revenue: `{overall['net_revenue_k']}k`",
        f"- Portfolio fulfillment rate: `{overall['fulfillment_rate_pct']}%`",
        f"- Highest-revenue market in this sample: `{top_market[0]}` with `{top_market[1]['net_revenue_k']}k` net revenue",
        "",
        "## Trusted Metric Layer",
    ]
    lines.extend(
        f"- `{row['label']}` is publishable at portfolio level with status `{row['trust_status']}`."
        for row in trusted
    )
    lines.extend(
        [
            "",
            "## Metrics Under Watch",
        ]
    )
    if watch:
        lines.extend(
            f"- `{row['label']}` remains under watch because one of its upstream sources is not fully release-ready."
            for row in watch
        )
    else:
        lines.append("- No metric is currently under watch.")

    lines.extend(
        [
            "",
            "## Source Controls",
        ]
    )
    for row in contract_rows:
        lines.append(
            f"- `{row['source_name']}` owned by `{row['owner']}` is `{row['release_signal']}`: {row['issue_summary']}."
        )

    lines.extend(
        [
            "",
            "## Why This Matters",
            "- Trusted metrics reduce dashboard churn and executive debate over definitions.",
            "- A semantic layer gives BI, analytics and AI teams a common metric contract.",
            "- Release notes clarify what is safe to expose broadly and what still needs remediation.",
            "",
            "## Recommended Next Actions",
        ]
    )

    if watched_sources:
        for row in watched_sources:
            lines.append(
                f"- Close the gap on `{row['source_name']}` by stabilising freshness and contract coverage before promoting dependent metrics."
            )
    lines.extend(
        [
            "- Publish the trusted metrics table as the default metric layer for dashboards and copilots.",
            "- Keep semantic definitions versioned so BI and AI consumers do not drift apart.",
        ]
    )
    return "\n".join(lines) + "\n"


def build_release_brief(overall, metric_rows, contract_rows):
    watched_metrics = [row["label"] for row in metric_rows if row["grain"] == "portfolio" and row["trust_status"] == "watch"]
    trusted_metrics = [row["label"] for row in metric_rows if row["grain"] == "portfolio" and row["trust_status"] == "trusted"]
    watched_sources = [row["source_name"] for row in contract_rows if row["release_signal"] == "watch"]

    lines = [
        "# BI Release Brief - Trusted Metrics Layer",
        "",
        f"**Release decision:** `{release_decision(metric_rows)}`",
        "",
        "## Cleared For Broad BI Consumption",
    ]
    lines.extend(f"- {metric}" for metric in trusted_metrics)
    lines.extend(
        [
            "",
            "## Use With Watch Status",
        ]
    )
    if watched_metrics:
        lines.extend(f"- {metric}" for metric in watched_metrics)
    else:
        lines.append("- None")

    lines.extend(
        [
            "",
            "## Source Remediation Queue",
        ]
    )
    if watched_sources:
        lines.extend(f"- {source}" for source in watched_sources)
    else:
        lines.append("- No open source issues.")

    lines.extend(
        [
            "",
            "## Leadership Note",
            f"- Current portfolio net revenue stands at `{overall['net_revenue_k']}k` with `{overall['fulfillment_rate_pct']}%` fulfillment.",
            "- The metric layer is strong enough for executive reporting, provided watched sources remain clearly flagged.",
        ]
    )
    return "\n".join(lines) + "\n"


def main():
    activity_rows = load_activity()
    sources = load_sources()
    metric_catalog = load_metric_catalog()
    source_lookup = {source["source_name"]: source for source in sources}

    overall, by_market = build_metric_views(activity_rows)
    metric_rows = build_trusted_metrics(metric_catalog, source_lookup, overall, by_market)
    contract_rows = build_contract_status_rows(sources)
    semantic_layer = build_semantic_layer(metric_catalog, sources, metric_rows, overall)

    write_trusted_metrics(metric_rows)
    write_contract_status(contract_rows)
    REPORT_PATH.write_text(build_report(metric_catalog, overall, by_market, contract_rows, metric_rows))
    RELEASE_BRIEF_PATH.write_text(build_release_brief(overall, metric_rows, contract_rows))
    SEMANTIC_LAYER_PATH.write_text(json.dumps(semantic_layer, indent=2))

    print("Modern data stack analytics engineering demo")
    print("=" * 43)
    print(f"Release decision: {release_decision(metric_rows)}")
    print(f"Portfolio net revenue: {overall['net_revenue_k']}k")
    print(f"Trusted metrics file: {TRUSTED_METRICS_PATH.name}")
    print(f"Contract status file: {CONTRACT_STATUS_PATH.name}")
    print(f"Semantic layer spec: {SEMANTIC_LAYER_PATH.name}")
    print(f"BI release brief: {RELEASE_BRIEF_PATH.name}")


if __name__ == "__main__":
    main()
