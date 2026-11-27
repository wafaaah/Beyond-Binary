"""Offline forecasting and constrained resource allocation."""
from pathlib import Path

import joblib
import numpy as np
import pandas as pd

from ml.weather_features import create_weather_features

ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = ROOT / "data" / "raw" / "dengue_dataset_onsite.csv"
MODEL_DIR = ROOT / "models"
BACKUP_PATH = ROOT / "data" / "processed" / "weather_model_predictions.csv"
TEST_START = pd.Timestamp("2024-07-01")

# Demand per predicted case, derived from the onsite dataset
FACTORS = {
    "saline_bags": 2.385,
    "diagnostic_kits": 1.165,
    "hospital_beds": 0.298,
}
NEEDED = {
    "saline_bags": "saline_bags_needed",
    "diagnostic_kits": "diagnostic_kits_needed",
    "hospital_beds": "hospital_beds_required",
}
# Assumptions (not in the dataset)
CREWS_REQUIRED = {"Low": 0, "Medium": 1, "High": 2, "Critical": 3}
RISK_RANK = {"Low": 0, "Medium": 1, "High": 2, "Critical": 3}


def classify_risk(cases):
    if cases < 1:
        return "Low"
    if cases < 5:
        return "Medium"
    if cases < 10:
        return "High"
    return "Critical"


def load_data():
    return pd.read_csv(DATA_PATH, parse_dates=["date"])


def available_weeks(data, horizon=2):
    """Forecast origin dates whose target week is in the test period."""
    start = TEST_START - pd.Timedelta(weeks=horizon)
    end = data["date"].max() - pd.Timedelta(weeks=horizon)
    dates = data.loc[data["date"].between(start, end), "date"]
    return sorted(dates.unique())


def peak_week(data, horizon=2):
    """Origin date whose target week had the most actual cases (for demos)."""
    totals = data.groupby("date")["dengue_cases"].sum()
    weeks = available_weeks(data, horizon)
    return max(
        weeks,
        key=lambda d: totals.get(pd.Timestamp(d) + pd.Timedelta(weeks=horizon), 0),
    )


def forecast(data, origin_date, horizon=2):
    """Run the local model. Falls back to saved predictions if it fails."""
    origin_date = pd.Timestamp(origin_date)
    wards = data.loc[
        data["date"] == origin_date,
        ["ward_id", "city", "population_density_sqkm",
         "water_logging_risk_index", "sanitation_score"],
    ].copy()
    if wards.empty:
        raise ValueError(f"No data for week {origin_date.date()}")

    try:
        package = joblib.load(MODEL_DIR / f"weather_model_{horizon}w.joblib")
        features = create_weather_features(data)
        rows = features[features["date"] == origin_date].set_index("ward_id")
        X = rows.loc[wards["ward_id"], package["features"]]
        if X.isnull().any().any():
            raise ValueError("Not enough weather history for this week")
        predictions = package["model"].predict(X)
        source = "local model"
    except Exception as error:
        saved = pd.read_csv(BACKUP_PATH, parse_dates=["forecast_origin"])
        saved = saved[
            (saved["forecast_origin"] == origin_date)
            & (saved["weeks_ahead"] == horizon)
        ].set_index("ward_id")
        if not wards["ward_id"].isin(saved.index).all():
            raise RuntimeError(f"Forecast unavailable: {error}") from error
        predictions = saved.loc[wards["ward_id"], "predicted_cases"].values
        source = "saved predictions (model fallback)"

    wards["predicted_cases"] = np.maximum(predictions, 0).round(2)
    wards["risk_level"] = wards["predicted_cases"].apply(classify_risk)
    wards["forecast_origin"] = origin_date
    wards["target_date"] = origin_date + pd.Timedelta(weeks=horizon)
    wards["forecast_source"] = source
    return wards.reset_index(drop=True)


def add_demand(forecasts):
    df = forecasts.copy()
    for item, factor in FACTORS.items():
        df[NEEDED[item]] = (df["predicted_cases"] * factor).round().astype(int)
    df["crews_required"] = df["risk_level"].map(CREWS_REQUIRED).astype(int)
    return df


def allocate(forecasts, stock_pct=100, total_crews=20):
    """
    Allocate scarce supplies and crews.

    Supplies: each city is a separate pool holding stock_pct % of its demand.
    Crews: one shared pool across all cities.
    Priority: risk level, then population density, then predicted cases.
    """
    if not 0 <= stock_pct <= 100:
        raise ValueError("stock_pct must be between 0 and 100")
    if total_crews < 0:
        raise ValueError("total_crews cannot be negative")

    df = add_demand(forecasts)
    df["_rank"] = df["risk_level"].map(RISK_RANK)
    df = df.sort_values(
        ["_rank", "population_density_sqkm", "predicted_cases", "ward_id"],
        ascending=[False, False, False, True],
    ).reset_index(drop=True)
    df["priority_rank"] = np.arange(1, len(df) + 1)

    # Supplies: fill wards in priority order until the city pool is empty
    for item, need_col in NEEDED.items():
        allocated = pd.Series(0, index=df.index)
        for _, group in df.groupby("city"):
            stock = int(group[need_col].sum() * stock_pct // 100)
            for i, need in group[need_col].items():
                give = min(int(need), stock)
                allocated[i] = give
                stock -= give
        df[f"{item}_allocated"] = allocated
        df[f"{item}_deficit"] = df[need_col] - allocated

    # Crews: first one crew per ward in need, then top up in priority order
    df["crews_allocated"] = 0
    remaining = int(total_crews)
    for i in df.index:
        if remaining and df.at[i, "crews_required"] > 0:
            df.at[i, "crews_allocated"] = 1
            remaining -= 1
    for i in df.index:
        extra = min(
            df.at[i, "crews_required"] - df.at[i, "crews_allocated"], remaining
        )
        df.at[i, "crews_allocated"] += extra
        remaining -= extra
    df["crews_deficit"] = df["crews_required"] - df["crews_allocated"]

    labels = {
        "saline_bags_deficit": "saline bags",
        "diagnostic_kits_deficit": "diagnostic kits",
        "hospital_beds_deficit": "beds",
        "crews_deficit": "crews",
    }
    df["deficit_alert"] = df.apply(
        lambda r: ", ".join(
            f"{int(r[c])} {name}" for c, name in labels.items() if r[c] > 0
        ),
        axis=1,
    ).map(lambda s: f"DEFICIT: {s}" if s else "")
    return df.drop(columns="_rank")


def city_summary(allocation):
    """Demand, allocation and deficit totals per city."""
    columns = list(NEEDED.values()) + ["crews_required", "crews_allocated",
                                       "crews_deficit"]
    for item in NEEDED:
        columns += [f"{item}_allocated", f"{item}_deficit"]
    return allocation.groupby("city")[columns].sum().reset_index()


if __name__ == "__main__":
    data = load_data()
    week = peak_week(data)
    result = allocate(forecast(data, week), stock_pct=60, total_crews=20)
    print("Origin week:", pd.Timestamp(week).date(),
          "| source:", result["forecast_source"].iloc[0])
    print(result[["priority_rank", "ward_id", "risk_level", "predicted_cases",
                  "saline_bags_needed", "saline_bags_allocated",
                  "crews_allocated"]].head(10).to_string(index=False))
    print(city_summary(result).T.to_string())
