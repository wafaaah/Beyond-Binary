"""Offline schematic operations map drawn as SVG (not real geography)."""
from base64 import b64encode

# zone: centre x, centre y, columns, outline
ZONES = {
    "Gazipur": (300, 105, 3, "M190 50L330 30L420 80L400 160L270 180L180 130Z"),
    "Dhaka North": (215, 295, 5, "M60 215L240 190L385 235L370 375L180 395L55 325Z"),
    "Dhaka South": (240, 500, 5, "M85 430L270 405L400 445L385 575L190 595L70 525Z"),
    "Narayanganj": (545, 465, 3, "M465 400L590 385L650 455L605 545L485 535L440 470Z"),
    "Chattogram": (815, 360, 4, "M705 240L860 225L955 310L935 465L790 500L690 400Z"),
}


def positions(ward_ids_by_city):
    """Fixed schematic position for every ward, spread inside its city zone."""
    result = {}
    for city, ids in ward_ids_by_city.items():
        cx, cy, columns, _ = ZONES.get(city, (500, 300, 5, ""))
        ids = sorted(ids)
        rows = (len(ids) + columns - 1) // columns
        for n, ward in enumerate(ids):
            row, col = divmod(n, columns)
            jitter_x = (n * 37) % 17 - 8
            jitter_y = (n * 53) % 15 - 7
            result[ward] = (cx + (col - (columns - 1) / 2) * 55 + jitter_x,
                            cy + (row - (rows - 1) / 2) * 44 + jitter_y)
    return result


def _text(x, y, text, size=13, color="#F6F0FA", weight=700, anchor="middle"):
    return (f"<text x='{x:.0f}' y='{y:.0f}' font-family='Arial' font-size='{size}' "
            f"font-weight='{weight}' fill='{color}' text-anchor='{anchor}'>{text}</text>")


def operations_map(wards, layers, alerts=(), routes=(), selected=None):
    """
    wards: dicts with id, city, color, heat (0 to 1), crews.
    layers: set of 'heat', 'wards', 'route', 'labels'.
    alerts: (title, text, color). routes: lists of ward ids in visit order.
    """
    by_city = {}
    for ward in wards:
        by_city.setdefault(ward["city"], []).append(ward["id"])
    where = positions(by_city)
    svg = ["<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 1000 620'>",
           "<rect width='1000' height='620' fill='#201229'/>"]
    # decorative street grid, river and highways
    for x in range(-200, 1100, 46):
        svg.append(f"<path d='M{x} 0L{x + 190} 620' stroke='#2C193A' stroke-width='1'/>")
    for y in range(20, 640, 42):
        svg.append(f"<path d='M0 {y}L1000 {y - 70}' stroke='#2C193A' stroke-width='1'/>")
    svg.append("<path d='M470 -10C420 110 520 180 470 290S380 390 430 480 640 570 660 640' "
               "fill='none' stroke='#26343A' stroke-width='22' stroke-linecap='round'/>")
    for road in ("M0 190C180 170 360 230 560 200S860 120 1000 150",
                 "M120 620C220 470 330 410 520 390S800 430 1000 560",
                 "M300 0C330 140 250 330 270 620"):
        svg.append(f"<path d='{road}' fill='none' stroke='#3B214D' stroke-width='4'/>")
    for city in by_city:
        if city in ZONES:
            svg.append(f"<path d='{ZONES[city][3]}' fill='#F4B647' fill-opacity='.05' "
                       "stroke='#8A7348' stroke-width='1.5' stroke-dasharray='7 5'/>")
    if "heat" in layers:
        svg.append("<defs>")
        for i, ward in enumerate(wards):
            svg.append(f"<radialGradient id='h{i}'><stop offset='0' stop-color='{ward['color']}' "
                       f"stop-opacity='{.15 + .6 * ward['heat']:.2f}'/><stop offset='1' "
                       f"stop-color='{ward['color']}' stop-opacity='0'/></radialGradient>")
        svg.append("</defs>")
        for i, ward in enumerate(wards):
            x, y = where[ward["id"]]
            svg.append(f"<circle cx='{x:.0f}' cy='{y:.0f}' r='{22 + 30 * ward['heat']:.0f}' "
                       f"fill='url(#h{i})'/>")
    if "route" in layers:
        for route in routes:
            if len(route) > 1:
                points = " ".join(f"{where[w][0]:.0f},{where[w][1]:.0f}" for w in route)
                svg.append(f"<polyline points='{points}' fill='none' stroke='#BCD070' "
                           "stroke-width='3' stroke-dasharray='9 6' stroke-linejoin='round'/>")
    if "wards" in layers:
        for ward in wards:
            x, y = where[ward["id"]]
            number = ward["id"].rsplit("_", 1)[-1]
            if ward["crews"]:
                svg.append(f"<path d='M{x:.0f} {y + 16:.0f}c-26-22-18-44 0-44s26 22 0 44z' "
                           "fill='#BCD070' stroke='#150C1C' stroke-width='2'/>")
                svg.append(_text(x, y - 8, number, 12, "#14140F"))
                svg.append(f"<circle cx='{x + 17:.0f}' cy='{y - 28:.0f}' r='10' fill='#fff'/>")
                svg.append(_text(x + 17, y - 24, ward["crews"], 12, "#14140F"))
            else:
                svg.append(f"<circle cx='{x:.0f}' cy='{y:.0f}' r='12' fill='#281634' "
                           f"stroke='{ward['color']}' stroke-width='3'/>")
                svg.append(_text(x, y + 4, number, 10))
    if selected in where:
        x, y = where[selected]
        svg.append(f"<circle cx='{x:.0f}' cy='{y:.0f}' r='21' fill='none' stroke='#FFFFFF' "
                   "stroke-width='3'/>"
                   f"<circle cx='{x:.0f}' cy='{y:.0f}' r='29' fill='none' stroke='#F4B647' "
                   "stroke-width='2' stroke-dasharray='5 4'/>")
    if "labels" in layers:
        for city in by_city:
            if city in ZONES:
                outline = ZONES[city][3]
                top = min(float(p.split()[1]) for p in
                          outline[1:-1].split("L"))
                cx = ZONES[city][0]
                svg.append(f"<rect x='{cx - 68}' y='{top - 16:.0f}' width='136' height='22' rx='11' "
                           "fill='#150C1C' stroke='#5E3F74'/>")
                svg.append(_text(cx, top - 1, city.upper(), 11, "#F5C84C"))
    for i, (title, text, color) in enumerate(alerts):
        y = 16 + i * 68
        svg.append(f"<rect x='690' y='{y}' width='294' height='58' rx='10' fill='#160C1D' "
                   f"fill-opacity='.93' stroke='{color}'/>")
        svg.append(f"<rect x='690' y='{y}' width='7' height='58' rx='3' fill='{color}'/>")
        svg.append(_text(710, y + 23, title, 13, color, 800, "start"))
        svg.append(_text(710, y + 43, text, 13, "#E6E0D6", 400, "start"))
    svg.append(_text(16, 606, "Schematic layout: not real geography", 12, "#8D63AB", 400, "start"))
    svg.append("</svg>")
    data = b64encode("".join(svg).encode()).decode()
    return ("<div class='dw-map'><img alt='Schematic ward operations map' "
            f"src='data:image/svg+xml;base64,{data}'></div>")
