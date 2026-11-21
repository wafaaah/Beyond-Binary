
import joblib
import pandas as pd
import numpy as np
from pathlib import Path


# ==========================================
# 1. PROJECT PATHS
# ==========================================

project_root = Path(__file__).resolve().parents[1]

input_path = (
    project_root / "data" / "processed" /
    "api_weather_features.csv"
)

output_path = (
    project_root / "data" / "processed" /
    "api_weather_forecasts.csv"
)

models_path = project_root / "models"


# ==========================================
# 2. LOAD WARD FEATURES
# ==========================================

print("Loading ward-level API features...")

df = pd.read_csv(input_path)

df["date"] = pd.to_datetime(df["date"])

if df.empty:
    raise ValueError("No ward feature data found.")

required_columns = [
    "ward_id",
    "city",
    "date"
]

for column in required_columns:

    if column not in df.columns:
        raise ValueError(
            f"Required column missing: {column}"
        )

if df["ward_id"].duplicated().any():
    raise ValueError("Duplicate ward IDs found.")

if df.isnull().any().any():
    raise ValueError(
        "Missing values found in API feature data."
    )

print("Total wards:", df["ward_id"].nunique())

print("\nWards per city:")
print(df.groupby("city")["ward_id"].nunique())


# ==========================================
# 3. RISK CLASSIFICATION
# ==========================================

def classify_risk(predicted_cases):

    if predicted_cases < 1:
        return "Low"

    elif predicted_cases < 5:
        return "Medium"

    elif predicted_cases < 10:
        return "High"

    else:
        return "Critical"


# ==========================================
# 4. GENERATE PREDICTIONS
# ==========================================

all_predictions = []

for horizon in [2, 3, 4]:

    print("\n" + "=" * 50)
    print(f"PREDICTING {horizon}-WEEK DENGUE RISK")
    print("=" * 50)

    model_file = (
        models_path /
        f"weather_model_{horizon}w.joblib"
    )

    if not model_file.exists():

        raise FileNotFoundError(
            f"Model not found: {model_file}"
        )

    # Load trained model package

    model_data = joblib.load(model_file)

    model = model_data["model"]
    features = model_data["features"]

    # Validate model features

    missing_features = [
        feature for feature in features
        if feature not in df.columns
    ]

    if missing_features:

        raise ValueError(
            f"Missing model features: {missing_features}"
        )

    if len(features) != 27:

        raise ValueError(
            f"Expected 27 model features, "
            f"but model requires {len(features)}."
        )

    # Prepare input for all wards

    X = df[features].copy()

    if X.isnull().any().any():

        raise ValueError(
            "Missing values found in prediction input."
        )

    # Predict dengue cases

    predictions = model.predict(X)

    predictions = np.maximum(
        predictions,
        0
    )

    # Prepare forecast dates

    forecast_origin = df["date"]

    target_dates = (
        forecast_origin
        + pd.to_timedelta(horizon * 7, unit="D")
    )

    # Create result for each ward

    prediction_df = pd.DataFrame({

        "ward_id": df["ward_id"],

        "city": df["city"],

        "forecast_origin": forecast_origin,

        "target_date": target_dates,

        "weeks_ahead": horizon,

        "predicted_cases": np.round(
            predictions,
            2
        ),

        "risk_level": [
            classify_risk(value)
            for value in predictions
        ]

    })

    all_predictions.append(prediction_df)

    print("Model:", model_file.name)
    print("Model features:", len(features))
    print("Predicted wards:", len(prediction_df))

    print("\nRisk distribution:")

    print(
        prediction_df["risk_level"]
        .value_counts()
        .to_string()
    )


# ==========================================
# 5. COMBINE ALL PREDICTIONS
# ==========================================

final_df = pd.concat(
    all_predictions,
    ignore_index=True
)

final_df = final_df.sort_values(
    ["city", "ward_id", "weeks_ahead"]
).reset_index(drop=True)


# ==========================================
# 6. VALIDATE OUTPUT
# ==========================================

expected_rows = (
    df["ward_id"].nunique() * 3
)

if len(final_df) != expected_rows:

    raise ValueError(
        f"Expected {expected_rows} predictions, "
        f"but got {len(final_df)}."
    )

if final_df.duplicated(
    subset=["ward_id", "weeks_ahead"]
).any():

    raise ValueError(
        "Duplicate ward-horizon predictions found."
    )

# Validate city information

if final_df["city"].isnull().any():

    raise ValueError(
        "Missing city information in predictions."
    )

# Validate forecast dates

for horizon in [2, 3, 4]:

    subset = final_df[
        final_df["weeks_ahead"] == horizon
    ]

    expected_dates = (
        subset["forecast_origin"]
        + pd.to_timedelta(horizon * 7, unit="D")
    )

    if not (
        subset["target_date"].reset_index(drop=True)
        == expected_dates.reset_index(drop=True)
    ).all():

        raise ValueError(
            f"Incorrect target dates for {horizon}-week forecast."
        )


# ==========================================
# 7. SAVE FORECASTS
# ==========================================

final_df.to_csv(
    output_path,
    index=False
)

print("\n" + "=" * 50)
print("PREDICTION COMPLETED SUCCESSFULLY!")
print("=" * 50)

print("Total wards:", df["ward_id"].nunique())
print("Forecast horizons: 2, 3, 4 weeks")
print("Total predictions:", len(final_df))

print("\nPredictions per city:")
print(final_df.groupby("city").size())

print("\nForecast dates:")

print(
    final_df.groupby("weeks_ahead")["target_date"]
    .first()
)

print("\nRisk distribution by horizon:")

print(
    final_df.groupby(
        ["weeks_ahead", "risk_level"]
    ).size().to_string()
)

print("\nPrediction preview:")

print(
    final_df.head(15).to_string(index=False)
)

print("\nSaved at:")
print(output_path)
