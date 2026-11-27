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
    allocate,
)
from ml.dispatch import (  # noqa: E402
    assign_teams, html_brief, sms_notice, whatsapp_notice,
)

st.set_page_config(page_title="Dispatch", layout="wide")
apply_style()
week, horizon, stock, crews = scenario_controls()
st.title("Dispatch Notifications")


result = allocate(cached_forecast(week, horizon), stock, crews)
teams = assign_teams(result)

ward = st.selectbox("Ward (priority order)", result["ward_id"])
row = result[result["ward_id"] == ward].iloc[0]
sms = sms_notice(row, teams[ward])
chat = whatsapp_notice(row, teams[ward])

tab1, tab2, tab3 = st.tabs(["SMS", "WhatsApp", "Printable brief"])
with tab1:
    st.code(sms, language=None, wrap_lines=True)
    st.caption(f"{len(sms)} characters (more than one SMS segment if over 160).")
    st.download_button("Download SMS", sms, f"{ward}_sms.txt")
with tab2:
    st.code(chat, language=None, wrap_lines=True)
    st.download_button("Download WhatsApp text", chat, f"{ward}_whatsapp.txt")
with tab3:
    one = html_brief(result[result["ward_id"] == ward], f"Brief: {ward}")
    st.download_button("Download ward brief (HTML)", one,
                       f"{ward}_brief.html", "text/html")
    st.download_button("Download all wards brief (HTML)", html_brief(result),
                       "all_wards_brief.html", "text/html")
    st.caption("Open the file and use Print > Save as PDF.")
st.info("Messages are generated for copy or download. Nothing is sent automatically.")