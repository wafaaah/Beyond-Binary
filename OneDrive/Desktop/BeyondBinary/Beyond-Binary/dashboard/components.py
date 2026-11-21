
import streamlit as st


# --------------------------------
# HEADER
# --------------------------------

def render_header():

    st.markdown(
        """
        <div class="dashboard-header">
            <h2 style="margin:0;">
                🦟 DengueWatch
            </h2>

           
        </div>
        """,
        unsafe_allow_html=True
    )


# --------------------------------
# INFORMATION NOTICE
# --------------------------------

def render_data_notice():

    st.markdown(
        """
        <div class="info-banner">
            ℹ️ HISTORICAL DATA MODE —
            The dashboard currently displays actual
            historical observations from the supplied
            dataset. ML forecasting is not yet connected.
        </div>
        """,
        unsafe_allow_html=True
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

    st.markdown("### Ward Vulnerability")

    if not profile:
        st.info("No ward information available.")
        return

    col1, col2 = st.columns(2)

    with col1:
        st.metric(
            "Population Density",
            f'{profile["population_density"]:,.2f}'
        )

        st.metric(
            "Waterlogging Index",
            f'{profile["waterlogging"]:.2f}'
        )

    with col2:
        st.metric(
            "Sanitation Score",
            f'{profile["sanitation"]:.2f}'
        )

        st.metric(
            "Historical Cases",
            f'{profile["historical_cases"]:,}'
        )


# --------------------------------
# FOOTER
# --------------------------------

def render_footer():

    st.divider()

    st.caption(
        "Beyond-Binary | Dengue Early Warning & "
        "Ward Risk Intelligence System"
    )

    st.caption(
        "Historical dataset analysis. "
        "Not a clinically validated forecasting system."
    )
