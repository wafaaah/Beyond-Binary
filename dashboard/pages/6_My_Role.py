import sys
from pathlib import Path

import pandas as pd
import streamlit as st

DASHBOARD = Path(__file__).resolve().parents[1]
if str(DASHBOARD) not in sys.path:
    sys.path.insert(0, str(DASHBOARD))

from shared import (  # noqa: E402
    RISK_COLORS, apply_style, cached_data, cached_forecast, scenario_controls,
)
from theme import (  # noqa: E402
    AMBER, GOLD, OLIVE, ORANGE, RED, bars, blocks, hero, pill, table,
)
from transfer_ui import render_transfer_desk  # noqa: E402
from ml.allocation import allocate, city_summary  # noqa: E402
from ml.dispatch import assign_teams, sms_notice  # noqa: E402
from ml.routing import estimate_capacity, route_overflow  # noqa: E402

ROLES = {
    "Ward Health Officer": "Watch your ward, act on urgent risk, ask for spray teams and supplies.",
    "Hospital Manager": "Watch bed shortage and patient pressure, move patients to another ward.",
    "City Health Authority": "Compare all wards and share limited stock and spraying teams.",
}
ITEMS = [
    ("Saline bags", "saline_bags_needed", "saline_bags_allocated"),
    ("Diagnostic kits", "diagnostic_kits_needed", "diagnostic_kits_allocated"),
    ("Hospital beds", "hospital_beds_required", "hospital_beds_allocated"),
    ("Spraying crews", "crews_required", "crews_allocated"),
]

st.set_page_config(page_title="My Role", layout="wide")
apply_style()
week, horizon, stock, crews = scenario_controls()
result = allocate(cached_forecast(week, horizon), stock, crews)
wards, moves = route_overflow(result, estimate_capacity(cached_data(), week))
# requests are shared between the three views during this browser session
requests = st.session_state.setdefault("requests", [])


def send_request(ward, city, need, amount):
    requests.append({"ward": ward, "city": city, "need": need, "amount": int(amount),
                     "week": str(week), "status": "Waiting"})


def decide(index, status):
    requests[index]["status"] = status


def request_table(rows, title):
    colors = {"Waiting": AMBER, "Approved": OLIVE, "Declined": RED}
    st.markdown(table(title, ["WARD", "NEED", "AMOUNT", "WEEK", "STATUS"], [
        [f"<b>{r['ward']}</b>", r["need"], r["amount"], r["week"],
         pill(r["status"], colors[r["status"]])] for r in rows
    ]), unsafe_allow_html=True)


st.markdown(hero(
    "MY ROLE",
    f"One system for three public health users. Historical replay for the week of "
    f"{result['target_date'].iloc[0]:%d %b %Y}.",
    [("Demo sign-in, not production security", False)],
), unsafe_allow_html=True)
role = st.session_state["user_role"]
st.subheader(role)
st.caption(ROLES[role])

if role == "Ward Health Officer":
    ward = st.selectbox("My ward", sorted(result["ward_id"]), key="role_ward")
    row = result[result["ward_id"] == ward].iloc[0]
    st.markdown(blocks([
        ("Risk level", row["risk_level"], row["city"], RISK_COLORS[row["risk_level"]]),
        ("Predicted cases", f"{row['predicted_cases']:.1f}", f"{horizon} weeks ahead", AMBER),
        ("Priority rank", int(row["priority_rank"]), f"of {len(result)} wards", GOLD),
        ("Spray crews", f"{int(row['crews_allocated'])}/{int(row['crews_required'])}",
         "assigned / needed", ORANGE),
    ]), unsafe_allow_html=True)

    st.markdown(table("Supplies for my ward", ["ITEM", "NEEDED", "ALLOCATED", "SHORT"], [
        [label, int(row[need]), int(row[given]),
         pill(str(int(row[need] - row[given])), RED if row[need] > row[given] else OLIVE)]
        for label, need, given in ITEMS
    ]), unsafe_allow_html=True)

    st.subheader("Ask the city authority")
    short = [(label, row[need] - row[given]) for label, need, given in ITEMS
             if row[need] > row[given]]
    if short:
        columns = st.columns(len(short))
        for column, (label, amount) in zip(columns, short):
            sent = any(r["ward"] == ward and r["need"] == label and r["week"] == str(week)
                       for r in requests)
            column.button(f"Request {int(amount)} {label}", key=f"req_{ward}_{label}",
                          disabled=sent, on_click=send_request,
                          args=(ward, row["city"], label, amount), use_container_width=True)
    else:
        st.success("My ward is fully covered in this scenario.")
    mine = [r for r in requests if r["ward"] == ward]
    if mine:
        request_table(mine, "My requests")

    message = sms_notice(row, assign_teams(result)[ward])
    st.download_button("Download field team SMS", message, f"{ward}_sms.txt")
    st.code(message, language=None, wrap_lines=True)

elif role == "Hospital Manager":
    city = st.selectbox("City", sorted(wards["city"].unique()), key="role_city")
    local = wards[wards["city"] == city]
    st.markdown(blocks([
        ("Beds required", int(local["demand"].sum()), "predicted demand", AMBER),
        ("Bed capacity", int(local["bed_capacity"].sum()), "estimated", OLIVE),
        ("Overflow patients", int(local["overflow"].sum()), "above ward capacity", ORANGE),
        ("Unplaced", int(local["unplaced"].sum()), "no bed in this city", RED),
    ]), unsafe_allow_html=True)
    pressure = local[local["overflow"] > 0].sort_values("overflow", ascending=False).head(8)
    if len(pressure):
        top = pressure["overflow"].max()
        st.markdown(bars("Wards with bed shortage", [
            (r.ward_id, f"{int(r.overflow)}", r.overflow / top, RED)
            for r in pressure.itertuples()
        ]), unsafe_allow_html=True)
    else:
        st.success("No ward in this city is over capacity.")
    st.subheader("Move a patient")
    render_transfer_desk(week, horizon, 1.0)

else:
    st.markdown(blocks([
        ("Urgent wards", int(result["risk_level"].isin(["High", "Critical"]).sum()),
         f"of {len(result)} wards", RED),
        ("Regional stock", f"{stock}%", "sidebar scenario", AMBER),
        ("Crews allocated",
         f"{int(result['crews_allocated'].sum())}/{int(result['crews_required'].sum())}",
         "assigned / needed", ORANGE),
        ("Waiting requests", sum(r["status"] == "Waiting" for r in requests),
         "from ward officers", GOLD),
    ]), unsafe_allow_html=True)

    st.subheader("Requests from wards")
    if requests:
        request_table(requests, "Request inbox")
        for index, item in enumerate(requests):
            if item["status"] == "Waiting":
                name, yes, no = st.columns([3, 1, 1])
                name.markdown(f"**{item['ward']}**: {item['amount']} {item['need']}")
                yes.button("Approve", key=f"yes_{index}", on_click=decide,
                           args=(index, "Approved"), use_container_width=True)
                no.button("Decline", key=f"no_{index}", on_click=decide,
                          args=(index, "Declined"), use_container_width=True)
        st.caption("A decision records the answer. It does not change the automatic allocation.")
    else:
        st.info("No requests yet. Sign in as Ward Health Officer to send one.")

    st.subheader("Compare cities")
    st.dataframe(city_summary(result), hide_index=True, use_container_width=True)
    ranked = result.sort_values("priority_rank")[
        ["priority_rank", "ward_id", "city", "risk_level", "predicted_cases",
         "crews_allocated", "deficit_alert"]]
    st.subheader("All wards in priority order")
    st.dataframe(ranked, hide_index=True, use_container_width=True)
    st.download_button("Download allocation CSV", pd.DataFrame(ranked).to_csv(index=False),
                       "city_allocation.csv", "text/csv")

st.caption("Bed capacity is estimated. Requests stay in this browser session only and are "
           "not sent to anyone.")
