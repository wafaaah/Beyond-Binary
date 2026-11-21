
import streamlit as st


def risk_color(risk_level):
    colors = {
        "Low": "#35C98A",
        "Medium": "#E7B84B",
        "High": "#F08B43",
        "Critical": "#EF5361"
    }

    return colors.get(risk_level, "#9FB0C8")


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
            <p style="color:#9FB0C8;margin:0;">Risk Assessment</p>
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


def render_drivers(drivers):
    st.markdown("### Key Risk Drivers")

    if not drivers:
        st.info("No risk driver available.")
        return

    for driver in drivers:
        st.markdown(f"- ⚠️ {driver}")


def render_recommendations(recommendations):
    st.markdown("### Recommended Actions")

    if not recommendations:
        st.info("No recommendations available.")
        return

    for i, recommendation in enumerate(recommendations, start=1):
        st.markdown(f"**{i}.** {recommendation}")


def render_demo_notice():
    st.markdown(
        """
        <div class="demo-banner">
            ⚠️ DEMO MODE — The values shown are mock data,
            not real dengue predictions.
        </div>
        """,
        unsafe_allow_html=True
    )
