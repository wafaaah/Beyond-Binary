
import streamlit as st
import pandas as pd
from pathlib import Path


# --------------------------------
# DATASET LOCATION
# --------------------------------

BASE_DIR = Path(__file__).resolve().parent

DATA_PATH = BASE_DIR / "data" / "dengue_dataset.csv"

# --------------------------------
# LOAD REAL DATA
# --------------------------------

@st.cache_data
def load_data():

    if not DATA_PATH.exists():
        raise FileNotFoundError(
            f"CSV not found at: {DATA_PATH}"
        )

    df = pd.read_csv(DATA_PATH)

    # Standardize column names
    df.columns = df.columns.str.strip().str.lower()

    required_columns = [
        "date",
        "city",
        "ward_id",
        "population_density_sqkm",
        "water_logging_risk_index",
        "sanitation_score",
        "avg_temp_c",
        "max_temp_c",
        "min_temp_c",
        "rainfall_mm",
        "relative_humidity_pct",
        "dengue_cases"
    ]

    missing = [
        column for column in required_columns
        if column not in df.columns
    ]

    if missing:
        raise ValueError(
            f"Missing required dataset columns: {missing}"
        )

    # Convert data types
    df["date"] = pd.to_datetime(
        df["date"],
        errors="coerce"
    )

    numeric_columns = [
        "population_density_sqkm",
        "water_logging_risk_index",
        "sanitation_score",
        "avg_temp_c",
        "max_temp_c",
        "min_temp_c",
        "rainfall_mm",
        "relative_humidity_pct",
        "dengue_cases"
    ]

    for column in numeric_columns:
        df[column] = pd.to_numeric(
            df[column],
            errors="coerce"
        )

    df = df.dropna(
        subset=[
            "date",
            "city",
            "ward_id",
            "dengue_cases"
        ]
    )

    df = df.sort_values(
        ["city", "ward_id", "date"]
    ).reset_index(drop=True)

    return df


# --------------------------------
# FILTER DATA
# --------------------------------

def filter_data(df, city, ward, start_date, end_date):

    filtered = df[
        (df["city"] == city) &
        (df["date"] >= pd.Timestamp(start_date)) &
        (df["date"] <= pd.Timestamp(end_date))
    ].copy()

    if ward != "All Wards":
        filtered = filtered[
            filtered["ward_id"] == ward
        ]

    return filtered


# --------------------------------
# HISTORICAL SUMMARY
# --------------------------------

def get_summary(df):

    return {
        "total_cases": int(df["dengue_cases"].sum()),
        "total_records": len(df),
        "total_wards": df["ward_id"].nunique(),
        "avg_rainfall": round(
            df["rainfall_mm"].mean(), 2
        ),
        "avg_temperature": round(
            df["avg_temp_c"].mean(), 2
        ),
        "avg_humidity": round(
            df["relative_humidity_pct"].mean(), 2
        )
    }


# --------------------------------
# MONTHLY CASE DATA
# --------------------------------

def get_monthly_cases(df):

    monthly = df.copy()

    monthly["month"] = (
        monthly["date"].dt.to_period("M").dt.to_timestamp()
    )

    result = (
        monthly.groupby("month", as_index=False)
        ["dengue_cases"].sum()
    )

    return result


# --------------------------------
# WEATHER DATA
# --------------------------------

def get_weather_data(df):

    weather = df.copy()

    weather["week"] = weather["date"]

    result = (
        weather.groupby("week", as_index=False)
        .agg({
            "rainfall_mm": "mean",
            "avg_temp_c": "mean",
            "relative_humidity_pct": "mean"
        })
    )

    return result


# --------------------------------
# HISTORICAL WARD RANKING
# --------------------------------

def get_ward_ranking(df):

    ranking = (
        df.groupby(
            ["city", "ward_id"],
            as_index=False
        )
        .agg(
            historical_cases=("dengue_cases", "sum"),
            avg_rainfall=("rainfall_mm", "mean"),
            waterlogging=("water_logging_risk_index", "mean"),
            population_density=("population_density_sqkm", "mean"),
            sanitation=("sanitation_score", "mean")
        )
        .sort_values(
            "historical_cases",
            ascending=False
        )
    )

    return ranking


# --------------------------------
# SELECTED WARD PROFILE
# --------------------------------

def get_ward_profile(df):

    if df.empty:
        return {}

    return {
        "population_density": round(
            df["population_density_sqkm"].mean(), 2
        ),
        "waterlogging": round(
            df["water_logging_risk_index"].mean(), 2
        ),
        "sanitation": round(
            df["sanitation_score"].mean(), 2
        ),
        "historical_cases": int(
            df["dengue_cases"].sum()
        )
    }
