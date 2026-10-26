
import numpy as np
import pandas as pd

data = pd.read_csv("challenge_data/train_aggregate.csv")

target = "aggregate_cpu_utilization"
values = data[target].to_numpy()

horizon = 24

# Each split uses only observations available before
# its validation window.
training_endpoints = [38, 50, 62, 74, 86]

results = []

for end in training_endpoints:
    history = values[:end]
    actual = values[end:end + horizon]

    predictions = {
        "Persistence": np.repeat(history[-1], horizon),
        "Moving Average 12": np.repeat(
            history[-12:].mean(), horizon
        ),
        "Moving Average 24": np.repeat(
            history[-24:].mean(), horizon
        ),
    }

    for model_name, predicted in predictions.items():
        mae = np.mean(np.abs(actual - predicted))
        rmse = np.sqrt(np.mean((actual - predicted) ** 2))

        results.append({
            "training_end": end,
            "model": model_name,
            "MAE": mae,
            "RMSE": rmse
        })

results_df = pd.DataFrame(results)

print("=== ROLLING VALIDATION RESULTS ===")
print(results_df.to_string(index=False))

print("\n=== AVERAGE MODEL PERFORMANCE ===")
summary = (
    results_df.groupby("model")[["MAE", "RMSE"]]
    .mean()
    .sort_values("MAE")
)

print(summary.round(6))

# Save results for the technical report
results_df.to_csv(
    "outputs/rolling_validation_results.csv",
    index=False
)
