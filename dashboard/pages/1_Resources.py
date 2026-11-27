import sys
from pathlib import Path

import streamlit as st

DASHBOARD = Path(__file__).resolve().parents[1]
if str(DASHBOARD) not in sys.path:
    sys.path.insert(0, str(DASHBOARD))

from shared import (  # noqa: E402
    RISK_COLORS, apply_style, cached_forecast, scenario_controls,
)
from theme import (  # noqa: E402
    AMBER, GOLD, OLIVE, ORANGE, RED, alert, bars, flow, gauges, pill, table,
    title_bar,
)
from ml.allocation import (  # noqa: E402
    allocate, city_summary,
)

# label: (required column, allocated column, deficit column, colour)
SUPPLIES = {
    "Saline bags": ("saline_bags_needed", "saline_bags_allocated",
                    "saline_bags_deficit", AMBER),
    "Diagnostic kits": ("diagnostic_kits_needed", "diagnostic_kits_allocated",
                        "diagnostic_kits_deficit", GOLD),
    "Hospital beds": ("hospital_beds_required", "hospital_beds_allocated",
                      "hospital_beds_deficit", ORANGE),
    "Spraying crews": ("crews_required", "crews_allocated", "crews_deficit", RED),
}

st.set_page_config(page_title="Resource Allocation", layout="wide")
apply_style()
week, horizon, stock, crews = scenario_controls()
result = allocate(cached_forecast(week, horizon), stock, crews)

st.markdown(title_bar(
    "Resource Allocation",
    f"Week of {result['target_date'].iloc[0]:%d %b %Y} | regional stock {stock}% | "
    f"{crews} crews | {result['forecast_source'].iloc[0]}",
), unsafe_allow_html=True)
st.markdown(flow(2), unsafe_allow_html=True)

rings = []
for label, (need, given, short, color) in SUPPLIES.items():
    total, allocated = result[need].sum(), result[given].sum()
    share = allocated / total if total else 1
    rings.append((f"{share:.0%}", label,
                  f"{int(allocated)} of {int(total)} | deficit {int(result[short].sum())}",
                  share, color))
st.markdown(gauges(rings), unsafe_allow_html=True)

short_wards = int((result["deficit_alert"] != "").sum())
if short_wards:
    st.markdown(alert("CRITICAL SUPPLY DEFICIT",
                      f"{short_wards} wards cannot be fully served. Move the stock and crew "
                      "sliders to test other scenarios.", RED), unsafe_allow_html=True)
else:
    st.markdown(alert("FULLY COVERED", "All ward demand is met.", OLIVE),
                unsafe_allow_html=True)

a, b, c, d = st.columns(4)
supply = a.selectbox("Supply", list(SUPPLIES))
city = b.selectbox("City", ["All cities"] + sorted(result["city"].unique()))
levels = c.selectbox("Risk", ["All levels"] + list(RISK_COLORS)[::-1])
only_short = d.checkbox("Only wards with deficit")
need, given, short, color = SUPPLIES[supply]

view = result if city == "All cities" else result[result["city"] == city]
if levels != "All levels":
    view = view[view["risk_level"] == levels]
if only_short:
    view = view[view[short] > 0]
view = view.sort_values("priority_rank")

left, right = st.columns([1.8, 1], gap="medium")
with left:
    lines = []
    for _, row in view.head(15).iterrows():
        share = row[given] / row[need] if row[need] else 1
        meter = (f"<div class='dw-track' style='width:110px;display:inline-block'>"
                 f"<div class='dw-fill' style='width:{share:.0%};background:{color}'></div></div> "
                 f"{share:.0%}")
        gap = (pill(f"-{int(row[short])} short", RED) if row[short]
               else pill("covered", OLIVE))
        lines.append([
            int(row["priority_rank"]), f"<b>{row['ward_id']}</b>",
            pill(row["risk_level"], RISK_COLORS[row["risk_level"]]),
            int(row[need]), int(row[given]), meter, gap,
        ])
    if lines:
        st.markdown(table(f"Priority Allocation: {supply}",
                          ["#", "WARD", "RISK", "REQUIRED", "ALLOCATED", "FULFILMENT",
                           "STATUS"], lines), unsafe_allow_html=True)
        st.caption(f"Showing {len(lines)} of {len(view)} wards in priority order.")
    else:
        st.info("No wards match these filters.")

with right:
    cities = city_summary(result)
    gaps = result.groupby("city")[short].sum().sort_values(ascending=False)
    st.markdown(bars(f"Deficit by City: {supply}", [
        (name, f"{int(value)}", value / gaps.max() if gaps.max() else 0, color)
        for name, value in gaps.items()
    ]), unsafe_allow_html=True)
    st.download_button("Download filtered CSV", view.to_csv(index=False),
                       "allocation.csv", "text/csv", use_container_width=True)

with st.expander("All columns and city summary"):
    st.dataframe(view.drop(columns=["forecast_origin", "forecast_source"]),
                 hide_index=True, use_container_width=True)
    st.dataframe(cities, hide_index=True, use_container_width=True)
with st.expander("Rules and assumptions"):
    st.markdown(
        "- Demand = predicted cases x 2.385 (saline), 1.165 (kits), 0.298 (beds), "
        "derived from the onsite dataset.\n"
        "- Assumption: each city is a separate stock pool; stock = slider % of demand.\n"
        "- Assumption: crews needed are Low 0, Medium 1, High 2, Critical 3.\n"
        "- Priority: risk level, then population density, then predicted cases."
    )
