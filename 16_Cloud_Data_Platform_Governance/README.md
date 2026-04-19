# Cloud Data Platform Governance

A cloud data platform example focused on data quality, governance ownership, release readiness and trusted downstream use for BI, analytics and AI.

## Business problem

AI and analytics programs fail when downstream teams consume data that is late, weakly governed or not release-ready.
The real client need is trusted data products, not just another model or dashboard.

## What the program does

- evaluates multiple datasets across freshness, tests, contracts and lineage,
- scores platform health with explicit governance rules,
- flags release blockers before dashboards or models consume the data,
- writes operational outputs that support remediation and ownership,
- frames the work like a delivery-oriented data platform review.

## Operational outputs

- `governance_report.md`
  Executive report with dataset findings, risks and actions.
- `dataset_health.csv`
  Scorecard across the evaluated data products.
- `pipeline_release_checklist.md`
  Release decision and platform-control review.
- `contracts_registry.csv`
  Ownership, consumers and contract-coverage view.

## Market fit

- France: Azure, Databricks, dbt, Power BI and analytics-engineering environments that expect platform discipline.
- Switzerland: finance, insurance and regulated AI programs that need ownership, controls and release gates.
- USA East: AWS, Snowflake, Databricks and enterprise data environments where governance and permissible use matter.

## Run

```bash
python3 app.py
```

## Review in 60 seconds

Open `governance_report.md`, then `pipeline_release_checklist.md`, then `dataset_health.csv`.
That sequence shows the strongest signal:
- trusted data-product thinking,
- governance and release control,
- downstream readiness for BI and AI,
- a profile that can talk both AI and platform delivery.
