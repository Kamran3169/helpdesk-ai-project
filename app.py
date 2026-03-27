# Müəllif: Kamran Muradov
# Fayl: app.py
# Məqsəd: ASOIU Command Center v7.0 - Soft & Modern SaaS UI (Hybrid NLP, 1M Data, Zero-Error)

import streamlit as st
import pandas as pd
import joblib
import os
import random
import hashlib
from datetime import datetime
from sklearn.pipeline import Pipeline
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.svm import LinearSVC
import plotly.express as px

try:
    from streamlit_autorefresh import st_autorefresh
except ImportError:
    st_autorefresh = None

# ==========================================
# 1. SOFT & MODERN SAAS DİZAYNI
# ==========================================
st.set_page_config(page_title="ASOIU Helpdesk", page_icon="💠", layout="wide")
st.markdown("""
<style>
    /* Yumşaq və Müasir Arxa Fon (Soft Light) */
    .stApp { background-color: #F4F7F6; color: #2D3748; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; }
    h1, h2, h3, p, label, .stMarkdown { color: #2D3748 !important; }
    
    /* Zərif Pastel Mavi/Bənövşəyi Düymələr */
    button[kind="primary"], button[kind="secondary"], .stButton>button, .stFormSubmitButton>button, div[data-testid="stDownloadButton"]>button { 
        background: linear-gradient(135deg, #84A9FF, #6A82FB) !important; color: #ffffff !important; border-radius: 8px !important; border: none !important;
        padding: 10px 24px !important; font-weight: 600 !important; text-transform: uppercase !important; letter-spacing: 1px !important;
        box-shadow: 0px 4px 10px rgba(106, 130, 251, 0.25) !important; transition: 0.3s !important; width: 100% !important;
    }
    button[kind="primary"]:hover, button[kind="secondary"]:hover, .stButton>button:hover, .stFormSubmitButton>button:hover, div[data-testid="stDownloadButton"]>button:hover { 
        background: linear-gradient(135deg, #6A82FB, #84A9FF) !important; box-shadow: 0px 4px 15px rgba(106, 130, 251, 0.4) !important; color: white !important; transform: translateY(-1px);
    }
    
    /* Açıq rəngli, zərif formalar */
    .stTextArea textarea { resize: none !important; border: 1px solid #E2E8F0 !important; border-radius: 8px !important; background-color: #FFFFFF !important; color: #2D3748 !important; font-family: sans-serif !important; box-shadow: inset 0px 1px 3px rgba(0,0,0,0.05); }
    .stTextInput input, .stSelectbox select { border: 1px solid #E2E8F0 !important; border-radius: 8px !important; background-color: #FFFFFF !important; color: #2D3748 !important; box-shadow: inset 0px 1px 3px rgba(0,0,0,0.05); }
    
    /* Bildiriş qutuları (Soft kölgə ilə) */
    div[data-testid="stAlert"] { background-color: #FFFFFF !important; border-left: 4px solid #6A82FB !important; border-radius: 8px !important; color: #4A5568 !important; box-shadow: 0px 2px 8px rgba(0,0,0,0.04) !important; }
    
    /* Sekmələr (Tabs) */
    button[data-baseweb="tab"] { font-weight: bold; color: #A0AEC0 !important; }
    button[data-baseweb="tab"][aria-selected="true"] { color: #6A82FB !important; border-bottom: 2px solid #6A82FB !important; }
    
    /* Metriklər (Gözoxşayan rənglər) */
    div[data-testid="stMetricValue"] { color: #6A82FB !important; font-weight: 700; }
    
    /* Yan Panel (Ağ və Təmiz) */
    [data-testid="stSidebar"] { background-color: #FFFFFF !important; border-right: 1px solid #E2E8F0 !important; }
</style>
""", unsafe_allow_html=True)

def play_notification_sound():
    st.markdown("""<audio autoplay="true"><source src="https://assets.mixkit.co/active_storage/sfx/2869/2869-preview.mp3" type="audio/mpeg"></audio>""", unsafe_allow_html=True)

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# ==========================================
# 2. QARA QUTU (AUDIT LOGS) VƏ DİL
# ==========================================
LANG = {
    "AZE": {"welcome": "ASOIU İT Dəstək Mərkəzi", "login_tab": "Sistemə Giriş", "signup_tab": "Yeni Qeydiyyat", "user": "İdentifikator (ad_soyad)", "pass": "Şifrə", "login_btn": "Daxil Ol", "forgot": "Şifrə Bərpası", "name": "Tam Ad", "signup_btn": "Hesab Yarat", "logout": "Sistemdən Çıx", "new_ticket": "YENİ İNSİDENT", "desc": "Problemin detallı təsviri:", "send": "Təhlil Et və Göndər", "stats": "GÖSTƏRİCİLƏR", "my_tickets": "Mənim İnsidentlərim", "exam": "AGENT İMTAHANI", "admin_panel": "MÜTƏXƏSSİS PANELİ", "solved_by_me": "Bağlanmış İnsidentlər", "open_tickets": "AÇIQ İNSİDENTLƏR (GÖZLƏMƏDƏ)", "mark_solved": "İNSİDENTİ BAĞLA", "download_csv": "☁️ SİSTEM BAZASINI ÇIXAR (CSV)", "accept_ticket": "İCRAYA QƏBUL ET", "my_active": "AKTİV İCRALARIM"}
}
st.sidebar.title("🌐 ASOIU Helpdesk")
sel_lang = st.sidebar.radio("", ["AZE"], horizontal=True, label_visibility="collapsed")
t = LANG[sel_lang]

USERS_FILE = "data/users_db.csv"
TICKETS_FILE = "data/live_tickets.csv"
LOGS_FILE = "data/system_logs.csv"

def add_log(action, username="Sistem"):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_df = pd.DataFrame([{"Tarix": timestamp, "İstifadəçi": username, "Əməliyyat": action}])
    log_df.to_csv(LOGS_FILE, mode='a', header=not os.path.exists(LOGS_FILE), index=False)

st.sidebar.markdown("---")
st.sidebar.subheader("📡 Sistem Statusu")
# Yumşaq rənglərlə status paneli
st.sidebar.markdown("""
<div style='font-size: 14px; color: #4A5568;'>
    <b>Əsas Server:</b> <span style='color: #38A169;'>🟢 Aktiv</span><br>
    <b>AI Mühərriki:</b> <span style='color: #3182CE;'>🧠 V6.6 NLP</span><br>
    <b>Baza Statusu:</b> <span style='color: #38A169;'>💾 Qorunur</span><br>
    <b>Jurnal (Logs):</b> <span style='color: #D69E2E;'>🔴 Yazılır</span>
</div>
""", unsafe_allow_html=True)

if st.session_state.get('logged_in'):
    st.sidebar.markdown("---")
    st.sidebar.subheader("👤 Profilim")
    st.sidebar.write(f"**İstifadəçi:** {st.session_state.name}")
    st.sidebar.write(f"**Səlahiyyət:** {st.session_state.role.upper()}")
    st.sidebar.write(f"**Bölmə:** {st.session_state.dept}")

if st.sidebar.button("📞 Təcili Dəstək Kanalı"):
    if os.path.exists(USERS_FILE):
        users_df = pd.read_csv(USERS_FILE)
        admins = users_df[users_df['role'].isin(['admin', 'super_admin'])]
        if not admins.empty:
            random_admin = admins.sample(1).iloc[0]
            st.sidebar.success(f"📡 **Dəstək Təyin Olundu:**\n\n👤 {random_admin['name']}\n🏢 {random_admin['dept']}\n📱 +994 50 123 45 67")
            add_log("Təcili Dəstək düyməsinə basdı", st.session_state.get('username', 'Anonim'))
        else: st.sidebar.warning("Hazırda aktiv agent tapılmadı.")

def normalize_text(text):
    text = text.lower()
    replacements = {
        "ə":"e", "ı":"i", "ö":"o", "ğ":"g", "ü":"u", "ş":"s", "ç":"c", 
        "prablem":"problem", "yoxdu":"yoxdur", "kasiyor":"donur", "zaydir":"yoxdur",
        "sebekede":"sebeke", "internetde":"internet", "komputerde":"komputer",
        "noutbukda":"noutbuk", "mailimde":"mail", "parolumu":"parol", "sifremi":"sifre",
        "internete":"internet", "wi-fida":"wi-fi"
    }
    for old, new in replacements.items(): text = text.replace(old, new)
    return text.strip()

# ==========================================
# 3. YÜKSƏK SÜRƏTLİ VECTOR NLP (LinearSVC) - 1M DATA
# ==========================================
@st.cache_resource
def initialize_system():
    os.makedirs('data', exist_ok=True)
    rebuild_needed = False
    
    if os.path.exists('data/tickets.csv'):
        df_check = pd.read_csv('data/tickets.csv', usecols=['category'])
        if len(df_check) < 990000: rebuild_needed = True
    else: rebuild_needed = True

    if rebuild_needed:
        network_issues = ["wi-fi qosulmur", "internet zeifdir", "ip xetasi", "lan kabel qirilib", "sebeke yoxdur", "internet kesilib", "sebeke problemi var", "wi-fi not working", "slow internet", "ip error", "broken cable", "no network", "connection dropped", "no internet", "network issue", "не работает wi-fi", "медленный интернет", "ошибка ip", "нет сети", "обрыв кабеля", "нет интернета", "плохое соединение", "wi-fi çalışmıyor", "internet yavaş", "ip hatası", "kablo koptu", "ağ yok", "bağlantı koptu", "internet gitti", "ağ sorunu"]
        hardware_issues = ["noutbuk donur", "proyektor islemir", "printer cap etmir", "ram problemi", "sistem bloku yanir", "ekran acilmir", "klaviatura islemir", "maus xarabdir", "laptop freezing", "screen is black", "printer not printing", "mouse broken", "keyboard not working", "pc crashing", "monitor dead", "battery issue", "ноутбук зависает", "черный экран", "принтер не печатает", "сломана мышь", "клавиатура не работает", "компьютер не включается", "проблема с батареей", "laptop donuyor", "ekran açılmıyor", "yazıcı yazdırmıyor", "fare bozuk", "klavye çalışmıyor", "bilgisayar kapandı", "şarj olmuyor", "kasa yandı"]
        account_issues = ["mailime gire bilmirem", "parolu unutmusam", "hesab bloklanib", "sisteme giris ede bilmirem", "sifre yalnisdir", "moodle hesabi acilmir", "forgot password", "account locked", "cant login", "wrong password", "email not working", "access denied", "reset my password", "забыл пароль", "аккаунт заблокирован", "не могу войти", "неверный пароль", "ошибка авторизации", "нет доступа", "şifremi unuttum", "hesabım kilitlendi", "giriş yapamıyorum", "yanlış şifre", "mail açılmıyor", "sisteme giremiyorum", "yetki yok"]
        software_issues = ["office lisenziya xetasi", "antivirus xetasi", "windows dondu", "proqram acilmir", "word islemir", "sistem update olunmur", "excel acmir", "software not opening", "windows crashed", "office error", "excel freezing", "update failed", "program crash", "blue screen app", "программа не открывается", "windows завис", "ошибка office", "excel не работает", "ошибка обновления", "сбой программы", "program açılmıyor", "windows çöktü", "office hatası", "excel donuyor", "güncelleme başarısız", "uygulama yanıt vermiyor", "mavi ekran"]
        security_issues = ["komputere virus dusub", "spam mailler", "fayllarim sifrelenib", "heker hucumu", "qeribe reklamlar cixir", "trojan var", "virus detected", "spam emails", "hacker attack", "files encrypted", "malware", "ransomware", "unauthorized access", "обнаружен вирус", "спам письма", "хакерская атака", "файлы зашифрованы", "троян", "взлом", "virüs bulaştı", "spam e-postalar", "hacker saldırısı", "dosyalar şifrelendi", "trojan var", "hesabım çalındı", "şüpheli işlem"]
        database_issues = ["melumat bazasina qosulmur", "sql xetasi", "1c acilmir", "servere qosulmaq olmur", "baza silinib", "server cokdu", "database connection failed", "sql error", "server down", "data deleted", "query failed", "oracle error", "db crash", "ошибка подключения к базе", "ошибка sql", "сервер недоступен", "данные удалены", "ошибка запроса", "база данных легла", "veritabanı bağlantı hatası", "sql hatası", "sunucu çöktü", "veriler silindi", "sorgu hatası", "db bağlantısı yok"]
        
        base_data = []
        for text in network_issues: base_data.append({"ticket_text": text, "category": "Şəbəkə"})
        for text in hardware_issues: base_data.append({"ticket_text": text, "category": "Avadanlıq"})
        for text in account_issues: base_data.append({"ticket_text": text, "category": "Hesab_Problemi"})
        for text in software_issues: base_data.append({"ticket_text": text, "category": "Proqram_Təminatı"})
        for text in security_issues: base_data.append({"ticket_text": text, "category": "Təhlükəsizlik"})
        for text in database_issues: base_data.append({"ticket_text": text, "category": "Məlumat_Bazası"})
        
        multiplier = 1000000 // len(base_data)
        massive_data = base_data * multiplier
        
        df = pd.DataFrame(massive_data)
        df = df.sample(frac=1).reset_index(drop=True)
        df.to_csv('data/tickets.csv', index=False)
        if os.path.exists('helpdesk_classifier_model.pkl'): os.remove('helpdesk_classifier_model.pkl')

    def train_new_model():
        df = pd.read_csv('data/tickets.csv')
        pipeline = Pipeline([
            ('tfidf', TfidfVectorizer(ngram_range=(1, 3), max_features=20000)), 
            ('clf', LinearSVC(random_state=42, dual="auto")) 
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

with st.spinner("⚙️ AI Modeli və 1 Milyonluq Baza Yüklənir... Zəhmət olmasa gözləyin."):
    model = initialize_system()

def ensure_db_exists():
    os.makedirs('data', exist_ok=True)
    if not os.path.exists(LOGS_FILE):
        pd.DataFrame(columns=["Tarix", "İstifadəçi", "Əməliyyat"]).to_csv(LOGS_FILE, index=False)
        
    try:
        u_df = pd.read_csv(USERS_FILE)
        if len(str(u_df['password'].iloc[0])) < 64: raise ValueError("Köhnə şifrələmə")
    except Exception:
        pd.DataFrame([
            {"username": "kamran_muradov", "password": hash_password("admin"), "role": "super_admin", "name": "Kamran Muradov", "dept": "Bütün_Sistem"},
            {"username": "orxan_eliyev", "password": hash_password("123"), "role": "admin", "name": "Orxan Əliyev", "dept": "Avadanlıq"},
            {"username": "cavid_memmedov", "password": hash_password("123"), "role": "admin", "name": "Cavid Məmmədov", "dept": "Şəbəkə"}
        ]).to_csv(USERS_FILE, index=False)
        add_log("Sistem bazası sıfırlandı və şifrələndi")
        
    try:
        t_df = pd.read_csv(TICKETS_FILE)
        if "Prioritet" not in t_df.columns: raise ValueError("Format error")
    except Exception:
        pd.DataFrame(columns=["Ticket_ID", "Tarix", "Göndərən", "Şikayət", "Kateqoriya", "Prioritet", "Məsul_Şəxs", "Status"]).to_csv(TICKETS_FILE, index=False)

ensure_db_exists()

def get_priority(category):
    # Yumşaq rənglərlə prioritetlər
    if category in ["Təhlükəsizlik", "Məlumat_Bazası"]: return "🔴 Kritik"
    elif category in ["Şəbəkə", "Hesab_Problemi"]: return "🟡 Yüksək"
    else: return "🟢 Normal"

def smart_ai_autosolve(text):
    text = normalize_text(text)
    if any(word in text for word in ["parol", "sifre", "unutmusam", "password", "reset"]): return "🤖 AI Həll Yolu: Şifrənizi sıfırlamaq üçün korporativ portalda 'Şifrəni Bərpa Et' bölməsinə daxil olun."
    elif any(word in text for word in ["zeif", "yavas", "qopur", "islemir"]) and any(word in text for word in ["internet", "wi-fi", "sebeke", "net"]): return "🤖 AI Həll Yolu: Hazırda serverlərdə yüklənmə mövcuddur. Bağlantını kəsib 30 saniyə sonra yenidən qoşulun."
    elif any(word in text for word in ["donur", "dondu", "kasiyor", "kilitlendi"]): return "🤖 AI Həll Yolu: Sistem donmalarının səbəbi RAM yüklənməsidir. 'Task Manager' açaraq lazımsız proqramları bağlayın."
    elif any(word in text for word in ["virus", "spam", "reklam", "heker", "trojan"]): return "🤖 AI Həll Yolu: DİQQƏT! Lütfən cihazı DƏRHAL şəbəkədən ayırın. Təhlükəsizlik şöbəsi gələnə qədər heç nə taxmayın!"
    return None 

# ==========================================
# 4. GİRİŞ VƏ QEYDİYYAT
# ==========================================
if 'logged_in' not in st.session_state: st.session_state.logged_in = False
if 'show_forgot_pass' not in st.session_state: st.session_state.show_forgot_pass = False

if not st.session_state.logged_in:
    st.markdown(f"<h1 style='text-align: center; color: #6A82FB !important; letter-spacing: 1px;'>{t['welcome']}</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #718096 !important;'>Müasir, Sürətli və Ağıllı İdarəetmə Paneli</p>", unsafe_allow_html=True)
    
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
                            add_log("Sistemə daxil oldu", u['username'])
                            st.rerun()
                        else: 
                            st.error("❌ Giriş xətası: İdentifikator və ya şifrə səhvdir.")
                            add_log(f"Uğursuz giriş cəhdi (ID: {login_user})", "Naməlum")
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
                        if len(new_user) < 3 or len(new_pass) < 3:
                            st.error("⚠️ Məlumatlar çox qısadır.")
                        else:
                            users_df = pd.read_csv(USERS_FILE)
                            if new_user in users_df['username'].values:
                                st.error("⚠️ Bu istifadəçi adı artıq mövcuddur.")
                            else:
                                pd.DataFrame([{"username": new_user, "password": hash_password(new_pass), "role": "user", "name": new_name, "dept": "Yoxdur"}]).to_csv(USERS_FILE, mode='a', header=False, index=False)
                                add_log("Yeni hesab yaradıldı", new_user)
                                st.success("✅ Hesab yaradıldı! Daxil ola bilərsiniz.")
        else:
            with st.form("reset_pass_form"):
                st.subheader("🔄 Şifrənin Bərpası")
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
                        add_log("Şifrəni sıfırladı", reset_user)
                        st.success("✅ Şifrə uğurla yeniləndi.")
                    else: st.error("İstifadəçi tapılmadı.")
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
            st.toast("🔔 Yeni İnsident Qeydə Alındı!", icon="🔔")
            play_notification_sound()
            st.session_state.last_ticket_count = len(tickets_df)

    colA, colB = st.columns([4, 1])
    with colA: st.markdown(f"<h3 style='color: #4A5568 !important;'>👋 Xoş Gəldiniz, {st.session_state.name}</h3>", unsafe_allow_html=True)
    with colB:
        if st.button(f"🚪 Çıxış Et", type="primary"):
            add_log("Sistemdən çıxış etdi", st.session_state.username)
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
                    
                    if submit_ticket:
                        if len(user_input.strip()) < 10:
                            st.error("⚠️ Zəhmət olmasa problemi daha ətraflı yazın.")
                        else:
                            clean_input = normalize_text(user_input)
                            
                            # HIBRID NLP MƏNTİQİ
                            if any(w in clean_input for w in ["virus", "heker", "spam", "trojan", "reklam", "sifrelenib"]): pred_category = "Təhlükəsizlik"
                            elif any(w in clean_input for w in ["baza", "sql", "server", "1c", "oracle", "db"]): pred_category = "Məlumat_Bazası"
                            elif any(w in clean_input for w in ["sebeke", "internet", "wi-fi", "wifi", "lan", "kabel", "ping"]): pred_category = "Şəbəkə"
                            elif any(w in clean_input for w in ["parol", "sifre", "mail", "hesab", "moodle", "login"]): pred_category = "Hesab_Problemi"
                            elif any(w in clean_input for w in ["ekran", "klaviatura", "maus", "proyektor", "printer", "noutbuk", "komputer", "ram", "yandi"]): pred_category = "Avadanlıq"
                            elif any(w in clean_input for w in ["proqram", "word", "excel", "office", "windows", "update", "teams"]): pred_category = "Proqram_Təminatı"
                            else:
                                pred_category = model.predict([clean_input])[0]
                                
                            priority = get_priority(pred_category)
                            ticket_id = f"TKT-{random.randint(10000, 99999)}"
                            
                            agent_mapping = {"Şəbəkə": "Şəbəkə Şöbəsi", "Avadanlıq": "Texniki Dəstək", "Hesab_Problemi": "Hesab Qeydiyyatı", "Proqram_Təminatı": "Proqram Təminatı", "Təhlükəsizlik": "Təhlükəsizlik Şöbəsi", "Məlumat_Bazası": "Baza Administratoru"}
                            assigned_dept = agent_mapping.get(pred_category, "Ümumi Şöbə")
                            
                            ai_reply = smart_ai_autosolve(user_input)
                            
                            if ai_reply:
                                new_t = pd.DataFrame([{"Ticket_ID": ticket_id, "Tarix": datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "Göndərən": st.session_state.username, "Şikayət": user_input, "Kateqoriya": pred_category, "Prioritet": priority, "Məsul_Şəxs": "AI 🤖", "Status": "Həll edildi"}])
                                new_t.to_csv(TICKETS_FILE, mode='a', header=False, index=False)
                                add_log(f"İnsident yaratdı və AI həll etdi ({ticket_id})", st.session_state.username)
                                st.success(f"⚡ İnsident {ticket_id} | Şöbə: {pred_category} | Prioritet: {priority}")
                                st.info(ai_reply)
                            else:
                                new_t = pd.DataFrame([{"Ticket_ID": ticket_id, "Tarix": datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "Göndərən": st.session_state.username, "Şikayət": user_input, "Kateqoriya": pred_category, "Prioritet": priority, "Məsul_Şəxs": "Gözləyir", "Status": "Açıq"}])
                                new_t.to_csv(TICKETS_FILE, mode='a', header=False, index=False)
                                add_log(f"İnsident yaratdı ({ticket_id})", st.session_state.username)
                                st.success(f"✅ İnsident {ticket_id} Qeydə Alındı. Şöbə: {assigned_dept} | Prioritet: {priority}")

            with col_stat:
                my_count = len(tickets_df[tickets_df['Göndərən'] == st.session_state.username])
                st.info(f"📈 **{t['stats']}**\n\nCəmi İnsidentlər: **{my_count}**")
                my_tickets_df = tickets_df[tickets_df['Göndərən'] == st.session_state.username]
                if not my_tickets_df.empty:
                    st.write("**İnsident İzləyici:**")
                    for index, row in my_tickets_df.head(3).iterrows():
                        if row['Status'] == 'Açıq': st.warning(f"{row['Ticket_ID']}: 🕒 Gözləyir")
                        elif row['Status'] == 'İcrada': st.info(f"{row['Ticket_ID']}: 🛠️ İcrada")
                        else: st.success(f"{row['Ticket_ID']}: ✅ Həll Edildi")

        with tab_exam:
            st.write("### İT Mütəxəssis İmtahanı")
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
                        add_log("İmtahandan keçdi və Admin oldu", st.session_state.username)
                        st.success("🎉 Təbriklər! Siz artıq Adminsiniz. Təkrar daxil olun.")
                    else: st.error("Təəssüf ki, imtahandan kəsildiniz.")

    # --- ADMIN PANELİ ---
    elif st.session_state.role == "admin":
        col_main, col_stat = st.columns([3, 1])
        with col_main:
            st.write(f"### 📬 {t['open_tickets']}")
            open_tickets = tickets_df[(tickets_df["Kateqoriya"] == st.session_state.dept) & (tickets_df["Status"] == "Açıq")]
            
            def color_priority(val):
                # Yumşaq rənglər: Pastel Qırmızı, Narıncı, Yaşıl
                color = '#E53E3E' if val == '🔴 Kritik' else '#DD6B20' if val == '🟡 Yüksək' else '#38A169'
                return f'color: {color}; font-weight: bold'
            
            if not open_tickets.empty:
                st.dataframe(open_tickets[['Ticket_ID', 'Tarix', 'Göndərən', 'Prioritet', 'Şikayət']].style.map(color_priority, subset=['Prioritet']), use_container_width=True, hide_index=True)
                with st.form("accept_ticket_form"):
                    accept_id = st.selectbox("İcraya Götürüləcək İnsident:", open_tickets['Ticket_ID'].tolist())
                    submit_accept = st.form_submit_button(t['accept_ticket'], type="primary")
                    if submit_accept:
                        original_df = pd.read_csv(TICKETS_FILE)
                        real_idx = original_df[original_df['Ticket_ID'] == accept_id].index[0]
                        original_df.loc[real_idx, "Status"] = "İcrada"
                        original_df.loc[real_idx, "Məsul_Şəxs"] = st.session_state.username
                        original_df.to_csv(TICKETS_FILE, index=False)
                        add_log(f"İnsidenti icraya götürdü ({accept_id})", st.session_state.username)
                        st.success(f"✅ {accept_id} İCRAYA GÖTÜRÜLDÜ!")
                        st.rerun()
            else: st.info("Sistem təmizdir. Gözləyən insident yoxdur.")
            
            st.markdown("---")
            st.write(f"### ⏳ {t['my_active']}")
            active_tickets = tickets_df[(tickets_df["Məsul_Şəxs"] == st.session_state.username) & (tickets_df["Status"] == "İcrada")]
            if not active_tickets.empty:
                st.dataframe(active_tickets[['Ticket_ID', 'Tarix', 'Prioritet', 'Şikayət']].style.map(color_priority, subset=['Prioritet']), use_container_width=True, hide_index=True)
                with st.form("close_ticket_form"):
                    close_id = st.selectbox("Bağlanacaq İnsident:", active_tickets['Ticket_ID'].tolist())
                    submit_close = st.form_submit_button(t['mark_solved'], type="primary")
                    if submit_close:
                        original_df = pd.read_csv(TICKETS_FILE)
                        real_idx = original_df[original_df['Ticket_ID'] == close_id].index[0]
                        original_df.loc[real_idx, "Status"] = "Həll edildi"
                        original_df.to_csv(TICKETS_FILE, index=False)
                        add_log(f"İnsidenti uğurla bağladı ({close_id})", st.session_state.username)
                        st.success(f"✅ {close_id} UĞURLA BAĞLANDI!")
                        st.rerun() 
            else: st.info("Aktiv icra yoxdur.")
        with col_stat:
            solved_count = len(tickets_df[(tickets_df['Məsul_Şəxs'] == st.session_state.username) & (tickets_df['Status'] == 'Həll edildi')])
            st.info(f"📈 **Məhsuldarlıq**\n\nBağlanmış İş: **{solved_count}**")

    # --- SUPER ADMIN PANELİ ---
    elif st.session_state.role == "super_admin":
        col_m1, col_m2, col_m3 = st.columns([1, 1, 2])
        col_m1.metric("Ümumi İnsidentlər", len(tickets_df))
        col_m2.metric("Açıq Sorğular", len(tickets_df[tickets_df['Status']=='Açıq']))
        with col_m3:
            csv_data = tickets_df.to_csv(index=False).encode('utf-8-sig')
            st.download_button(label=t['download_csv'], data=csv_data, file_name=f"CORE_DATA_{datetime.now().strftime('%Y%m%d_%H%M')}.csv", mime="text/csv", type="primary")
        st.markdown("---")
        
        tab_dash, tab_users, tab_logs = st.tabs(["📊 Analitika", "👥 İstifadəçilər", "🕵️ Sistem Jurnalı"])
        
        with tab_dash:
            if not tickets_df.empty:
                col_chart1, col_chart2 = st.columns(2)
                cat_counts = tickets_df["Kateqoriya"].value_counts().reset_index()
                cat_counts.columns = ["Kateqoriya", "Say"]
                # Plotly White teması (Açıq rəngli qrafiklər)
                fig_donut = px.pie(cat_counts, names="Kateqoriya", values="Say", hole=0.5, title="Şöbələr Üzrə Yük", color_discrete_sequence=px.colors.sequential.Pastel)
                fig_donut.update_layout(template="plotly_white")
                col_chart1.plotly_chart(fig_donut, use_container_width=True)
                
                tickets_df['Tarix_Gun'] = pd.to_datetime(tickets_df['Tarix'], errors='coerce').dt.date
                daily_counts = tickets_df.groupby('Tarix_Gun').size().reset_index(name='Say')
                fig_line = px.line(daily_counts, x='Tarix_Gun', y='Say', title="Günlük Trendlər", markers=True)
                fig_line.update_traces(line_color='#6A82FB')
                fig_line.update_layout(template="plotly_white")
                col_chart2.plotly_chart(fig_line, use_container_width=True)
            
            st.markdown("---")
            all_categories = ["Bütün Sorğular", "Şəbəkə", "Avadanlıq", "Hesab_Problemi", "Proqram_Təminatı", "Təhlükəsizlik", "Məlumat_Bazası"]
            cat_tabs = st.tabs([f"📂 {c}" for c in all_categories])
            
            def color_priority(val):
                color = '#E53E3E' if val == '🔴 Kritik' else '#DD6B20' if val == '🟡 Yüksək' else '#38A169'
                return f'color: {color}; font-weight: bold'

            for i, cat in enumerate(all_categories):
                with cat_tabs[i]:
                    if cat == "Bütün Sorğular": 
                        st.dataframe(tickets_df.drop(columns=['Tarix_Gun'], errors='ignore').style.map(color_priority, subset=['Prioritet']), use_container_width=True, hide_index=True)
                    else:
                        filtered_df = tickets_df[tickets_df["Kateqoriya"] == cat]
                        st.write(f"**Sayı:** {len(filtered_df)}")
                        st.dataframe(filtered_df.drop(columns=['Tarix_Gun'], errors='ignore').style.map(color_priority, subset=['Prioritet']), use_container_width=True, hide_index=True)
        
        with tab_users:
            st.write("### Hesablar Bazası")
            users_db = pd.read_csv(USERS_FILE)
            safe_users_db = users_db.drop(columns=['password'])
            st.dataframe(safe_users_db, use_container_width=True, hide_index=True)
            
        with tab_logs:
            st.write("### 🕵️ Audit Jurnalı (Logs)")
            if os.path.exists(LOGS_FILE):
                logs_df = pd.read_csv(LOGS_FILE)
                logs_df = logs_df.sort_values(by="Tarix", ascending=False).reset_index(drop=True)
                st.dataframe(logs_df, use_container_width=True, hide_index=True)
                
                csv_logs = logs_df.to_csv(index=False).encode('utf-8-sig')
                st.download_button(label="☁️ Jurnalı Yüklə (CSV)", data=csv_logs, file_name=f"AUDIT_LOGS_{datetime.now().strftime('%Y%m%d')}.csv", mime="text/csv", type="secondary")
            else:
                st.info("Sistem jurnalı hələ boşdur.")
