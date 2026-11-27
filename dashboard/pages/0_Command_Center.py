import sys
from pathlib import Path

import plotly.express as px
import streamlit as st

DASHBOARD = Path(__file__).resolve().parents[1]
if str(DASHBOARD) not in sys.path:
    sys.path.insert(0, str(DASHBOARD))

from shared import (  # noqa: E402
    RISK_COLORS, apply_style, cached_data, cached_forecast, risk_style,
    scenario_controls,
)
from ml.allocation import allocate, city_summary  # noqa: E402
from ml.routing import estimate_capacity, route_overflow  # noqa: E402

st.set_page_config(page_title="Command Center", layout="wide")
apply_style()
week, horizon, stock, crews = scenario_controls()

result = allocate(cached_forecast(week, horizon), stock, crews)
wards, moves = route_overflow(result, estimate_capacity(cached_data(), week))

st.title("Dengue Command Center")
st.caption(
    f"Historical replay. Target week: {result['target_date'].iloc[0]:%d %b %Y}. "
    f"Source: {result['forecast_source'].iloc[0]}. Not a live warning."
)

urgent = int(result["risk_level"].isin(["High", "Critical"]).sum())
c1, c2, c3, c4 = st.columns(4)
c1.metric("Predicted cases", f"{result['predicted_cases'].sum():.0f}")
c2.metric("High / Critical wards", f"{urgent} / {len(result)}")
c3.metric("Beds required", int(result["hospital_beds_required"].sum()))
c4.metric("Unplaced patients", int(wards["unplaced"].sum()))

c1, c2, c3, c4 = st.columns(4)
c1.metric("Saline bag deficit", int(result["saline_bags_deficit"].sum()))
c2.metric("Test kit deficit", int(result["diagnostic_kits_deficit"].sum()))
c3.metric("Bed stock deficit", int(result["hospital_beds_deficit"].sum()))
c4.metric("Crew deficit", int(result["crews_deficit"].sum()))

short = int((result["deficit_alert"] != "").sum())
if short:
    st.error(f"Action needed: {short} wards have a supply or crew deficit.")
else:
    st.success("All ward demand is covered in this scenario.")

st.subheader("City overview")
cities = city_summary(result)
columns = st.columns(len(cities))
for column, (_, row) in zip(columns, cities.iterrows()):
    group = result[result["city"] == row["city"]]
    with column.container(border=True):
        st.markdown(f"**{row['city']}**")
        st.metric("Cases", f"{group['predicted_cases'].sum():.0f}")
        st.caption(
            f"{int(group['risk_level'].eq('Critical').sum())} critical wards | "
            f"{int(row['crews_allocated'])}/{int(row['crews_required'])} crews"
        )

left, right = st.columns(2)
with left:
    st.subheader("Saline: required vs allocated")
    chart = px.bar(
        cities, x="city", barmode="group",
        y=["saline_bags_needed", "saline_bags_allocated"],
        labels={"value": "Bags", "city": "", "variable": ""},
    )
    st.plotly_chart(chart, use_container_width=True)
with right:
    st.subheader("Wards by risk")
    counts = result.groupby(["city", "risk_level"]).size().reset_index(name="wards")
    chart = px.bar(
        counts, x="city", y="wards", color="risk_level",
        color_discrete_map=RISK_COLORS,
        category_orders={"risk_level": list(RISK_COLORS)},
        labels={"city": "", "risk_level": "Risk"},
    )
    st.plotly_chart(chart, use_container_width=True)

st.subheader("Top 10 priority wards")
top = result.sort_values("priority_rank").head(10)[
    ["priority_rank", "ward_id", "city", "risk_level", "predicted_cases",
     "population_density_sqkm", "crews_allocated", "deficit_alert"]
]
top.columns = ["Rank", "Ward", "City", "Risk", "Predicted cases",
               "Density / sq km", "Crews", "Alert"]
st.dataframe(
    top.style.map(risk_style, subset=["Risk"]).format({"Predicted cases": "{:.1f}"}),
    hide_index=True, use_container_width=True,
)
