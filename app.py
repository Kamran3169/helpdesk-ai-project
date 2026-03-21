# Müəllif: Kamran Muradov
# Fayl: app.py
# Məqsəd: ASOIU IT Helpdesk AI - Parol Yeniləmə, Auto-Refresh və Təmiz Dizayn

import streamlit as st
import pandas as pd
import joblib
import os
import random
from datetime import datetime
from sklearn.pipeline import Pipeline
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.ensemble import RandomForestClassifier

# Auto-refresh kitabxanasının yüklənməsi
try:
    from streamlit_autorefresh import st_autorefresh
except ImportError:
    st_autorefresh = None

# ==========================================
# 1. DİZAYN VƏ SƏHİFƏ TƏNZİMLƏMƏLƏRİ
# ==========================================
st.set_page_config(page_title="ASOIU IT Helpdesk AI", page_icon="⚙️", layout="wide")
st.markdown("""
<style>
    .stApp {
        background-color: #ffffff;
        background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 1440 320'%3E%3Cpath fill='%23ffecec' fill-opacity='1' d='M0,224L48,213.3C96,203,192,181,288,186.7C384,192,480,224,576,218.7C672,213,768,171,864,149.3C960,128,1056,128,1152,144C1248,160,1344,192,1392,208L1440,224L1440,320L1392,320C1344,320,1248,320,1152,320C1056,320,960,320,864,320C768,320,672,320,576,320C480,320,384,320,288,320C192,320,96,320,48,320L0,320Z'%3E%3C/path%3E%3C/svg%3E");
        background-attachment: fixed;
        background-size: cover;
    }
    h1, h2, h3, p, label, .stMarkdown { color: #800000 !important; }
    
    .stButton>button { background-color: #cc0000; color: #ffffff; border-radius: 25px; border: none; padding: 10px 24px; font-weight: bold; box-shadow: 0px 4px 6px rgba(204, 0, 0, 0.2); transition: 0.3s; width: 100%;}
    .stButton>button:hover { background-color: #990000; color: white; }
    
    /* resize: none; əlavə edildi ki, text area kənarındakı çıxıntılar ləğv olunsun */
    .stTextArea textarea { resize: none !important; border: 2px solid #cc0000; border-radius: 15px; background-color: #fff9f9; color: #800000; }
    .stTextInput input { border: 2px solid #cc0000; border-radius: 15px; background-color: #fff9f9; color: #800000; }
    div[data-testid="stAlert"] { background-color: #ffe6e6; border-left: 5px solid #cc0000; border-radius: 12px; color: #800000; }
</style>
""", unsafe_allow_html=True)

# ==========================================
# 2. SİSTEMİN ÖZÜNÜ YARATMASI (AUTO-SETUP)
# ==========================================
@st.cache_resource
def initialize_system():
    os.makedirs('data', exist_ok=True)
    if not os.path.exists('data/tickets.csv'):
        network_issues = ["Wi-Fi qoşulmur", "İnternet zəifdir", "IP xətası", "Lan kabel qırılıb"]
        hardware_issues = ["Noutbuk donur", "Proyektor işləmir", "Printer çap etmir", "RAM problemi"]
        account_issues = ["Mailimə girə bilmirəm", "Parolu unutmuşam", "Hesab bloklanıb"]
        software_issues = ["Office lisenziya xətası", "Antivirus xətası", "Windows dondu"]
        
        data = []
        for _ in range(50):
            data.append({"ticket_text": random.choice(network_issues), "category": "Şəbəkə"})
            data.append({"ticket_text": random.choice(hardware_issues), "category": "Avadanlıq"})
            data.append({"ticket_text": random.choice(account_issues), "category": "Hesab_Problemi"})
            data.append({"ticket_text": random.choice(software_issues), "category": "Proqram_Təminatı"})
        pd.DataFrame(data).to_csv('data/tickets.csv', index=False)

    def train_new_model():
        df = pd.read_csv('data/tickets.csv')
        pipeline = Pipeline([('tfidf', TfidfVectorizer()), ('clf', RandomForestClassifier(n_estimators=100, random_state=42))])
        pipeline.fit(df['ticket_text'], df['category'])
        return pipeline

    if not os.path.exists('helpdesk_classifier_model.pkl'):
        model = train_new_model()
        joblib.dump(model, 'helpdesk_classifier_model.pkl')
        return model
    else:
        try: return joblib.load('helpdesk_classifier_model.pkl')
        except Exception:
            model = train_new_model()
            joblib.dump(model, 'helpdesk_classifier_model.pkl')
            return model

with st.spinner("Sistem konfiqurasiya edilir..."):
    model = initialize_system()

# ==========================================
# 3. İSTİFADƏÇİ VƏ SORĞU BAZALARI
# ==========================================
USERS_FILE = "data/users_db.csv"
TICKETS_FILE = "data/live_tickets.csv"

if not os.path.exists(USERS_FILE):
    pd.DataFrame([
        {"username": "kamran", "password": "admin", "role": "super_admin", "name": "Kamran Muradov", "dept": "Bütün_Sistem"},
        {"username": "orxan", "password": "123", "role": "admin", "name": "Orxan Əliyev", "dept": "Avadanlıq"},
        {"username": "cavid", "password": "123", "role": "admin", "name": "Cavid Məmmədov", "dept": "Şəbəkə"},
        {"username": "aygun", "password": "123", "role": "admin", "name": "Aygün Həsənova", "dept": "Hesab_Problemi"},
        {"username": "elvin", "password": "123", "role": "admin", "name": "Elvin Qasımov", "dept": "Proqram_Təminatı"}
    ]).to_csv(USERS_FILE, index=False)

if not os.path.exists(TICKETS_FILE):
    pd.DataFrame(columns=["Tarix", "Göndərən", "Şikayət", "Kateqoriya", "Məsul_Şəxs"]).to_csv(TICKETS_FILE, index=False)

# ==========================================
# 4. GİRİŞ VƏ PAROL YENİLƏMƏ
# ==========================================
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'show_forgot_pass' not in st.session_state:
    st.session_state.show_forgot_pass = False

if not st.session_state.logged_in:
    st.markdown("<h1 style='text-align: center;'>ASOIU IT Helpdesk Sisteminə Xoş Gəldiniz</h1>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if not st.session_state.show_forgot_pass:
            tab_login, tab_signup = st.tabs(["🔐 Daxil Ol", "📝 Qeydiyyat"])
            
            with tab_login:
                st.subheader("Sistemə Giriş")
                login_user = st.text_input("İstifadəçi adı:")
                login_pass = st.text_input("Şifrə:", type="password")
                
                if st.button("Daxil Ol"):
                    users_df = pd.read_csv(USERS_FILE)
                    user_match = users_df[(users_df['username'] == login_user) & (users_df['password'] == login_pass)]
                    if not user_match.empty:
                        user_data = user_match.iloc[0]
                        st.session_state.logged_in = True
                        st.session_state.username = user_data['username']
                        st.session_state.role = user_data['role']
                        st.session_state.name = user_data['name']
                        st.session_state.dept = user_data['dept']
                        st.rerun()
                    else:
                        st.error("❌ İstifadəçi adı və ya şifrə yanlışdır.")
                        
                # PAROLUMU UNUTDUM DÜYMƏSİ
                if st.button("❓ Parolumu Unutdum"):
                    st.session_state.show_forgot_pass = True
                    st.rerun()
            
            with tab_signup:
                st.subheader("Yeni Hesab Yarat")
                new_name = st.text_input("Tam Adınız:")
                new_username = st.text_input("Yeni İstifadəçi adı:")
                new_password = st.text_input("Yeni Şifrə:", type="password")
                if st.button("Qeydiyyatdan Keç"):
                    if new_name and new_username and new_password:
                        users_df = pd.read_csv(USERS_FILE)
                        if new_username in users_df['username'].values:
                            st.error("⚠️ Bu istifadəçi adı mövcuddur.")
                        else:
                            pd.DataFrame([{"username": new_username, "password": new_password, "role": "user", "name": new_name, "dept": "Yoxdur"}]).to_csv(USERS_FILE, mode='a', header=False, index=False)
                            st.success("✅ Qeydiyyat uğurludur! 'Daxil Ol' bölməsindən giriş edin.")
                    else:
                        st.warning("Xanaları doldurun.")
        else:
            # PAROL SIFIRLAMA EKRANI
            st.subheader("🔄 Şifrənin Yenilənməsi")
            reset_user = st.text_input("İstifadəçi adınızı daxil edin:")
            new_pass = st.text_input("Yeni Şifrənizi daxil edin:", type="password")
            
            if st.button("Şifrəni Dəyiş"):
                users_df = pd.read_csv(USERS_FILE)
                if reset_user in users_df['username'].values:
                    users_df.loc[users_df['username'] == reset_user, 'password'] = new_pass
                    users_df.to_csv(USERS_FILE, index=False)
                    st.success("✅ Şifrəniz uğurla yeniləndi!")
                else:
                    st.error("Belə bir istifadəçi tapılmadı.")
            if st.button("⬅️ Geri Qayıt"):
                st.session_state.show_forgot_pass = False
                st.rerun()

# ==========================================
# 5. ƏSAS SİSTEM VƏ AUTO-REFRESH
# ==========================================
else:
    # 5 Saniyəlik Auto-Refresh (Yalnız Adminlər üçün)
    if st.session_state.role in ["admin", "super_admin"] and st_autorefresh is not None:
        st_autorefresh(interval=5000, key="admin_refresh")

    colA, colB = st.columns([4, 1])
    with colA:
        st.subheader(f"👋 Xoş gəldiniz, {st.session_state.name} ({st.session_state.role.upper()})")
    with colB:
        if st.button("🚪 Çıxış Et"):
            st.session_state.logged_in = False
            st.rerun()
    st.markdown("---")

    # --- USER PANELİ ---
    if st.session_state.role == "user":
        st.title("📝 Yeni Texniki Sorğu")
        user_input = st.text_area("Probleminizi daxil edin:", height=150)
        
        if st.button("Sorğunu Göndər"):
            if user_input.strip():
                prediction = model.predict([user_input])[0]
                agent_mapping = {"Şəbəkə": "Cavid Məmmədov", "Avadanlıq": "Orxan Əliyev", "Hesab_Problemi": "Aygün Həsənova", "Proqram_Təminatı": "Elvin Qasımov"}
                assigned_agent = agent_mapping.get(prediction, "Ümumi Şöbə")
                
                pd.DataFrame([{"Tarix": datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "Göndərən": st.session_state.name, "Şikayət": user_input, "Kateqoriya": prediction, "Məsul_Şəxs": assigned_agent}]).to_csv(TICKETS_FILE, mode='a', header=False, index=False)
                st.success(f"✅ Sorğunuz qeydə alındı! Kateqoriya: **{prediction}**")
                st.info(f"👤 Məsul mütəxəssis: **{assigned_agent}**.")
            else:
                st.warning("Problemi yazın.")

    # --- ADMIN PANELİ ---
    elif st.session_state.role == "admin":
        st.title(f"🛠️ İş Paneli: {st.session_state.dept}")
        st.markdown("*Bu panel yeni sorğuları yoxlamaq üçün hər 5 saniyədən bir avtomatik yenilənir.*")
        tickets_df = pd.read_csv(TICKETS_FILE)
        my_tickets = tickets_df[tickets_df["Kateqoriya"] == st.session_state.dept]
        
        if my_tickets.empty:
            st.success("🎉 Şöbənizə aid yeni sorğu yoxdur!")
        else:
            st.write(f"Aktiv sorğular: **{len(my_tickets)}**")
            st.dataframe(my_tickets, use_container_width=True)

    # --- SUPER ADMIN PANELİ ---
    elif st.session_state.role == "super_admin":
        st.title("👑 Super Admin Paneli")
        st.markdown("*Bu panel canlı nəzarət üçün hər 5 saniyədən bir avtomatik yenilənir.*")
        tab_tickets, tab_users = st.tabs(["🗂️ Bütün Biletlər", "👥 İstifadəçilər"])
        
        with tab_tickets:
            tickets_df = pd.read_csv(TICKETS_FILE)
            if tickets_df.empty:
                st.warning("Sistemə heç bir sorğu daxil olmayıb.")
            else:
                col1, col2 = st.columns([1, 2])
                with col1:
                    st.metric("Ümumi Sorğu", len(tickets_df))
                    st.bar_chart(tickets_df["Kateqoriya"].value_counts(), color="#cc0000")
                with col2:
                    st.dataframe(tickets_df, use_container_width=True)
                
                if st.button("🗑️ Bazasını Sıfırla"):
                    pd.DataFrame(columns=["Tarix", "Göndərən", "Şikayət", "Kateqoriya", "Məsul_Şəxs"]).to_csv(TICKETS_FILE, index=False)
                    st.success("Baza təmizləndi!")
                    st.rerun()
                    
        with tab_users:
            users_df = pd.read_csv(USERS_FILE)
            st.dataframe(users_df.drop(columns=['password']), use_container_width=True)
