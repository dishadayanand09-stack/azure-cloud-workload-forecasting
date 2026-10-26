# Cloud Workload Forecasting and Analysis

**Atomity AI/ML Engineering Take-Home Challenge**

## 1. Executive Summary

This project investigates the predictability of cloud infrastructure workloads using a curated subset of the Microsoft Azure Public Dataset V2.

The dataset contains CPU utilization measurements for 10,000 virtual machines (VMs), sampled every five minutes across 134 timestamps. The objective is to forecast active VM count and aggregate CPU utilization for the final 24 timestamps, representing a two-hour forecasting horizon.

Three forecasting approaches were evaluated: persistence, a 12-observation moving average and a 24-observation moving average. Rolling-origin validation showed that persistence achieved the lowest average errors, with a CPU utilization MAE of 0.203427 percentage points and RMSE of 0.244942 percentage points.

The final model therefore uses persistence, forecasting 10,000 active VMs and 9.164556% aggregate CPU utilization throughout the two-hour horizon.

Although average CPU utilization is relatively low, individual VMs frequently experience high CPU demand. This suggests that infrastructure planning should combine aggregate forecasting with VM-level saturation monitoring.

## 2. Dataset Understanding and Preprocessing

### 2.1 Dataset

The challenge uses a curated Azure VM trace containing:

- 10,000 virtual machines.
- 1,340,000 VM-level CPU observations.
- 134 timestamps.
- Five-minute sampling intervals.
- VM metadata, including workload categories and lifetime information.

The CPU dataset includes timestamps, VM identifiers, and minimum, maximum and average CPU utilization measurements.

### 2.2 Data Quality

Initial inspection identified:

- No missing values in the CPU readings.
- No duplicate VM-timestamp observations.
- Consistent 300-second sampling intervals.
- No invalid CPU utilization values.
- Complete VM observations at each timestamp.

The resulting dataset was suitable for chronological time-series aggregation.

### 2.3 Target Construction

Two forecasting targets were constructed:

**Active VM count:** Number of distinct VMs with valid CPU observations at each timestamp.

**Aggregate CPU utilization:** Arithmetic mean of valid VM-level average CPU utilization measurements at each timestamp.

Each VM contributes at most once per timestamp.

The complete target series contains 134 observations. The first 110 timestamps form the modeling and validation period; the final 24 timestamps are reserved for forecasting.

The final 24 observed target values were not used for model fitting, tuning or selection.

## 3. Exploratory Workload Analysis

### 3.1 Active VM Population

The active VM count remained constant at 10,000 across all 110 training timestamps.

No VM arrivals or departures were observed between consecutive timestamps in the training window.

This indicates that VM population changes are not a major source of forecasting uncertainty in this curated trace. However, the result should not be generalized to all production cloud environments.

### 3.2 CPU Utilization

Aggregate CPU utilization varied within a relatively narrow range.

The highest observed training-period aggregate CPU utilization was approximately 9.912% at timestamp 16500, while the lowest was approximately 9.112% at timestamp 32400.

Despite this aggregate stability, individual VM CPU utilization was substantially more variable.

The 95th percentile of VM-level average CPU utilization was 37.293%, while the 99th percentile was 87.406%.

This difference highlights the risk of relying exclusively on aggregate utilization when assessing infrastructure pressure.

### 3.3 Workload Segments

Average CPU utilization differed across VM categories:

| VM category | Mean CPU utilization |
|---|---:|
| Interactive | 11.505% |
| Unknown | 10.355% |
| Delay-insensitive | 8.257% |

Interactive workloads showed higher average utilization than delay-insensitive workloads.

This suggests that category-level monitoring could improve operational visibility, particularly where workloads have different performance requirements.

### 3.4 High-Utilization VMs

Across the training period, an average of approximately 127 VMs per timestamp had CPU utilization at or above 80%.

An average of approximately 88 VMs exceeded or reached 90%.

The highest observed count of VMs at or above 80% CPU was 146, at timestamp 17400.

Therefore, a low aggregate utilization forecast does not necessarily imply that every VM has sufficient processing headroom.

## 4. Forecasting Methodology

### 4.1 Forecasting Problem

The objective is to forecast two hours ahead at five-minute intervals.

The final forecast consists of 24 predictions for:

1. Active VM count.
2. Aggregate CPU utilization.

All model selection and validation were restricted to the first 110 timestamps.

### 4.2 Candidate Models

Three simple forecasting approaches were compared:

**Persistence:** Repeats the most recently observed value throughout the forecasting horizon.

**12-observation moving average:** Uses the average of the preceding 12 observations.

**24-observation moving average:** Uses the average of the preceding 24 observations.

A linear-trend approach was also examined in an initial single-window comparison, but it performed poorly in that experiment and was not included in the final rolling comparison.

These methods were selected because the available training history is short and the aggregate series exhibits relatively modest variation.

### 4.3 Model Selection

Persistence was selected because it achieved the lowest mean errors across the evaluated rolling-origin windows.

This choice prioritizes reproducibility, interpretability and validation performance over unnecessary model complexity.

The active VM forecast uses the same persistence approach because the observed training population was constant.

## 5. Validation Methodology and Results

### 5.1 Temporal Validation

Five rolling-origin validation windows were used, with training endpoints at observations 38, 50, 62, 74 and 86.

Each validation window predicted the following 24 timestamps.

The validation windows overlap, so their errors are not independent. The results should be interpreted as an exploratory comparison rather than as five independent test samples.

This evaluation design resembles the intended production task: using historical observations to forecast the next two hours without accessing future target values.

### 5.2 Forecasting Performance

| Model | CPU MAE | CPU RMSE |
|---|---:|---:|
| Persistence | **0.203427** | **0.244942** |
| Moving average (12) | 0.242838 | 0.280380 |
| Moving average (24) | 0.260740 | 0.294380 |

All errors are measured in CPU utilization percentage points.

Persistence reduced MAE by approximately 16.2% relative to the 12-observation moving average and approximately 21.9% relative to the 24-observation moving average.

The active VM count was constant throughout the training and validation periods, resulting in zero validation error for persistence.

### 5.3 Normalized Error

The persistence model achieved a normalized MAE of approximately 2.152% of mean observed aggregate CPU utilization across the rolling validation records.

This provides a relative interpretation of forecast error in addition to absolute percentage-point metrics.

## 6. Forecast Error and Failure Analysis

### 6.1 Peak-Period Performance

A high-load threshold of 9.4857% aggregate CPU utilization was established using the 75th percentile of the first 38 training observations.

Forecast errors were then examined separately for higher-load and normal-load periods.

| Metric | High load | Normal load |
|---|---:|---:|
| Observations | 43 | 77 |
| MAE | 0.275301 | 0.163289 |
| RMSE | 0.310919 | 0.221728 |
| Mean signed error | -0.205634 | +0.151344 |

Signed error is defined as predicted minus actual utilization.

High-load MAE was approximately 69% greater than normal-load MAE.

The negative signed error during high-load periods indicates that the persistence model tended to underestimate elevated demand.

Conversely, it tended to overestimate demand during normal-load periods.

### 6.2 Largest Forecast Errors

The largest observed absolute error was approximately 0.638 percentage points at timestamp 22800 in the validation window starting after observation 62.

Other large errors occurred around timestamps 16500 and 17400, when aggregate utilization increased above the forecast.

These results illustrate a limitation of persistence: it cannot anticipate sudden increases or decreases in workload.

### 6.3 Model Limitations

The main limitations are:

- A relatively short training history of 110 observations.
- Limited evidence of recurring daily or weekly seasonality.
- Constant observed VM count, which makes churn forecasting trivial in this subset.
- Difficulty predicting rapid workload changes.
- Overlapping validation windows.
- No host-level capacity or service-level objective data.

These limitations reduce confidence in extrapolating performance to longer forecasting horizons or different cloud environments.

## 7. Capacity-Planning Recommendation

### 7.1 Aggregate CPU Safety Margin

A historical error-based safety margin was estimated using the 95th percentile of positive underprediction errors, after retaining one prediction per overlapping validation timestamp.

The resulting illustrative safety margin was approximately 0.393 percentage points.

Given the final aggregate CPU forecast of 9.164556%, the proposed planning target becomes approximately 9.5575%.

This margin provides a simple way to account for observed underprediction risk. It is not a calibrated prediction interval or a guarantee of sufficient physical capacity.

### 7.2 VM-Level Saturation Monitoring

Because individual VMs can experience high CPU utilization even when aggregate utilization is low, the infrastructure team should monitor VM-level saturation alongside the aggregate forecast.

The historical 95th-percentile count of VMs at or above 80% CPU was approximately 137.

A count above this historical reference level could trigger additional investigation into workload concentration and available headroom.

This threshold is an illustrative monitoring rule, not a validated production alert threshold.

### 7.3 Provisioning Trade-Offs

Under-provisioning can increase the risk of degraded application performance, resource contention and service-level objective violations.

Over-provisioning can lead to unnecessary infrastructure costs and inefficient resource utilization.

An appropriate operational policy should balance these risks using forecast errors, workload criticality, host capacity and actual service requirements.

## 8. Reproducibility and Engineering

The implementation uses Python, pandas and NumPy.

The project includes scripts for data exploration, preprocessing, forecasting, rolling validation, error analysis and capacity-planning analysis.

The final prediction generator reads the challenge release data and produces the required `predictions.csv` without manually editing forecast values.

The submission contains 24 chronologically ordered forecasts with the required columns:

`timestamp,active_vm_count,aggregate_cpu_utilization`

All submission-format checks passed, and the existing automated test suite reported two passing tests.

## 9. Limitations and Future Work

Future improvements could include:

- Evaluating additional models using longer historical periods.
- Building category-specific forecasting models.
- Estimating calibrated forecast uncertainty.
- Incorporating host-level capacity and workload placement constraints.
- Testing performance under VM arrivals, departures and irregular sampling.
- Investigating anomaly detection for sudden utilization spikes.
- Validating capacity policies against operational service-level objectives.

## 10. Conclusion

The challenge demonstrates that simple forecasting methods can provide useful near-term cloud workload predictions when supported by leakage-safe temporal validation.

Persistence was the strongest of the compared approaches on the available training windows.

However, forecasting aggregate utilization alone is insufficient for reliable capacity planning. VM-level utilization distributions and high-load behavior reveal operational risks that are not visible in the aggregate average.

A practical infrastructure decision system should therefore combine aggregate demand forecasts, historical error-based margins and monitoring of individual high-utilization VMs.