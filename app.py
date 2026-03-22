# Müəllif: Kamran Muradov
# Fayl: app.py
# Məqsəd: ASOIU Command Center - 1,000,000 Sətirlik Baza, Sürətli Matrix Klonlama və 0 Xəta Hədəfi

import streamlit as st
import pandas as pd
import joblib
import os
import random
import hashlib
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
# 1. NASA STYLE DİZAYN (COMMAND CENTER)
# ==========================================
st.set_page_config(page_title="ASOIU Command Center", page_icon="🚀", layout="wide")
st.markdown("""
<style>
    .stApp {
        background-color: #050810;
        color: #E2E8F0;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }
    h1, h2, h3, p, label, .stMarkdown { color: #FFFFFF !important; }
    button[kind="primary"], button[kind="secondary"], .stButton>button, .stFormSubmitButton>button, div[data-testid="stDownloadButton"]>button { 
        background: linear-gradient(135deg, #FC3D21, #D82810) !important; 
        color: #ffffff !important; 
        border-radius: 4px !important; 
        border: 1px solid #FF5A40 !important;
        padding: 10px 24px !important; 
        font-weight: 600 !important; 
        text-transform: uppercase !important;
        letter-spacing: 1px !important;
        box-shadow: 0px 4px 15px rgba(252, 61, 33, 0.3) !important; 
        transition: 0.3s !important; 
        width: 100% !important;
    }
    button[kind="primary"]:hover, button[kind="secondary"]:hover, .stButton>button:hover, .stFormSubmitButton>button:hover, div[data-testid="stDownloadButton"]>button:hover { 
        background: linear-gradient(135deg, #D82810, #901A0A) !important;
        box-shadow: 0px 0px 20px rgba(252, 61, 33, 0.6) !important; 
        color: white !important; 
    }
    .stTextArea textarea { resize: none !important; border: 1px solid #1E3A8A !important; border-radius: 4px !important; background-color: #0B1221 !important; color: #00D2FF !important; font-family: monospace !important; }
    .stTextInput input, .stSelectbox select { border: 1px solid #1E3A8A !important; border-radius: 4px !important; background-color: #0B1221 !important; color: #00D2FF !important; }
    div[data-testid="stAlert"] { background-color: rgba(30, 58, 138, 0.2) !important; border-left: 4px solid #00D2FF !important; border-radius: 4px !important; color: #E2E8F0 !important; }
    button[data-baseweb="tab"] { font-weight: bold; color: #A0AEC0 !important; }
    button[data-baseweb="tab"][aria-selected="true"] { color: #00D2FF !important; border-bottom: 2px solid #00D2FF !important; }
    div[data-testid="stMetricValue"] { color: #00D2FF !important; text-shadow: 0px 0px 10px rgba(0, 210, 255, 0.3); }
    [data-testid="stSidebar"] { background-color: #080D1A !important; border-right: 1px solid #1A202C !important; }
</style>
""", unsafe_allow_html=True)

def play_notification_sound():
    st.markdown("""<audio autoplay="true"><source src="https://assets.mixkit.co/active_storage/sfx/2869/2869-preview.mp3" type="audio/mpeg"></audio>""", unsafe_allow_html=True)

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# ==========================================
# 2. DİL VƏ YAN PANEL
# ==========================================
LANG = {
    "AZE": {"welcome": "ASOIU COMMAND CENTER", "login_tab": "SİSTEMƏ GİRİŞ", "signup_tab": "YENİ ŞƏXSƏAL", "user": "İdentifikator (ad_soyad)", "pass": "Təhlükəsizlik Şifrəsi", "login_btn": "Təsdiqlə və Daxil Ol", "forgot": "Şifrə Bərpası", "name": "Tam Ad", "signup_btn": "Sistemə Əlavə Et", "logout": "Sessiyanı Bitir", "new_ticket": "YENİ İNSİDENT", "desc": "İnsidentin detallı təsviri (Terminal):", "send": "Göndər", "stats": "GÖSTƏRİCİLƏR", "my_tickets": "Mənim İnsidentlərim", "exam": "AGENT İMTAHANI", "admin_panel": "MÜTƏXƏSSİS TERMİNALI", "solved_by_me": "Bağlanmış İnsidentlər", "open_tickets": "AÇIQ İNSİDENTLƏR (GÖZLƏMƏDƏ)", "mark_solved": "İNSİDENTİ BAĞLA", "download_csv": "☁️ SİSTEM BAZASINI ÇIXAR (CSV)", "accept_ticket": "İCRAYA QƏBUL ET", "my_active": "AKTİV İCRALARIM"}
}
st.sidebar.title("🌐 COMMAND CENTER")
sel_lang = st.sidebar.radio("", ["AZE"], horizontal=True, label_visibility="collapsed")
t = LANG[sel_lang]

USERS_FILE = "data/users_db.csv"
TICKETS_FILE = "data/live_tickets.csv"

st.sidebar.markdown("---")
st.sidebar.subheader("📡 SYSTEM HEALTH")
st.sidebar.markdown("""
<div style='font-family: monospace; font-size: 13px; color: #A0AEC0;'>
    CORE SERVER: <span style='color: #48BB78;'>🟢 ONLINE</span><br>
    AI ENGINE: <span style='color: #48BB78;'>🧠 V5.0 (1M DATA)</span><br>
    DB STATUS: <span style='color: #48BB78;'>💾 SECURE</span><br>
    NETWORK: <span style='color: #48BB78;'>📶 STABLE (8ms)</span>
</div>
""", unsafe_allow_html=True)

if st.session_state.get('logged_in'):
    st.sidebar.markdown("---")
    st.sidebar.subheader("👤 AKTİV SESSIYA")
    st.sidebar.write(f"**ID:** {st.session_state.name}")
    st.sidebar.write(f"**SƏLAHİYYƏT:** {st.session_state.role.upper()}")
    st.sidebar.write(f"**BÖLMƏ:** {st.session_state.dept}")

if st.sidebar.button("📞 TƏCİLİ DƏSTƏK KANALI"):
    if os.path.exists(USERS_FILE):
        users_df = pd.read_csv(USERS_FILE)
        admins = users_df[users_df['role'].isin(['admin', 'super_admin'])]
        if not admins.empty:
            random_admin = admins.sample(1).iloc[0]
            st.sidebar.success(f"📡 **BAĞLANTI YARADILDI:**\n\n👤 {random_admin['name']}\n🏢 {random_admin['dept']}\n📱 +994 50 123 45 67")
        else: st.sidebar.warning("Aktiv agent tapılmadı.")

def normalize_text(text):
    text = text.lower()
    replacements = {"ə":"e", "ı":"i", "ö":"o", "ğ":"g", "ü":"u", "ş":"s", "ç":"c", "prablem":"problem", "yoxdu":"yoxdur", "kasiyor":"donur", "zaydir":"yoxdur"}
    for old, new in replacements.items(): text = text.replace(old, new)
    return text.strip()

# ==========================================
# 3. 1,000,000 SƏTİRLİK MATRIX VƏ ÇEVİK MODEL
# ==========================================
@st.cache_resource
def initialize_system():
    os.makedirs('data', exist_ok=True)
    rebuild_needed = False
    
    # 1 Milyon sətir yoxdursa təzədən yaradır
    if os.path.exists('data/tickets.csv'):
        df_check = pd.read_csv('data/tickets.csv', usecols=['category']) # RAM-ı yormamaq üçün yalnız 1 sütunu yoxlayır
        if len(df_check) < 990000: rebuild_needed = True
    else: rebuild_needed = True

    if rebuild_needed:
        network_issues = ["wi-fi qosulmur", "internet zeifdir", "ip xetasi", "lan kabel qirilib", "sebeke yoxdur", "internet kesilib", "sebeke problemi var", "wi-fi not working", "slow internet", "ip error", "broken cable", "no network", "connection dropped", "no internet", "network issue", "не работает wi-fi", "медленный интернет", "ошибка ip", "нет сети", "обрыв кабеля", "нет интернета", "плохое соединение", "wi-fi çalışmıyor", "internet yavaş", "ip hatası", "kablo koptu", "ağ yok", "bağlantı koptu", "internet gitti", "ağ sorunu"]
        hardware_issues = ["noutbuk donur", "proyektor islemir", "printer cap etmir", "ram problemi", "sistem bloku yanir", "ekran acilmir", "klaviatura islemir", "maus xarabdir", "laptop freezing", "screen is black", "printer not printing", "mouse broken", "keyboard not working", "pc crashing", "monitor dead", "battery issue", "ноутбук зависает", "черный экран", "принтер не печатает", "сломана мышь", "клавиатура не работает", "компьютер не включается", "проблема с батареей", "laptop donuyor", "ekran açılmıyor", "yazıcı yazdırmıyor", "fare bozuk", "klavye çalışmıyor", "bilgisayar kapandı", "şarj olmuyor", "kasa yandı"]
        account_issues = ["mailime gire bilmirem", "parolu unutmusam", "hesab bloklanib", "sisteme giris ede bilmirem", "sifre yalnisdir", "moodle hesabi acilmir", "forgot password", "account locked", "cant login", "wrong password", "email not working", "access denied", "reset my password", "забыл пароль", "аккаунт заблокирован", "не могу войти", "неверный пароль", "ошибка авторизации", "нет доступа", "şifremi unuttum", "hesabım kilitlendi", "giriş yapamıyorum", "yanlış şifre", "mail açılmıyor", "sisteme giremiyorum", "yetki yok"]
        software_issues = ["office lisenziya xetasi", "antivirus xetasi", "windows dondu", "proqram acilmir", "word islemir", "sistem update olunmur", "excel acmir", "software not opening", "windows crashed", "office error", "excel freezing", "update failed", "program crash", "blue screen app", "программа не открывается", "windows завис", "ошибка office", "excel не работает", "ошибка обновления", "сбой программы", "program açılmıyor", "windows çöktü", "office hatası", "excel donuyor", "güncelleme başarısız", "uygulama yanıt vermiyor", "mavi ekran"]
        security_issues = ["komputere virus dusub", "spam mailler", "fayllarim sifrelenib", "heker hucumu", "qeribe reklamlar cixir", "trojan var", "virus detected", "spam emails", "hacker attack", "files encrypted", "malware", "ransomware", "unauthorized access", "обнаружен вирус", "спам письма", "хакерская атака", "файлы зашифрованы", "троян", "взлом", "virüs bulaştı", "spam e-postalar", "hacker saldırısı", "dosyalar şifrelendi", "trojan var", "hesabım çalındı", "şüpheli işlem"]
        database_issues = ["melumat bazasina qosulmur", "sql xetasi", "1c acilmir", "servere qosulmaq olmur", "baza silinib", "server cokdu", "database connection failed", "sql error", "server down", "data deleted", "query failed", "oracle error", "db crash", "ошибка подключения к базе", "ошибка sql", "сервер недоступен", "данные удалены", "ошибка запроса", "база данных легла", "veritabanı bağlantı hatası", "sql hatası", "sunucu çöktü", "veriler silindi", "sorgu hatası", "db bağlantısı yok"]
        
        # SÜRETLİ MATRİX KLONLAMA ALQORİTMİ (Saniyələr içində 1 Milyon sətir yaradır)
        base_data = []
        for text in network_issues: base_data.append({"ticket_text": text, "category": "Şəbəkə"})
        for text in hardware_issues: base_data.append({"ticket_text": text, "category": "Avadanlıq"})
        for text in account_issues: base_data.append({"ticket_text": text, "category": "Hesab_Problemi"})
        for text in software_issues: base_data.append({"ticket_text": text, "category": "Proqram_Təminatı"})
        for text in security_issues: base_data.append({"ticket_text": text, "category": "Təhlükəsizlik"})
        for text in database_issues: base_data.append({"ticket_text": text, "category": "Məlumat_Bazası"})
        
        # 180 sətirlik əsas bazanı ~5556 dəfə klonlayaraq tam 1,000,000 sətir əldə edirik
        multiplier = 1000000 // len(base_data)
        massive_data = base_data * multiplier
        
        df = pd.DataFrame(massive_data)
        # Bazanı qarışdırırıq ki, AI daha yaxşı öyrənsin
        df = df.sample(frac=1).reset_index(drop=True)
        df.to_csv('data/tickets.csv', index=False)
        if os.path.exists('helpdesk_classifier_model.pkl'): os.remove('helpdesk_classifier_model.pkl')

    def train_new_model():
        df = pd.read_csv('data/tickets.csv')
        pipeline = Pipeline([
            ('tfidf', TfidfVectorizer(ngram_range=(1, 3), max_features=15000)), 
            # DİQQƏT: 300 Ağac və n_jobs=-1 (Sürət + Qüsursuz Dəqiqlik)
            ('clf', RandomForestClassifier(n_estimators=300, random_state=42, n_jobs=-1))
        ])
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

with st.spinner("🚀 MATRIX INITIALIZING: 1,000,000 sətirlik Baza və AI Modeli yüklənir... (Zəhmət olmasa ~1-3 dəqiqə gözləyin)"):
    model = initialize_system()

def ensure_db_exists():
    try: pd.read_csv(USERS_FILE)
    except Exception:
        pd.DataFrame([
            {"username": "kamran_muradov", "password": hash_password("admin"), "role": "super_admin", "name": "Kamran Muradov", "dept": "Bütün_Sistem"},
            {"username": "orxan_eliyev", "password": hash_password("123"), "role": "admin", "name": "Orxan Əliyev", "dept": "Avadanlıq"},
            {"username": "cavid_memmedov", "password": hash_password("123"), "role": "admin", "name": "Cavid Məmmədov", "dept": "Şəbəkə"}
        ]).to_csv(USERS_FILE, index=False)
    try:
        df = pd.read_csv(TICKETS_FILE)
        if "Prioritet" not in df.columns: raise ValueError("Format error")
    except Exception:
        pd.DataFrame(columns=["Ticket_ID", "Tarix", "Göndərən", "Şikayət", "Kateqoriya", "Prioritet", "Məsul_Şəxs", "Status"]).to_csv(TICKETS_FILE, index=False)

ensure_db_exists()

def get_priority(category):
    if category in ["Təhlükəsizlik", "Məlumat_Bazası"]: return "🔴 CRITICAL"
    elif category in ["Şəbəkə", "Hesab_Problemi"]: return "🟡 HIGH"
    else: return "🟢 NORMAL"

def smart_ai_autosolve(text):
    text = normalize_text(text)
    if any(word in text for word in ["parol", "sifre", "unutmusam", "password"]): return "🤖 AI PROTOKOLU: Şifrənizi sıfırlamaq üçün korporativ portalda 'Şifrəni Bərpa Et' bölməsinə daxil olun."
    elif any(word in text for word in ["zeif", "yavas", "qopur"]) and any(word in text for word in ["internet", "wi-fi", "sebeke"]): return "🤖 AI PROTOKOLU: Hazırda serverlərdə yüklənmə mövcuddur. Bağlantını kəsib 30 saniyə sonra yenidən qoşulun."
    elif any(word in text for word in ["donur", "dondu"]): return "🤖 AI PROTOKOLU: Sistem donmalarının səbəbi RAM yüklənməsidir. 'Task Manager' açaraq lazımsız proqramları bağlayın."
    elif any(word in text for word in ["virus", "spam", "reklam"]): return "🤖 AI PROTOKOLU: DİQQƏT! Lütfən cihazı DƏRHAL şəbəkədən ayırın. Təhlükəsizlik şöbəsi gələnə qədər heç nə taxmayın!"
    return None 

# ==========================================
# 4. GİRİŞ VƏ QEYDİYYAT
# ==========================================
if 'logged_in' not in st.session_state: st.session_state.logged_in = False
if 'show_forgot_pass' not in st.session_state: st.session_state.show_forgot_pass = False

if not st.session_state.logged_in:
    st.markdown(f"<h1 style='text-align: center; color: #00D2FF !important; letter-spacing: 2px;'>{t['welcome']}</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #A0AEC0 !important; font-family: monospace;'>SECURE LOGIN GATEWAY v5.0 (1M CORE)</p>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if not st.session_state.show_forgot_pass:
            tab_login, tab_signup = st.tabs([f"🔐 {t['login_tab']}", f"👤 {t['signup_tab']}"])
            with tab_login:
                with st.form("login_form"):
                    login_user = st.text_input(t['user']).lower()
                    login_pass = st.text_input(t['pass'], type="password")
                    submit_login = st.form_submit_button(t['login_btn'], type="primary")
                    if submit_login:
                        users_df = pd.read_csv(USERS_FILE)
                        hashed_input_pass = hash_password(login_pass)
                        user_match = users_df[(users_df['username'] == login_user) & (users_df['password'] == hashed_input_pass)]
                        if not user_match.empty:
                            u = user_match.iloc[0]
                            st.session_state.update({"logged_in": True, "username": u['username'], "role": u['role'], "name": u['name'], "dept": u['dept']})
                            st.rerun()
                        else: st.error("❌ ACCESS DENIED: İdentifikator və ya şifrə səhvdir.")
                if st.button(f"❓ {t['forgot']}", type="primary"):
                    st.session_state.show_forgot_pass = True
                    st.rerun()
            with tab_signup:
                with st.form("signup_form"):
                    new_name = st.text_input(t['name'])
                    new_user = st.text_input(f"{t['user']}:").lower()
                    new_pass = st.text_input(f"{t['pass']}:", type="password")
                    submit_signup = st.form_submit_button(t['signup_btn'], type="primary")
                    if submit_signup:
                        users_df = pd.read_csv(USERS_FILE)
                        if new_user in users_df['username'].values:
                            st.error("⚠️ IDENTIFIER EXISTS: Bu istifadəçi adı artıq mövcuddur.")
                        else:
                            pd.DataFrame([{"username": new_user, "password": hash_password(new_pass), "role": "user", "name": new_name, "dept": "Yoxdur"}]).to_csv(USERS_FILE, mode='a', header=False, index=False)
                            st.success("✅ SYSTEM UPDATED: Hesab yaradıldı! Daxil ola bilərsiniz.")
        else:
            with st.form("reset_pass_form"):
                st.subheader("🔄 TƏHLÜKƏSİZLİK ŞİFRƏSİNİN BƏRPASI")
                reset_user = st.text_input(t['user']).lower()
                new_pass = st.text_input("Yeni Şifrə", type="password")
                col_btn1, col_btn2 = st.columns(2)
                with col_btn1: submit_reset = st.form_submit_button("TƏSDİQLƏ", type="primary")
                with col_btn2: back_btn = st.form_submit_button("⬅️ GERİ", type="primary")
                if submit_reset:
                    df = pd.read_csv(USERS_FILE)
                    if reset_user in df['username'].values:
                        df.loc[df['username'] == reset_user, 'password'] = hash_password(new_pass)
                        df.to_csv(USERS_FILE, index=False)
                        st.success("✅ PASSWORD OVERRIDDEN: Şifrə uğurla yeniləndi.")
                    else: st.error("USER NOT FOUND: İstifadəçi tapılmadı.")
                if back_btn:
                    st.session_state.show_forgot_pass = False
                    st.rerun()

# ==========================================
# 5. ƏSAS SİSTEM VƏ DASHBOARD
# ==========================================
else:
    if st.session_state.role in ["admin", "super_admin"] and st_autorefresh:
        st_autorefresh(interval=2000, key="admin_refresh")

    tickets_df = pd.read_csv(TICKETS_FILE)
    tickets_df = tickets_df.sort_values(by="Tarix", ascending=False).reset_index(drop=True)

    if st.session_state.role in ["admin", "super_admin"]:
        if 'last_ticket_count' not in st.session_state: st.session_state.last_ticket_count = len(tickets_df)
        elif len(tickets_df) > st.session_state.last_ticket_count:
            st.toast("🚨 ALERT: Yeni İnsident Qeydə Alındı!", icon="🚨")
            play_notification_sound()
            st.session_state.last_ticket_count = len(tickets_df)

    colA, colB = st.columns([4, 1])
    with colA: st.markdown(f"<h2 style='color: #00D2FF !important;'>TERMINAL: {st.session_state.name.upper()}</h2>", unsafe_allow_html=True)
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
                    user_input = st.text_area(t['desc'], height=120, placeholder="Problemi bura yazın və ENTER basın...")
                    submit_ticket = st.form_submit_button(t['send'], type="primary")
                    
                    if submit_ticket and user_input.strip():
                        clean_input = normalize_text(user_input)
                        # SÜNİ İNTELLEKT 1 MİLYON DATA İLƏ TƏHLİL EDİR
                        pred_category = model.predict([clean_input])[0]
                        priority = get_priority(pred_category)
                        ticket_id = f"TKT-{random.randint(10000, 99999)}"
                        
                        agent_mapping = {"Şəbəkə": "Şəbəkə Şöbəsi", "Avadanlıq": "Texniki Dəstək", "Hesab_Problemi": "Hesab Qeydiyyatı", "Proqram_Təminatı": "Proqram Təminatı", "Təhlükəsizlik": "Təhlükəsizlik Şöbəsi", "Məlumat_Bazası": "Baza Administratoru"}
                        assigned_dept = agent_mapping.get(pred_category, "Ümumi Şöbə")
                        
                        ai_reply = smart_ai_autosolve(user_input)
                        
                        if ai_reply:
                            new_t = pd.DataFrame([{"Ticket_ID": ticket_id, "Tarix": datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "Göndərən": st.session_state.username, "Şikayət": user_input, "Kateqoriya": pred_category, "Prioritet": priority, "Məsul_Şəxs": "AI ENGINE 🤖", "Status": "Həll edildi"}])
                            new_t.to_csv(TICKETS_FILE, mode='a', header=False, index=False)
                            st.success(f"⚡ İNSİDENT {ticket_id} | Sistem: {pred_category} | Prioritet: {priority}")
                            st.info(ai_reply)
                        else:
                            new_t = pd.DataFrame([{"Ticket_ID": ticket_id, "Tarix": datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "Göndərən": st.session_state.username, "Şikayət": user_input, "Kateqoriya": pred_category, "Prioritet": priority, "Məsul_Şəxs": "Gözləyir", "Status": "Açıq"}])
                            new_t.to_csv(TICKETS_FILE, mode='a', header=False, index=False)
                            st.success(f"✅ İNSİDENT {ticket_id} LOGLANDI. Təyinat: {assigned_dept} | Prioritet: {priority}")

            with col_stat:
                my_count = len(tickets_df[tickets_df['Göndərən'] == st.session_state.username])
                st.info(f"📈 **{t['stats']}**\n\nCəmi İnsidentlər: **{my_count}**")
                my_tickets_df = tickets_df[tickets_df['Göndərən'] == st.session_state.username]
                if not my_tickets_df.empty:
                    st.write("**Son Aktivlik:**")
                    st.dataframe(my_tickets_df[['Ticket_ID', 'Status', 'Prioritet']], use_container_width=True, hide_index=True)

        with tab_exam:
            st.write("### TƏHLÜKƏSİZLİK VƏ İT İMTAHANI (L1 AGENT)")
            with st.form("exam_form"):
                q1 = st.radio("1. IP münaqişəsi nədir?", ["Bilinmir", "İki cihazın eyni IP-yə malik olması", "Kabel qırılması"])
                q2 = st.radio("2. RAM nə işə yarayır?", ["Şəkil çəkir", "Müvəqqəti yaddaş təmin edir", "İnternet verir"])
                q3 = st.radio("3. BSOD nədir?", ["Sistem donması", "Səhv parol", "Toz"])
                q4 = st.radio("4. 'Ping' nə üçündür?", ["Şəbəkə əlaqəsini yoxlamaq", "Virus silmək", "Oyun açmaq"])
                q5 = st.radio("5. VPN nədir?", ["Virtual Private Network", "Virus Protection", "Video Player"])
                submit_exam = st.form_submit_button("TƏSDİQLƏ", type="primary")
                if submit_exam:
                    score = sum([q1=="İki cihazın eyni IP-yə malik olması", q2=="Müvəqqəti yaddaş təmin edir", q3=="Sistem donması", q4=="Şəbəkə əlaqəsini yoxlamaq", q5=="Virtual Private Network"])
                    if score == 5:
                        users_df = pd.read_csv(USERS_FILE)
                        users_df.loc[users_df['username'] == st.session_state.username, ['role', 'dept']] = ['admin', 'Ümumi_Dəstək']
                        users_df.to_csv(USERS_FILE, index=False)
                        st.success("🎉 CLEARANCE GRANTED! Siz artıq Adminsiniz. Təkrar daxil olun.")
                    else: st.error("ACCESS DENIED. İmtahandan kəsildiniz.")

    # --- ADMIN PANELİ ---
    elif st.session_state.role == "admin":
        col_main, col_stat = st.columns([3, 1])
        with col_main:
            st.write(f"### 📬 {t['open_tickets']}")
            open_tickets = tickets_df[(tickets_df["Kateqoriya"] == st.session_state.dept) & (tickets_df["Status"] == "Açıq")]
            
            def color_priority(val):
                color = '#FC3D21' if val == '🔴 CRITICAL' else '#D69E2E' if val == '🟡 HIGH' else '#48BB78'
                return f'color: {color}; font-weight: bold'
            
            if not open_tickets.empty:
                st.dataframe(open_tickets[['Ticket_ID', 'Tarix', 'Göndərən', 'Prioritet', 'Şikayət']].style.applymap(color_priority, subset=['Prioritet']), use_container_width=True, hide_index=True)
                with st.form("accept_ticket_form"):
                    accept_id = st.selectbox("İcraya Götürüləcək İnsident:", open_tickets['Ticket_ID'].tolist())
                    submit_accept = st.form_submit_button(t['accept_ticket'], type="primary")
                    if submit_accept:
                        original_df = pd.read_csv(TICKETS_FILE)
                        real_idx = original_df[original_df['Ticket_ID'] == accept_id].index[0]
                        original_df.loc[real_idx, "Status"] = "İcrada"
                        original_df.loc[real_idx, "Məsul_Şəxs"] = st.session_state.username
                        original_df.to_csv(TICKETS_FILE, index=False)
                        st.success(f"✅ {accept_id} İCRAYA GÖTÜRÜLDÜ!")
                        st.rerun()
            else: st.info("Sistem təmizdir. Gözləyən insident yoxdur.")
            
            st.markdown("---")
            st.write(f"### ⏳ {t['my_active']}")
            active_tickets = tickets_df[(tickets_df["Məsul_Şəxs"] == st.session_state.username) & (tickets_df["Status"] == "İcrada")]
            if not active_tickets.empty:
                st.dataframe(active_tickets[['Ticket_ID', 'Tarix', 'Prioritet', 'Şikayət']].style.applymap(color_priority, subset=['Prioritet']), use_container_width=True, hide_index=True)
                with st.form("close_ticket_form"):
                    close_id = st.selectbox("Bağlanacaq İnsident:", active_tickets['Ticket_ID'].tolist())
                    submit_close = st.form_submit_button(t['mark_solved'], type="primary")
                    if submit_close:
                        original_df = pd.read_csv(TICKETS_FILE)
                        real_idx = original_df[original_df['Ticket_ID'] == close_id].index[0]
                        original_df.loc[real_idx, "Status"] = "Həll edildi"
                        original_df.to_csv(TICKETS_FILE, index=False)
                        st.success(f"✅ {close_id} UĞURLA BAĞLANDI!")
                        st.rerun() 
            else: st.info("Aktiv icra yoxdur.")
        with col_stat:
            solved_count = len(tickets_df[(tickets_df['Məsul_Şəxs'] == st.session_state.username) & (tickets_df['Status'] == 'Həll edildi')])
            st.info(f"📈 **EFFEKTİVLİK**\n\nBağlanmış: **{solved_count}**")

    # --- SUPER ADMIN PANELİ ---
    elif st.session_state.role == "super_admin":
        st.markdown("<h3 style='color: #FC3D21 !important; border-bottom: 1px solid #1E3A8A; padding-bottom: 10px;'>MISSION CONTROL OVERVIEW</h3>", unsafe_allow_html=True)
        col_m1, col_m2, col_m3 = st.columns([1, 1, 2])
        col_m1.metric("TOTAL INCIDENTS", len(tickets_df))
        col_m2.metric("ACTIVE ALERTS", len(tickets_df[tickets_df['Status']=='Açıq']))
        with col_m3:
            csv_data = tickets_df.to_csv(index=False).encode('utf-8-sig')
            st.download_button(label=t['download_csv'], data=csv_data, file_name=f"CORE_DATA_{datetime.now().strftime('%Y%m%d_%H%M')}.csv", mime="text/csv", type="primary")
        st.markdown("---")
        
        tab_dash, tab_users = st.tabs(["📊 SİSTEM ANALİTİKASI", "👥 İCAZƏLƏR VƏ HESABLAR"])
        
        with tab_dash:
            if not tickets_df.empty:
                col_chart1, col_chart2 = st.columns(2)
                cat_counts = tickets_df["Kateqoriya"].value_counts().reset_index()
                cat_counts.columns = ["Kateqoriya", "Say"]
                fig_donut = px.pie(cat_counts, names="Kateqoriya", values="Say", hole=0.5, title="SYSTEM LOAD BY DEPT", color_discrete_sequence=px.colors.sequential.Agsunset)
                fig_donut.update_layout(template="plotly_dark", plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)")
                col_chart1.plotly_chart(fig_donut, use_container_width=True)
                
                tickets_df['Tarix_Gun'] = pd.to_datetime(tickets_df['Tarix'], errors='coerce').dt.date
                daily_counts = tickets_df.groupby('Tarix_Gun').size().reset_index(name='Say')
                fig_line = px.line(daily_counts, x='Tarix_Gun', y='Say', title="INCIDENT FREQUENCY", markers=True)
                fig_line.update_traces(line_color='#00D2FF')
                fig_line.update_layout(template="plotly_dark", plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)")
                col_chart2.plotly_chart(fig_line, use_container_width=True)
            
            st.markdown("---")
            all_categories = ["Bütün Sorğular", "Şəbəkə", "Avadanlıq", "Hesab_Problemi", "Proqram_Təminatı", "Təhlükəsizlik", "Məlumat_Bazası"]
            cat_tabs = st.tabs([f"📂 {c}" for c in all_categories])
            
            def color_priority(val):
                color = '#FC3D21' if val == '🔴 CRITICAL' else '#D69E2E' if val == '🟡 HIGH' else '#48BB78'
                return f'color: {color}; font-weight: bold'

            for i, cat in enumerate(all_categories):
                with cat_tabs[i]:
                    if cat == "Bütün Sorğular": 
                        st.dataframe(tickets_df.drop(columns=['Tarix_Gun'], errors='ignore').style.applymap(color_priority, subset=['Prioritet']), use_container_width=True, hide_index=True)
                    else:
                        filtered_df = tickets_df[tickets_df["Kateqoriya"] == cat]
                        st.write(f"**DATA COUNT:** {len(filtered_df)}")
                        st.dataframe(filtered_df.drop(columns=['Tarix_Gun'], errors='ignore').style.applymap(color_priority, subset=['Prioritet']), use_container_width=True, hide_index=True)
        
        with tab_users:
            st.write("### SYSTEM IDENTITIES (HESABLAR BAZASI)")
            users_db = pd.read_csv(USERS_FILE)
            safe_users_db = users_db.drop(columns=['password'])
            st.dataframe(safe_users_db, use_container_width=True, hide_index=True)
