
import pandas as pd

# Load the compressed datasets
cpu = pd.read_csv("challenge_data/vm_cpu_readings.csv.gz")
metadata = pd.read_csv("challenge_data/vm_metadata.csv.gz")

print("=== CPU DATASET ===")
print("Shape:", cpu.shape)
print("\nFirst 5 rows:")
print(cpu.head())

print("\nColumn names:")
print(cpu.columns.tolist())

print("\nMissing values:")
print(cpu.isnull().sum())

print("\n=== VM METADATA ===")
print("Shape:", metadata.shape)
print("\nFirst 5 rows:")
print(metadata.head())

print("\nColumn names:")
print(metadata.columns.tolist())
