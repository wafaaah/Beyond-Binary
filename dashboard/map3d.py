import math

import pydeck as pdk
import streamlit as st


# Approximate city centres. The dataset has no ward coordinates.
CITY_CENTER = {
    "Chattogram": (22.3569, 91.7832),
    "Dhaka North": (23.8103, 90.4125),
    "Dhaka South": (23.7104, 90.4074),
    "Gazipur": (24.0023, 90.4264),
    "Narayanganj": (23.6238, 90.4990),
}

RISK_RGB = {
    "Low": [53, 201, 138],
    "Medium": [231, 184, 75],
    "High": [240, 139, 67],
    "Critical": [239, 83, 97],
}


def _grid_coords(ward_ids, city):
    """Schematic grid layout around the city centre (not real locations)."""
    lat0, lon0 = CITY_CENTER.get(city, (23.8103, 90.4125))
    ward_ids = sorted(ward_ids)
    side = math.ceil(math.sqrt(len(ward_ids)))
    spacing = 0.014
    offset = (side - 1) / 2

    coords = {}
    for i, ward in enumerate(ward_ids):
        row, col = divmod(i, side)
        coords[ward] = (
            lat0 + (row - offset) * spacing,
            lon0 + (col - offset) * spacing,
        )
    return coords


def render_ward_3d_map(backtest_df, ward_info_df, city, horizon=None):
    """3D ward risk map (historical replay). Works without a base map."""

    st.markdown("### 3D Ward Risk Map")

    if backtest_df is None or backtest_df.empty:
        st.info("Historical prediction data is unavailable for the map.")
        return

    city_data = backtest_df[backtest_df["city"] == city]

    if city_data.empty:
        st.info("No prediction data available for this city.")
        return

    # ---------- horizon ----------
    if horizon is None:
        horizon = st.radio(
            "Forecast horizon",
            sorted(int(h) for h in city_data["weeks_ahead"].unique()),
            format_func=lambda h: f"{h} weeks",
            horizontal=True,
            key=f"map_horizon_{city}",
        )

    data = city_data[city_data["weeks_ahead"] == horizon].copy()

    if data.empty:
        st.info("No prediction data available for this horizon.")
        return

    # ---------- week (default = highest predicted week) ----------
    totals = data.groupby("target_date")["predicted_cases"].sum()
    dates = [d.date() for d in totals.index.sort_values()]
    peak_date = totals.idxmax().date()

    if len(dates) > 1:
        selected = st.select_slider(
            f"Target week ({horizon}-week-ahead predictions)",
            options=dates,
            value=peak_date,
            format_func=lambda d: d.strftime("%d %b %Y"),
            key=f"map_week_{city}_{horizon}",
        )
    else:
        selected = dates[0]

    week_df = data[data["target_date"].dt.date == selected].copy()

    # ---------- position and colour ----------
    coords = _grid_coords(data["ward_id"].unique(), city)
    week_df["lat"] = week_df["ward_id"].map(lambda w: coords[w][0])
    week_df["lon"] = week_df["ward_id"].map(lambda w: coords[w][1])
    week_df["color"] = week_df["risk_level"].map(
        lambda r: RISK_RGB.get(r, [150, 150, 150]) + [215]
    )
    week_df["predicted"] = week_df["predicted_cases"].round(1)
    week_df["actual"] = week_df["actual_cases"].round(0)

    # ---------- quick numbers ----------
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Predicted cases", f"{week_df['predicted_cases'].sum():.0f}")
    c2.metric("Actual cases", f"{week_df['actual_cases'].sum():.0f}")
    c3.metric(
        "High / Critical wards",
        int(week_df["risk_level"].isin(["High", "Critical"]).sum()),
    )
    c4.metric("Wards shown", len(week_df))

    # ---------- map ----------
    layer = pdk.Layer(
        "ColumnLayer",
        data=week_df[
            ["ward_id", "lat", "lon", "color",
             "predicted", "actual", "risk_level"]
        ],
        get_position=["lon", "lat"],
        get_elevation="predicted",
        elevation_scale=120,
        radius=480,
        get_fill_color="color",
        pickable=True,
        extruded=True,
        auto_highlight=True,
    )

    view = pdk.ViewState(
        latitude=float(week_df["lat"].mean()),
        longitude=float(week_df["lon"].mean()),
        zoom=11.5,
        pitch=55,
        bearing=15,
    )

    st.pydeck_chart(
        pdk.Deck(
            layers=[layer],
            initial_view_state=view,
            map_provider=None,
            map_style=None,
            tooltip={
                "text": "{ward_id}\nPredicted: {predicted}\n"
                        "Actual: {actual}\nRisk: {risk_level}"
            },
        ),
        use_container_width=True,
    )

    # ---------- table (also a fallback if the 3D view cannot render) ----------
    with st.expander("Ward values"):
        st.dataframe(
            week_df[["ward_id", "predicted", "actual", "risk_level"]]
            .sort_values("predicted", ascending=False),
            hide_index=True,
            use_container_width=True,
        )

    st.caption(
        "Column height = predicted cases, colour = risk level. "
        "Replay of a historical test week, not a live forecast. "
        "Ward positions are a schematic grid (the dataset has no ward "
        "coordinates), not real ward locations."
    )