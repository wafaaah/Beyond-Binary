
import pandas as pd
import numpy as np
from pathlib import Path

# Project folder
project_root = Path(__file__).resolve().parents[1]

# Input and output files
input_path = (
    project_root / "data" / "processed" /
    "chattogram_weather_weekly.csv"
)

output_path = (
    project_root / "data" / "processed" /
    "api_weather_features.csv"
)

print("Loading weekly weather data...")

df = pd.read_csv(input_path)
df["date"] = pd.to_datetime(df["date"])
df = df.sort_values("date").reset_index(drop=True)

# Rainfall lag features: 2 to 8 weeks
for lag in range(2, 9):
    df[f"rain_lag_{lag}"] = df["rainfall_mm"].shift(lag)

# Temperature and humidity lag features
weather_variables = [
    "avg_temp_c",
    "min_temp_c",
    "max_temp_c",
    "relative_humidity_pct"
]

for variable in weather_variables:
    for lag in [2, 3, 4]:
        df[f"{variable}_lag_{lag}"] = df[variable].shift(lag)

# Rolling rainfall features
for window in [2, 4, 6]:
    df[f"rain_sum_{window}w"] = (
        df["rainfall_mm"]
        .shift(2)
        .rolling(window=window)
        .sum()
    )

# Seasonal features
week_number = df["date"].dt.isocalendar().week.astype(int)

df["week_sin"] = np.sin(2 * np.pi * week_number / 52.0)
df["week_cos"] = np.cos(2 * np.pi * week_number / 52.0)

# Required model features
feature_columns = (
    [f"rain_lag_{i}" for i in range(2, 9)]
    + [
        f"{variable}_lag_{lag}"
        for variable in weather_variables
        for lag in [2, 3, 4]
    ]
    + [
        "rain_sum_2w",
        "rain_sum_4w",
        "rain_sum_6w",
        "week_sin",
        "week_cos"
    ]
)

# Select the latest row with all required features
valid_rows = df.dropna(subset=feature_columns)

if valid_rows.empty:
    raise ValueError(
        "Not enough weekly weather data to create all features."
    )

latest = valid_rows.iloc[[-1]].copy()

# Save features
result = latest[["date"] + feature_columns]
result.to_csv(output_path, index=False)

print("\nFeatures created successfully!")
print("Forecast origin:", latest["date"].iloc[0].date())
print("Total features:", len(feature_columns))
print("Output shape:", result.shape)
print("\nSaved at:", output_path)
print("\nFeature preview:")
print(result.to_string(index=False))
