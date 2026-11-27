"""Offline question answering for the public Copilot (rule based, no external AI)."""
import difflib
import re
import unicodedata

import public_en

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

FAQ = [
    ("আমার এলাকা", "my_area", "আমার এলাকায় ডেঙ্গুর ঝুঁকি কত?",
     "my area|amar elaka|amar ward|আমার এলাকা|আমার ওয়ার্ড",
     "উপরের বক্সে শহর ও ওয়ার্ড নম্বর লিখে খুঁজুন, যেমন “ঢাকা উত্তর ৩” বা “Gazipur 2”।"),
    ("আমার এলাকা", "top", "কোন ওয়ার্ডগুলোতে ঝুঁকি সবচেয়ে বেশি?",
     "highest|most risk|risky|top ward|beshi jhuki|jhuki beshi|সবচেয়ে বেশি|ঝুঁকিপূর্ণ", None),
    ("আমার এলাকা", "low", "কোন ওয়ার্ডগুলোতে ঝুঁকি সবচেয়ে কম?",
     "lowest|safest|safe area|kom jhuki|jhuki kom|সবচেয়ে কম|নিরাপদ এলাকা", None),
    ("আমার এলাকা", "high_action", "আমার এলাকায় ঝুঁকি বেশি হলে কী করবো?",
     "jhuki beshi hole|if risk is high|ঝুঁকি বেশি হলে",
     "বাড়ি ও আশেপাশের জমা পানি ফেলুন, মশারি ও রিপেলেন্ট ব্যবহার করুন, ফুলহাতা জামা পরুন। "
     "কারও জ্বর হলে দ্রুত ডাক্তার দেখান ও পরীক্ষা করান।"),
    ("আমার এলাকা", "ward_help", "আমার ওয়ার্ড নম্বর কীভাবে জানবো?",
     "ward number|ward kivabe|which ward am i|ওয়ার্ড নম্বর",
     "স্থানীয় ওয়ার্ড কাউন্সিলর কার্যালয় বা সিটি কর্পোরেশন থেকে ওয়ার্ড নম্বর জেনে নিন।"),
    ("আমার এলাকা", "cities", "কোন কোন শহরের তথ্য আছে?",
     "which cit|available cit|kon shohor|কোন কোন শহর|কোন শহর",
     "চট্টগ্রাম (১০টি ওয়ার্ড), ঢাকা উত্তর (২০), ঢাকা দক্ষিণ (২০), গাজীপুর (৫) ও নারায়ণগঞ্জ (৫)।"),
    ("ডেঙ্গু সম্পর্কে", "what", "ডেঙ্গু কী?",
     "what is dengue|dengue ki|dengue mane|ডেঙ্গু কী|ডেঙ্গু কি",
     "ডেঙ্গু একটি ভাইরাসজনিত রোগ, যা প্রধানত সংক্রমিত এডিস মশার কামড়ে ছড়ায়। অনেকের হালকা উপসর্গ হয় "
     "বা হয় না, তবে কারও কারও রোগ গুরুতর হতে পারে।"),
    ("ডেঙ্গু সম্পর্কে", "spread", "ডেঙ্গু কীভাবে ছড়ায়? ছোঁয়াচে কি?",
     "spread|transmi|contagious|choyache|chorai|ছড়ায়|ছোঁয়াচে|সংক্রমণ",
     "প্রধানত সংক্রমিত এডিস মশার কামড়ে ছড়ায়। স্পর্শ বা পাশে থাকার মাধ্যমে সরাসরি মানুষ থেকে মানুষে ছড়ায় না। "
     "গর্ভাবস্থায় মা থেকে শিশুর সংক্রমণ সম্ভব, তবে কম দেখা যায়।"),
    ("ডেঙ্গু সম্পর্কে", "bite_time", "এডিস মশা কখন কামড়ায়?",
     "bite|biting|kamray|kokhon kamr|কামড়ায়|কামড়",
     "এডিস মশা দিনের বেলায় সক্রিয় থাকে। তাই দিনেও সতর্ক থাকুন, দিনে ঘুমালেও মশারি ব্যবহার করুন।"),
    ("ডেঙ্গু সম্পর্কে", "breeding", "এডিস মশা কোথায় ডিম পাড়ে?",
     "breed|egg|dim pare|ডিম পাড়ে|ডিম|বংশ",
     "পানি জমে থাকে এমন পাত্র ও আবর্জনায়, যেমন টব, টায়ার, ড্রাম, খোলা বোতল বা কৌটা।"),
    ("ডেঙ্গু সম্পর্কে", "again", "একবার ডেঙ্গু হলে কি আবার হতে পারে?",
     "again|second time|twice|abar|আবার|দ্বিতীয়বার",
     "হ্যাঁ, আবার হতে পারে। দ্বিতীয়বার সংক্রমণে গুরুতর ডেঙ্গুর ঝুঁকি বাড়ে, তাই আরও সতর্ক থাকুন।"),
    ("লক্ষণ ও পরীক্ষা", "symptoms", "ডেঙ্গুর লক্ষণ কী কী?",
     "symptom|lokkhon|লক্ষণ|উপসর্গ|র‍্যাশ|মাথাব্যথা|শরীর ব্যথা",
     "হঠাৎ তীব্র জ্বর, তীব্র মাথাব্যথা, চোখের পেছনে ব্যথা, পেশি ও জোড়ায় ব্যথা, ত্বকে র‍্যাশ, "
     "বমি বমি ভাব বা বমি। এমন হলে ডাক্তার দেখান।"),
    ("লক্ষণ ও পরীক্ষা", "incubation", "মশা কামড়ানোর কতদিন পর লক্ষণ দেখা দেয়?",
     "how many days|incubation|how long|koto din|kotodin|কতদিন|কত দিন",
     "সাধারণত ৪ থেকে ১০ দিন পর লক্ষণ শুরু হয় এবং ২ থেকে ৭ দিন থাকে।"),
    ("লক্ষণ ও পরীক্ষা", "test", "ডেঙ্গু পরীক্ষা কখন ও কীভাবে করবো?",
     "test|ns1|diagnos|porikkha|পরীক্ষা|টেস্ট",
     "জ্বর হলে শুরুতেই ডাক্তার দেখান। প্রথম সপ্তাহে ভাইরাস বা অ্যান্টিজেন (যেমন NS1) পরীক্ষা করা যায়; "
     "পরে অ্যান্টিবডি পরীক্ষা লাগতে পারে। কোন পরীক্ষা দরকার তা ডাক্তার ঠিক করবেন।"),
    ("লক্ষণ ও পরীক্ষা", "danger", "কখন হাসপাতালে যেতে হবে?",
     "danger|emergency|hospital|bleed|blood|rokto|breath|হাসপাতাল|বিপদ|রক্ত|শ্বাস|পেটব্যথা|পেট ব্যথা|বারবার বমি",
     "**দেরি না করে হাসপাতালে যান** যদি থাকে: তীব্র পেটব্যথা, বারবার বমি, দ্রুত শ্বাস, নাক বা মাড়ি থেকে রক্ত, "
     "বমি বা পায়খানায় রক্ত, অস্থিরতা, খুব দুর্বলতা বা পিপাসা, ফ্যাকাশে ঠান্ডা ত্বক। "
     "জ্বর কমার পরেও এগুলো হতে পারে। জরুরি: **৯৯৯**"),
    ("চিকিৎসা ও যত্ন", "care", "জ্বর হলে কী করবো?",
     "fever|treatment|jor|জ্বর|চিকিৎসা",
     "ডাক্তার দেখান ও পরীক্ষা করান, বিশ্রাম নিন এবং প্রচুর তরল খান। জ্বর-ব্যথায় নির্দেশমতো প্যারাসিটামল। "
     "বিপদচিহ্ন দেখলে সাথে সাথে হাসপাতালে যান (৯৯৯)।"),
    ("চিকিৎসা ও যত্ন", "medicine", "কোন ওষুধ খাওয়া যাবে না?",
     "medicine|drug|aspirin|ibuprofen|painkiller|paracetamol|osudh|ওষুধ|ঔষধ|ব্যথানাশক|প্যারাসিটামল",
     "**অ্যাসপিরিন, আইবুপ্রোফেন ও এ ধরনের ব্যথানাশক খাবেন না**, এতে রক্তক্ষরণের ঝুঁকি বাড়ে। "
     "জ্বর-ব্যথায় প্যারাসিটামল ব্যবহার করা যায়; মাত্রা ডাক্তার বা ফার্মাসিস্টের কাছে জেনে নিন।"),
    ("চিকিৎসা ও যত্ন", "food", "ডেঙ্গু হলে কী খাবো?",
     "food|eat|drink|diet|khabo|khabar|খাবো|খাব|খাবার|পানীয়",
     "প্রচুর পানি, খাবার স্যালাইন, স্যুপ ও অন্যান্য তরল এবং সহজে হজম হয় এমন খাবার খান। "
     "অন্য কোনো অসুখ থাকলে ডাক্তারের পরামর্শ নিন।"),
    ("চিকিৎসা ও যত্ন", "papaya", "পেঁপে পাতার রস বা ঘরোয়া চিকিৎসা কি কাজ করে?",
     "papaya|home remed|pepe|পেঁপে|ঘরোয়া",
     "ডেঙ্গুর কোনো নির্দিষ্ট ওষুধ নেই। ঘরোয়া উপায়ের ওপর ভরসা করে হাসপাতালে যেতে দেরি করবেন না; "
     "কিছু খাওয়ার আগে ডাক্তারকে জানান।"),
    ("চিকিৎসা ও যত্ন", "platelet", "প্লাটিলেট কমে গেলে কী করবো?",
     "platelet|plate let|প্লাটিলেট|অণুচক্রিকা",
     "দ্রুত ডাক্তারের তত্ত্বাবধানে থাকুন। প্লাটিলেট দেওয়া লাগবে কিনা তা ডাক্তার ঠিক করবেন। "
     "বিপদচিহ্ন থাকলে সাথে সাথে হাসপাতালে যান।"),
    ("চিকিৎসা ও যত্ন", "after_fever", "জ্বর কমে গেলে কি আমি নিরাপদ?",
     "fever gone|after fever|jor kom|জ্বর কমে|জ্বর চলে|জ্বর সেরে",
     "সবসময় নয়। **গুরুতর লক্ষণ অনেক সময় জ্বর কমার পরে দেখা দেয়।** তখনও বিপদচিহ্ন খেয়াল রাখুন।"),
    ("চিকিৎসা ও যত্ন", "child", "বাচ্চার জ্বর হলে কী করবো?",
     "child|baby|kid|bacha|baccha|বাচ্চা|শিশু",
     "দেরি না করে ডাক্তার দেখান। নিজে থেকে ওষুধ বা মাত্রা ঠিক করবেন না; অ্যাসপিরিন বা আইবুপ্রোফেন দেবেন না। "
     "বিপদচিহ্ন দেখলে সাথে সাথে হাসপাতালে নিন (৯৯৯)।"),
    ("চিকিৎসা ও যত্ন", "pregnant", "গর্ভবতী মায়ের ডেঙ্গু হলে কী করবো?",
     "pregnan|gorvoboti|গর্ভ",
     "দ্রুত ডাক্তার দেখান। গর্ভাবস্থায় ডেঙ্গু মা ও শিশুর ওপর প্রভাব ফেলতে পারে, তাই চিকিৎসকের তত্ত্বাবধান জরুরি।"),
    ("প্রতিরোধ", "prevent", "ডেঙ্গু কীভাবে প্রতিরোধ করবো?",
     "prevent|protect|mosquito|protirodh|mosha|প্রতিরোধ|মশা|বাঁচ",
     "সপ্তাহে অন্তত একবার জমা পানি ফেলুন, পানির পাত্র ঢেকে রাখুন, মশারি, রিপেলেন্ট ও ফুলহাতা জামা ব্যবহার করুন।"),
    ("প্রতিরোধ", "home", "বাড়িতে মশা কমাবো কীভাবে?",
     "at home|house|bari|ghor|বাড়ি|ঘরে|জমা পানি",
     "টব, টায়ার, ড্রাম ও অন্য পাত্রের জমা পানি ফেলুন, পানির পাত্র ঢেকে রাখুন ও সপ্তাহে একবার পরিষ্কার করুন, "
     "আবর্জনা সরান এবং সম্ভব হলে জানালায় জাল লাগান।"),
    ("প্রতিরোধ", "patient_net", "ডেঙ্গু রোগীকে কি মশারির ভেতরে রাখতে হবে?",
     "patient|rogi|রোগী|রোগীকে",
     "হ্যাঁ। রোগীকে কামড়ানো মশা সংক্রমিত হয়ে অন্যদের মধ্যে ভাইরাস ছড়াতে পারে।"),
    ("প্রতিরোধ", "vaccine", "ডেঙ্গুর টিকা আছে কি?",
     "vaccine|tika|টিকা|ভ্যাকসিন",
     "কিছু দেশে একটি টিকা (QDenga) অনুমোদিত। WHO বেশি সংক্রমণের এলাকায় ৬ থেকে ১৬ বছর বয়সীদের জন্য সুপারিশ করে। "
     "আপনার জন্য পাওয়া যায় কিনা বা প্রযোজ্য কিনা ডাক্তারের কাছে জেনে নিন।"),
    ("এই ওয়েবসাইট", "about", "এই ওয়েবসাইট কী কাজ করে?",
     "website|about|purpose|denguewatch|ওয়েবসাইট|কী কাজ",
     "DengueWatch ওয়ার্ডভিত্তিক ডেঙ্গু ঝুঁকির পূর্বাভাস দেখায় এবং ডেঙ্গুর লক্ষণ, বিপদচিহ্ন ও প্রতিরোধের উপায় জানায়।"),
    ("এই ওয়েবসাইট", "model", "পূর্বাভাস কীভাবে করা হয়? কতটা নির্ভরযোগ্য?",
     "model|forecast|predict|accura|reliab|পূর্বাভাস|মডেল|নির্ভরযোগ্য|সঠিক",
     "আবহাওয়া ও আগের সপ্তাহগুলোর রোগীর তথ্য থেকে একটি machine learning মডেল কয়েক সপ্তাহ পরের ঝুঁকি "
     "অনুমান করে। এটি অনুমান, ভুল হতে পারে; কম ঝুঁকি মানে ঝুঁকি নেই এমন নয়।"),
    ("এই ওয়েবসাইট", "levels", "ঝুঁকির মাত্রাগুলোর মানে কী?",
     "risk level|threshold|level|মাত্রা",
     "ওয়ার্ডে সাপ্তাহিক পূর্বাভাসের রোগী ১-এর কম হলে **কম**, ৫-এর কম হলে **মাঝারি**, ১০-এর কম হলে **বেশি**, "
     "আর ১০ বা তার বেশি হলে **খুব বেশি** ঝুঁকি।"),
    ("এই ওয়েবসাইট", "live", "এটা কি আজকের তথ্য?",
     "live|today|real time|ajker|আজকের|লাইভ|তারিখ", None),
]
QUESTIONS, KEYWORDS, STATIC = {}, {}, {}
for _group, _key, _question, _words, _answer in FAQ:
    QUESTIONS.setdefault(_group, {})[_key] = _question
    KEYWORDS[_key] = _words
    if _answer:
        STATIC[_key] = _answer
HEALTH = {key for group, key, *_ in FAQ if group not in ("আমার এলাকা", "এই ওয়েবসাইট")}
# a more specific topic wins over a general one when both match
PRIORITY = ("after_fever", "child", "pregnant", "platelet", "papaya", "danger",
            "medicine", "spread", "breeding", "vaccine")
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
    for intent, (canned, _) in public_en.FAQ.items():
        if text == normalize(canned):
            return intent
    words = text.split()
    scores = {}
    for intent, keywords in KEYWORDS.items():
        score = 0
        for keyword in map(normalize, keywords.split("|")):
            if keyword.isascii():
                if re.search(rf"\b{keyword}", text):
                    score += len(keyword)
                elif len(keyword) >= 6 and difflib.get_close_matches(keyword, words, 1, 0.82):
                    score += len(keyword) - 2
            elif keyword in text:
                score += len(keyword)
        if score:
            scores[intent] = score
    for intent in PRIORITY:
        if intent in scores:
            return intent
    return max(scores, key=scores.get) if scores else None


def questions(lang="bn"):
    """Question buttons grouped by topic in the chosen language."""
    if lang != "en":
        return QUESTIONS
    return {public_en.GROUPS[group]: {key: public_en.FAQ[key][0] for key in items}
            for group, items in QUESTIONS.items()}


def _wards(frame, lang="bn"):
    table = frame[["ward_id", "city", "risk_level"]].copy()
    if lang == "en":
        table.columns = ["Ward", "City", "Risk"]
        return table
    table["risk_level"] = table["risk_level"].map(RISK_BN)
    table.columns = ["ওয়ার্ড", "শহর", "ঝুঁকি"]
    return table


def answer(question, forecasts, lang="bn"):
    """Return (markdown text, optional table). forecasts has one row per ward."""
    if lang == "en":
        return _answer_en(question, forecasts)
    text = normalize(question)
    city, number = find_city(text), find_ward(text)
    intent = match_intent(question)
    if intent in HEALTH:
        note = "\n\n_সাধারণ তথ্য, চিকিৎসকের পরামর্শের বিকল্প নয়।_"
        return STATIC[intent] + note, None
    if number is None and intent in STATIC:
        return STATIC[intent], None
    if number is None and intent is None and city is None:
        return ("দুঃখিত, প্রশ্নটি বুঝতে পারিনি। কোনো প্রশ্নে ক্লিক করুন, অথবা এভাবে লিখুন: "
                "“ঢাকা উত্তর ৩”, “Gazipur 2”, “ডেঙ্গুর লক্ষণ”।"), None

    target = forecasts["target_date"].iloc[0].strftime("%d-%m-%Y")
    scope = f"**{target}** সপ্তাহের পূর্বাভাস (পুরোনো তথ্যের ডেমো)"
    if city:
        scope += f", শহর: {city}"
    view = forecasts[forecasts["city"] == city] if city else forecasts

    if number is not None:
        found = view[view["ward_id"].str.endswith(f"_{number:02d}")]
        if found.empty:
            return f"{number} নম্বর ওয়ার্ড পাওয়া যায়নি।", None
        order = list(RISK_BN)
        worst = max(found["risk_level"], key=order.index)
        hint = "" if city else " শহরের নামসহ লিখলে শুধু আপনার ওয়ার্ড দেখাবে।"
        return (f"{scope}\n\n{number} নম্বর ওয়ার্ডে ঝুঁকি: **{RISK_BN[worst]}**"
                f"{'' if len(found) == 1 else ' (শহরগুলোর মধ্যে সর্বোচ্চ)'}।{hint}\n\n"
                f"**করণীয়:** {ADVICE[worst]}"), _wards(found)

    if intent == "low":
        lowest = view.sort_values(["predicted_cases", "ward_id"]).head(5)
        return (f"{scope}\n\nপূর্বাভাসে তুলনামূলক কম ঝুঁকির ওয়ার্ড (কম মানে ঝুঁকিমুক্ত নয়):",
                _wards(lowest))

    if intent == "live":
        return f"না, এটি আজকের সতর্কবার্তা নয়। এখন দেখানো হচ্ছে {scope}।", None

    high = int(view["risk_level"].isin(["High", "Critical"]).sum())
    return (f"{scope}\n\n**{high}** টি ওয়ার্ডে বেশি বা খুব বেশি ঝুঁকি। সবার উপরের ওয়ার্ডগুলো:",
            _wards(view.sort_values("predicted_cases", ascending=False).head(5)))


def _answer_en(question, forecasts):
    text = normalize(question)
    city, number = find_city(text), find_ward(text)
    intent = match_intent(question)
    static = public_en.FAQ[intent][1] if intent else None
    if intent in HEALTH:
        return static + "\n\n_General information, not a substitute for medical advice._", None
    if number is None and static:
        return static, None
    if number is None and intent is None and city is None:
        return ("Sorry, I did not understand. Click a question, or type for example "
                "“Dhaka North 3”, “Gazipur 2” or “dengue symptoms”."), None

    target = forecasts["target_date"].iloc[0].strftime("%d-%m-%Y")
    scope = f"Forecast for the week of **{target}** (demo using past data)"
    if city:
        scope += f", city: {city}"
    view = forecasts[forecasts["city"] == city] if city else forecasts

    if number is not None:
        found = view[view["ward_id"].str.endswith(f"_{number:02d}")]
        if found.empty:
            return f"Ward number {number} was not found.", None
        worst = max(found["risk_level"], key=list(RISK_BN).index)
        label, advice = public_en.RISK[worst]
        hint = "" if city else " Add the city name to see only your ward."
        several = "" if len(found) == 1 else " (highest among the cities)"
        return (f"{scope}\n\nWard {number}: **{label}**{several}.{hint}\n\n"
                f"**What to do:** {advice}"), _wards(found, "en")

    if intent == "low":
        lowest = view.sort_values(["predicted_cases", "ward_id"]).head(5)
        return (f"{scope}\n\nWards with comparatively low predicted risk (low is not "
                "risk free):", _wards(lowest, "en"))

    if intent == "live":
        return f"No, this is not today's alert. Shown now: {scope}.", None

    high = int(view["risk_level"].isin(["High", "Critical"]).sum())
    return (f"{scope}\n\n**{high}** wards are at high or very high risk. Top wards:",
            _wards(view.sort_values("predicted_cases", ascending=False).head(5), "en"))

