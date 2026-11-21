
import streamlit as st


# --------------------------------
# RISK COLORS
# --------------------------------

def risk_color(risk_level):
    colors = {
        "Low": "#35C98A",
        "Medium": "#E7B84B",
        "High": "#F08B43",
        "Critical": "#EF5361"
    }

    return colors.get(risk_level, "#9FB0C8")


# --------------------------------
# DASHBOARD HEADER
# --------------------------------

def render_header():

    st.markdown(
        """
        <div style="padding:10px 0 5px 0;">
            <h1 style="margin-bottom:0;">
                🦟 DengueWatch
            </h1>
            <p style="color:#20A878; margin-top:5px;">
                Beyond-Binary | AI for Urban Dengue Outbreak
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )


# --------------------------------
# DATA NOTICE
# --------------------------------

def render_data_notice():

    st.info(
        "Historical dengue data is used for surveillance analysis. "
        "ML forecasts are experimental early-warning estimates and "
        "should not be treated as confirmed outbreak predictions."
    )


# --------------------------------
# SECTION TITLE
# --------------------------------

def render_section_title(title, description=None):

    st.markdown(f"### {title}")

    if description:
        st.caption(description)


# --------------------------------
# WARD PROFILE
# --------------------------------

def render_ward_profile(profile):

    if profile is None:
        st.info("No ward indicator data available.")
        return

    if hasattr(profile, "empty") and profile.empty:
        st.info("No ward indicator data available.")
        return

    if isinstance(profile, dict):

        items = profile.items()

    elif hasattr(profile, "to_dict"):

        items = profile.to_dict().items()

    else:
        st.write(profile)
        return

    for key, value in items:

        label = str(key).replace("_", " ").title()

        if isinstance(value, (int, float)):

            st.metric(
                label,
                f"{value:,.2f}"
            )

        else:

            st.markdown(
                f"**{label}:** {value}"
            )


# --------------------------------
# RISK CARD
# --------------------------------

def render_risk_card(risk_level, risk_score):

    color = risk_color(risk_level)

    st.markdown(
        f"""
        <div style="
            background:#141F33;
            border:1px solid {color};
            border-radius:14px;
            padding:20px;
        ">
            <p style="color:#9FB0C8;margin:0;">
                Risk Assessment
            </p>

            <h2 style="color:{color};margin:8px 0;">
                {risk_level}
            </h2>

            <p style="color:#E8EDF5;margin:0;">
                Risk Score: {risk_score}/100
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )


# --------------------------------
# RISK DRIVERS
# --------------------------------

def render_drivers(drivers):

    st.markdown("### Key Risk Drivers")

    if not drivers:
        st.info("No risk driver available.")
        return

    for driver in drivers:
        st.markdown(f"- 🌧️ {driver}")


# --------------------------------
# RECOMMENDATIONS
# --------------------------------

def render_recommendations(recommendations):

    st.markdown("### Recommended Actions")

    if not recommendations:
        st.info("No recommendations available.")
        return

    for i, recommendation in enumerate(
        recommendations,
        start=1
    ):

        st.markdown(
            f"**{i}.** {recommendation}"
        )


# --------------------------------
# DEMO NOTICE
# --------------------------------

def render_demo_notice():

    st.markdown(
        """
        <div style="
            background:#18263B;
            border:1px solid #E7B84B;
            border-radius:10px;
            padding:12px;
            color:#E8EDF5;
        ">
            ⚠️ DEMO MODE — Values shown may include mock data
            and are not confirmed dengue predictions.
        </div>
        """,
        unsafe_allow_html=True
    )


# --------------------------------
# FOOTER
# --------------------------------

def render_footer():

    st.markdown(
        """
        <hr>

        <div style="
            text-align:center;
            color:#9FB0C8;
            padding:10px;
        ">
            DengueWatch | Beyond-Binary | EDU AI Engineering Hackathon 2026
            <br>
            Experimental AI-based dengue early warning system
        </div>
        """,
        unsafe_allow_html=True
    )
