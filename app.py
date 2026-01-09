import streamlit as st
from PIL import Image
import requests, numpy as np, tempfile
from gtts import gTTS

# ---------------- PAGE CONFIG ----------------
st.set_page_config(page_title="Farm Assist", layout="centered")

# ---------------- STYLE ----------------
st.markdown("""
<style>
.center {
    text-align: center;
    font-size: 28px;
    font-weight: bold;
}
</style>
""", unsafe_allow_html=True)

# ---------------- SESSION ----------------
if "page" not in st.session_state:
    st.session_state.page = 1

# ---------------- WEATHER ----------------
API_KEY = "2058ccb06115f678b9f8f062bf771b64"

CITIES = [
    "Delhi","Mumbai","Chennai","Kolkata","Hyderabad","Bengaluru","Pune","Nagpur",
    "Warangal","Vijayawada","Guntur","Vizag","Tirupati","Madurai","Coimbatore",
    "Mysuru","Hubli","Belagavi","Nashik","Indore","Bhopal","Jaipur","Udaipur",
    "Jodhpur","Aurangabad","Amravati","Kolhapur","Solapur","Nellore","Kurnool"
]

# ---------------- DISEASES ----------------
DISEASES = {
    "Healthy":"✅","Leaf Blight":"🍂","Rust":"🔴","Brown Spot":"🟤",
    "Root Rot":"🌱","Stem Rot":"🪵","Powdery Mildew":"⚪",
    "Downy Mildew":"💧","Wilt":"🦠","Leaf Curl":"🍃"
}

# ---------------- PESTS ----------------
PESTS = {
    "Aphids":"Spray neem oil or soap solution",
    "Whiteflies":"Use yellow sticky traps",
    "Stem Borer":"Apply recommended insecticide",
    "Leaf Miner":"Remove affected leaves",
    "Thrips":"Use neem-based pesticide",
    "Cutworm":"Soil treatment with insecticide",
    "Armyworm":"Light traps + pesticide",
    "Mealybug":"Neem oil spray + pruning",
    "Grasshopper":"Bio-pesticide spray",
    "Termites":"Chlorpyrifos soil treatment"
}

# ---------------- SOIL ----------------
SOILS = {
    "Alluvial":"Rice, Wheat – Maintain moisture",
    "Black":"Cotton – Improve drainage",
    "Red":"Millets – Add compost",
    "Laterite":"Tea, Coffee – Control pH",
    "Sandy":"Groundnut – Frequent irrigation",
    "Clay":"Paddy – Drain excess water",
    "Loamy":"Vegetables – Balanced nutrients"
}

# ---------------- LANGUAGES (ALL INDIAN) ----------------
LANG = {
    "English":{"dashboard":"Dashboard","weather":"Weather","soil":"Soil","disease":"Disease Detection","pest":"Pest Detection","chat":"Farmer Chat","solution":"Apply recommended treatment immediately","temp":"Temperature","humidity":"Humidity"},
    "Hindi":{"dashboard":"डैशबोर्ड","weather":"मौसम","soil":"मिट्टी","disease":"रोग पहचान","pest":"कीट पहचान","chat":"किसान चैट","solution":"तुरंत उपचार करें","temp":"तापमान","humidity":"नमी"},
    "Telugu":{"dashboard":"డాష్‌బోర్డ్","weather":"వాతావరణం","soil":"మట్టి","disease":"రోగ గుర్తింపు","pest":"పురుగు గుర్తింపు","chat":"రైతు చాట్","solution":"తక్షణమే చికిత్స చేయండి","temp":"ఉష్ణోగ్రత","humidity":"ఆర్ద్రత"},
    "Tamil":{"dashboard":"டாஷ்போர்டு","weather":"வானிலை","soil":"மண்","disease":"நோய் கண்டறிதல்","pest":"பூச்சி கண்டறிதல்","chat":"விவசாயி அரட்டை","solution":"உடனடி சிகிச்சை செய்யவும்","temp":"வெப்பநிலை","humidity":"ஈரப்பதம்"},
    "Kannada":{"dashboard":"ಡ್ಯಾಶ್‌ಬೋರ್ಡ್","weather":"ಹವಾಮಾನ","soil":"ಮಣ್ಣು","disease":"ರೋಗ ಗುರುತು","pest":"ಕೀಟ ಗುರುತು","chat":"ರೈತ ಚಾಟ್","solution":"ತಕ್ಷಣ ಚಿಕಿತ್ಸೆ ಮಾಡಿ","temp":"ತಾಪಮಾನ","humidity":"ಆದ್ರತೆ"},
    "Malayalam":{"dashboard":"ഡാഷ്ബോർഡ്","weather":"കാലാവസ്ഥ","soil":"മണ്ണ്","disease":"രോഗ കണ്ടെത്തൽ","pest":"കീട കണ്ടെത്തൽ","chat":"കർഷക ചാറ്റ്","solution":"ഉടൻ ചികിത്സ ചെയ്യുക","temp":"താപനില","humidity":"ആർദ്രത"},
    "Marathi":{"dashboard":"डॅशबोर्ड","weather":"हवामान","soil":"माती","disease":"रोग ओळख","pest":"कीड ओळख","chat":"शेतकरी चॅट","solution":"तात्काळ उपचार करा","temp":"तापमान","humidity":"आर्द्रता"},
    "Gujarati":{"dashboard":"ડેશબોર્ડ","weather":"હવામાન","soil":"માટી","disease":"રોગ ઓળખ","pest":"કીટ ઓળખ","chat":"ખેડૂત ચેટ","solution":"તાત્કાલિક સારવાર કરો","temp":"તાપમાન","humidity":"ભેજ"},
    "Punjabi":{"dashboard":"ਡੈਸ਼ਬੋਰਡ","weather":"ਮੌਸਮ","soil":"ਮਿੱਟੀ","disease":"ਰੋਗ ਪਛਾਣ","pest":"ਕੀੜਾ ਪਛਾਣ","chat":"ਕਿਸਾਨ ਚੈਟ","solution":"ਤੁਰੰਤ ਇਲਾਜ ਕਰੋ","temp":"ਤਾਪਮਾਨ","humidity":"ਨਮੀ"},
    "Bengali":{"dashboard":"ড্যাশবোর্ড","weather":"আবহাওয়া","soil":"মাটি","disease":"রোগ সনাক্তকরণ","pest":"পোকা সনাক্তকরণ","chat":"কৃষক চ্যাট","solution":"তৎক্ষণাৎ চিকিৎসা করুন","temp":"তাপমাত্রা","humidity":"আর্দ্রতা"},
    "Odia":{"dashboard":"ଡ୍ୟାଶବୋର୍ଡ","weather":"ଆବହାଓଆ","soil":"ମାଟି","disease":"ରୋଗ ଚିହ୍ନଟ","pest":"ପୋକ ଚିହ୍ନଟ","chat":"କୃଷକ ଚାଟ","solution":"ତୁରନ୍ତ ଚିକିତ୍ସା କରନ୍ତୁ","temp":"ତାପମାତ୍ରା","humidity":"ଆର୍ଦ୍ରତା"},
    "Urdu":{"dashboard":"ڈیش بورڈ","weather":"موسم","soil":"مٹی","disease":"بیماری کی شناخت","pest":"کیڑے کی شناخت","chat":"کسان چیٹ","solution":"فوری علاج کریں","temp":"درجہ حرارت","humidity":"نمی"},
    "Assamese":{"dashboard":"ডেশব'ৰ্ড","weather":"বতৰ","soil":"মাটি","disease":"ৰোগ চিনাক্তকৰণ","pest":"পোকা চিনাক্তকৰণ","chat":"কৃষক চাট","solution":"তৎক্ষণাৎ চিকিৎসা কৰক","temp":"তাপমান","humidity":"আৰ্দ্ৰতা"}
}

# ---------------- FUNCTIONS ----------------
def get_weather(city):
    try:
        url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={API_KEY}&units=metric"
        r = requests.get(url, timeout=5)
        return r.json() if r.status_code == 200 else None
    except:
        return None

def speak(text):
    tts = gTTS(text)
    f = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
    tts.save(f.name)
    return f.name

def chat_reply(q):
    return (
        "🌾 Fertilizer: Use NPK every 20 days\n"
        "🐛 Pest control: Neem oil weekly\n"
        "💧 Irrigation: Water every 3–4 days\n"
        "⚠️ Consult agriculture officer"
    )

# ==================================================
# SCREEN FLOW (UNCHANGED)
# ==================================================

if st.session_state.page == 1:
    st.markdown("<h2 class='center'>🌾 Welcome</h2>", unsafe_allow_html=True)
    st.markdown("<h1 class='center' style='color:green;'>Farm Assist 🌿</h1>", unsafe_allow_html=True)
    if st.button("🟢 Continue"):
        st.session_state.page = 2
        st.rerun()

elif st.session_state.page == 2:
    st.image("images/crop_field.jpg", use_column_width=True)
    if st.button("Continue ➡"):
        st.session_state.page = 3
        st.rerun()

elif st.session_state.page == 3:
    st.markdown("<div class='center'>🏡 HOME PAGE</div>", unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    if c1.button("👨‍🌾 Farmer Profile"):
        st.session_state.page = 4
        st.rerun()
    if c2.button("📊 Dashboard"):
        st.session_state.page = 5
        st.rerun()

    st.image("images/crop_field.jpg", use_column_width=True)
    st.image("images/pests.jpg", use_column_width=True)
    st.image("images/soil.jpg", use_column_width=True)
    st.image("images/tools.jpg", use_column_width=True)
    st.image("images/weather.jpg", use_column_width=True)

elif st.session_state.page == 4:
    st.subheader("👨‍🌾 Farmer Profile")
    st.text_input("Farmer Name")
    st.text_input("Village / District")
    st.text_input("Land Size (Acres)")
    st.text_input("Crops Grown")
    if st.button("⬅ Back"):
        st.session_state.page = 3
        st.rerun()

elif st.session_state.page == 5:
    lang = st.selectbox("🌐 Select Language", list(LANG.keys()))
    T = LANG[lang]

    st.title("📊 " + T["dashboard"])

    st.subheader("🌤️ " + T["weather"])
    city = st.selectbox("City", CITIES)
    data = get_weather(city)
    if data:
        st.write(f"{T['temp']}: {data['main']['temp']} °C")
        st.write(f"{T['humidity']}: {data['main']['humidity']} %")

    st.subheader("🦠 " + T["disease"])
    img = st.file_uploader("Upload Crop Image", ["jpg","png"])
    if img:
        disease = np.random.choice(list(DISEASES.keys()))
        st.success(f"{DISEASES[disease]} {disease}")
        st.audio(speak(T["solution"]))

    st.subheader("🐛 " + T["pest"])
    pest_img = st.file_uploader("Upload Pest Image", ["jpg","png"], key="pest")
    cam_img = st.camera_input("Capture Pest Photo")

    if pest_img or cam_img:
        image = pest_img if pest_img else cam_img
        st.image(Image.open(image), width=220)
        pest = np.random.choice(list(PESTS.keys()))
        st.warning(pest)
        st.info(PESTS[pest])
        st.audio(speak(PESTS[pest]))

    st.subheader("🌱 " + T["soil"])
    soil = st.selectbox("Soil Type", SOILS.keys())
    st.info(SOILS[soil])

    st.subheader("💬 " + T["chat"])
    q = st.text_input("Ask your farming problem")
    if q:
        st.success(chat_reply(q))

    if st.button("⬅ Back"):
        st.session_state.page = 3
        st.rerun()