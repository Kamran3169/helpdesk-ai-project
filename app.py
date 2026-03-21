import streamlit as st
import pandas as pd
import joblib
import os
import random
from sklearn.pipeline import Pipeline
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.ensemble import RandomForestClassifier

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
        # Əvvəlcə hazır modeli oxumağa çalışır
        return joblib.load(model_path)
    except Exception:
        # FAYLLAR TAPILMADIQDA BİRBAŞA YADDAŞDA ÖYRƏNİR (TAM MÜSTƏQİL)
        st.toast("Model buludda yenidən qurulur...", icon="🧠")
        
        network_issues = ["Korpustakı Wi-Fi şəbəkəsinə qoşulmur", "İnternet bağlantısı qırılır", "IP xətası verir", "Lan kabeli qırılıb"]
        hardware_issues = ["Noutbuk donur və mavi ekran verir", "Proyektor işləmir", "Printer çap etmir", "RAM problemi var, donur", "SSD xarab olub", "Ana plata yandı"]
        account_issues = ["Korporativ mailimə giriş edə bilmirəm", "Moodle parolumu unutmuşam", "Hesabım bloklanıb", "Active Directory-də hesabım silinib"]
        software_issues = ["Office proqramları lisenziya xətası verir", "Python PATH problemi", "Windows update dondu", "Antivirus yenilənmir"]

        data = []
        for _ in range(80):
            data.append({"ticket_text": random.choice(network_issues), "category": "Şəbəkə"})
            data.append({"ticket_text": random.choice(hardware_issues), "category": "Avadanlıq"})
            data.append({"ticket_text": random.choice(account_issues), "category": "Hesab_Problemi"})
            data.append({"ticket_text": random.choice(software_issues), "category": "Proqram_Təminatı"})

        df = pd.DataFrame(data)
        pipeline = Pipeline([
            ('tfidf', TfidfVectorizer()),
            ('clf', RandomForestClassifier(n_estimators=100, random_state=42))
        ])
        pipeline.fit(df['ticket_text'], df['category'])
        return pipeline

model = load_or_train_model()

st.title("IT Sorğularının Avtomatlaşdırılmış Təsnifatı")
st.markdown("Şikayəti daxil edin və Süni İntellekt onu dərhal aidiyyəti əməkdaşa yönləndirsin.")

tab1, tab2 = st.tabs(["📝 Anında Analiz", "📁 Toplu CSV Analizi"])

with tab1:
    user_input = st.text_area("İstifadəçi Şikayəti:", height=120, placeholder="Məsələn: SSD yaddaş xarab olub...")
    if st.button("Təhlil Et və Yönləndir"):
        if user_input.strip():
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
            df['Təyin_Edilmiş_Kateqoriya'] = model.predict(df['ticket_text'].fillna(""))
            df['Təyin_Edilmiş_Əməkdaş'] = df['Təyin_Edilmiş_Kateqoriya'].map(employees)
            st.dataframe(df.head())
            csv_data = df.to_csv(index=False).encode('utf-8')
            st.download_button("📥 İşçilər Üzrə Bölünmüş CSV-ni Endir", data=csv_data, file_name='is_bolgusu.csv', mime='text/csv')
        else:
            st.error("Xəta: 'ticket_text' adlı sütun yoxdur.")
