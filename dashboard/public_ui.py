"""Offline Bangla infographic for the public page. All artwork is inline SVG."""
from base64 import b64encode

SKIN, HAIR, INK = "#E8B48C", "#2B2230", "#1F3A4A"
RED, TEAL, BLUE, WATER = "#D93A3F", "#0F7C86", "#2F6FB2", "#5BB8E8"


def _svg(body, bg="#BFE3E6"):
    svg = (
        "<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'>"
        "<defs><clipPath id='c'><circle cx='50' cy='50' r='48'/></clipPath>"
        "<radialGradient id='g' cx='35%' cy='28%' r='80%'><stop offset='0' stop-color='#fff'/>"
        f"<stop offset='1' stop-color='{bg}'/></radialGradient></defs>"
        "<circle cx='50' cy='50' r='48' fill='url(#g)'/>"
        f"<g clip-path='url(#c)'>{body}</g></svg>"
    )
    return "data:image/svg+xml;base64," + b64encode(svg.encode()).decode()


def _line(d, color=INK, width=3, fill="none"):
    return (f"<path d='{d}' fill='{fill}' stroke='{color}' stroke-width='{width}' "
            "stroke-linecap='round' stroke-linejoin='round'/>")


def _person(shirt=TEAL, mouth="M44 55q6 -4 12 0", eyes="open", skin=SKIN):
    """Adult head and shoulders."""
    eye = (_line("M39 41h7M54 41h7", HAIR, 2.5) if eyes == "closed" else
           f"<circle cx='43' cy='42' r='2.2' fill='{HAIR}'/>"
           f"<circle cx='57' cy='42' r='2.2' fill='{HAIR}'/>")
    return (
        f"<path d='M16 100c2-24 16-31 34-31s32 7 34 31z' fill='{shirt}'/>"
        f"<path d='M43 58h14v13q-7 7-14 0z' fill='{skin}'/>"
        f"<ellipse cx='50' cy='42' rx='19' ry='23' fill='{skin}'/>"
        f"<path d='M30 41c-3-33 44-34 40 0-3-9-6-13-9-16-8 7-20 8-27 5-2 3-3 6-4 11z' fill='{HAIR}'/>"
        + _line("M38 36l9 1M62 36l-9 1", HAIR, 2) + eye
        + _line("M50 43l-2 7h4", "#B9805C", 1.8) + _line(mouth, "#8A3B34", 2.4)
    )


def _hand(x, y, angle=0):
    return (f"<g transform='translate({x} {y}) rotate({angle})'>"
            f"<rect x='-7' y='-9' width='14' height='19' rx='7' fill='#D99E76'/>"
            f"<rect x='-5' y='8' width='10' height='30' rx='4' fill='{SKIN}'/></g>")


def _pain(x, y):
    return _line(f"M{x} {y}l7-5M{x+2} {y+7}h9M{x} {y+14}l7 5", RED, 3)


def _ban(cx=50, cy=50, r=38, width=7):
    k = r * 0.707
    return (f"<circle cx='{cx}' cy='{cy}' r='{r}' fill='none' stroke='{RED}' stroke-width='{width}'/>"
            + _line(f"M{cx-k} {cy-k}L{cx+k} {cy+k}", RED, width))


def _mosquito():
    legs = _line("M44 50L24 40 15 55M46 55L30 66 26 82M54 56L58 72 50 86"
                 "M60 54L76 66 84 80M58 48L78 38 88 46", INK, 2)
    return (
        "<ellipse cx='42' cy='34' rx='21' ry='8' fill='#BFE0EA' opacity='.9' transform='rotate(35 42 34)'/>"
        "<ellipse cx='62' cy='33' rx='21' ry='8' fill='#BFE0EA' opacity='.9' transform='rotate(-30 62 33)'/>"
        + legs +
        f"<ellipse cx='64' cy='58' rx='20' ry='8' fill='{INK}' transform='rotate(28 64 58)'/>"
        + _line("M60 51l-4 10M69 56l-4 11M77 61l-3 9", "#fff", 2.2) +
        f"<circle cx='45' cy='48' r='9' fill='{INK}'/><circle cx='33' cy='44' r='7' fill='{INK}'/>"
        + _line("M28 47L13 66", INK, 2.5) + _line("M31 38L22 25M36 38L34 23", INK, 1.5)
    )


PREVENT = [
    (_svg(f"<path d='M30 34l36 12-12 34-30-10z' fill='#C4673F'/>"
          + _line("M28 33l41 14", "#9C4A2A", 6)
          + _line("M68 52q14 8 12 26M74 48q18 6 20 20", WATER, 4)
          + f"<ellipse cx='78' cy='88' rx='20' ry='5' fill='{WATER}'/>"),
     "টব, টায়ার ও পাত্রের জমা পানি ফেলে দিন"),
    (_svg(f"<rect x='28' y='38' width='44' height='46' rx='6' fill='{BLUE}'/>"
          + _line("M29 52h42M29 68h42", "#1E4F85", 3)
          + f"<rect x='22' y='28' width='56' height='11' rx='5' fill='{INK}'/>"
          f"<rect x='43' y='19' width='14' height='10' rx='4' fill='{INK}'/>"),
     "পানির পাত্র সবসময় ঢেকে রাখুন"),
    (_svg(f"<rect x='18' y='68' width='64' height='12' fill='#8A5A3B'/>"
          f"<rect x='22' y='58' width='56' height='12' rx='4' fill='{TEAL}'/>"
          "<rect x='25' y='52' width='17' height='9' rx='4' fill='#fff'/>"
          + _line("M50 14L18 80M50 14L82 80M50 14L36 80M50 14L64 80M50 14v66"
                  "M37 40h26M29 55h42", "#6C8E99", 1.4)),
     "দিনে ও রাতে ঘুমানোর সময় মশারি ব্যবহার করুন"),
    (_svg(f"<rect x='30' y='42' width='26' height='44' rx='6' fill='{TEAL}'/>"
          f"<rect x='35' y='30' width='16' height='13' fill='{INK}'/>"
          f"<rect x='47' y='24' width='13' height='9' rx='3' fill='{INK}'/>"
          "<rect x='34' y='56' width='18' height='16' rx='3' fill='#fff'/>"
          + "".join(f"<circle cx='{x}' cy='{y}' r='{r}' fill='{WATER}'/>"
                    for x, y, r in [(67, 28, 2.5), (75, 22, 3), (76, 33, 2.5),
                                    (85, 27, 3.5), (83, 40, 2)])),
     "মশা তাড়ানোর ওষুধ বা রিপেলেন্ট ব্যবহার করুন"),
    (_svg(f"<path d='M36 22l14 8 14-8 18 12 8 44-13 3-9-31v36H32V50l-9 31-13-3 8-44z' fill='{BLUE}'/>"
          + _line("M50 31v52", "#fff", 2) + _line("M38 23l12 13 12-13", "#fff", 3)),
     "ফুলহাতা জামা ও লম্বা পায়জামা পরুন"),
]

SYMPTOMS = [
    (_svg(_person(eyes="closed")
          + "<rect x='73' y='18' width='9' height='44' rx='4.5' fill='#fff' stroke='#1F3A4A' stroke-width='2'/>"
          + _line("M77.5 30v30", RED, 4) + f"<circle cx='77.5' cy='66' r='9' fill='{RED}'/>", "#FFD3C4"),
     "হঠাৎ তীব্র জ্বর"),
    (_svg(_person(eyes="closed") + _hand(29, 32, 38) + _pain(74, 16), "#FFD3C4"),
     "তীব্র মাথাব্যথা"),
    (_svg(_line("M12 52Q50 18 88 52Q50 82 12 52z", INK, 3, "#fff")
          + "<circle cx='50' cy='50' r='15' fill='#6B4A33'/><circle cx='50' cy='50' r='7' fill='#14100E'/>"
          "<circle cx='55' cy='45' r='3' fill='#fff'/>"
          + _line("M14 30Q50 4 86 30", HAIR, 5)
          + _line("M24 74l-7 9M50 79v12M76 74l7 9", RED, 4), "#FFD3C4"),
     "চোখের পেছনে ব্যথা"),
    (_svg(_line("M38 2L50 52", SKIN, 24) + _line("M50 52L40 100", SKIN, 19)
          + "<circle cx='50' cy='52' r='17' fill='#EF6B5E' opacity='.75'/>"
          "<circle cx='50' cy='52' r='8' fill='#D93A3F'/>" + _pain(72, 38), "#FFD3C4"),
     "পেশি ও হাড়ের জোড়ায় ব্যথা"),
    (_svg(_line("M8 76L92 28", SKIN, 36)
          + "".join(f"<circle cx='{x}' cy='{y}' r='{r}' fill='{RED}' opacity='.85'/>"
                    for x, y, r in [(26, 66, 3), (34, 56, 2.2), (39, 68, 3.5),
                                    (46, 51, 3), (53, 60, 2.2), (58, 45, 3.5),
                                    (66, 52, 2.5), (71, 35, 3), (50, 70, 2),
                                    (20, 75, 2.2), (78, 40, 2)]), "#FFD3C4"),
     "ত্বকে লালচে দানা বা র‍্যাশ"),
    (_svg(_person(mouth="M43 56q3 -3 7 0t7 0", eyes="closed", skin="#CFC08F")
          + _hand(51, 60, -62), "#FFD3C4"),
     "বমি বমি ভাব বা বমি"),
]

DANGERS = [
    (_svg(f"<path d='M26 6h48l-6 44 6 50H26l6-50z' fill='{TEAL}'/>"
          "<circle cx='50' cy='60' r='19' fill='#fff' opacity='.5'/>"
          f"<circle cx='50' cy='60' r='11' fill='{RED}'/>"
          + _hand(30, 66, -72) + _pain(72, 46), "#F9BFC2"),
     "তীব্র পেটব্যথা"),
    (_svg(_person(mouth="M44 54q6 9 12 0z", eyes="closed", skin="#CFC08F")
          + _line("M52 60q18 4 20 26", "#8DAA3A", 7)
          + "<circle cx='75' cy='93' r='6' fill='#8DAA3A'/>", "#F9BFC2"),
     "বারবার বমি"),
    (_svg(f"<path d='M50 10C64 32 76 47 76 63a26 26 0 0 1-52 0c0-16 12-31 26-53z' fill='{RED}'/>"
          + _line("M36 64q1 13 13 16", "#fff", 4), "#F9BFC2"),
     "নাক, মাড়ি, বমি বা পায়খানায় রক্ত"),
    (_svg(_person(shirt="#6D7F8A", eyes="closed")
          + _line("M72 20q16 8 4 18t4 18", "#6D4AA0", 3.5)
          + _line("M24 18q-14 9-2 19", "#6D4AA0", 3.5), "#F9BFC2"),
     "খুব দুর্বল বা অস্থির লাগা"),
    (_svg(_line("M50 12v34M50 40L38 52M50 40L62 52", INK, 5)
          + "<path d='M40 32C20 38 12 68 18 84c10 8 24 0 26-8V40z' fill='#E8747C'/>"
          "<path d='M60 32c20 6 28 36 22 52-10 8-24 0-26-8V40z' fill='#E8747C'/>", "#F9BFC2"),
     "শ্বাসকষ্ট"),
]

CARE = [
    (_svg(f"<path d='M26 30h30l-4 52H30z' fill='#fff' stroke='{INK}' stroke-width='3'/>"
          f"<path d='M29 46h24l-3 33H32z' fill='{WATER}'/>"
          + "<path d='M54 58h36q-2 26-18 26T54 58z' fill='#E39A3B'/>"
          + _line("M64 48q-6-8 0-15M77 48q-6-8 0-15", "#8C8C8C", 3)),
     "প্রচুর পানি, স্যালাইন ও তরল খাবার"),
    (_svg("<rect x='12' y='66' width='76' height='12' fill='#8A5A3B'/>"
          f"<circle cx='30' cy='55' r='11' fill='{SKIN}'/>"
          + _line("M24 54h7", HAIR, 2.5)
          + f"<path d='M38 66q4-20 24-16t26 16z' fill='{TEAL}'/>"
          + _line("M50 10L12 66M50 10L88 66M50 10v38", "#6C8E99", 1.5)),
     "মশারির ভেতরে বিশ্রাম"),
    (_svg(f"<g transform='rotate(-35 50 50)'><rect x='18' y='37' width='64' height='27' rx='13' "
          f"fill='#fff' stroke='{INK}' stroke-width='3'/>"
          + _line("M50 38v25", INK, 3) + "</g>" + _line("M66 76l7 7 14-17", "#1E9E5A", 7)),
     "জ্বর-ব্যথায় শুধু প্যারাসিটামল, নির্দেশমতো"),
    (_svg("<rect x='34' y='34' width='32' height='46' rx='7' fill='#C98B3C'/>"
          "<rect x='38' y='22' width='24' height='13' rx='3' fill='#fff' stroke='#1F3A4A' stroke-width='2'/>"
          "<rect x='38' y='47' width='24' height='20' fill='#fff'/>" + _ban(r=40)),
     "অ্যাসপিরিন বা আইবুপ্রোফেন খাবেন না"),
]

CSS = """<style>
.dg{font-family:'Hind Siliguri','Noto Sans Bengali','Nirmala UI',FreeSans,sans-serif;color:#17343F;
background:linear-gradient(180deg,#F4FAFB,#FFF8F3);border-radius:28px;overflow:hidden;
box-shadow:0 24px 60px rgba(0,0,0,.35);margin-bottom:18px}
.dg *{box-sizing:border-box}
.dg-hero{position:relative;display:flex;align-items:center;justify-content:space-between;gap:20px;
padding:42px 40px 74px;color:#fff;overflow:hidden;
background:radial-gradient(circle at 85% 20%,#E4575C 0,transparent 42%),linear-gradient(125deg,#06303A,#0F7C86 55%,#8E1F3C)}
.dg-hero>div,.dg-hero>span{position:relative;z-index:2}
.dg-tag{display:inline-block;background:rgba(255,255,255,.16);border:1px solid rgba(255,255,255,.35);
border-radius:40px;padding:5px 16px;font-size:15px;font-weight:600;margin-bottom:14px}
.dg-title{font-size:clamp(30px,5vw,52px);font-weight:800;line-height:1.3;text-shadow:0 4px 18px rgba(0,0,0,.35)}
.dg-title b{color:#FFD166}
.dg-sub{font-size:clamp(17px,2.4vw,22px);opacity:.92;margin-top:8px}
.dg-orb{flex:none;border-radius:50%;padding:12px;background:rgba(255,255,255,.18);
box-shadow:0 0 0 14px rgba(255,255,255,.08),0 0 60px rgba(255,209,102,.45);animation:dgfloat 4s ease-in-out infinite}
.dg-orb img{display:block;width:clamp(92px,17vw,180px)}
.dg-drop{position:absolute;border-radius:50%;background:rgba(255,255,255,.09);animation:dgfloat 6s ease-in-out infinite}
.dg-wave{position:absolute;left:0;bottom:-1px;width:100%;height:46px;z-index:1}
.dg-facts{display:grid;grid-template-columns:repeat(auto-fit,minmax(210px,1fr));gap:14px;padding:6px 22px 4px}
.dg-fact{background:#fff;border-radius:18px;padding:16px 18px;border-left:6px solid #FFB020;
box-shadow:0 8px 22px rgba(15,60,75,.10);font-size:17px;font-weight:700;line-height:1.55}
.dg-fact small{display:block;font-size:13px;color:#0F7C86;font-weight:700}
.dg-sec{margin:22px 18px 0;background:#fff;border-radius:24px;padding:20px 10px 12px;
box-shadow:0 10px 30px rgba(15,60,75,.10);border-top:6px solid var(--a)}
.dg-head{display:table;margin:0 auto 8px;padding:8px 28px;border-radius:40px;color:#fff;
font-size:23px;font-weight:800;text-align:center;line-height:1.5;
background:linear-gradient(100deg,var(--a),var(--b));box-shadow:0 8px 18px rgba(0,0,0,.18)}
.dg-row{display:flex;flex-wrap:wrap;justify-content:center}
.dg-item{flex:1 1 145px;max-width:210px;text-align:center;padding:16px 8px;border-radius:20px;
transition:transform .25s,box-shadow .25s,background .25s;animation:dgin .7s ease both}
.dg-item:hover{transform:translateY(-8px);background:var(--s);box-shadow:0 14px 28px rgba(15,60,75,.16)}
.dg-ring{width:132px;height:132px;margin:0 auto 12px;border-radius:50%;padding:4px;
background:linear-gradient(140deg,var(--a),var(--b));box-shadow:0 10px 22px rgba(15,60,75,.22);transition:transform .25s}
.dg-ring img{display:block;width:100%;height:100%;border-radius:50%;border:4px solid #fff;background:#fff}
.dg-item:hover .dg-ring{transform:scale(1.08) rotate(-3deg)}
.dg-item .dg-label{font-size:17px;font-weight:700;line-height:1.55}
.dg-teal{--a:#0F7C86;--b:#35C2B0;--s:#EAF8F6}
.dg-coral{--a:#E4572E;--b:#FFA14A;--s:#FFF1E8}
.dg-red{--a:#B71F35;--b:#F0525F;--s:#FDECEE;background:linear-gradient(180deg,#FFF0F1,#fff 55%)}
.dg-blue{--a:#2457A6;--b:#42A5E8;--s:#EBF4FD}
.dg-red .dg-ring{animation:dgring 2s ease-out infinite}
.dg-foot{display:flex;flex-wrap:wrap;gap:14px;justify-content:space-between;align-items:center;
margin-top:24px;padding:26px 30px;color:#fff;font-size:21px;font-weight:800;
background:linear-gradient(120deg,#06303A,#0F5F68)}
.dg-call{background:linear-gradient(100deg,#B71F35,#F0525F);border-radius:40px;padding:10px 28px;
animation:dgring 2s ease-out infinite}
@keyframes dgin{from{opacity:0;transform:translateY(22px)}to{opacity:1;transform:none}}
@keyframes dgfloat{50%{transform:translateY(-12px)}}
@keyframes dgring{0%{box-shadow:0 0 0 0 rgba(215,50,70,.55)}100%{box-shadow:0 0 0 16px rgba(215,50,70,0)}}
@media (max-width:560px){.dg-hero{flex-direction:column-reverse;text-align:center;padding:30px 20px 64px}
.dg-item{flex-basis:46%}.dg-ring{width:112px;height:112px}.dg-sec{margin-left:10px;margin-right:10px}
.dg-foot{justify-content:center;text-align:center}}
@media (prefers-reduced-motion:reduce){.dg *{animation:none!important;transition:none!important}}
</style>"""

FACTS = [
    ("জেনে রাখুন", "এডিস মশা সাধারণত দিনের বেলায় কামড়ায়"),
    ("মনে রাখুন", "অল্প জমা পানিতেও এডিস মশা ডিম পাড়ে"),
    ("প্রতি সপ্তাহে", "অন্তত একবার জমা পানি ফেলে পাত্র পরিষ্কার করুন"),
]


def _section(title, items, tone):
    cells = "".join(
        f"<div class='dg-item' style='animation-delay:{i * 0.1:.1f}s'>"
        f"<div class='dg-ring'><img src='{image}' alt=''></div>"
        f"<div class='dg-label'>{label}</div></div>"
        for i, (image, label) in enumerate(items)
    )
    return (f"<div class='dg-sec dg-{tone}'><div class='dg-head'>{title}</div>"
            f"<div class='dg-row'>{cells}</div></div>")


def poster_html():
    hero = _svg(_mosquito() + _ban(r=43, width=6), "#DDF3F5")
    drops = "".join(
        f"<i class='dg-drop' style='left:{x}%;top:{y}%;width:{d}px;height:{d}px;animation-delay:{t}s'></i>"
        for x, y, d, t in [(4, 12, 46, 0), (42, 70, 24, 1), (60, 8, 34, 2), (91, 62, 70, .5), (26, 4, 18, 3)]
    )
    wave = ("<svg class='dg-wave' viewBox='0 0 1200 60' preserveAspectRatio='none'>"
            "<path d='M0 32Q150 0 300 28T600 30T900 26T1200 22V60H0z' fill='#F4FAFB'/></svg>")
    wave_uri = "data:image/svg+xml;base64," + b64encode(
        wave.replace("<svg class='dg-wave'", "<svg xmlns='http://www.w3.org/2000/svg'").encode()).decode()
    facts = "".join(f"<div class='dg-fact'><small>{k}</small>{v}</div>" for k, v in FACTS)
    html = (
        f"<div class='dg'><div class='dg-hero'>{drops}<div>"
        "<span class='dg-tag'>ডেঙ্গু সচেতনতা</span>"
        "<div class='dg-title'>ডেঙ্গু চিনুন,<br><b>সময়মতো ব্যবস্থা নিন</b></div>"
        "<div class='dg-sub'>সচেতন থাকলে পরিবার নিরাপদ থাকে</div></div>"
        f"<span class='dg-orb'><img src='{hero}' alt=''></span>"
        f"<img class='dg-wave' src='{wave_uri}' alt=''></div>"
        f"<div class='dg-facts'>{facts}</div>"
        + _section("ডেঙ্গুর লক্ষণ", SYMPTOMS, "coral")
        + _section("বিপদচিহ্ন: দেরি না করে হাসপাতালে যান<br><small>জ্বর কমার পরেও হতে পারে</small>", DANGERS, "red")
        + _section("প্রতিরোধে করণীয়", PREVENT, "teal")
        + _section("জ্বর হলে করণীয়", CARE, "blue")
        + "<div class='dg-foot'><span>প্রয়োজনে দ্রুত ডাক্তারের পরামর্শ নিন</span>"
        "<span class='dg-call'>জরুরি: ৯৯৯</span></div></div>"
    )
    return CSS + html


def risk_card_html(level, label, advice, color):
    """Gradient risk banner with a four step meter."""
    steps = [("Low", "কম"), ("Medium", "মাঝারি"), ("High", "বেশি"), ("Critical", "খুব বেশি")]
    current = [name for name, _ in steps].index(level)
    meter = "".join(
        "<div style='flex:1;text-align:center;font-size:14px;font-weight:700;"
        f"opacity:{1 if i <= current else .5}'><div style='height:12px;border-radius:12px;margin-bottom:6px;"
        f"background:{'#fff' if i <= current else 'rgba(255,255,255,.4)'}'></div>{name}</div>"
        for i, (_, name) in enumerate(steps)
    )
    return (
        "<div style=\"font-family:'Hind Siliguri','Noto Sans Bengali','Nirmala UI',FreeSans,sans-serif;"
        "color:#fff;border-radius:24px;padding:26px 28px;text-align:center;"
        f"background:linear-gradient(120deg,rgba(0,0,0,.55),rgba(0,0,0,.18)),{color};"
        f"box-shadow:0 14px 36px {color}66;text-shadow:0 2px 8px rgba(0,0,0,.45)\">"
        "<div style='font-size:15px'>এই ওয়ার্ডের পূর্বাভাস</div>"
        f"<div style='font-size:40px;font-weight:800;line-height:1.4'>{label}</div>"
        f"<div style='font-size:19px;margin-bottom:18px'>{advice}</div>"
        f"<div style='display:flex;gap:8px;max-width:620px;margin:auto'>{meter}</div></div>"
    )
