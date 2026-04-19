import csv
import math
from pathlib import Path

BASE_DIR = Path(__file__).parent
INPUT_PATH = BASE_DIR / "customers.csv"
REPORT_PATH = BASE_DIR / "segmentation_report.md"
PLAYBOOK_PATH = BASE_DIR / "segment_actions.csv"

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


def feature_ranges(rows):
    mins = {feature: min(row[feature] for row in rows) for feature in FEATURES}
    maxs = {feature: max(row[feature] for row in rows) for feature in FEATURES}
    return mins, maxs


def normalize(rows, mins, maxs):
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


def kmeans(points, k=3, iterations=15):
    centroids = [points[0], points[2], points[6]]
    assignments = [-1 for _ in points]
    for _ in range(iterations):
        new_assignments = []
        for point in points:
            cluster_id = min(range(k), key=lambda index: distance(point, centroids[index]))
            new_assignments.append(cluster_id)
        if new_assignments == assignments:
            break
        assignments = new_assignments
        for cluster_id in range(k):
            cluster_points = [point for point, assignment in zip(points, assignments) if assignment == cluster_id]
            if cluster_points:
                centroids[cluster_id] = mean_point(cluster_points)
    return assignments, centroids


def recommend_action(cluster_id):
    if cluster_id == 0:
        return "Prioritize expansion and executive coverage."
    if cluster_id == 1:
        return "Stabilize service, enable adoption and reduce support friction."
    return "Protect revenue with targeted upsell and low-friction servicing."


def segment_health_score(rows):
    revenue = sum(row["annual_revenue_k"] for row in rows) / len(rows)
    support = sum(row["support_load"] for row in rows) / len(rows)
    maturity = sum(row["digital_maturity"] for row in rows) / len(rows)
    score = (revenue / 12) + (maturity * 6) - (support * 7)
    return round(score, 1)


def summarize(rows, assignments):
    summary = {}
    for cluster_id in sorted(set(assignments)):
        members = [row for row, assignment in zip(rows, assignments) if assignment == cluster_id]
        summary[cluster_id] = {
            "label": CLUSTER_LABELS[cluster_id],
            "accounts": [row["company"] for row in members],
            "average_revenue_k": round(sum(row["annual_revenue_k"] for row in members) / len(members), 1),
            "average_support_load": round(sum(row["support_load"] for row in members) / len(members), 1),
            "average_digital_maturity": round(sum(row["digital_maturity"] for row in members) / len(members), 1),
            "health_score": segment_health_score(members),
            "recommended_action": recommend_action(cluster_id),
        }
    return summary


def export_playbook(summary):
    with PLAYBOOK_PATH.open("w", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=["cluster_id", "label", "accounts", "health_score", "recommended_action"],
        )
        writer.writeheader()
        for cluster_id, details in summary.items():
            writer.writerow(
                {
                    "cluster_id": cluster_id,
                    "label": details["label"],
                    "accounts": ", ".join(details["accounts"]),
                    "health_score": details["health_score"],
                    "recommended_action": details["recommended_action"],
                }
            )


def build_report(summary):
    lines = [
        "# Segmentation Report - Customer Segmentation Clustering",
        "",
        "This report shows how unsupervised segmentation can be turned into a readable commercial and operational playbook.",
        "",
    ]
    for cluster_id, details in summary.items():
        lines.extend(
            [
                f"## Cluster {cluster_id} - {details['label']}",
                f"- Accounts: {', '.join(details['accounts'])}",
                f"- Average revenue (k): `{details['average_revenue_k']}`",
                f"- Average support load: `{details['average_support_load']}`",
                f"- Average digital maturity: `{details['average_digital_maturity']}`",
                f"- Health score: `{details['health_score']}`",
                f"- Recommended action: {details['recommended_action']}",
                "",
            ]
        )
    lines.append("## What This Demonstrates")
    lines.append(
        "This example shows segmentation not as a clustering exercise alone, but as a practical playbook for account prioritization."
    )
    return "\n".join(lines) + "\n"


def main():
    rows = load_rows()
    mins, maxs = feature_ranges(rows)
    points = normalize(rows, mins, maxs)
    assignments, _ = kmeans(points)
    summary = summarize(rows, assignments)
    export_playbook(summary)
    REPORT_PATH.write_text(build_report(summary))

    print("Customer segmentation demo")
    print("=" * 25)
    for cluster_id, details in summary.items():
        print(
            f"- Cluster {cluster_id}: {details['label']} | accounts={len(details['accounts'])} | health_score={details['health_score']}"
        )
    print(f"Generated: {REPORT_PATH.name}, {PLAYBOOK_PATH.name}")


if __name__ == "__main__":
    main()
