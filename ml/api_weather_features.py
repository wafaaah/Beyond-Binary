
import pandas as pd
import numpy as np
from pathlib import Path


# ==========================================
# 1. PROJECT PATHS
# ==========================================

project_root = Path(__file__).resolve().parents[1]

weather_path = (
    project_root / "data" / "processed" /
    "city_weather_weekly.csv"
)

ward_data_path = (
    project_root / "data" / "processed" /
    "cleaned_dengue.csv"
)

output_path = (
    project_root / "data" / "processed" /
    "api_weather_features.csv"
)


# ==========================================
# 2. LOAD WEATHER DATA
# ==========================================

print("Loading city-wise weekly weather data...")

weather_df = pd.read_csv(weather_path)

weather_df["date"] = pd.to_datetime(
    weather_df["date"]
)

required_weather_columns = [
    "date",
    "city",
    "rainfall_mm",
    "avg_temp_c",
    "min_temp_c",
    "max_temp_c",
    "relative_humidity_pct"
]

missing_columns = [
    col for col in required_weather_columns
    if col not in weather_df.columns
]

if missing_columns:
    raise ValueError(
        f"Missing weather columns: {missing_columns}"
    )

weather_df = weather_df.sort_values(
    ["city", "date"]
).reset_index(drop=True)


# ==========================================
# 3. WEATHER FEATURE DEFINITIONS
# ==========================================

weather_variables = [
    "avg_temp_c",
    "min_temp_c",
    "max_temp_c",
    "relative_humidity_pct"
]

weather_feature_columns = (
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


# ==========================================
# 4. CREATE FEATURES SEPARATELY PER CITY
# ==========================================

print("\nCreating weather features for each city...")

city_weather_features = []

for city in weather_df["city"].unique():

    print(f"Processing {city}...")

    city_df = (
        weather_df[weather_df["city"] == city]
        .copy()
        .sort_values("date")
        .reset_index(drop=True)
    )

    # Rainfall lags: 2 to 8 weeks

    for lag in range(2, 9):

        city_df[f"rain_lag_{lag}"] = (
            city_df["rainfall_mm"].shift(lag)
        )

    # Temperature and humidity lags

    for variable in weather_variables:

        for lag in [2, 3, 4]:

            city_df[f"{variable}_lag_{lag}"] = (
                city_df[variable].shift(lag)
            )

    # Rolling rainfall sums

    for window in [2, 4, 6]:

        city_df[f"rain_sum_{window}w"] = (
            city_df["rainfall_mm"]
            .shift(2)
            .rolling(
                window=window,
                min_periods=window
            )
            .sum()
        )

    # Seasonal features

    week_number = (
        city_df["date"]
        .dt.isocalendar()
        .week.astype(int)
    )

    city_df["week_sin"] = np.sin(
        2 * np.pi * week_number / 52.0
    )

    city_df["week_cos"] = np.cos(
        2 * np.pi * week_number / 52.0
    )

    # Select latest valid row for this city

    valid_rows = city_df.dropna(
        subset=weather_feature_columns
    )

    if valid_rows.empty:

        raise ValueError(
            f"Not enough weekly weather data for {city}."
        )

    latest_city_weather = valid_rows.iloc[[-1]].copy()

    latest_city_weather["city"] = city

    city_weather_features.append(
        latest_city_weather[
            ["city", "date"] + weather_feature_columns
        ]
    )

# Combine all city-wise weather features

city_features = pd.concat(
    city_weather_features,
    ignore_index=True
)

print("\nCity weather feature generation completed!")

print("\nWeather forecast origins:")

print(
    city_features[["city", "date"]]
    .to_string(index=False)
)


# ==========================================
# 5. LOAD WARD INFORMATION
# ==========================================

print("\nLoading ward information...")

ward_df = pd.read_csv(ward_data_path)

ward_columns = [
    "ward_id",
    "city",
    "population_density_sqkm",
    "water_logging_risk_index",
    "sanitation_score"
]

missing_columns = [
    col for col in ward_columns
    if col not in ward_df.columns
]

if missing_columns:

    raise ValueError(
        f"Missing ward columns: {missing_columns}"
    )


# Check whether each ward belongs to one city

city_counts = (
    ward_df.groupby("ward_id")["city"]
    .nunique()
)

if (city_counts > 1).any():

    raise ValueError(
        "Some ward IDs belong to multiple cities."
    )


# Check whether ward attributes remain constant

ward_attribute_columns = [
    "population_density_sqkm",
    "water_logging_risk_index",
    "sanitation_score"
]

attribute_counts = (
    ward_df.groupby("ward_id")[ward_attribute_columns]
    .nunique()
)

if (attribute_counts > 1).any().any():

    raise ValueError(
        "Ward attributes change across historical records. "
        "Please inspect ward-level attributes before continuing."
    )


# Extract one record per ward

ward_info = (
    ward_df[ward_columns]
    .drop_duplicates(subset=["ward_id"])
    .copy()
)

if ward_info["ward_id"].duplicated().any():

    raise ValueError("Duplicate ward IDs found.")

if ward_info[ward_columns].isnull().any().any():

    raise ValueError(
        "Missing values found in ward information."
    )


# ==========================================
# 6. COMBINE CITY WEATHER WITH WARDS
# ==========================================

print("\nCombining city weather with ward information...")

result = pd.merge(
    ward_info,
    city_features,
    on="city",
    how="left",
    validate="many_to_one"
)

if result["date"].isnull().any():

    raise ValueError(
        "Weather data not found for one or more cities."
    )


# Arrange final feature columns

result = result[
    ["ward_id", "city", "date"]
    + weather_feature_columns
    + ward_attribute_columns
]

result = result.sort_values(
    ["city", "ward_id"]
).reset_index(drop=True)


# ==========================================
# 7. VALIDATION
# ==========================================

if result["ward_id"].nunique() != len(result):

    raise ValueError(
        "Each ward must have exactly one prediction input row."
    )

if result.isnull().any().any():

    raise ValueError(
        "Missing values found in final API features."
    )

expected_cities = {
    "Chattogram",
    "Dhaka North",
    "Dhaka South",
    "Gazipur",
    "Narayanganj"
}

actual_cities = set(result["city"].unique())

if actual_cities != expected_cities:

    raise ValueError(
        f"City mismatch. Found: {actual_cities}"
    )

if len(result) != 60:

    raise ValueError(
        f"Expected 60 wards, but found {len(result)}."
    )

print("\nWard feature generation successful!")

print("Number of wards:", result["ward_id"].nunique())
print("Total rows:", len(result))

print(
    "Weather features:",
    len(weather_feature_columns)
)

print("Ward-specific features:", len(ward_attribute_columns))

print(
    "Total model features:",
    len(weather_feature_columns) + len(ward_attribute_columns)
)

print("\nWards per city:")
print(result.groupby("city")["ward_id"].nunique())

print("\nWeather origin per city:")
print(
    result.groupby("city")["date"]
    .first()
    .to_string()
)


# ==========================================
# 8. SAVE OUTPUT
# ==========================================

result.to_csv(
    output_path,
    index=False
)

print("\nSaved at:", output_path)

print("\nFeature preview:")
print(result.head(10).to_string(index=False))
