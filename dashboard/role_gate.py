"""Demo sign-in for the three roles.

The accounts are fixed and shown on screen so that judges can enter easily.
This is a demonstration of role-based access, not production security.
"""
import streamlit as st

from logo import logo_img
from splash import show_intro

# role: (username, password, icon, colour, duty)
DEMO_USERS = {
    "Ward Health Officer": (
        "officer", "officer123", "&#128737;", "#F4B647",
        "Watch your ward, act on urgent risk, ask for spray teams and supplies."),
    "Hospital Manager": (
        "hospital", "hospital123", "&#127973;", "#F2762E",
        "Watch bed shortage and patient pressure, move patients to another ward."),
    "City Health Authority": (
        "city", "city123", "&#127963;", "#B565E8",
        "Compare all wards and share limited stock and spraying teams."),
}
ROLE_PAGE = "pages/6_My_Role.py"
PUBLIC_PAGE = "pages/5_Public_Advisory.py"
PUBLIC_BUTTON_HEIGHT = 84  # pixels; change to resize the Public Advisory button
PUBLIC_BUTTON_FONT = 20  # largest text size in pixels


def check_login(username, password):
    """Return the role for a correct demo account, otherwise None."""
    for role, (name, secret, *_) in DEMO_USERS.items():
        if username.strip().lower() == name and password == secret:
            return role
    return None


def sign_out():
    st.session_state.pop("user_role", None)
    st.session_state.pop("login_role", None)


def _enter(role):
    st.session_state["user_role"] = role
    st.switch_page(ROLE_PAGE)


def choose(role):
    """Open the sign-in step for a role, or go back with None."""
    st.session_state["login_role"] = role


def _title(subtitle):
    st.markdown(
        "<div style='text-align:center;padding:12px 0 20px'>"
        "<div style='font-size:42px;font-weight:800;color:#F6F0FA'>"
        f"{logo_img()}DengueWatch</div>"
        "<div style='color:#F4B647;font-size:16px'>Public Health Operations Dashboard</div>"
        f"<div style='color:#D2C3DD;margin-top:12px'>{subtitle}</div></div>",
        unsafe_allow_html=True,
    )


def _card(name):
    _, _, icon, color, duty = DEMO_USERS[name]
    return (
        f"<div style='border:1px solid #4B2A62;border-top:5px solid {color};"
        "border-radius:16px;background:#251530;padding:20px 16px;text-align:center;"
        "min-height:200px;margin-bottom:8px'>"
        f"<div style='font-size:42px'>{icon}</div>"
        f"<div style='font-size:19px;font-weight:800;color:#F6F0FA'>{name}</div>"
        f"<div style='font-size:14px;color:#D2C3DD;margin-top:8px'>{duty}</div></div>"
    )


def _showcase():
    """Lower band of the first screen: work flow, coverage figures and city artwork."""
    from dashboard_ui import _skyline  # imported here to avoid a circular import

    steps = [("&#128200;", "Forecast", "Ward risk 2 to 4 weeks ahead"),
             ("&#128230;", "Allocate", "Share limited supplies and teams"),
             ("&#127973;", "Route", "Plan where extra patients can go"),
             ("&#128232;", "Dispatch", "Prepare orders for field teams")]
    flow = "".join(
        "<div style='flex:1;min-width:170px;border:1px solid #4B2A62;border-radius:14px;"
        "background:#251530;padding:12px 14px'>"
        f"<div style='font-size:22px'>{icon}</div>"
        f"<div style='font-weight:800;color:#F4B647'>{name}</div>"
        f"<div style='font-size:13px;color:#D2C3DD'>{note}</div></div>"
        for icon, name, note in steps)
    figures = "".join(
        "<div style='min-width:110px'>"
        f"<div style='font-size:34px;font-weight:800;color:#F4B647;line-height:1.1'>{value}</div>"
        f"<div style='font-size:13px;color:#D2C3DD'>{label}</div></div>"
        for value, label in [("60", "wards"), ("5", "city corporations"),
                             ("2&ndash;4", "weeks ahead"), ("2", "languages")])
    st.markdown(
        f"<div style='display:flex;flex-wrap:wrap;gap:12px;margin:18px 0 12px'>{flow}</div>"
        "<div style='display:flex;flex-wrap:wrap;align-items:center;gap:18px;overflow:hidden;"
        "border:1px solid #4B2A62;border-radius:18px;padding:12px 24px;"
        "background:linear-gradient(100deg,#2E1A3D,#3D2150)'>"
        f"<div style='flex:2;display:flex;flex-wrap:wrap;gap:22px'>{figures}</div>"
        f"<img src='{_skyline()}' alt='' style='flex:1;min-width:220px;max-width:380px'></div>",
        unsafe_allow_html=True,
    )


def _sign_in_step(role):
    """Second step: authentication for the chosen role only."""
    username, password = DEMO_USERS[role][:2]
    _title("Sign in to continue")
    _, middle, _ = st.columns([1, 1.4, 1])
    middle.markdown(_card(role), unsafe_allow_html=True)
    middle.markdown(
        "<div style='text-align:center;font-size:13px;color:#BFA9CE;margin-bottom:8px'>"
        f"Demo account<br><code>{username}</code> &nbsp; <code>{password}</code></div>",
        unsafe_allow_html=True,
    )
    if middle.button("Demo login", key=f"demo_{username}", type="primary",
                     use_container_width=True):
        _enter(role)
    with middle.form("login"):
        typed_name = st.text_input("Username")
        typed_password = st.text_input("Password", type="password")
        submitted = st.form_submit_button("Sign in", use_container_width=True)
    if submitted:
        if check_login(typed_name, typed_password) == role:
            _enter(role)
        middle.error("Wrong username or password.")
    middle.button("Back to roles", on_click=choose, args=(None,), use_container_width=True)


def require_login():
    """Show the sign-in screen and stop the page until a role has signed in."""
    role = st.session_state.get("user_role")
    if role:
        st.sidebar.markdown(f"**Signed in:** {role}")
        st.sidebar.button("Log out", on_click=sign_out, use_container_width=True)
        return role

    show_intro()
    selected = st.session_state.get("login_role")
    if selected in DEMO_USERS:
        _sign_in_step(selected)
    else:
        # public entry comes first: no account needed
        text, action = st.columns([2.4, 1])
        text.markdown(
            "<style>.st-key-public_entry button{"
            f"min-height:{PUBLIC_BUTTON_HEIGHT}px;border-radius:14px}}"
            ".st-key-public_entry button p{"
            f"font-size:clamp(15px,1.4vw,{PUBLIC_BUTTON_FONT}px);font-weight:800}}</style>"
            "<div style='border:1px solid #FFD98A;border-left:6px solid #C9861A;border-radius:14px;"
            "background:linear-gradient(100deg,#F8C95C,#EDA43A);padding:14px 18px'>"
            "<div style='font-size:19px;font-weight:800;color:#24102F'>&#128226; Are you a member "
            "of the public?</div>"
            "<div style='font-size:14px;font-weight:600;color:#3A1D45'>See the dengue risk of your ward and health "
            "advice. No login needed.</div></div>",
            unsafe_allow_html=True,
        )
        if action.button("Open Public Advisory", key="public_entry", type="primary",
                         use_container_width=True):
            st.switch_page(PUBLIC_PAGE)

        _title("Choose your role")
        for column, name in zip(st.columns(3), DEMO_USERS):
            column.markdown(_card(name), unsafe_allow_html=True)
            column.button("Continue", key=f"role_{DEMO_USERS[name][0]}", type="primary",
                          on_click=choose, args=(name,), use_container_width=True)
        _showcase()
    st.caption("Demo sign-in with fixed accounts, not production security. "
               "The Public Advisory page is open to everyone.")
    st.stop()
