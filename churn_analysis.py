
import pandas as pd
from pathlib import Path

Path("outputs").mkdir(exist_ok=True)

cpu = pd.read_csv(
    "challenge_data/vm_cpu_readings.csv.gz"
)

# Use training timestamps only
timestamps = sorted(cpu["timestamp"].unique())[:110]
cpu = cpu[cpu["timestamp"].isin(timestamps)].copy()

print("=== VM CHURN ANALYSIS ===")

previous_vms = None
results = []

for timestamp, group in cpu.groupby("timestamp", sort=True):
    current_vms = set(group["vm_id"])

    if previous_vms is None:
        new_vms = None
        departed_vms = None
    else:
        new_vms = len(current_vms - previous_vms)
        departed_vms = len(previous_vms - current_vms)

    results.append({
        "timestamp": timestamp,
        "active_vm_count": len(current_vms),
        "new_vms": new_vms,
        "departed_vms": departed_vms
    })

    previous_vms = current_vms

churn = pd.DataFrame(results)

print(churn.describe().round(2).to_string())

print("\n=== HIGH CPU UTILIZATION ===")

high_cpu = (
    cpu.groupby("timestamp")
    .agg(
        total_vms=("vm_id", "nunique"),
        vms_above_80=("avg_cpu", lambda x: (x >= 80).sum()),
        vms_above_90=("avg_cpu", lambda x: (x >= 90).sum())
    )
    .reset_index()
)

high_cpu["pct_above_80"] = (
    100 * high_cpu["vms_above_80"] / high_cpu["total_vms"]
)

print(high_cpu[[
    "vms_above_80",
    "vms_above_90",
    "pct_above_80"
]].describe().round(3).to_string())

print("\n=== HIGHEST RISK TIMESTAMPS ===")
print(
    high_cpu.nlargest(5, "vms_above_80")[
        ["timestamp", "vms_above_80", "pct_above_80"]
    ].to_string(index=False)
)

churn.to_csv("outputs/vm_churn.csv", index=False)
high_cpu.to_csv("outputs/high_cpu_risk.csv", index=False)

print("\nAnalysis completed.")
