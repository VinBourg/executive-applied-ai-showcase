import csv
from datetime import date, timedelta
from pathlib import Path

BASE_DIR = Path(__file__).parent
INPUT_PATH = BASE_DIR / "daily_ticket_volume.csv"


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


def forecast(values, horizon=5):
    slope, intercept = linear_trend(values)
    base = moving_average(values, 5)
    forecasts = []
    for step in range(1, horizon + 1):
        trend_value = intercept + slope * (len(values) + step - 1)
        forecast_value = round((trend_value + base) / 2)
        forecasts.append(forecast_value)
    return forecasts, slope


def main():
    series = load_series()
    dates = [item[0] for item in series]
    values = [item[1] for item in series]
    forecasts, slope = forecast(values)
    print("Time series forecasting demo")
    print("=" * 28)
    print(f"Latest observed volume: {values[-1]} tickets")
    print(f"Estimated trend slope: {slope:.2f} tickets/day")
    print("Next 5-day forecast:")
    start_date = dates[-1]
    for offset, predicted in enumerate(forecasts, start=1):
        print(f"  {(start_date + timedelta(days=offset)).isoformat()}: {predicted} tickets")
    print()
    if slope > 1.0:
        print("Planning signal: rising support demand, prepare extra coverage.")
    else:
        print("Planning signal: stable demand profile.")


if __name__ == "__main__":
    main()
