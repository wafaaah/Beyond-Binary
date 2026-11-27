"""Nearest same-city wards that still have estimated free beds (offline demo)."""
import math

import numpy as np
import pandas as pd

from ml.allocation import ROOT, add_demand
from ml.routing import estimate_capacity, route_overflow

# Optional file with real positions: ward_id,lat,lon
LOCATIONS_PATH = ROOT / "data" / "ward_locations.csv"
GRID_SPACING = 0.014  # same schematic grid as the 3D map (about 1.5 km)


def ward_positions(ward_ids):
    """
    Positions for the wards of ONE city, as (positions, are_real).

    The dataset has no coordinates. Without a complete locations file the
    wards are placed on a schematic grid, so distances are demonstrations.
    """
    ward_ids = sorted(ward_ids)
    if LOCATIONS_PATH.exists():
        table = pd.read_csv(LOCATIONS_PATH).set_index("ward_id")
        if table.reindex(ward_ids)[["lat", "lon"]].notnull().all().all():
            return {w: (table.at[w, "lat"], table.at[w, "lon"])
                    for w in ward_ids}, True
    side = math.ceil(math.sqrt(len(ward_ids)))
    positions = {}
    for i, ward in enumerate(ward_ids):
        row, col = divmod(i, side)
        # degrees around latitude 23; only relative distance matters
        positions[ward] = (23.0 + row * GRID_SPACING, 90.0 + col * GRID_SPACING)
    return positions, False


def distance_km(a, b):
    """Straight line distance between two (lat, lon) points."""
    lat1, lon1, lat2, lon2 = map(math.radians, (*a, *b))
    h = (math.sin((lat2 - lat1) / 2) ** 2
         + math.cos(lat1) * math.cos(lat2) * math.sin((lon2 - lon1) / 2) ** 2)
    return 2 * 6371 * math.asin(math.sqrt(h))


def bed_status(forecasts, data, origin_date, multiplier=1.0):
    """Estimated free beds per ward after the planned overflow transfers."""
    capacity = estimate_capacity(data, origin_date, multiplier)
    wards, _ = route_overflow(add_demand(forecasts), capacity)
    free = np.floor(wards["headroom_after"]).clip(lower=0).astype(int)
    return pd.DataFrame(
        {"ward_id": wards["ward_id"], "city": wards["city"], "free_beds": free}
    )


def place_patients(free_beds, positions, ward_id, patients):
    """
    Admit at the arrival ward first, then at the nearest wards with a free bed.

    free_beds: {ward_id: count} for ONE city. Returns (plan, unplaced) where
    plan is a list of (ward_id, patients, distance_km). Nothing is modified.
    """
    if patients < 0:
        raise ValueError("patients cannot be negative")
    order = sorted(
        free_beds,
        key=lambda w: (w != ward_id,
                       distance_km(positions[ward_id], positions[w]), w),
    )
    plan, remaining = [], int(patients)
    for ward in order:
        give = min(remaining, max(int(free_beds[ward]), 0))
        if give:
            distance = distance_km(positions[ward_id], positions[ward])
            plan.append((ward, give, round(distance, 1)))
            remaining -= give
    return plan, remaining
