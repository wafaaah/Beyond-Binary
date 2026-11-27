"""English / Bangla toggle for the front page. Works offline: a fixed dictionary."""
import re

import streamlit as st

from i18n_pages import PATTERNS, PHRASES

LANGUAGES = {"en": "English", "bn": "বাংলা"}

BN = {
    # sidebar
    "Layers": "ফিল্টার", "DENGUE SURVEILLANCE CONTROLS": "ডেঙ্গু নজরদারি নিয়ন্ত্রণ",
    "Location": "এলাকা", "Select City": "শহর বাছাই করুন",
    "Administrative Level / Ward": "প্রশাসনিক স্তর / ওয়ার্ড", "All Wards": "সব ওয়ার্ড",
    "Historical Period": "পুরোনো তথ্যের সময়কাল", "Select Period": "সময় বাছাই করুন",
    "All Available Data": "সব তথ্য", "Last 12 Months": "শেষ ১২ মাস",
    "Last 6 Months": "শেষ ৬ মাস", "Last 3 Months": "শেষ ৩ মাস",
    "Custom Range": "নিজে তারিখ দিন", "Choose date range": "তারিখ বাছাই করুন",
    "Source: Provided Bangladesh dengue dataset": "উৎস: প্রদত্ত বাংলাদেশ ডেঙ্গু ডেটাসেট",
    "Historical observations only.": "শুধু অতীতের পর্যবেক্ষণ।",
    "Chattogram": "চট্টগ্রাম", "Dhaka North": "ঢাকা উত্তর", "Dhaka South": "ঢাকা দক্ষিণ",
    "Gazipur": "গাজীপুর", "Narayanganj": "নারায়ণগঞ্জ",
    # header and overview
    "WARD RISK INTELLIGENCE SYSTEM | BANGLADESH": "ওয়ার্ড ঝুঁকি বিশ্লেষণ ব্যবস্থা | বাংলাদেশ",
    "Historical dengue data is used for surveillance analysis. "
    "ML forecasts are experimental early-warning estimates and "
    "should not be treated as confirmed outbreak predictions.":
        "নজরদারি বিশ্লেষণে অতীতের ডেঙ্গু তথ্য ব্যবহার করা হয়েছে। মেশিন লার্নিং পূর্বাভাস "
        "পরীক্ষামূলক আগাম অনুমান; এটি নিশ্চিত প্রাদুর্ভাবের ঘোষণা নয়।",
    "Surveillance Overview": "নজরদারি সারসংক্ষেপ",
    "Historical Dengue Cases": "অতীতের ডেঙ্গু রোগী",
    "Wards Represented": "ওয়ার্ড সংখ্যা", "Average Rainfall": "গড় বৃষ্টিপাত",
    "Average Temperature": "গড় তাপমাত্রা", "Average Humidity": "গড় আর্দ্রতা",
    "Historical Records": "মোট রেকর্ড",
    # season
    "Seasonal Dengue Intelligence": "মৌসুমি ডেঙ্গু বিশ্লেষণ",
    "HISTORICAL PEAK SEASON": "অতীতের সর্বোচ্চ মৌসুম",
    "FORECAST SEASON CONTEXT": "পূর্বাভাসের মৌসুম",
    "Peak months calculated from unique actual observations in the historical test dataset.":
        "ঐতিহাসিক পরীক্ষার ডেটার প্রকৃত পর্যবেক্ষণ থেকে সর্বোচ্চ মাসগুলো হিসাব করা।",
    "Unavailable": "পাওয়া যায়নি", "Peak-season window": "সর্বোচ্চ মৌসুমের মধ্যে",
    "Includes peak months": "কিছু সর্বোচ্চ মাস আছে",
    "Outside historical peak months": "সর্বোচ্চ মৌসুমের বাইরে",
    "Peak-month ranking is based on aggregated actual cases for the selected city/ward "
    "in the historical test period.":
        "বাছাই করা শহর বা ওয়ার্ডের প্রকৃত রোগীর যোগফল থেকে সর্বোচ্চ মাস ঠিক করা হয়েছে।",
    "Historical seasonality is calculated from actual test observations. "
    "Forecasts are experimental model estimates, not confirmed cases.":
        "মৌসুমের হিসাব প্রকৃত তথ্য থেকে। পূর্বাভাস মডেলের পরীক্ষামূলক অনুমান, নিশ্চিত রোগী নয়।",
    # forecast and tabs
    "Dengue Forecast Outlook": "ডেঙ্গু পূর্বাভাস", "Overview": "সারসংক্ষেপ",
    "Forecast": "পূর্বাভাস", "3D Risk Map": "৩ডি ঝুঁকি মানচিত্র", "Backtesting": "মডেল যাচাই",
    "Action Plan": "করণীয়", "Ward Ranking": "ওয়ার্ড র‍্যাংকিং", "Cases": "রোগী",
    "Weather": "আবহাওয়া", "Ward Indicators": "ওয়ার্ডের সূচক",
    "Monthly aggregation of available weekly observations.": "সাপ্তাহিক তথ্যের মাসিক যোগফল।",
    "Weather Analysis": "আবহাওয়া বিশ্লেষণ",
    "Historical rainfall, temperature and humidity.": "অতীতের বৃষ্টিপাত, তাপমাত্রা ও আর্দ্রতা।",
    "Environmental Vulnerability": "পরিবেশগত ঝুঁকি",
    "Actual ward-level characteristics from the dataset.": "ডেটাসেট থেকে ওয়ার্ডের প্রকৃত বৈশিষ্ট্য।",
    "Selected Location": "বাছাই করা এলাকা", "Historical Weather Summary": "অতীতের আবহাওয়া",
    "Ward-Level Forecast": "ওয়ার্ডভিত্তিক পূর্বাভাস",
    "Predicted weekly dengue cases and risk level for each ward.":
        "প্রতিটি ওয়ার্ডের সাপ্তাহিক সম্ভাব্য রোগী ও ঝুঁকির মাত্রা।",
    "Forecast Window": "পূর্বাভাসের সময়",
    "Historical Model Backtesting": "অতীত তথ্যে মডেল যাচাই",
    "Evaluation of model predictions on historical test data.":
        "অতীতের পরীক্ষার ডেটায় মডেলের পূর্বাভাস মূল্যায়ন।",
    "Public Health Action Plan": "জনস্বাস্থ্য করণীয়",
    "Suggested actions based on current model forecast risk.":
        "পূর্বাভাসের ঝুঁকি অনুযায়ী প্রস্তাবিত পদক্ষেপ।",
    "Ward Intelligence Ranking": "ওয়ার্ড র‍্যাংকিং",
    "Experimental model estimates, not clinically validated.":
        "পরীক্ষামূলক মডেল অনুমান, চিকিৎসাগতভাবে যাচাই করা নয়।",
    "Low": "কম", "Medium": "মাঝারি", "High": "বেশি", "Critical": "অতি ঝুঁকিপূর্ণ",
}


def is_bangla():
    return st.session_state.get("lang") == "bn"


def t(text):
    """Bangla text when selected, otherwise the English original."""
    return BN.get(text, text) if is_bangla() else text


ALL = {**PHRASES, **BN}
PHRASE_RE = re.compile(
    "(?<![A-Za-z_])(" + "|".join(map(re.escape, sorted(PHRASES, key=len, reverse=True)))
    + ")(?![A-Za-z_])"
)
# styles, message previews and tags are never translated
SKIP_RE = re.compile(r"(<style.*?</style>|<div class='dw-bubble'>.*?</div>|<[^>]*>)", re.S)

FONT_CSS = """<style>
.stApp, .stApp p, .stApp li, .stApp label, .stApp div, .stApp span:not([data-testid="stIconMaterial"]),
.stApp button, .stApp input, .stApp h1, .stApp h2, .stApp h3, .stApp h4, .stApp td, .stApp th,
.stApp b, .stApp small{font-family:'Noto Sans Bengali','Hind Siliguri','Nirmala UI','Vrinda',sans-serif!important;
letter-spacing:normal!important}
.stApp [data-testid="stIconMaterial"]{font-family:'Material Symbols Rounded'!important}
.stApp p,.stApp li,.stApp label,.stApp div[class^="dw-"],.cx span,.cx b{line-height:1.6}
.stApp h1,.stApp h2,.stApp h3,.dw-hero-title{line-height:1.45!important}
</style>"""


def _part(text):
    if text in ALL:
        return ALL[text]
    for pattern, replacement in PATTERNS:
        text = re.sub(pattern, replacement, text)
    return PHRASE_RE.sub(lambda match: PHRASES[match.group(1)], text)


def tr(value):
    """Translate the visible text of a label or an HTML block."""
    if not is_bangla() or not isinstance(value, str):
        return value
    pieces = SKIP_RE.split(value)
    # odd positions are the skipped tags and blocks
    return "".join(p if i % 2 else _part(p) for i, p in enumerate(pieces))


TEXT_CALLS = ("markdown", "caption", "title", "header", "subheader", "info", "warning",
              "error", "success", "write", "metric", "button", "download_button",
              "checkbox", "slider", "number_input", "multiselect", "expander")
CHOICE_CALLS = ("radio", "selectbox")


def _wrap(original, name, has_self):
    def wrapper(*args, **kwargs):
        args = list(args)
        first = 1 if has_self else 0
        if name == "tabs" and len(args) > first:
            args[first] = [tr(label) for label in args[first]]
        elif len(args) > first:
            args[first] = tr(args[first])
        if "label" in kwargs:
            kwargs["label"] = tr(kwargs["label"])
        if name in CHOICE_CALLS and is_bangla():
            shown = kwargs.get("format_func", str)
            kwargs["format_func"] = lambda option: tr(str(shown(option)))
        return original(*args, **kwargs)

    return wrapper


def _install():
    """Wrap Streamlit text calls once. Each call checks the viewer's language."""
    if getattr(st, "_dw_translated", False) is True:
        return
    from streamlit.delta_generator import DeltaGenerator

    for name in TEXT_CALLS + CHOICE_CALLS + ("tabs",):
        setattr(DeltaGenerator, name, _wrap(getattr(DeltaGenerator, name), name, True))
        setattr(st, name, _wrap(getattr(st, name), name, False))
    st._dw_translated = True


def _name_home_page():
    """Show "Dashboard" in the sidebar for the main file, which is named app.py."""
    label = "ড্যাশবোর্ড" if is_bangla() else "Dashboard"
    st.markdown(
        "<style>[data-testid='stSidebarNav'] li:first-child a span{font-size:0!important}"
        "[data-testid='stSidebarNav'] li:first-child a span::after{"
        f"content:'{label}';font-size:.9rem}}</style>",
        unsafe_allow_html=True,
    )


def _changed():
    st.session_state["lang"] = st.session_state["lang_widget"]


def enable(in_sidebar=True, bangla_page=False):
    """Show the language toggle and translate everything drawn after it."""
    _install()
    st.session_state["lang_widget"] = st.session_state.setdefault("lang", "en")
    area = st.sidebar if in_sidebar else st
    area.radio("ভাষা / Language", list(LANGUAGES), key="lang_widget",
               format_func=LANGUAGES.get, horizontal=True, on_change=_changed)
    _name_home_page()
    if is_bangla() or bangla_page:
        st.markdown(FONT_CSS, unsafe_allow_html=True)
