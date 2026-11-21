
import os
import joblib
import numpy as np
import pandas as pd

from sklearn.ensemble import HistGradientBoostingRegressor
from sklearn.metrics import (
    mean_absolute_error,
    mean_squared_error,
    r2_score
)

from ml.weather_features import (
    create_weather_features,
    get_all_features
)


# ==========================================
# 1. SETTINGS
# ==========================================

TRAIN_END = "2022-12-31"
TEST_START = "2024-07-01"

HIGH_CASE_THRESHOLD = 10

os.makedirs("models", exist_ok=True)
os.makedirs("data/processed", exist_ok=True)


# ==========================================
# 2. LOAD DATA
# ==========================================

print("Loading dataset...")

df = pd.read_csv(
    "data/processed/cleaned_dengue.csv"
)

featured_df = create_weather_features(df)

FEATURES = get_all_features()

print("Dataset loaded:", featured_df.shape)
print("Total features:", len(FEATURES))
print("Features:", FEATURES)


# ==========================================
# 3. MODEL CONFIGURATION
# ==========================================

def create_model():

    return HistGradientBoostingRegressor(
        loss="poisson",
        learning_rate=0.05,
        max_iter=300,
        max_leaf_nodes=15,
        min_samples_leaf=20,
        l2_regularization=1.0,
        random_state=42
    )


# ==========================================
# 4. MODEL EVALUATION
# ==========================================

def evaluate_model(actual, predicted):

    actual = np.asarray(actual)
    predicted = np.maximum(
        np.asarray(predicted),
        0
    )

    mae = mean_absolute_error(
        actual,
        predicted
    )

    rmse = np.sqrt(
        mean_squared_error(actual, predicted)
    )

    r2 = r2_score(actual, predicted)

    high_mask = actual >= HIGH_CASE_THRESHOLD

    if high_mask.sum() > 0:

        high_case_mae = mean_absolute_error(
            actual[high_mask],
            predicted[high_mask]
        )

    else:
        high_case_mae = np.nan

    return {
        "MAE": round(mae, 4),
        "RMSE": round(rmse, 4),
        "R2_Score": round(r2, 4),
        "High_Case_MAE": round(high_case_mae, 4),
        "High_Case_Count": int(high_mask.sum())
    }


# ==========================================
# 5. TRAIN THREE MODELS
# ==========================================

all_results = []
all_predictions = []

for horizon in [2, 3, 4]:

    print("\n" + "=" * 50)
    print(f"TRAINING {horizon}-WEEK MODEL")
    print("=" * 50)

    target_col = f"target_{horizon}w"
    target_date_col = f"target_date_{horizon}w"

    model_df = featured_df.dropna(
        subset=FEATURES + [
            target_col,
            target_date_col
        ]
    ).copy()

    model_df[target_date_col] = pd.to_datetime(
        model_df[target_date_col]
    )

    # Chronological split
    train_df = model_df[
        model_df[target_date_col] <= TRAIN_END
    ].copy()

    validation_df = model_df[
        (model_df[target_date_col] > TRAIN_END)
        & (model_df[target_date_col] < TEST_START)
    ].copy()

    test_df = model_df[
        model_df[target_date_col] >= TEST_START
    ].copy()

    print("Train rows:", len(train_df))
    print("Validation rows:", len(validation_df))
    print("Test rows:", len(test_df))

    if (
        train_df.empty
        or validation_df.empty
        or test_df.empty
    ):
        raise ValueError(
            f"Empty dataset split for {horizon}-week model."
        )

    # Features and targets
    X_train = train_df[FEATURES]
    y_train = train_df[target_col]

    X_val = validation_df[FEATURES]
    y_val = validation_df[target_col]

    X_test = test_df[FEATURES]
    y_test = test_df[target_col]

    # Train
    model = create_model()

    print("Training model...")

    model.fit(X_train, y_train)

    # Validation
    val_predictions = model.predict(X_val)

    validation_metrics = evaluate_model(
        y_val,
        val_predictions
    )

    # Test
    test_predictions = model.predict(X_test)

    test_metrics = evaluate_model(
        y_test,
        test_predictions
    )

    # Risk cutoffs
    risk_cutoffs = {
        "p50": float(y_train.quantile(0.50)),
        "p75": float(y_train.quantile(0.75)),
        "p90": float(y_train.quantile(0.90))
    }

    # Save model package
    model_path = (
        f"models/weather_model_{horizon}w.joblib"
    )

    model_package = {
        "model": model,
        "features": FEATURES,
        "horizon": horizon,
        "risk_cutoffs": risk_cutoffs,
        "high_case_threshold": HIGH_CASE_THRESHOLD
    }

    joblib.dump(
        model_package,
        model_path
    )

    print("\nValidation metrics:", validation_metrics)
    print("Test metrics:", test_metrics)
    print("Risk cutoffs:", risk_cutoffs)
    print("Saved:", model_path)

    all_results.append({
        "Horizon": f"{horizon} weeks",
        "Validation_MAE": validation_metrics["MAE"],
        "Validation_RMSE": validation_metrics["RMSE"],
        "Validation_R2": validation_metrics["R2_Score"],
        "Test_MAE": test_metrics["MAE"],
        "Test_RMSE": test_metrics["RMSE"],
        "Test_R2": test_metrics["R2_Score"],
        "Test_High_Case_MAE": test_metrics["High_Case_MAE"],
        "Test_High_Case_Count": test_metrics["High_Case_Count"]
    })

    prediction_df = pd.DataFrame({
        "ward_id": test_df["ward_id"].values,
        "forecast_origin": test_df["date"].values,
        "target_date": test_df[target_date_col].values,
        "weeks_ahead": horizon,
        "actual_cases": y_test.values,
        "predicted_cases": np.maximum(
            test_predictions,
            0
        )
    })

    all_predictions.append(prediction_df)


# ==========================================
# 6. SAVE RESULTS
# ==========================================

results_df = pd.DataFrame(all_results)

results_df.to_csv(
    "data/processed/weather_model_results.csv",
    index=False
)

predictions_df = pd.concat(
    all_predictions,
    ignore_index=True
)

predictions_df.to_csv(
    "data/processed/weather_model_predictions.csv",
    index=False
)


# ==========================================
# 7. FINAL COMPARISON
# ==========================================

print("\n" + "=" * 50)
print("FINAL MODEL COMPARISON")
print("=" * 50)

print(results_df.to_string(index=False))

print("\nSaved results:")
print("data/processed/weather_model_results.csv")
print("data/processed/weather_model_predictions.csv")

print("\nALL THREE MODELS TRAINED SUCCESSFULLY!")
