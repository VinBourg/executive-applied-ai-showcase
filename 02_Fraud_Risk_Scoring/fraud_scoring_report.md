# Fraud Risk Scoring Report

## Model Diagnostics
- Accuracy on training sample: `1.0`
- True positives: `5`
- False positives: `0`
- True negatives: `5`
- False negatives: `0`

## Feature Weights
| feature | weight |
| --- | --- |
| foreign transfer | 2.931 |
| transaction amount | 2.461 |
| 24h transaction velocity | 1.859 |
| night-time execution | 0.943 |
| new beneficiary | 0.332 |

## Sample Decisions
### Suspicious transfer
- Probability: `0.9999`
- Risk band: `critical`
- Recommended action: Block and escalate to fraud operations immediately.
- Main drivers:
  - foreign transfer=1 raises risk
  - transaction amount=980 raises risk
  - 24h transaction velocity=5 raises risk

### Borderline case
- Probability: `0.6678`
- Risk band: `high`
- Recommended action: Hold for analyst review before execution.
- Main drivers:
  - foreign transfer=1 raises risk
  - transaction amount=420 reduces risk
  - night-time execution=0 reduces risk

### Corporate supplier payment
- Probability: `0.0173`
- Risk band: `low`
- Recommended action: Allow with routine monitoring.
- Main drivers:
  - foreign transfer=0 reduces risk
  - 24h transaction velocity=2 reduces risk
  - night-time execution=0 reduces risk

### Low-risk card payment
- Probability: `0.0001`
- Risk band: `low`
- Recommended action: Allow with routine monitoring.
- Main drivers:
  - foreign transfer=0 reduces risk
  - transaction amount=140 reduces risk
  - 24h transaction velocity=1 reduces risk

## What This Demonstrates
This example shows a compact but credible fraud-scoring workflow: model training, scoring, interpretable drivers and operational decisions.
