
import numpy as np
import pandas as pd

data = pd.read_csv("challenge_data/train_aggregate.csv")

history = data.iloc[:86].copy()
validation = data.iloc[86:110].copy()

target = "aggregate_cpu_utilization"

actual = validation[target].to_numpy()
values = history[target].to_numpy()

horizon = len(validation)

# Model 1: Persistence
persistence = np.repeat(values[-1], horizon)

# Model 2: Moving average (last 12 readings)
moving_average = np.repeat(
    np.mean(values[-12:]),
    horizon
)

# Model 3: Linear trend (last 24 readings)
recent = values[-24:]
x = np.arange(len(recent))

slope, intercept = np.polyfit(x, recent, 1)

future_x = np.arange(
    len(recent),
    len(recent) + horizon
)

linear_trend = np.clip(
    slope * future_x + intercept,
    0,
    100
)

def evaluate(predictions):
    mae = np.mean(np.abs(actual - predictions))
    rmse = np.sqrt(np.mean((actual - predictions) ** 2))
    return mae, rmse

models = {
    "Persistence": persistence,
    "Moving Average": moving_average,
    "Linear Trend": linear_trend
}

print("=== CPU FORECAST MODEL COMPARISON ===")

for name, predictions in models.items():
    mae, rmse = evaluate(predictions)
    print(f"{name}: MAE={mae:.6f}, RMSE={rmse:.6f}")
