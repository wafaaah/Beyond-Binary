"""Top section of the main dashboard: situation banner, KPI cards, priority wards."""
from base64 import b64encode

import streamlit as st

from i18n import is_bangla, t
from shared import RISK_COLORS

CSS = """<style>
.db-hero{position:relative;overflow:hidden;border-radius:22px;border:1px solid #4B2A62;padding:30px 34px;
margin-bottom:14px;background-color:#251530;background-repeat:no-repeat;background-position:right center;
background-size:auto 100%;box-shadow:0 24px 60px rgba(0,0,0,.45)}
.db-title{font-size:clamp(30px,4.6vw,50px);font-weight:800;color:#F6F0FA;line-height:1.25}
.db-title b{color:#F4B647}
.db-sub{font-size:16px;color:#D2C3DD;margin-top:4px}
.db-chip{display:inline-block;margin:14px 8px 0 0;border-radius:30px;padding:5px 15px;font-size:12px;
font-weight:700;border:1px solid #6B4685;background:rgba(21,12,28,.75);color:#F6F0FA}
.db-chip.gold{background:linear-gradient(135deg,#F8CB6B,#E89A34);border:0;color:#1F1027}
.db-cards{display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));gap:12px;margin-bottom:14px}
.db-card{position:relative;border-radius:18px;border:1px solid;padding:16px 18px 6px;overflow:hidden;
transition:transform .2s}
.db-card:hover{transform:translateY(-4px)}
.db-card span{display:block;font-size:13px;font-weight:700;color:#D2C3DD}
.db-card b{display:block;font-size:34px;line-height:1.35;color:#fff}
.db-card small{display:block;font-size:12px;color:#BFA9CE;min-height:18px}
.db-card img{display:block;width:100%;height:52px;margin-top:4px}
.db-strip{display:grid;grid-template-columns:repeat(auto-fit,minmax(170px,1fr));gap:10px;margin-bottom:8px}
.db-ward{border-radius:14px;background:#251530;border:1px solid #39204B;border-top:4px solid;padding:12px 14px}
.db-ward em{font-style:normal;font-size:11px;color:#A687BC}
.db-ward b{display:block;font-size:16px;color:#F6F0FA;margin:2px 0}
.db-ward span{font-size:13px;font-weight:800}
.db-h{font-size:13px;font-weight:800;letter-spacing:1.5px;color:#F4B647;margin:4px 0 8px}
</style>"""


def _uri(svg):
    return "data:image/svg+xml;base64," + b64encode(svg.encode()).decode()


def _skyline():
    """Original artwork: radar rings over a city skyline with a river wave."""
    svg = ["<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 620 220'>",
           "<defs><radialGradient id='g'><stop offset='0' stop-color='#F4B647' stop-opacity='.55'/>"
           "<stop offset='1' stop-color='#F4B647' stop-opacity='0'/></radialGradient></defs>",
           "<circle cx='450' cy='96' r='120' fill='url(#g)'/>"]
    for r in (34, 62, 92, 124):
        svg.append(f"<circle cx='450' cy='96' r='{r}' fill='none' stroke='#F4B647' "
                   f"stroke-opacity='{.6 - r / 280:.2f}' stroke-width='1.5'/>")
    heights = [52, 84, 60, 112, 74, 138, 66, 98, 54, 120, 80, 62, 104, 70, 90, 58, 76, 46]
    for i, height in enumerate(heights):
        x = 60 + i * 31
        svg.append(f"<rect x='{x}' y='{220 - height}' width='24' height='{height}' fill='#150C1C'/>")
        for y in range(228 - height, 210, 14):
            if (i + y) % 3:
                svg.append(f"<rect x='{x + 6 + (y % 2) * 7}' y='{y}' width='4' height='5' "
                           "fill='#F4B647' opacity='.75'/>")
    for x, y, color in [(450, 96, "#E5484D"), (508, 64, "#F2762E"), (396, 128, "#F5C84C")]:
        svg.append(f"<circle cx='{x}' cy='{y}' r='13' fill='{color}' opacity='.3'/>"
                   f"<circle cx='{x}' cy='{y}' r='5' fill='{color}'/>")
    svg.append("<path d='M0 204C150 170 300 226 450 192S590 180 620 188' fill='none' "
               "stroke='#B565E8' stroke-width='3' opacity='.7'/></svg>")
    return _uri("".join(svg))


def _spark(values, color):
    values = [float(v) for v in values] or [0, 0]
    if len(values) == 1:
        values *= 2
    low, high = min(values), max(values)
    span = (high - low) or 1
    points = " ".join(f"{i * 200 / (len(values) - 1):.1f},{46 - (v - low) / span * 40:.1f}"
                      for i, v in enumerate(values))
    return _uri(
        "<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 200 50' preserveAspectRatio='none'>"
        f"<polygon points='0,50 {points} 200,50' fill='{color}' opacity='.18'/>"
        f"<polyline points='{points}' fill='none' stroke='{color}' stroke-width='2.5'/></svg>")


def _card(label, value, note, color, series):
    return (f"<div class='db-card' style='border-color:{color}66;"
            f"background:linear-gradient(150deg,{color}2E,#251530 60%)'><span>{label}</span>"
            f"<b>{value}</b><small>{note}</small><img src='{_spark(series, color)}' alt=''></div>")


def render_briefing(frame, city, ward, start, end, summary, forecasts):
    """Draw the banner, four KPI cards and the priority wards."""
    def say(bangla, english):
        return bangla if is_bangla() else english

    st.markdown(CSS, unsafe_allow_html=True)
    st.markdown(
        f"<div class='db-hero' style=\"background-image:linear-gradient(90deg,#251530 34%,"
        f"rgba(37,21,48,.15) 75%),url('{_skyline()}')\">"
        "<div class='db-title'>Dengue<b>Watch</b></div>"
        f"<div class='db-sub'>{t('WARD RISK INTELLIGENCE SYSTEM | BANGLADESH')}</div>"
        f"<span class='db-chip gold'>{t(city)} | {t(ward)}</span>"
        f"<span class='db-chip'>{start:%d %b %Y} → {end:%d %b %Y}</span>"
        f"<span class='db-chip'>{say('পুরোনো তথ্য, সরাসরি নয়', 'Historical data, not live')}</span>"
        "</div>", unsafe_allow_html=True)

    month = frame["date"].dt.to_period("M")
    monthly = frame.groupby(month).agg(
        cases=("dengue_cases", "sum"), rain=("rainfall_mm", "mean"),
        temp=("avg_temp_c", "mean")).tail(24)
    per_ward = frame.groupby("ward_id")["dengue_cases"].sum().sort_values(ascending=False)
    shown = say(f"শেষ {len(monthly)} মাসের ধারা", f"trend, last {len(monthly)} months")
    st.markdown("<div class='db-cards'>" + "".join([
        _card(t("Historical Dengue Cases"), f"{summary['total_cases']:,}", shown,
              "#F4B647", monthly["cases"]),
        _card(t("Wards Represented"), summary["total_wards"],
              say("ওয়ার্ডভিত্তিক রোগী, বেশি থেকে কম", "cases by ward, high to low"), "#B565E8", per_ward),
        _card(t("Average Rainfall"), f"{summary['avg_rainfall']:.1f} mm", shown,
              "#4DA6F0", monthly["rain"]),
        _card(t("Average Temperature"), f"{summary['avg_temperature']:.1f} °C", shown,
              "#F2762E", monthly["temp"]),
    ]) + "</div>", unsafe_allow_html=True)

    if forecasts.empty:
        return
    nearest = forecasts[forecasts["weeks_ahead"] == forecasts["weeks_ahead"].min()]
    top = nearest.sort_values("predicted_cases", ascending=False).head(5)
    weeks = int(nearest["weeks_ahead"].iloc[0])
    title = say(f"অগ্রাধিকার ওয়ার্ড: {weeks} সপ্তাহ পরের পূর্বাভাস",
                f"PRIORITY WARDS: {weeks}-WEEK FORECAST")
    cells = "".join(
        f"<div class='db-ward' style='border-top-color:{RISK_COLORS[r.risk_level]}'>"
        f"<em>#{i}</em><b>{r.ward_id}</b>"
        f"<span style='color:{RISK_COLORS[r.risk_level]}'>{t(r.risk_level)} · "
        f"{r.predicted_cases:.1f} {say('রোগী', 'cases')}</span></div>"
        for i, r in enumerate(top.itertuples(), start=1))
    st.markdown(f"<div class='db-h'>{title}</div><div class='db-strip'>{cells}</div>",
                unsafe_allow_html=True)
