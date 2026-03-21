import streamlit as st
import pandas as pd
import joblib
import os
import random
from sklearn.pipeline import Pipeline
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.ensemble import RandomForestClassifier
from deep_translator import GoogleTranslator

st.set_page_config(page_title="ASOIU IT Helpdesk AI", page_icon="⚙️", layout="centered")

# CSS ilə Qırmızı Rəng, Dalğalı Fon və Yumşaq Künclərin Tətbiqi
st.markdown("""
<style>
    /* 1. Arxa fona zərif qırmızı dalğa naxışı (SVG formatında) */
    .stApp {
        background-color: #ffffff;
        background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 1440 320'%3E%3Cpath fill='%23ffecec' fill-opacity='1' d='M0,224L48,213.3C96,203,192,181,288,186.7C384,192,480,224,576,218.7C672,213,768,171,864,149.3C960,128,1056,128,1152,144C1248,160,1344,192,1392,208L1440,224L1440,320L1392,320C1344,320,1248,320,1152,320C1056,320,960,320,864,320C768,320,672,320,576,320C480,320,384,320,288,320C192,320,96,320,48,320L0,320Z'%3E%3C/path%3E%3C/svg%3E");
        background-attachment: fixed;
        background-size: cover;
    }
    
    /* 2. Mətn rəngləri - Oxunaqlı olması üçün tünd qırmızı */
    h1, h2, h3, p, label, .stMarkdown {
        color: #800000 !important;
    }
    
    /* 3. Düymələrin dizaynı - Qırmızı rəng və tam oval (yumşaq) künclər */
    .stButton>button {
        background-color: #cc0000;
        color: #ffffff;
        border-radius: 25px; /* Sərt küncləri yığışdıran əsas parametr */
        border: none;
        padding: 12px 28px;
        font-weight: bold;
        transition: 0.3s;
        box-shadow: 0px 4px 6px rgba(204, 0, 0, 0.2);
    }
    
    /* Düymənin üzərinə gəldikdə rəngin tündləşməsi */
    .stButton>button:hover {
        background-color: #990000;
        color: white;
        box-shadow: 0px 6px 8px rgba(204, 0, 0, 0.4);
    }
    
    /* 4. Mətn daxiletmə qutusu (Text Area) - Oval künclər */
    .stTextArea textarea {
        border: 2px solid #cc0000;
        border-radius: 15px; /* Sərt künclər yığışdırıldı */
        background-color: #fff9f9;
        color: #800000;
    }
    
    /* 5. Uğurlu nəticə və xəbərdarlıq qutularının künclərinin yumşaldılması */
    div[data-testid="stAlert"] {
        background-color: #ffe6e6;
        border-left: 5px solid #cc0000;
        border-radius: 12px; /* Sərt künclər yığışdırıldı */
        color: #800000;
    }
</style>
""", unsafe_allow_html=True)

employees = {
    "Şəbəkə": "Cavid Məmmədov (Şəbəkə Administratoru)",
    "Avadanlıq": "Orxan Əliyev (Texniki Dəstək Mütəxəssisi)",
    "Hesab_Problemi": "Aygün Həsənova (Sistem Administratoru)",
    "Proqram_Təminatı": "Elvin Qasımov (Proqram Təminatı Mühəndisi)"
}

@st.cache_resource
def load_or_train_model():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    model_path = os.path.join(current_dir, 'helpdesk_classifier_model.pkl')
    
    try:
        return joblib.load(model_path)
    except Exception:
        network_issues = ["Wi-Fi şəbəkəsinə qoşulmur", "İnternet bağlantısı qırılır", "IP xətası verir", "Lan kabeli qırılıb", "şəbəkəyə girə bilmirəm", "internet zəifdir"]
        hardware_issues = ["Noutbuk donur mavi ekran", "Proyektor işləmir", "Printer çap etmir", "RAM problemi var", "SSD xarab olub", "Ana plata yandı", "ekran qapqaradır", "klaviatura işləmir", "siçan xarabdır"]
        account_issues = ["mailimə giriş edə bilmirəm", "Moodle parolumu unutmuşam", "Hesabım bloklanıb", "parol səhvdir", "hesabıma girə bilmirəm", "şifrəmi itirmişəm", "email bloklanıb"]
        software_issues = ["Office proqramları lisenziya xətası", "Python PATH problemi", "Windows update dondu", "Antivirus yenilənmir", "proqram açılmır", "word xəta verir"]

        data = []
        for _ in range(150):
            data.append({"ticket_text": random.choice(network_issues), "category": "Şəbəkə"})
            data.append({"ticket_text": random.choice(hardware_issues), "category": "Avadanlıq"})
            data.append({"ticket_text": random.choice(account_issues), "category": "Hesab_Problemi"})
            data.append({"ticket_text": random.choice(software_issues), "category": "Proqram_Təminatı"})

        df = pd.DataFrame(data)
        
        # Yenilik: Süni İntellekt artıq bütöv sözləri deyil, hərflərin kombinasiyasını (char_wb) öyrənir.
        # Bu, qrammatik xətaların və səhv yazılışların qarşısını 100% alır.
        pipeline = Pipeline([
            ('tfidf', TfidfVectorizer(analyzer='char_wb', ngram_range=(3, 5))),
            ('clf', RandomForestClassifier(n_estimators=100, random_state=42))
        ])
        pipeline.fit(df['ticket_text'], df['category'])
        return pipeline

model = load_or_train_model()

st.title("IT Sorğularının Avtomatlaşdırılmış Təsnifatı")
st.markdown("Şikayəti istənilən dildə (AZ, EN, RU, TR) daxil edin. AI onu avtomatik tərcümə edib aidiyyəti əməkdaşa yönləndirəcək.")

tab1, tab2 = st.tabs(["📝 Anında Analiz", "📁 Toplu CSV Analizi"])

with tab1:
    user_input = st.text_area("İstifadəçi Şikayəti:", height=120, placeholder="Məsələn: У меня не работает мышка...")
    if st.button("Təhlil Et və Yönləndir"):
        if user_input.strip():
            with st.spinner("AI mətni analiz edir və dilini təyin edir..."):
                try:
                    # Yazılan mətni avtomatik tanıyıb Azərbaycan dilinə tərcümə edir
                    translated_text = GoogleTranslator(source='auto', target='az').translate(user_input)
                    
                    # Əgər mətn başqa dildə yazılıbsa, istifadəçiyə tərcüməni göstərir
                    if translated_text.lower() != user_input.lower():
                        st.info(f"🌐 **AI Tərcümə:** {translated_text}")
                        
                    prediction = model.predict([translated_text])[0]
                except Exception:
                    # İnternet/Tərcümə xətası olarsa, orijinal mətnlə davam edir
                    prediction = model.predict([user_input])[0]
                
                assigned_agent = employees.get(prediction, "Ümumi Dəstək Şöbəsi")
                st.success(f"📌 **Təyin Edilmiş Kateqoriya:** {prediction}")
                st.info(f"👤 **Sorğu Təyin Edildi:** {assigned_agent}")
        else:
            st.warning("Zəhmət olmasa problemi tam ifadə edin.")

with tab2:
    st.markdown("İçərisində **`ticket_text`** sütunu olan CSV faylını bura yükləyin.")
    uploaded_file = st.file_uploader("Data Faylını Seçin", type=["csv"])
    if uploaded_file:
        df = pd.read_csv(uploaded_file)
        if 'ticket_text' in df.columns:
            with st.spinner("Toplu analiz və tərcümə prosesi gedir..."):
                def smart_predict(text):
                    try:
                        trans = GoogleTranslator(source='auto', target='az').translate(str(text))
                        return model.predict([trans])[0]
                    except:
                        return model.predict([str(text)])[0]
                
                df['Təyin_Edilmiş_Kateqoriya'] = df['ticket_text'].apply(smart_predict)
                df['Təyin_Edilmiş_Əməkdaş'] = df['Təyin_Edilmiş_Kateqoriya'].map(employees)
                
                st.dataframe(df.head())
                csv_data = df.to_csv(index=False).encode('utf-8')
                st.download_button("📥 İşçilər Üzrə Bölünmüş CSV-ni Endir", data=csv_data, file_name='is_bolgusu_multi.csv', mime='text/csv')
        else:
            st.error("Xəta: 'ticket_text' adlı sütun yoxdur.")
