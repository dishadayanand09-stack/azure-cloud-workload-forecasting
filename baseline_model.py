
import pandas as pd
import numpy as np

# Load training data only
train = pd.read_csv("challenge_data/train_aggregate.csv")

# Use the final observed training values
last_vm_count = train["active_vm_count"].iloc[-1]
last_cpu = train["aggregate_cpu_utilization"].iloc[-1]

# Generate the next 24 timestamps
last_timestamp = train["timestamp"].iloc[-1]
future_timestamps = [
    last_timestamp + 300 * i
    for i in range(1, 25)
]

# Persistence baseline: repeat the last known values
predictions = pd.DataFrame({
    "timestamp": future_timestamps,
    "active_vm_count": np.repeat(last_vm_count, 24),
    "aggregate_cpu_utilization": np.repeat(last_cpu, 24)
})

# Save baseline predictions
predictions.to_csv(
    "outputs/baseline_predictions.csv",
    index=False
)

print("=== BASELINE FORECAST ===")
print(predictions.head())
print("\nTotal predictions:", len(predictions))
print("\nBaseline saved successfully.")
