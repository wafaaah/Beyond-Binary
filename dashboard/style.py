
def load_css():
    return """
    <style>

    .stApp {
        background-color: #0B1120;
        color: #E8EDF5;
    }

    [data-testid="stSidebar"] {
        background-color: #111A2C;
    }

    [data-testid="stSidebar"] * {
        color: #E8EDF5;
    }

    .block-container {
        padding-top: 1.8rem;
        padding-bottom: 2rem;
        max-width: 1450px;
    }

    h1, h2, h3 {
        color: #F3F6FC !important;
    }

    p, label {
        color: #A9B7CB;
    }

    div[data-testid="stMetric"] {
        background-color: #141F33;
        border: 1px solid #25334B;
        padding: 18px;
        border-radius: 14px;
    }

    div[data-testid="stMetricLabel"] {
        color: #9FB0C8;
    }

    div[data-testid="stMetricValue"] {
        color: #F3F6FC;
    }

    div[data-testid="stMetricDelta"] {
        font-size: 14px;
    }

    div[data-testid="stPlotlyChart"] {
        background-color: #141F33;
        border-radius: 14px;
        padding: 8px;
    }

    div[data-testid="stDataFrame"] {
        border: 1px solid #25334B;
        border-radius: 12px;
    }

    .risk-box {
        padding: 20px;
        border-radius: 14px;
        margin-bottom: 10px;
    }

    .risk-low {
        background-color: #12352A;
        border: 1px solid #26754B;
    }

    .risk-medium {
        background-color: #3A3216;
        border: 1px solid #A38327;
    }

    .risk-high {
        background-color: #422718;
        border: 1px solid #C16A26;
    }

    .risk-critical {
        background-color: #421F29;
        border: 1px solid #B64252;
    }

    .small-note {
        color: #8FA2BC;
        font-size: 13px;
    }

    .demo-banner {
        background-color: #332A16;
        border: 1px solid #8B7029;
        padding: 12px 16px;
        border-radius: 10px;
        color: #F5D78A;
        margin-bottom: 18px;
    }
    /* Selectbox dark theme fix */
    [data-testid="stSelectbox"] [data-baseweb="select"] {
        background-color: #1B2940 !important;
    }

    [data-testid="stSelectbox"] [role="combobox"] {
        background-color: #1B2940 !important;
        color: #FFFFFF !important;
        border: 1px solid #40536F !important;
        border-radius: 8px !important;
    }

    [data-testid="stSelectbox"] [role="combobox"] * {
        color: #FFFFFF !important;
        background-color: transparent !important;
    }

    [data-testid="stSelectbox"] svg {
        fill: #FFFFFF !important;
        color: #FFFFFF !important;
    }

    /* Dropdown menu options */
    div[data-baseweb="popover"] ul {
        background-color: #162238 !important;
    }

    div[data-baseweb="popover"] li {
        color: #FFFFFF !important;
        background-color: #162238 !important;
    }

    div[data-baseweb="popover"] li:hover {
        background-color: #344B6B !important;
    }
    /* Dropdown arrow - white */
    div[data-testid="stSelectbox"] div[data-baseweb="select"] svg {
        color: #FFFFFF !important;
        fill: #FFFFFF !important;
    }

    </style>
    """
