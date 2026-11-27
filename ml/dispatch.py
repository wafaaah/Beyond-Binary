import sys
from pathlib import Path

import pandas as pd
import streamlit as st

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from ml.allocation import (  # noqa: E402
    allocate, available_weeks, forecast, load_data, peak_week,
)
from ml.dispatch import (  # noqa: E402
    assign_teams, html_brief, sms_notice, whatsapp_notice,
)

st.set_page_config(page_title="Dispatch", layout="wide")
st.title("Dispatch Notifications")


@st.cache_data
def cached_data():
    return load_data()


@st.cache_data
def cached_forecast(week, horizon):
    return forecast(cached_data(), week, horizon)


data = cached_data()
horizon = st.sidebar.radio("Forecast horizon (weeks)", [2, 3, 4], horizontal=True)
weeks = [pd.Timestamp(w).date() for w in available_weeks(data, horizon)]
week = st.sidebar.selectbox(
    "Forecast origin week", weeks,
    index=weeks.index(pd.Timestamp(peak_week(data, horizon)).date()),
)
stock = st.sidebar.slider("Available Regional Stock (%)", 30, 100, 70, step=5)
total = st.sidebar.slider("Total Spraying Crews", 0, 150, 20)

result = allocate(cached_forecast(week, horizon), stock, total)
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
