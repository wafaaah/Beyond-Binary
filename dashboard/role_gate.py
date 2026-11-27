"""Entry screen: choose a role first, then open that role's page."""
import streamlit as st

CARDS = [
    ("Ward Health Officer", "&#128737;", "#F4B647",
     "Watch your ward, act on urgent risk, ask for spray teams and supplies."),
    ("Hospital Manager", "&#127973;", "#F2762E",
     "Watch bed shortage and patient pressure, move patients to another ward."),
    ("City Health Authority", "&#127963;", "#B565E8",
     "Compare all wards and share limited stock and spraying teams."),
]


def show_role_gate():
    """Stop the front page until a role or the full dashboard is chosen."""
    if st.session_state.get("entered"):
        if st.sidebar.button("Change role", use_container_width=True):
            st.session_state["entered"] = False
            st.rerun()
        return

    st.markdown(
        "<div style='text-align:center;padding:18px 0 22px'>"
        "<div style='font-size:42px;font-weight:800;color:#F6F0FA'>DengueWatch</div>"
        "<div style='color:#F4B647;font-size:16px'>Public Health Operations Dashboard</div>"
        "<div style='color:#D2C3DD;margin-top:14px'>Choose your role to continue</div></div>",
        unsafe_allow_html=True,
    )
    for column, (role, icon, color, text) in zip(st.columns(3), CARDS):
        column.markdown(
            f"<div style='border:1px solid #4B2A62;border-top:5px solid {color};"
            "border-radius:16px;background:#251530;padding:22px 18px;text-align:center;"
            "min-height:210px;margin-bottom:8px'>"
            f"<div style='font-size:44px'>{icon}</div>"
            f"<div style='font-size:19px;font-weight:800;color:#F6F0FA'>{role}</div>"
            f"<div style='font-size:14px;color:#D2C3DD;margin-top:8px'>{text}</div></div>",
            unsafe_allow_html=True,
        )
        if column.button("Continue", key=f"gate_{role}", type="primary",
                         use_container_width=True):
            st.session_state["entered"] = True
            st.session_state["my_role"] = role
            st.switch_page("pages/6_My_Role.py")

    _, middle, _ = st.columns([1, 1, 1])
    if middle.button("Open full dashboard", use_container_width=True):
        st.session_state["entered"] = True
        st.rerun()
    st.caption("Role view for the demo, not a secure login.")
    st.stop()
