"""Demo sign-in for the three roles.

The accounts are fixed and shown on screen so that judges can enter easily.
This is a demonstration of role-based access, not production security.
"""
import streamlit as st

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


def check_login(username, password):
    """Return the role for a correct demo account, otherwise None."""
    for role, (name, secret, *_) in DEMO_USERS.items():
        if username.strip().lower() == name and password == secret:
            return role
    return None


def sign_out():
    st.session_state.pop("user_role", None)


def _enter(role):
    st.session_state["user_role"] = role
    st.switch_page(ROLE_PAGE)


def require_login():
    """Show the sign-in screen and stop the page until a role has signed in."""
    role = st.session_state.get("user_role")
    if role:
        st.sidebar.markdown(f"**Signed in:** {role}")
        st.sidebar.button("Log out", on_click=sign_out, use_container_width=True)
        return role

    # public entry comes first: no account needed
    text, action = st.columns([3, 1])
    text.markdown(
        "<div style='border:1px solid #6E8436;border-left:6px solid #A9BC5F;border-radius:14px;"
        "background:#222A1C;padding:14px 18px'>"
        "<div style='font-size:19px;font-weight:800;color:#F6F0FA'>&#128226; Are you a member "
        "of the public?</div>"
        "<div style='font-size:14px;color:#D2C3DD'>See the dengue risk of your ward and health "
        "advice. No login needed.</div></div>",
        unsafe_allow_html=True,
    )
    if action.button("Open Public Advisory", key="public_entry", type="primary",
                     use_container_width=True):
        st.switch_page(PUBLIC_PAGE)

    st.markdown(
        "<div style='text-align:center;padding:12px 0 20px'>"
        "<div style='font-size:42px;font-weight:800;color:#F6F0FA'>DengueWatch</div>"
        "<div style='color:#F4B647;font-size:16px'>Public Health Operations Dashboard</div>"
        "<div style='color:#D2C3DD;margin-top:12px'>Sign in with your role</div></div>",
        unsafe_allow_html=True,
    )
    for column, (name, user) in zip(st.columns(3), DEMO_USERS.items()):
        username, password, icon, color, duty = user
        column.markdown(
            f"<div style='border:1px solid #4B2A62;border-top:5px solid {color};"
            "border-radius:16px;background:#251530;padding:20px 16px;text-align:center;"
            "min-height:250px;margin-bottom:8px'>"
            f"<div style='font-size:42px'>{icon}</div>"
            f"<div style='font-size:19px;font-weight:800;color:#F6F0FA'>{name}</div>"
            f"<div style='font-size:14px;color:#D2C3DD;margin:8px 0 12px'>{duty}</div>"
            "<div style='font-size:13px;color:#BFA9CE'>Demo account</div>"
            f"<code>{username}</code> &nbsp; <code>{password}</code></div>",
            unsafe_allow_html=True,
        )
        if column.button("Demo login", key=f"demo_{username}", type="primary",
                         use_container_width=True):
            _enter(name)

    _, middle, _ = st.columns([1, 1.4, 1])
    with middle.form("login"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        submitted = st.form_submit_button("Sign in", use_container_width=True)
    if submitted:
        found = check_login(username, password)
        if found:
            _enter(found)
        middle.error("Wrong username or password.")
    st.caption("Demo sign-in with fixed accounts, not production security. "
               "The Public Advisory page is open to everyone.")
    st.stop()
