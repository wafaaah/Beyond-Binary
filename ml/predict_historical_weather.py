
import joblib
import pandas as pd
import numpy as np
from pathlib import Path

from ml.weather_features import (
    create_weather_features,
    get_all_features
)


# =====================================
# 1. PROJECT PATHS
# =====================================

ROOT = Path(__file__).resolve().parents[1]

DATA_PATH = ROOT / "data" / "processed" / "cleaned_dengue.csv"
MODEL_PATH = ROOT / "models"

OUTPUT_PATH = (
    ROOT / "data" / "processed" /
    "historical_weather_forecasts.csv"
)


# =====================================
# 2. LOAD AND PROCESS DATA
# =====================================

print("Loading historical dengue data...")

df = pd.read_csv(DATA_PATH)

df["date"] = pd.to_datetime(df["date"])

df = create_weather_features(df)

features = get_all_features()

# Get latest complete weather record for each ward

latest = (
    df.sort_values(["ward_id", "date"])
    .groupby("ward_id")
    .tail(1)
    .copy()
)

if latest[features].isnull().any().any():
    raise ValueError("Missing features found.")

print("Total wards:", latest["ward_id"].nunique())
print("Latest data date:", latest["date"].max())


# =====================================
# 3. RISK CLASSIFICATION
# =====================================

def classify_risk(value):

    if value < 1:
        return "Low"

    elif value < 5:
        return "Medium"

    elif value < 10:
        return "High"

    else:
        return "Critical"


# =====================================
# 4. GENERATE MODEL PREDICTIONS
# =====================================

all_predictions = []

for horizon in [2, 3, 4]:

    print(f"\nGenerating {horizon}-week predictions...")

    model_file = (
        MODEL_PATH /
        f"weather_model_{horizon}w.joblib"
    )

    model_data = joblib.load(model_file)

    model = model_data["model"]
    model_features = model_data["features"]

    if model_features != features:
        raise ValueError(
            f"Feature mismatch for {horizon}-week model."
        )

    X = latest[model_features]

    predictions = np.maximum(
        model.predict(X),
        0
    )

    forecast = pd.DataFrame({

        "ward_id": latest["ward_id"].values,

        "city": latest["city"].values,

        "forecast_origin": latest["date"].values,

        "target_date": (
            latest["date"]
            + pd.to_timedelta(horizon * 7, unit="D")
        ).values,

        "weeks_ahead": horizon,

        "predicted_cases": np.round(
            predictions, 2
        ),

        "risk_level": [
            classify_risk(value)
            for value in predictions
        ],

        "forecast_source": "Historical weather data"

    })

    all_predictions.append(forecast)

    print("\nRisk distribution:")
    print(forecast["risk_level"].value_counts().to_string())


# =====================================
# 5. COMBINE AND SAVE
# =====================================

final_df = pd.concat(
    all_predictions,
    ignore_index=True
)

final_df = final_df.sort_values(
    ["city", "ward_id", "weeks_ahead"]
).reset_index(drop=True)

final_df.to_csv(
    OUTPUT_PATH,
    index=False
)

print("\n================================")
print("PREDICTION COMPLETED")
print("================================")

print("Total predictions:", len(final_df))

print("\nPredictions by horizon and risk:")

print(
    final_df.groupby(
        ["weeks_ahead", "risk_level"]
    ).size().to_string()
)

print("\nPreview:")
print(final_df.head(10).to_string(index=False))

print("\nSaved to:", OUTPUT_PATH)
