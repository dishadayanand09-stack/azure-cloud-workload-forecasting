
import pandas as pd
import numpy as np

# Load only the 110 training timestamps
data = pd.read_csv("challenge_data/train_aggregate.csv")

# Use first 86 timestamps for training
history = data.iloc[:86].copy()

# Use next 24 timestamps for validation
validation = data.iloc[86:110].copy()

targets = [
    "active_vm_count",
    "aggregate_cpu_utilization"
]

print("=== BASELINE VALIDATION ===")
print("Training observations:", len(history))
print("Validation observations:", len(validation))

for target in targets:
    # Persistence forecast
    last_value = history[target].iloc[-1]
    predicted = np.repeat(last_value, len(validation))
    actual = validation[target].to_numpy()

    # Calculate evaluation metrics
    mae = np.mean(np.abs(actual - predicted))
    rmse = np.sqrt(np.mean((actual - predicted) ** 2))

    print(f"\nTarget: {target}")
    print(f"MAE: {mae:.6f}")
    print(f"RMSE: {rmse:.6f}")
