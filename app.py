# Müəllif: Kamran Muradov
# Fayl: app.py
# Məqsəd: ASOIU Command Center - NASA Style Enterprise Helpdesk AI (Qüsursuz Versiya)

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
    /* Kosmik Tünd Arxa Fon */
    .stApp {
        background-color: #050810;
        color: #E2E8F0;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }
    
    /* Yazıların rəngləri */
    h1, h2, h3, p, label, .stMarkdown { color: #FFFFFF !important; }
    
    /* NASA Qırmızısı və Texnoloji Düymələr */
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
    
    /* Tünd İnputlar (Terminal tərzi) */
    .stTextArea textarea { resize: none !important; border: 1px solid #1E3A8A !important; border-radius: 4px !important; background-color: #0B1221 !important; color: #00D2FF !important; font-family: monospace !important; }
    .stTextInput input, .stSelectbox select { border: 1px solid #1E3A8A !important; border-radius: 4px !important; background-color: #0B1221 !important; color: #00D2FF !important; }
    
    /* Məlumat Qutuları */
    div[data-testid="stAlert"] { background-color: rgba(30, 58, 138, 0.2) !important; border-left: 4px solid #00D2FF !important; border-radius: 4px !important; color: #E2E8F0 !important; }
    
    /* Sekmələr (Tabs) */
    button[data-baseweb="tab"] { font-weight: bold; color: #A0AEC0 !important; }
    button[data-baseweb="tab"][aria-selected="true"] { color: #00D2FF !important; border-bottom: 2px solid #00D2FF !important; }
    
    /* Metriklər (Yuxarıdakı böyük rəqəmlər) */
    div[data-testid="stMetricValue"] { color: #00D2FF !important; text-shadow: 0px 0px 10px rgba(0, 210, 255, 0.3); }
    
    /* Yan Panel */
    [data-testid="stSidebar"] { background-color: #080D1A !important; border-right: 1px solid #1A202C !important; }
</style>
""", unsafe_allow_html=True)

def play_notification_sound():
    st.markdown("""<audio autoplay="true"><source src="https://assets.mixkit.co/active_storage/sfx/2869/2869-preview.mp3" type="audio/mpeg"></audio>""", unsafe_allow_html=True)

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# ==========================================
# 2. DİL VƏ YAN PANEL (SYSTEM HEALTH)
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
    AI ENGINE: <span style='color: #48BB78;'>🧠 V4.0 ACTIVE</span><br>
    DB STATUS: <span style='color: #48BB78;'>💾 SECURE</span><br>
    NETWORK: <span style='color: #48BB78;'>📶 STABLE (12ms)</span>
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
# 3. ULTRA BAZA VƏ AI MÜHƏRRİKİ (ENGINE)
# ==========================================
@st.cache_resource
def initialize_system():
    os.makedirs('data', exist_ok=True)
    rebuild_needed = False
    
    if os.path.exists('data/tickets.csv'):
        df_check = pd.
