# Analytics Engineering Report - Modern Data Stack Readiness

This example shows how an analytics-engineering layer can turn raw commercial activity into trusted metrics, semantic definitions and BI-ready release notes.

## Executive View
- Release status: `conditional release`
- Portfolio net revenue: `878.0k`
- Portfolio fulfillment rate: `91.8%`
- Highest-revenue market in this sample: `USA East` with `348.0k` net revenue

## Trusted Metric Layer
- `Net Revenue` is publishable at portfolio level with status `trusted`.
- `Fulfillment Rate` is publishable at portfolio level with status `trusted`.
- `Revenue per Active Customer` is publishable at portfolio level with status `trusted`.

## Metrics Under Watch
- `Support Case Rate` remains under watch because one of its upstream sources is not fully release-ready.

## Source Controls
- `orders_core` owned by `Data Platform` is `trusted`: no issue.
- `crm_accounts` owned by `Analytics Engineering` is `trusted`: no issue.
- `support_tickets` owned by `Customer Operations` is `watch`: contract status is draft, tests pass rate is 0.94, freshness is 7h for a 4h SLA.
- `finance_adjustments` owned by `Finance Data` is `trusted`: freshness is 9h for a 8h SLA.

## Why This Matters
- Trusted metrics reduce dashboard churn and executive debate over definitions.
- A semantic layer gives BI, analytics and AI teams a common metric contract.
- Release notes clarify what is safe to expose broadly and what still needs remediation.

## Recommended Next Actions
- Close the gap on `support_tickets` by stabilising freshness and contract coverage before promoting dependent metrics.
- Publish the trusted metrics table as the default metric layer for dashboards and copilots.
- Keep semantic definitions versioned so BI and AI consumers do not drift apart.
