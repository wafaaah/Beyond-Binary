import sys
from pathlib import Path

import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

DASHBOARD = Path(__file__).resolve().parents[1]
if str(DASHBOARD) not in sys.path:
    sys.path.insert(0, str(DASHBOARD))

from shared import (  # noqa: E402
    RISK_COLORS, apply_style, cached_data, cached_forecast, risk_style,
    scenario_controls,
)
from theme import (  # noqa: E402
    AMBER, GOLD, OLIVE, ORANGE, RED, actions, bars, gauges, hero, style_figure,
    ward_board, flow,
)
from ml.allocation import allocate, city_summary  # noqa: E402
from ml.routing import estimate_capacity, route_overflow  # noqa: E402

st.set_page_config(page_title="Command Center", layout="wide")
apply_style()
week, horizon, stock, crews = scenario_controls()

data = cached_data()
result = allocate(cached_forecast(week, horizon), stock, crews)
wards, moves = route_overflow(result, estimate_capacity(data, week))
cities = city_summary(result)

st.markdown(hero(
    "DENGUE COMMAND CENTER",
    f"Ward level surveillance and response planning. Historical replay for the week of "
    f"{result['target_date'].iloc[0]:%d %b %Y}. Not a live warning.",
    [("Offline ready: no external API", True),
     (f"Source: {result['forecast_source'].iloc[0]}", False),
     (f"{horizon} week forecast", False)],
), unsafe_allow_html=True)

st.markdown(flow(1), unsafe_allow_html=True)

total = result["predicted_cases"].sum()
weekly_actual = data.groupby("date")["dengue_cases"].sum()
record = weekly_actual[weekly_actual.index <= str(week)].max()
current = weekly_actual.get(str(week), 0)
change = f"{(total / current - 1) * 100:+.0f}% vs origin week actual" if current else ""
urgent = int(result["risk_level"].isin(["High", "Critical"]).sum())
items = ["saline_bags", "diagnostic_kits", "hospital_beds"]
needed = sum(result[c].sum() for c in
             ["saline_bags_needed", "diagnostic_kits_needed", "hospital_beds_required"])
given = sum(result[f"{i}_allocated"].sum() for i in items)
fulfilment = given / needed if needed else 1
required = result["crews_required"].sum()
coverage = result["crews_allocated"].sum() / required if required else 1

st.markdown(gauges([
    (f"{total:.0f}", "Predicted cases", change, total / record if record else 0, AMBER),
    (f"{urgent}", "High / Critical wards", f"out of {len(result)} wards",
     urgent / len(result), RED),
    (f"{fulfilment:.0%}", "Supply fulfilment", "allocated / required units",
     fulfilment, GOLD),
    (f"{coverage:.0%}", "Crew coverage",
     f"{int(result['crews_allocated'].sum())} of {int(required)} crews needed",
     coverage, ORANGE),
]), unsafe_allow_html=True)

left, right = st.columns([1.7, 1], gap="medium")

with left:
    board = []
    order = result.groupby("city")["predicted_cases"].sum().sort_values(ascending=False)
    for city, city_total in order.items():
        group = result[result["city"] == city].sort_values("ward_id")
        tiles = [
            (f"W{row.ward_id.rsplit('_', 1)[-1]}", f"{row.predicted_cases:.1f}",
             f"{row.ward_id}: {row.risk_level}, {row.predicted_cases:.1f} predicted cases",
             RISK_COLORS[row.risk_level])
            for row in group.itertuples()
        ]
        urgent_city = int(group["risk_level"].isin(["High", "Critical"]).sum())
        board.append((city, f"{city_total:.0f} cases | {urgent_city} of {len(group)} high or critical",
                      tiles))
    st.markdown(ward_board("Ward Risk Board: predicted cases",
                           list(RISK_COLORS.items()), board), unsafe_allow_html=True)

with right:
    todo = []
    for _, row in result[result["deficit_alert"] != ""].nsmallest(3, "priority_rank").iterrows():
        todo.append((f"<b>{row['ward_id']}</b>: short of {row['deficit_alert'][9:]}", RED))
    for _, row in moves.nlargest(2, "patients").iterrows():
        todo.append((f"Route <b>{row['patients']}</b> patient(s) from "
                     f"<b>{row['from_ward']}</b> to <b>{row['to_ward']}</b>", ORANGE))
    unplaced = int(wards["unplaced"].sum())
    if unplaced:
        todo.append((f"<b>{unplaced}</b> patient(s) have no bed in their city: escalate", RED))
    if not todo:
        todo.append(("All demand is covered in this scenario.", OLIVE))
    st.markdown(actions("Recommended Actions", todo), unsafe_allow_html=True)

    by_city = result.groupby("city")["predicted_cases"].sum().sort_values(ascending=False)
    palette = [RED, ORANGE, AMBER, GOLD, OLIVE]
    st.markdown(bars("Predicted Cases by City", [
        (city, f"{value:.0f}", value / by_city.max() if by_city.max() else 0,
         palette[i % len(palette)])
        for i, (city, value) in enumerate(by_city.items())
    ]), unsafe_allow_html=True)

left, right = st.columns([1.7, 1], gap="medium")

with left:
    history = weekly_actual[weekly_actual.index <= str(week)].tail(26)
    future = [cached_forecast(week, h) for h in (2, 3, 4)]
    figure = go.Figure()
    figure.add_trace(go.Scatter(
        x=history.index, y=history.values, name="Actual cases", mode="lines",
        line={"color": AMBER, "width": 3}, fill="tozeroy",
        fillcolor="rgba(242,163,58,.14)",
    ))
    figure.add_trace(go.Scatter(
        x=[history.index[-1]] + [f["target_date"].iloc[0] for f in future],
        y=[history.values[-1]] + [f["predicted_cases"].sum() for f in future],
        name="Forecast (2 to 4 weeks)", mode="lines+markers",
        line={"color": GOLD, "width": 3, "dash": "dot"}, marker={"size": 9},
    ))
    style_figure(figure, 360)
    figure.update_layout(title="Disease Trend: all wards, weekly")
    st.plotly_chart(figure, use_container_width=True)

with right:
    st.markdown(bars("Supply Fulfilment", [
        (label, f"{share:.0%}", share, color)
        for label, key, need, color in [
            ("Saline bags", "saline_bags", "saline_bags_needed", AMBER),
            ("Test kits", "diagnostic_kits", "diagnostic_kits_needed", GOLD),
            ("Hospital beds", "hospital_beds", "hospital_beds_required", ORANGE),
        ]
        for share in [result[f"{key}_allocated"].sum() / result[need].sum()
                      if result[need].sum() else 1]
    ] + [("Spray crews", f"{coverage:.0%}", coverage, RED)]), unsafe_allow_html=True)

left, right = st.columns(2)
with left:
    chart = px.bar(
        cities, x="city", barmode="group",
        y=["saline_bags_needed", "saline_bags_allocated"],
        labels={"value": "Bags", "city": "", "variable": ""},
        color_discrete_sequence=["#6A5A3E", AMBER],
    )
    style_figure(chart)
    chart.update_layout(title="Saline: required vs allocated")
    st.plotly_chart(chart, use_container_width=True)
with right:
    counts = result.groupby(["city", "risk_level"]).size().reset_index(name="wards")
    chart = px.bar(
        counts, x="city", y="wards", color="risk_level",
        color_discrete_map=RISK_COLORS,
        category_orders={"risk_level": list(RISK_COLORS)},
        labels={"city": "", "risk_level": "Risk"},
    )
    style_figure(chart)
    chart.update_layout(title="Wards by risk")
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
