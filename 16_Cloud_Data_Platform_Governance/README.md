# Cloud Data Platform Governance

A market-aligned cloud data platform example focused on data quality, governance ownership, release readiness and trusted downstream consumption for analytics, BI and AI use cases.

## Why it matters

This example demonstrates:
- cloud-style data platform discipline rather than isolated notebook work,
- explicit data quality scoring and release gates,
- governance ownership across datasets, contracts and consumers,
- operational outputs that support BI, reporting and AI use cases.

## Business relevance

- trusted data products for reporting, finance, operations and AI,
- release readiness before dashboards or models consume data,
- platform governance for regulated or multi-stakeholder environments,
- clearer ownership, faster remediation and lower delivery risk.

## Market relevance

This folder is especially aligned with current demand signals across:
- France: Azure, Databricks, dbt, Power BI, data platform RUN and analytics engineering environments,
- Switzerland: cloud data platforms, finance and risk data products, MLOps, CI/CD and governance expectations,
- US East: AWS, Snowflake, Databricks, data quality, governance, permissible use and enterprise platform discipline.

## Files

- `app.py`
  Runs the governance evaluation and generates operational outputs.
- `source_systems.json`
  Sample multi-country datasets covering CRM, finance/risk, support and document workflows.
- `quality_rules.json`
  Governance thresholds, platform controls and release expectations.
- `pipeline_manifest.json`
  Compact view of cloud footprint, jobs and release controls.
- `governance_report.md`
  Generated executive report with risks, readiness and actions.
- `dataset_health.csv`
  Generated scorecard for each data product.
- `pipeline_release_checklist.md`
  Generated release-readiness checklist for the platform.
- `contracts_registry.csv`
  Generated view of data contracts, owners and consumption coverage.

## Run

```bash
python3 app.py
```

## What a recruiter should see quickly

This folder shows that the profile is not limited to AI demos.
It also demonstrates the ability to:
- structure trusted data products,
- enforce platform controls before release,
- connect ownership, quality and downstream business use,
- think like a delivery-oriented data engineer or platform consultant.
