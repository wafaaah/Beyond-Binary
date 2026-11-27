"""English text for the public advisory page, poster and Copilot."""

RISK = {
    "Low": ("Low risk", "Stay alert and do not let water collect around your home."),
    "Medium": ("Medium risk", "Check around your house today and empty any standing water."),
    "High": ("High risk", "Avoid mosquito bites. If you have a fever, see a doctor quickly."),
    "Critical": ("Very high risk", "Take care now. If you have a fever, see a doctor and get "
                 "tested without delay."),
}

# poster and risk card: Bangla text -> English text
POSTER = {
    "টব, টায়ার ও পাত্রের জমা পানি ফেলে দিন": "Empty water from pots, tyres and containers",
    "পানির পাত্র সবসময় ঢেকে রাখুন": "Always keep water containers covered",
    "দিনে ও রাতে ঘুমানোর সময় মশারি ব্যবহার করুন": "Use a bed net when sleeping, day or night",
    "মশা তাড়ানোর ওষুধ বা রিপেলেন্ট ব্যবহার করুন": "Use mosquito repellent",
    "ফুলহাতা জামা ও লম্বা পায়জামা পরুন": "Wear long sleeves and long trousers",
    "হঠাৎ তীব্র জ্বর": "Sudden high fever",
    "তীব্র মাথাব্যথা": "Severe headache",
    "চোখের পেছনে ব্যথা": "Pain behind the eyes",
    "পেশি ও হাড়ের জোড়ায় ব্যথা": "Muscle and joint pain",
    "ত্বকে লালচে দানা বা র‍্যাশ": "Skin rash",
    "বমি বমি ভাব বা বমি": "Nausea or vomiting",
    "তীব্র পেটব্যথা": "Severe stomach pain",
    "বারবার বমি": "Repeated vomiting",
    "নাক, মাড়ি, বমি বা পায়খানায় রক্ত": "Bleeding from nose or gums, or blood in vomit or stool",
    "খুব দুর্বল বা অস্থির লাগা": "Feeling very weak or restless",
    "শ্বাসকষ্ট": "Difficulty breathing",
    "প্রচুর পানি, স্যালাইন ও তরল খাবার": "Plenty of water, oral saline and fluids",
    "মশারির ভেতরে বিশ্রাম": "Rest under a bed net",
    "জ্বর-ব্যথায় শুধু প্যারাসিটামল, নির্দেশমতো": "Only paracetamol for fever and pain, as directed",
    "অ্যাসপিরিন বা আইবুপ্রোফেন খাবেন না": "Do not take aspirin or ibuprofen",
    "জেনে রাখুন": "Know this", "এডিস মশা সাধারণত দিনের বেলায় কামড়ায়": "Aedes mosquitoes usually bite in the daytime",
    "মনে রাখুন": "Remember", "অল্প জমা পানিতেও এডিস মশা ডিম পাড়ে": "Aedes can lay eggs in even a little standing water",
    "প্রতি সপ্তাহে": "Every week", "অন্তত একবার জমা পানি ফেলে পাত্র পরিষ্কার করুন": "Empty standing water and clean containers at least once",
    "ডেঙ্গু সচেতনতা": "Dengue awareness", "ডেঙ্গু চিনুন,": "Know dengue,", "সময়মতো ব্যবস্থা নিন": "act in time",
    "সচেতন থাকলে পরিবার নিরাপদ থাকে": "An aware family is a safer family",
    "ডেঙ্গুর লক্ষণ": "Dengue symptoms",
    "বিপদচিহ্ন: দেরি না করে হাসপাতালে যান": "Warning signs: go to hospital without delay",
    "জ্বর কমার পরেও হতে পারে": "They can appear even after the fever falls",
    "প্রতিরোধে করণীয়": "How to prevent", "জ্বর হলে করণীয়": "If you have a fever",
    "প্রয়োজনে দ্রুত ডাক্তারের পরামর্শ নিন": "See a doctor quickly when needed", "জরুরি: ৯৯৯": "Emergency: 999",
    "এই ওয়ার্ডের পূর্বাভাস": "Forecast for this ward",
}
METER = {"কম": "Low", "মাঝারি": "Medium", "বেশি": "High", "খুব বেশি": "Very high"}

GROUPS = {
    "আমার এলাকা": "My area", "ডেঙ্গু সম্পর্কে": "About dengue", "লক্ষণ ও পরীক্ষা": "Symptoms and tests",
    "চিকিৎসা ও যত্ন": "Treatment and care", "প্রতিরোধ": "Prevention", "এই ওয়েবসাইট": "This website",
}

# intent: (question, answer or None when the answer comes from the forecast)
FAQ = {
    "my_area": ("What is the dengue risk in my area?", "Search your city and ward number in the box above, for example “Dhaka North 3” or “Gazipur 2”."),
    "top": ("Which wards have the highest risk?", None),
    "low": ("Which wards have the lowest risk?", None),
    "high_action": ("What should I do if risk is high in my area?", "Empty standing water in and around your home, use bed nets and repellent, and wear long sleeves. If anyone has a fever, see a doctor quickly and get tested."),
    "ward_help": ("How can I find my ward number?", "Ask your local ward councillor's office or city corporation."),
    "cities": ("Which cities are covered?", "Chattogram (10 wards), Dhaka North (20), Dhaka South (20), Gazipur (5) and Narayanganj (5)."),
    "what": ("What is dengue?", "Dengue is a viral disease spread mainly by the bite of infected Aedes mosquitoes. Many people have mild or no symptoms, but some can become seriously ill."),
    "spread": ("How does dengue spread? Is it contagious?", "It spreads mainly through the bite of infected Aedes mosquitoes. It does not pass directly between people by touch or being close. Spread from a pregnant mother to her baby is possible but uncommon."),
    "bite_time": ("When do Aedes mosquitoes bite?", "Aedes mosquitoes are active in the daytime. Stay careful during the day and use a bed net for daytime sleep too."),
    "breeding": ("Where do Aedes mosquitoes lay eggs?", "In containers and rubbish that hold water, such as flower pots, tyres, drums, open bottles or cans."),
    "again": ("Can I get dengue again?", "Yes. A second infection raises the risk of severe dengue, so be extra careful."),
    "symptoms": ("What are the symptoms of dengue?", "Sudden high fever, severe headache, pain behind the eyes, muscle and joint pain, rash, nausea or vomiting. See a doctor if you have these."),
    "incubation": ("How many days after a bite do symptoms start?", "Symptoms usually start 4 to 10 days later and last 2 to 7 days."),
    "test": ("When and how should I get tested?", "See a doctor early when you have a fever. In the first week a virus or antigen test (such as NS1) can be used; later an antibody test may be needed. Your doctor will decide."),
    "danger": ("When should I go to hospital?", "**Go to hospital without delay** for: severe stomach pain, repeated vomiting, fast breathing, bleeding from nose or gums, blood in vomit or stool, restlessness, severe weakness or thirst, or pale cold skin. These can appear after the fever falls. Emergency: **999**"),
    "care": ("What should I do if I have a fever?", "See a doctor and get tested, rest and drink plenty of fluids. Use paracetamol for fever and pain as directed. Go to hospital at once if you see warning signs (999)."),
    "medicine": ("Which medicines should be avoided?", "**Do not take aspirin, ibuprofen or similar painkillers**, as they raise the risk of bleeding. Paracetamol can be used for fever and pain; ask a doctor or pharmacist about the dose."),
    "food": ("What should I eat during dengue?", "Plenty of water, oral saline, soup and other fluids, and easily digested food. If you have another illness, ask your doctor."),
    "papaya": ("Does papaya leaf juice or a home remedy work?", "There is no specific medicine for dengue. Do not delay going to hospital because of home remedies, and tell your doctor before taking anything."),
    "platelet": ("What if my platelet count drops?", "Stay under medical care. Your doctor will decide whether platelets are needed. Go to hospital at once if there are warning signs."),
    "after_fever": ("Am I safe once the fever goes down?", "Not always. **Severe signs often appear after the fever falls.** Keep watching for warning signs."),
    "child": ("What if my child has a fever?", "See a doctor without delay. Do not choose medicine or dose yourself, and do not give aspirin or ibuprofen. Go to hospital at once if you see warning signs (999)."),
    "pregnant": ("What if a pregnant mother gets dengue?", "See a doctor quickly. Dengue in pregnancy can affect both mother and baby, so medical care is important."),
    "prevent": ("How can I prevent dengue?", "Empty standing water at least once a week, cover water containers, and use bed nets, repellent and long sleeves."),
    "home": ("How can I reduce mosquitoes at home?", "Empty water from pots, tyres, drums and other containers, cover water containers and clean them weekly, remove rubbish, and fit window screens if you can."),
    "patient_net": ("Should a dengue patient stay under a net?", "Yes. A mosquito that bites a patient can become infected and spread the virus to others."),
    "vaccine": ("Is there a dengue vaccine?", "One vaccine (QDenga) is approved in some countries. WHO recommends it for ages 6 to 16 in high transmission areas. Ask a doctor whether it is available and suitable for you."),
    "about": ("What does this website do?", "DengueWatch shows ward level dengue risk forecasts and explains symptoms, warning signs and prevention."),
    "model": ("How is the forecast made? Is it reliable?", "A machine learning model uses weather and cases from earlier weeks to estimate risk a few weeks ahead. It is an estimate and can be wrong; low risk does not mean no risk."),
    "levels": ("What do the risk levels mean?", "Predicted weekly cases in a ward below 1 is **Low**, below 5 is **Medium**, below 10 is **High**, and 10 or more is **Very high**."),
    "live": ("Is this today's information?", None),
}
