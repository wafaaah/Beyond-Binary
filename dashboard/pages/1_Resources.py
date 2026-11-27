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
    allocate, city_summary,
)

st.set_page_config(page_title="Resource Allocation", layout="wide")
apply_style()
week, horizon, stock, crews = scenario_controls()
st.title("Constrained Resource Allocation")


result = allocate(cached_forecast(week, horizon), stock, crews)
st.caption(
    f"Historical replay. Target week: {result['target_date'].iloc[0]:%d %b %Y}. "
    f"Source: {result['forecast_source'].iloc[0]}."
)

cols = st.columns(4)
for col, (label, key) in zip(cols, [
    ("Saline bag deficit", "saline_bags_deficit"),
    ("Diagnostic kit deficit", "diagnostic_kits_deficit"),
    ("Bed deficit", "hospital_beds_deficit"),
    ("Crew deficit", "crews_deficit"),
]):
    col.metric(label, int(result[key].sum()))

short = int((result["deficit_alert"] != "").sum())
if short:
    st.error(f"Critical supply deficit: {short} wards cannot be fully served.")
else:
    st.success("All ward demand is fully met.")

city = st.selectbox("City", ["All cities"] + sorted(result["city"].unique()))
view = result if city == "All cities" else result[result["city"] == city]

st.subheader("Ward allocation (priority order)")
st.dataframe(view.drop(columns=["forecast_origin", "forecast_source"]),
             hide_index=True, use_container_width=True)
st.download_button("Download CSV", view.to_csv(index=False),
                   "allocation.csv", "text/csv")

st.subheader("City summary")
st.dataframe(city_summary(result), hide_index=True, use_container_width=True)

with st.expander("Rules and assumptions"):
    st.markdown(
        "- Demand = predicted cases x 2.385 (saline), 1.165 (kits), 0.298 (beds), "
        "derived from the onsite dataset.\n"
        "- Assumption: each city is a separate stock pool; stock = slider % of demand.\n"
        "- Assumption: crews needed are Low 0, Medium 1, High 2, Critical 3.\n"
        "- Priority: risk level, then population density, then predicted cases."
    )
