
from pathlib import Path

import pandas as pd
import streamlit as st
import plotly.express as px

from mock_data import (
    load_data,
    filter_data,
    get_summary,
    get_monthly_cases,
    get_weather_data,
    get_ward_ranking,
    get_ward_profile,
    load_forecasts,
    get_ward_forecasts
)

from style import load_css

from components import (
    render_header,
    render_data_notice,
    render_section_title,
    render_ward_profile,
    render_footer
)

from action_recommendations import get_action_recommendations


# ========================================
# PAGE CONFIGURATION
# ========================================

st.set_page_config(
    page_title="DengueWatch | Beyond-Binary",
    page_icon="🦟",
    layout="wide",
    initial_sidebar_state="expanded"
)


# ========================================
# LOAD CSS
# ========================================

st.markdown(
    load_css(),
    unsafe_allow_html=True
)


# ========================================
# LOAD MAIN DATA
# ========================================

try:
    df = load_data()
    forecast_df = load_forecasts()

except Exception as error:
    st.error(f"Data loading failed: {error}")
    st.info("Please check your data files and their locations.")
    st.stop()


# ========================================
# LOAD HISTORICAL BACKTESTING DATA
# ========================================

BACKTEST_PATH = (
    Path(__file__).resolve().parents[1]
    / "data"
    / "processed"
    / "weather_model_predictions.csv"
)

try:
    backtest_df = pd.read_csv(BACKTEST_PATH)

    backtest_df["forecast_origin"] = pd.to_datetime(
        backtest_df["forecast_origin"]
    )

    backtest_df["target_date"] = pd.to_datetime(
        backtest_df["target_date"]
    )

    def classify_risk(value):

        if value < 1:
            return "Low"

        elif value < 5:
            return "Medium"

        elif value < 10:
            return "High"

        else:
            return "Critical"

    backtest_df["risk_level"] = (
        backtest_df["predicted_cases"].apply(classify_risk)
    )

    ward_city = (
        df[["ward_id", "city"]]
        .drop_duplicates(subset=["ward_id"])
    )

    backtest_df = backtest_df.merge(
        ward_city,
        on="ward_id",
        how="left"
    )

except Exception as error:

    backtest_df = pd.DataFrame()

    st.warning(
        f"Historical backtesting data could not be loaded: {error}"
    )


# ========================================
# SIDEBAR
# ========================================

st.sidebar.title("Layers")

st.sidebar.caption(
    "DENGUE SURVEILLANCE CONTROLS"
)

st.sidebar.markdown("### Location")

cities = sorted(
    df["city"].dropna().unique().tolist()
)

if not cities:
    st.error("No city information found.")
    st.stop()

default_city = (
    cities.index("Chattogram")
    if "Chattogram" in cities
    else 0
)

city = st.sidebar.selectbox(
    "Select City",
    cities,
    index=default_city
)


# ========================================
# WARD SELECTION
# ========================================

city_data = df[df["city"] == city]

wards = sorted(
    city_data["ward_id"].dropna().unique().tolist()
)

selected_ward = st.sidebar.selectbox(
    "Administrative Level / Ward",
    ["All Wards"] + wards
)


# ========================================
# HISTORICAL DATE FILTER
# ========================================

st.sidebar.divider()

st.sidebar.markdown("### Historical Period")

min_date = df["date"].min().date()
max_date = df["date"].max().date()

date_options = [
    "All Available Data",
    "Last 12 Months",
    "Last 6 Months",
    "Last 3 Months",
    "Custom Range"
]

period = st.sidebar.selectbox(
    "Select Period",
    date_options
)

if period == "All Available Data":

    start_date = min_date
    end_date = max_date

elif period == "Last 12 Months":

    start_date = max(
        min_date,
        (df["date"].max() - pd.DateOffset(months=12)).date()
    )

    end_date = max_date

elif period == "Last 6 Months":

    start_date = max(
        min_date,
        (df["date"].max() - pd.DateOffset(months=6)).date()
    )

    end_date = max_date

elif period == "Last 3 Months":

    start_date = max(
        min_date,
        (df["date"].max() - pd.DateOffset(months=3)).date()
    )

    end_date = max_date

else:

    selected_dates = st.sidebar.date_input(
        "Choose date range",
        value=(min_date, max_date),
        min_value=min_date,
        max_value=max_date
    )

    if isinstance(selected_dates, (tuple, list)):

        if len(selected_dates) == 2:
            start_date, end_date = selected_dates

        elif len(selected_dates) == 1:
            start_date = selected_dates[0]
            end_date = selected_dates[0]

        else:
            start_date = min_date
            end_date = max_date

    else:

        start_date = selected_dates
        end_date = selected_dates


st.sidebar.divider()

st.sidebar.caption(
    "Source: Provided Bangladesh dengue dataset"
)

st.sidebar.caption(
    "Historical observations only."
)


# ========================================
# FILTER MAIN DATA
# ========================================

filtered_df = filter_data(
    df,
    city,
    selected_ward,
    start_date,
    end_date
)

if filtered_df.empty:

    st.warning(
        "No observations available for this selection."
    )

    st.stop()


city_period_df = filter_data(
    df,
    city,
    "All Wards",
    start_date,
    end_date
)


# ========================================
# DASHBOARD HEADER
# ========================================

render_header()

st.markdown(
    """
    <div class="dashboard-subtitle">
        WARD RISK INTELLIGENCE SYSTEM | BANGLADESH
    </div>
    """,
    unsafe_allow_html=True
)

render_data_notice()


# ========================================
# DASHBOARD TITLE
# ========================================

st.markdown(
    "## Surveillance Overview"
)

st.caption(
    f"Monitoring area: {city} | "
    f"Administrative level: {selected_ward}"
)

st.caption(
    f"Historical reporting period: "
    f"{start_date} to {end_date}"
)


# ========================================
# SUMMARY METRICS
# ========================================

summary = get_summary(filtered_df)

col1, col2, col3, col4 = st.columns(4)

with col1:

    st.metric(
        "Historical Dengue Cases",
        f'{summary["total_cases"]:,}'
    )

with col2:

    st.metric(
        "Wards Represented",
        summary["total_wards"]
    )

with col3:

    st.metric(
        "Average Rainfall",
        f'{summary["avg_rainfall"]:.1f} mm'
    )

with col4:

    st.metric(
        "Average Temperature",
        f'{summary["avg_temperature"]:.1f} °C'
    )

st.divider()


# ========================================
# MAIN ANALYTICS AREA
# ========================================

left_col, right_col = st.columns(
    [2.1, 1],
    gap="large"
)


# ========================================
# LEFT: ANALYTICS TABS
# ========================================

with left_col:

    cases_tab, weather_tab, indicators_tab = st.tabs(
        ["Cases", "Weather", "Ward Indicators"]
    )

    # ------------------------------------
    # HISTORICAL CASES
    # ------------------------------------

    with cases_tab:

        render_section_title(
            "Historical Dengue Cases",
            "Monthly aggregation of available weekly observations."
        )

        monthly_df = get_monthly_cases(filtered_df)

        if not monthly_df.empty:

            fig = px.area(
                monthly_df,
                x="month",
                y="dengue_cases",
                markers=True,
                labels={
                    "month": "Month",
                    "dengue_cases": "Reported Cases"
                },
                color_discrete_sequence=["#20A878"]
            )

            fig.update_layout(
                template=(
                    "plotly_dark"
                    if st.get_option("theme.base") == "dark"
                    else "plotly_white"
                ),
                height=360,
                margin=dict(
                    l=15,
                    r=15,
                    t=20,
                    b=15
                ),
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                showlegend=False
            )

            st.plotly_chart(
                fig,
                use_container_width=True
            )

        else:

            st.info(
                "No historical case data available."
            )

    # ------------------------------------
    # WEATHER ANALYSIS
    # ------------------------------------

    with weather_tab:

        render_section_title(
            "Weather Analysis",
            "Historical rainfall, temperature and humidity."
        )

        weather_df = get_weather_data(filtered_df)

        if not weather_df.empty:

            rainfall_fig = px.bar(
                weather_df,
                x="week",
                y="rainfall_mm",
                title="Weekly Rainfall",
                color_discrete_sequence=["#249DBB"],
                labels={
                    "week": "Date",
                    "rainfall_mm": "Rainfall (mm)"
                }
            )

            rainfall_fig.update_layout(
                template=(
                    "plotly_dark"
                    if st.get_option("theme.base") == "dark"
                    else "plotly_white"
                ),
                height=300,
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)"
            )

            st.plotly_chart(
                rainfall_fig,
                use_container_width=True
            )

            temp_col, humidity_col = st.columns(2)

            with temp_col:

                temp_fig = px.line(
                    weather_df,
                    x="week",
                    y="avg_temp_c",
                    title="Average Temperature",
                    markers=True
                )

                temp_fig.update_layout(
                    template=(
                        "plotly_dark"
                        if st.get_option("theme.base") == "dark"
                        else "plotly_white"
                    ),
                    height=280,
                    paper_bgcolor="rgba(0,0,0,0)",
                    plot_bgcolor="rgba(0,0,0,0)"
                )

                st.plotly_chart(
                    temp_fig,
                    use_container_width=True
                )

            with humidity_col:

                humidity_fig = px.line(
                    weather_df,
                    x="week",
                    y="relative_humidity_pct",
                    title="Relative Humidity",
                    markers=True
                )

                humidity_fig.update_layout(
                    template=(
                        "plotly_dark"
                        if st.get_option("theme.base") == "dark"
                        else "plotly_white"
                    ),
                    height=280,
                    paper_bgcolor="rgba(0,0,0,0)",
                    plot_bgcolor="rgba(0,0,0,0)"
                )

                st.plotly_chart(
                    humidity_fig,
                    use_container_width=True
                )

        else:

            st.info(
                "No historical weather data available."
            )

    # ------------------------------------
    # WARD INDICATORS
    # ------------------------------------

    with indicators_tab:

        render_section_title(
            "Environmental Vulnerability",
            "Actual ward-level characteristics from the dataset."
        )

        profile = get_ward_profile(filtered_df)

        render_ward_profile(profile)

        st.caption(
            "These indicators describe recorded ward characteristics. "
            "They are not model-generated risk scores."
        )


# ========================================
# RIGHT: LOCATION & ML FORECAST
# ========================================

with right_col:

    st.markdown(
        "### Selected Location"
    )

    st.markdown(f"**City:** {city}")

    st.markdown(f"**Ward:** {selected_ward}")

    st.markdown(
        f"**Observations:** {len(filtered_df):,}"
    )

    st.divider()

    st.markdown(
        "### Model Indicators"
    )

    ward_forecasts = get_ward_forecasts(
        forecast_df,
        city,
        selected_ward
    )

    # ------------------------------------
    # DISPLAY RISK BADGE
    # ------------------------------------

    def display_risk_badge(risk):

        colors = {
            "Low": "#35C98A",
            "Medium": "#E7B84B",
            "High": "#F08B43",
            "Critical": "#EF5361"
        }

        color = colors.get(
            risk,
            "#9FB0C8"
        )

        st.markdown(
            f"""
            <span style="
                background-color:{color}22;
                color:{color};
                border:1px solid {color};
                padding:7px 14px;
                border-radius:20px;
                font-weight:600;
                font-size:14px;
            ">
                {risk} Risk
            </span>
            """,
            unsafe_allow_html=True
        )

    # ------------------------------------
    # NO FORECAST AVAILABLE
    # ------------------------------------

    if ward_forecasts.empty:

        st.warning(
            "No forecast available for this selection."
        )

    # ------------------------------------
    # INDIVIDUAL WARD FORECAST
    # ------------------------------------

    elif selected_ward != "All Wards":

        st.caption(
            "Predicted dengue risk for the selected ward."
        )

        predictions = ward_forecasts.sort_values(
            "weeks_ahead"
        )

        for _, prediction in predictions.iterrows():

            weeks = int(
                prediction["weeks_ahead"]
            )

            risk = prediction["risk_level"]

            with st.container(border=True):

                st.markdown(
                    f"### {weeks}-Week Forecast"
                )

                display_risk_badge(risk)


    # ------------------------------------
    # ALL WARDS FORECAST
    # ------------------------------------

    else:

        st.caption(
            "Predicted dengue risk across all wards."
        )

        summary_forecast = (
            ward_forecasts
            .groupby("weeks_ahead")
            .agg(
                risk_level=(
                    "risk_level",
                    lambda x: (
                        x.mode().iloc[0]
                        if not x.mode().empty
                        else "Low"
                    )
                )
            )
            .reset_index()
            .sort_values("weeks_ahead")
        )

        risk_colors = {
            "Low": "🟢",
            "Medium": "🟡",
            "High": "🟠",
            "Critical": "🔴"
        }

        for _, prediction in summary_forecast.iterrows():

            weeks = int(
                prediction["weeks_ahead"]
            )

            risk = prediction["risk_level"]

            with st.container(border=True):

                st.markdown(
                    f"### {weeks}-Week Forecast"
                )

                st.markdown(
                    f"## {risk_colors.get(risk, '⚪')} {risk} Risk"
                )

    # ------------------------------------
    # FORECAST DISCLAIMER
    # ------------------------------------

    st.caption(
        "Experimental forecasts based on available historical weather "
        "features and ward-level characteristics. "
        "Not clinically validated."
    )

    st.divider()

    # ------------------------------------
    # HISTORICAL WEATHER SUMMARY
    # ------------------------------------

    st.markdown(
        "### Historical Weather Summary"
    )

    st.metric(
        "Average Humidity",
        f'{summary["avg_humidity"]:.1f}%'
    )

    st.metric(
        "Average Rainfall",
        f'{summary["avg_rainfall"]:.1f} mm'
    )

    st.metric(
        "Historical Records",
        f'{summary["total_records"]:,}'
    )


# ========================================
# HISTORICAL MODEL BACKTESTING
# ========================================

st.divider()

render_section_title(
    "Historical Model Backtesting",
    "Evaluation of model predictions on historical test data."
)

st.info(
    "These are historical test predictions from 2024–2025, "
    "not current outbreak forecasts."
)

if not backtest_df.empty:

    selected_backtest = backtest_df[
        backtest_df["city"] == city
    ].copy()

    if selected_ward != "All Wards":

        selected_backtest = selected_backtest[
            selected_backtest["ward_id"] == selected_ward
        ]

    if not selected_backtest.empty:

        risk_order = [
            "Low",
            "Medium",
            "High",
            "Critical"
        ]

        # --------------------------------
        # RISK DISTRIBUTION
        # --------------------------------

        risk_counts = (
            selected_backtest["risk_level"]
            .value_counts()
            .reindex(risk_order, fill_value=0)
            .reset_index()
        )

        risk_counts.columns = [
            "Risk Level",
            "Predictions"
        ]

        col1, col2 = st.columns(
            [1.2, 1]
        )

        with col1:

            st.markdown(
                "### Historical Risk Distribution"
            )

            risk_fig = px.bar(
                risk_counts,
                x="Risk Level",
                y="Predictions",
                color="Risk Level",
                category_orders={
                    "Risk Level": risk_order
                },
                color_discrete_map={
                    "Low": "#35C98A",
                    "Medium": "#E7B84B",
                    "High": "#F08B43",
                    "Critical": "#EF5361"
                }
            )

            risk_fig.update_layout(
                height=330,
                showlegend=False,
                template=(
                    "plotly_dark"
                    if st.get_option("theme.base") == "dark"
                    else "plotly_white"
                )
            )

            st.plotly_chart(
                risk_fig,
                use_container_width=True
            )

        with col2:

            st.markdown(
                "### Risk Summary"
            )

            for risk in risk_order:

                count = int(
                    risk_counts.loc[
                        risk_counts["Risk Level"] == risk,
                        "Predictions"
                    ].iloc[0]
                )

                st.metric(
                    f"{risk} Risk Predictions",
                    f"{count:,}"
                )

        st.divider()

        # --------------------------------
        # HISTORICAL WARD PREDICTIONS
        # --------------------------------

        st.markdown(
            "### Historical Ward Predictions"
        )

        available_horizons = sorted(
            selected_backtest["weeks_ahead"]
            .dropna()
            .unique()
            .tolist()
        )

        if available_horizons:

            horizon = st.selectbox(
                "Select Backtesting Horizon",
                available_horizons,
                format_func=lambda x: (
                    f"{int(x)}-Week Prediction"
                ),
                key="backtest_horizon"
            )

            horizon_df = selected_backtest[
                selected_backtest["weeks_ahead"] == horizon
            ].copy()

            horizon_df = horizon_df.sort_values(
                "predicted_cases",
                ascending=False
            )

            display_df = horizon_df[
                [
                    "ward_id",
                    "forecast_origin",
                    "target_date",
                    "predicted_cases",
                    "risk_level"
                ]
            ].copy()

            display_df.columns = [
                "Ward",
                "Forecast Origin",
                "Target Date",
                "Predicted Cases",
                "Risk Level"
            ]

            st.dataframe(
                display_df,
                use_container_width=True,
                hide_index=True,
                column_config={
                    "Predicted Cases": st.column_config.NumberColumn(
                        format="%.2f"
                    ),
                    "Forecast Origin": st.column_config.DateColumn(
                        format="DD MMM YYYY"
                    ),
                    "Target Date": st.column_config.DateColumn(
                        format="DD MMM YYYY"
                    )
                }
            )

            st.caption(
                "Historical predictions use the model's existing "
                "risk classification thresholds."
            )

        else:

            st.info(
                "No historical prediction horizons available."
            )

    else:

        st.info(
            "No historical backtesting records for this location."
        )

else:

    st.warning(
        "Historical backtesting data is unavailable."
    )


# ========================================
# PUBLIC HEALTH ACTION RECOMMENDATIONS
# ========================================

st.divider()

render_section_title(
    "Public Health Action Plan",
    "Suggested actions based on current model forecast risk."
)

if not ward_forecasts.empty:

    available_horizons = sorted(
        ward_forecasts["weeks_ahead"]
        .dropna()
        .unique()
        .tolist()
    )

    selected_horizon = st.selectbox(
        "Select Forecast Window",
        available_horizons,
        format_func=lambda x: (
            f"{int(x)}-Week Forecast"
        ),
        key="action_horizon"
    )

    action_forecasts = ward_forecasts[
        ward_forecasts["weeks_ahead"] == selected_horizon
    ].copy()

    if selected_ward != "All Wards":

        action_forecasts = action_forecasts[
            action_forecasts["ward_id"] == selected_ward
        ]

    if not action_forecasts.empty:

        for _, prediction in action_forecasts.iterrows():

            risk = prediction["risk_level"]

            ward = prediction["ward_id"]

            plan = get_action_recommendations(risk)

            with st.container(border=True):

                st.markdown(
                    f"### {ward}"
                )

                st.write(
                    f"Predicted Risk: **{risk}**"
                )

                if plan:

                    st.write(
                        f"Priority: **{plan['priority']}**"
                    )

                    st.write(
                        f"Responsible Team: **{plan['team']}**"
                    )

                    st.write(
                        f"Suggested Timeframe: **{plan['timeframe']}**"
                    )

                    st.markdown(
                        "#### Recommended Actions"
                    )

                    for action in plan["actions"]:

                        st.markdown(
                            f"- {action}"
                        )

                else:

                    st.info(
                        "No recommendation available for this risk level."
                    )

    else:

        st.info(
            "No forecasts available for this selection."
        )

else:

    st.info(
        "No forecast available for action recommendations."
    )

st.caption(
    "These are suggested operational actions, not clinically "
    "validated treatment instructions. Actual deployment decisions "
    "require public health authority assessment."
)


# ========================================
# WARD INTELLIGENCE RANKING
# ========================================

st.divider()

render_section_title(
    "Ward Intelligence Ranking",
    "Ranking by historical dengue case count in the selected period, "
    "not by predicted outbreak risk."
)

ranking_df = get_ward_ranking(
    city_period_df
)

ranking_df = ranking_df.rename(
    columns={
        "city": "City",
        "ward_id": "Ward",
        "historical_cases": "Historical Cases",
        "avg_rainfall": "Avg Rainfall (mm)",
        "waterlogging": "Waterlogging Index",
        "population_density": "Population Density",
        "sanitation": "Sanitation Score"
    }
)

st.dataframe(
    ranking_df.style.highlight_max(
        subset=["Historical Cases"],
        color="#D9485525"
    ),
    use_container_width=True,
    hide_index=True,
    column_config={
        "Historical Cases": st.column_config.NumberColumn(
            format="%d"
        ),
        "Avg Rainfall (mm)": st.column_config.NumberColumn(
            format="%.2f"
        )
    }
)


# ========================================
# FOOTER
# ========================================

render_footer()
