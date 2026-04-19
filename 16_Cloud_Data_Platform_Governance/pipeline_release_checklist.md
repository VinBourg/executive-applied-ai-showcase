# Pipeline Release Checklist

- Platform: `Global Customer Intelligence Platform`
- Version: `2026.04.2`
- Release decision: `hold_release`

## Platform Controls
- `pass` CI pipeline: Unit, contract and integration checks are green on the release branch.
- `pass` Rollback plan: Rollback steps and data backfill procedure are documented.
- `pass` Monitoring activation: Freshness, failures and SLA alerts are wired to operations channels.
- `warning` Data contract verification: Two medium or high criticality datasets remain below the target contract coverage.
- `warning` Lineage completeness: Lineage is partial for regulated claims and document-intake flows.
- `warning` Security review: One regulated dataset is not masked in non-production environments.

## Dataset Readiness
- `customer_360`: `ready` with score `100.0` and action `No immediate remediation required beyond routine monitoring.`
- `support_interactions`: `ready` with score `93.0` and action `Complete schema contracts and publish field-level ownership for remaining unmanaged attributes.`
- `treasury_positions`: `ready` with score `88` and action `Resolve outstanding incidents and document residual risk for consumers.`
- `document_intake_events`: `hold` with score `49.3` and action `Fix failing tests and block release until the dataset clears the minimum coverage threshold.`
- `claims_events`: `hold` with score `0.0` and action `Stabilize ingestion scheduling and alert on SLA breach before consumers are impacted.`

## Release Actions
- `claims_events`: Stabilize ingestion scheduling and alert on SLA breach before consumers are impacted.
- `document_intake_events`: Fix failing tests and block release until the dataset clears the minimum coverage threshold.
- `treasury_positions`: Resolve outstanding incidents and document residual risk for consumers.
- `support_interactions`: Complete schema contracts and publish field-level ownership for remaining unmanaged attributes.
