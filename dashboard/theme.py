"""Purple and gold visual theme shared by every page."""
import re
from base64 import b64encode
from html import escape

BG, PANEL, TEXT, MUTED = "#170D21", "#2A1837", "#F6F0FA", "#A687BC"
AMBER, ORANGE, GOLD, RED, OLIVE = "#F4B647", "#F2762E", "#F5C84C", "#E5484D", "#A9BC5F"

CSS = """<style>
.stApp{background:radial-gradient(circle at 15% 110%,rgba(232,154,52,.12) 0,transparent 40%),radial-gradient(circle at 80% -10%,#371F48 0,transparent 45%),#170D21}
[data-testid="stSidebar"]{background:linear-gradient(180deg,#24142F,#170D1F);border-right:1px solid #39204B}
.block-container{padding-top:3.2rem;padding-bottom:2rem;max-width:1450px}
h1,h2,h3{letter-spacing:.3px}
h1{background:linear-gradient(90deg,#F6F0FA 35%,#F4B647);-webkit-background-clip:text;background-clip:text;
-webkit-text-fill-color:transparent}
[data-testid="stMetric"]{background:linear-gradient(160deg,#321C42,#24142F);border:1px solid #3F2352;
border-top:2px solid #F4B647;border-radius:12px;padding:14px 16px;box-shadow:0 10px 24px rgba(0,0,0,.35)}
[data-testid="stPlotlyChart"],[data-testid="stDataFrame"]{border:1px solid #3F2352;border-radius:12px;
overflow:hidden;box-shadow:0 10px 24px rgba(0,0,0,.3)}
.stButton>button,.stDownloadButton>button,[data-testid="stFormSubmitButton"] button{border-radius:10px;
border:1px solid #5E3F74;background:linear-gradient(160deg,#311C41,#24142F);color:#F6F0FA}
.stButton>button:hover,.stDownloadButton>button:hover{border-color:#F4B647;color:#F5C84C;
box-shadow:0 0 14px rgba(244,182,71,.35)}
.dw-hero{border-radius:16px;border:1px solid #3F2352;padding:24px 28px;margin-bottom:14px;
background-color:#2A1837;background-repeat:no-repeat;background-position:right bottom;background-size:75% 100%}
.dw-hero-title{font-size:clamp(24px,3.4vw,36px);font-weight:800;letter-spacing:2px;color:#F6F0FA}
.dw-hero-text{color:#B8A0C9;font-size:15px;margin-top:6px;max-width:720px}
.dw-badge{display:inline-block;margin:12px 8px 0 0;padding:4px 14px;border-radius:30px;font-size:12px;
font-weight:700;border:1px solid #5E3F74;background:#20122A;color:#F5C84C}
.dw-badge.ok{border-color:#58703A;color:#BCD070}
.dw-gauges{display:grid;grid-template-columns:repeat(auto-fit,minmax(190px,1fr));gap:12px;margin-bottom:14px}
.dw-gauge{background:linear-gradient(160deg,#321C42,#23142E);border:1px solid #3F2352;border-radius:14px;
padding:14px;text-align:center;box-shadow:0 10px 24px rgba(0,0,0,.35)}
.dw-ring{position:relative;width:150px;height:150px;margin:auto}
.dw-ring img{width:100%;height:100%}
.dw-value{position:absolute;inset:0;display:flex;align-items:center;justify-content:center;
font-size:30px;font-weight:700;color:#F6F0FA}
.dw-label{font-size:15px;font-weight:700;color:#F6F0FA}
.dw-note{font-size:12px;color:#A687BC;margin-top:2px}
.dw-panel{background:linear-gradient(160deg,#301B3F,#23142E);border:1px solid #3F2352;border-radius:14px;
padding:16px 18px;margin-bottom:14px;box-shadow:0 10px 24px rgba(0,0,0,.35)}
.dw-panel-title{font-size:18px;font-weight:700;color:#F6F0FA;margin-bottom:6px}
.dw-line{display:flex;align-items:center;gap:12px;padding:9px 0;border-bottom:1px solid #39204B;color:#E6E0D6}
.dw-line:last-child{border-bottom:0}
.dw-name{width:130px;flex:none;font-size:14px}
.dw-track{flex:1;height:7px;border-radius:8px;background:#402454}
.dw-fill{height:7px;border-radius:8px}
.dw-num{min-width:64px;text-align:right;font-size:18px;font-weight:700}
.dw-dot{width:10px;height:10px;border-radius:50%;flex:none;box-shadow:0 0 10px currentColor;background:currentColor}
.dw-action{font-size:14px;line-height:1.45}
.dw-action b{color:#F5C84C}
.risk-box{padding:20px;border-radius:14px;margin-bottom:10px}
.risk-low{background:#242A16;border:1px solid #7E9142}
.risk-medium{background:#332C13;border:1px solid #B5932F}
.risk-high{background:#392313;border:1px solid #C96A24}
.risk-critical{background:#3B191B;border:1px solid #B9444A}
.small-note{color:#A687BC;font-size:13px}
.demo-banner{background:#2F2716;border:1px solid #8B7029;padding:12px 16px;border-radius:10px;
color:#F5D78A;margin-bottom:18px}
.dw-board-head{display:flex;justify-content:space-between;flex-wrap:wrap;gap:8px;align-items:center;
margin-bottom:6px}
.dw-legend span{font-size:12px;color:#B8A0C9;margin-left:14px}
.dw-legend i{display:inline-block;width:10px;height:10px;border-radius:3px;margin-right:6px}
.dw-city{padding:12px 0 6px;border-top:1px solid #39204B}
.dw-city-head{display:flex;justify-content:space-between;font-size:13px;font-weight:700;color:#F6F0FA;
letter-spacing:1px;text-transform:uppercase;margin-bottom:8px}
.dw-city-head small{font-weight:500;color:#A687BC;letter-spacing:0;text-transform:none;font-size:12px}
.dw-tiles{display:grid;grid-template-columns:repeat(10,minmax(0,1fr));gap:6px}
.dw-tile{border-radius:8px;padding:6px 2px;text-align:center;border:1px solid;transition:transform .15s}
.dw-tile:hover{transform:translateY(-3px)}
.dw-tile span{display:block;font-size:10px;color:#CEBEDA}
.dw-tile b{display:block;font-size:16px;color:#FFF;line-height:1.35}
@media (max-width:700px){.dw-tiles{grid-template-columns:repeat(5,minmax(0,1fr))}}
.dw-stats{display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:12px;margin-bottom:14px}
.dw-stat{border-radius:12px;padding:14px 16px;border:1px solid #3F2352;border-left:5px solid;
background:linear-gradient(160deg,#321C42,#23142E);box-shadow:0 10px 24px rgba(0,0,0,.3)}
.dw-stat b{display:block;font-size:32px;line-height:1.3;color:#F6F0FA}
.dw-stat span{font-size:13px;font-weight:700;color:#E6E0D6}
.dw-stat small{display:block;font-size:12px;color:#A687BC}
.dw-alert{border-radius:12px;border:1px solid;padding:12px 16px;margin-bottom:10px;font-size:14px;color:#F6F0FA}
.dw-alert b{display:block;font-size:12px;letter-spacing:1.5px;margin-bottom:3px}
.dw-compare{display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));gap:12px;margin-bottom:14px}
.dw-card{border-radius:14px;border:1px solid #3F2352;background:#291736;padding:14px 16px;text-align:center}
.dw-card-title{font-size:13px;font-weight:700;color:#A687BC;letter-spacing:1px}
.dw-ab{display:flex;justify-content:center;align-items:center;gap:18px;margin:8px 0}
.dw-ab div{font-size:12px;color:#A687BC}
.dw-ab b{display:block;font-size:30px;color:#F2762E}
.dw-ab div+i+div b{color:#BCD070}
.dw-ab i{font-style:normal;font-size:24px;color:#5E3F74}
.dw-saved{display:inline-block;border-radius:30px;padding:3px 14px;font-size:13px;font-weight:700;
background:rgba(169,188,95,.16);color:#BCD070}
.dw-phone{max-width:370px;margin:0 auto 14px;border:8px solid #412455;border-radius:34px;background:#130B19;
padding:12px;box-shadow:0 18px 40px rgba(0,0,0,.5),0 0 30px rgba(244,182,71,.14)}
.dw-notch{width:90px;height:6px;border-radius:6px;background:#412455;margin:0 auto 12px}
.dw-sender{font-size:13px;font-weight:700;color:#F6F0FA;border-bottom:1px solid #341D44;padding-bottom:8px}
.dw-banner{border-radius:10px 10px 0 0;padding:8px 12px;margin-top:12px;font-size:12px;font-weight:800;
letter-spacing:1.5px;color:#fff}
.dw-bubble{border-radius:0 0 14px 14px;background:#2B1839;padding:12px;font-size:13px;line-height:1.65;
color:#EDE8E0;word-wrap:break-word;min-height:170px}
.dw-map{border:1px solid #3F2352;border-radius:14px;overflow:hidden;margin-bottom:14px;
box-shadow:0 14px 32px rgba(0,0,0,.45)}
.dw-map img{display:block;width:100%}
.dw-bar{display:flex;justify-content:space-between;flex-wrap:wrap;gap:8px;align-items:center;
background:linear-gradient(90deg,#2D1A3C,#251531);border:1px solid #3F2352;border-left:5px solid #F4B647;
border-radius:12px;padding:12px 18px;margin-bottom:14px}
.dw-bar b{font-size:22px;color:#F6F0FA;letter-spacing:.5px}
.dw-bar span{font-size:12px;color:#B8A0C9}
.dw-quad{display:grid;grid-template-columns:1fr 1fr;gap:10px;margin-bottom:12px}
.dw-quad div{background:linear-gradient(160deg,#341D44,#23142E);border:1px solid #3F2352;border-radius:12px;
padding:12px}
.dw-quad span{display:block;font-size:12px;color:#B8A0C9}
.dw-quad b{display:block;font-size:30px;line-height:1.35}
.dw-blocks{display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:12px;margin-bottom:14px}
.dw-block{border-radius:12px;padding:16px;color:#17140F;box-shadow:0 12px 26px rgba(0,0,0,.35)}
.dw-block span{display:block;font-size:13px;font-weight:700}
.dw-block b{display:block;font-size:40px;line-height:1.25}
.dw-block small{font-size:12px;font-weight:600}
.dw-table{width:100%;border-collapse:collapse;font-size:13px;color:#E6E0D6}
.dw-table th{text-align:left;color:#A687BC;font-size:11px;letter-spacing:1px;padding:8px 6px;
border:0;border-bottom:1px solid #4E2C66}
.dw-table td{padding:10px 6px;border:0;border-bottom:1px solid #39204B}
.dw-pill{display:inline-block;border-radius:20px;padding:2px 11px;font-size:11px;font-weight:800;color:#17140F}
.dw-flow{display:grid;grid-template-columns:repeat(5,minmax(0,1fr));gap:8px;margin-bottom:16px}
.dw-step{border:1px solid #3F2352;border-radius:10px;padding:9px 12px;background:#24142F}
.dw-step b{display:block;font-size:13px;color:#B8A0C9}
.dw-step span{font-size:11px;color:#8659A6}
.dw-step.done{border-color:#5E3F74}
.dw-step.now{background:linear-gradient(135deg,#F4B647,#F2762E);border-color:#F5C84C;
box-shadow:0 0 22px rgba(244,182,71,.35)}
.dw-step.now b,.dw-step.now span{color:#17140F}
.dw-routes{display:grid;grid-template-columns:repeat(auto-fill,minmax(260px,1fr));gap:12px;margin-bottom:14px}
.dw-route{display:flex;align-items:center;justify-content:space-between;gap:8px;border:1px solid #3F2352;
border-radius:14px;padding:14px;background:linear-gradient(160deg,#321C42,#23142E)}
.dw-route div{text-align:center;font-size:11px;color:#A687BC}
.dw-route div b{display:block;font-size:14px;color:#F6F0FA}
.dw-route .mid{flex:1;border-bottom:2px dashed #F4B647;padding-bottom:6px;color:#F5C84C;font-weight:800}
@media (max-width:700px){.dw-flow{grid-template-columns:repeat(2,minmax(0,1fr))}}
[data-testid="stSidebarNav"] a{border-radius:10px;margin:2px 8px}
[data-testid="stSidebarNav"] a[aria-current="page"]{background:linear-gradient(135deg,#F8CB6B,#E89A34);
box-shadow:0 6px 18px rgba(244,182,71,.35)}
[data-testid="stSidebarNav"] a[aria-current="page"] span{color:#1F1027;font-weight:700}
[data-testid="stHeader"]{background:transparent}
</style>"""


def _uri(svg):
    return "data:image/svg+xml;base64," + b64encode(svg.encode()).decode()


def hero(title, text, badges=()):
    """Banner with layered waves. badges: (label, is_ok) pairs."""
    waves = (
        "<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 800 160' preserveAspectRatio='none'>"
        "<path d='M0 160C130 150 190 60 300 80S450 130 540 70 680 10 800 40V160z' fill='#B565E8' opacity='.22'/>"
        "<path d='M120 160C250 150 310 90 420 105S590 150 660 100 750 70 800 80V160z' fill='#F4B647' opacity='.12'/>"
        "<path d='M260 160C380 150 450 120 540 132S700 150 800 118V160z' fill='#000' opacity='.28'/></svg>"
    )
    chips = "".join(
        f"<span class='dw-badge{' ok' if ok else ''}'>{label}</span>" for label, ok in badges
    )
    return (
        f"<div class='dw-hero' style=\"background-image:url('{_uri(waves)}')\">"
        f"<div class='dw-hero-title'>{title}</div>"
        f"<div class='dw-hero-text'>{text}</div>{chips}</div>"
    )


def _ring(fraction, color):
    """270 degree arc filled to the given fraction."""
    fraction = min(max(float(fraction), 0), 1)
    full = 2 * 3.14159 * 50 * 0.75
    arc = ("<circle cx='60' cy='60' r='50' fill='none' stroke-linecap='round' "
           "transform='rotate(135 60 60)' stroke='{c}' stroke-width='{w}' opacity='{o}' "
           f"stroke-dasharray='{{n:.1f}} 400'/>")
    parts = arc.format(c="#502D69", w=7, o=1, n=full)
    if fraction > 0:
        parts += arc.format(c=color, w=13, o=.22, n=full * fraction)
        parts += arc.format(c=color, w=7, o=1, n=full * fraction)
    return _uri(f"<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 120 120'>{parts}</svg>")


def gauges(items):
    """items: (value text, label, note, fraction, color)."""
    cards = "".join(
        f"<div class='dw-gauge'><div class='dw-ring'><img src='{_ring(fraction, color)}' alt=''>"
        f"<div class='dw-value'>{value}</div></div><div class='dw-label'>{label}</div>"
        f"<div class='dw-note'>{note}</div></div>"
        for value, label, note, fraction, color in items
    )
    return f"<div class='dw-gauges'>{cards}</div>"


def bars(title, rows):
    """rows: (name, value text, fraction, color)."""
    lines = "".join(
        f"<div class='dw-line'><span class='dw-dot' style='color:{color}'></span>"
        f"<span class='dw-name'>{name}</span><span class='dw-track'><div class='dw-fill' "
        f"style='width:{min(max(fraction, 0), 1) * 100:.0f}%;background:{color}'></div></span>"
        f"<span class='dw-num'>{value}</span></div>"
        for name, value, fraction, color in rows
    )
    return f"<div class='dw-panel'><div class='dw-panel-title'>{title}</div>{lines}</div>"


def actions(title, rows):
    """rows: (html text, color)."""
    lines = "".join(
        f"<div class='dw-line'><span class='dw-dot' style='color:{color}'></span>"
        f"<span class='dw-action'>{text}</span></div>"
        for text, color in rows
    )
    return f"<div class='dw-panel'><div class='dw-panel-title'>{title}</div>{lines}</div>"


def ward_board(title, legend, cities):
    """
    Ward risk grid grouped by city.

    legend: (level, color) pairs.
    cities: (name, summary, tiles) with tiles (label, value, tooltip, color).
    """
    keys = "".join(f"<span><i style='background:{color}'></i>{level}</span>"
                   for level, color in legend)
    blocks = ""
    for name, summary, tiles in cities:
        cells = "".join(
            f"<div class='dw-tile' title='{tip}' style='border-color:{color};"
            f"background:linear-gradient(180deg,{color}66,{color}1F)'>"
            f"<span>{label}</span><b>{value}</b></div>"
            for label, value, tip, color in tiles
        )
        blocks += (f"<div class='dw-city'><div class='dw-city-head'>{name}<small>{summary}</small></div>"
                   f"<div class='dw-tiles'>{cells}</div></div>")
    return (f"<div class='dw-panel'><div class='dw-board-head'><div class='dw-panel-title'>{title}</div>"
            f"<div class='dw-legend'>{keys}</div></div>{blocks}</div>")


def stats(items):
    """items: (value, label, note, color)."""
    tiles = "".join(
        f"<div class='dw-stat' style='border-left-color:{color}'><b>{value}</b>"
        f"<span>{label}</span><small>{note}</small></div>"
        for value, label, note, color in items
    )
    return f"<div class='dw-stats'>{tiles}</div>"


def alert(title, text, color):
    return (f"<div class='dw-alert' style='border-color:{color};background:{color}22'>"
            f"<b style='color:{color}'>{title}</b>{text}</div>")


def compare(items):
    """Before and after cards. items: (title, before, after)."""
    cards = "".join(
        f"<div class='dw-card'><div class='dw-card-title'>{title}</div><div class='dw-ab'>"
        f"<div>Before<b>{before:.1f}</b></div><i>&#8594;</i><div>After<b>{after:.1f}</b></div></div>"
        f"<span class='dw-saved'>{before - after:.1f} cases prevented</span></div>"
        for title, before, after in items
    )
    return f"<div class='dw-compare'>{cards}</div>"


def phone(sender, banner, color, message):
    """Phone preview of a plain text message (*bold* is shown as bold)."""
    body = re.sub(r"\*([^*\n]+)\*", r"<b>\1</b>", escape(message)).replace("\n", "<br>")
    return (f"<div class='dw-phone'><div class='dw-notch'></div><div class='dw-sender'>{sender}</div>"
            f"<div class='dw-banner' style='background:{color}'>{banner}</div>"
            f"<div class='dw-bubble'>{body}</div></div>")


def title_bar(title, note):
    return f"<div class='dw-bar'><b>{title}</b><span>{note}</span></div>"


def quad(items):
    """Two by two metric tiles. items: (label, value, color)."""
    tiles = "".join(f"<div><span>{label}</span><b style='color:{color}'>{value}</b></div>"
                    for label, value, color in items)
    return f"<div class='dw-quad'>{tiles}</div>"


def blocks(items):
    """Solid colour counters. items: (label, value, note, color)."""
    tiles = "".join(
        f"<div class='dw-block' style='background:linear-gradient(135deg,{color},{color}C0)'>"
        f"<span>{label}</span><b>{value}</b><small>{note}</small></div>"
        for label, value, note, color in items
    )
    return f"<div class='dw-blocks'>{tiles}</div>"


def pill(text, color):
    return f"<span class='dw-pill' style='background:{color}'>{text}</span>"


def table(title, headers, rows):
    """rows hold ready HTML cells."""
    head = "".join(f"<th>{h}</th>" for h in headers)
    body = "".join("<tr>" + "".join(f"<td>{c}</td>" for c in row) + "</tr>" for row in rows)
    return (f"<div class='dw-panel'><div class='dw-panel-title'>{title}</div>"
            f"<table class='dw-table'><tr>{head}</tr>{body}</table></div>")


STEPS = [
    ("Detect", "Where is the risk"), ("Allocate", "Share scarce supplies"),
    ("Route", "Move overflow patients"), ("Simulate", "Test crew impact"),
    ("Dispatch", "Send the orders"),
]


def flow(current):
    """Five step decision path; current is 1 to 5."""
    cells = "".join(
        f"<div class='dw-step{' now' if n == current else ' done' if n < current else ''}'>"
        f"<b>{n}. {name}</b><span>{note}</span></div>"
        for n, (name, note) in enumerate(STEPS, start=1)
    )
    return f"<div class='dw-flow'>{cells}</div>"


def routes(items):
    """items: (from ward, to ward, patients)."""
    cards = "".join(
        f"<div class='dw-route'><div>FROM<b>{source}</b></div>"
        f"<div class='mid'>{count} patient(s) &#8594;</div><div>TO<b>{target}</b></div></div>"
        for source, target, count in items
    )
    return f"<div class='dw-routes'>{cards}</div>"


def style_figure(figure, height=360):
    figure.update_layout(
        template="plotly_dark", height=height,
        paper_bgcolor="#271633", plot_bgcolor="#271633",
        font={"color": "#D2C3DD"}, margin={"l": 16, "r": 16, "t": 44, "b": 16},
        colorway=[AMBER, GOLD, ORANGE, RED, OLIVE],
        legend={"orientation": "h", "y": 1.08, "x": 0},
    )
    figure.update_xaxes(gridcolor="rgba(255,255,255,.07)", zeroline=False)
    figure.update_yaxes(gridcolor="rgba(255,255,255,.07)", zeroline=False)
    return figure
