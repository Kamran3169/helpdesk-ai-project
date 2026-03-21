# Müəllif: Kamran Muradov
# Fayl: app.py
# Məqsəd: ASOIU IT Helpdesk AI - Qeydiyyat Sistemi (Login/Sign Up) və Rollar

import streamlit as st
import pandas as pd
import joblib
import os
from datetime import datetime

# ==========================================
# 1. DİZAYN TƏNZİMLƏMƏLƏRİ (Qırmızı Fon və Oval Künclər)
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
    .stTextArea textarea, .stTextInput input { border: 2px solid #cc0000; border-radius: 15px; background-color: #fff9f9; color: #800000; }
    div[data-testid="stAlert"] { background-color: #ffe6e6; border-left: 5px solid #cc0000; border-radius: 12px; color: #800000; }
</style>
""", unsafe_allow_html=True)

# ==========================================
# 2. VERİLƏNLƏR BAZASININ İNİSİALİZASİYASI (İstifadəçilər və Sorğular)
# ==========================================
os.makedirs('data', exist_ok=True)
USERS_FILE = "data/users_db.csv"
TICKETS_FILE = "data/live_tickets.csv"

# Əgər istifadəçi bazası yoxdursa, Super Admin və Adminlərlə birlikdə yaradırıq
if not os.path.exists(USERS_FILE):
    initial_users = pd.DataFrame([
        {"username": "kamran", "password": "admin", "role": "super_admin", "name": "Kamran Muradov", "dept": "Bütün_Sistem"},
        {"username": "orxan", "password": "123", "role": "admin", "name": "Orxan Əliyev", "dept": "Avadanlıq"},
        {"username": "cavid", "password": "123", "role": "admin", "name": "Cavid Məmmədov", "dept": "Şəbəkə"},
        {"username": "aygun", "password": "123", "role": "admin", "name": "Aygün Həsənova", "dept": "Hesab_Problemi"},
        {"username": "elvin", "password": "123", "role": "admin", "name": "Elvin Qasımov", "dept": "Proqram_Təminatı"}
    ])
    initial_users.to_csv(USERS_FILE, index=False)

# Əgər sorğu bazası yoxdursa yaradırıq
if not os.path.exists(TICKETS_FILE):
    pd.DataFrame(columns=["Tarix", "Göndərən", "Şikayət", "Kateqoriya", "Məsul_Şəxs"]).to_csv(TICKETS_FILE, index=False)

# ==========================================
# 3. SÜNİ İNTELLEKT MODELİNİN YÜKLƏNMƏSİ
# ==========================================
@st.cache_resource
def load_model():
    return joblib.load('helpdesk_classifier_model.pkl')

try:
    model = load_model()
except Exception:
    st.error("Xəta: 'helpdesk_classifier_model.pkl' tapılmadı. Modeli train edin.")
    st.stop()

# ==========================================
# 4. SESSİYA (GİRİŞ) VƏZİYYƏTİNİN İDARƏSİ
# ==========================================
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

# ==========================================
# 5. QEYDİYYAT VƏ GİRİŞ EKRANI (LOG OUT VƏZİYYƏTİ)
# ==========================================
if not st.session_state.logged_in:
    st.markdown("<h1 style='text-align: center;'>ASOIU IT Helpdesk Sisteminə Xoş Gəldiniz</h1>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        # Tablarla Log In və Sign Up ayırırıq
        tab_login, tab_signup = st.tabs(["🔐 Daxil Ol (Log In)", "📝 Qeydiyyat (Sign Up)"])
        
        # --- LOG IN BÖLMƏSİ ---
        with tab_login:
            st.subheader("Sistemə Giriş")
            login_user = st.text_input("İstifadəçi adı:", key="login_user")
            login_pass = st.text_input("Şifrə:", type="password", key="login_pass")
            
            if st.button("Daxil Ol"):
                users_df = pd.read_csv(USERS_FILE)
                # İstifadəçini bazada yoxlayırıq
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
        
        # --- SIGN UP BÖLMƏSİ ---
        with tab_signup:
            st.subheader("Yeni Hesab Yarat")
            st.markdown("Qeydiyyatdan keçən hər kəs avtomatik olaraq **User (İstifadəçi)** təyin edilir.")
            new_name = st.text_input("Tam Adınız (Məs: Əli Əliyev):")
            new_username = st.text_input("Yeni İstifadəçi adı:")
            new_password = st.text_input("Yeni Şifrə:", type="password")
            
            if st.button("Qeydiyyatdan Keç"):
                if new_name and new_username and new_password:
                    users_df = pd.read_csv(USERS_FILE)
                    if new_username in users_df['username'].values:
                        st.error("⚠️ Bu istifadəçi adı artıq mövcuddur. Başqasını seçin.")
                    else:
                        # Yeni istifadəçini bazaya əlavə edirik
                        new_row = pd.DataFrame([{"username": new_username, "password": new_password, "role": "user", "name": new_name, "dept": "Yoxdur"}])
                        new_row.to_csv(USERS_FILE, mode='a', header=False, index=False)
                        st.success("✅ Qeydiyyat uğurla tamamlandı! İndi sol tərəfdəki 'Daxil Ol' bölməsindən sistemə girə bilərsiniz.")
                else:
                    st.warning("Zəhmət olmasa bütün xanaları doldurun.")

# ==========================================
# 6. ƏSAS SİSTEM PANNELLƏRİ (LOG IN OLDUQDAN SONRA)
# ==========================================
else:
    # Üst məlumat və Çıxış düyməsi
    colA, colB = st.columns([4, 1])
    with colA:
        st.subheader(f"👋 Xoş gəldiniz, {st.session_state.name} ({st.session_state.role.upper()})")
    with colB:
        if st.button("🚪 Çıxış Et"):
            st.session_state.logged_in = False
            st.rerun()
    st.markdown("---")

    # ----------------- USER PANELİ (Ancaq şikayət göndərənlər) -----------------
    if st.session_state.role == "user":
        st.title("📝 Yeni Texniki Sorğu Yaradın")
        user_input = st.text_area("Probleminizi ətraflı təsvir edin:", height=150)
        
        if st.button("Sorğunu Göndər"):
            if user_input.strip():
                prediction = model.predict([user_input])[0]
                agent_mapping = {"Şəbəkə": "Cavid Məmmədov", "Avadanlıq": "Orxan Əliyev", "Hesab_Problemi": "Aygün Həsənova", "Proqram_Təminatı": "Elvin Qasımov"}
                assigned_agent = agent_mapping.get(prediction, "Ümumi Şöbə")
                
                # Sorğunu bazaya yazırıq
                new_ticket = pd.DataFrame([{"Tarix": datetime.now().strftime("%Y-%m-%d %H:%M"), "Göndərən": st.session_state.name, "Şikayət": user_input, "Kateqoriya": prediction, "Məsul_Şəxs": assigned_agent}])
                new_ticket.to_csv(TICKETS_FILE, mode='a', header=False, index=False)
                
                st.success(f"✅ Sorğunuz qeydə alındı! AI problemi **{prediction}** olaraq təsnif etdi.")
                st.info(f"👤 Məsul mütəxəssis: **{assigned_agent}**.")
            else:
                st.warning("Problemi yazmadan göndərə bilməzsiniz.")

    # ----------------- ADMIN PANELİ (Mütəxəssislər) -----------------
    elif st.session_state.role == "admin":
        st.title(f"🛠️ İş Paneli: {st.session_state.dept} Şöbəsi")
        tickets_df = pd.read_csv(TICKETS_FILE)
        my_tickets = tickets_df[tickets_df["Kateqoriya"] == st.session_state.dept]
        
        if my_tickets.empty:
            st.success("🎉 Hazırda şöbənizə aid həll edilməmiş problem yoxdur!")
        else:
            st.write(f"Aktiv sorğuların sayı: **{len(my_tickets)}**")
            st.dataframe(my_tickets, use_container_width=True)

    # ----------------- SUPER ADMIN PANELİ (Kamran Muradov) -----------------
    elif st.session_state.role == "super_admin":
        st.title("👑 Super Admin İdarəetmə Mərkəzi")
        st.markdown("Sistemdəki bütün fəaliyyətlərə, şikayətlərə və istifadəçilərə tam nəzarət paneli.")
        
        tab_tickets, tab_users = st.tabs(["🗂️ Bütün Biletlər", "👥 Sistem İstifadəçiləri"])
        
        with tab_tickets:
            tickets_df = pd.read_csv(TICKETS_FILE)
            if tickets_df.empty:
                st.warning("Sistemə hələ heç bir sorğu daxil olmayıb.")
            else:
                col1, col2 = st.columns([1, 2])
                with col1:
                    st.metric("Ümumi Daxil Olan Sorğu", len(tickets_df))
                    st.write("**Şöbələr üzrə statistika:**")
                    st.bar_chart(tickets_df["Kateqoriya"].value_counts(), color="#cc0000")
                with col2:
                    st.write("### Canlı Sorğu Bazası")
                    st.dataframe(tickets_df, use_container_width=True)
                
                if st.button("🗑️ Sorğu Bazasını Sıfırla"):
                    pd.DataFrame(columns=["Tarix", "Göndərən", "Şikayət", "Kateqoriya", "Məsul_Şəxs"]).to_csv(TICKETS_FILE, index=False)
                    st.success("Baza təmizləndi! Səhifəni yeniləyin.")
                    
        with tab_users:
            users_df = pd.read_csv(USERS_FILE)
            st.write("### Qeydiyyatdan Keçmiş Bütün Şəxslər")
            # Şifrələri təhlükəsizlik üçün gizlədərək göstəririk
            display_users = users_df.drop(columns=['password'])
            st.dataframe(display_users, use_container_width=True)
