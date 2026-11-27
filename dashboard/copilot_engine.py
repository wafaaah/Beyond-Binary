"""Offline question answering for the Copilot page (rule based, no external AI)."""
import difflib
import re
import unicodedata

from ml.allocation import allocate, forecast
from ml.routing import estimate_capacity, route_overflow
from ml.simulator import prepare, rank_roi

CITIES = {
    "Chattogram": ("chattogram", "chittagong", "ctg", "ccc", "চট্টগ্রাম"),
    "Dhaka North": ("dhaka north", "north dhaka", "dncc", "ঢাকা উত্তর", "uttor"),
    "Dhaka South": ("dhaka south", "south dhaka", "dscc", "ঢাকা দক্ষিণ", "dokkhin"),
    "Gazipur": ("gazipur", "gcc", "গাজীপুর"),
    "Narayanganj": ("narayanganj", "ncc", "নারায়ণগঞ্জ"),
}
RISK_BN = {"Low": "কম", "Medium": "মাঝারি", "High": "বেশি", "Critical": "খুব বেশি"}
ADVICE = {
    "Low": "সতর্ক থাকুন এবং ঘরের আশেপাশে পানি জমতে দেবেন না।",
    "Medium": "আজই বাড়ির চারপাশ দেখুন এবং জমা পানি ফেলে দিন।",
    "High": "মশার কামড় থেকে বাঁচুন। জ্বর হলে দ্রুত ডাক্তার দেখান।",
    "Critical": "এখনই সাবধান হোন। জ্বর হলে দেরি না করে ডাক্তার দেখান ও পরীক্ষা করান।",
}

QUESTIONS = {
    "লাইভ তথ্য": {
        "top": "কোন ওয়ার্ডগুলোতে ঝুঁকি সবচেয়ে বেশি?",
        "deficit": "কোন কোন জিনিসের ঘাটতি আছে?",
        "city": "কোন শহরে কত রোগী হতে পারে?",
        "overflow": "কোন ওয়ার্ডে বেড কম পড়বে?",
        "roi": "স্প্রে টিম কোথায় আগে পাঠানো উচিত?",
    },
    "ওয়েবসাইট": {
        "about": "এই ওয়েবসাইট কী কাজ করে?",
        "model": "পূর্বাভাস কীভাবে করা হয়?",
        "levels": "ঝুঁকির মাত্রা কীভাবে ঠিক হয়?",
        "allocation": "সরঞ্জাম কীভাবে ভাগ করা হয়?",
        "export": "রিপোর্ট বা SMS কীভাবে পাবো?",
        "offline": "ইন্টারনেট ছাড়া কি চলে?",
        "live": "এটা কি আজকের তথ্য?",
    },
    "ডেঙ্গু সচেতনতা": {
        "symptoms": "ডেঙ্গুর লক্ষণ কী কী?",
        "danger": "কখন হাসপাতালে যেতে হবে?",
        "prevent": "ডেঙ্গু কীভাবে প্রতিরোধ করবো?",
        "care": "জ্বর হলে কী করবো?",
    },
}

KEYWORDS = {
    "top": "top|highest|most risk|risky|beshi jhuki|jhuki beshi|সবচেয়ে বেশি|ঝুঁকিপূর্ণ|critical ward",
    "deficit": "deficit|shortage|stock|saline|kit|crew|ghatti|ঘাটতি|স্যালাইন কত|কিট|সরঞ্জামের অভাব",
    "city": "city|cases|total|summary|shohor|rogi|কত রোগী|শহর|আক্রান্ত",
    "overflow": "overflow|bed|transfer|capacity|বেড|শয্যা|স্থানান্তর",
    "roi": "roi|spray|fogging|team|simulator|what if|স্প্রে|টিম|ফগিং|সিমুলেটর",
    "about": "website|about|purpose|dashboard|project|denguewatch|ওয়েবসাইট|কী কাজ",
    "model": "model|forecast|predict|accuracy|accurate|mae|machine learning|পূর্বাভাস|মডেল|কতটা সঠিক",
    "levels": "risk level|threshold|medium|level|মাত্রা|ঝুঁকির স্তর",
    "allocation": "allocation|allocate|priority|distribute|ভাগ|বণ্টন|অগ্রাধিকার",
    "export": "export|download|sms|whatsapp|pdf|print|report|brief|dispatch|রিপোর্ট|ডাউনলোড",
    "offline": "offline|internet|api|network|ইন্টারনেট|অফলাইন",
    "live": "live|today|real time|ajker|date|আজকের|আজ|লাইভ|তারিখ",
    "symptoms": "symptom|lokkhon|লক্ষণ|উপসর্গ|র‍্যাশ|মাথাব্যথা",
    "danger": "danger|emergency|hospital|bleeding|blood|rokto|breathing|হাসপাতাল|বিপদ|রক্ত|শ্বাসকষ্ট|পেটব্যথা|বারবার বমি",
    "prevent": "prevent|protect|mosquito|protirodh|mosha|প্রতিরোধ|মশা|জমা পানি|বাঁচ",
    "care": "fever|medicine|treatment|paracetamol|jor|osudh|জ্বর|ওষুধ|ঔষধ|চিকিৎসা|প্যারাসিটামল",
}

STATIC = {
    "about": "DengueWatch ওয়ার্ডভিত্তিক ডেঙ্গুর পূর্বাভাস দেয় এবং স্যালাইন, টেস্ট কিট, বেড ও স্প্রে টিম "
             "কোথায় আগে দরকার তা দেখায়। বাম পাশের মেনু থেকে Command Center, Resources, Overflow, "
             "Simulator, Dispatch ও Public Advisory পেজ খোলা যায়।",
    "model": "লোকাল machine learning মডেল (HistGradientBoosting, Poisson) আবহাওয়া ও আগের রোগীর তথ্য থেকে "
             "২, ৩ ও ৪ সপ্তাহ পরের রোগী অনুমান করে। টেস্ট ডেটায় গড় ভুল (MAE) ১.৫৪, ১.৬৩ ও ১.৫৭; "
             "শুধু আগের সপ্তাহের মান ধরলে ২.০৪, ২.৩৩ ও ২.৫৮।",
    "levels": "পূর্বাভাসে সাপ্তাহিক রোগী ১-এর কম হলে **কম**, ৫-এর কম হলে **মাঝারি**, ১০-এর কম হলে **বেশি**, "
              "আর ১০ বা তার বেশি হলে **খুব বেশি** ঝুঁকি।",
    "allocation": "আগে ঝুঁকির মাত্রা, তারপর জনঘনত্ব, তারপর পূর্বাভাসের রোগী দেখে ওয়ার্ডের ক্রম ঠিক হয়। "
                  "প্রতিটি শহরের স্টক সেই ক্রমে ভাগ হয়। স্প্রে টিম আগে প্রতিটি দরকারি ওয়ার্ডে একটি করে, "
                  "তারপর বাকিগুলো ক্রম অনুযায়ী দেওয়া হয়।",
    "export": "**Dispatch** পেজ থেকে SMS, WhatsApp বার্তা ও প্রিন্টযোগ্য রিপোর্ট ডাউনলোড করা যায়।",
    "offline": "হ্যাঁ। মডেল ও ডেটা এই অ্যাপের সাথেই থাকে, তাই লোকাল কম্পিউটারে ইন্টারনেট ছাড়া চলে। "
               "এই Copilot-ও কোনো বাইরের AI বা API ব্যবহার করে না।",
    "symptoms": "হঠাৎ তীব্র জ্বর, তীব্র মাথাব্যথা, চোখের পেছনে ব্যথা, পেশি ও জোড়ায় ব্যথা, "
                "ত্বকে র‍্যাশ, বমি বমি ভাব বা বমি। এমন হলে ডাক্তার দেখান।",
    "danger": "**দেরি না করে হাসপাতালে যান** যদি থাকে: তীব্র পেটব্যথা, বারবার বমি, নাক বা মাড়ি থেকে রক্ত, "
              "বমি বা পায়খানায় রক্ত, খুব দুর্বল বা অস্থির লাগা, শ্বাসকষ্ট। জ্বর কমার পরেও এগুলো হতে পারে। "
              "জরুরি: **৯৯৯**",
    "prevent": "সপ্তাহে অন্তত একবার জমা পানি ফেলুন, পানির পাত্র ঢেকে রাখুন, দিনে ও রাতে ঘুমানোর সময় মশারি, "
               "রিপেলেন্ট ও ফুলহাতা জামা ব্যবহার করুন।",
    "care": "বিশ্রাম নিন, প্রচুর পানি, স্যালাইন ও তরল খাবার খান এবং ডাক্তার দেখিয়ে পরীক্ষা করান। "
            "জ্বর-ব্যথায় নির্দেশমতো প্যারাসিটামল; **অ্যাসপিরিন বা আইবুপ্রোফেন খাবেন না।** "
            "বিপদচিহ্ন দেখলে সাথে সাথে হাসপাতালে যান (৯৯৯)।",
}
HEALTH = {"symptoms", "danger", "prevent", "care"}
BN_DIGITS = str.maketrans("০১২৩৪৫৬৭৮৯", "0123456789")


def normalize(text):
    text = unicodedata.normalize("NFC", str(text)).lower().translate(BN_DIGITS)
    return " ".join(re.sub(r"[?!।,.:;_\-()'\"]", " ", text).split())


def find_city(text):
    for city, names in CITIES.items():
        for name in names:
            name = normalize(name)
            pattern = rf"\b{name}\b" if name.isascii() else re.escape(name)
            if re.search(pattern, text):
                return city
    return None


def find_ward(text):
    word = normalize("ওয়ার্ড")
    match = (re.search(rf"(?:ward|{word})\s*(?:no|number|নম্বর|নং)?\s*(\d{{1,2}})\b", text)
             or re.search(r"\b(?:ccc|dncc|dscc|gcc|ncc)\s*(\d{1,2})\b", text))
    if not match and find_city(text):
        match = re.search(r"\b(\d{1,2})\b", text)  # e.g. "gazipur 3"
    return int(match.group(1)) if match else None


def match_intent(question):
    """Return the best intent name, or None if nothing matches."""
    text = normalize(question)
    for group in QUESTIONS.values():
        for intent, canned in group.items():
            if text == normalize(canned):
                return intent
    words = text.split()
    scores = {}
    for intent, keywords in KEYWORDS.items():
        score = 0
        for keyword in map(normalize, keywords.split("|")):
            if keyword.isascii():
                if re.search(rf"\b{keyword}s?\b", text):
                    score += len(keyword)
                elif len(keyword) >= 6 and difflib.get_close_matches(keyword, words, 1, 0.82):
                    score += len(keyword) - 2
            elif keyword in text:
                score += len(keyword)
        if score:
            scores[intent] = score
    if "danger" in scores and "overflow" not in scores:  # safety first
        return "danger"
    return max(scores, key=scores.get) if scores else None


def _wards(frame):
    table = frame[["ward_id", "city", "risk_level", "predicted_cases"]].copy()
    table["risk_level"] = table["risk_level"].map(RISK_BN)
    table.columns = ["ওয়ার্ড", "শহর", "ঝুঁকি", "পূর্বাভাস রোগী"]
    return table


def answer(question, data, week, horizon=2, stock=70, crews=20):
    """Return (markdown text, optional table) for a question."""
    text = normalize(question)
    city, number = find_city(text), find_ward(text)
    intent = match_intent(question)
    if intent in HEALTH:
        note = "\n\n_সাধারণ তথ্য, চিকিৎসকের পরামর্শের বিকল্প নয়।_"
        return STATIC[intent] + note, None
    if number is None and intent in STATIC:
        return STATIC[intent], None
    if number is None and intent is None and city is None:
        return ("দুঃখিত, প্রশ্নটি বুঝতে পারিনি। উপরের কোনো প্রশ্নে ক্লিক করুন, অথবা এভাবে লিখুন: "
                "“ঢাকা উত্তর ওয়ার্ড ৩ এর ঝুঁকি”, “saline shortage”, “ডেঙ্গুর লক্ষণ”।"), None

    plan = allocate(forecast(data, week, horizon), stock, crews)
    target = plan["target_date"].iloc[0].strftime("%d-%m-%Y")
    scope = f"**{target}** সপ্তাহের পূর্বাভাস (পুরোনো তথ্যের ডেমো, স্টক {stock}%, টিম {crews})"
    if city:
        scope += f", শহর: {city}"
    view = plan[plan["city"] == city] if city else plan

    if number is not None:
        found = view[view["ward_id"].str.endswith(f"_{number:02d}")]
        if found.empty:
            return f"{number} নম্বর ওয়ার্ড পাওয়া যায়নি।", None
        order = list(RISK_BN)
        worst = max(found["risk_level"], key=order.index)
        table = _wards(found)[["ওয়ার্ড", "শহর", "ঝুঁকি"]]
        hint = "" if city else " শহরের নামসহ লিখলে শুধু আপনার ওয়ার্ড দেখাবে।"
        return (f"{scope}\n\n{number} নম্বর ওয়ার্ডে ঝুঁকি: **{RISK_BN[worst]}**"
                f"{'' if len(found) == 1 else ' (শহরগুলোর মধ্যে সর্বোচ্চ)'}।{hint}\n\n"
                f"**করণীয়:** {ADVICE[worst]}"), table

    if intent == "deficit":
        items = [("saline_bags", "স্যালাইন ব্যাগ"), ("diagnostic_kits", "টেস্ট কিট"),
                 ("hospital_beds", "বেড"), ("crews", "স্প্রে টিম")]
        lines = [f"- {label}: **{int(view[f'{key}_deficit'].sum())}** টি কম" for key, label in items]
        if city:
            lines[-1] += " (টিম সব শহরের জন্য একসাথে বণ্টন হয়)"
        return f"{scope}\n\n" + "\n".join(lines), None

    if intent == "overflow":
        wards, moves = route_overflow(plan, estimate_capacity(data, week))
        if city:
            wards, moves = wards[wards["city"] == city], moves[moves["city"] == city]
        head = (f"{scope}\n\nঅতিরিক্ত রোগী: **{int(wards['overflow'].sum())}**, সরানো যাবে: "
                f"**{int(wards['sent_out'].sum())}**, জায়গা হবে না: **{int(wards['unplaced'].sum())}**। "
                "(বেড ক্ষমতা আমাদের অনুমান।)")
        if moves.empty:
            return head, None
        moves = moves[["from_ward", "to_ward", "patients"]]
        moves.columns = ["যে ওয়ার্ড থেকে", "যে ওয়ার্ডে", "রোগী"]
        return head, moves

    if intent == "roi":
        rows, models = prepare(data, week)
        ranking = rank_roi(rows, models)
        if city:
            ranking = ranking[ranking["city"] == city]
        table = ranking[["ward_id", "city", "cases_prevented"]].head(5)
        table.columns = ["ওয়ার্ড", "শহর", "প্রতি টিমে কম রোগী (২-৪ সপ্তাহ)"]
        return ("মডেলের হিসাবে এই ওয়ার্ডগুলোতে একটি টিম পাঠালে সবচেয়ে বেশি লাভ হতে পারে। "
                "এটি অনুমানভিত্তিক, বাস্তবে প্রমাণিত ফল নয়।"), table

    if intent == "live":
        return f"না, এটি আজকের সতর্কবার্তা নয়। এখন দেখানো হচ্ছে {scope}।", None

    if intent == "city" or (intent is None and city):
        totals = view.groupby("city", as_index=False)["predicted_cases"].sum().round(1)
        totals.columns = ["শহর", "পূর্বাভাস রোগী"]
        return f"{scope}\n\nমোট রোগী (পূর্বাভাস): **{view['predicted_cases'].sum():.0f}**", totals

    high = int(view["risk_level"].isin(["High", "Critical"]).sum())
    return (f"{scope}\n\n**{high}** টি ওয়ার্ডে বেশি বা খুব বেশি ঝুঁকি। সবার উপরের ওয়ার্ডগুলো:",
            _wards(view.sort_values("predicted_cases", ascending=False).head(5)))
