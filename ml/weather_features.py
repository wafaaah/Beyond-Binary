
import numpy as np
import pandas as pd


# ==========================================
# 1. WEATHER FEATURES
# ==========================================

WEATHER_FEATURE_COLUMNS = (
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


# ==========================================
# 2. WARD-SPECIFIC FEATURES
# ==========================================

WARD_FEATURE_COLUMNS = [
    "population_density_sqkm",
    "water_logging_risk_index",
    "sanitation_score"
]


# ==========================================
# 3. COMPLETE MODEL FEATURES
# ==========================================

def get_weather_features():

    return WEATHER_FEATURE_COLUMNS.copy()


def get_ward_features():

    return WARD_FEATURE_COLUMNS.copy()


def get_all_features():

    return WEATHER_FEATURE_COLUMNS + WARD_FEATURE_COLUMNS


# ==========================================
# 4. FEATURE ENGINEERING
# ==========================================

def create_weather_features(df):

    df = df.copy()

    required_columns = [
        "date",
        "ward_id",
        "rainfall_mm",
        "avg_temp_c",
        "min_temp_c",
        "max_temp_c",
        "relative_humidity_pct",
        "dengue_cases"
    ] + WARD_FEATURE_COLUMNS

    missing_columns = [
        column for column in required_columns
        if column not in df.columns
    ]

    if missing_columns:
        raise ValueError(
            f"Missing dataset columns: {missing_columns}"
        )

    df["date"] = pd.to_datetime(df["date"])

    df = df.sort_values(
        ["ward_id", "date"]
    ).reset_index(drop=True)

    grouped = df.groupby("ward_id", group_keys=False)

    # Rainfall lags: 2 to 8 weeks
    for lag in range(2, 9):

        df[f"rain_lag_{lag}"] = (
            grouped["rainfall_mm"].shift(lag)
        )

    # Temperature and humidity lags
    weather_variables = [
        "avg_temp_c",
        "min_temp_c",
        "max_temp_c",
        "relative_humidity_pct"
    ]

    for variable in weather_variables:

        for lag in [2, 3, 4]:

            df[f"{variable}_lag_{lag}"] = (
                grouped[variable].shift(lag)
            )

    # Rolling rainfall sums
    for window in [2, 4, 6]:

        df[f"rain_sum_{window}w"] = (
            grouped["rainfall_mm"]
            .transform(
                lambda s: s.shift(2).rolling(
                    window=window,
                    min_periods=window
                ).sum()
            )
        )

    # Week-of-year encoding
    week_number = (
        df["date"].dt.isocalendar().week.astype(int)
    )

    df["week_sin"] = np.sin(
        2 * np.pi * week_number / 52.0
    )

    df["week_cos"] = np.cos(
        2 * np.pi * week_number / 52.0
    )

    # Multi-horizon targets
    for horizon in [2, 3, 4]:

        df[f"target_{horizon}w"] = (
            grouped["dengue_cases"].shift(-horizon)
        )

        df[f"target_date_{horizon}w"] = (
            grouped["date"].shift(-horizon)
        )

    return df
