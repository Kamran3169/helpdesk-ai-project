# Müəllif: Kamran Muradov
# Fayl: app.py
# Məqsəd: ASOIU IT Helpdesk AI - Səsli Bildiriş, Müasir İkonlar və Data Vizualizasiyası

import streamlit as st
import pandas as pd
import joblib
import os
import random
from datetime import datetime
from sklearn.pipeline import Pipeline
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.ensemble import RandomForestClassifier
import plotly.express as px

try:
    from streamlit_autorefresh import st_autorefresh
except ImportError:
    st_autorefresh = None

# ==========================================
# 1. DİZAYN VƏ SƏHİFƏ TƏNZİMLƏMƏLƏRİ
# ==========================================
st.set_page_config(page_title="ASOIU IT Helpdesk AI", page_icon="💠", layout="wide")
st.markdown("""
<style>
    .stApp {
        background-color: #ffffff;
        background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 1440 320'%3E%3Cpath fill='%23ffecec' fill-opacity='1' d='M0,224L48,213.3C96,203,192,181,288,186.7C384,192,480,224,576,218.7C672,213,768,171,864,149.3C960,128,1056,128,1152,144C1248,160,1344,192,1392,208L1440,224L1440,320L1392,320C1344,320,1248,320,1152,320C1056,320,960,320,864,320C768,320,672,320,576,320C480,320,384,320,288,320C192,320,96,320,48,320L0,320Z'%3E%3C/path%3E%3C/svg%3E");
        background-attachment: fixed;
        background-size: cover;
    }
    h1, h2, h3, p, label, .stMarkdown { color: #5c0000 !important; }
    
    button[kind="primary"], button[kind="secondary"], .stButton>button, .stFormSubmitButton>button, div[data-testid="stDownloadButton"]>button { 
        background-color: #cc0000 !important; color: #ffffff !important; border-radius: 25px !important; border: none !important; padding: 10px 24px !important; font-weight: bold !important; box-shadow: 0px 4px 6px rgba(204, 0, 0, 0.3) !important; transition: 0.3s !important; width: 100% !important;
    }
    button[kind="primary"]:hover, button[kind="secondary"]:hover, .stButton>button:hover, .stFormSubmitButton>button:hover, div[data-testid="stDownloadButton"]>button:hover { 
        background-color: #8b0000 !important; color: white !important; 
    }
    
    .stTextArea textarea { resize: none !important; border: 2px solid #b30000; border-radius: 15px; background-color: #fffafb; color: #5c0000; }
    .stTextInput input, .stSelectbox select { border: 2px solid #b30000; border-radius: 15px; background-color: #fffafb; color: #5c0000; }
    div[data-testid="stAlert"] { background-color: #fff0f0; border-left: 5px solid #cc0000; border-radius: 12px; color: #5c0000; }
    button[data-baseweb="tab"] { font-weight: bold; color: #cc0000 !important; }
</style>
""", unsafe_allow_html=True)

# Səs Oynatmaq üçün Funksiya (WhatsApp iOS Pop Sound)
def play_notification_sound():
    audio_html = """
        <audio autoplay="true">
        <source src="https://assets.mixkit.co/active_storage/sfx/2869/2869-preview.mp3" type="audio/mpeg">
        </audio>
    """
    st.markdown(audio_html, unsafe_allow_html=True)

# ==========================================
# 2. DİL SÖZLÜYÜ (Müasir İkonlar)
# ==========================================
LANG = {
    "AZE": {"welcome": "Sistemə Xoş Gəldiniz", "login_tab": "Daxil Ol", "signup_tab": "Qeydiyyat", "user": "İstifadəçi adı", "pass": "Şifrə", "login_btn": "Daxil Ol", "forgot": "Parolumu Unutdum", "name": "Tam Adınız", "signup_btn": "Qeydiyyatdan Keç", "logout": "Çıxış Et", "new_ticket": "Yeni Sorğu", "desc": "Problemi daxil edin:", "send": "Göndər", "stats": "Statistika", "my_tickets": "Göndərdiyim sorğular", "exam": "Admin İmtahanı", "admin_panel": "İş Paneli", "solved_by_me": "Həll etdiklərim", "open_tickets": "Açıq Sorğular", "mark_solved": "Həll edildi", "download_csv": "☁️ CSV Yüklə"},
    "ENG": {"welcome": "Welcome to the System", "login_tab": "Log In", "signup_tab": "Sign Up", "user": "Username", "pass": "Password", "login_btn": "Log In", "forgot": "Forgot Password", "name": "Full Name", "signup_btn": "Sign Up", "logout": "Log Out", "new_ticket": "New Ticket", "desc": "Describe the problem:", "send": "Submit", "stats": "Statistics", "my_tickets": "Submitted", "exam": "Admin Exam", "admin_panel": "Work Panel", "solved_by_me": "Resolved by me", "open_tickets": "Open Tickets", "mark_solved": "Mark Resolved", "download_csv": "☁️ Download CSV"},
    "RUS": {"welcome": "Добро пожаловать", "login_tab": "Войти", "signup_tab": "Регистрация", "user": "Имя пользователя", "pass": "Пароль", "login_btn": "Войти", "forgot": "Забыл пароль", "name": "Полное имя", "signup_btn": "Зарегистрироваться", "logout": "Выйти", "new_ticket": "Новый запрос", "desc": "Опишите проблему:", "send": "Отправить", "stats": "Статистика", "my_tickets": "Мои запросы", "exam": "Экзамен Админа", "admin_panel": "Панель", "solved_by_me": "Решенные мной", "open_tickets": "Открытые", "mark_solved": "Решено", "download_csv": "☁️ Скачать CSV"},
    "TR": {"welcome": "Sisteme Hoş Geldiniz", "login_tab": "Giriş Yap", "signup_tab": "Kayıt Ol", "user": "Kullanıcı Adı", "pass": "Şifre", "login_btn": "Giriş Yap", "forgot": "Şifremi Unuttum", "name": "Tam Adınız", "signup_btn": "Kayıt Ol", "logout": "Çıkış Yap", "new_ticket": "Yeni Talep", "desc": "Sorunu açıklayın:", "send": "Gönder", "stats": "İstatistikler", "my_tickets": "Taleplerim", "exam": "Admin Sınavı", "admin_panel": "Çalışma Paneli", "solved_by_me": "Çözdüklerim", "open_tickets": "Açık Talepler", "mark_solved": "Çözüldü", "download_csv": "☁️ CSV İndir"}
}

st.sidebar.title("🌍 Language")
sel_lang = st.sidebar.radio("", ["AZE", "ENG", "RUS", "TR"], horizontal=True, label_visibility="collapsed")
t = LANG[sel_lang]

# ==========================================
# 3. AUTO-SETUP & DB
# ==========================================
@st.cache_resource
def initialize_system():
    os.makedirs('data', exist_ok=True)
    rebuild_needed = False
    if os.path.exists('data/tickets.csv'):
        if len(pd.read_csv('data/tickets.csv')['category'].unique()) < 6: rebuild_needed = True
    else: rebuild_needed = True

    if rebuild_needed:
        network_issues = ["Wi-Fi qoşulmur", "İnternet zəifdir", "IP xətası", "Lan kabel qırılıb"]
        hardware_issues = ["Noutbuk donur", "Proyektor işləmir", "Printer çap etmir", "RAM problemi"]
        account_issues = ["Mailimə girə bilmirəm", "Parolu unutmuşam", "Hesab bloklanıb"]
        software_issues = ["Office lisenziya xətası", "Antivirus xətası", "Windows dondu"]
        security_issues = ["Kompüterə virus düşüb", "Spam maillər", "Fayllarım şifrələnib"]
        database_issues = ["Məlumat bazasına qoşulmur", "SQL xətası", "1C açılmır"]
        
        data = []
        for _ in range(50):
            data.append({"ticket_text": random.choice(network_issues), "category": "Şəbəkə"})
            data.append({"ticket_text": random.choice(hardware_issues), "category": "Avadanlıq"})
            data.append({"ticket_text": random.choice(account_issues), "category": "Hesab_Problemi"})
            data.append({"ticket_text": random.choice(software_issues), "category": "Proqram_Təminatı"})
            data.append({"ticket_text": random.choice(security_issues), "category": "Təhlükəsizlik"})
            data.append({"ticket_text": random.choice(database_issues), "category": "Məlumat_Bazası"})
        pd.DataFrame(data).to_csv('data/tickets.csv', index=False)
        if os.path.exists('helpdesk_classifier_model.pkl'): os.remove('helpdesk_classifier_model.pkl')

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

model = initialize_system()

USERS_FILE = "data/users_db.csv"
TICKETS_FILE = "data/live_tickets.csv"

def ensure_db_exists():
    try: pd.read_csv(USERS_FILE)
    except Exception:
        pd.DataFrame([
            {"username": "kamran", "password": "admin", "role": "super_admin", "name": "Kamran Muradov", "dept": "Bütün_Sistem"},
            {"username": "orxan", "password": "123", "role": "admin", "name": "Orxan Əliyev", "dept": "Avadanlıq"},
            {"username": "cavid", "password": "123", "role": "admin", "name": "Cavid Məmmədov", "dept": "Şəbəkə"}
        ]).to_csv(USERS_FILE, index=False)
    try:
        df = pd.read_csv(TICKETS_FILE)
        if "Status" not in df.columns: raise ValueError("Format error")
    except Exception:
        pd.DataFrame(columns=["Tarix", "Göndərən", "Şikayət", "Kateqoriya", "Məsul_Şəxs", "Status"]).to_csv(TICKETS_FILE, index=False)

ensure_db_exists()

# ==========================================
# 4. GİRİŞ VƏ QEYDİYYAT
# ==========================================
if 'logged_in' not in st.session_state: st.session_state.logged_in = False
if 'show_forgot_pass' not in st.session_state: st.session_state.show_forgot_pass = False

if not st.session_state.logged_in:
    st.markdown(f"<h1 style='text-align: center;'>{t['welcome']}</h1>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if not st.session_state.show_forgot_pass:
            tab_login, tab_signup = st.tabs([f"🔐 {t['login_tab']}", f"👤 {t['signup_tab']}"])
            with tab_login:
                with st.form("login_form"):
                    login_user = st.text_input(t['user'])
                    login_pass = st.text_input(t['pass'], type="password")
                    submit_login = st.form_submit_button(t['login_btn'], type="primary")
                    if submit_login:
                        users_df = pd.read_csv(USERS_FILE)
                        user_match = users_df[(users_df['username'] == login_user) & (users_df['password'] == login_pass)]
                        if not user_match.empty:
                            u = user_match.iloc[0]
                            st.session_state.update({"logged_in": True, "username": u['username'], "role": u['role'], "name": u['name'], "dept": u['dept']})
                            st.rerun()
                        else: st.error("❌ Xəta / Error")
                if st.button(f"❓ {t['forgot']}", type="primary"):
                    st.session_state.show_forgot_pass = True
                    st.rerun()
                    
            with tab_signup:
                with st.form("signup_form"):
                    new_name = st.text_input(t['name'])
                    new_user = st.text_input(f"{t['user']} (Yeni):")
                    new_pass = st.text_input(f"{t['pass']} (Yeni):", type="password")
                    submit_signup = st.form_submit_button(t['signup_btn'], type="primary")
                    if submit_signup:
                        pd.DataFrame([{"username": new_user, "password": new_pass, "role": "user", "name": new_name, "dept": "Yoxdur"}]).to_csv(USERS_FILE, mode='a', header=False, index=False)
                        st.success("✅ OK")
        else:
            with st.form("reset_pass_form"):
                st.subheader("🔄 Şifrənin Yenilənməsi")
                reset_user = st.text_input(t['user'])
                new_pass = st.text_input(t['pass'], type="password")
                col_btn1, col_btn2 = st.columns(2)
                with col_btn1: submit_reset = st.form_submit_button("OK", type="primary")
                with col_btn2: back_btn = st.form_submit_button("⬅️ Back", type="primary")
                if submit_reset:
                    df = pd.read_csv(USERS_FILE)
                    df.loc[df['username'] == reset_user, 'password'] = new_pass
                    df.to_csv(USERS_FILE, index=False)
                    st.success("✅ Şifrə yeniləndi")
                if back_btn:
                    st.session_state.show_forgot_pass = False
                    st.rerun()

# ==========================================
# 5. ƏSAS SİSTEM VƏ VİZUALİZASİYA
# ==========================================
else:
    if st.session_state.role in ["admin", "super_admin"] and st_autorefresh:
        st_autorefresh(interval=1500, key="admin_refresh")

    tickets_df = pd.read_csv(TICKETS_FILE)

    # --- SƏSLİ BİLDİRİŞ SİSTEMİ ---
    if st.session_state.role in ["admin", "super_admin"]:
        if 'last_ticket_count' not in st.session_state:
            st.session_state.last_ticket_count = len(tickets_df)
        elif len(tickets_df) > st.session_state.last_ticket_count:
            st.toast("🔔 Yeni sorğu daxil oldu!", icon="⚡")
            play_notification_sound()  # iPhone/WhatsApp səsi oynadılır
            st.session_state.last_ticket_count = len(tickets_df)

    colA, colB = st.columns([4, 1])
    with colA: st.subheader(f"👋 {st.session_state.name} ({st.session_state.role.upper()})")
    with colB:
        if st.button(f"🚪 {t['logout']}", type="primary"):
            st.session_state.logged_in = False
            st.rerun()
    st.markdown("---")

    # --- USER PANELİ ---
    if st.session_state.role == "user":
        tab_new, tab_exam = st.tabs([f"✍️ {t['new_ticket']}", f"🎯 {t['exam']}"])
        with tab_new:
            col_main, col_stat = st.columns([3, 1])
            with col_main:
                with st.form("ticket_form", clear_on_submit=True):
                    user_input = st.text_area(t['desc'], height=120)
                    submit_ticket = st.form_submit_button(t['send'], type="primary")
                    if submit_ticket and user_input.strip():
                        pred = model.predict([user_input])[0]
                        new_t = pd.DataFrame([{"Tarix": datetime.now().strftime("%Y-%m-%d %H:%M"), "Göndərən": st.session_state.username, "Şikayət": user_input, "Kateqoriya": pred, "Məsul_Şəxs": "Gözləyir", "Status": "Açıq"}])
                        new_t.to_csv(TICKETS_FILE, mode='a', header=False, index=False)
                        st.success(f"✅ Kateqoriya: {pred}")
            with col_stat:
                my_count = len(tickets_df[tickets_df['Göndərən'] == st.session_state.username])
                st.info(f"📈 **{t['stats']}**\n\n{t['my_tickets']}: **{my_count}**")

        with tab_exam:
            st.write("### Helpdesk Mütəxəssisi İmtahanı")
            with st.form("exam_form"):
                q1 = st.radio("1. IP münaqişəsi nədir?", ["Bilinmir", "İki cihazın eyni IP-yə malik olması", "Kabel qırılması"])
                q2 = st.radio("2. RAM nə işə yarayır?", ["Şəkil çəkir", "Müvəqqəti yaddaş təmin edir", "İnternet verir"])
                q3 = st.radio("3. Mavi ekran (BSOD) nəyin xətasıdır?", ["Sistem/Hardware donması", "Səhv parol", "Toz"])
                q4 = st.radio("4. 'Ping' komandası nə üçündür?", ["Musiqi açmaq", "Şəbəkə əlaqəsini yoxlamaq", "Virus silmək"])
                q5 = st.radio("5. VPN nədir?", ["Virtual Private Network", "Video Player Network", "Virus Protection"])
                q6 = st.radio("6. SSD ilə HDD fərqi nədir?", ["Rəngi", "Sürəti və texnologiyası", "Ölçüsü"])
                q7 = st.radio("7. Phishing (Fişinq) nədir?", ["Balıq tutmaq", "Kiber fırıldaqçılıq növü", "Kod dili"])
                q8 = st.radio("8. DHCP nə iş görür?", ["IP ünvanlarını avtomatik paylayır", "Ekranı təmizləyir", "Məlumat silir"])
                q9 = st.radio("9. DNS nədir?", ["Domain Name System", "Data Network System", "Digital Node Server"])
                q10 = st.radio("10. Active Directory harada istifadə olunur?", ["Oyunlarda", "İstifadəçi və kompüterlərin idarə edilməsində", "Dizaynda"])

                submit_exam = st.form_submit_button("İmtahanı Bitir", type="primary")
                if submit_exam:
                    score = sum([q1=="İki cihazın eyni IP-yə malik olması", q2=="Müvəqqəti yaddaş təmin edir", q3=="Sistem/Hardware donması", q4=="Şəbəkə əlaqəsini yoxlamaq", q5=="Virtual Private Network", q6=="Sürəti və texnologiyası", q7=="Kiber fırıldaqçılıq növü", q8=="IP ünvanlarını avtomatik paylayır", q9=="Domain Name System", q10=="İstifadəçi və kompüterlərin idarə edilməsində"])
                    st.write(f"Sizin balınız: **{score}/10**")
                    if score >= 8:
                        users_df = pd.read_csv(USERS_FILE)
                        users_df.loc[users_df['username'] == st.session_state.username, ['role', 'dept']] = ['admin', 'Ümumi_Dəstək']
                        users_df.to_csv(USERS_FILE, index=False)
                        st.success("🎉 TƏBRİKLƏR! Siz artıq Adminsiniz. Çıxış edib yenidən daxil olun.")
                    else: st.error("Kəsildiniz. Yenidən cəhd edin.")

    # --- ADMIN PANELİ ---
    elif st.session_state.role == "admin":
        st.title(f"⚡ {t['admin_panel']}: {st.session_state.dept}")
        col_main, col_stat = st.columns([3, 1])
        with col_main:
            my_tickets = tickets_df[(tickets_df["Kateqoriya"] == st.session_state.dept) & (tickets_df["Status"] == "Açıq")]
            st.write(f"### 📬 {t['open_tickets']}: {len(my_tickets)}")
            st.dataframe(my_tickets, use_container_width=True)
            if not my_tickets.empty:
                with st.form("close_ticket_form"):
                    close_id = st.selectbox("Təsdiqləmək üçün sorğunun indeksini seçin (Sol sütun):", my_tickets.index)
                    submit_close = st.form_submit_button(t['mark_solved'], type="primary")
                    if submit_close:
                        tickets_df.loc[close_id, "Status"] = "Həll edildi"
                        tickets_df.loc[close_id, "Məsul_Şəxs"] = st.session_state.username
                        tickets_df.to_csv(TICKETS_FILE, index=False)
                        st.success("✅ Sorğu 'Həll Edildi' olaraq təsdiqləndi!")
                        st.rerun() 
        with col_stat:
            solved_count = len(tickets_df[(tickets_df['Məsul_Şəxs'] == st.session_state.username) & (tickets_df['Status'] == 'Həll edildi')])
            st.info(f"📈 **{t['stats']}**\n\n{t['solved_by_me']}: **{solved_count}**")

    # --- SUPER ADMIN PANELİ (Data Vizualizasiyası ilə) ---
    elif st.session_state.role == "super_admin":
        st.title("🛡️ Super Admin Paneli")
        
        # Üst Panel: Statistika və Yükləmə
        col_m1, col_m2, col_m3 = st.columns([1, 1, 2])
        col_m1.metric("Ümumi Baza Sorğuları", len(tickets_df))
        col_m2.metric("Açıq Sorğular", len(tickets_df[tickets_df['Status']=='Açıq']))
        with col_m3:
            csv_data = tickets_df.to_csv(index=False).encode('utf-8')
            st.download_button(label=t['download_csv'], data=csv_data, file_name=f"helpdesk_baza_{datetime.now().strftime('%Y%m%d_%H%M')}.csv", mime="text/csv", type="primary")
        
        st.markdown("---")
        
        # Qrafiklər Bölməsi (Plotly)
        st.write("### 📊 Ümumi Sistem Analitikası")
        if not tickets_df.empty:
            col_chart1, col_chart2 = st.columns(2)
            
            # 1. Donut Chart (Kateqoriyalar Üzrə)
            cat_counts = tickets_df["Kateqoriya"].value_counts().reset_index()
            cat_counts.columns = ["Kateqoriya", "Say"]
            fig_donut = px.pie(cat_counts, names="Kateqoriya", values="Say", hole=0.5, 
                               title="Şöbələr Üzrə Yük Dağılımı", color_discrete_sequence=px.colors.sequential.RdBu)
            col_chart1.plotly_chart(fig_donut, use_container_width=True)
            
            # 2. Line Chart (Günlük Trendlər)
            # Tarixi formata salırıq ki, qrafik günləri birləşdirə bilsin
            tickets_df['Tarix_Gun'] = pd.to_datetime(tickets_df['Tarix'], errors='coerce').dt.date
            daily_counts = tickets_df.groupby('Tarix_Gun').size().reset_index(name='Say')
            fig_line = px.line(daily_counts, x='Tarix_Gun', y='Say', title="Günlük Daxil Olan Sorğuların Dinamikası", markers=True)
            fig_line.update_traces(line_color='#8b0000')
            col_chart2.plotly_chart(fig_line, use_container_width=True)
        else:
            st.info("Qrafiklərin qurulması üçün hələ bazada heç bir məlumat yoxdur.")

        st.markdown("---")
        
        # Sekməli İdarəetmə Paneli
        all_categories = ["Bütün Sorğular", "Şəbəkə", "Avadanlıq", "Hesab_Problemi", "Proqram_Təminatı", "Təhlükəsizlik", "Məlumat_Bazası"]
        cat_tabs = st.tabs([f"📂 {c}" for c in all_categories])
        
        for i, cat in enumerate(all_categories):
            with cat_tabs[i]:
                if cat == "Bütün Sorğular": 
                    st.dataframe(tickets_df.drop(columns=['Tarix_Gun'], errors='ignore'), use_container_width=True)
                else:
                    filtered_df = tickets_df[tickets_df["Kateqoriya"] == cat]
                    st.write(f"**{cat}** üzrə cəmi sorğu: **{len(filtered_df)}**")
                    st.dataframe(filtered_df.drop(columns=['Tarix_Gun'], errors='ignore'), use_container_width=True)
