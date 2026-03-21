# Müəllif: Kamran Muradov
# Fayl: app.py
import streamlit as st
import pandas as pd
import joblib

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

@st.cache_resource
def load_model():
    return joblib.load('helpdesk_classifier_model.pkl')

try:
    model = load_model()
except Exception:
    st.error("Xəta: Model faylı tapılmadı!")
    st.stop()

# --- YENİ ƏLAVƏ: Əməkdaş Məlumat Bazası ---
# Hər kateqoriya üçün uyğun mütəxəssis təyin edirik
employees = {
    "Şəbəkə": "Cavid Məmmədov (Şəbəkə Administratoru)",
    "Avadanlıq": "Orxan Əliyev (Texniki Dəstək Mütəxəssisi)",
    "Hesab_Problemi": "Aygün Həsənova (Sistem Administratoru)",
    "Proqram_Təminatı": "Elvin Qasımov (Proqram Təminatı Mühəndisi)"
}

st.title("IT Sorğularının Avtomatlaşdırılmış Təsnifatı")
st.markdown("Şikayəti daxil edin və Süni İntellekt onu dərhal müvafiq departamentə və **aidiyyəti əməkdaşa** yönləndirsin.")

tab1, tab2 = st.tabs(["📝 Anında Analiz", "📁 Toplu CSV Analizi"])

with tab1:
    user_input = st.text_area("İstifadəçi Şikayəti:", height=120, placeholder="Məsələn: Korporativ mailimə daxil ola bilmirəm...")
    
    if st.button("Təhlil Et və Yönləndir"):
        if user_input.strip():
            # 1. Kateqoriyanı tapırıq
            prediction = model.predict([user_input])[0]
            
            # 2. Həmin kateqoriyaya uyğun işçini tapırıq
            assigned_agent = employees.get(prediction, "Ümumi Dəstək Şöbəsi")
            
            # 3. Nəticələri ekranda göstəririk
            st.success(f"📌 **Təyin Edilmiş Kateqoriya:** {prediction}")
            st.info(f"👤 **Sorğu Təyin Edildi:** {assigned_agent}")
            st.write(f"Sizin sorğunuz icraya götürüldü. Tezliklə {assigned_agent.split(' ')[0]} sizinlə əlaqə saxlayacaq.")
        else:
            st.warning("Zəhmət olmasa problemi tam ifadə edin.")

with tab2:
    st.markdown("İçərisində **`ticket_text`** sütunu olan CSV faylını bura yükləyin.")
    uploaded_file = st.file_uploader("Data Faylını Seçin", type=["csv"])
    
    if uploaded_file:
        df = pd.read_csv(uploaded_file)
        if 'ticket_text' in df.columns:
            # Həm kateqoriyanı, həm də əməkdaşı tapıb cədvələ əlavə edirik
            df['Təyin_Edilmiş_Kateqoriya'] = model.predict(df['ticket_text'].fillna(""))
            df['Təyin_Edilmiş_Əməkdaş'] = df['Təyin_Edilmiş_Kateqoriya'].map(employees)
            
            st.write("### Nəticənin Önizləməsi (İlk 5 sətir):")
            st.dataframe(df.head())
            
            csv_data = df.to_csv(index=False).encode('utf-8')
            st.download_button("📥 İşçilər Üzrə Bölünmüş CSV-ni Endir", data=csv_data, file_name='is_bolgusu_ticketler.csv', mime='text/csv')
        else:
            st.error("Xəta: Yüklədiyiniz faylda 'ticket_text' adlı sütun yoxdur.")