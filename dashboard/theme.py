"""Charcoal and amber visual theme shared by every page."""
from base64 import b64encode

BG, PANEL, TEXT, MUTED = "#151517", "#222226", "#F1ECE3", "#A9A39A"
AMBER, ORANGE, GOLD, RED, OLIVE = "#F2A33A", "#F2762E", "#F5C84C", "#E5484D", "#A9BC5F"

CSS = """<style>
.stApp{background:radial-gradient(circle at 80% -10%,#33302C 0,transparent 45%),#151517}
[data-testid="stSidebar"]{background:linear-gradient(180deg,#1D1D20,#121214);border-right:1px solid #34322F}
.block-container{padding-top:3.2rem;padding-bottom:2rem;max-width:1450px}
h1,h2,h3{letter-spacing:.3px}
h1{background:linear-gradient(90deg,#F1ECE3 35%,#F2A33A);-webkit-background-clip:text;background-clip:text;
-webkit-text-fill-color:transparent}
[data-testid="stMetric"]{background:linear-gradient(160deg,#29292E,#1D1D20);border:1px solid #3A3733;
border-top:2px solid #F2A33A;border-radius:12px;padding:14px 16px;box-shadow:0 10px 24px rgba(0,0,0,.35)}
[data-testid="stPlotlyChart"],[data-testid="stDataFrame"]{border:1px solid #3A3733;border-radius:12px;
overflow:hidden;box-shadow:0 10px 24px rgba(0,0,0,.3)}
.stButton>button,.stDownloadButton>button,[data-testid="stFormSubmitButton"] button{border-radius:10px;
border:1px solid #6A5A3E;background:linear-gradient(160deg,#2E2B27,#201F1D);color:#F1ECE3}
.stButton>button:hover,.stDownloadButton>button:hover{border-color:#F2A33A;color:#F5C84C;
box-shadow:0 0 14px rgba(242,163,58,.35)}
.dw-hero{border-radius:16px;border:1px solid #3A3733;padding:24px 28px;margin-bottom:14px;
background-color:#222226;background-repeat:no-repeat;background-position:right bottom;background-size:75% 100%}
.dw-hero-title{font-size:clamp(24px,3.4vw,36px);font-weight:800;letter-spacing:2px;color:#F1ECE3}
.dw-hero-text{color:#BDB6AC;font-size:15px;margin-top:6px;max-width:720px}
.dw-badge{display:inline-block;margin:12px 8px 0 0;padding:4px 14px;border-radius:30px;font-size:12px;
font-weight:700;border:1px solid #6A5A3E;background:#1A1A1C;color:#F5C84C}
.dw-badge.ok{border-color:#58703A;color:#BCD070}
.dw-gauges{display:grid;grid-template-columns:repeat(auto-fit,minmax(190px,1fr));gap:12px;margin-bottom:14px}
.dw-gauge{background:linear-gradient(160deg,#29292E,#1C1C1F);border:1px solid #3A3733;border-radius:14px;
padding:14px;text-align:center;box-shadow:0 10px 24px rgba(0,0,0,.35)}
.dw-ring{position:relative;width:150px;height:150px;margin:auto}
.dw-ring img{width:100%;height:100%}
.dw-value{position:absolute;inset:0;display:flex;align-items:center;justify-content:center;
font-size:30px;font-weight:700;color:#F1ECE3}
.dw-label{font-size:15px;font-weight:700;color:#F1ECE3}
.dw-note{font-size:12px;color:#A9A39A;margin-top:2px}
.dw-panel{background:linear-gradient(160deg,#27272B,#1C1C1F);border:1px solid #3A3733;border-radius:14px;
padding:16px 18px;margin-bottom:14px;box-shadow:0 10px 24px rgba(0,0,0,.35)}
.dw-panel-title{font-size:18px;font-weight:700;color:#F1ECE3;margin-bottom:6px}
.dw-line{display:flex;align-items:center;gap:12px;padding:9px 0;border-bottom:1px solid #333130;color:#E6E0D6}
.dw-line:last-child{border-bottom:0}
.dw-name{width:130px;flex:none;font-size:14px}
.dw-track{flex:1;height:7px;border-radius:8px;background:#38363A}
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
.small-note{color:#A9A39A;font-size:13px}
.demo-banner{background:#2F2716;border:1px solid #8B7029;padding:12px 16px;border-radius:10px;
color:#F5D78A;margin-bottom:18px}
.dw-board-head{display:flex;justify-content:space-between;flex-wrap:wrap;gap:8px;align-items:center;
margin-bottom:6px}
.dw-legend span{font-size:12px;color:#BDB6AC;margin-left:14px}
.dw-legend i{display:inline-block;width:10px;height:10px;border-radius:3px;margin-right:6px}
.dw-city{padding:12px 0 6px;border-top:1px solid #333130}
.dw-city-head{display:flex;justify-content:space-between;font-size:13px;font-weight:700;color:#F1ECE3;
letter-spacing:1px;text-transform:uppercase;margin-bottom:8px}
.dw-city-head small{font-weight:500;color:#A9A39A;letter-spacing:0;text-transform:none;font-size:12px}
.dw-tiles{display:grid;grid-template-columns:repeat(10,minmax(0,1fr));gap:6px}
.dw-tile{border-radius:8px;padding:6px 2px;text-align:center;border:1px solid;transition:transform .15s}
.dw-tile:hover{transform:translateY(-3px)}
.dw-tile span{display:block;font-size:10px;color:#D5CEC3}
.dw-tile b{display:block;font-size:16px;color:#FFF;line-height:1.35}
@media (max-width:700px){.dw-tiles{grid-template-columns:repeat(5,minmax(0,1fr))}}
</style>"""


def _uri(svg):
    return "data:image/svg+xml;base64," + b64encode(svg.encode()).decode()


def hero(title, text, badges=()):
    """Banner with layered waves. badges: (label, is_ok) pairs."""
    waves = (
        "<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 800 160' preserveAspectRatio='none'>"
        "<path d='M0 160C130 150 190 60 300 80S450 130 540 70 680 10 800 40V160z' fill='#fff' opacity='.05'/>"
        "<path d='M120 160C250 150 310 90 420 105S590 150 660 100 750 70 800 80V160z' fill='#F2A33A' opacity='.12'/>"
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
    parts = arc.format(c="#45424A", w=7, o=1, n=full)
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


def style_figure(figure, height=360):
    figure.update_layout(
        template="plotly_dark", height=height,
        paper_bgcolor="#1F1F23", plot_bgcolor="#1F1F23",
        font={"color": "#D9D2C7"}, margin={"l": 16, "r": 16, "t": 44, "b": 16},
        colorway=[AMBER, GOLD, ORANGE, RED, OLIVE],
        legend={"orientation": "h", "y": 1.08, "x": 0},
    )
    figure.update_xaxes(gridcolor="rgba(255,255,255,.07)", zeroline=False)
    figure.update_yaxes(gridcolor="rgba(255,255,255,.07)", zeroline=False)
    return figure
