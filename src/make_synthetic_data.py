"""Generate synthetic labeled complaints for JanSadhak AI.

Labels are NOT guessed per row. Every scenario below encodes one situation and its
urgency is computed from the facts (days pending, injury yes/no, ...) using
docs/labeling_rules.md. So the labels stay consistent with the rules.

Usage:  python make_synthetic_data.py <existing_cdi_labeled.csv> <output.csv>
Seeded, so the same command always gives the same file.
"""
import random
import sys
import pandas as pd

rng = random.Random(42)
ri = rng.randint

# ---------- helpers ----------
UNITS = {
    "en": {"day": ("day", "days"), "hour": ("hour", "hours"), "month": ("month", "months"), "week": ("week", "weeks")},
    "hg": {"day": ("din", "din"), "hour": ("ghanta", "ghante"), "month": ("mahina", "mahine"), "week": ("hafta", "hafte")},
    "hi": {"day": ("दिन", "दिन"), "hour": ("घंटा", "घंटे"), "month": ("महीना", "महीने"), "week": ("हफ्ता", "हफ्ते")},
}


def dur(lang, n, unit):
    one, many = UNITS[lang][unit]
    return f"{n} {one if n == 1 else many}"


LOC_EN = ["Sector 14", "Gandhi Nagar", "Ward 12", "Model Town", "near Shiv Mandir", "Rajiv Chowk", "Sai Colony",
          "Lajpat Nagar", "Civil Lines", "MG Road", "near Nehru Park", "Kalyan Nagar", "Saraswati Vihar",
          "Ashok Vihar", "Patel Nagar", "Green Park", "Ward 7", "Subhash Chowk", "near City Mall", "Shastri Nagar",
          "Gali no 5, Rajendra Nagar", "Phase 2, Vikas Puri", "Block C, Janakpuri", "Indira Colony",
          "near Bus Stand", "Tilak Nagar", "Anand Vihar", "Sector 9", "Ward 21", "Bhagat Singh Colony"]
LOC_HI = ["सेक्टर 14", "गांधी नगर", "वार्ड 12", "मॉडल टाउन", "शिव मंदिर के पास", "राजीव चौक", "साई कॉलोनी",
          "लाजपत नगर", "सिविल लाइंस", "एमजी रोड", "नेहरू पार्क के पास", "कल्याण नगर", "सरस्वती विहार",
          "अशोक विहार", "पटेल नगर", "ग्रीन पार्क", "वार्ड 7", "सुभाष चौक", "सिटी मॉल के पास", "शास्त्री नगर",
          "गली नंबर 5, राजेंद्र नगर", "फेज 2, विकास पुरी", "ब्लॉक सी, जनकपुरी", "इंदिरा कॉलोनी",
          "बस स्टैंड के पास", "तिलक नगर", "आनंद विहार", "सेक्टर 9", "वार्ड 21", "भगत सिंह कॉलोनी"]
assert len(LOC_EN) == len(LOC_HI)

SCEN = []  # (dept, weight, sampler, templates)


def S(dept, weight, sampler, en, hg, hi):
    SCEN.append((dept, weight, sampler, {"en": en, "hg": hg, "hi": hi}))


def fixed(u, **extra):
    return lambda: (dict(extra), u)


def with_n(lo, hi, unit, u, **extra):
    def f():
        p = {"n": ri(lo, hi), "unit": unit}
        p.update(extra)
        return p, u
    return f


# ---------- ELECTRICITY ----------
S("electricity", 4, with_n(1, 3, "day", "low"),
  ["One streetlight in our lane has not been working for {d}, please replace the bulb",
   "The streetlight near my house is off since {d}. Kindly get it fixed",
   "A single streetlight on our road is out for {d}, everything else is fine"],
  ["Gali ki ek streetlight {d} se band hai, bulb change karwa do",
   "Ghar ke paas wali streetlight {d} se nahi jal rahi, please dekh lo",
   "Ek streetlight kharab hai {d} se, baaki sab theek hai"],
  ["हमारी गली की एक स्ट्रीट लाइट {d} से बंद है, कृपया बल्ब बदलवाएं"])
S("electricity", 4, with_n(4, 15, "day", "medium"),
  ["All the streetlights in our lane have been off for {d}. The whole road is dark after sunset",
   "Streetlights on the entire stretch are not working for {d}, residents find it hard to walk at night"],
  ["Poori gali ki streetlights {d} se band hain, raat ko andhera rehta hai",
   "Is road ki saari streetlights {d} se off hain, raat mein chalna mushkil ho gaya hai",
   "Colony ki lights {d} se nahi jal rahi, andhere mein aana jaana pad raha hai"],
  ["हमारी पूरी गली की स्ट्रीट लाइटें {d} से बंद हैं, रात में अंधेरा रहता है"])
S("electricity", 3, with_n(4, 12, "day", "high"),
  ["Streetlights are off for {d} and last night an old man fell in the dark and got hurt. Please fix them immediately",
   "Road is completely dark since {d}, a bike rider crashed into a divider last night. Need lights urgently"],
  ["Streetlights {d} se band hain, kal raat andhere mein ek buzurg gir gaye aur chot lagi. Jaldi lights chalu karo",
   "{d} se andhera hai road par, kal raat ek bike divider se takra gayi"],
  ["स्ट्रीट लाइटें {d} से बंद हैं, कल रात अंधेरे में एक बुजुर्ग गिरकर घायल हो गए, तुरंत ठीक करवाएं"])
S("electricity", 5, with_n(1, 20, "hour", "medium"),
  ["There has been no electricity in our area for the last {d}, no information from the office",
   "Power has been out for {d} now. Nobody is picking up the complaint number",
   "Power cut since {d} in our locality, work from home is badly affected"],
  ["Light nahi hai pichle {d} se, office wale koi jawab nahi dete",
   "{d} ho gaye bijli gayi hui hai, complaint number bhi nahi lag raha",
   "Area mein {d} se power cut hai, bohot pareshani ho rahi hai"],
  ["हमारे इलाके में पिछले {d} से बिजली नहीं है, कोई जानकारी नहीं दे रहा"])


def e_out():
    if rng.random() < 0.3:
        return {"n": ri(24, 48), "unit": "hour"}, "high"
    return {"n": ri(2, 5), "unit": "day"}, "high"


S("electricity", 4, e_out,
  ["There is no power at all in our colony for {d}. Old people and children are suffering",
   "Complete blackout for {d}, no electricity in the whole lane. Please send a team now"],
  ["Colony mein {d} se bilkul light nahi hai, buzurg aur bachche bohot pareshan hain",
   "{d} ho gaye poora blackout hai, pura mohalla andhere mein, team bhejo"],
  ["हमारी कॉलोनी में {d} से बिल्कुल बिजली नहीं है, बुजुर्ग और बच्चे परेशान हैं"])
S("electricity", 3, fixed("high"),
  ["A live electric wire has fallen on the road near the school, children are walking right next to it",
   "Electric wire is hanging low and sparking in front of our gate after the storm, very dangerous",
   "Broken high tension wire lying on the footpath, people are passing by it"],
  ["School ke paas road par bijli ka taar gir gaya hai, bachche paas se guzar rahe hain",
   "Toofan ke baad hamare gate ke saamne taar latak raha hai aur spark kar raha hai, bohot khatarnaak",
   "Footpath par bijli ka toota hua taar pada hai, log paas se nikal rahe hain"],
  ["स्कूल के पास सड़क पर बिजली का तार गिरा हुआ है, बच्चे उसके पास से गुजर रहे हैं"])
S("electricity", 2, fixed("high"),
  ["The transformer near the market is sparking and smoking, shops are right next to it",
   "Transformer in our lane made a loud blast and is on fire"],
  ["Market ke paas transformer se spark aur dhuan nikal raha hai, dukaane bilkul saath mein hain",
   "Gali wale transformer mein blast hua aur aag lag gayi hai"],
  ["बाजार के पास ट्रांसफार्मर से चिंगारियां और धुआं निकल रहा है, दुकानें बिल्कुल साथ में हैं"])
S("electricity", 1, fixed("high"),
  ["Electric pole is leaning badly on the main road after the rain and may fall any time"],
  ["Barish ke baad main road ka bijli ka khamba bahut jhuk gaya hai, kabhi bhi gir sakta hai"],
  ["बारिश के बाद मुख्य सड़क का बिजली का खंभा बहुत झुक गया है, कभी भी गिर सकता है"])


def e_bill():
    return {"amt": rng.choice([4800, 7200, 9650, 12400, 15800, 23500])}, "medium"


S("electricity", 3, e_bill,
  ["My electricity bill is Rs {amt} though we use very little power. They are threatening to cut the connection if I do not pay",
   "Bill of Rs {amt} came this month which is wrong. A disconnection notice has also been sent"],
  ["Bijli ka bill Rs {amt} aaya hai jabki use bohot kam hai, na bharne par connection kaatne ki dhamki de rahe",
   "Is mahine Rs {amt} ka galat bill aaya aur disconnection notice bhi aa gaya"],
  ["बिजली का बिल {amt} रुपये आया है जबकि खपत बहुत कम है, बिल न भरने पर कनेक्शन काटने की धमकी दे रहे हैं"])
S("electricity", 3, fixed("low"),
  ["Please check my meter reading, the bill looks a little higher than last month",
   "I want to know how to get my meter reading corrected on the bill",
   "Request to replace my old electricity meter, applied 10 days back"],
  ["Meter reading ek baar check karwa dijiye, bill pichle mahine se thoda zyada aaya hai",
   "Bill mein meter reading sahi karwani hai, kya process hai",
   "Purana meter badalwana hai, 10 din pehle application di thi"],
  ["कृपया मेरे मीटर की रीडिंग जांच लें, बिल पिछले महीने से थोड़ा ज्यादा आया है"])
S("electricity", 2, with_n(3, 20, "day", "medium"),
  ["Voltage keeps fluctuating in our area for {d}, the fridge and TV have started to malfunction",
   "Low voltage every evening for {d}, tubelights and fans are not working properly"],
  ["Hamare area mein {d} se voltage upar neeche ho raha hai, fridge aur TV kharab hone lage hain",
   "{d} se roz shaam ko low voltage rehta hai, fan aur tubelight theek se nahi chalte"],
  ["हमारे इलाके में {d} से वोल्टेज ऊपर-नीचे हो रहा है, फ्रिज और टीवी खराब होने लगे हैं"])

# ---------- WATER_SEWAGE ----------
S("water_sewage", 5, with_n(6, 20, "hour", "medium"),
  ["No water supply in our area for the last {d}",
   "Water has not come since morning, almost {d} now, we have nothing for cooking",
   "Tap water stopped {d} ago and the tanker is not here either"],
  ["Paani nahi aa raha pichle {d} se",
   "Subah se paani nahi aaya, {d} ho gaye, khana banane ko bhi nahi hai",
   "{d} pehle supply band hui thi, ab tak kuch nahi"],
  ["हमारे इलाके में पिछले {d} से पानी नहीं आ रहा है"])
S("water_sewage", 2, fixed("medium"),
  ["There has been no water since yesterday",
   "Taps are dry since yesterday, please check the supply line"],
  ["Kal se paani nahi aa raha, please check karo",
   "Kal se tap sookha pada hai"],
  ["कल से पानी नहीं आ रहा है, कृपया जांच करें"])
S("water_sewage", 5, with_n(2, 7, "day", "high"),
  ["No water at all for {d}, we are buying tankers every day",
   "Water supply has been completely cut off for {d} in our street. People are collecting water from far away",
   "{d} without a drop of tap water. Elderly people at home are suffering"],
  ["{d} se ek boond paani nahi aaya, roz tanker mangwana pad raha hai",
   "Gali mein {d} se supply poori band hai, log door se paani la rahe hain",
   "Ghar mein {d} se paani nahi hai, buzurg bohot pareshan hain"],
  ["{d} से नल में पानी की एक बूंद नहीं आई है, रोज टैंकर मंगवाना पड़ रहा है"])
S("water_sewage", 2, fixed("low"),
  ["Water pressure is very low in the morning, it takes long to fill the tank",
   "Pressure of tap water has dropped a bit, please check"],
  ["Subah paani ka pressure bohot kam hota hai, tanki bharne mein time lagta hai",
   "Nal mein pressure thoda kam ho gaya hai, ek baar dekh lo"],
  ["सुबह नल में पानी का प्रेशर बहुत कम रहता है, टंकी भरने में समय लगता है"])
S("water_sewage", 4, with_n(2, 10, "day", "medium"),
  ["Dirty brown water is coming from the tap for {d}, it smells bad",
   "The supplied water has been smelling like sewage for {d}, we cannot use it for drinking"],
  ["Nal se {d} se ganda bhura paani aa raha hai, badbu bhi hai",
   "{d} se supply ke paani mein sewage jaisi smell hai, peene layak nahi"],
  ["नल से {d} से गंदा भूरा पानी आ रहा है, बदबू भी है"])
S("water_sewage", 2, with_n(2, 6, "day", "high"),
  ["Dirty water is coming in taps and several children in our lane have fallen sick with loose motions",
   "Contaminated water supply for {d}, many people in the colony have stomach infection and vomiting"],
  ["Nal mein ganda paani aa raha hai aur gali ke kaafi bachche loose motion se bimar ho gaye hain",
   "{d} se ganda paani aa raha hai, colony mein kai logon ko pet ki infection aur ulti ho rahi hai"],
  ["नल में गंदा पानी आ रहा है और गली के कई बच्चे दस्त से बीमार हो गए हैं"])
S("water_sewage", 5, with_n(2, 10, "day", "medium"),
  ["Sewer is overflowing on the road in front of our gate, the smell is unbearable",
   "Drain has been blocked for {d} and dirty water is flowing on the street",
   "Gutter overflow on the main lane, vehicles and people are walking through sewage"],
  ["Gate ke saamne road par sewer overflow ho raha hai, badbu se rehna mushkil",
   "Naali {d} se jam hai aur ganda paani gali mein beh raha hai",
   "Main gali mein gutter overflow hai, log gande paani se guzar rahe hain"],
  ["हमारे गेट के सामने सड़क पर सीवर ओवरफ्लो हो रहा है, बदबू से रहना मुश्किल है"])
S("water_sewage", 3, fixed("high"),
  ["Sewage water is entering our houses and ground floor rooms since last night",
   "Drain overflow water has come inside my house, whole family is stuck in dirty water"],
  ["Kal raat se ghar ke andar sewage ka paani aa raha hai, ground floor poora bhar gaya",
   "Naali ka ganda paani ghar mein ghus gaya hai, poora parivaar pareshan hai"],
  ["कल रात से घरों के अंदर सीवर का पानी घुस रहा है, ग्राउंड फ्लोर में पानी भर गया है"])
S("water_sewage", 2, fixed("low"),
  ["Our lane drain is partly clogged with plastic, water is flowing slowly but not overflowing",
   "Please clean the small drain outside the house, it is slow but working"],
  ["Gali ki naali plastic se thodi jam hai, paani dheere ja raha hai par overflow nahi hai",
   "Ghar ke bahar ki chhoti naali saaf karwa dijiye, dheere chal rahi hai"],
  ["गली की नाली प्लास्टिक से थोड़ी जाम है, पानी धीरे जा रहा है पर ओवरफ्लो नहीं है"])
S("water_sewage", 2, fixed("low"),
  ["There is a small leak in the water pipe near the corner, water is dripping slowly",
   "Minor leakage from the supply pipeline outside my house"],
  ["Kone ke paas paani ki pipe mein chhota leak hai, boond boond paani tapak raha hai",
   "Ghar ke bahar supply pipe se halka leakage ho raha hai"],
  ["कोने के पास पानी की पाइप में छोटा रिसाव है, बूंद-बूंद पानी टपक रहा है"])
S("water_sewage", 2, fixed("medium"),
  ["Main water pipeline has burst and water is flooding the street since morning",
   "Big pipe burst near the chowk, thousands of litres wasted and the road is under water"],
  ["Subah se main pipeline phat gayi hai aur gali mein paani bhar gaya hai",
   "Chowk ke paas badi pipe phat gayi, hazaaron litre paani waste aur road par paani bhar gaya"],
  ["सुबह से मुख्य पाइपलाइन फट गई है और गली में पानी भर गया है"])
S("water_sewage", 2, fixed("high"),
  ["Manhole cover is missing in the middle of the lane, a child or cow can fall in",
   "Open sewer manhole on the main road without any barricade, someone already slipped yesterday"],
  ["Gali ke beech manhole ka dhakkan gayab hai, bachcha ya gaay gir sakti hai",
   "Main road par khula manhole hai bina kisi barricade ke, kal ek aadmi gir bhi gaya"],
  ["गली के बीच में मैनहोल का ढक्कन गायब है, बच्चा या गाय गिर सकती है"])
S("water_sewage", 2, with_n(2, 5, "day", "medium"),
  ["Heavy waterlogging on the road after rain, vehicles are getting stuck",
   "Rain water is not draining from our street for {d}, it has become a pond"],
  ["Barish ke baad road par bohot paani bhar gaya hai, gaadiyan phans rahi hain",
   "Gali mein barish ka paani {d} se nikal nahi raha, talaab ban gaya hai"],
  ["बारिश के बाद सड़क पर बहुत पानी भर गया है, गाड़ियां फंस रही हैं"])

# ---------- ROADS ----------
S("roads", 8, fixed("low"),
  ["There is a big pothole on our road, please repair when possible",
   "A pothole has formed in front of the bus stop. No accident so far, just needs repair",
   "Pothole on the service road is getting bigger, please fill it",
   "Road near my house has a deep gaddha, nothing serious but needs patching"],
  ["Road par ek bada gaddha ban gaya hai, repair karwa dijiye",
   "Bus stop ke saamne gaddha hai, abhi tak koi accident nahi hua, bas bharwa do",
   "Service road ka pothole badhta ja raha hai, please dekh lo",
   "Ghar ke paas road mein gehra gaddha hai, patching karwa do"],
  ["सड़क पर एक बड़ा गड्ढा हो गया है, कृपया मरम्मत करवा दें",
   "बस स्टॉप के सामने गड्ढा बन गया है, अभी तक कोई हादसा नहीं हुआ, बस भरवा दीजिए"])
S("roads", 8, fixed("medium"),
  ["Potholes on the main road are causing long traffic jams every evening",
   "Deep pothole damaged the tyre and rim of my car yesterday",
   "Many potholes on this stretch, vehicles move at crawling speed and two-wheelers are getting damaged",
   "Big pothole near the signal is blocking one lane and creating jams"],
  ["Main road ke gaddhon ki wajah se roz shaam ko lamba jam lagta hai",
   "Kal gehre gaddhe se meri car ka tyre aur rim kharab ho gaya",
   "Is stretch par bohot gaddhe hain, gaadiyan dheere chalti hain aur bike ko nuksaan ho raha hai",
   "Signal ke paas bada gaddha ek lane block kar raha hai, jam lag jata hai"],
  ["मुख्य सड़क के गड्ढों की वजह से रोज शाम को लंबा जाम लगता है",
   "कल गहरे गड्ढे से मेरी कार का टायर खराब हो गया"])
S("roads", 4, fixed("high"),
  ["A scooter rider fell into the pothole yesterday and broke his arm. Please repair it urgently",
   "Pothole accident today, a woman on a bike got badly injured near the school",
   "Child on a cycle fell in a pothole and got hurt, this is dangerous"],
  ["Kal ek scooter wala gaddhe mein gir gaya aur haath toot gaya, jaldi repair karwao",
   "Aaj gaddhe ki wajah se accident hua, school ke paas ek mahila bike se gir kar buri tarah ghayal ho gayi",
   "Cycle chalate bachche gaddhe mein gir kar chotil ho gaya, bahut khatarnaak hai"],
  ["कल एक स्कूटर सवार गड्ढे में गिर गया और उसका हाथ टूट गया, तुरंत मरम्मत करवाएं"])
S("roads", 2, fixed("high"),
  ["Huge pothole on the busy highway road, no lights at night, trucks swerve around it",
   "Very deep pothole on the flyover approach at night, no signboard or reflector"],
  ["Busy highway par bada gaddha hai, raat ko light nahi hoti, trucks bachke nikalte hain",
   "Flyover ke paas raat mein bahut gehra gaddha dikhta nahi, koi signboard ya reflector nahi"],
  ["व्यस्त हाईवे पर बड़ा गड्ढा है, रात में रोशनी नहीं होती, ट्रक बचकर निकलते हैं"])
S("roads", 2, fixed("high"),
  ["Bikes are slipping on the same pothole every day, three people fell this week",
   "People keep falling at this broken patch of road daily, it needs urgent repair"],
  ["Is gaddhe par roz bikes slip ho rahi hain, is hafte teen log gir chuke",
   "Isi toote hue hisse par roz log gir rahe hain, jaldi repair karo"],
  ["इसी गड्ढे पर रोज बाइकें फिसल रही हैं, इस हफ्ते तीन लोग गिर चुके हैं"])
S("roads", 2, fixed("high"),
  ["A big sinkhole has opened in the middle of the road after rain, cars cannot pass",
   "Road has caved in near the bridge and the hole keeps getting bigger"],
  ["Barish ke baad road ke beech bada sinkhole khul gaya hai, gaadiyan nahi nikal paa rahi",
   "Pul ke paas road dhans gayi hai aur gaddha badhta ja raha hai"],
  ["बारिश के बाद सड़क के बीच में बड़ा गड्ढा धंस गया है, गाड़ियां नहीं निकल पा रहीं"])
S("roads", 6, with_n(2, 8, "week", "medium"),
  ["The road was dug for cable work {d} ago and has not been repaired, dust and jams everywhere",
   "Pipeline digging left the road in bad shape for {d}, traffic is badly affected"],
  ["Cable ke kaam ke liye road khodi thi, {d} ho gaye repair nahi hui, dhool aur jam rehta hai",
   "Pipeline ki khudai ke baad road {d} se kharab padi hai, traffic bohot affect ho raha hai"],
  ["केबल के काम के लिए सड़क खोदी गई थी, {d} हो गए मरम्मत नहीं हुई, धूल और जाम रहता है"])
S("roads", 6, fixed("low"),
  ["Footpath tiles are broken in front of the market, pedestrians find it difficult",
   "Hawkers have occupied the footpath completely, we have to walk on the road",
   "Footpath near the park is damaged at some places, please repair"],
  ["Market ke saamne footpath ki tiles toot gayi hain, paidal chalne mein dikkat hai",
   "Footpath par pura thele wale baithe hain, road par chalna padta hai",
   "Park ke paas footpath kai jagah se toota hai, repair karwa do"],
  ["बाजार के सामने फुटपाथ की टाइलें टूटी हुई हैं, पैदल चलने में दिक्कत होती है"])
S("roads", 4, fixed("low"),
  ["Please add paint or reflectors on the speed breaker, it is hard to see",
   "Speed breaker outside my house is too high, request to reduce its height",
   "An unmarked speed breaker has come up on our street, a sign would help"],
  ["Speed breaker par paint ya reflector laga do, dikhta nahi",
   "Mere ghar ke bahar speed breaker bohot ooncha hai, height kam karwa do",
   "Gali mein bina marking ka speed breaker bana diya hai, sign laga dena chahiye"],
  ["स्पीड ब्रेकर पर पेंट या रिफ्लेक्टर लगवा दें, दिखाई नहीं देता"])
S("roads", 2, fixed("high"),
  ["Illegal high speed breaker without paint, two bikes crashed there at night this week",
   "Unmarked speed breaker on the highway turn caused an accident yesterday, a man is in hospital"],
  ["Bina paint ka illegal ooncha speed breaker hai, is hafte raat ko do bike gir chuki hain",
   "Highway mod par bina marking ka speed breaker hai, kal accident hua aur ek aadmi hospital mein hai"],
  ["बिना पेंट का गैरकानूनी ऊंचा स्पीड ब्रेकर है, इस हफ्ते रात में दो बाइकें गिर चुकी हैं"])
S("roads", 3, fixed("low"),
  ["Zebra crossing paint has faded near the school, please repaint",
   "Lane markings on the road are not visible anymore"],
  ["School ke paas zebra crossing ka paint ud gaya hai, dobara karwa do",
   "Road ki lane marking ab dikhti nahi hai"],
  ["स्कूल के पास जेब्रा क्रॉसिंग का पेंट उड़ गया है, दोबारा करवा दें"])
S("roads", 5, fixed("medium"),
  ["The entire road is broken with cracks and loose stones, vehicles have to move very slowly",
   "Whole lane has no tar left, it is only stones and mud and vehicles take double the time"],
  ["Poori road tooti hui hai, patthar bikhre hain, gaadiyan bahut dheere nikalti hain",
   "Poori gali mein tar nahi bacha, sirf patthar aur mitti hai, gaadiyon ko double time lagta hai"],
  ["पूरी सड़क टूटी हुई है, पत्थर बिखरे हैं, गाड़ियां बहुत धीरे निकलती हैं"])

# ---------- GARBAGE ----------
S("garbage", 6, with_n(1, 2, "day", "low"),
  ["Garbage truck has not visited for {d}, a small pile is forming",
   "Waste has not been collected from our lane for {d}",
   "Garbage van missed our street for {d}, bins are filling up"],
  ["Kachra gadi {d} se nahi aayi, dustbin bharne laga hai",
   "Gali se {d} se kachra nahi uthaya gaya",
   "Garbage wali gaadi {d} se nahi aa rahi, thoda kachra jama ho gaya"],
  ["कचरा गाड़ी {d} से नहीं आई है, डस्टबिन भरने लगा है"])
S("garbage", 8, with_n(3, 6, "day", "medium"),
  ["Garbage has not been picked up for {d}, piles are growing on the corner",
   "No waste collection for {d}, the whole lane smells and stray animals are scattering it",
   "The garbage truck has not come for {d}, residents are throwing waste on the road"],
  ["Kachra {d} se nahi uthaya gaya, kone par dher lag gaya hai",
   "{d} se garbage collection band hai, poori gali mein badbu hai aur jaanwar bikher rahe hain",
   "Kachra gadi {d} se nahi aayi, log road par kachra fenk rahe hain"],
  ["{d} से कचरा नहीं उठाया गया है, कोने पर ढेर लग गया है",
   "{d} से कचरा गाड़ी नहीं आई है, पूरी गली में बदबू फैली है"])
S("garbage", 5, with_n(7, 20, "day", "medium"),
  ["Garbage has been lying on the street for {d} now, there are flies and rats everywhere",
   "{d} of uncollected waste near the park, the smell is horrible and flies are spreading"],
  ["Gali mein {d} se kachra pada hai, makkhi aur chuhe bohot ho gaye hain",
   "Park ke paas {d} se kachra nahi uthaya, badbu aur makkhiyan bohot hain"],
  ["गली में {d} से कचरा पड़ा है, मक्खियां और चूहे बहुत हो गए हैं"])
S("garbage", 4, fixed("medium"),
  ["The public dustbin at the corner is overflowing and waste is spilling onto the road",
   "Community bin has not been emptied and garbage is spread all around it"],
  ["Kone ka public dustbin overflow ho raha hai aur kachra road par aa gaya hai",
   "Community bin khali nahi hua, uske aas paas kachra phaila hua hai"],
  ["कोने का सार्वजनिक डस्टबिन ओवरफ्लो हो रहा है और कचरा सड़क पर आ गया है"])
S("garbage", 4, fixed("medium"),
  ["A dead dog is lying on the road since morning and has started to smell",
   "Dead cow on the roadside near the market, please remove it",
   "Dead animal on our street, stench is spreading"],
  ["Subah se road par mara hua kutta pada hai, badbu aane lagi hai",
   "Market ke paas road kinare mari hui gaay pari hai, hatwa do",
   "Gali mein mara hua jaanwar pada hai, badbu phail rahi hai"],
  ["सुबह से सड़क पर एक मरा हुआ कुत्ता पड़ा है, बदबू आने लगी है"])
S("garbage", 3, fixed("medium"),
  ["Someone is burning garbage near our colony every evening, the smoke is irritating",
   "Waste is being burnt in the open plot daily and smoke is coming into homes"],
  ["Colony ke paas roz shaam ko koi kachra jalata hai, dhuan bohot pareshan karta hai",
   "Khali plot mein roz kachra jalaya ja raha hai aur dhuan ghar mein aa raha hai"],
  ["हमारी कॉलोनी के पास रोज शाम को कचरा जलाया जाता है, धुआं बहुत परेशान करता है"])
S("garbage", 2, fixed("high"),
  ["Garbage dump is on fire and the flames are reaching nearby houses",
   "Big fire in the waste heap near the school, children are coughing"],
  ["Kachre ke dher mein aag lagi hai aur lapten paas ke ghar tak pahunch rahi hain",
   "School ke paas kachre ke dher mein badi aag lagi hai, bachche khaans rahe hain"],
  ["कचरे के ढेर में आग लगी है और लपटें पास के घरों तक पहुंच रही हैं"])
S("garbage", 3, fixed("medium"),
  ["Construction debris has been dumped on the road and is blocking half the lane",
   "Someone dumped a truck load of rubble in front of our gate and nobody is clearing it"],
  ["Road par construction ka malba daal diya gaya hai, aadhi lane block ho gayi",
   "Gate ke saamne kisi ne truck bhar malba daal diya, koi uthata nahi"],
  ["सड़क पर निर्माण का मलबा डाल दिया गया है, आधी लेन बंद हो गई है"])
S("garbage", 4, fixed("low"),
  ["Please install a dustbin near the bus stop, people throw waste on the ground",
   "Road sweeping is not done regularly in our lane, request to start it",
   "The garbage truck comes late in the day, could the timing be changed to morning"],
  ["Bus stop ke paas ek dustbin lagwa dijiye, log zameen par kachra fenkte hain",
   "Hamari gali mein road sweeping regular nahi hoti, shuru karwa dijiye",
   "Kachra gadi der se aati hai, timing subah ki kar sakte hain kya"],
  ["बस स्टॉप के पास एक डस्टबिन लगवा दें, लोग जमीन पर कचरा फेंकते हैं"])

# ---------- POLICE ----------
S("police", 6, fixed("medium"),
  ["My bike was stolen from outside my house last night, no CCTV in the lane",
   "Phone snatched near the bus stop yesterday evening, I want to register a complaint",
   "House lock was broken and valuables are missing, we returned from a trip today",
   "Cycle and a water motor stolen from our parking overnight"],
  ["Kal raat ghar ke bahar se meri bike chori ho gayi, gali mein CCTV bhi nahi hai",
   "Kal shaam bus stop ke paas phone cheen liya gaya, complaint likhwani hai",
   "Ghar ka taala toota hua mila aur samaan gayab hai, aaj trip se wapas aaye",
   "Parking se raat ko cycle aur water motor chori ho gaye"],
  ["कल रात घर के बाहर से मेरी बाइक चोरी हो गई, गली में सीसीटीवी भी नहीं है",
   "घर का ताला टूटा मिला और कीमती सामान गायब है"])
S("police", 5, fixed("high"),
  ["Some people are trying to break into the shop next door right now, please send police",
   "Two men are snatching bags from women near the market at this moment",
   "A group is beating a man in the street right now, someone call police immediately",
   "Burglars are inside the neighbour's house at this moment"],
  ["Abhi padosi ki dukaan ka taala kuch log tod rahe hain, police bhejo",
   "Market ke paas is waqt do ladke mahilaon ke bag cheen rahe hain",
   "Abhi gali mein kuch log ek aadmi ko maar rahe hain, turant police bhejo",
   "Padosi ke ghar mein abhi chor ghuse hue hain"],
  ["अभी पड़ोसी की दुकान का ताला कुछ लोग तोड़ रहे हैं, पुलिस भेजिए",
   "इस समय बाजार के पास दो लड़के महिलाओं के बैग छीन रहे हैं"])
S("police", 4, fixed("high"),
  ["Boys on bikes harass girls outside the college gate every day and follow them",
   "Girls are being teased and followed near the girls hostel every evening by a group"],
  ["College gate ke bahar roz bike wale ladke ladkiyon ko pareshan karte hain aur peecha karte hain",
   "Girls hostel ke paas roz shaam ko ek group ladkiyon ko chhedta hai aur follow karta hai"],
  ["कॉलेज के गेट के बाहर रोज बाइक वाले लड़के लड़कियों को परेशान करते हैं और पीछा करते हैं"])
S("police", 5, with_n(3, 10, "day", "medium"),
  ["Loud DJ and speakers run till 2 am for {d} in the park next to us, children cannot study",
   "Neighbours play very loud music at night for {d}, no one can sleep"],
  ["Bagal ke park mein {d} se raat 2 baje tak DJ aur speaker chalte hain, bachche padh nahi paate",
   "Padosi {d} se raat ko bahut tez music bajate hain, neend nahi aati"],
  ["बगल के पार्क में {d} से रात 2 बजे तक डीजे और स्पीकर चलते हैं, बच्चे पढ़ नहीं पाते"])
S("police", 2, fixed("low"),
  ["Loud speaker was played after 10 pm at a wedding last night, please warn them in future",
   "Neighbour's party was a bit noisy yesterday, requesting a polite word"],
  ["Kal raat shaadi mein 10 baje ke baad bhi loud speaker bajta raha, aage ke liye samjha dijiye",
   "Kal padosi ki party thodi shor wali thi, bas ek baar baat kar lijiye"],
  ["कल रात शादी में 10 बजे के बाद भी तेज स्पीकर बजता रहा, आगे के लिए समझा दें"])
S("police", 4, fixed("medium"),
  ["Some unknown men keep roaming in our lane at night and checking the gates",
   "A suspicious car parks outside our society every night with people sitting inside"],
  ["Kuch anjaan log raat ko hamari gali mein ghoomte hain aur gate check karte hain",
   "Roz raat ek shak wali gaadi society ke bahar khadi hoti hai aur uske andar log baithe rehte hain"],
  ["कुछ अनजान लोग रात को हमारी गली में घूमते हैं और गेट चेक करते हैं"])
S("police", 3, fixed("medium"),
  ["Illegal liquor is being sold from a shop in our lane and drunk men create trouble",
   "Gambling happens every night in the empty plot behind the temple"],
  ["Hamari gali mein ek dukaan se avaidh sharab bik rahi hai aur nashe mein log jhagde karte hain",
   "Mandir ke peeche khali plot mein roz raat ko juaa chalta hai"],
  ["हमारी गली में एक दुकान से अवैध शराब बिक रही है और नशे में लोग झगड़ा करते हैं"])
S("police", 4, fixed("low"),
  ["Please increase police patrolling in our colony in the evenings",
   "What is the status of the complaint I gave at the police booth last week, nobody has called me",
   "Please put a police beat on the market road during festival days"],
  ["Colony mein shaam ko police patrolling badha dijiye",
   "Pichle hafte police booth mein jo complaint di thi uska status kya hai, kisi ne call nahi kiya",
   "Tyohaar ke din market road par police beat laga do"],
  ["हमारी कॉलोनी में शाम को पुलिस गश्त बढ़ा दीजिए"])
S("police", 3, fixed("medium"),
  ["A group of drunk men sit near the tea stall every night abusing and fighting with passersby",
   "Drunk youths shout and throw bottles in our street at midnight on most nights"],
  ["Chai ki tapri ke paas roz raat nashe mein kuch log gaali galoch aur ladai karte hain",
   "Raat ko aksar nashe mein ladke gali mein chillate hain aur bottles fenkte hain"],
  ["चाय की टपरी के पास रोज रात नशे में कुछ लोग गाली-गलौज और लड़ाई करते हैं"])
S("police", 3, fixed("medium"),
  ["Chain snatching happened yesterday evening on our road, police have not come yet",
   "There was a fight between two groups last night and a shop glass was broken, please take action"],
  ["Kal shaam hamari road par chain snatching hui, police abhi tak nahi aayi",
   "Kal raat do groups mein ladai hui aur dukaan ka sheesha tod diya, action lo"],
  ["कल शाम हमारी सड़क पर चेन स्नैचिंग हुई, पुलिस अभी तक नहीं आई"])

# ---------- HEALTH ----------
S("health", 5, with_n(2, 10, "day", "medium"),
  ["The doctor has not come to the dispensary for {d}, patients are going back",
   "PHC has no doctor for {d}, only a compounder gives medicines"],
  ["Dispensary mein {d} se doctor nahi aaye, mareez wapas jaa rahe hain",
   "PHC mein {d} se koi doctor nahi hai, sirf compounder dawai deta hai"],
  ["डिस्पेंसरी में {d} से डॉक्टर नहीं आए हैं, मरीज लौट रहे हैं"])
S("health", 4, fixed("medium"),
  ["Basic medicines like paracetamol and BP tablets are not available at the government dispensary",
   "Medicine stock is empty at the community health centre, we are told to buy outside"],
  ["Sarkari dispensary mein paracetamol aur BP ki goliyan bhi nahi hain",
   "CHC mein dawai khatam hai, bahar se kharidne ko bol rahe hain"],
  ["सरकारी डिस्पेंसरी में पैरासिटामोल और बीपी की गोलियां भी नहीं हैं"])
S("health", 3, fixed("high"),
  ["Ambulance did not come for an emergency chest pain patient even after 40 minutes of calls",
   "Hospital refused ambulance for a delivery case at night, family had to take an auto"],
  ["Seene mein dard ke emergency mareez ke liye 40 minute baad bhi ambulance nahi aayi",
   "Raat ko delivery case ke liye hospital ne ambulance se mana kar diya, parivaar ko auto se jana pada"],
  ["सीने में दर्द के आपातकालीन मरीज के लिए 40 मिनट बाद भी एम्बुलेंस नहीं आई"])
S("health", 3, fixed("low"),
  ["The toilets in the government hospital waiting area are not clean",
   "Waiting hall at the dispensary needs fans and better cleaning"],
  ["Sarkari hospital ke waiting area ke toilet saaf nahi hain",
   "Dispensary ke waiting hall mein pankhe aur safai ki zarurat hai"],
  ["सरकारी अस्पताल के प्रतीक्षा क्षेत्र के शौचालय साफ नहीं हैं"])
S("health", 3, fixed("low"),
  ["OPD queue is very long in the morning, could a token system be started",
   "What are the OPD timings of the community health centre on Saturdays",
   "Reception staff speaks rudely to patients"],
  ["Subah OPD ki line bahut lambi hoti hai, token system shuru kar do",
   "CHC ki Saturday ko OPD timing kya hai",
   "Reception ka staff mareezon se rudely baat karta hai"],
  ["सुबह ओपीडी की लाइन बहुत लंबी होती है, टोकन सिस्टम शुरू करवा दें"])
S("health", 5, with_n(3, 15, "day", "medium"),
  ["Water has collected in the empty plot next to our house and mosquitoes are everywhere",
   "Mosquito breeding in the stagnant water near the park, please spray",
   "Too many mosquitoes in our lane for {d}, nobody has come for fogging"],
  ["Ghar ke bagal ke khali plot mein paani jama hai aur machhar bohot hain",
   "Park ke paas ruke hue paani mein machhar paida ho rahe hain, spray karwa do",
   "Gali mein {d} se bohot machhar hain, fogging ke liye koi nahi aaya"],
  ["घर के बगल के खाली प्लॉट में पानी जमा है और मच्छर बहुत हैं"])
S("health", 4, fixed("medium"),
  ["Stagnant water near our block, high risk of dengue and malaria, no one is ill yet, please do fogging",
   "Dengue season is here and our lane has open water tanks and puddles, we need larvicide spray"],
  ["Block ke paas paani ruka hua hai, dengue malaria ka bohot khatra hai, abhi tak koi bimar nahi hai, fogging karwa do",
   "Dengue ka season hai aur gali mein khuli tankiyan aur gadhdhon mein paani hai, larvicide spray chahiye"],
  ["हमारे ब्लॉक के पास पानी रुका हुआ है, डेंगू-मलेरिया का खतरा है, अभी तक कोई बीमार नहीं है, फॉगिंग करवाएं"])
S("health", 4, fixed("high"),
  ["Three people in our lane have been diagnosed with dengue this week, please do fogging immediately",
   "Dengue cases are rising in our colony, two children are admitted in hospital"],
  ["Is hafte hamari gali mein teen logon ko dengue nikla hai, turant fogging karwao",
   "Colony mein dengue ke cases badh rahe hain, do bachche hospital mein admit hain"],
  ["इस हफ्ते हमारी गली में तीन लोगों को डेंगू हुआ है, तुरंत फॉगिंग करवाएं"])
S("health", 3, fixed("high"),
  ["Many people in our area have high fever and vomiting for the past few days, looks like an outbreak",
   "Several families have jaundice and diarrhoea in our slum, no health team has visited"],
  ["Hamare area mein kaafi logon ko pichle kuch din se tez bukhar aur ulti ho rahi hai, outbreak lag raha hai",
   "Basti mein kai parivaron ko jaundice aur dast ho rahe hain, koi health team nahi aayi"],
  ["हमारे इलाके में कई लोगों को पिछले कुछ दिनों से तेज बुखार और उल्टी हो रही है, महामारी जैसा लग रहा है"])
S("health", 2, fixed("low"),
  ["When is the next vaccination camp for children in our ward",
   "Please inform where the free health checkup camp is being held this month"],
  ["Hamare ward mein bachchon ka agla vaccination camp kab hai",
   "Is mahine free health checkup camp kahan lag raha hai bata dijiye"],
  ["हमारे वार्ड में बच्चों का अगला टीकाकरण शिविर कब है"])

# ---------- PENSION_GOVT ----------
S("pension_govt", 3, with_n(4, 10, "month", "high"),
  ["My old age pension has not come for {d}, I depend on it for medicines and food",
   "Old age pension is stopped since {d}, I have no other income"],
  ["Meri vridha pension {d} se nahi aayi, dawai aur khane ke liye usi par depend hoon",
   "Vridha pension {d} se band hai, aur koi income nahi hai"],
  ["मेरी वृद्धा पेंशन {d} से नहीं आई है, दवा और खाने के लिए उसी पर निर्भर हूं"])
S("pension_govt", 4, with_n(1, 3, "month", "medium"),
  ["Widow pension has not been credited for {d}, please check the status",
   "Disability pension is pending for {d}, application is in the office"],
  ["Vidhwa pension {d} se account mein nahi aayi, status check karwa do",
   "Viklang pension {d} se pending hai, application office mein padi hai"],
  ["विधवा पेंशन {d} से खाते में नहीं आई है, कृपया स्थिति जांचें"])
S("pension_govt", 1, with_n(2, 3, "month", "high"),
  ["Widow pension pending for {d} and my family has no other income, we are struggling to eat"],
  ["Vidhwa pension {d} se atki hai aur ghar mein koi aur kamaane wala nahi, khane ke laale pad gaye hain"],
  ["विधवा पेंशन {d} से अटकी है और घर में कमाने वाला कोई नहीं, खाने के लाले पड़ गए हैं"])
S("pension_govt", 4, with_n(1, 3, "month", "medium"),
  ["Applied for a new ration card {d} ago and it has not been issued yet",
   "Ration card application is pending for {d}, status shows under verification"],
  ["Naye ration card ke liye {d} pehle apply kiya tha, abhi tak nahi bana",
   "Ration card ki application {d} se pending hai, status mein verification dikha raha hai"],
  ["नए राशन कार्ड के लिए {d} पहले आवेदन किया था, अभी तक नहीं बना"])
S("pension_govt", 3, with_n(4, 12, "month", "high"),
  ["I applied for my ration card {d} ago and still have not received it, I cannot get subsidised grain",
   "Ration card is pending for {d}, every time the office gives a new excuse"],
  ["Ration card ke liye {d} pehle apply kiya tha, ab tak nahi mila, sasta anaaj nahi mil pa raha",
   "Ration card {d} se pending hai, office har baar naya bahana banata hai"],
  ["राशन कार्ड के लिए {d} पहले आवेदन किया था, अब तक नहीं मिला, सस्ता अनाज नहीं मिल पा रहा"])
S("pension_govt", 5, with_n(3, 20, "day", "low"),
  ["Applied for a birth certificate {d} ago, just wanted to know the expected date",
   "Income certificate application is {d} old, kindly update the status",
   "Caste certificate was applied {d} back, when will it be ready"],
  ["Birth certificate ke liye {d} pehle apply kiya tha, bas expected date jaanni hai",
   "Income certificate ki application {d} purani hai, status bata dijiye",
   "Caste certificate {d} pehle apply kiya tha, kab tak ban jayega"],
  ["जन्म प्रमाणपत्र के लिए {d} पहले आवेदन किया था, बस अपेक्षित तारीख जाननी है"])
S("pension_govt", 3, with_n(5, 12, "week", "medium"),
  ["Domicile certificate pending for {d}, I need it for college admission",
   "Death certificate of my father has not been issued for {d}, bank work is stuck"],
  ["Domicile certificate {d} se pending hai, college admission ke liye chahiye",
   "Pitaji ka death certificate {d} se nahi bana, bank ka kaam ruka hua hai"],
  ["डोमिसाइल प्रमाणपत्र {d} से लंबित है, कॉलेज एडमिशन के लिए चाहिए"])
S("pension_govt", 3, fixed("low"),
  ["I want to correct a spelling mistake in my ration card, applied last week",
   "Please tell me how to check my pension application status online"],
  ["Ration card mein naam ki spelling theek karwani hai, pichle hafte apply kiya tha",
   "Pension application ka status online kaise check karein bata dijiye"],
  ["राशन कार्ड में नाम की स्पेलिंग ठीक करवानी है, पिछले हफ्ते आवेदन किया था"])
S("pension_govt", 2, with_n(4, 9, "month", "high"),
  ["Property mutation file is pending in the municipal office for {d}, I cannot sell my house",
   "Land record correction has been stuck for {d}, officers keep asking me to come back next week"],
  ["Property mutation ki file {d} se municipal office mein atki hai, ghar bech nahi pa raha",
   "Zameen ke record ki correction {d} se ruki hai, officer har baar agle hafte bulate hain"],
  ["संपत्ति म्यूटेशन की फाइल {d} से नगर निगम कार्यालय में अटकी है, मैं घर नहीं बेच पा रहा"])

# ---------- OTHER ----------
S("other", 4, fixed("low"),
  ["There are too many stray dogs in our street",
   "Please do something about the stray dogs near the market",
   "Stray dogs sleep and bark on our lane, request to relocate them"],
  ["Hamari gali mein awara kutte bahut hain",
   "Market ke paas awara kutton ke liye kuch karo",
   "Gali mein awara kutte bhaunkte aur sote rehte hain, unhe shift karwa do"],
  ["हमारी गली में आवारा कुत्ते बहुत हैं"])
S("other", 3, fixed("medium"),
  ["Stray dogs chase bikes and morning walkers in our lane, people are scared",
   "A pack of dogs growls at children going to school every day"],
  ["Awara kutte bike aur subah walk karne walon ke peeche padte hain, log dare hue hain",
   "Kutton ka jhund roz school jaate bachon par bhaunkta hai"],
  ["आवारा कुत्ते बाइक और सुबह टहलने वालों के पीछे पड़ते हैं, लोग डरे हुए हैं"])
S("other", 3, fixed("high"),
  ["A stray dog bit a small child in our lane today and he is being taken for injections",
   "Two people were bitten by street dogs near the park this morning"],
  ["Aaj hamari gali mein awara kutte ne ek chhote bachche ko kaat liya, injection ke liye le ja rahe hain",
   "Aaj subah park ke paas awara kutton ne do logon ko kaat liya"],
  ["आज हमारी गली में एक आवारा कुत्ते ने छोटे बच्चे को काट लिया, इंजेक्शन के लिए ले जा रहे हैं"])
S("other", 3, fixed("medium"),
  ["Stray cows are sitting in the middle of the road and blocking traffic",
   "Cattle herd roams on the highway service road, bikers often have to brake suddenly"],
  ["Awara gaayein road ke beech baithi rehti hain aur traffic block hota hai",
   "Service road par pashuon ka jhund ghoomta hai, bike walon ko achanak brake lagana padta hai"],
  ["आवारा गायें सड़क के बीच बैठी रहती हैं और ट्रैफिक रुक जाता है"])
S("other", 3, fixed("medium"),
  ["Monkeys snatch food and damage things in our colony, they enter homes through balconies",
   "Monkey menace has increased a lot in our area in recent weeks"],
  ["Colony mein bandar khaana cheen lete hain aur saaman kharab karte hain, balcony se ghar mein ghus jaate hain",
   "Hamare area mein pichle kuch hafton se bandar bohot badh gaye hain"],
  ["कॉलोनी में बंदर खाना छीन लेते हैं और सामान खराब करते हैं, बालकनी से घर में घुस जाते हैं"])
S("other", 3, fixed("low"),
  ["Cars are parked in front of my gate every day and I cannot take my vehicle out",
   "Illegal parking on the lane outside the market makes it narrow"],
  ["Roz meri gate ke saamne gaadiyan khadi rehti hain, meri gaadi nikalne mein dikkat hoti hai",
   "Market ke bahar gali mein galat parking se rasta tang ho jata hai"],
  ["रोज मेरे गेट के सामने गाड़ियां खड़ी रहती हैं, अपनी गाड़ी निकालने में दिक्कत होती है"])
S("other", 3, fixed("low"),
  ["Benches in the park are broken and the grass has not been cut for weeks",
   "Please add a few more dustbins and benches in our colony park"],
  ["Park ki benches tooti hui hain aur ghaas hafton se nahi kati",
   "Colony ke park mein kuch aur dustbin aur bench lagwa dijiye"],
  ["पार्क की बेंचें टूटी हुई हैं और घास हफ्तों से नहीं कटी"])
S("other", 3, fixed("low"),
  ["Neighbour has built a shed outside their plot on the public land",
   "Shopkeepers have extended their shop fronts onto the lane, it feels cramped"],
  ["Padosi ne apne plot ke bahar sarkari zameen par shed bana liya hai",
   "Dukandaaron ne dukaan ke aage gali tak jagah gher li hai, rasta tang ho gaya"],
  ["पड़ोसी ने अपने प्लॉट के बाहर सरकारी जमीन पर शेड बना लिया है"])
S("other", 3, fixed("medium"),
  ["A big tree has fallen across the lane after last night's storm and nobody can pass",
   "Large branch has broken and is blocking the road to our colony"],
  ["Kal raat ke toofan mein bada ped gali ke aar-paar gir gaya hai, koi nikal nahi sakta",
   "Bada hissa toot kar colony ke road par pada hai aur raasta band hai"],
  ["कल रात के तूफान में बड़ा पेड़ गली के आर-पार गिर गया है, कोई नहीं निकल सकता"])
S("other", 3, fixed("low"),
  ["Please look into the problem in our area",
   "Many problems here, nobody is listening",
   "Need help, issue in our locality"],
  ["Hamare area mein problem hai, please dekh lo",
   "Yaha kaafi dikkatein hain, koi sunta nahi",
   "Help chahiye, mohalle mein ek issue hai"],
  ["हमारे इलाके में समस्या है, कृपया देखें"])

# ---------- how many rows per department (new rows only) ----------
QUOTA = {"roads": 70, "garbage": 60, "police": 55, "water_sewage": 46,
         "health": 40, "electricity": 36, "pension_govt": 34, "other": 29}
N_HINDI = 40


def allocate(total, weights):
    s = sum(weights)
    raw = [total * w / s for w in weights]
    out = [int(r) for r in raw]
    rest = total - sum(out)
    order = sorted(range(len(raw)), key=lambda i: raw[i] - out[i], reverse=True)
    for i in order[:rest]:
        out[i] += 1
    return out


slots = []  # (dept, sampler, templates)
for dept, q in QUOTA.items():
    sc = [s for s in SCEN if s[0] == dept]
    for (d, w, sampler, tpl), k in zip(sc, allocate(q, [s[1] for s in sc])):
        for _ in range(k):
            slots.append((dept, sampler, tpl))
assert len(slots) == sum(QUOTA.values())
rng.shuffle(slots)

# language assignment: exact counts
n = len(slots)
n_hi = N_HINDI
n_en = round((n - n_hi) * 105 / 330)
langs = ["hi"] * n_hi + ["en"] * n_en + ["hg"] * (n - n_hi - n_en)
rng.shuffle(langs)


def typo_noise(text):
    out = []
    for w in text.split():
        if len(w) > 3 and w.isalpha() and rng.random() < 0.08:
            i = rng.randrange(1, len(w) - 1)
            w = w[:i] + w[i + 1:]
        out.append(w)
    return " ".join(out)


def build(lang, tpl, params):
    kw = dict(params)
    if "n" in params:
        kw["d"] = dur(lang, params["n"], params["unit"])
    base = rng.choice(tpl[lang]).format(**kw)
    loc = None
    if rng.random() < 0.7:
        i = rng.randrange(len(LOC_EN))
        loc = LOC_HI[i] if lang == "hi" else LOC_EN[i]
        pat = rng.choice(["{b}, {l}", "{l}: {b}", "{b} ({l})", "{b} - {l}"]) if lang != "hi" else rng.choice(["{b}, {l}", "{l}: {b}"])
        base = pat.format(b=base, l=loc)
    return base, loc is not None


rows = []
for (dept, sampler, tpl), lang in zip(slots, langs):
    params, urg = sampler()
    text, has_loc = build(lang, tpl, params)
    if lang != "hi":
        if rng.random() < 0.12:
            op = rng.choice(["Sir, ", "Dear sir, ", "Hello, "] if lang == "en" else ["Sir, ", "Bhaiya ", "Namaste, "])
            text = op + text[0].lower() + text[1:]
        if urg in ("low", "medium") and rng.random() < 0.07:   # Rule 3: loud tone, same label
            if rng.random() < 0.5:
                text = text.upper() + "!!!"
            else:
                text = text + ("!!! jaldi karo" if lang == "hg" else "!!! please do something fast")
        if rng.random() < 0.3:
            text = typo_noise(text)
        if rng.random() < 0.3:
            text = text.lower()
        if rng.random() < 0.4:
            text = text.rstrip(".")
    rows.append({"complaint_text": text, "department": dept, "urgency": urg,
                 "language": {"en": "english", "hg": "hinglish", "hi": "hindi"}[lang],
                 "source": "synthetic", "location_mentioned": "yes" if has_loc else "no"})

new = pd.DataFrame(rows)
new = new[~new["complaint_text"].str.lower().duplicated()].reset_index(drop=True)

old = pd.read_csv(sys.argv[1], encoding="utf-8-sig", dtype=str, keep_default_na=False)
new = new[~new["complaint_text"].isin(set(old["complaint_text"]))].reset_index(drop=True)
start = len(old) + 1
new.insert(0, "id", [f"cdi{start + i:03d}" for i in range(len(new))])
out = pd.concat([old, new], ignore_index=True)
out.to_csv(sys.argv[2], index=False, encoding="utf-8-sig", lineterminator="\r\n")

print("new rows:", len(new), "| total:", len(out))
print(out["language"].value_counts().to_string())
print(out["department"].value_counts().to_string())
print(out["urgency"].value_counts().to_string())
print(pd.crosstab(out["department"], out["urgency"]).to_string())
print(out["location_mentioned"].value_counts().to_string())
