# Automation Runbook

## Purpose

This runbook describes how an Alteryx-style analytics automation should be executed, reviewed and handed off to reporting or AI consumers.

## Run Sequence

1. Place the latest operational extracts and reference files in the controlled input area.
2. Run the workflow with the current reporting period parameter.
3. Review the exception queue before publishing outputs.
4. Validate critical controls in the control matrix.
5. Publish the clean dataset only when blocking checks are resolved or formally accepted.
6. Send the quality report to the business owner and analytics owner.

## Human Review Points

- Business owner validates unusual variances.
- Data steward reviews unmatched keys and mapping issues.
- Analytics owner confirms that dashboard-ready outputs can be published.
- AI product owner confirms whether the dataset is safe for downstream AI workflows.

## Handoff Outputs

- BI-ready dataset for Power BI.
- Exception queue for remediation.
- Quality report for review.
- Control matrix for auditability and continuous improvement.

## Operating Principle

The workflow should not only automate preparation. It should also make data quality, ownership and publication readiness visible enough for business teams to trust the output.
