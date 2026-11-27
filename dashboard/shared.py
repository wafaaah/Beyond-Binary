"""Scenario controls shared by all pages (values persist across pages)."""
import sys
from pathlib import Path

import pandas as pd
import streamlit as st

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from ml.allocation import forecast, load_data, peak_week  # noqa: E402
from ml.simulator import simulation_weeks  # noqa: E402
from theme import CSS  # noqa: E402

RISK_COLORS = {
    "Low": "#A9BC5F",
    "Medium": "#F5C84C",
    "High": "#F2762E",
    "Critical": "#E5484D",
}


@st.cache_data
def cached_data():
    return load_data()


@st.cache_data
def cached_forecast(week, horizon):
    return forecast(cached_data(), week, horizon)


def week_options():
    return [pd.Timestamp(w).date() for w in simulation_weeks(cached_data())]


def default_week():
    return pd.Timestamp(peak_week(cached_data())).date()


def _keep(name):
    st.session_state[name] = st.session_state[f"_{name}"]


def _restore(name, default):
    # Streamlit drops widget keys on page change, so keep a separate copy
    st.session_state.setdefault(name, default)
    st.session_state[f"_{name}"] = st.session_state[name]
    return {"key": f"_{name}", "on_change": _keep, "args": (name,)}


def scenario_controls():
    """Draw the sidebar controls and return the current scenario."""
    st.sidebar.header("Scenario (all pages)")
    week = st.sidebar.selectbox(
        "Forecast origin week", week_options(),
        **_restore("week", default_week()),
    )
    horizon = st.sidebar.radio(
        "Forecast horizon (weeks)", [2, 3, 4], horizontal=True,
        **_restore("horizon", 2),
    )
    stock = st.sidebar.slider(
        "Available Regional Stock (%)", 30, 100, step=5,
        **_restore("stock", 70),
    )
    crews = st.sidebar.slider(
        "Total Spraying Crews", 0, 150, **_restore("crews", 20),
    )
    return week, horizon, stock, crews


def apply_style():
    st.markdown(CSS, unsafe_allow_html=True)


def risk_style(value):
    color = RISK_COLORS.get(value)
    return f"background-color:{color}33;font-weight:600" if color else ""
