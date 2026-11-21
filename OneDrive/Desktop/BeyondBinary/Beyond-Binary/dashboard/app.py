
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
    get_ward_profile
)

from style import load_css

from components import (
    render_header,
    render_data_notice,
    render_section_title,
    render_ward_profile,
    render_footer
)


# --------------------------------
# PAGE CONFIGURATION
# --------------------------------

st.set_page_config(
    page_title="DengueWatch | Beyond-Binary",
    page_icon="🦟",
    layout="wide",
    initial_sidebar_state="expanded"
)


# --------------------------------
# LOAD CSS
# --------------------------------

st.markdown(
    load_css(),
    unsafe_allow_html=True
)


# --------------------------------
# LOAD DATASET
# --------------------------------

try:
    df = load_data()

except Exception as error:
    st.error(f"Dataset loading failed: {error}")

    st.info(
        "Please check that your CSV file is inside "
        "the data folder and that its filename is correct."
    )

    st.stop()


# --------------------------------
# SIDEBAR
# --------------------------------

st.sidebar.title("Layers")

st.sidebar.caption(
    "DENGUE SURVEILLANCE CONTROLS"
)

st.sidebar.markdown("### Location")

# Get available cities from dataset
cities = sorted(df["city"].dropna().unique().tolist())

if not cities:
    st.error("No city information was found in the dataset.")
    st.stop()

# Set Chattogram as default if available
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


# --------------------------------
# DYNAMIC WARD LIST
# --------------------------------

city_data = df[df["city"] == city]

wards = sorted(
    city_data["ward_id"].dropna().unique().tolist()
)

selected_ward = st.sidebar.selectbox(
    "Administrative Level / Ward",
    ["All Wards"] + wards
)


# --------------------------------
# DATE FILTER
# --------------------------------

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


# --------------------------------
# FILTER DATA
# --------------------------------

filtered_df = filter_data(
    df,
    city,
    selected_ward,
    start_date,
    end_date
)

if filtered_df.empty:

    st.warning(
        "No observations are available for this selection."
    )

    st.stop()


# Keep all city wards for comparison
city_period_df = filter_data(
    df,
    city,
    "All Wards",
    start_date,
    end_date
)


# --------------------------------
# DASHBOARD HEADER
# --------------------------------

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


# --------------------------------
# DASHBOARD TITLE
# --------------------------------

st.markdown("## Surveillance Overview")

st.caption(
    f"Monitoring area: {city} | "
    f"Administrative level: {selected_ward}"
)

st.caption(
    f"Historical reporting period: {start_date} to {end_date}"
)


# --------------------------------
# SUMMARY METRICS
# --------------------------------

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


# --------------------------------
# MAIN ANALYTICS AREA
# --------------------------------

left_col, right_col = st.columns(
    [2.1, 1],
    gap="large"
)


# --------------------------------
# LEFT: ANALYTICS TABS
# --------------------------------

with left_col:

    cases_tab, weather_tab, indicators_tab = st.tabs(
        [
            "Cases",
            "Weather",
            "Ward Indicators"
        ]
    )


    # --------------------------------
    # CASES
    # --------------------------------

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

            st.info("No historical case data available.")


    # --------------------------------
    # WEATHER
    # --------------------------------

    with weather_tab:

        render_section_title(
            "Weather Analysis",
            "Historical rainfall, temperature and humidity."
        )

        weather_df = get_weather_data(filtered_df)

        if not weather_df.empty:

            # Weekly rainfall chart
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


            # Temperature and humidity charts
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

            st.info("No historical weather data available.")


    # --------------------------------
    # WARD INDICATORS
    # --------------------------------

    with indicators_tab:

        render_section_title(
            "Environmental Vulnerability",
            "Actual ward-level characteristics from the dataset."
        )

        profile = get_ward_profile(filtered_df)

        render_ward_profile(profile)

        st.caption(
            "These indicators describe recorded ward "
            "characteristics. They are not model-generated "
            "risk scores."
        )


# --------------------------------
# RIGHT: WARD INFORMATION
# --------------------------------

with right_col:

    st.markdown("### Selected Location")

    st.markdown(
        f"**City:** {city}"
    )

    st.markdown(
        f"**Ward:** {selected_ward}"
    )

    st.markdown(
        f"**Observations:** {len(filtered_df):,}"
    )

    st.divider()

    st.markdown("### Model Indicators")

    st.info(
        "ML forecasting engine is not connected yet."
    )

    st.metric(
        "Forecast Horizon",
        "Pending"
    )

    st.metric(
        "Model Validation",
        "Pending"
    )

    st.caption(
        "No artificial forecast scores are displayed."
    )

    st.divider()

    st.markdown("### Historical Weather Summary")

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


# --------------------------------
# WARD RANKING
# --------------------------------

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


# --------------------------------
# FOOTER
# --------------------------------

render_footer()
