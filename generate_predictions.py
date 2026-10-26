
import argparse
from pathlib import Path

import numpy as np
import pandas as pd


def generate_predictions(data_dir, output_path):
    data_dir = Path(data_dir)
    output_path = Path(output_path)

    cpu = pd.read_csv(data_dir / "vm_cpu_readings.csv.gz")

    required = {"timestamp", "vm_id", "avg_cpu"}
    if not required.issubset(cpu.columns):
        raise ValueError("Dataset is missing required columns.")

    cpu["timestamp"] = pd.to_numeric(
        cpu["timestamp"], errors="raise"
    )
    cpu["avg_cpu"] = pd.to_numeric(
        cpu["avg_cpu"], errors="coerce"
    )

    # Valid CPU readings only
    cpu = cpu[
        cpu["avg_cpu"].between(0, 100)
    ].copy()

    # Each VM contributes at most once per timestamp.
    cpu = cpu.drop_duplicates(
        subset=["timestamp", "vm_id"]
    )

    aggregate = (
        cpu.groupby("timestamp")
        .agg(
            active_vm_count=("vm_id", "nunique"),
            aggregate_cpu_utilization=("avg_cpu", "mean")
        )
        .reset_index()
        .sort_values("timestamp")
    )

    # The official challenge has 110 training observations
    # and 24 held-out observations.
    if len(aggregate) < 25:
        raise ValueError(
            "At least 25 timestamps are required."
        )

    train = aggregate.iloc[:-24].copy()
    holdout_timestamps = aggregate["timestamp"].iloc[-24:]

    # Persistence forecasts based on training data only
    last_vm_count = train["active_vm_count"].iloc[-1]
    last_cpu = train["aggregate_cpu_utilization"].iloc[-1]

    predictions = pd.DataFrame({
        "timestamp": holdout_timestamps.to_numpy(),
        "active_vm_count": np.repeat(last_vm_count, 24),
        "aggregate_cpu_utilization": np.repeat(last_cpu, 24)
    })

    assert len(predictions) == 24
    assert predictions["timestamp"].is_unique
    assert np.isfinite(
        predictions[
            ["active_vm_count", "aggregate_cpu_utilization"]
        ].to_numpy(dtype=float)
    ).all()

    output_path.parent.mkdir(
        parents=True, exist_ok=True
    )
    predictions.to_csv(output_path, index=False)

    print("Training observations:", len(train))
    print("Forecast horizon:", len(predictions))
    print("Saved predictions to:", output_path)
    print(predictions.head().to_string(index=False))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--data",
        default="challenge_data",
        help="Directory containing the original dataset"
    )

    parser.add_argument(
        "--output",
        default="predictions.csv",
        help="Output prediction CSV path"
    )

    args = parser.parse_args()

    generate_predictions(args.data, args.output)
