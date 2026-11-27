"""Bed capacity and intra-city overflow routing (offline, deterministic)."""
import numpy as np
import pandas as pd

CAPACITY_QUANTILE = 0.90  # assumption: dataset has no bed capacity


def estimate_capacity(data, origin_date, multiplier=1.0):
    """Beds per ward = 90th percentile of past weekly bed demand x multiplier."""
    history = data[data["date"] <= pd.Timestamp(origin_date)]
    capacity = history.groupby("ward_id")["hospital_beds_required"].quantile(
        CAPACITY_QUANTILE
    )
    return np.ceil(capacity * multiplier).astype(int).rename("bed_capacity")


def route_overflow(allocation, capacity):
    """
    Move overflow patients to the least-burdened ward in the same city.

    Takes the output of allocate() or add_demand(). Returns (wards, transfers).
    """
    wards = allocation[
        ["ward_id", "city", "risk_level", "population_density_sqkm",
         "hospital_beds_required"]
    ].copy()
    wards.columns = ["ward_id", "city", "risk_level", "density", "demand"]
    wards = wards.join(capacity, on="ward_id")
    if wards["bed_capacity"].isnull().any():
        raise ValueError("Missing bed capacity for some wards")

    wards["net_balance"] = wards["bed_capacity"] - wards["demand"]
    wards["overflow"] = (-wards["net_balance"]).clip(lower=0)
    wards["sent_out"] = 0
    wards["received"] = 0
    rank = {"Low": 0, "Medium": 1, "High": 2, "Critical": 3}
    wards["_rank"] = wards["risk_level"].map(rank)
    wards = wards.sort_values("ward_id").reset_index(drop=True)

    transfers = []
    for city, group in wards.groupby("city"):
        sources = group[group["overflow"] > 0].sort_values(
            ["_rank", "density", "overflow", "ward_id"],
            ascending=[False, False, False, True],
        )
        for source, row in sources.iterrows():
            remaining = int(row["overflow"])
            while remaining > 0:
                pool = wards[wards["city"] == city]
                used = pool["demand"] - pool["sent_out"] + pool["received"]
                pool = pool[(pool["overflow"] == 0)
                            & (used < pool["bed_capacity"])]
                if pool.empty:
                    break
                # lowest utilisation first, one bed at a time
                target = (used[pool.index] / pool["bed_capacity"]).idxmin()
                wards.at[target, "received"] += 1
                wards.at[source, "sent_out"] += 1
                transfers.append(
                    (city, row["ward_id"], wards.at[target, "ward_id"])
                )
                remaining -= 1

    wards["unplaced"] = wards["overflow"] - wards["sent_out"]
    occupied = wards["demand"] - wards["overflow"] + wards["received"]
    wards["headroom_after"] = wards["bed_capacity"] - occupied

    moves = pd.DataFrame(transfers, columns=["city", "from_ward", "to_ward"])
    moves = (
        moves.groupby(["city", "from_ward", "to_ward"])
        .size().reset_index(name="patients")
    )
    return wards.drop(columns="_rank"), moves


def city_bed_summary(wards):
    summary = wards.groupby("city")[
        ["demand", "bed_capacity", "overflow", "sent_out",
         "unplaced", "headroom_after"]
    ].sum().reset_index()
    summary["utilization_pct"] = (
        100 * summary["demand"] / summary["bed_capacity"].replace(0, np.nan)
    ).round(1)
    return summary
