
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

Path("outputs").mkdir(exist_ok=True)

# Load the dataset
cpu = pd.read_csv("challenge_data/vm_cpu_readings.csv.gz")
metadata = pd.read_csv("challenge_data/vm_metadata.csv.gz")

# Use training timestamps only for workload analysis
timestamps = sorted(cpu["timestamp"].unique())
training_timestamps = timestamps[:110]
cpu = cpu[cpu["timestamp"].isin(training_timestamps)].copy()

print("=== CPU UTILIZATION STATISTICS ===")
print(cpu["avg_cpu"].describe(
    percentiles=[0.25, 0.5, 0.75, 0.90, 0.95, 0.99]
).round(3))

# CPU utilization distribution
plt.figure(figsize=(10, 5))
plt.hist(cpu["avg_cpu"], bins=50, edgecolor="black")
plt.title("Distribution of VM CPU Utilization")
plt.xlabel("Average CPU Utilization (%)")
plt.ylabel("Number of Observations")
plt.tight_layout()
plt.savefig("outputs/cpu_distribution.png", dpi=150)
plt.close()

# Workload analysis by VM category
merged = cpu.merge(
    metadata[["vm_id", "vm_category"]],
    on="vm_id",
    how="left",
    validate="many_to_one"
)

category_stats = (
    merged.groupby("vm_category", dropna=False)["avg_cpu"]
    .agg(["mean", "median", "count"])
    .sort_values("mean", ascending=False)
)

print("\n=== CPU UTILIZATION BY VM CATEGORY ===")
print(category_stats.round(3).to_string())

category_stats.to_csv("outputs/category_statistics.csv")

# Identify peak and low demand timestamps
aggregate = (
    cpu.groupby("timestamp")["avg_cpu"]
    .mean()
)

print("\n=== PEAK CPU PERIODS ===")
print(aggregate.nlargest(5).round(3))

print("\n=== LOW CPU PERIODS ===")
print(aggregate.nsmallest(5).round(3))

# VM lifetimes from metadata
print("\n=== VM LIFETIME INFORMATION ===")
created = pd.to_numeric(
    metadata["timestamp_vm_created"], errors="coerce"
)
deleted = pd.to_numeric(
    metadata["timestamp_vm_deleted"], errors="coerce"
)

lifetimes = deleted - created
valid_lifetimes = lifetimes[lifetimes >= 0]

print("Valid lifetime records:", len(valid_lifetimes))
print("Lifetime statistics:")
print(valid_lifetimes.describe().round(2))

print("\nAnalysis completed.")
