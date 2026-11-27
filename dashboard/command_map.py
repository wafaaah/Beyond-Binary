"""Command and control map: layer panel, schematic heat map and ward detail."""
from html import escape

import streamlit as st

from ops_map import operations_map
from shared import RISK_COLORS

# layer name: (column, unit, colour). None means colour by predicted risk.
HEAT_LAYERS = {
    "Predicted dengue risk": ("predicted_cases", "cases", None),
    "Rainfall": ("rainfall_mm", "mm", "#4DA6F0"),
    "Population density": ("population_density_sqkm", "per sq km", "#C77DF0"),
    "Water logging risk": ("water_logging_risk_index", "index", "#35C2B0"),
}


def _detail(row):
    color = RISK_COLORS[row["risk_level"]]
    lines = [
        ("Predicted cases", f"{row['predicted_cases']:.1f}"),
        ("Rainfall, origin week", f"{row['rainfall_mm']:.1f} mm"),
        ("Density / sq km", f"{row['population_density_sqkm']:,.0f}"),
        ("Water logging index", f"{row['water_logging_risk_index']:.2f}"),
        ("Sanitation score", f"{row['sanitation_score']:.2f}"),
        ("Saline (got / need)",
         f"{row['saline_bags_allocated']:.0f} / {row['saline_bags_needed']:.0f}"),
        ("Test kits (got / need)",
         f"{row['diagnostic_kits_allocated']:.0f} / {row['diagnostic_kits_needed']:.0f}"),
        ("Beds (got / need)",
         f"{row['hospital_beds_allocated']:.0f} / {row['hospital_beds_required']:.0f}"),
        ("Spray crews (got / need)",
         f"{row['crews_allocated']:.0f} / {row['crews_required']:.0f}"),
    ]
    body = "".join(
        f"<div style='display:flex;justify-content:space-between;gap:8px;padding:7px 0;"
        f"border-bottom:1px solid #39204B;font-size:13px'><span style='color:#BFA9CE'>{k}</span>"
        f"<b style='color:#F6F0FA'>{v}</b></div>" for k, v in lines
    )
    if row["deficit_alert"]:
        action = escape(str(row["deficit_alert"]))
    elif row["risk_level"] in ("High", "Critical"):
        action = "Resources assigned. Send the dispatch order and inspect breeding spots."
    else:
        action = "Continue routine surveillance."
    return (
        f"<div class='dw-panel' style='border-top:4px solid {color}'>"
        f"<div class='dw-panel-title'>{row['ward_id']}</div>"
        f"<div style='margin-bottom:6px'><span class='dw-pill' style='background:{color}'>"
        f"{row['risk_level']}</span> <small style='color:#BFA9CE'>{row['city']}</small></div>"
        f"{body}<div style='margin-top:10px;font-size:13px;color:#F6F0FA'><b style='color:#F5C84C'>Action: </b>"
        f"{action}</div></div>"
    )


def render_command_map(result, data, week, moves):
    """Draw the layer panel, the map and the selected ward detail."""
    env = data.loc[data["date"] == str(week),
                   ["ward_id", "rainfall_mm", "water_logging_risk_index", "sanitation_score"]]
    extra = [c for c in env.columns if c != "ward_id" and c in result.columns]
    table = result.drop(columns=extra).merge(env, on="ward_id", how="left")
    table = table.sort_values("priority_rank")

    panel, middle, side = st.columns([1, 2.9, 1.25], gap="small")
    with panel:
        st.markdown("**Command & Control**")
        layer = st.radio("Heat layer", list(HEAT_LAYERS), key="cc_layer")
        st.caption("Map overlays")
        chosen = set()
        for key, label, on in [("heat", "Heat zones", True), ("wards", "Ward markers", True),
                               ("labels", "City boundaries and names", True),
                               ("crews", "Spray crew pins", False),
                               ("route", "Patient overflow routes", False),
                               ("alerts", "Alert cards", True)]:
            if st.checkbox(label, value=on, key=f"cc_{key}"):
                chosen.add(key)
        selected = st.selectbox("Inspect ward", table["ward_id"].tolist(), key="cc_ward")

    column, unit, flat = HEAT_LAYERS[layer]
    values = table[column].fillna(0)
    low, high = values.min(), values.max()
    wards = [
        {"id": row["ward_id"], "city": row["city"],
         "color": flat or RISK_COLORS[row["risk_level"]],
         "heat": float((value - low) / (high - low)) if high > low else .5,
         "crews": int(row["crews_allocated"]) if "crews" in chosen else 0}
        for (_, row), value in zip(table.iterrows(), values)
    ]
    alerts = []
    if "alerts" in chosen:
        critical = int((table["risk_level"] == "Critical").sum())
        if critical:
            alerts.append(("CRITICAL RISK", f"{critical} wards predicted critical", "#E5484D"))
        if table["rainfall_mm"].notna().any():
            wet = table.loc[table["rainfall_mm"].idxmax()]
            alerts.append(("RAINFALL WATCH",
                           f"{wet['city']}: {wet['rainfall_mm']:.0f} mm in origin week", "#4DA6F0"))
    routes = [[m.from_ward, m.to_ward] for m in moves.itertuples()]

    with middle:
        st.markdown(operations_map(wards, chosen, alerts, routes, selected),
                    unsafe_allow_html=True)
        if flat:
            legend = f"Stronger glow = higher {layer.lower()} ({low:,.1f} to {high:,.1f} {unit})"
        else:
            legend = " &nbsp; ".join(
                f"<span style='color:{color}'>&#9679;</span> {name}"
                for name, color in RISK_COLORS.items())
        st.markdown(f"<div class='small-note'>{legend}</div>", unsafe_allow_html=True)
    with side:
        row = table[table["ward_id"] == selected]
        st.markdown(_detail((row if len(row) else table).iloc[0]), unsafe_allow_html=True)
