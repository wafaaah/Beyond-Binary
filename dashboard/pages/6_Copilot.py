import sys
from pathlib import Path

import streamlit as st

DASHBOARD = Path(__file__).resolve().parents[1]
if str(DASHBOARD) not in sys.path:
    sys.path.insert(0, str(DASHBOARD))

from shared import apply_style, cached_data, scenario_controls  # noqa: E402
from copilot_engine import QUESTIONS, answer  # noqa: E402

st.set_page_config(page_title="DengueWatch Copilot", layout="wide")
apply_style()
week, horizon, stock, crews = scenario_controls()

st.markdown(
    "<style>.stButton>button{border-radius:14px;min-height:56px;"
    "border:1px solid rgba(53,194,176,.55);"
    "background:linear-gradient(120deg,rgba(15,124,134,.22),rgba(53,194,176,.08))}"
    ".stButton>button:hover{border-color:#35C2B0;transform:translateY(-2px)}</style>"
    "<div style='border-radius:22px;padding:26px 30px;color:#fff;margin-bottom:14px;"
    "background:linear-gradient(120deg,#06303A,#0F7C86 60%,#8E1F3C)'>"
    "<div style='font-size:32px;font-weight:800'>DengueWatch Copilot</div>"
    "<div style='font-size:17px'>প্রশ্নে ক্লিক করুন অথবা নিচের বক্সে নিজের প্রশ্ন লিখুন "
    "(বাংলা, English বা Banglish)</div></div>",
    unsafe_allow_html=True,
)

history = st.session_state.setdefault("chat", [])
question = None

LIVE = "লাইভ তথ্য"


def question_buttons(items):
    clicked = None
    columns = st.columns(2)
    for i, (intent, label) in enumerate(items.items()):
        if columns[i % 2].button(label, key=f"q_{intent}", use_container_width=True):
            clicked = label
    return clicked


for tab, (group, items) in zip(st.tabs(list(QUESTIONS)), QUESTIONS.items()):
    with tab:
        if group == LIVE:
            with st.form("area_search"):
                text = st.text_input(
                    "আপনার এলাকা বা প্রশ্ন লিখে খুঁজুন",
                    placeholder="যেমন: ঢাকা উত্তর ৩, Gazipur 2, Chattogram",
                )
                if st.form_submit_button("খুঁজুন", use_container_width=True):
                    question = text.strip() or question
            st.caption("শহর: চট্টগ্রাম, ঢাকা উত্তর, ঢাকা দক্ষিণ, গাজীপুর, নারায়ণগঞ্জ। "
                       "তথ্য পুরোনো ডেটার ডেমো পূর্বাভাস, আজকের নয়।")
        else:
            question = question_buttons(items) or question

typed = st.chat_input("আপনার প্রশ্ন লিখুন... যেমন: ঢাকা উত্তর ওয়ার্ড ৩")
question = typed or question

if question:
    try:
        reply, table = answer(question, cached_data(), week, horizon, stock, crews)
    except Exception as error:
        reply, table = f"উত্তর তৈরি করা যায়নি: {error}", None
    history.append((question, reply, table))

if history:
    if st.button("চ্যাট মুছুন"):
        history.clear()
        st.rerun()

# newest first, so the latest answer is visible without scrolling
for asked, reply, table in reversed(history):
    with st.chat_message("user"):
        st.write(asked)
    with st.chat_message("assistant"):
        st.markdown(reply)
        if table is not None:
            st.dataframe(table, hide_index=True, use_container_width=True)

st.caption("এটি নিয়মভিত্তিক অফলাইন সহকারী; অ্যাপের ডেটা ও নির্ধারিত তথ্য থেকে উত্তর দেয়।")
