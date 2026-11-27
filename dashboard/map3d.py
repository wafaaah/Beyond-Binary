import math

import pandas as pd
import pydeck as pdk
import streamlit as st


# Approximate city centres (used only when the dataset has no coordinates)
CITY_CENTER = {
    "Chattogram": (22.3569, 91.7832),
    "Dhaka North": (23.8103, 90.4125),
    "Dhaka South": (23.7104, 90.4074),
}

RISK_RGB = {
    "Low": [53, 201, 138],
    "Medium": [231, 184, 75],
    "High": [240, 139, 67],
    "Critical": [239, 83, 97],
}

LAT_NAMES = ("latitude", "lat")
LON_NAMES = ("longitude", "lon", "lng", "long")


def _find_col(df, names):
    lower = {c.lower(): c for c in df.columns}
    for name in names:
        if name in lower:
            return lower[name]
    return None


def _grid_coords(ward_ids, city):
    """Schematic grid layout around the city centre (not real locations)."""
    lat0, lon0 = CITY_CENTER.get(city, (23.8103, 90.4125))
    ward_ids = sorted(ward_ids)
    side = math.ceil(math.sqrt(len(ward_ids)))
    spacing = 0.014

    coords = {}
    for i, ward in enumerate(ward_ids):
        row, col = divmod(i, side)
        coords[ward] = (
            lat0 + (row - side / 2) * spacing,
            lon0 + (col - side / 2) * spacing,
        )
    return coords


def render_ward_3d_map(backtest_df, ward_info_df, city, horizon=2):
    """3D ward risk map (Historical Replay)."""

    st.markdown("### 3D Ward Risk Map")

    if backtest_df is None or backtest_df.empty:
        st.info("Historical prediction data is unavailable for the map.")
        return

    data = backtest_df[
        (backtest_df["city"] == city)
        & (backtest_df["weeks_ahead"] == horizon)
    ].copy()

    if data.empty:
        st.info("No prediction data available for this city.")
        return

    # ---------- choose week (default = highest predicted week) ----------
    totals = data.groupby("target_date")["predicted_cases"].sum()
    dates = [d.date() for d in totals.index.sort_values()]
    peak_date = totals.idxmax().date()

    selected = st.select_slider(
        f"Target week ({horizon}-week-ahead predictions)",
        options=dates,
        value=peak_date,
        format_func=lambda d: d.strftime("%d %b %Y"),
    )

    week_df = data[data["target_date"].dt.date == selected].copy()
    week_df["predicted_cases"] = week_df["predicted_cases"].round(1)

    # ---------- coordinates ----------
    lat_col = _find_col(ward_info_df, LAT_NAMES)
    lon_col = _find_col(ward_info_df, LON_NAMES)
    schematic = True

    if lat_col and lon_col:
        ward_xy = (
            ward_info_df.groupby("ward_id")[[lat_col, lon_col]]
            .mean()
            .rename(columns={lat_col: "lat", lon_col: "lon"})
        )
        week_df = week_df.merge(
            ward_xy, left_on="ward_id", right_index=True, how="left"
        ).dropna(subset=["lat", "lon"])
        schematic = False

    if schematic or week_df.empty:
        coords = _grid_coords(data["ward_id"].unique(), city)
        week_df = data[data["target_date"].dt.date == selected].copy()
        week_df["predicted_cases"] = week_df["predicted_cases"].round(1)
        week_df["lat"] = week_df["ward_id"].map(lambda w: coords[w][0])
        week_df["lon"] = week_df["ward_id"].map(lambda w: coords[w][1])
        schematic = True

    week_df["color"] = week_df["risk_level"].map(
        lambda r: RISK_RGB.get(r, [150, 150, 150]) + [215]
    )

    # ---------- quick numbers ----------
    c1, c2, c3 = st.columns(3)
    c1.metric("Total predicted cases", f"{week_df['predicted_cases'].sum():.0f}")
    c2.metric(
        "High / Critical wards",
        int(week_df["risk_level"].isin(["High", "Critical"]).sum()),
    )
    c3.metric("Wards shown", len(week_df))

    # ---------- map ----------
    layer = pdk.Layer(
        "ColumnLayer",
        data=week_df,
        get_position=["lon", "lat"],
        get_elevation="predicted_cases",
        elevation_scale=250,
        radius=480,
        get_fill_color="color",
        pickable=True,
        extruded=True,
        auto_highlight=True,
    )

    view = pdk.ViewState(
        latitude=float(week_df["lat"].mean()),
        longitude=float(week_df["lon"].mean()),
        zoom=11,
        pitch=55,
        bearing=15,
    )

    st.pydeck_chart(
        pdk.Deck(
            layers=[layer],
            initial_view_state=view,
            map_style="dark",
            tooltip={
                "text": "{ward_id}\nPredicted cases: {predicted_cases}\nRisk: {risk_level}"
            },
        ),
        use_container_width=True,
    )

    caption = (
        "Column height = predicted cases, colour = risk level. "
        "This is a replay of a historical test week, not a live forecast."
    )
    if schematic:
        caption += (
            " Ward positions are a schematic layout around the city centre "
            "(the dataset has no ward coordinates), not real ward locations."
        )
    st.caption(caption)