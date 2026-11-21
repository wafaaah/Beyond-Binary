import pandas as pd

FEATURE_COLUMNS = [
    "population_density_sqkm",
    "water_logging_risk_index",
    "sanitation_score",
    "avg_temp_c",
    "max_temp_c",
    "min_temp_c",
    "rainfall_mm",
    "relative_humidity_pct",
    "cases_lag_1",
    "cases_lag_2",
    "cases_lag_3",
    "rain_lag_1",
    "rain_lag_2",
    "cases_rolling_mean_3",
    "rain_rolling_mean_3",
    "month"
]

def create_features(df):
    df = df.copy()

    df["date"] = pd.to_datetime(df["date"])
    df = df.sort_values(["ward_id", "date"])

    grouped = df.groupby("ward_id", group_keys=False)

    # Historical case features
    df["cases_lag_1"] = grouped["dengue_cases"].shift(1)
    df["cases_lag_2"] = grouped["dengue_cases"].shift(2)
    df["cases_lag_3"] = grouped["dengue_cases"].shift(3)

    # Historical rainfall features
    df["rain_lag_1"] = grouped["rainfall_mm"].shift(1)
    df["rain_lag_2"] = grouped["rainfall_mm"].shift(2)

    # Rolling averages use previous observations only
    df["cases_rolling_mean_3"] = (
        grouped["dengue_cases"]
        .transform(lambda s: s.shift(1).rolling(3).mean())
    )

    df["rain_rolling_mean_3"] = (
        grouped["rainfall_mm"]
        .transform(lambda s: s.shift(1).rolling(3).mean())
    )

    df["month"] = df["date"].dt.month

    # Predict the next observation's cases
    df["target_next"] = grouped["dengue_cases"].shift(-1)

    # Target date: date of the next observation
    df["target_date"] = grouped["date"].shift(-1)

    return df


def get_model_features():
    return FEATURE_COLUMNS.copy()