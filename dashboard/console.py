"""Single window console layouts for the Simulator and Dispatch pages."""
from base64 import b64encode

from ops_map import positions

CSS = """<style>
.cx{border:1px solid #4A4339;border-radius:18px;overflow:hidden;background:#111113;
box-shadow:0 24px 60px rgba(0,0,0,.55),0 0 0 4px rgba(242,163,58,.07);margin-bottom:16px;color:#F1ECE3}
.cx-head{display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:8px;
padding:13px 20px;background:linear-gradient(90deg,#F2762E,#F2A33A 45%,#3A3125 90%);color:#17120A}
.cx-head b{font-size:21px;letter-spacing:.5px}
.cx-head span{font-size:12px;font-weight:700;color:#F6E7CC}
.cx-grid{display:grid;gap:10px;padding:10px}
.cx-sim{grid-template-columns:1.35fr 1.35fr 1.15fr;grid-template-areas:"map map side" "route chart side"}
.cx-card{background:#1D1D21;border:1px solid #34322F;border-radius:12px;padding:12px;min-width:0}
.cx-title{font-size:12px;font-weight:800;letter-spacing:1.2px;color:#C9BFAE;text-transform:uppercase;
margin-bottom:8px}
.cx-card img{display:block;width:100%;border-radius:8px}
.cx-map{grid-area:map;padding:0;overflow:hidden}.cx-map .dw-map{margin:0;border:0;border-radius:0;box-shadow:none}
.cx-map .dw-map img{border-radius:0}
.cx-side{grid-area:side;display:flex;flex-direction:column;gap:10px}
.cx-route{grid-area:route}.cx-chart{grid-area:chart}
.cx-kpis{display:grid;grid-template-columns:1fr 1fr;gap:8px}
.cx-kpi{background:#1D1D21;border:1px solid #34322F;border-radius:12px;padding:10px 12px}
.cx-kpi span{display:block;font-size:11px;color:#A9A39A}
.cx-kpi b{display:block;font-size:30px;line-height:1.35}
.cx-kpi small{font-size:10px;color:#85807A}
.cx-row{display:flex;align-items:center;gap:10px;padding:7px 0;border-bottom:1px solid #2E2C2A;font-size:12px}
.cx-row:last-child{border:0}
.cx-row em{font-style:normal;width:112px;flex:none}
.cx-row i{flex:1;height:8px;border-radius:8px;background:#34323A;overflow:hidden}
.cx-row i u{display:block;height:8px;border-radius:8px}
.cx-row strong{min-width:42px;text-align:right;font-size:14px}
.cx-dispatch{grid-template-columns:2.2fr 1fr}
.cx-main{display:flex;flex-direction:column;gap:10px;min-width:0}
.cx-three{display:grid;grid-template-columns:repeat(3,1fr);gap:10px}
.cx-big{border-radius:12px;padding:14px 16px;color:#17120A}
.cx-big span{display:block;font-size:12px;font-weight:800}
.cx-big b{display:block;font-size:44px;line-height:1.2}
.cx-big small{font-size:11px;font-weight:700}
.cx-channel b{display:block;font-size:28px;line-height:1.35}
.cx-channel small{font-size:11px;color:#A9A39A}
@media (max-width:900px){.cx-sim{grid-template-columns:1fr;grid-template-areas:"map" "side" "route" "chart"}
.cx-dispatch,.cx-three{grid-template-columns:1fr}}
</style>"""


def _image(svg):
    return f"<img alt='' src='data:image/svg+xml;base64,{b64encode(svg.encode()).decode()}'>"


def _card(title, body, extra=""):
    return f"<div class='cx-card {extra}'><div class='cx-title'>{title}</div>{body}</div>"


def _rows(rows):
    """rows: (name, value text, fraction, colour)."""
    return "".join(
        f"<div class='cx-row'><em>{name}</em><i><u style='width:{min(max(share, 0), 1) * 100:.0f}%;"
        f"background:{color}'></u></i><strong>{value}</strong></div>"
        for name, value, share, color in rows
    )


def route_map(city_wards, city, stops):
    """Close-up of one city with numbered crew stops in visit order."""
    where = positions({city: city_wards})
    xs, ys = [p[0] for p in where.values()], [p[1] for p in where.values()]
    left, top = min(xs) - 40, min(ys) - 45
    width, height = max(xs) - left + 40, max(ys) - top + 35
    if width < height * 1.6:  # keep a landscape frame
        left -= (height * 1.6 - width) / 2
        width = height * 1.6
    svg = [f"<svg xmlns='http://www.w3.org/2000/svg' viewBox='{left:.0f} {top:.0f} {width:.0f} "
           f"{height:.0f}'><rect x='{left:.0f}' y='{top:.0f}' width='{width:.0f}' "
           f"height='{height:.0f}' fill='#17171A'/>"]
    for n in range(-8, 24):
        x = left + n * 34
        svg.append(f"<path d='M{x:.0f} {top:.0f}l{height * .35:.0f} {height:.0f}' stroke='#29282C'/>")
        y = top + n * 30
        svg.append(f"<path d='M{left:.0f} {y:.0f}l{width:.0f} {-width * .08:.0f}' stroke='#29282C'/>")
    if len(stops) > 1:
        points = " ".join(f"{where[w][0]:.0f},{where[w][1]:.0f}" for w in stops)
        for line_width, color in ((9, "#3E4527"), (4, "#BCD070")):
            svg.append(f"<polyline points='{points}' fill='none' stroke='{color}' "
                       f"stroke-width='{line_width}' stroke-linejoin='round' stroke-linecap='round'/>")
    for ward, (x, y) in where.items():
        if ward not in stops:
            svg.append(f"<circle cx='{x:.0f}' cy='{y:.0f}' r='5' fill='#57535C'/>")
    for number, ward in enumerate(stops, start=1):
        x, y = where[ward]
        svg.append(f"<circle cx='{x:.0f}' cy='{y:.0f}' r='13' fill='#F2A33A' stroke='#fff' "
                   f"stroke-width='2'/><text x='{x:.0f}' y='{y + 4:.0f}' text-anchor='middle' "
                   f"font-family='Arial' font-size='13' font-weight='800' fill='#17120A'>{number}</text>"
                   f"<text x='{x:.0f}' y='{y - 18:.0f}' text-anchor='middle' font-family='Arial' "
                   f"font-size='11' font-weight='700' fill='#F1ECE3'>W{ward.rsplit('_', 1)[-1]}</text>")
    svg.append("</svg>")
    return _image("".join(svg))


def trend_chart(labels, series):
    """series: (name, values, colour). Small SVG line chart."""
    peak = max((max(values) for _, values, _ in series), default=0) or 1
    xs = [52 + i * (300 / max(len(labels) - 1, 1)) for i in range(len(labels))]
    svg = ["<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 390 244' font-family='Arial'>"
           "<rect width='390' height='244' fill='#17171A'/>"]
    for step in range(5):
        y = 188 - step * 40
        svg.append(f"<path d='M40 {y}H372' stroke='#2F2D31'/><text x='34' y='{y + 4}' "
                   f"text-anchor='end' font-size='10' fill='#8F897F'>{peak * step / 4:.0f}</text>")
    for x, label in zip(xs, labels):
        svg.append(f"<text x='{x:.0f}' y='207' text-anchor='middle' font-size='11' "
                   f"fill='#BDB6AC'>{label}</text>")
    for index, (name, values, color) in enumerate(series):
        coords = [(x, 188 - value / peak * 160) for x, value in zip(xs, values)]
        line = " ".join(f"{x:.0f},{y:.0f}" for x, y in coords)
        svg.append(f"<polygon points='{xs[0]:.0f},188 {line} {xs[-1]:.0f},188' fill='{color}' opacity='.1'/>"
                   f"<polyline points='{line}' fill='none' stroke='{color}' stroke-width='3'/>")
        svg += [f"<circle cx='{x:.0f}' cy='{y:.0f}' r='4.5' fill='{color}'/>" for x, y in coords]
        lx = 52 + index * 150
        svg.append(f"<rect x='{lx}' y='222' width='11' height='11' rx='3' fill='{color}'/>"
                   f"<text x='{lx + 17}' y='232' font-size='11' fill='#D9D2C7'>{name}</text>")
    svg.append("</svg>")
    return _image("".join(svg))


def simulator_console(subtitle, map_html, kpis, impact_rows, route_title, route_html,
                      chart_title, chart_html):
    """kpis: (label, value, note, colour)."""
    tiles = "".join(
        f"<div class='cx-kpi'><span>{label}</span><b style='color:{color}'>{value}</b>"
        f"<small>{note}</small></div>" for label, value, note, color in kpis
    )
    return (
        f"{CSS}<div class='cx'><div class='cx-head'><b>Mosquito Control Operations</b>"
        f"<span>{subtitle}</span></div><div class='cx-grid cx-sim'>"
        f"<div class='cx-card cx-map'>{map_html}</div>"
        f"<div class='cx-side'><div class='cx-kpis'>{tiles}</div>"
        f"{_card('Impact by ward', _rows(impact_rows))}</div>"
        f"{_card(route_title, route_html, 'cx-route')}"
        f"{_card(chart_title, chart_html, 'cx-chart')}</div></div>"
    )


def dispatch_console(subtitle, totals, replies, channels, city_table, phone_html):
    """
    totals: (label, value, note, colour) x3. replies: bar rows.
    channels: (title, value, note, colour). city_table: ready HTML.
    """
    big = "".join(
        f"<div class='cx-big' style='background:linear-gradient(135deg,{color},{color}B8)'>"
        f"<span>{label}</span><b>{value}</b><small>{note}</small></div>"
        for label, value, note, color in totals
    )
    cards = "".join(
        _card(title, f"<b style='color:{color}'>{value}</b><small>{note}</small>", "cx-channel")
        for title, value, note, color in channels
    )
    return (
        f"{CSS}<div class='cx'><div class='cx-head'><b>Ward Alert Broadcast</b>"
        f"<span>{subtitle}</span></div><div class='cx-grid cx-dispatch'><div class='cx-main'>"
        f"<div class='cx-three'>{big}</div>{_card('Reply status', _rows(replies))}"
        f"<div class='cx-three'>{cards}</div>{city_table}</div>"
        f"<div>{phone_html}</div></div></div>"
    )

