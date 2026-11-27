import sys
from pathlib import Path

import streamlit as st

DASHBOARD = Path(__file__).resolve().parents[1]
if str(DASHBOARD) not in sys.path:
    sys.path.insert(0, str(DASHBOARD))

from shared import (  # noqa: E402
    RISK_COLORS, apply_style, cached_data, cached_forecast, scenario_controls,
)
from theme import (  # noqa: E402
    AMBER, GOLD, OLIVE, ORANGE, RED, compare, flow, table,
)
from ops_map import operations_map  # noqa: E402
from console import route_map, simulator_console, trend_chart  # noqa: E402
from ml.simulator import (  # noqa: E402
    prepare, rank_roi, simulate,
)

GREY = "#8458A4"

st.set_page_config(page_title="What-If Simulator", layout="wide")
apply_style()
week, horizon, stock, crews = scenario_controls()


@st.cache_resource
def cached_prepare(week):
    return prepare(cached_data(), week)


limit = crews
effect = st.sidebar.slider("Assumed effect per crew (%)", 5, 50, 25, 5) / 100
rows, models = cached_prepare(week)
ranking = rank_roi(rows, models, 1, effect)

st.markdown(flow(4), unsafe_allow_html=True)

top = ranking.loc[ranking["cases_prevented"] > 0, "ward_id"].head(5).tolist()
selected = st.multiselect(
    "Deploy crews to these wards", sorted(rows.index), default=top[:min(5, limit)]
)
plan = {}
columns = st.columns(5)
for i, ward in enumerate(selected):
    plan[ward] = columns[i % 5].number_input(
        f"Crews: {ward}", 0, 5, 1, key=f"crew_{ward}"
    )
used = sum(plan.values())
valid = 0 < used <= limit
result = simulate(rows, models, plan, effect) if valid else None
deployed = {w: n for w, n in plan.items() if n} if valid else {}

toggles = st.columns([1, 1, 1, 1, 1.6])
layers = {
    key for column, (key, label) in zip(toggles, [
        ("heat", "Heat zones"), ("wards", "Ward pins"),
        ("route", "Visit order line"), ("labels", "City names"),
    ]) if column.checkbox(label, value=True, key=f"layer_{key}")
}
mode = toggles[4].radio("Colour wards by", ["Crew impact", "Forecast risk"], horizontal=True)
if mode == "Crew impact":
    legend = [("Deployed", OLIVE), ("Top 20%", RED), ("Above average", AMBER), ("Low", GREY)]
else:
    legend = list(RISK_COLORS.items())

impact = ranking.set_index("ward_id")["roi_cases_per_crew"]
high, middle = impact.quantile(0.8), impact.quantile(0.5)
forecasts = cached_forecast(week, horizon).set_index("ward_id")
map_wards = []
for ward, row in ranking.set_index("ward_id").iterrows():
    value = impact[ward]
    if mode == "Crew impact":
        color = (OLIVE if ward in deployed else RED if value >= high and value > 0
                 else AMBER if value >= middle and value > 0 else GREY)
        heat = value / impact.max() if impact.max() > 0 else 0
    else:
        color = RISK_COLORS[forecasts.at[ward, "risk_level"]]
        heat = forecasts.at[ward, "predicted_cases"] / forecasts["predicted_cases"].max()
    map_wards.append({
        "id": ward, "city": row["city"], "color": color,
        "heat": float(min(max(heat, 0), 1)), "crews": deployed.get(ward, 0),
    })

gain = result.groupby("ward_id")["cases_prevented"].sum() if result is not None else None
order = sorted(deployed, key=lambda w: -gain[w]) if deployed else []
routes = {}
for ward in order:
    routes.setdefault(rows.at[ward, "city"], []).append(ward)

if used > limit:
    notices = [("CREW LIMIT EXCEEDED", f"{used} selected, {limit} available", RED)]
elif not used:
    notices = [("NO DEPLOYMENT", "Select wards and assign crews", GOLD)]
else:
    notices = [("DEPLOYMENT READY", f"{used} crews in {len(deployed)} wards", OLIVE)]
waiting = ranking[~ranking["ward_id"].isin(deployed)]
if not waiting.empty:
    best = waiting.iloc[0]
    notices.append(("NEXT BEST TARGET",
                    f"{best['ward_id']}: {best['roi_cases_per_crew']:.1f} cases per crew", ORANGE))

prevented = result["cases_prevented"].sum() if result is not None else 0
beds = result["hospital_beds_saved"].sum() if result is not None else 0
saline = result["saline_bags_saved"].sum() if result is not None else 0
kpis = [
    ("Crews used", f"{used}/{limit}", "of available", RED if used > limit else AMBER),
    ("Cases prevented", f"{prevented:.1f}", "weeks 2 to 4", OLIVE),
    ("Beds freed", f"{beds:.1f}", "estimated", GOLD),
    ("Saline saved", f"{saline:.0f}", "bags, estimated", ORANGE),
]
peak = impact.max() if impact.max() > 0 else 1
impact_rows = [
    (row.ward_id, f"{row.roi_cases_per_crew:.1f}", row.roi_cases_per_crew / peak,
     OLIVE if row.ward_id in deployed else AMBER)
    for row in ranking.head(8).itertuples()
]
focus = (max(routes, key=lambda c: len(routes[c])) if routes else ranking["city"].iloc[0])
city_ids = list(rows.index[rows["city"] == focus])
if result is not None:
    selected_rows = result[result["crews"] > 0]
    weekly_sel = selected_rows.groupby("weeks_ahead")[
        ["baseline_cases", "scenario_cases"]].sum()
    chart_title = "Forecast: selected wards"
    series = [("Without crews", list(weekly_sel["baseline_cases"]), ORANGE),
              ("With crews", list(weekly_sel["scenario_cases"]), OLIVE)]
else:
    base = simulate(rows, models, {}, effect).groupby("weeks_ahead")["baseline_cases"].sum()
    chart_title = "Forecast: all wards"
    series = [("Without crews", list(base), ORANGE)]

st.markdown(simulator_console(
    f"{crews} crews available | local models, offline | {notices[0][0].lower()}",
    operations_map(map_wards, layers, notices, routes.values()),
    kpis, impact_rows, f"Visit priority: {focus}",
    route_map(city_ids, focus, routes.get(focus, [])),
    chart_title, trend_chart(["Week +2", "Week +3", "Week +4"], series),
), unsafe_allow_html=True)
st.markdown("".join(
    f"<span style='font-size:12px;margin-right:16px'><span style='display:inline-block;width:11px;"
    f"height:11px;border-radius:3px;background:{color};margin-right:6px'></span>{name}</span>"
    for name, color in legend), unsafe_allow_html=True)

if result is not None:
    treated = result[result["crews"] > 0]
    weekly = treated.groupby("weeks_ahead")[["baseline_cases", "scenario_cases"]].sum()
    st.markdown(compare([
        (f"SELECTED WARDS, WEEK +{ahead}", row["baseline_cases"], row["scenario_cases"])
        for ahead, row in weekly.iterrows()
    ]), unsafe_allow_html=True)

    team, steps = 1, []
    for position, ward in enumerate(order, start=1):
        names = ", ".join(f"TEAM-{team + i:02d}" for i in range(deployed[ward]))
        team += deployed[ward]
        steps.append([position, f"<b>{ward}</b>", rows.at[ward, "city"], names,
                      f"{gain[ward]:.1f}"])
    st.markdown(table("Deployment Order", ["STOP", "WARD", "CITY", "TEAMS", "PREVENTED"], steps),
                unsafe_allow_html=True)
    st.download_button("Download scenario CSV", treated.round(2).to_csv(index=False),
                       "scenario.csv", "text/csv")

with st.expander("Full ward ROI ranking"):
    st.dataframe(ranking, hide_index=True, use_container_width=True)

st.warning(
    "Assumption: each crew fixes a share of the remaining water logging and "
    "sanitation gap. The model is then re-run. This shows model sensitivity, "
    "not a proven real-world effect. The map is a schematic."
)
