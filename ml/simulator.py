"""What-if vector control simulator (model-driven counterfactual, offline)."""
import joblib
import numpy as np
import pandas as pd

from ml.allocation import FACTORS, MODEL_DIR, available_weeks
from ml.weather_features import create_weather_features

HORIZONS = (2, 3, 4)
CREW_EFFECT = 0.25  # assumption: share of remaining ward risk fixed per crew


def simulation_weeks(data):
    return sorted(set(available_weeks(data, 2)) & set(available_weeks(data, 4)))


def apply_crews(rows, crews, effect=CREW_EFFECT):
    """Lower water logging and raise sanitation according to crews per ward."""
    out = rows.copy()
    n = out.index.to_series().map(crews).fillna(0).astype(float)
    remaining = (1 - effect) ** n
    out["water_logging_risk_index"] = out["water_logging_risk_index"] * remaining
    out["sanitation_score"] = 1 - (1 - out["sanitation_score"]) * remaining
    return out


def prepare(data, origin_date):
    """Features for one week plus the three local models."""
    features = create_weather_features(data)
    rows = features[features["date"] == pd.Timestamp(origin_date)]
    rows = rows.set_index("ward_id")
    models = {
        h: joblib.load(MODEL_DIR / f"weather_model_{h}w.joblib")
        for h in HORIZONS
    }
    return rows, models


def simulate(rows, models, crews, effect=CREW_EFFECT):
    """
    Baseline vs intervention for 2, 3 and 4 weeks ahead.

    crews: {ward_id: number of crews}. A scenario is never allowed to exceed
    the baseline (small model irregularities are clipped to zero reduction).
    """
    changed = apply_crews(rows, crews, effect)
    results = []
    for horizon, package in models.items():
        names = package["features"]
        base = np.maximum(package["model"].predict(rows[names]), 0)
        new = np.maximum(package["model"].predict(changed[names]), 0)
        treated = rows.index.isin([w for w, n in crews.items() if n > 0])
        new = np.where(treated, np.minimum(new, base), base)
        frame = pd.DataFrame({
            "ward_id": rows.index,
            "city": rows["city"].values,
            "weeks_ahead": horizon,
            "crews": [crews.get(w, 0) for w in rows.index],
            "baseline_cases": base,
            "scenario_cases": new,
        })
        frame["cases_prevented"] = base - new
        for item in ("hospital_beds", "saline_bags"):
            frame[f"{item}_saved"] = frame["cases_prevented"] * FACTORS[item]
        results.append(frame)
    return pd.concat(results, ignore_index=True)


def rank_roi(rows, models, crews_per_ward=1, effect=CREW_EFFECT):
    """Rank wards by cases prevented (weeks 2-4 combined) per crew."""
    plan = {ward: crews_per_ward for ward in rows.index}
    result = simulate(rows, models, plan, effect)
    ranking = result.groupby(["ward_id", "city"], as_index=False)[
        ["baseline_cases", "scenario_cases", "cases_prevented",
         "hospital_beds_saved", "saline_bags_saved"]
    ].sum()
    ranking["roi_cases_per_crew"] = ranking["cases_prevented"] / crews_per_ward
    ranking = ranking.sort_values(
        ["roi_cases_per_crew", "ward_id"], ascending=[False, True]
    ).reset_index(drop=True)
    ranking.insert(0, "roi_rank", ranking.index + 1)
    return ranking.round(2)
