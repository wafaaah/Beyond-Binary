"""Opening animation and sidebar menu.

Streamlit's built-in menu appears before any page code runs, so it is switched
off in config.toml and drawn here, after the intro has started.
"""
import sys
from pathlib import Path

import streamlit as st

from splash import show_intro

PAGES = [
    ("Dashboard.py", "Dashboard"),
    ("pages/0_Command_Center.py", "Command Center"),
    ("pages/1_Resources.py", "Resources"),
    ("pages/2_Overflow.py", "Overflow"),
    ("pages/3_Simulator.py", "Simulator"),
    ("pages/4_Dispatch.py", "Dispatch"),
    ("pages/5_Public_Advisory.py", "Public Advisory"),
    ("pages/6_My_Role.py", "My Role"),
]

CSS = """<style>
.st-key-nav_menu{gap:.15rem}
.st-key-nav_menu a{border-radius:10px;padding:.35rem .6rem}
.st-key-nav_active a{background:linear-gradient(135deg,#F8CB6B,#E89A34);
box-shadow:0 6px 18px rgba(244,182,71,.35)}
.st-key-nav_active a p,.st-key-nav_active a span{color:#1F1027;font-weight:700}
</style>"""


def open_app():
    """Start the intro (first visit only), then draw the menu."""
    show_intro()
    current = Path(getattr(sys.modules.get("__main__"), "__file__", "") or "").name
    menu = st.sidebar.container(key="nav_menu")
    menu.markdown(CSS, unsafe_allow_html=True)
    for path, label in PAGES:
        if Path(path).name == current:
            with menu.container(key="nav_active"):
                st.page_link(path, label=label)
        else:
            menu.page_link(path, label=label)
    st.sidebar.divider()
