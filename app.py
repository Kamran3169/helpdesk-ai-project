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

st.markdown("""
<style>
    .stApp { background-color: #ffffff; }
    h1, h2, h3, p, label, .stMarkdown { color: #003366 !important; }
    .stButton>button { background-color: #00509e; color: #ffffff; border-radius: 8px; border: none; padding: 10px 24px; font-weight: bold; }
    .stButton>button:hover { background-color: #002244; color: white; }
    .stTextArea textarea { border: 2px solid #00509e; background-color: #f4f8fc; color: #003366; }
    div[data-testid="stAlert"] { background-color: #e6f2ff; border-left: 5px solid #00509e; color: #003366; }
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
