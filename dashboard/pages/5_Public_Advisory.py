import sys
from pathlib import Path

import streamlit as st

DASHBOARD = Path(__file__).resolve().parents[1]
if str(DASHBOARD) not in sys.path:
    sys.path.insert(0, str(DASHBOARD))

from copilot_engine import QUESTIONS, answer  # noqa: E402
from public_ui import poster_html, risk_card_html  # noqa: E402
from shared import (  # noqa: E402
    RISK_COLORS, apply_style, cached_forecast, default_week,
)

st.set_page_config(page_title="জনসাধারণের পরামর্শ", layout="wide")
apply_style()

RISK_BN = {
    "Low": ("কম ঝুঁকি", "সতর্ক থাকুন এবং ঘরের আশেপাশে পানি জমতে দেবেন না।"),
    "Medium": ("মাঝারি ঝুঁকি", "আজই বাড়ির চারপাশ দেখুন এবং জমা পানি ফেলে দিন।"),
    "High": ("বেশি ঝুঁকি", "মশার কামড় থেকে বাঁচুন। জ্বর হলে দ্রুত ডাক্তার দেখান।"),
    "Critical": (
        "খুব বেশি ঝুঁকি",
        "এখনই সাবধান হোন। জ্বর হলে দেরি না করে ডাক্তার দেখান ও পরীক্ষা করান।",
    ),
}
CITY_BN = {
    "Chattogram": "চট্টগ্রাম",
    "Dhaka North": "ঢাকা উত্তর",
    "Dhaka South": "ঢাকা দক্ষিণ",
    "Gazipur": "গাজীপুর",
    "Narayanganj": "নারায়ণগঞ্জ",
}
BN_DIGITS = str.maketrans("0123456789", "০১২৩৪৫৬৭৮৯")
MONTHS = [
    "জানুয়ারি", "ফেব্রুয়ারি", "মার্চ", "এপ্রিল", "মে", "জুন", "জুলাই",
    "আগস্ট", "সেপ্টেম্বর", "অক্টোবর", "নভেম্বর", "ডিসেম্বর",
]


def bn_date(date):
    text = f"{date.day} {MONTHS[date.month - 1]} {date.year}"
    return text.translate(BN_DIGITS)


st.title("আপনার ওয়ার্ডে ডেঙ্গুর ঝুঁকি")

week = st.session_state.get("week", default_week())
data = cached_forecast(week, 2)
target = data["target_date"].iloc[0]
st.warning(
    f"ডেমো: এটি পুরোনো তথ্যের ভিত্তিতে {bn_date(target)} সপ্তাহের পূর্বাভাস। "
    "এটি আজকের সতর্কবার্তা নয়।"
)

city = st.selectbox(
    "শহর", sorted(data["city"].unique()),
    format_func=lambda c: CITY_BN.get(c, c),
)
wards = data[data["city"] == city]
ward = st.selectbox(
    "ওয়ার্ড নম্বর", sorted(wards["ward_id"]),
    format_func=lambda w: w.rsplit("_", 1)[-1].translate(BN_DIGITS),
)
risk = wards.loc[wards["ward_id"] == ward, "risk_level"].iloc[0]
label, advice = RISK_BN[risk]
color = RISK_COLORS[risk]

st.markdown(risk_card_html(risk, label, advice, color), unsafe_allow_html=True)



def show_copilot(forecasts):
    st.caption("প্রশ্নে ক্লিক করুন অথবা নিজের এলাকা বা প্রশ্ন লিখে খুঁজুন (বাংলা, English বা Banglish)")
    question = None
    with st.form("copilot_search"):
        text = st.text_input(
            "খুঁজুন", placeholder="যেমন: ঢাকা উত্তর ৩, Gazipur 2, ডেঙ্গুর লক্ষণ",
        )
        if st.form_submit_button("উত্তর দেখুন", use_container_width=True):
            question = text.strip() or None

    answer_box = st.container()
    st.markdown("**সাধারণ প্রশ্ন** (বিষয় খুলে ক্লিক করুন)")
    for number, (group, items) in enumerate(QUESTIONS.items()):
        with st.expander(group, expanded=number == 0):
            columns = st.columns(2)
            for i, (intent, prompt) in enumerate(items.items()):
                if columns[i % 2].button(prompt, key=f"q_{intent}", use_container_width=True):
                    question = prompt

    if question:
        st.session_state["copilot_last"] = question
    last = st.session_state.get("copilot_last")
    if last:
        reply, table = answer(last, forecasts)
        # shown right below the search box, so no scrolling is needed
        with answer_box:
            with st.chat_message("user"):
                st.write(last)
            with st.chat_message("assistant"):
                st.markdown(reply)
                if table is not None:
                    st.dataframe(table, hide_index=True, use_container_width=True)


st.markdown(
    "<style>.stButton>button{border-radius:14px;min-height:52px;"
    "border:1px solid rgba(53,194,176,.55);"
    "background:linear-gradient(120deg,rgba(15,124,134,.22),rgba(53,194,176,.08))}"
    ".stButton>button:hover{border-color:#35C2B0}</style>",
    unsafe_allow_html=True,
)
st.write("")
poster_tab, copilot_tab = st.tabs(["সচেতনতা পোস্টার", "Copilot: প্রশ্ন করুন"])
with poster_tab:
    st.markdown(poster_html(), unsafe_allow_html=True)
with copilot_tab:
    show_copilot(data)
st.caption("সাধারণ তথ্য, চিকিৎসকের পরামর্শের বিকল্প নয়। সূত্র: WHO ও CDC-এর ডেঙ্গু নির্দেশনা।")
