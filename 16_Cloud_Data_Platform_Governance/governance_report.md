# Governance Report - Cloud Data Platform Governance

This report shows how a data platform can be assessed before trusted consumption by dashboards, analytical products and AI workflows.

## Platform Snapshot
- Platform: `Global Customer Intelligence Platform`
- Version: `2026.04.2`
- Orchestrator: `dbt jobs and scheduled cloud pipelines`
- Cloud footprint: Azure, AWS, Databricks, Snowflake, Power BI
- Average dataset health score: `66.1`
- Release decision: `hold_release`
- Ready datasets: `3`
- Ready with actions: `0`
- Hold datasets: `2`

## Score Overview
| dataset | market | score | readiness | contract_coverage | tests | freshness_hours |
| --- | --- | --- | --- | --- | --- | --- |
| customer_360 | France | 100.0 | ready | 96.0% | 98.0% | 2.4 |
| support_interactions | France | 93.0 | ready | 88.0% | 96.0% | 4.5 |
| treasury_positions | USA East | 88 | ready | 91.0% | 97.0% | 1.8 |
| document_intake_events | Switzerland | 49.3 | hold | 79.0% | 94.0% | 5.0 |
| claims_events | Switzerland | 0.0 | hold | 84.0% | 92.0% | 7.8 |

## claims_events
- Market focus: `Switzerland`
- Domain: `risk and operations`
- Owner: `Insurance Risk Data Steward`
- Readiness: `hold`
- Primary action: Stabilize ingestion scheduling and alert on SLA breach before consumers are impacted.
- Consumers: fraud_monitoring, claims_ops_dashboard, reserve_forecast_ml

### Findings
- Freshness is `7.8h` versus an allowed `4h`.
- Null rate is `1.6%` versus a maximum `1.0%`.
- Duplicate rate is `0.5%` versus a maximum `0.2%`.
- Test pass rate is `92.0%`, below the `95%` floor.
- Contract coverage is `84.0%`, below the `90%` target.
- Schema drift events total `2`, above the allowed `1`.
- Documentation is stale and no longer reflects current production behavior.
- Lineage is incomplete for a dataset consumed by BI, automation or AI workflows.
- Sensitive data is not masked in non-production environments.
- There are `2` open incidents affecting dataset reliability.
- The latest release already surfaced warnings for this dataset pipeline.

## document_intake_events
- Market focus: `Switzerland`
- Domain: `document automation`
- Owner: `Automation Product Owner`
- Readiness: `hold`
- Primary action: Fix failing tests and block release until the dataset clears the minimum coverage threshold.
- Consumers: approval_queue, audit_trail, document_classification_models

### Findings
- Test pass rate is `94.0%`, below the `95%` floor.
- Contract coverage is `79.0%`, below the `90%` target.
- Documentation is stale and no longer reflects current production behavior.
- Lineage is incomplete for a dataset consumed by BI, automation or AI workflows.
- There are `1` open incidents affecting dataset reliability.
- The latest release already surfaced warnings for this dataset pipeline.

## treasury_positions
- Market focus: `USA East`
- Domain: `finance platform`
- Owner: `Enterprise Data Platform Manager`
- Readiness: `ready`
- Primary action: Resolve outstanding incidents and document residual risk for consumers.
- Consumers: finance_reporting, executive_kpi_pack, liquidity_risk_models

### Findings
- There are `1` open incidents affecting dataset reliability.
- The latest release already surfaced warnings for this dataset pipeline.

## support_interactions
- Market focus: `France`
- Domain: `service operations`
- Owner: `Service Analytics Manager`
- Readiness: `ready`
- Primary action: Complete schema contracts and publish field-level ownership for remaining unmanaged attributes.
- Consumers: support_dashboard, routing_automation, knowledge_assistant

### Findings
- Contract coverage is `88.0%`, below the `90%` target.

## customer_360
- Market focus: `France`
- Domain: `commercial analytics`
- Owner: `Customer Data Product Lead`
- Readiness: `ready`
- Primary action: No immediate remediation required beyond routine monitoring.
- Consumers: sales_ops, power_bi_commercial, lead_scoring_ai

### Findings
- No blocking governance issue detected.

## Why this matters
- France: data platform, Power BI and analytics engineering environments increasingly expect cloud delivery discipline, not only modeling skills.
- Switzerland: finance, insurance and regulated AI teams need trusted data products, release controls and clear ownership.
- USA East: enterprise platform teams emphasize governance, permissible use, CI/CD and reliable data pipelines alongside GenAI initiatives.

## What a recruiter should see quickly
This example makes the repository look closer to real delivery work in cloud data and AI programs: ownership, data quality, release gates, platform controls and downstream business readiness.
