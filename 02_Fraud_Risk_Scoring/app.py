import math

FEATURES = [
    "amount",
    "foreign_transfer",
    "new_beneficiary",
    "night_transfer",
    "velocity_24h",
]

TRAINING_DATA = [
    {"amount": 120, "foreign_transfer": 0, "new_beneficiary": 0, "night_transfer": 0, "velocity_24h": 1, "label": 0},
    {"amount": 180, "foreign_transfer": 0, "new_beneficiary": 1, "night_transfer": 0, "velocity_24h": 2, "label": 0},
    {"amount": 950, "foreign_transfer": 1, "new_beneficiary": 1, "night_transfer": 1, "velocity_24h": 5, "label": 1},
    {"amount": 870, "foreign_transfer": 1, "new_beneficiary": 0, "night_transfer": 1, "velocity_24h": 4, "label": 1},
    {"amount": 250, "foreign_transfer": 0, "new_beneficiary": 0, "night_transfer": 0, "velocity_24h": 2, "label": 0},
    {"amount": 1100, "foreign_transfer": 1, "new_beneficiary": 1, "night_transfer": 1, "velocity_24h": 6, "label": 1},
    {"amount": 300, "foreign_transfer": 0, "new_beneficiary": 1, "night_transfer": 0, "velocity_24h": 3, "label": 0},
    {"amount": 760, "foreign_transfer": 1, "new_beneficiary": 1, "night_transfer": 0, "velocity_24h": 5, "label": 1},
]

SAMPLES = [
    {"name": "Low-risk card payment", "amount": 140, "foreign_transfer": 0, "new_beneficiary": 0, "night_transfer": 0, "velocity_24h": 1},
    {"name": "Suspicious transfer", "amount": 980, "foreign_transfer": 1, "new_beneficiary": 1, "night_transfer": 1, "velocity_24h": 5},
    {"name": "Borderline case", "amount": 420, "foreign_transfer": 1, "new_beneficiary": 0, "night_transfer": 0, "velocity_24h": 3},
]


def sigmoid(value):
    return 1 / (1 + math.exp(-value))


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


def scale(row, means, stds):
    return [(row[feature] - means[feature]) / stds[feature] for feature in FEATURES]


def train(rows, iterations=2500, learning_rate=0.12):
    means, stds = compute_stats(rows)
    weights = [0.0 for _ in FEATURES]
    bias = 0.0
    for _ in range(iterations):
        gradient_w = [0.0 for _ in FEATURES]
        gradient_b = 0.0
        for row in rows:
            x = scale(row, means, stds)
            y = row["label"]
            prediction = sigmoid(sum(weight * value for weight, value in zip(weights, x)) + bias)
            error = prediction - y
            for index, value in enumerate(x):
                gradient_w[index] += error * value
            gradient_b += error
        sample_count = len(rows)
        weights = [w - learning_rate * gradient / sample_count for w, gradient in zip(weights, gradient_w)]
        bias -= learning_rate * gradient_b / sample_count
    return weights, bias, means, stds


def predict_proba(row, weights, bias, means, stds):
    x = scale(row, means, stds)
    return sigmoid(sum(weight * value for weight, value in zip(weights, x)) + bias)


def explain_risk(row):
    reasons = []
    if row["amount"] >= 800:
        reasons.append("high amount")
    if row["foreign_transfer"]:
        reasons.append("foreign transfer")
    if row["new_beneficiary"]:
        reasons.append("new beneficiary")
    if row["night_transfer"]:
        reasons.append("night transfer")
    if row["velocity_24h"] >= 4:
        reasons.append("high transaction velocity")
    return ", ".join(reasons) or "stable transaction pattern"


def main():
    weights, bias, means, stds = train(TRAINING_DATA)
    print("Fraud risk scoring demo")
    print("=" * 24)
    for sample in SAMPLES:
        probability = predict_proba(sample, weights, bias, means, stds)
        print(f"{sample['name']}: risk={probability:.2%} | drivers={explain_risk(sample)}")


if __name__ == "__main__":
    main()
