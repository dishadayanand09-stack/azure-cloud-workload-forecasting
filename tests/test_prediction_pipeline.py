
import subprocess
import sys

import numpy as np
import pandas as pd


def test_prediction_pipeline_with_small_dataset(tmp_path):
    # Create a small synthetic dataset:
    # 30 timestamps, 3 VMs, 5-minute intervals.
    data_dir = tmp_path / "challenge_data"
    data_dir.mkdir()

    rows = []

    for step in range(30):
        timestamp = 1000 + step * 300

        for vm_id, cpu in [
            ("vm_1", 10.0),
            ("vm_2", 20.0),
            ("vm_3", 30.0),
        ]:
            rows.append({
                "timestamp": timestamp,
                "vm_id": vm_id,
                "avg_cpu": cpu
            })

    pd.DataFrame(rows).to_csv(
        data_dir / "vm_cpu_readings.csv.gz",
        index=False,
        compression="gzip"
    )

    output_file = tmp_path / "predictions.csv"

    result = subprocess.run(
        [
            sys.executable,
            "generate_predictions.py",
            "--data",
            str(data_dir),
            "--output",
            str(output_file)
        ],
        capture_output=True,
        text=True
    )

    assert result.returncode == 0, result.stderr
    assert output_file.exists()

    predictions = pd.read_csv(output_file)

    assert len(predictions) == 24

    assert predictions.columns.tolist() == [
        "timestamp",
        "active_vm_count",
        "aggregate_cpu_utilization"
    ]

    assert predictions["timestamp"].tolist() == [
        1000 + step * 300
        for step in range(6, 30)
    ]

    assert (predictions["active_vm_count"] == 3).all()

    assert np.allclose(
        predictions["aggregate_cpu_utilization"],
        20.0
    )
