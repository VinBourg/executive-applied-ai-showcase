import csv
import math
from pathlib import Path

BASE_DIR = Path(__file__).parent
REPORT_PATH = BASE_DIR / "fraud_scoring_report.md"
DECISIONS_PATH = BASE_DIR / "fraud_decisions.csv"

FEATURES = [
    "amount",
    "foreign_transfer",
    "new_beneficiary",
    "night_transfer",
    "velocity_24h",
]

FEATURE_LABELS = {
    "amount": "transaction amount",
    "foreign_transfer": "foreign transfer",
    "new_beneficiary": "new beneficiary",
    "night_transfer": "night-time execution",
    "velocity_24h": "24h transaction velocity",
}

TRAINING_DATA = [
    {"amount": 120, "foreign_transfer": 0, "new_beneficiary": 0, "night_transfer": 0, "velocity_24h": 1, "label": 0},
    {"amount": 180, "foreign_transfer": 0, "new_beneficiary": 1, "night_transfer": 0, "velocity_24h": 2, "label": 0},
    {"amount": 950, "foreign_transfer": 1, "new_beneficiary": 1, "night_transfer": 1, "velocity_24h": 5, "label": 1},
    {"amount": 870, "foreign_transfer": 1, "new_beneficiary": 0, "night_transfer": 1, "velocity_24h": 4, "label": 1},
    {"amount": 250, "foreign_transfer": 0, "new_beneficiary": 0, "night_transfer": 0, "velocity_24h": 2, "label": 0},
    {"amount": 1100, "foreign_transfer": 1, "new_beneficiary": 1, "night_transfer": 1, "velocity_24h": 6, "label": 1},
    {"amount": 300, "foreign_transfer": 0, "new_beneficiary": 1, "night_transfer": 0, "velocity_24h": 3, "label": 0},
    {"amount": 760, "foreign_transfer": 1, "new_beneficiary": 1, "night_transfer": 0, "velocity_24h": 5, "label": 1},
    {"amount": 210, "foreign_transfer": 0, "new_beneficiary": 0, "night_transfer": 0, "velocity_24h": 1, "label": 0},
    {"amount": 910, "foreign_transfer": 1, "new_beneficiary": 1, "night_transfer": 0, "velocity_24h": 4, "label": 1},
]

SAMPLES = [
    {"name": "Low-risk card payment", "amount": 140, "foreign_transfer": 0, "new_beneficiary": 0, "night_transfer": 0, "velocity_24h": 1},
    {"name": "Suspicious transfer", "amount": 980, "foreign_transfer": 1, "new_beneficiary": 1, "night_transfer": 1, "velocity_24h": 5},
    {"name": "Borderline case", "amount": 420, "foreign_transfer": 1, "new_beneficiary": 0, "night_transfer": 0, "velocity_24h": 3},
    {"name": "Corporate supplier payment", "amount": 650, "foreign_transfer": 0, "new_beneficiary": 1, "night_transfer": 0, "velocity_24h": 2},
]


def sigmoid(value):
    return 1 / (1 + math.exp(-value))


def dot_product(left, right):
    return sum(a * b for a, b in zip(left, right))


def compute_stats(rows):
    means = {}
    stds = {}
    for feature in FEATURES:
        values = [row[feature] for row in rows]
        mean = sum(values) / len(values)
        variance = sum((value - mean) ** 2 for value in values) / len(values)
        means[feature] = mean
        stds[feature] = math.sqrt(variance) or 1.0
    return means, stds


def scale_row(row, means, stds):
    return [(row[feature] - means[feature]) / stds[feature] for feature in FEATURES]


def train(rows, iterations=3200, learning_rate=0.12):
    means, stds = compute_stats(rows)
    weights = [0.0 for _ in FEATURES]
    bias = 0.0

    for _ in range(iterations):
        gradient_w = [0.0 for _ in FEATURES]
        gradient_b = 0.0
        for row in rows:
            scaled = scale_row(row, means, stds)
            prediction = sigmoid(dot_product(weights, scaled) + bias)
            error = prediction - row["label"]
            for index, value in enumerate(scaled):
                gradient_w[index] += error * value
            gradient_b += error

        sample_count = len(rows)
        weights = [weight - learning_rate * gradient / sample_count for weight, gradient in zip(weights, gradient_w)]
        bias -= learning_rate * gradient_b / sample_count

    return weights, bias, means, stds


def predict_proba(row, weights, bias, means, stds):
    scaled = scale_row(row, means, stds)
    probability = sigmoid(dot_product(weights, scaled) + bias)
    return probability, scaled


def classify_risk(probability):
    if probability >= 0.8:
        return "critical"
    if probability >= 0.6:
        return "high"
    if probability >= 0.35:
        return "medium"
    return "low"


def recommend_action(risk_band):
    if risk_band == "critical":
        return "Block and escalate to fraud operations immediately."
    if risk_band == "high":
        return "Hold for analyst review before execution."
    if risk_band == "medium":
        return "Request additional verification and monitor closely."
    return "Allow with routine monitoring."


def feature_contributions(row, scaled_values, weights):
    contributions = []
    for feature, scaled, weight in zip(FEATURES, scaled_values, weights):
        contribution = scaled * weight
        contributions.append((feature, contribution, row[feature]))
    contributions.sort(key=lambda item: abs(item[1]), reverse=True)
    return contributions


def explain_drivers(contributions):
    lines = []
    for feature, contribution, raw_value in contributions[:3]:
        direction = "raises risk" if contribution >= 0 else "reduces risk"
        lines.append(f"{FEATURE_LABELS[feature]}={raw_value} {direction}")
    return lines


def evaluate_training(rows, weights, bias, means, stds):
    true_positive = false_positive = true_negative = false_negative = 0
    for row in rows:
        probability, _ = predict_proba(row, weights, bias, means, stds)
        predicted = 1 if probability >= 0.5 else 0
        actual = row["label"]
        if predicted == 1 and actual == 1:
            true_positive += 1
        elif predicted == 1 and actual == 0:
            false_positive += 1
        elif predicted == 0 and actual == 0:
            true_negative += 1
        else:
            false_negative += 1
    accuracy = (true_positive + true_negative) / len(rows)
    return {
        "accuracy": round(accuracy, 2),
        "true_positive": true_positive,
        "false_positive": false_positive,
        "true_negative": true_negative,
        "false_negative": false_negative,
    }


def feature_weight_table(weights):
    table = []
    for feature, weight in sorted(zip(FEATURES, weights), key=lambda item: abs(item[1]), reverse=True):
        table.append({"feature": FEATURE_LABELS[feature], "weight": round(weight, 3)})
    return table


def score_samples(weights, bias, means, stds):
    scored = []
    for sample in SAMPLES:
        probability, scaled_values = predict_proba(sample, weights, bias, means, stds)
        contributions = feature_contributions(sample, scaled_values, weights)
        risk_band = classify_risk(probability)
        scored.append(
            {
                "name": sample["name"],
                "probability": round(probability, 4),
                "risk_band": risk_band,
                "drivers": explain_drivers(contributions),
                "action": recommend_action(risk_band),
            }
        )
    scored.sort(key=lambda item: item["probability"], reverse=True)
    return scored


def write_decisions(scored_samples):
    with DECISIONS_PATH.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=["name", "probability", "risk_band", "action", "drivers"])
        writer.writeheader()
        for sample in scored_samples:
            writer.writerow(
                {
                    "name": sample["name"],
                    "probability": sample["probability"],
                    "risk_band": sample["risk_band"],
                    "action": sample["action"],
                    "drivers": " | ".join(sample["drivers"]),
                }
            )


def build_report(model_diagnostics, feature_weights, scored_samples):
    lines = [
        "# Fraud Risk Scoring Report",
        "",
        "## Model Diagnostics",
        f"- Accuracy on training sample: `{model_diagnostics['accuracy']}`",
        f"- True positives: `{model_diagnostics['true_positive']}`",
        f"- False positives: `{model_diagnostics['false_positive']}`",
        f"- True negatives: `{model_diagnostics['true_negative']}`",
        f"- False negatives: `{model_diagnostics['false_negative']}`",
        "",
        "## Feature Weights",
        "| feature | weight |",
        "| --- | --- |",
    ]
    for row in feature_weights:
        lines.append(f"| {row['feature']} | {row['weight']} |")

    lines.extend(["", "## Sample Decisions"])
    for sample in scored_samples:
        lines.extend(
            [
                f"### {sample['name']}",
                f"- Probability: `{sample['probability']}`",
                f"- Risk band: `{sample['risk_band']}`",
                f"- Recommended action: {sample['action']}",
                "- Main drivers:",
            ]
        )
        lines.extend(f"  - {driver}" for driver in sample["drivers"])
        lines.append("")

    lines.append("## What This Demonstrates")
    lines.append(
        "This example shows a compact but credible fraud-scoring workflow: model training, scoring, interpretable drivers and operational decisions."
    )
    return "\n".join(lines) + "\n"


def main():
    weights, bias, means, stds = train(TRAINING_DATA)
    model_diagnostics = evaluate_training(TRAINING_DATA, weights, bias, means, stds)
    feature_weights = feature_weight_table(weights)
    scored_samples = score_samples(weights, bias, means, stds)
    write_decisions(scored_samples)
    REPORT_PATH.write_text(build_report(model_diagnostics, feature_weights, scored_samples))

    print("Fraud risk scoring demo")
    print("=" * 24)
    print(f"Training accuracy: {model_diagnostics['accuracy']}")
    print("Sample decisions:")
    for sample in scored_samples:
        print(
            f"- {sample['name']}: risk={sample['probability']:.2%} | band={sample['risk_band']} | action={sample['action']}"
        )
    print(f"Generated: {REPORT_PATH.name}, {DECISIONS_PATH.name}")


if __name__ == "__main__":
    main()
