
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

# Load training data only
train = pd.read_csv("challenge_data/train_aggregate.csv")

# Create a folder for charts
Path("outputs").mkdir(exist_ok=True)

# Convert timestamps to hours
hours = (train["timestamp"] - train["timestamp"].min()) / 3600

# Graph 1: Active VM count
plt.figure(figsize=(10, 5))
plt.plot(hours, train["active_vm_count"])
plt.title("Active Virtual Machines Over Time")
plt.xlabel("Hours from Start")
plt.ylabel("Active VM Count")
plt.grid(alpha=0.3)
plt.tight_layout()
plt.savefig("outputs/active_vm_count.png", dpi=150)
plt.show()

# Graph 2: CPU utilization
plt.figure(figsize=(10, 5))
plt.plot(hours, train["aggregate_cpu_utilization"])
plt.title("Aggregate CPU Utilization Over Time")
plt.xlabel("Hours from Start")
plt.ylabel("CPU Utilization (%)")
plt.grid(alpha=0.3)
plt.tight_layout()
plt.savefig("outputs/cpu_utilization.png", dpi=150)
plt.show()

print("Both charts saved in the outputs folder.")

print("\n=== TRAINING DATA SUMMARY ===")
print(train.describe().round(2))
