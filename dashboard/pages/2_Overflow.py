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
from theme import (  # noqa: E402
    AMBER, OLIVE, ORANGE, RED, alert, bars, blocks, flow, routes, title_bar,
    ward_board,
)

GREY = "#8458A4"

st.set_page_config(page_title="Overflow Routing", layout="wide")
apply_style()
week, horizon, stock, crews = scenario_controls()


data = cached_data()
multiplier = st.sidebar.slider("Bed capacity scenario", 0.5, 2.0, 1.0, 0.1)

demand = add_demand(cached_forecast(week, horizon))
capacity = estimate_capacity(data, week, multiplier)
wards, moves = route_overflow(demand, capacity)
summary = city_bed_summary(wards)

st.markdown(title_bar(
    "Bed Management and Overflow Routing",
    f"Week of {demand['target_date'].iloc[0]:%d %b %Y} | capacity is an assumption: "
    "90th percentile of past weekly bed demand",
), unsafe_allow_html=True)
st.markdown(flow(3), unsafe_allow_html=True)
overview_tab, desk_tab = st.tabs(["Overflow Overview", "Patient Transfer"])

with overview_tab:
    st.markdown(blocks([
        ("Beds required", int(wards["demand"].sum()), "predicted demand", AMBER),
        ("Bed capacity", int(wards["bed_capacity"].sum()), "all wards", OLIVE),
        ("Routed within city", int(wards["sent_out"].sum()),
         f"of {int(wards['overflow'].sum())} overflow patients", ORANGE),
        ("Unplaced", int(wards["unplaced"].sum()), "no bed in their city", RED),
    ]), unsafe_allow_html=True)

    if wards["unplaced"].sum():
        st.markdown(alert("ESCALATE", "Some cities have no free bed left for all overflow "
                          "patients.", RED), unsafe_allow_html=True)

    lines = []
    for _, row in summary.sort_values("utilization_pct", ascending=False).iterrows():
        used = row["utilization_pct"]
        color = RED if used > 100 else ORANGE if used > 85 else OLIVE
        net = int(row["bed_capacity"] - row["demand"])
        text = f"+{net} free" if net >= 0 else f"{net} short"
        lines.append((f"{row['city']} ({text})", f"{used:.0f}%", used / 100, color))
    st.markdown(bars("City Bed Utilisation", lines), unsafe_allow_html=True)

    city = st.selectbox("City", sorted(wards["city"].unique()))
    st.subheader("Transfer routes")
    city_moves = moves[moves["city"] == city]
    if city_moves.empty:
        st.info("No transfers needed or no free bed available in this city.")
    else:
        st.markdown(routes([
            (row.from_ward, row.to_ward, row.patients) for row in city_moves.itertuples()
        ]), unsafe_allow_html=True)

    view = wards[wards["city"] == city].sort_values("ward_id")
    tiles = []
    for row in view.itertuples():
        net = int(row.net_balance)
        color = RED if net < 0 else OLIVE if net > 0 else GREY
        tiles.append((f"W{row.ward_id.rsplit('_', 1)[-1]}", f"{net:+d}",
                      f"{row.ward_id}: need {int(row.demand)}, capacity "
                      f"{int(row.bed_capacity)}", color))
    st.markdown(ward_board(
        "Ward Bed Balance (capacity minus demand)",
        [("Free beds", OLIVE), ("Exactly full", GREY), ("Deficit", RED)],
        [(city, f"{int((view['net_balance'] < 0).sum())} wards in deficit", tiles)],
    ), unsafe_allow_html=True)

    with st.expander("Detailed tables"):
        st.dataframe(summary, hide_index=True, use_container_width=True)
        st.dataframe(view, hide_index=True, use_container_width=True)
    st.download_button("Download transfers CSV", moves.to_csv(index=False),
                       "transfers.csv", "text/csv")

with desk_tab:
    render_transfer_desk(week, horizon, multiplier)
