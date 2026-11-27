"""Opening scene: mosquito control in original SVG and CSS art. No video, works offline."""
from base64 import b64encode

import streamlit as st

SECONDS = 5.2


def _mosquito(body="#F6F0FA", wing="#BFE0EA"):
    """A mosquito centred on (0, 0), about 200 wide."""
    legs = ("M-14 8L-60 -8L-84 26M-8 14L-44 40L-52 78M6 16L10 52L-8 80"
            "M18 14L46 40L62 74M16 6L56 -4L82 22M-4 12L-24 48L-34 66")
    return (
        f"<path d='{legs}' fill='none' stroke='{body}' stroke-width='4' stroke-linecap='round'/>"
        f"<g class='wing'><ellipse cx='-10' cy='-34' rx='46' ry='15' fill='{wing}' opacity='.75' "
        "transform='rotate(42 -10 -34)'/></g>"
        f"<g class='wing w2'><ellipse cx='36' cy='-34' rx='46' ry='15' fill='{wing}' opacity='.75' "
        "transform='rotate(-28 36 -34)'/></g>"
        f"<ellipse cx='42' cy='20' rx='44' ry='15' fill='{body}' transform='rotate(24 42 20)'/>"
        "<path d='M30 6l-8 22M50 14l-8 22M68 24l-7 18' stroke='#F2762E' stroke-width='5'/>"
        f"<circle cx='-4' cy='0' r='19' fill='{body}'/><circle cx='-30' cy='-8' r='14' fill='{body}'/>"
        "<circle cx='-35' cy='-11' r='5' fill='#E5484D'/>"
        f"<path d='M-40 -2L-76 38M-34 -20L-56 -48M-24 -21L-30 -54' stroke='{body}' stroke-width='3.5' "
        "fill='none' stroke-linecap='round'/>"
    )


def _fogger():
    """Hand held fogging machine, shaded to look three dimensional."""
    def ramp(name, colors):
        stops = "".join(f"<stop offset='{i / (len(colors) - 1):.2f}' stop-color='{c}'/>"
                        for i, c in enumerate(colors))
        return f"<linearGradient id='{name}' x1='0' y1='0' x2='0' y2='1'>{stops}</linearGradient>"

    defs = "".join([
        ramp("body", ["#8A4B12", "#FFD98A", "#F4B647", "#C9761F", "#5E300B"]),
        ramp("steel", ["#4A4552", "#F7F5FA", "#B9B3C4", "#6F687A", "#2E2A35"]),
        ramp("dark", ["#5A5064", "#2C2533", "#0F0B14"]),
        ramp("red", ["#FFB27A", "#F2762E", "#8E3A10"]),
        "<radialGradient id='jet' cx='0' cy='.5' r='1'><stop offset='0' stop-color='#fff'/>"
        "<stop offset='.45' stop-color='#E4EEDB' stop-opacity='.55'/>"
        "<stop offset='.95' stop-color='#E4EEDB' stop-opacity='0'/></radialGradient>",
    ])
    holes = "".join(f"<ellipse cx='{x}' cy='{y}' rx='4' ry='3' fill='#2E2A35' opacity='.8'/>"
                    for x in range(190, 292, 17) for y in (48, 62))
    rings = "".join(f"<rect x='{x}' y='34' width='9' height='45' rx='4' fill='url(#steel)'/>"
                    for x in (166, 298))
    return (
        f"<defs>{defs}</defs><g class='gun'><g transform='translate(60 430) rotate(-16) scale(1.15)'>"
        "<ellipse cx='130' cy='196' rx='170' ry='16' fill='#000' opacity='.35'/>"
        # carry handle and grip
        "<path d='M18 18C30 -48 128 -48 146 14' fill='none' stroke='url(#steel)' stroke-width='13' "
        "stroke-linecap='round'/>"
        "<path d='M52 100L30 178Q40 192 70 186L98 104Z' fill='url(#dark)'/>"
        "<path d='M96 104q22 30-8 40' fill='none' stroke='#8F879C' stroke-width='6'/>"
        # fuel tank
        "<rect x='20' y='84' width='122' height='44' rx='22' fill='url(#steel)'/>"
        # engine body with end cap and highlight
        "<rect x='-8' y='6' width='176' height='96' rx='44' fill='url(#body)'/>"
        "<ellipse cx='20' cy='54' rx='28' ry='47' fill='url(#dark)'/>"
        "<ellipse cx='20' cy='54' rx='17' ry='30' fill='none' stroke='#F4B647' stroke-width='4'/>"
        "<path d='M20 30V78M6 54H34' stroke='#8F879C' stroke-width='3'/>"
        "<rect x='46' y='16' width='100' height='12' rx='6' fill='#fff' opacity='.45'/>"
        "<rect x='60' y='44' width='72' height='26' rx='6' fill='url(#dark)'/>"
        "<text x='96' y='62' text-anchor='middle' font-size='15' font-weight='800' fill='#F4B647'>VECTOR</text>"
        # filler cap
        "<rect x='86' y='-8' width='38' height='20' rx='6' fill='url(#red)'/>"
        "<ellipse cx='105' cy='-8' rx='19' ry='6' fill='#FFB27A'/>"
        # barrel with heat shield and nozzle
        "<rect x='160' y='40' width='158' height='33' rx='12' fill='url(#steel)'/>"
        f"{holes}{rings}"
        "<path d='M306 38L334 30V84L306 75Z' fill='url(#red)'/>"
        "<ellipse cx='334' cy='57' rx='10' ry='27' fill='url(#dark)' stroke='#FFB27A' stroke-width='3'/>"
        "<path class='jet' d='M338 46L560 -34Q600 55 560 150L338 68Z' fill='url(#jet)'/>"
        "</g></g>"
    )


def _scene():
    css = (
        "*{transform-box:fill-box;transform-origin:center}"
        ".wing{animation:flap .09s linear infinite alternate}.w2{animation-delay:.045s}"
        "@keyframes flap{to{transform:scaleY(.45)}}"
        ".fly{animation:fly 1.5s cubic-bezier(.2,.7,.3,1) both,fall 1.1s ease-in 2.65s forwards}"
        "@keyframes fly{0%{transform:translate(620px,-300px) scale(.4)}45%{transform:translate(170px,60px)}"
        "70%{transform:translate(-60px,-50px)}100%{transform:none}}"
        "@keyframes fall{20%{transform:translate(0,-26px) rotate(-18deg)}"
        "100%{transform:translate(60px,360px) rotate(200deg) scale(.5);opacity:0}}"
        ".buzz{animation:buzz .16s linear infinite alternate}@keyframes buzz{to{transform:translate(5px,-6px)}}"
        ".gun{animation:gun .8s ease-out both}@keyframes gun{from{transform:translateX(-420px)}}"
        ".puff{opacity:0;animation:puff 1.5s ease-out forwards}"
        "@keyframes puff{0%{opacity:0;transform:translate(0,0) scale(.2)}25%{opacity:.8}"
        "100%{opacity:0;transform:translate(var(--x),var(--y)) scale(3.4)}}"
        ".aim{opacity:0;animation:aim .6s ease-out 1.3s forwards,off .3s 3s forwards}"
        "@keyframes aim{from{opacity:0;transform:scale(2.6) rotate(120deg)}to{opacity:1;transform:none}}"
        "@keyframes off{from{opacity:1}to{opacity:0}}"
        ".swarm{animation:vanish .7s ease-in forwards}"
        "@keyframes vanish{60%{opacity:.9}100%{opacity:0;transform:translateY(90px) rotate(140deg) scale(.2)}}"
        ".jet{opacity:0;animation:jet .12s linear 1.1s 18 alternate}"
        "@keyframes jet{from{opacity:.35;transform:scaleY(.82)}to{opacity:.8;transform:scaleY(1.08)}}"
        ".jet{transform-origin:left center}"
        ".flash{opacity:0;animation:flash .8s ease-out 2.65s}"
        "@keyframes flash{0%{opacity:.9;transform:scale(.2)}100%{opacity:0;transform:scale(2.2)}}"
        ".shield{opacity:0;animation:stamp .7s cubic-bezier(.2,1.6,.4,1) 3.4s forwards}"
        "@keyframes stamp{from{opacity:0;transform:scale(2.4)}to{opacity:1;transform:none}}"
        ".t1{opacity:0;animation:up .6s ease 3.75s forwards}.t2{opacity:0;animation:up .6s ease 4.1s forwards}"
        "@keyframes up{from{opacity:0;transform:translateY(30px)}to{opacity:1;transform:none}}"
    )
    svg = [
        "<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 1200 675' font-family='Arial'>",
        f"<style>{css}</style>",
        "<defs><radialGradient id='mist'><stop offset='0' stop-color='#EAFBD2' stop-opacity='.95'/>"
        "<stop offset='1' stop-color='#A9BC5F' stop-opacity='0'/></radialGradient>"
        "<radialGradient id='smoke'><stop offset='0' stop-color='#FFFFFF' stop-opacity='.9'/>"
        "<stop offset='.55' stop-color='#D8D2E0' stop-opacity='.45'/>"
        "<stop offset='1' stop-color='#D8D2E0' stop-opacity='0'/></radialGradient>"
        "<radialGradient id='glow'><stop offset='0' stop-color='#F4B647' stop-opacity='.5'/>"
        "<stop offset='1' stop-color='#F4B647' stop-opacity='0'/></radialGradient></defs>",
        "<circle cx='600' cy='290' r='330' fill='url(#glow)'/>",
    ]
    for i, height in enumerate([90, 150, 110, 200, 130, 240, 120, 170, 95, 215, 140, 105,
                                185, 125, 160, 100, 135, 85, 175, 115]):
        x = i * 61
        svg.append(f"<rect x='{x}' y='{675 - height}' width='52' height='{height}' fill='#100918'/>")
        for y in range(690 - height, 650, 26):
            if (i * 7 + y) % 4:
                svg.append(f"<rect x='{x + 10 + (y % 3) * 11}' y='{y}' width='8' height='9' "
                           "fill='#F4B647' opacity='.5'/>")
    # small swarm that disappears in the mist
    for x, y, s, d in [(420, 170, .36, 1.7), (800, 200, .3, 2.0), (720, 420, .26, 2.2),
                       (470, 400, .32, 2.45), (860, 330, .22, 2.6), (360, 280, .24, 2.1)]:
        svg.append(f"<g transform='translate({x} {y}) scale({s})'><g class='swarm' "
                   f"style='animation-delay:{d}s'><g class='buzz'>{_mosquito('#D2C3DD')}</g></g></g>")
    # target lock
    svg.append("<g transform='translate(600 290)'><g class='aim' fill='none' stroke='#E5484D' stroke-width='5'>"
               "<circle r='132'/><circle r='108' stroke-dasharray='14 12' stroke-width='3'/>"
               "<path d='M0 -165V-105M0 105V165M-165 0H-105M105 0H165'/></g></g>")
    svg.append("<g transform='translate(600 290) scale(1.25)'><g class='fly'><g class='buzz'>"
               f"{_mosquito()}</g></g></g>")
    svg.append(_fogger())
    # billowing fog that rolls from the nozzle towards the target
    for i in range(64):
        dx, dy = 80 + (i * 53) % 290, -250 + (i * 71) % 240
        svg.append(f"<circle class='puff' cx='{398 + i % 4 * 5}' cy='{454 + i % 3 * 6}' "
                   f"r='{16 + i % 6 * 6}' fill='url(#{'mist' if i % 3 else 'smoke'})' "
                   f"style='--x:{dx}px;--y:{dy}px;animation-delay:{1.15 + i * .031:.2f}s'/>")
    svg.append("<g transform='translate(600 290)'><circle class='flash' r='110' fill='#fff'/></g>")
    # shield with the mosquito crossed out
    svg.append(
        "<g transform='translate(600 262)'><g class='shield'>"
        "<path d='M0 -150L128 -102V6C128 90 68 140 0 168C-68 140 -128 90 -128 6V-102Z' "
        "fill='#251530' stroke='#F4B647' stroke-width='9'/>"
        f"<g transform='scale(.72)'>{_mosquito()}</g>"
        "<circle r='90' fill='none' stroke='#E5484D' stroke-width='13'/>"
        "<path d='M-64 -64L64 64' stroke='#E5484D' stroke-width='13'/></g></g>")
    svg.append("<g class='t1'><text x='600' y='522' text-anchor='middle' font-size='76' font-weight='800' "
               "fill='#F6F0FA' letter-spacing='2'>Dengue<tspan fill='#F4B647'>Watch</tspan></text></g>"
               "<g class='t2'><text x='600' y='566' text-anchor='middle' font-size='26' font-weight='700' "
               "fill='#F6F0FA' letter-spacing='6'>DETECT  &#183;  CONTROL  &#183;  PROTECT</text></g></svg>")
    return "data:image/svg+xml;base64," + b64encode("".join(svg).encode()).decode()


CSS = """<style>
.sp{position:fixed;inset:0;z-index:1000001;display:flex;align-items:center;justify-content:center;
pointer-events:none;background:radial-gradient(circle at 50% 42%,#3B2050 0,#170D21 65%);
animation:sp-out .7s ease __DELAY__s forwards}
.sp img{width:min(100vw,177vh);height:auto;max-height:100vh}
.sp-bar{position:absolute;left:0;bottom:0;height:6px;width:0;
background:linear-gradient(90deg,#F4B647,#F2762E);animation:sp-load __DELAY__s linear forwards}
@keyframes sp-load{to{width:100%}}
@keyframes sp-out{to{opacity:0;visibility:hidden}}
@media (prefers-reduced-motion:reduce){.sp{display:none}}
</style>""".replace("__DELAY__", str(SECONDS))


def show_intro():
    """Play the intro once for each browser session. It never blocks clicks."""
    if st.session_state.get("intro_seen"):
        return
    st.session_state["intro_seen"] = True
    st.markdown(
        CSS + "<div class='sp' aria-hidden='true'>"
        f"<img src='{_scene()}' alt=''><div class='sp-bar'></div></div>",
        unsafe_allow_html=True,
    )
