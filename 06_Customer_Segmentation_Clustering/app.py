import csv
import math
from pathlib import Path

BASE_DIR = Path(__file__).parent
INPUT_PATH = BASE_DIR / "customers.csv"
FEATURES = ["annual_revenue_k", "monthly_orders", "digital_maturity", "support_load"]
CLUSTER_LABELS = {
    0: "Strategic growth accounts",
    1: "Support-intensive developing accounts",
    2: "Efficient mid-market accounts",
}


def load_rows():
    with INPUT_PATH.open() as handle:
        rows = list(csv.DictReader(handle))
    for row in rows:
        for feature in FEATURES:
            row[feature] = float(row[feature])
    return rows


def normalize(rows):
    mins = {feature: min(row[feature] for row in rows) for feature in FEATURES}
    maxs = {feature: max(row[feature] for row in rows) for feature in FEATURES}
    normalized = []
    for row in rows:
        point = []
        for feature in FEATURES:
            spread = maxs[feature] - mins[feature] or 1.0
            point.append((row[feature] - mins[feature]) / spread)
        normalized.append(point)
    return normalized


def distance(point_a, point_b):
    return math.sqrt(sum((a - b) ** 2 for a, b in zip(point_a, point_b)))


def mean_point(points):
    return [sum(values) / len(values) for values in zip(*points)]


def kmeans(points, k=3, iterations=10):
    centroids = [points[0], points[2], points[6]]
    assignments = [0 for _ in points]
    for _ in range(iterations):
        new_assignments = []
        for point in points:
            idx = min(range(k), key=lambda i: distance(point, centroids[i]))
            new_assignments.append(idx)
        if new_assignments == assignments:
            break
        assignments = new_assignments
        for index in range(k):
            cluster_points = [point for point, assignment in zip(points, assignments) if assignment == index]
            if cluster_points:
                centroids[index] = mean_point(cluster_points)
    return assignments


def summarize(rows, assignments):
    summary = {}
    for cluster_id in sorted(set(assignments)):
        members = [row for row, assignment in zip(rows, assignments) if assignment == cluster_id]
        summary[cluster_id] = {
            "label": CLUSTER_LABELS[cluster_id],
            "accounts": [row["company"] for row in members],
            "average_revenue_k": round(sum(row["annual_revenue_k"] for row in members) / len(members), 1),
            "average_support_load": round(sum(row["support_load"] for row in members) / len(members), 1),
            "recommended_action": recommend_action(cluster_id),
        }
    return summary


def recommend_action(cluster_id):
    if cluster_id == 0:
        return "Prioritize expansion and executive relationship coverage."
    if cluster_id == 1:
        return "Focus on enablement, onboarding and service stabilization."
    return "Protect growth with targeted upsell and efficient servicing."


def main():
    rows = load_rows()
    points = normalize(rows)
    assignments = kmeans(points)
    summary = summarize(rows, assignments)
    print("Customer segmentation demo")
    print("=" * 25)
    for cluster_id, details in summary.items():
        print(f"Cluster {cluster_id}: {details['label']}")
        print(f"  Accounts: {', '.join(details['accounts'])}")
        print(f"  Avg revenue (k): {details['average_revenue_k']}")
        print(f"  Avg support load: {details['average_support_load']}")
        print(f"  Action: {details['recommended_action']}")
        print()


if __name__ == "__main__":
    main()
