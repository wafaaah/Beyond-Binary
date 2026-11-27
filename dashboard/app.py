import calendar
from pathlib import Path

import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go

from mock_data import (
    load_data,
    filter_data,
    get_summary,
    get_monthly_cases,
    get_weather_data,
    get_ward_ranking,
    get_ward_profile,
    load_forecasts,
    get_ward_forecasts,
)

from style import load_css

from components import (
    render_header,
    render_data_notice,
    render_section_title,
    render_ward_profile,
    render_footer,
)

from action_recommendations import get_action_recommendations

try:
    from map3d import render_ward_3d_map
except Exception:
    render_ward_3d_map = None


# ============================================================
# CONSTANTS & HELPERS
# ============================================================

RISK_ORDER = ["Critical", "High", "Medium", "Low"]
RISK_LEVELS = ["Low", "Medium", "High", "Critical"]

RISK_COLORS = {
    "Low": "#35C98A",
    "Medium": "#E7B84B",
    "High": "#F08B43",
    "Critical": "#EF5361",
}


def html(text):
    """Remove indentation so Streamlit does not render HTML as a code block."""
    return "".join(line.strip() for line in text.splitlines())


def classify_risk(value):
    """Keep risk classification consistent with the prediction pipeline."""
    value = float(value)

    if value < 1:
        return "Low"
    elif value < 5:
        return "Medium"
    elif value < 10:
        return "High"
    return "Critical"


def style_fig(fig, height=340):
    fig.update_layout(
        template="plotly_dark",
        height=height,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=10, r=10, t=40, b=10),
        font=dict(color="#C9D6D2"),
        xaxis=dict(gridcolor="rgba(255,255,255,0.06)"),
        yaxis=dict(gridcolor="rgba(255,255,255,0.06)"),
    )
    return fig


def forecast_strip(fdf, selected_ward):
    """Render one forecast summary card for each available horizon."""
    if fdf.empty:
        st.warning("No forecast available for this selection.")
        return

    horizons = sorted(fdf["weeks_ahead"].dropna().unique().tolist())
    if not horizons:
        st.warning("Forecast horizons are unavailable.")
        return

    cols = st.columns(len(horizons))

    for col, weeks in zip(cols, horizons):
        group = fdf[fdf["weeks_ahead"] == weeks]
        counts = group["risk_level"].value_counts()

        worst = next(
            (risk for risk in RISK_ORDER if risk in counts.index),
            "Low",
        )
        color = RISK_COLORS[worst]

        total = float(group["predicted_cases"].sum())
        cases_text = "<1" if total < 1 else f"~{total:.0f}"

        if selected_ward == "All Wards":
            alert_count = int(
                counts.get("Critical", 0) + counts.get("High", 0)
            )

            top = group.sort_values(
                "predicted_cases", ascending=False
            ).iloc[0]

            line1 = (
                f"{alert_count} of {len(group)} wards High/Critical "
                f"&middot; {cases_text} cases expected"
            )
            line2 = (
                f"Highest: {top['ward_id']} "
                f"({top['predicted_cases']:.2f})"
            )
        else:
            line1 = (
                f"{selected_ward} &middot; {cases_text} cases expected"
            )
            line2 = ""

        col.markdown(
            html(
                f"""
                <div class="fc-card" style="border-left:6px solid {color};">
                    <div class="fc-label">{int(weeks)}-WEEK FORECAST</div>
                    <div class="fc-risk" style="color:{color};">{worst}</div>
                    <div class="fc-line">{line1}</div>
                    <div class="fc-line fc-muted">{line2}</div>
                </div>
                """
            ),
            unsafe_allow_html=True,
        )

    caption = "Experimental model estimates, not clinically validated."
    if "forecast_origin" in fdf.columns and not fdf.empty:
        origin = pd.to_datetime(
            fdf["forecast_origin"], errors="coerce"
        ).dropna()
        if not origin.empty:
            caption = (
                f"Forecast origin: {origin.max():%d %b %Y}. "
                + caption
            )

    st.caption(caption)


def get_peak_season_months(backtest_data, selected_city, selected_ward):
    """
    Calculate peak calendar months from unique actual test observations.

    The same actual ward/date can appear more than once in the backtesting
    file because it may be predicted by different forecast horizons. It is
    therefore deduplicated before monthly aggregation.
    """
    if backtest_data.empty:
        return [], pd.Series(dtype="float64")

    required = {"ward_id", "target_date", "actual_cases", "city"}
    if not required.issubset(backtest_data.columns):
        return [], pd.Series(dtype="float64")

    actual = backtest_data.copy()
    actual = actual[actual["city"] == selected_city]

    if selected_ward != "All Wards":
        actual = actual[actual["ward_id"] == selected_ward]

    actual["target_date"] = pd.to_datetime(
        actual["target_date"], errors="coerce"
    )
    actual["actual_cases"] = pd.to_numeric(
        actual["actual_cases"], errors="coerce"
    )

    actual = actual.dropna(
        subset=["ward_id", "target_date", "actual_cases"]
    )

    actual = actual.drop_duplicates(
        subset=["ward_id", "target_date"]
    )

    if actual.empty:
        return [], pd.Series(dtype="float64")

    monthly_cases = actual.groupby(
        actual["target_date"].dt.month
    )["actual_cases"].sum()

    if monthly_cases.empty:
        return [], monthly_cases

    peak_months = (
        monthly_cases.nlargest(min(3, len(monthly_cases)))
        .index.astype(int)
        .tolist()
    )

    return peak_months, monthly_cases


def render_seasonal_intelligence(
    backtest_data,
    forecast_data,
    selected_city,
    selected_ward,
):
    """Render historical peak season and current forecast-month context."""
    peak_months, monthly_cases = get_peak_season_months(
        backtest_data,
        selected_city,
        selected_ward,
    )

    peak_month_text = (
        " · ".join(calendar.month_abbr[m] for m in sorted(peak_months))
        if peak_months
        else "Unavailable"
    )

    forecast_months = []
    if (
        not forecast_data.empty
        and "target_date" in forecast_data.columns
    ):
        target_dates = pd.to_datetime(
            forecast_data["target_date"], errors="coerce"
        ).dropna()
        forecast_months = sorted(
            target_dates.dt.month.unique().astype(int).tolist()
        )

    forecast_month_text = (
        " · ".join(calendar.month_abbr[m] for m in forecast_months)
        if forecast_months
        else "Unavailable"
    )

    peak_overlap = set(forecast_months).intersection(peak_months)

    if not forecast_months or not peak_months:
        season_status = "Unavailable"
    elif len(peak_overlap) == len(forecast_months):
        season_status = "Peak-season window"
    elif peak_overlap:
        season_status = "Includes peak months"
    else:
        season_status = "Outside historical peak months"

    st.markdown("## Seasonal Dengue Intelligence")

    with st.container(border=True):
        season_col1, season_col2 = st.columns([1.2, 1])

        with season_col1:
            st.caption("HISTORICAL PEAK SEASON")
            st.markdown(f"### {peak_month_text}")
            st.write(
                "Peak months calculated from unique actual observations "
                "in the historical test dataset."
            )

        with season_col2:
            st.caption("FORECAST SEASON CONTEXT")
            st.markdown(f"### {season_status}")
            st.write(f"Forecast target months: {forecast_month_text}")

        if peak_months and not monthly_cases.empty:
            st.caption(
                "Peak-month ranking is based on aggregated actual cases "
                "for the selected city/ward in the historical test period."
            )
        else:
            st.warning(
                "Historical peak season is unavailable for this selection. "
                "Check the historical backtesting data."
            )

        all_low = (
            not forecast_data.empty
            and "risk_level" in forecast_data.columns
            and forecast_data["risk_level"].notna().all()
            and forecast_data["risk_level"].eq("Low").all()
        )

        if (
            all_low
            and forecast_months
            and peak_months
            and not peak_overlap
        ):
            st.info(
                "Low predicted cases are occurring outside the historical "
                "peak months. This is consistent with the lower-incidence "
                "seasonal pattern in the historical test data. Off-season "
                "does not mean zero dengue risk."
            )
        elif (
            all_low
            and peak_overlap
        ):
            st.info(
                "The model currently predicts Low risk, although the "
                "forecast window overlaps historical peak months. Continue "
                "routine surveillance; a Low prediction does not mean zero risk."
            )

        st.caption(
            "Historical seasonality is calculated from actual test observations. "
            "Forecasts are experimental model estimates, not confirmed cases."
        )


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="DengueWatch | Beyond-Binary",
    page_icon="🦟",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ============================================================
# LOAD CSS
# ============================================================

st.markdown(load_css(), unsafe_allow_html=True)

st.markdown(
    html(
        """
        <style>
        [data-testid="stToolbar"], footer {display: none !important;}
        .block-container {padding-top: 1.5rem; max-width: 1300px;}

        [data-testid="stMetric"] {
            background: rgba(255,255,255,0.04);
            border: 1px solid rgba(255,255,255,0.08);
            border-radius: 16px;
            padding: 14px 18px;
        }

        .fc-card {
            background: rgba(255,255,255,0.04);
            border: 1px solid rgba(255,255,255,0.08);
            border-radius: 16px;
            padding: 16px 20px;
            margin-bottom: 8px;
        }
        .fc-label {color: #9fb3ad; font-size: 12px; letter-spacing: 1px;}
        .fc-risk {font-size: 30px; font-weight: 700; line-height: 1.3;}
        .fc-line {color: #c9d6d2; font-size: 13px;}
        .fc-muted {color: #8fa39d;}
        </style>
        """
    ),
    unsafe_allow_html=True,
)


# ============================================================
# LOAD MAIN DATA
# ============================================================

try:
    df = load_data()
    forecast_df = load_forecasts()
except Exception as error:
    st.error(f"Data loading failed: {error}")
    st.info("Please check your data files and their locations.")
    st.stop()

if df.empty:
    st.error("The historical dengue dataset is empty.")
    st.stop()

if forecast_df.empty:
    st.warning("No current forecast records were found.")
    forecast_df = pd.DataFrame(
        columns=[
            "ward_id",
            "city",
            "forecast_origin",
            "target_date",
            "weeks_ahead",
            "predicted_cases",
            "risk_level",
        ]
    )
else:
    required_forecast_columns = {
        "ward_id",
        "city",
        "forecast_origin",
        "target_date",
        "weeks_ahead",
        "predicted_cases",
    }
    missing_forecast_columns = (
        required_forecast_columns - set(forecast_df.columns)
    )

    if missing_forecast_columns:
        st.error(
            "Forecast file is missing required columns: "
            f"{sorted(missing_forecast_columns)}"
        )
        st.stop()

    forecast_df["forecast_origin"] = pd.to_datetime(
        forecast_df["forecast_origin"], errors="coerce"
    )
    forecast_df["target_date"] = pd.to_datetime(
        forecast_df["target_date"], errors="coerce"
    )
    forecast_df["predicted_cases"] = pd.to_numeric(
        forecast_df["predicted_cases"], errors="coerce"
    )
    forecast_df["weeks_ahead"] = pd.to_numeric(
        forecast_df["weeks_ahead"], errors="coerce"
    )

    forecast_df = forecast_df.dropna(
        subset=[
            "ward_id",
            "city",
            "forecast_origin",
            "target_date",
            "weeks_ahead",
            "predicted_cases",
        ]
    ).copy()

    if "risk_level" not in forecast_df.columns:
        forecast_df["risk_level"] = forecast_df[
            "predicted_cases"
        ].apply(classify_risk)
    else:
        forecast_df["risk_level"] = forecast_df[
            "risk_level"
        ].fillna(
            forecast_df["predicted_cases"].apply(classify_risk)
        )


# ============================================================
# LOAD HISTORICAL BACKTESTING DATA
# ============================================================

BACKTEST_PATH = (
    Path(__file__).resolve().parents[1]
    / "data"
    / "processed"
    / "weather_model_predictions.csv"
)

try:
    if not BACKTEST_PATH.exists():
        raise FileNotFoundError(
            f"Historical predictions file not found: {BACKTEST_PATH}"
        )

    backtest_df = pd.read_csv(BACKTEST_PATH)

    required_backtest_columns = {
        "ward_id",
        "forecast_origin",
        "target_date",
        "weeks_ahead",
        "actual_cases",
        "predicted_cases",
    }
    missing_backtest_columns = (
        required_backtest_columns - set(backtest_df.columns)
    )
    if missing_backtest_columns:
        raise ValueError(
            "Historical prediction file is missing columns: "
            f"{sorted(missing_backtest_columns)}"
        )

    backtest_df["forecast_origin"] = pd.to_datetime(
        backtest_df["forecast_origin"], errors="coerce"
    )
    backtest_df["target_date"] = pd.to_datetime(
        backtest_df["target_date"], errors="coerce"
    )

    for column in [
        "weeks_ahead",
        "actual_cases",
        "predicted_cases",
    ]:
        backtest_df[column] = pd.to_numeric(
            backtest_df[column], errors="coerce"
        )

    backtest_df = backtest_df.dropna(
        subset=[
            "ward_id",
            "forecast_origin",
            "target_date",
            "weeks_ahead",
            "actual_cases",
            "predicted_cases",
        ]
    ).copy()

    backtest_df["risk_level"] = backtest_df[
        "predicted_cases"
    ].apply(classify_risk)

    ward_city = df[["ward_id", "city"]].drop_duplicates(
        subset=["ward_id"]
    )

    backtest_df = backtest_df.merge(
        ward_city,
        on="ward_id",
        how="left",
        validate="many_to_one",
    )

except Exception as error:
    backtest_df = pd.DataFrame()
    st.warning(
        f"Historical backtesting data could not be loaded: {error}"
    )


# ============================================================
# SIDEBAR
# ============================================================

st.sidebar.title("Layers")
st.sidebar.caption("DENGUE SURVEILLANCE CONTROLS")
st.sidebar.markdown("### Location")

cities = sorted(df["city"].dropna().unique().tolist())
if not cities:
    st.error("No city information found.")
    st.stop()

default_city = cities.index("Chattogram") if "Chattogram" in cities else 0

city = st.sidebar.selectbox(
    "Select City",
    cities,
    index=default_city,
)


# ============================================================
# WARD SELECTION
# ============================================================

city_data = df[df["city"] == city]
wards = sorted(city_data["ward_id"].dropna().unique().tolist())

selected_ward = st.sidebar.selectbox(
    "Administrative Level / Ward",
    ["All Wards"] + wards,
)


# ============================================================
# HISTORICAL DATE FILTER
# ============================================================

st.sidebar.divider()
st.sidebar.markdown("### Historical Period")

min_date = df["date"].min().date()
max_date = df["date"].max().date()

date_options = [
    "All Available Data",
    "Last 12 Months",
    "Last 6 Months",
    "Last 3 Months",
    "Custom Range",
]

period = st.sidebar.selectbox("Select Period", date_options)

if period == "All Available Data":
    start_date = min_date
    end_date = max_date
elif period == "Last 12 Months":
    start_date = max(
        min_date,
        (df["date"].max() - pd.DateOffset(months=12)).date(),
    )
    end_date = max_date
elif period == "Last 6 Months":
    start_date = max(
        min_date,
        (df["date"].max() - pd.DateOffset(months=6)).date(),
    )
    end_date = max_date
elif period == "Last 3 Months":
    start_date = max(
        min_date,
        (df["date"].max() - pd.DateOffset(months=3)).date(),
    )
    end_date = max_date
else:
    selected_dates = st.sidebar.date_input(
        "Choose date range",
        value=(min_date, max_date),
        min_value=min_date,
        max_value=max_date,
    )

    if isinstance(selected_dates, (tuple, list)):
        if len(selected_dates) == 2:
            start_date, end_date = selected_dates
        elif len(selected_dates) == 1:
            start_date = selected_dates[0]
            end_date = selected_dates[0]
        else:
            start_date, end_date = min_date, max_date
    else:
        start_date = selected_dates
        end_date = selected_dates

st.sidebar.divider()
st.sidebar.caption("Source: Provided Bangladesh dengue dataset")
st.sidebar.caption("Historical observations only.")


# ============================================================
# FILTER MAIN DATA
# ============================================================

filtered_df = filter_data(
    df,
    city,
    selected_ward,
    start_date,
    end_date,
)

if filtered_df.empty:
    st.warning("No observations available for this selection.")
    st.stop()

city_period_df = filter_data(
    df,
    city,
    "All Wards",
    start_date,
    end_date,
)

ward_forecasts = get_ward_forecasts(
    forecast_df,
    city,
    selected_ward,
)


# ============================================================
# DASHBOARD HEADER
# ============================================================

render_header()

st.markdown(
    """
    <div class="dashboard-subtitle">
        WARD RISK INTELLIGENCE SYSTEM | BANGLADESH
    </div>
    """,
    unsafe_allow_html=True,
)

render_data_notice()


# ============================================================
# SURVEILLANCE OVERVIEW + SUMMARY METRICS
# ============================================================

st.markdown("## Surveillance Overview")
st.caption(
    f"Monitoring area: {city} | "
    f"Administrative level: {selected_ward}"
)
st.caption(
    f"Historical reporting period: {start_date} to {end_date}"
)

summary = get_summary(filtered_df)

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        "Historical Dengue Cases",
        f'{summary["total_cases"]:,}',
    )

with col2:
    st.metric("Wards Represented", summary["total_wards"])

with col3:
    st.metric(
        "Average Rainfall",
        f'{summary["avg_rainfall"]:.1f} mm',
    )

with col4:
    st.metric(
        "Average Temperature",
        f'{summary["avg_temperature"]:.1f} °C',
    )


# ============================================================
# SEASONAL INTELLIGENCE CARD
# Placed after overview metrics and before forecast outlook.
# ============================================================

render_seasonal_intelligence(
    backtest_df,
    ward_forecasts,
    city,
    selected_ward,
)

st.divider()


# ============================================================
# HERO: FORECAST STRIP
# ============================================================

st.markdown("### Dengue Forecast Outlook")
forecast_strip(ward_forecasts, selected_ward)
st.divider()


# ============================================================
# MAIN TABS
# ============================================================

(
    tab_overview,
    tab_forecast,
    tab_map,
    tab_backtest,
    tab_action,
    tab_ranking,
) = st.tabs(
    [
        "Overview",
        "Forecast",
        "3D Risk Map",
        "Backtesting",
        "Action Plan",
        "Ward Ranking",
    ]
)


# ============================================================
# TAB 1: OVERVIEW
# ============================================================

with tab_overview:
    left_col, right_col = st.columns([2.1, 1], gap="large")

    with left_col:
        cases_tab, weather_tab, indicators_tab = st.tabs(
            ["Cases", "Weather", "Ward Indicators"]
        )

        # HISTORICAL CASES
        with cases_tab:
            render_section_title(
                "Historical Dengue Cases",
                "Monthly aggregation of available weekly observations.",
            )

            monthly_df = get_monthly_cases(filtered_df)

            if not monthly_df.empty:
                fig = px.area(
                    monthly_df,
                    x="month",
                    y="dengue_cases",
                    labels={
                        "month": "Month",
                        "dengue_cases": "Reported Cases",
                    },
                    color_discrete_sequence=["#20A878"],
                )
                fig.update_traces(line=dict(width=2.5))
                fig.update_layout(showlegend=False)

                st.plotly_chart(
                    style_fig(fig, 360),
                    use_container_width=True,
                )
            else:
                st.info("No historical case data available.")

        # WEATHER ANALYSIS
        with weather_tab:
            render_section_title(
                "Weather Analysis",
                "Historical rainfall, temperature and humidity.",
            )

            weather_data = get_weather_data(filtered_df)

            if not weather_data.empty:
                rainfall_fig = px.bar(
                    weather_data,
                    x="week",
                    y="rainfall_mm",
                    title="Weekly Rainfall",
                    color_discrete_sequence=["#249DBB"],
                    labels={
                        "week": "Date",
                        "rainfall_mm": "Rainfall (mm)",
                    },
                )
                st.plotly_chart(
                    style_fig(rainfall_fig, 300),
                    use_container_width=True,
                )

                temp_col, humidity_col = st.columns(2)

                with temp_col:
                    temp_fig = px.line(
                        weather_data,
                        x="week",
                        y="avg_temp_c",
                        title="Average Temperature",
                        color_discrete_sequence=["#F08B43"],
                    )
                    st.plotly_chart(
                        style_fig(temp_fig, 280),
                        use_container_width=True,
                    )

                with humidity_col:
                    humidity_fig = px.line(
                        weather_data,
                        x="week",
                        y="relative_humidity_pct",
                        title="Relative Humidity",
                        color_discrete_sequence=["#8E9BFF"],
                    )
                    st.plotly_chart(
                        style_fig(humidity_fig, 280),
                        use_container_width=True,
                    )
            else:
                st.info("No historical weather data available.")

        # WARD INDICATORS
        with indicators_tab:
            render_section_title(
                "Environmental Vulnerability",
                "Actual ward-level characteristics from the dataset.",
            )

            profile = get_ward_profile(filtered_df)
            render_ward_profile(profile)

            st.caption(
                "These indicators describe recorded ward characteristics. "
                "They are not model-generated risk scores."
            )

    # RIGHT: LOCATION + WEATHER SUMMARY
    with right_col:
        st.markdown("### Selected Location")
        st.markdown(f"**City:** {city}")
        st.markdown(f"**Ward:** {selected_ward}")
        st.markdown(f"**Observations:** {len(filtered_df):,}")

        st.divider()
        st.markdown("### Historical Weather Summary")

        st.metric(
            "Average Humidity",
            f'{summary["avg_humidity"]:.1f}%',
        )
        st.metric(
            "Average Rainfall",
            f'{summary["avg_rainfall"]:.1f} mm',
        )
        st.metric(
            "Historical Records",
            f'{summary["total_records"]:,}',
        )


# ============================================================
# TAB 2: FORECAST DETAILS
# ============================================================

with tab_forecast:
    render_section_title(
        "Ward-Level Forecast",
        "Predicted weekly dengue cases and risk level for each ward.",
    )

    if ward_forecasts.empty:
        st.info("No forecast available for this selection.")
    else:
        fc_horizons = sorted(
            ward_forecasts["weeks_ahead"].dropna().unique().tolist()
        )

        if not fc_horizons:
            st.info("No valid forecast horizon is available.")
        else:
            fc_horizon = st.selectbox(
                "Forecast Window",
                fc_horizons,
                format_func=lambda x: f"{int(x)}-Week Forecast",
                key="forecast_horizon",
            )

            fc = (
                ward_forecasts[
                    ward_forecasts["weeks_ahead"] == fc_horizon
                ]
                .sort_values("predicted_cases", ascending=False)
                .copy()
            )

            bar_fig = px.bar(
                fc,
                x="ward_id",
                y="predicted_cases",
                color="risk_level",
                category_orders={"risk_level": RISK_LEVELS},
                color_discrete_map=RISK_COLORS,
                labels={
                    "ward_id": "Ward",
                    "predicted_cases": "Predicted Cases",
                    "risk_level": "Risk Level",
                },
            )

            st.plotly_chart(
                style_fig(bar_fig, 340),
                use_container_width=True,
            )

            forecast_table = fc[
                [
                    column
                    for column in [
                        "ward_id",
                        "forecast_origin",
                        "target_date",
                        "predicted_cases",
                        "risk_level",
                    ]
                    if column in fc.columns
                ]
            ].rename(
                columns={
                    "ward_id": "Ward",
                    "forecast_origin": "Forecast Origin",
                    "target_date": "Target Date",
                    "predicted_cases": "Predicted Cases",
                    "risk_level": "Risk Level",
                }
            )

            st.dataframe(
                forecast_table,
                use_container_width=True,
                hide_index=True,
                column_config={
                    "Predicted Cases": st.column_config.NumberColumn(
                        format="%.2f"
                    )
                },
            )

            st.caption(
                "Experimental forecasts based on available historical weather "
                "features and ward-level characteristics. Not clinically validated."
            )


# ============================================================
# TAB 3: 3D RISK MAP
# ============================================================

with tab_map:
    if render_ward_3d_map is None:
        st.info(
            "3D map module (map3d.py) was not found. "
            "Place map3d.py next to app.py to enable this tab."
        )
    else:
        render_ward_3d_map(
            backtest_df,
            df,
            city,
        )


# ============================================================
# TAB 4: HISTORICAL MODEL BACKTESTING
# ============================================================

with tab_backtest:
    render_section_title(
        "Historical Model Backtesting",
        "Evaluation of model predictions on historical test data.",
    )

    if backtest_df.empty:
        st.warning("Historical backtesting data is unavailable.")
    else:
        bt_start = backtest_df["target_date"].min()
        bt_end = backtest_df["target_date"].max()

        st.info(
            f"These are historical test predictions "
            f"({bt_start:%b %Y} to {bt_end:%b %Y}), "
            "not current outbreak forecasts."
        )

        selected_backtest = backtest_df[
            backtest_df["city"] == city
        ].copy()

        if selected_ward != "All Wards":
            selected_backtest = selected_backtest[
                selected_backtest["ward_id"] == selected_ward
            ]

        if selected_backtest.empty:
            st.info(
                "No historical backtesting records for this location."
            )
        else:
            bt = selected_backtest.copy()

            origin_lookup = (
                backtest_df[
                    ["ward_id", "target_date", "actual_cases"]
                ]
                .drop_duplicates(["ward_id", "target_date"])
                .rename(
                    columns={
                        "target_date": "forecast_origin",
                        "actual_cases": "origin_actual",
                    }
                )
            )

            bt = bt.merge(
                origin_lookup,
                on=["ward_id", "forecast_origin"],
                how="left",
            )

            bt["model_err"] = (
                bt["actual_cases"] - bt["predicted_cases"]
            ).abs()
            bt["base_err"] = (
                bt["actual_cases"] - bt["origin_actual"]
            ).abs()

            valid = bt.dropna(subset=["origin_actual"])

            st.markdown("### Model Accuracy")

            if not valid.empty:
                mae = (
                    valid.groupby("weeks_ahead")
                    .agg(
                        model_mae=("model_err", "mean"),
                        base_mae=("base_err", "mean"),
                    )
                    .reset_index()
                )

                mae_cols = st.columns(len(mae))

                for mae_col, row in zip(mae_cols, mae.itertuples()):
                    gain = (
                        (1 - row.model_mae / row.base_mae) * 100
                        if row.base_mae
                        else 0
                    )
                    mae_col.metric(
                        f"{int(row.weeks_ahead)}-Week MAE",
                        f"{row.model_mae:.2f} cases",
                        f"{gain:+.0f}% vs naive baseline",
                    )

                st.caption(
                    "MAE = mean absolute error per ward-week. Naive baseline = "
                    "assume the same cases as the last observed week at the "
                    "forecast origin."
                )
            else:
                mae = (
                    bt.groupby("weeks_ahead")["model_err"]
                    .mean()
                    .reset_index()
                )

                if not mae.empty:
                    mae_cols = st.columns(len(mae))
                    for mae_col, row in zip(mae_cols, mae.itertuples()):
                        mae_col.metric(
                            f"{int(row.weeks_ahead)}-Week MAE",
                            f"{row.model_err:.2f} cases",
                        )

            peak_rows = bt[bt["actual_cases"] >= 10]
            if not peak_rows.empty:
                bias = (
                    peak_rows["predicted_cases"]
                    - peak_rows["actual_cases"]
                ).mean()
                st.caption(
                    "Limitation: in high-incidence weeks (10 or more actual "
                    f"cases) predictions differ from actual cases by {bias:+.1f} "
                    "cases on average (negative = under-prediction)."
                )

            st.divider()

            # ACTUAL VS PREDICTED
            st.markdown("### Actual vs Predicted Cases")

            avp_horizons = sorted(
                bt["weeks_ahead"].dropna().unique().tolist()
            )

            avp_horizon = st.selectbox(
                "Select Horizon",
                avp_horizons,
                format_func=lambda x: f"{int(x)}-Week Prediction",
                key="avp_horizon",
            )

            hb = bt[bt["weeks_ahead"] == avp_horizon]
            line_df = (
                hb.groupby("target_date")[
                    ["actual_cases", "predicted_cases"]
                ]
                .sum()
                .reset_index()
            )

            avp_fig = go.Figure()
            avp_fig.add_scatter(
                x=line_df["target_date"],
                y=line_df["actual_cases"],
                name="Actual",
                line=dict(color="#C9D6D2", width=2),
            )
            avp_fig.add_scatter(
                x=line_df["target_date"],
                y=line_df["predicted_cases"],
                name="Predicted",
                line=dict(color="#20A878", width=3),
                fill="tozeroy",
                fillcolor="rgba(32,168,120,0.12)",
            )

            st.plotly_chart(
                style_fig(avp_fig, 380),
                use_container_width=True,
            )

            # WARD x WEEK HEATMAP
            if selected_ward == "All Wards":
                st.markdown("### Ward x Week Predicted Cases")

                pivot = hb.pivot_table(
                    index="ward_id",
                    columns="target_date",
                    values="predicted_cases",
                )
                pivot.columns = pivot.columns.strftime("%Y-%m-%d")

                heat_fig = px.imshow(
                    pivot,
                    aspect="auto",
                    color_continuous_scale=[
                        "#10201c",
                        "#E7B84B",
                        "#EF5361",
                    ],
                    labels=dict(color="Predicted cases"),
                )

                st.plotly_chart(
                    style_fig(heat_fig, 420),
                    use_container_width=True,
                )

            st.divider()

            # RISK DISTRIBUTION
            risk_counts = (
                selected_backtest["risk_level"]
                .value_counts()
                .reindex(RISK_LEVELS, fill_value=0)
                .reset_index()
            )
            risk_counts.columns = ["Risk Level", "Predictions"]

            rcol1, rcol2 = st.columns([1.2, 1])

            with rcol1:
                st.markdown("### Historical Risk Distribution")

                risk_fig = px.bar(
                    risk_counts,
                    x="Risk Level",
                    y="Predictions",
                    color="Risk Level",
                    category_orders={"Risk Level": RISK_LEVELS},
                    color_discrete_map=RISK_COLORS,
                )
                risk_fig.update_layout(showlegend=False)

                st.plotly_chart(
                    style_fig(risk_fig, 330),
                    use_container_width=True,
                )

            with rcol2:
                st.markdown("### Risk Summary")

                for risk in RISK_LEVELS:
                    count = int(
                        risk_counts.loc[
                            risk_counts["Risk Level"] == risk,
                            "Predictions",
                        ].iloc[0]
                    )
                    st.metric(f"{risk} Risk Predictions", f"{count:,}")

            st.divider()

            # HISTORICAL WARD PREDICTIONS
            st.markdown("### Historical Ward Predictions")

            horizon = st.selectbox(
                "Select Backtesting Horizon",
                avp_horizons,
                format_func=lambda x: f"{int(x)}-Week Prediction",
                key="backtest_horizon",
            )

            horizon_df = (
                selected_backtest[
                    selected_backtest["weeks_ahead"] == horizon
                ]
                .sort_values("predicted_cases", ascending=False)
                .copy()
            )

            display_columns = [
                "ward_id",
                "forecast_origin",
                "target_date",
                "actual_cases",
                "predicted_cases",
                "risk_level",
            ]
            display_df = horizon_df[display_columns].copy()
            display_df.columns = [
                "Ward",
                "Forecast Origin",
                "Target Date",
                "Actual Cases",
                "Predicted Cases",
                "Risk Level",
            ]

            st.dataframe(
                display_df,
                use_container_width=True,
                hide_index=True,
                column_config={
                    "Actual Cases": st.column_config.NumberColumn(
                        format="%d"
                    ),
                    "Predicted Cases": st.column_config.NumberColumn(
                        format="%.2f"
                    ),
                    "Forecast Origin": st.column_config.DateColumn(
                        format="DD MMM YYYY"
                    ),
                    "Target Date": st.column_config.DateColumn(
                        format="DD MMM YYYY"
                    ),
                },
            )

            st.caption(
                "Historical predictions use the model's existing risk "
                "classification thresholds."
            )


# ============================================================
# TAB 5: PUBLIC HEALTH ACTION RECOMMENDATIONS
# ============================================================

with tab_action:
    render_section_title(
        "Public Health Action Plan",
        "Suggested actions based on current model forecast risk.",
    )

    if not ward_forecasts.empty:
        action_horizons = sorted(
            ward_forecasts["weeks_ahead"].dropna().unique().tolist()
        )

        if action_horizons:
            selected_horizon = st.selectbox(
                "Select Forecast Window",
                action_horizons,
                format_func=lambda x: f"{int(x)}-Week Forecast",
                key="action_horizon",
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
                        st.markdown(f"### {ward}")
                        st.write(f"Predicted Risk: **{risk}**")

                        if plan:
                            st.write(f"Priority: **{plan['priority']}**")
                            st.write(
                                f"Responsible Team: **{plan['team']}**"
                            )
                            st.write(
                                f"Suggested Timeframe: **{plan['timeframe']}**"
                            )
                            st.markdown("#### Recommended Actions")

                            for action in plan["actions"]:
                                st.markdown(f"- {action}")
                        else:
                            st.info(
                                "No recommendation available for this risk level."
                            )
            else:
                st.info("No forecasts available for this selection.")
        else:
            st.info("No valid forecast horizon is available.")
    else:
        st.info("No forecast available for action recommendations.")

    st.caption(
        "These are suggested operational actions, not clinically validated "
        "treatment instructions. Actual deployment decisions require public "
        "health authority assessment."
    )


# ============================================================
# TAB 6: WARD INTELLIGENCE RANKING
# ============================================================

with tab_ranking:
    render_section_title(
        "Ward Intelligence Ranking",
        "Ranking by historical dengue case count in the selected period, "
        "not by predicted outbreak risk.",
    )

    ranking_df = get_ward_ranking(city_period_df)
    ranking_df = ranking_df.rename(
        columns={
            "city": "City",
            "ward_id": "Ward",
            "historical_cases": "Historical Cases",
            "avg_rainfall": "Avg Rainfall (mm)",
            "waterlogging": "Waterlogging Index",
            "population_density": "Population Density",
            "sanitation": "Sanitation Score",
        }
    )

    st.dataframe(
        ranking_df.style.highlight_max(
            subset=["Historical Cases"],
            color="#D9485525",
        ),
        use_container_width=True,
        hide_index=True,
        column_config={
            "Historical Cases": st.column_config.NumberColumn(
                format="%d"
            ),
            "Avg Rainfall (mm)": st.column_config.NumberColumn(
                format="%.2f"
            ),
        },
    )


# ============================================================
# FOOTER
# ============================================================

render_footer()
