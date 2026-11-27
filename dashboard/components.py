
import streamlit as st


# --------------------------------
# RISK COLORS
# --------------------------------

def risk_color(risk_level):
    colors = {
        "Low": "#A9BC5F",
        "Medium": "#F5C84C",
        "High": "#F2762E",
        "Critical": "#E5484D"
    }

    return colors.get(risk_level, "#A687BC")


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
            <p style="color:#F4B647; margin-top:5px;">
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
            background:#2A1837;
            border:1px solid {color};
            border-radius:14px;
            padding:20px;
        ">
            <p style="color:#A687BC;margin:0;">
                Risk Assessment
            </p>

            <h2 style="color:{color};margin:8px 0;">
                {risk_level}
            </h2>

            <p style="color:#F6F0FA;margin:0;">
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
            background:#2A1837;
            border:1px solid #F5C84C;
            border-radius:10px;
            padding:12px;
            color:#F6F0FA;
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
            color:#A687BC;
            padding:10px;
        ">
            DengueWatch | Beyond-Binary | EDU AI Engineering Hackathon 2026
            <br>
            Experimental AI-based dengue early warning system
        </div>
        """,
        unsafe_allow_html=True
    )
