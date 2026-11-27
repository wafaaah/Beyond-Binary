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
    AMBER, OLIVE, ORANGE, RED, flow, phone, pill, table,
)
from console import dispatch_console  # noqa: E402
from ml.allocation import (  # noqa: E402
    allocate,
)
from ml.dispatch import (  # noqa: E402
    assign_teams, html_brief, sms_notice, whatsapp_notice,
)

STATUS = {"Pending": AMBER, "Acknowledged": OLIVE, "Needs support": ORANGE}

st.set_page_config(page_title="Dispatch", layout="wide",
                   page_icon=str(DASHBOARD / "assets" / "logo.png"))
apply_style()
week, horizon, stock, crews = scenario_controls()

result = allocate(cached_forecast(week, horizon), stock, crews)
teams = assign_teams(result)
ordered = result.sort_values("priority_rank")
alerts = ordered[ordered["risk_level"].isin(["High", "Critical"])]
# replies are recorded by the operator and kept for this browser session
replies = st.session_state.setdefault(f"replies_{week}_{horizon}", {})


def mark(ward, status):
    replies[ward] = status


st.markdown(flow(5), unsafe_allow_html=True)

a, b, c, d = st.columns([1.5, 1, 1, 1])
ward = a.selectbox("Ward (priority order)", ordered["ward_id"])
channel = b.radio("Channel", ["SMS", "WhatsApp"], horizontal=True)
c.button("Mark acknowledged", on_click=mark, args=(ward, "Acknowledged"),
         type="primary", use_container_width=True)
d.button("Needs support", on_click=mark, args=(ward, "Needs support"),
         use_container_width=True)

row = result[result["ward_id"] == ward].iloc[0]
sms = sms_notice(row, teams[ward])
chat = whatsapp_notice(row, teams[ward])
message = sms if channel == "SMS" else chat
needs_action = bool(row["deficit_alert"])

status_of = {w: replies.get(w, "Pending") for w in alerts["ward_id"]}
counts = {name: list(status_of.values()).count(name) for name in STATUS}
total = len(alerts)
sms_all = [sms_notice(r, teams[r["ward_id"]]) for _, r in alerts.iterrows()]
city_rows = []
for city, group in alerts.groupby("city"):
    states = [status_of[w] for w in group["ward_id"]]
    city_rows.append([
        f"<b>{city}</b>", len(group), int(group["crews_allocated"].sum()),
        pill(str(states.count("Acknowledged")), OLIVE),
        pill(str(states.count("Needs support")), ORANGE),
        pill(str(states.count("Pending")), AMBER),
    ])

st.markdown(dispatch_console(
    f"Week of {result['target_date'].iloc[0]:%d %b %Y} | built offline | nothing is sent "
    "automatically",
    [("WARDS TO ALERT", total, "High or Critical risk", RED),
     ("ACKNOWLEDGED", counts["Acknowledged"], "marked by operator", OLIVE),
     ("NOT YET REPLIED", counts["Pending"], "follow up needed", AMBER)],
    [(name, counts[name], counts[name] / total if total else 0, color)
     for name, color in STATUS.items()],
    [("SMS", len(sms_all),
      f"ready | about {sum(-(-len(m) // 160) for m in sms_all)} segments", AMBER),
     ("WhatsApp", total, "ready to copy", OLIVE),
     ("Teams", int(result["crews_allocated"].sum()),
      f"of {int(result['crews_required'].sum())} needed", ORANGE)],
    table("Response by City",
          ["CITY", "ALERTS", "TEAMS", "ACK", "SUPPORT", "PENDING"], city_rows),
    phone(f"DengueWatch | {channel} preview",
          "ACTION REQUIRED" if needs_action else "FOR INFORMATION",
          "#B83A3F" if needs_action else "#6E8436", message),
), unsafe_allow_html=True)

a, b, c = st.columns(3)
a.download_button(f"Download {channel}", message,
                  f"{ward}_{channel.lower()}.txt", use_container_width=True)
b.download_button("Ward brief (HTML)",
                  html_brief(result[result["ward_id"] == ward], f"Brief: {ward}"),
                  f"{ward}_brief.html", "text/html", use_container_width=True)
if channel == "SMS":
    c.caption(f"{len(sms)} characters (more than one SMS segment if over 160).")
with st.expander("Copy message text"):
    st.code(message, language=None, wrap_lines=True)

shown = list(alerts["ward_id"].head(8))
shown += [w for w in replies if w not in shown]
lines = []
for item in ordered[ordered["ward_id"].isin(shown + [ward])].itertuples():
    status = replies.get(item.ward_id, "Pending")
    marker = " &#9664;" if item.ward_id == ward else ""
    lines.append([
        int(item.priority_rank), f"<b>{item.ward_id}</b>{marker}",
        pill(item.risk_level, RISK_COLORS[item.risk_level]),
        f"{item.predicted_cases:.1f}",
        ", ".join(teams[item.ward_id]) or "none",
        pill(status, STATUS[status]),
    ])
st.markdown(table("Response Board", ["#", "WARD", "RISK", "CASES", "TEAMS", "STATUS"], lines),
            unsafe_allow_html=True)

st.markdown("#### Bulk dispatch")
chosen = st.multiselect(
    "Wards to include", list(ordered["ward_id"]), default=list(ordered["ward_id"].head(5))
)
if chosen:
    group = ordered[ordered["ward_id"].isin(chosen)]
    build = sms_notice if channel == "SMS" else whatsapp_notice
    bundle = "\n\n---\n\n".join(
        build(r, teams[r["ward_id"]]) for _, r in group.iterrows()
    )
    a, b, c = st.columns(3)
    a.download_button(f"{channel} for {len(group)} wards", bundle,
                      f"bulk_{channel.lower()}.txt", use_container_width=True)
    b.download_button("Brief for selected (HTML)", html_brief(group),
                      "selected_wards_brief.html", "text/html", use_container_width=True)
    c.download_button("Brief for all wards (HTML)", html_brief(result),
                      "all_wards_brief.html", "text/html", use_container_width=True)
st.caption("Open an HTML brief and use Print > Save as PDF.")
