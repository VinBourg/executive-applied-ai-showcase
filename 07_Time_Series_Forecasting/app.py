import csv
from datetime import date, timedelta
from pathlib import Path

BASE_DIR = Path(__file__).parent
INPUT_PATH = BASE_DIR / "daily_ticket_volume.csv"
REPORT_PATH = BASE_DIR / "forecast_report.md"
STAFFING_PATH = BASE_DIR / "staffing_plan.csv"


def load_series():
    with INPUT_PATH.open() as handle:
        rows = list(csv.DictReader(handle))
    return [(date.fromisoformat(row["date"]), int(row["tickets"])) for row in rows]


def moving_average(values, window):
    return sum(values[-window:]) / window


def linear_trend(values):
    x_values = list(range(len(values)))
    x_mean = sum(x_values) / len(x_values)
    y_mean = sum(values) / len(values)
    numerator = sum((x - x_mean) * (y - y_mean) for x, y in zip(x_values, values))
    denominator = sum((x - x_mean) ** 2 for x in x_values) or 1.0
    slope = numerator / denominator
    intercept = y_mean - slope * x_mean
    return slope, intercept


def detect_anomalies(values, window=5):
    anomalies = []
    for index in range(window, len(values)):
        baseline = sum(values[index - window:index]) / window
        if values[index] >= baseline * 1.12:
            anomalies.append(index)
    return anomalies


def forecast(values, horizon=5):
    slope, intercept = linear_trend(values)
    base = moving_average(values, 5)
    forecasts = []
    for step in range(1, horizon + 1):
        trend_value = intercept + slope * (len(values) + step - 1)
        forecast_value = round((trend_value + base) / 2)
        forecasts.append(forecast_value)
    return forecasts, slope


def staffing_needed(ticket_volume):
    if ticket_volume >= 65:
        return 6
    if ticket_volume >= 58:
        return 5
    return 4


def build_staffing_plan(series, forecasts):
    start_date = series[-1][0]
    plan = []
    for offset, predicted in enumerate(forecasts, start=1):
        plan.append(
            {
                "date": (start_date + timedelta(days=offset)).isoformat(),
                "forecast_tickets": predicted,
                "recommended_agents": staffing_needed(predicted),
                "shift_signal": "reinforce" if predicted >= 60 else "standard",
            }
        )
    return plan


def write_staffing_plan(plan):
    with STAFFING_PATH.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=["date", "forecast_tickets", "recommended_agents", "shift_signal"])
        writer.writeheader()
        writer.writerows(plan)


def build_report(series, forecasts, slope, anomalies, plan):
    latest_date, latest_value = series[-1]
    lines = [
        "# Forecast Report - Time Series Forecasting",
        "",
        f"- Latest observed date: `{latest_date.isoformat()}`",
        f"- Latest observed volume: `{latest_value}` tickets",
        f"- Estimated trend slope: `{round(slope, 2)}` tickets/day",
        f"- Detected local anomalies: `{len(anomalies)}`",
        "",
        "## Next 5-Day Forecast",
        "| date | forecast_tickets | recommended_agents | shift_signal |",
        "| --- | --- | --- | --- |",
    ]
    for row in plan:
        lines.append(
            f"| {row['date']} | {row['forecast_tickets']} | {row['recommended_agents']} | {row['shift_signal']} |"
        )
    lines.extend(
        [
            "",
            "## Interpretation",
            "The planning signal combines a simple trend estimate with a recent-volume baseline to keep the forecast readable and operationally useful.",
            "",
            "## What This Demonstrates",
            "This example shows forecasting used for staffing and operational preparation rather than for abstract modeling alone.",
        ]
    )
    return "\n".join(lines) + "\n"


def main():
    series = load_series()
    values = [item[1] for item in series]
    forecasts, slope = forecast(values)
    anomalies = detect_anomalies(values)
    plan = build_staffing_plan(series, forecasts)
    write_staffing_plan(plan)
    REPORT_PATH.write_text(build_report(series, forecasts, slope, anomalies, plan))

    print("Time series forecasting demo")
    print("=" * 28)
    print(f"Latest observed volume: {values[-1]} tickets")
    print(f"Estimated trend slope: {slope:.2f} tickets/day")
    print(f"Detected anomalies: {len(anomalies)}")
    for row in plan:
        print(f"- {row['date']}: {row['forecast_tickets']} tickets | agents={row['recommended_agents']}")
    print(f"Generated: {REPORT_PATH.name}, {STAFFING_PATH.name}")


if __name__ == "__main__":
    main()
