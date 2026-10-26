
import numpy as np
import pandas as pd
from pathlib import Path

Path("outputs").mkdir(exist_ok=True)

data = pd.read_csv("challenge_data/train_aggregate.csv")

values = data["aggregate_cpu_utilization"].to_numpy()
timestamps = data["timestamp"].to_numpy()

horizon = 24
training_endpoints = [38, 50, 62, 74, 86]

records = []

for end in training_endpoints:
    actual = values[end:end + horizon]
    predicted = np.repeat(values[end - 1], horizon)

    for i in range(horizon):
        records.append({
            "training_end": end,
            "timestamp": timestamps[end + i],
            "actual": actual[i],
            "predicted": predicted[i],
            "absolute_error": abs(actual[i] - predicted[i]),
            "signed_error": predicted[i] - actual[i]
        })

errors = pd.DataFrame(records)

# Define high-load periods using the 75th percentile
# of the first 38 training observations only.
peak_threshold = np.percentile(values[:38], 75)

errors["load_period"] = np.where(
    errors["actual"] >= peak_threshold,
    "High Load",
    "Normal Load"
)

print("=== FORECAST ERROR ANALYSIS ===")
print("Peak threshold:", round(peak_threshold, 4))

print("\n=== ERROR BY LOAD PERIOD ===")
print(
    errors.groupby("load_period")
    .agg(
        observations=("absolute_error", "count"),
        MAE=("absolute_error", "mean"),
        RMSE=("absolute_error", lambda x: np.sqrt(np.mean(x**2))),
        mean_signed_error=("signed_error", "mean")
    )
    .round(6)
    .to_string()
)

print("\n=== FIVE LARGEST FORECAST ERRORS ===")
print(
    errors.nlargest(5, "absolute_error")[
        [
            "training_end",
            "timestamp",
            "actual",
            "predicted",
            "absolute_error"
        ]
    ].round(6).to_string(index=False)
)

# Normalized MAE, relative to mean actual utilization
normalized_mae = (
    errors["absolute_error"].mean()
    / errors["actual"].mean()
    * 100
)

print("\nNormalized MAE (% of mean CPU):",
      round(normalized_mae, 3))

errors.to_csv("outputs/forecast_errors.csv", index=False)

print("\nError analysis completed.")
