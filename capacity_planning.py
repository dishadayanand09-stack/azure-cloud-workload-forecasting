
import numpy as np
import pandas as pd
from pathlib import Path

Path("outputs").mkdir(exist_ok=True)

# Load final forecasts and historical validation errors
predictions = pd.read_csv("predictions.csv")
errors = pd.read_csv("outputs/forecast_errors.csv")
risk = pd.read_csv("outputs/high_cpu_risk.csv")

# Use the 95th percentile of positive underprediction
# errors as a proposed aggregate CPU safety margin.
# Deduplicate overlapping validation timestamps for
# this exploratory margin calculation.
errors = errors.sort_values(
    "training_end"
).drop_duplicates(
    subset=["timestamp"],
    keep="last"
)

underprediction = np.maximum(
    errors["actual"] - errors["predicted"],
    0
)

safety_margin = np.percentile(underprediction, 95)

# Proposed CPU planning target
predictions["cpu_planning_target"] = np.clip(
    predictions["aggregate_cpu_utilization"] + safety_margin,
    0,
    100
)

# Use the observed high-CPU VM count as a risk indicator
historical_high_cpu_p95 = np.percentile(
    risk["vms_above_80"],
    95
)

print("=== CAPACITY PLANNING RECOMMENDATION ===")
print(
    "CPU safety margin:",
    round(safety_margin, 4),
    "percentage points"
)

print(
    "Historical P95 count of VMs above 80% CPU:",
    round(historical_high_cpu_p95, 2)
)

print("\n=== PROPOSED PLANNING TARGETS ===")
print(
    predictions[
        [
            "timestamp",
            "aggregate_cpu_utilization",
            "cpu_planning_target"
        ]
    ].head().round(4).to_string(index=False)
)

# Save policy analysis separately
predictions.to_csv(
    "outputs/capacity_planning.csv",
    index=False
)

print("\nCapacity planning analysis completed.")
print("Original predictions.csv remains unchanged.")
