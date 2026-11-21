
import os
import joblib
import numpy as np
import pandas as pd

from ml.weather_features import (
    create_weather_features
)


# =====================================
# 1. SETTINGS
# =====================================

INPUT_FILE = "data/processed/cleaned_dengue.csv"

OUTPUT_FILE = (
    "data/processed/latest_weather_forecasts.csv"
)

HORIZONS = [2, 3, 4]


# =====================================
# 2. RISK CLASSIFICATION
# =====================================

def classify_risk(predicted_cases):

    if predicted_cases < 1:
        return "Low"

    elif predicted_cases < 5:
        return "Medium"

    elif predicted_cases < 10:
        return "High"

    else:
        return "Critical"


# =====================================
# 3. LOAD LATEST WEATHER DATA
# =====================================

def generate_predictions():

    print("Loading weather dataset...")

    df = pd.read_csv(INPUT_FILE)

    featured_df = create_weather_features(df)

    featured_df["date"] = pd.to_datetime(
        featured_df["date"]
    )

    latest_data = (
        featured_df
        .sort_values("date")
        .groupby("ward_id")
        .tail(1)
        .copy()
    )

    print("Total wards:", latest_data["ward_id"].nunique())

    all_predictions = []


    # =====================================
    # 4. LOAD MODELS AND PREDICT
    # =====================================

    for horizon in HORIZONS:

        print(f"\nGenerating {horizon}-week forecast...")

        model_path = (
            f"models/weather_model_{horizon}w.joblib"
        )

        package = joblib.load(model_path)

        model = package["model"]

        features = package["features"]

        # Verify required features
        missing = set(features) - set(latest_data.columns)

        if missing:
            raise ValueError(
                f"Missing features: {missing}"
            )

        X = latest_data[features]

        if X.isna().any().any():
            raise ValueError(
                "Missing values found in prediction input."
            )

        predicted = model.predict(X)

        predicted = np.maximum(predicted, 0)

        forecast_origin = latest_data["date"]

        target_date = (
            forecast_origin
            + pd.to_timedelta(horizon, unit="W")
        )

        result = pd.DataFrame({

            "ward_id": latest_data["ward_id"].values,

            "forecast_origin": forecast_origin.values,

            "target_date": target_date.values,

            "weeks_ahead": horizon,

            "predicted_cases": predicted,

        })

        result["risk_level"] = (
            result["predicted_cases"]
            .apply(classify_risk)
        )

        all_predictions.append(result)

        print("Ward count:", len(result))

        print(
            "Average predicted cases:",
            round(result["predicted_cases"].mean(), 2)
        )


    # =====================================
    # 5. SAVE FORECASTS
    # =====================================

    final_df = pd.concat(
        all_predictions,
        ignore_index=True
    )

    os.makedirs(
        "data/processed",
        exist_ok=True
    )

    final_df.to_csv(
        OUTPUT_FILE,
        index=False
    )

    print("\nPrediction completed successfully!")

    print("Total forecast records:", len(final_df))

    print("\nRisk distribution:")

    print(
        final_df.groupby(
            ["weeks_ahead", "risk_level"]
        ).size()
    )

    print("\nSaved:", OUTPUT_FILE)


# =====================================
# 6. RUN
# =====================================

if __name__ == "__main__":

    generate_predictions()
