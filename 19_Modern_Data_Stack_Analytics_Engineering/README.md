# Modern Data Stack Analytics Engineering

A compact analytics-engineering example focused on trusted metrics, semantic definitions, data contracts and BI readiness.

## Business problem

Many teams have dashboards, but not a stable metric layer.
The real problem is not the lack of charts. It is the lack of trusted definitions, contract discipline and release signals that BI, analytics and AI consumers can rely on.

## What the program does

- aggregates commercial activity into a reusable metric layer,
- evaluates source freshness, tests and contract status,
- writes a trusted-metrics table for portfolio and market views,
- generates a semantic-layer style specification for BI and AI consumers,
- produces a release brief that clarifies what is ready and what remains under watch.

## Operational outputs

- `analytics_engineering_report.md`
  Executive report summarizing metric trust, source issues and next actions.
- `trusted_metrics.csv`
  Publishable metric layer with trust status by portfolio and market.
- `semantic_layer_spec.json`
  Semantic definitions, dimensions, formulas and source dependencies.
- `data_contract_status.csv`
  Contract, freshness and test view across upstream data products.
- `bi_release_brief.md`
  Short release note for BI and analytics stakeholders.

## Market fit

- France: dbt, Power BI, Snowflake, Databricks and analytics-engineering environments that need trusted metrics rather than dashboard drift.
- Switzerland: finance, insurance and regulated operating contexts where definitions, ownership and release signals matter.
- USA East: enterprise analytics engineering, semantic layers, trusted metrics and data-product discipline in cloud-heavy stacks.

## Run

```bash
python3 app.py
```

## Review in 60 seconds

Open `analytics_engineering_report.md`, then `trusted_metrics.csv`, then `semantic_layer_spec.json`.
That sequence shows the strongest signal:
- trusted-metric thinking,
- semantic-layer discipline,
- data contracts and release logic,
- a profile that can support both BI and AI with the same data foundation.
