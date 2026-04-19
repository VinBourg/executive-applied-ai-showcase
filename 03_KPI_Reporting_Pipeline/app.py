import json

from metrics import CATEGORY_PATH, DAILY_PATH, SUMMARY_PATH, compute_metrics, load_rows, write_dashboard, write_outputs


def main():
    rows = load_rows()
    summary, category_rows, daily_rows = compute_metrics(rows)
    write_outputs(summary, category_rows, daily_rows)
    write_dashboard(summary, category_rows, daily_rows)

    print("KPI pipeline completed")
    print(json.dumps(summary, indent=2))
    print(f"Generated: {SUMMARY_PATH.name}, {CATEGORY_PATH.name}, {DAILY_PATH.name}, dashboard.html")


if __name__ == "__main__":
    main()
