import sys
from pathlib import Path

import pandas as pd
import streamlit as st

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from ml.allocation import load_data, peak_week  # noqa: E402
from ml.simulator import (  # noqa: E402
    prepare, rank_roi, simulate, simulation_weeks,
)

st.set_page_config(page_title="What-If Simulator", layout="wide")
st.title("What-If Vector Control Simulator")


@st.cache_data
def cached_data():
    return load_data()


@st.cache_resource
def cached_prepare(week):
    return prepare(cached_data(), week)


data = cached_data()
weeks = [pd.Timestamp(w).date() for w in simulation_weeks(data)]
default = pd.Timestamp(peak_week(data)).date()
week = st.sidebar.selectbox(
    "Forecast origin week", weeks,
    index=weeks.index(default) if default in weeks else len(weeks) - 1,
)
limit = st.sidebar.slider("Available crews", 1, 60, 20)
effect = st.sidebar.slider("Assumed effect per crew (%)", 5, 50, 25, 5) / 100

rows, models = cached_prepare(week)
ranking = rank_roi(rows, models, 1, effect)

st.subheader("Ward ROI ranking (1 crew each)")
st.dataframe(ranking, hide_index=True, use_container_width=True)

st.subheader("Deploy crews")
top = ranking.loc[ranking["cases_prevented"] > 0, "ward_id"].head(5).tolist()
selected = st.multiselect(
    "Selected wards", sorted(rows.index), default=top[:min(5, limit)]
)
crews = {
    ward: st.number_input(f"Crews for {ward}", 0, 5, 1, key=f"crew_{ward}")
    for ward in selected
}
used = sum(crews.values())

if used > limit:
    st.error(f"{used} crews selected but only {limit} available.")
elif used == 0:
    st.info("Select wards and assign at least one crew.")
else:
    result = simulate(rows, models, crews, effect)
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Crews used", f"{used} / {limit}")
    c2.metric("Cases prevented", f"{result['cases_prevented'].sum():.1f}")
    c3.metric("Bed load reduced", f"{result['hospital_beds_saved'].sum():.1f}")
    c4.metric("Saline bags saved", f"{result['saline_bags_saved'].sum():.1f}")

    weekly = result.groupby("weeks_ahead")[
        ["baseline_cases", "scenario_cases"]].sum()
    weekly.index = [f"Week +{i}" for i in weekly.index]
    st.subheader("All wards: projected cases, weeks 2 to 4")
    st.line_chart(weekly)
    detail = result[result["crews"] > 0].round(2)
    st.dataframe(detail, hide_index=True, use_container_width=True)
    st.download_button("Download scenario CSV", detail.to_csv(index=False),
                       "scenario.csv", "text/csv")

st.warning(
    "Assumption: each crew fixes a share of the remaining water logging and "
    "sanitation gap. The model is then re-run. This shows model sensitivity, "
    "not a proven real-world effect."
)