
import pandas as pd
from pathlib import Path

# Project folder
project_root = Path(__file__).resolve().parents[1]

# Read daily API data
input_path = (
    project_root / "data" / "raw" /
    "chattogram_weather_api.csv"
)

df = pd.read_csv(input_path)

# Convert date column
df["date"] = pd.to_datetime(df["date"])

# Find Monday of each week
df["week_start"] = (
    df["date"] -
    pd.to_timedelta(df["date"].dt.day_of_week, unit="D")
)

# Weekly aggregation
weekly = df.groupby("week_start").agg(
    rainfall_mm=("rainfall_mm", "sum"),
    avg_temp_c=("avg_temp_c", "mean"),
    min_temp_c=("min_temp_c", "mean"),
    max_temp_c=("max_temp_c", "mean"),
    relative_humidity_pct=("relative_humidity_pct", "mean"),
    days_count=("date", "count")
).reset_index()

# Keep only complete weeks
weekly = weekly[weekly["days_count"] == 7].copy()

# Remove helper column
weekly = weekly.drop(columns=["days_count"])

# Rename date column
weekly = weekly.rename(columns={"week_start": "date"})

# Round values
numeric_columns = [
    "rainfall_mm",
    "avg_temp_c",
    "min_temp_c",
    "max_temp_c",
    "relative_humidity_pct"
]

weekly[numeric_columns] = weekly[numeric_columns].round(2)

# Save weekly CSV
output_path = (
    project_root / "data" / "processed" /
    "chattogram_weather_weekly.csv"
)

output_path.parent.mkdir(parents=True, exist_ok=True)

weekly.to_csv(output_path, index=False)

print("Weekly weather data created successfully!")
print("Total complete weeks:", len(weekly))

print("\nWeekly data:")
print(weekly.to_string(index=False))

print("\nColumns:")
print(weekly.columns.tolist())

print("\nSaved at:", output_path)
