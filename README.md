# Azure Cloud Workload Forecasting

**Atomity AI/ML Engineering Take-Home Challenge**

## Project Overview

This project forecasts near-term cloud infrastructure demand using a curated subset of Microsoft Azure Public Dataset V2.

The two forecasting targets are:

- `active_vm_count`: Number of distinct VMs with valid CPU readings.
- `aggregate_cpu_utilization`: Average CPU utilization across the active VMs.

The objective is to forecast the final 24 five-minute observations, representing a two-hour horizon.

## Dataset

The original challenge dataset contains 10,000 VMs and 134 observations per VM, totaling 1,340,000 CPU readings.

Download the `data-v1` release from:

https://github.com/atomityhq/forecasting-challenge/releases/tag/data-v1

Extract the release and place the following files inside `challenge_data/`:

- `vm_cpu_readings.csv.gz`
- `vm_metadata.csv.gz`

The dataset files are not included in this repository.

## Installation

Python 3.11 or later is recommended, subject to dependency compatibility.

Clone this repository, navigate into the project directory, and create a virtual environment.

On Windows:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -e ".[dev]"
```

## Generate Predictions

Run:

```powershell
python generate_predictions.py --data challenge_data --output predictions.csv
```

The command reads the original CPU dataset, constructs aggregate targets, reserves the final 24 timestamps as holdout, and generates predictions using the persistence forecasting model.

The output file contains exactly:

```text
timestamp,active_vm_count,aggregate_cpu_utilization
```

with 24 rows in chronological order.

## Modeling Approach

The first 110 observations are used for model selection and forecasting. The final 24 observations are reserved as the holdout period.

The following models were evaluated using rolling-origin validation:

- Persistence forecasting.
- 12-observation moving average.
- 24-observation moving average.

Persistence achieved the lowest average CPU forecast error across five rolling-validation windows.

| Model | MAE | RMSE |
|---|---:|---:|
| Persistence | 0.203427 | 0.244942 |
| Moving average (12) | 0.242838 | 0.280380 |
| Moving average (24) | 0.260740 | 0.294380 |

The final model repeats the most recently observed training value across the forecast horizon.

## Workload Analysis

The analysis examines:

- Timestamp coverage and data quality.
- VM population stability and churn.
- CPU utilization distribution.
- Differences across workload categories.
- Peak utilization periods.
- VM-level saturation risk.

Although aggregate CPU utilization is relatively stable, individual VMs can experience substantial CPU pressure.

## Operational Recommendation

Use aggregate CPU forecasts with a historical error-based safety margin, while separately monitoring VMs approaching high utilization.

An illustrative margin of 0.393 percentage points was derived from rolling-validation underprediction errors.

See `reports/final_report.md` for methodology, findings, limitations and capacity-planning recommendations.

## Testing

Run:

```powershell
python -m pytest -q
```

The tests include a small synthetic dataset check to verify that the forecasting pipeline does not depend on the original VM count or timestamp values.

## Project Outputs

- `predictions.csv`: Final two-hour forecast.
- `reports/final_report.md`: Technical analysis and recommendations.
- `outputs/`: Generated charts and diagnostic analysis files.

## Data Leakage Prevention

The final 24 observed target values are not used for fitting, model selection or forecasting.

Model comparison uses chronological validation windows entirely within the first 110 observations.

The prediction generator uses holdout timestamps only to determine the required output schedule.

## Limitations

The historical window is short, the curated VM population exhibits no observed churn, and persistence cannot anticipate sudden utilization changes.

Future work could explore longer histories, category-level forecasting and calibrated uncertainty estimates.