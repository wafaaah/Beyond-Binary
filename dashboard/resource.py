import sys
from pathlib import Path

import pandas as pd
import streamlit as st

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from ml.allocation import (  # noqa: E402
    allocate, available_weeks, city_summary, forecast, load_data, peak_week,
)

st.set_page_config(page_title="Resource Allocation", layout="wide")
st.title("Constrained Resource Allocation")


@st.cache_data
def cached_data():
    return load_data()


@st.cache_data
def cached_forecast(week, horizon):
    return forecast(cached_data(), week, horizon)


data = cached_data()

st.sidebar.header("Scenario")
horizon = st.sidebar.radio("Forecast horizon (weeks)", [2, 3, 4], horizontal=True)
weeks = [pd.Timestamp(w).date() for w in available_weeks(data, horizon)]
week = st.sidebar.selectbox(
    "Forecast origin week",
    weeks,
    index=weeks.index(pd.Timestamp(peak_week(data, horizon)).date()),
)
stock = st.sidebar.slider("Available Regional Stock (%)", 30, 100, 70, step=5)
crews = st.sidebar.slider("Total Spraying Crews", 0, 150, 20)

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
