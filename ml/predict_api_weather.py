
import pandas as pd
import joblib
from pathlib import Path

# Project directory
project_root = Path(__file__).resolve().parents[1]

# File paths
input_path = (
    project_root / "data" / "processed" /
    "api_weather_features.csv"
)

output_path = (
    project_root / "data" / "processed" /
    "api_weather_forecasts.csv"
)

model_dir = project_root / "models"

print("Loading API weather features...")

df = pd.read_csv(input_path)
forecast_origin = pd.to_datetime(df["date"].iloc[0])

# Model input columns
feature_columns = (
    [f"rain_lag_{i}" for i in range(2, 9)]
    + [
        f"{variable}_lag_{lag}"
        for variable in [
            "avg_temp_c",
            "min_temp_c",
            "max_temp_c",
            "relative_humidity_pct"
        ]
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

X = df[feature_columns]

# Load trained models
horizons = [2, 3, 4]
results = []

print("Generating predictions...")

for horizon in horizons:

    model_path = (
        model_dir / f"weather_model_{horizon}w.joblib"
    )

    # Load saved model package
    model_data = joblib.load(model_path)

    # Extract trained model and feature names
    model = model_data["model"]
    model_features = model_data["features"]

    # Check required features
    missing_features = [
        col for col in model_features
        if col not in X.columns
    ]

    if missing_features:
        raise ValueError(
            f"Missing features for {horizon}w model: "
            f"{missing_features}"
        )

    # Generate prediction
    prediction = float(
        model.predict(X[model_features])[0]
    )

    prediction = max(0, prediction)

    # Use saved risk cutoffs
    risk_cutoffs = model_data["risk_cutoffs"]

    if prediction < 1:
        risk = "Low"
    elif prediction < 5:
        risk = "Medium"
    elif prediction < 10:
        risk = "High"
    else:
        risk = "Critical"
    # Calculate target date
    target_date = (
        forecast_origin + pd.Timedelta(weeks=horizon)
    )

    results.append({
        "forecast_origin": forecast_origin.date(),
        "horizon_weeks": horizon,
        "target_date": target_date.date(),
        "predicted_cases": round(prediction, 2),
        "risk_level": risk
    })

# Create results DataFrame
result_df = pd.DataFrame(results)

# Save predictions
result_df.to_csv(output_path, index=False)

print("\nAPI-based predictions completed!")
print("\nForecast results:")
print(result_df.to_string(index=False))

print("\nSaved at:", output_path)
