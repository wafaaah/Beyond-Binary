import sys
from pathlib import Path

import pandas as pd
import streamlit as st

DASHBOARD = Path(__file__).resolve().parents[1]
if str(DASHBOARD) not in sys.path:
    sys.path.insert(0, str(DASHBOARD))

from shared import (  # noqa: E402
    apply_style, cached_data, cached_forecast, scenario_controls,
)
from ml.allocation import (  # noqa: E402
    add_demand,
)
from ml.routing import (  # noqa: E402
    city_bed_summary, estimate_capacity, route_overflow,
)
from transfer_ui import render_transfer_desk  # noqa: E402

st.set_page_config(page_title="Overflow Routing", layout="wide")
apply_style()
week, horizon, stock, crews = scenario_controls()
st.title("Hospital Surge and Overflow Routing")


data = cached_data()
multiplier = st.sidebar.slider("Bed capacity scenario", 0.5, 2.0, 1.0, 0.1)

demand = add_demand(cached_forecast(week, horizon))
capacity = estimate_capacity(data, week, multiplier)
wards, moves = route_overflow(demand, capacity)
summary = city_bed_summary(wards)

st.caption(
    f"Historical replay. Target week: {demand['target_date'].iloc[0]:%d %b %Y}. "
    "Capacity is an assumption: 90th percentile of past weekly bed demand."
)
overview_tab, desk_tab = st.tabs(["Overflow Overview", "Patient Transfer"])

with overview_tab:
    c1, c2, c3 = st.columns(3)
    c1.metric("Overflow patients", int(wards["overflow"].sum()))
    c2.metric("Routed within city", int(wards["sent_out"].sum()))
    c3.metric("Unplaced", int(wards["unplaced"].sum()))

    if wards["unplaced"].sum():
        st.error("Some cities have no headroom left for all overflow patients.")

    st.subheader("City bed utilization")
    st.dataframe(summary, hide_index=True, use_container_width=True)
    st.bar_chart(summary.set_index("city")["utilization_pct"])

    city = st.selectbox("City", sorted(wards["city"].unique()))
    st.subheader("Transfer routes")
    city_moves = moves[moves["city"] == city]
    if city_moves.empty:
        st.info("No transfers needed or no headroom available in this city.")
    else:
        st.dataframe(city_moves, hide_index=True, use_container_width=True)

    st.subheader("Ward deficit and headroom")
    view = wards[wards["city"] == city]
    st.dataframe(view, hide_index=True, use_container_width=True)
    st.download_button("Download transfers CSV", moves.to_csv(index=False),
                       "transfers.csv", "text/csv")

with desk_tab:
    render_transfer_desk(week, horizon, multiplier)
