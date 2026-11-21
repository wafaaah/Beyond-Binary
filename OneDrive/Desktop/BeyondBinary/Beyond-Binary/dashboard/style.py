import streamlit as st


def load_css():

    return """
    <style>

    /* MAIN DASHBOARD BACKGROUND */
    .stApp {
        background:
            radial-gradient(
                circle at 10% 10%,
                rgba(190, 145, 205, 0.10),
                transparent 35%
            ),
            radial-gradient(
                circle at 90% 80%,
                rgba(130, 110, 165, 0.12),
                transparent 35%
            ),
            var(--background-color);

        color: var(--text-color);
    }


    /* --------------------------------
       MAIN DASHBOARD BACKGROUND
    -------------------------------- */

    .stApp {
        background:
            radial-gradient(
                circle at 10% 10%,
                var(--glow-one),
                transparent 35%
            ),
            radial-gradient(
                circle at 90% 80%,
                var(--glow-two),
                transparent 35%
            ),
            var(--background-color);

        color: var(--text-color);
    }


    /* --------------------------------
       MAIN CONTENT AREA
    -------------------------------- */

    [data-testid="stAppViewContainer"] {
        background: transparent;
    }

    [data-testid="stMain"] {
        background: transparent;
    }


    /* --------------------------------
       SIDEBAR GLASSMORPHISM
    -------------------------------- */

    [data-testid="stSidebar"] {
        background: var(--glass-bg);
        backdrop-filter: blur(18px);
        border-right: 1px solid var(--glass-border);
    }

    [data-testid="stSidebar"] > div:first-child {
        background: transparent;
    }


    /* --------------------------------
       METRIC CARDS
    -------------------------------- */

    [data-testid="stMetric"] {
        background: var(--glass-bg);
        border: 1px solid var(--glass-border);
        border-radius: 16px;
        padding: 18px;
        backdrop-filter: blur(18px);
        box-shadow: 0 8px 24px rgba(0, 0, 0, 0.05);
    }

    [data-testid="stMetricValue"],
    [data-testid="stMetricLabel"] {
        color: var(--text-color);
    }


    /* --------------------------------
       TABS
    -------------------------------- */

    .stTabs [data-baseweb="tab-list"] {
        gap: 12px;
        background: transparent;
    }

    .stTabs [data-baseweb="tab"] {
        color: var(--text-color);
        border-radius: 10px;
    }

    .stTabs [aria-selected="true"] {
        border-bottom-color: var(--primary-color);
        color: var(--primary-color);
    }


    /* --------------------------------
       GLASS PANELS
    -------------------------------- */

    div[data-testid="stVerticalBlockBorderWrapper"] {
        background: var(--glass-bg);
        border: 1px solid var(--glass-border);
        border-radius: 16px;
        backdrop-filter: blur(18px);
    }


    /* --------------------------------
       INPUTS AND SELECT BOXES
    -------------------------------- */

    [data-baseweb="select"] > div {
        background: var(--glass-bg);
        border-color: var(--glass-border);
        border-radius: 10px;
    }

    [data-testid="stDateInput"] input {
        background: var(--glass-bg);
        color: var(--text-color);
        border-color: var(--glass-border);
    }


    /* --------------------------------
       BUTTONS
    -------------------------------- */

    .stButton > button {
        border-radius: 10px;
        border: 1px solid var(--glass-border);
        background: var(--glass-bg);
        color: var(--text-color);
        transition: all 0.2s ease;
    }

    .stButton > button:hover {
        border-color: var(--primary-color);
        color: var(--primary-color);
    }


    /* --------------------------------
       DIVIDERS
    -------------------------------- */

    hr {
        border-color: var(--border-color);
    }


    /* --------------------------------
       HEADINGS AND TEXT
    -------------------------------- */

    h1, h2, h3, h4, h5, h6 {
        color: var(--text-color);
    }

    p, label, span {
        color: inherit;
    }

    [data-testid="stCaptionContainer"] {
        color: var(--muted-color);
    }


    /* --------------------------------
       DASHBOARD SUBTITLE
    -------------------------------- */

    .dashboard-subtitle {
        color: var(--muted-color);
        font-size: 12px;
        font-weight: 600;
        letter-spacing: 2px;
        margin-top: -10px;
        margin-bottom: 20px;
    }


    /* --------------------------------
       DATAFRAME
    -------------------------------- */

    [data-testid="stDataFrame"] {
        border: 1px solid var(--glass-border);
        border-radius: 12px;
        overflow: hidden;
    }


    /* --------------------------------
       ALERTS AND NOTIFICATIONS
    -------------------------------- */

    [data-testid="stAlert"] {
        border-radius: 12px;
        backdrop-filter: blur(12px);
    }


    /* --------------------------------
       RESPONSIVE DESIGN
    -------------------------------- */

    @media (max-width: 768px) {

        [data-testid="stMetric"] {
            padding: 12px;
            border-radius: 12px;
        }

        .dashboard-subtitle {
            font-size: 10px;
            letter-spacing: 1px;
        }

    }


    /* Clear readable text */
    h1, h2, h3, h4, h5, h6 {
        color: var(--text-color) !important;
    }

    .stMarkdown p,
    .stMarkdown li,
    [data-testid="stMetricLabel"] {
        color: var(--text-color);
    }

    [data-testid="stMetricValue"] {
        color: var(--text-color);
    }

    [data-testid="stCaptionContainer"] {
        color: var(--muted-color);
    }

    /* Card surfaces */
    [data-testid="stMetric"] {
        background: var(--glass-bg);
        border: 1px solid var(--glass-border);
        border-radius: 16px;
        padding: 18px;
    }

    /* Sidebar */
    [data-testid="stSidebar"] {
        background: var(--glass-bg);
        border-right: 1px solid var(--glass-border);
    }

    /* Buttons */
    .stButton > button {
        color: var(--text-color);
        border-color: var(--glass-border);
    }


    </style>
    """
