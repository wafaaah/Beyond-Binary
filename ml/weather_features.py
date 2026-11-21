
import numpy as np
import pandas as pd


# Weather-only input features
WEATHER_FEATURE_COLUMNS = (
    [f"rain_lag_{i}" for i in range(2, 9)]
    + [
        f"{variable}_lag_{lag}"
        for variable in ["avg_temp_c", "min_temp_c", "max_temp_c",
                         "relative_humidity_pct"]
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


def create_weather_features(df):

    df = df.copy()

    df["date"] = pd.to_datetime(df["date"])

    df = df.sort_values(
        ["ward_id", "date"]
    ).reset_index(drop=True)

    grouped = df.groupby("ward_id", group_keys=False)

    # 1. Rainfall lags: 2 to 8 weeks
    for lag in range(2, 9):
        df[f"rain_lag_{lag}"] = (
            grouped["rainfall_mm"].shift(lag)
        )

    # 2. Temperature and humidity lags: 2, 3, 4 weeks
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

    # 3. Rolling rainfall sums
    # Shift by 2 first: only information available
    # at least two weeks before the prediction target.

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

    # 4. Week-of-year cyclic encoding
    week_number = df["date"].dt.isocalendar().week.astype(int)

    df["week_sin"] = np.sin(
        2 * np.pi * week_number / 52.0
    )

    df["week_cos"] = np.cos(
        2 * np.pi * week_number / 52.0
    )

    # 5. Multi-horizon targets
    for horizon in [2, 3, 4]:

        df[f"target_{horizon}w"] = (
            grouped["dengue_cases"].shift(-horizon)
        )

        df[f"target_date_{horizon}w"] = (
            grouped["date"].shift(-horizon)
        )

    return df


def get_weather_features():

    return WEATHER_FEATURE_COLUMNS.copy()
