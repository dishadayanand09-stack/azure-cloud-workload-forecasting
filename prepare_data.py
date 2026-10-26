
import pandas as pd

# Load CPU observations
cpu = pd.read_csv("challenge_data/vm_cpu_readings.csv.gz")

print("=== DATA QUALITY CHECKS ===")

# Check duplicate VM observations at the same timestamp
duplicates = cpu.duplicated(subset=["timestamp", "vm_id"]).sum()
print("Duplicate VM-timestamp rows:", duplicates)

# Check invalid CPU values
for col in ["min_cpu", "max_cpu", "avg_cpu"]:
    invalid = (~cpu[col].between(0, 100)).sum()
    print(f"Invalid {col} values:", invalid)

# Check timestamp intervals
timestamps = sorted(cpu["timestamp"].unique())
intervals = pd.Series(timestamps).diff().dropna()

print("Unique timestamps:", len(timestamps))
print("Timestamp intervals:")
print(intervals.value_counts())

# Create aggregate forecasting targets
# Do not silently discard duplicates
if duplicates > 0:
    raise ValueError("Duplicate VM-timestamp rows require investigation.")

if len(timestamps) != 134:
    raise ValueError("Unexpected number of timestamps.")

if not (intervals == 300).all():
    raise ValueError("Unexpected timestamp gaps.")

if not cpu[["min_cpu", "max_cpu", "avg_cpu"]].apply(
    lambda col: col.between(0, 100).all()
).all():
    raise ValueError("Invalid CPU utilization values found.")

aggregate = (
    cpu.groupby("timestamp", as_index=False)
    .agg(
        active_vm_count=("vm_id", "nunique"),
        aggregate_cpu_utilization=("avg_cpu", "mean")
    )
    .sort_values("timestamp")
    .reset_index(drop=True)
)

print("\n=== AGGREGATED DATA ===")
print("Shape:", aggregate.shape)
print(aggregate.head())

# Split chronologically
train = aggregate.iloc[:110].copy()
holdout = aggregate.iloc[110:].copy()

# Save training targets only
train.to_csv("challenge_data/train_aggregate.csv", index=False)

print("\nTraining timestamps:", len(train))
print("Reserved holdout timestamps:", len(holdout))
print("Training data saved successfully.")
