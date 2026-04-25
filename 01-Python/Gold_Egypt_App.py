
import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
import requests
import yfinance as yf
import time
import os
import warnings
warnings.filterwarnings("ignore")

DATA_DIR = os.path.dirname(os.path.abspath(__file__))
CSV_PATH = os.path.join(DATA_DIR, "new_gold_data.csv")

_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/122.0.0.0 Safari/537.36",
    "Accept-Language": "ar,en;q=0.9",
}

try:
    from streamlit_autorefresh import st_autorefresh
    if 13 <= datetime.utcnow().hour <= 21:
        st_autorefresh(interval=300_000, key="market_refresh")
except ImportError:
    pass

st.set_page_config(
    page_title="GOLD EGYPT · ذهب مصر",
    page_icon="🥇",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(r"""
<style>
/* ── Fonts ── */
@import url('https://fonts.googleapis.com/css2?family=Cairo:wght@300;400;600;700;900&family=Bebas+Neue&family=DM+Mono:wght@400;500&display=swap');

/* ── CSS Variables ── */
:root {
  --gold:        #FFD700;
  --gold-dim:    #B8960C;
  --gold-glow:   rgba(255,215,0,0.18);
  --gold-trace:  rgba(255,215,0,0.06);
  --emerald:     #06D6A0;
  --crimson:     #EF476F;
  --sapphire:    #4CC9F0;
  --violet:      #A855F7;
  --amber:       #FF9F43;
  --bg-void:     #03060F;
  --bg-deep:     #060C18;
  --bg-card:     #0A1525;
  --bg-card2:    #0D1E36;
  --border:      #132238;
  --border-glow: #1E3A5F;
  --text-prime:  #E8EDF5;
  --text-muted:  #8D99AE;
  --text-faint:  #3A4A65;
  --radius:      16px;
  --radius-sm:   10px;
  --transition:  0.35s cubic-bezier(0.4, 0, 0.2, 1);
}

/* ── Reset & Base ── */
html, body, [class*="css"] {
  font-family: 'Cairo', sans-serif;
  -webkit-font-smoothing: antialiased;
}
.stApp {
  background: radial-gradient(ellipse 120% 80% at 50% -10%, #0D2040 0%, var(--bg-void) 60%);
  min-height: 100vh;
}

/* ── Animated gold particle background ── */
.stApp::before {
  content: '';
  position: fixed;
  inset: 0;
  background-image:
    radial-gradient(1px 1px at 20% 30%, rgba(255,215,0,0.12) 0%, transparent 100%),
    radial-gradient(1px 1px at 80% 10%, rgba(255,215,0,0.08) 0%, transparent 100%),
    radial-gradient(1px 1px at 60% 70%, rgba(255,215,0,0.06) 0%, transparent 100%),
    radial-gradient(1px 1px at 40% 90%, rgba(76,201,240,0.06) 0%, transparent 100%);
  pointer-events: none;
  z-index: 0;
}

/* ── Page enter animation ── */
@keyframes pageIn {
  from { opacity: 0; transform: translateY(18px); }
  to   { opacity: 1; transform: translateY(0); }
}
@keyframes fadeSlide {
  from { opacity: 0; transform: translateX(-12px); }
  to   { opacity: 1; transform: translateX(0); }
}
@keyframes shimmer {
  0%   { background-position: -200% center; }
  100% { background-position: 200% center; }
}
@keyframes pulseGold {
  0%, 100% { box-shadow: 0 0 0 0 rgba(255,215,0,0.18); }
  50%       { box-shadow: 0 0 0 8px rgba(255,215,0,0); }
}
@keyframes countUp {
  from { opacity: 0; transform: translateY(10px); }
  to   { opacity: 1; transform: translateY(0); }
}
@keyframes borderFlow {
  0%   { background-position: 0% 50%; }
  50%  { background-position: 100% 50%; }
  100% { background-position: 0% 50%; }
}
@keyframes spin {
  from { transform: rotate(0deg); }
  to   { transform: rotate(360deg); }
}
@keyframes blink {
  0%, 100% { opacity: 1; }
  50%       { opacity: 0.3; }
}

/* Main content animation - flush with sidebar top */
.main .block-container {
  animation: pageIn var(--transition) both;
  padding: 50px clamp(0.5rem, 2vw, 2rem) clamp(0.5rem, 2vw, 1.5rem) !important;
  max-width: 1600px;
}

/* ── SIDEBAR ── */
[data-testid="stSidebar"] {
  background: linear-gradient(180deg, #070E1D 0%, #04080F 100%) !important;
  border-right: 1px solid var(--border) !important;
  box-shadow: 4px 0 30px rgba(0,0,0,0.6);
}
[data-testid="stSidebar"] > div { padding-top: 0 !important; }

/* Nav items */
[data-testid="stSidebar"] .stRadio div[role="radiogroup"] label {
  direction: ltr !important;
  text-align: left !important;
  display: flex !important;
  align-items: center !important;
  gap: 10px !important;
  color: var(--text-muted) !important;
  font-size: 0.85rem !important;
  padding: 8px 12px !important;
  border-radius: 8px !important;
  transition: all 0.2s ease !important;
  cursor: pointer !important;
  margin: 2px 0 !important;
}
[data-testid="stSidebar"] .stRadio div[role="radiogroup"] label:hover {
  color: var(--gold) !important;
  background: var(--gold-trace) !important;
}
[data-testid="stSidebar"] .stRadio div[role="radiogroup"] label[data-testid*="checked"],
[data-testid="stSidebar"] .stRadio div[role="radiogroup"] label:has(input:checked) {
  color: var(--gold) !important;
  background: var(--gold-trace) !important;
  border-left: 2px solid var(--gold) !important;
}

/* Sidebar selectbox & toggle */
[data-testid="stSidebar"] .stSelectbox label,
[data-testid="stSidebar"] .stToggle label {
  direction: rtl !important; text-align: right !important;
  width: 100%; color: var(--text-muted) !important; font-size: 0.8rem !important;
}

/* ── HERO BANNER - cinematic ── */
.hero-wrap {
  position: relative;
  overflow: hidden;
  background: linear-gradient(135deg, #081428 0%, #0C1E3D 40%, #091628 100%);
  border: 1px solid var(--border-glow);
  border-top: none;
  border-radius: var(--radius);
  padding: clamp(20px, 4vw, 40px) clamp(16px, 4vw, 48px);
  margin-top: 0;
  margin-bottom: 24px;
  animation: pageIn 0.5s both;
}
.hero-wrap::before {
  content: '';
  position: absolute;
  top: 0; left: 0; right: 0; height: 3px;
  background: linear-gradient(90deg, transparent, var(--gold), #FFF9C4, var(--gold), transparent);
  background-size: 200% 100%;
  animation: shimmer 3s linear infinite;
}
.hero-wrap::after {
  content: '';
  position: absolute;
  top: -60%; right: -10%;
  width: 400px; height: 400px;
  background: radial-gradient(circle, rgba(255,215,0,0.04) 0%, transparent 70%);
  border-radius: 50%;
  pointer-events: none;
}
.hero-eyebrow {
  font-family: 'DM Mono', monospace;
  font-size: 0.68rem;
  letter-spacing: 3px;
  color: var(--gold-dim);
  text-transform: uppercase;
  margin-bottom: 8px;
  direction: ltr;
}
.hero-title {
  font-family: 'Cairo', sans-serif;
  font-size: clamp(1.4rem, 4vw, 2.2rem);
  font-weight: 900;
  color: var(--gold);
  margin: 0 0 8px 0;
  line-height: 1.15;
  direction: rtl;
  text-align: right;
}
.hero-sub {
  font-size: clamp(0.78rem, 2vw, 0.88rem);
  color: #6B7A99;
  line-height: 1.7;
  direction: rtl;
  text-align: right;
  max-width: 700px;
  margin-right: 0;
  margin-left: auto;
}
.hero-date {
  font-family: 'DM Mono', monospace;
  font-size: 0.75rem;
  color: var(--emerald);
  margin-top: 12px;
  direction: ltr;
  display: flex;
  align-items: center;
  gap: 6px;
  justify-content: flex-end;
}
.hero-date .dot {
  width: 6px; height: 6px;
  background: var(--emerald);
  border-radius: 50%;
  animation: blink 2s ease-in-out infinite;
}
.hero-badges {
  display: flex; gap: 8px; margin-top: 14px;
  justify-content: flex-end; flex-wrap: wrap;
}
.hero-badge {
  font-family: 'DM Mono', monospace;
  font-size: 0.65rem; letter-spacing: 1px;
  background: rgba(255,215,0,0.08);
  border: 1px solid rgba(255,215,0,0.2);
  color: var(--gold); padding: 4px 12px;
  border-radius: 20px; direction: ltr; white-space: nowrap;
  text-transform: uppercase;
}

/* ── KPI CARDS - premium glass ── */
.kpi-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(140px, 1fr));
  gap: 12px;
  margin-bottom: 8px;
}
.kpi-card {
  position: relative;
  background: linear-gradient(145deg, var(--bg-card), var(--bg-card2));
  border: 1px solid var(--border);
  border-radius: var(--radius);
  padding: 18px 16px;
  text-align: center;
  overflow: hidden;
  transition: transform var(--transition), border-color var(--transition), box-shadow var(--transition);
  animation: countUp 0.5s both;
  cursor: default;
}
.kpi-card::before {
  content: '';
  position: absolute;
  top: 0; left: 0; right: 0; height: 1px;
  background: linear-gradient(90deg, transparent, rgba(255,255,255,0.06), transparent);
}
.kpi-card:hover {
  transform: translateY(-3px);
  border-color: rgba(255,215,0,0.3);
  box-shadow: 0 8px 32px rgba(0,0,0,0.5), 0 0 20px rgba(255,215,0,0.06);
}
.kpi-value {
  font-family: 'Bebas Neue', 'DM Mono', monospace;
  font-size: clamp(1.5rem, 3vw, 1.9rem);
  line-height: 1.1;
  margin-bottom: 4px;
  direction: ltr;
  letter-spacing: 1px;
}
.kpi-label {
  font-size: 0.68rem;
  color: var(--text-faint);
  letter-spacing: 0.5px;
  direction: rtl;
  text-transform: uppercase;
}
.kpi-card:nth-child(1) { animation-delay: 0.05s; }
.kpi-card:nth-child(2) { animation-delay: 0.10s; }
.kpi-card:nth-child(3) { animation-delay: 0.15s; }
.kpi-card:nth-child(4) { animation-delay: 0.20s; }
.kpi-card:nth-child(5) { animation-delay: 0.25s; }

/* ── SECTION HEADER ── */
.section-wrap {
  margin: 32px 0 10px 0;
  direction: rtl;
  animation: fadeSlide 0.4s both;
}
.section-title {
  display: flex;
  align-items: center;
  gap: 10px;
  justify-content: flex-end;
  flex-direction: row-reverse;
}
.section-icon { font-size: 1rem; }
.section-text {
  font-size: 1rem; font-weight: 700; color: var(--gold);
  letter-spacing: -0.3px; direction: rtl; unicode-bidi: embed;
}
.section-line {
  height: 1px;
  background: linear-gradient(90deg, transparent 0%, var(--gold-dim) 30%, transparent 100%);
  margin: 8px 0 6px 0;
  opacity: 0.4;
}
.section-sub { font-size: 0.76rem; color: var(--text-faint); direction: rtl; text-align: right; margin: 0 0 12px 0; }

/* ── INSIGHT BOX ── */
.insight-box {
  position: relative;
  background: linear-gradient(135deg, #060D1C, #0A1728);
  border: 1px solid var(--border);
  border-radius: var(--radius-sm);
  padding: 14px 20px 14px 14px;
  margin: 6px 0 12px 0;
  font-size: 0.83rem;
  color: #A0AEBE;
  line-height: 1.8;
  direction: rtl; text-align: right;
  overflow: hidden;
}
.insight-box::after {
  content: '';
  position: absolute;
  top: 0; right: 0;
  width: 3px; height: 100%;
  background: linear-gradient(180deg, var(--gold), var(--gold-dim));
  border-radius: 0 var(--radius-sm) var(--radius-sm) 0;
}
.insight-box b { color: var(--gold); }
.insight-box .num     { color: var(--emerald); font-weight: 700; font-family: 'DM Mono', monospace; direction: ltr; display: inline; }
.insight-box .num-red { color: var(--crimson);  font-weight: 700; font-family: 'DM Mono', monospace; direction: ltr; display: inline; }

/* ── SIGNAL BADGES ── */
.sig-buy  { background: var(--emerald); color:#000; padding:3px 12px; border-radius:20px; font-weight:700; font-size:0.78rem; font-family:'DM Mono',monospace; }
.sig-sell { background: var(--crimson);  color:#fff; padding:3px 12px; border-radius:20px; font-weight:700; font-size:0.78rem; font-family:'DM Mono',monospace; }
.sig-hold { background: var(--sapphire); color:#000; padding:3px 12px; border-radius:20px; font-weight:700; font-size:0.78rem; font-family:'DM Mono',monospace; }

/* ── METRIC CARD ── */
.metric-card {
  background: linear-gradient(145deg, var(--bg-card), var(--bg-card2));
  border: 1px solid var(--border);
  border-radius: var(--radius);
  padding: 20px;
  transition: border-color var(--transition);
}
.metric-card:hover { border-color: rgba(255,215,0,0.2); }
.metric-card-title {
  font-size: 0.9rem; font-weight: 700; text-align: center; margin-bottom: 14px;
}
.metric-row {
  display: flex; justify-content: space-between; align-items: center;
  padding: 8px 0; border-bottom: 1px solid var(--border); font-size: 0.8rem; direction: rtl;
}
.metric-row:last-child { border-bottom: none; }
.metric-label { color: var(--text-faint); }
.metric-val { font-family: 'DM Mono', monospace; font-size: 0.82rem; }

/* ── GOLD DIVIDER ── */
.gold-divider {
  height: 1px;
  background: linear-gradient(90deg, transparent, rgba(255,215,0,0.15), transparent);
  margin: 18px 0;
}

/* ── SIDEBAR LOGO ── */
.sb-logo {
  text-align: center;
  padding: 24px 16px 16px;
  background: linear-gradient(180deg, rgba(255,215,0,0.03) 0%, transparent 100%);
  border-bottom: 1px solid var(--border);
  margin-bottom: 8px;
}
.sb-logo-icon { font-size: 2.4rem; line-height: 1; margin-bottom: 6px; }
.sb-logo-text {
  font-family: 'Bebas Neue', sans-serif;
  letter-spacing: 4px; color: var(--gold);
  font-size: 1.1rem; direction: ltr;
}
.sb-logo-sub { font-size: 0.62rem; color: var(--text-faint); direction: rtl; margin-top: 2px; letter-spacing: 0.5px; }

/* ── SIDEBAR SOURCE ── */
.sb-src { padding: 4px 0; }
.sb-src-head { color: var(--gold); font-size: 0.66rem; font-weight: 700; direction: rtl; text-align: right; margin-bottom: 3px; letter-spacing: 0.3px; }
.sb-src-val  { color: var(--text-faint); font-family: 'DM Mono', monospace; font-size: 0.6rem; direction: ltr; text-align: left; line-height: 1.9; }

/* ── LIVE BADGE ── */
.live-badge {
  display: inline-flex; align-items: center; gap: 5px;
  background: rgba(6,214,160,0.1); border: 1px solid rgba(6,214,160,0.25);
  color: var(--emerald); font-size: 0.62rem; font-family: 'DM Mono', monospace;
  padding: 3px 10px; border-radius: 20px; letter-spacing: 1px;
}
.live-dot { width: 5px; height: 5px; background: var(--emerald); border-radius: 50%; animation: blink 1.5s infinite; }

/* ── FORECAST SLIDER ── */
.fc-label { color: var(--text-muted); font-size: 0.8rem; direction: rtl; text-align: right; margin-bottom: 4px; }

/* ── PAGE TRANSITION WRAPPER ── */
.page-content { animation: pageIn 0.4s cubic-bezier(0.4,0,0.2,1) both; }

/* ── FILTER TRANSITION ── */
.stSelectbox > div, .stSlider > div { transition: all 0.3s ease !important; }

/* ── MOBILE RESPONSIVE ── */
@media (max-width: 768px) {
  .main .block-container { padding: 0 0.4rem 0.5rem !important; }
  .hero-wrap { padding: 16px 14px; margin-bottom: 16px; }
  .hero-title { font-size: 1.25rem; }
  .hero-eyebrow { font-size: 0.58rem; letter-spacing: 2px; }
  .kpi-grid { grid-template-columns: repeat(2, 1fr); gap: 8px; }
  .kpi-value { font-size: 1.35rem; }
  .kpi-label { font-size: 0.62rem; }
  .kpi-card { padding: 14px 10px; }
  .section-text { font-size: 0.88rem; }
  .insight-box { font-size: 0.78rem; padding: 11px 14px 11px 10px; }
  .metric-card { padding: 14px; }
}
@media (max-width: 480px) {
  .kpi-grid { grid-template-columns: repeat(2, 1fr); gap: 6px; }
  .hero-title { font-size: 1.05rem; line-height: 1.25; }
  .hero-wrap { padding: 12px 10px; }
  .hero-date { font-size: 0.65rem; }
  .hero-badge { font-size: 0.58rem; padding: 3px 8px; }
  .sb-logo-text { font-size: 0.9rem; }
}

/* ── HIDE CLUTTER ── */
#MainMenu, footer, .stDeployButton { display: none !important; }
header { visibility: visible !important; background: transparent !important; }
[data-testid="collapsedControl"] {
  visibility: visible !important; background: #07101F !important;
  border-right: 1px solid rgba(255,215,0,0.15) !important;
}
[data-testid="collapsedControl"] svg { fill: var(--gold) !important; }

/* ── SCROLLBAR ── */
::-webkit-scrollbar { width: 4px; }
::-webkit-scrollbar-track { background: var(--bg-void); }
::-webkit-scrollbar-thumb { background: #1E3A5F; border-radius: 4px; }
::-webkit-scrollbar-thumb:hover { background: var(--gold-dim); }

/* ── DATAFRAME ── */
.stDataFrame { border-radius: var(--radius-sm) !important; overflow: hidden; }

/* ── CHART wrapper - glass card behind every plotly ── */
.stPlotlyChart {
  background: linear-gradient(145deg, rgba(10,21,37,0.7), rgba(13,30,54,0.5));
  border: 1px solid var(--border);
  border-radius: var(--radius);
  padding: 4px;
  box-shadow: 0 4px 40px rgba(0,0,0,0.4);
  margin-bottom: 4px;
}

/* ── Streamlit slider premium (TradingView style) ── */

[data-testid="stSlider"] > div > div > div {
  background: linear-gradient(
      90deg,
      #ff4d4d 0%,
      #ff7a7a 25%,
      #ffb347 60%,
      var(--gold) 100%
  ) !important;

  height: 4px !important;
  border-radius: 10px !important;
}

/* ── Slider handle (النقطة) ── */

[data-testid="stSlider"] [role="slider"] {
  background: var(--gold) !important;
  border: 2px solid #fff !important;
  width: 14px !important;
  height: 14px !important;
  border-radius: 50% !important;

  box-shadow:
      0 0 6px rgba(255,215,0,0.8),
      0 0 14px rgba(255,215,0,0.35);
}

/* ── إزالة الخلفية الصفراء للأرقام ── */

[data-baseweb="slider"] [role="tooltip"] {
  background: transparent !important;
  color: var(--gold) !important;
  border: none !important;
  box-shadow: none !important;
  font-weight: 600;
  padding: 0 !important;
}

/* إزالة المربع نهائياً */
[data-baseweb="slider"] [role="tooltip"]::before,
[data-baseweb="slider"] [role="tooltip"]::after {
  display: none !important;
}

/* ── Streamlit toggle ── */
[data-testid="stToggle"] input:checked + div {
  background-color: var(--gold-dim) !important;
}
[data-testid="stSlider"] [role="slider"]:hover {
  transform: scale(1.2);
}

/* ── Remove top gap injected by streamlit ── */
.stApp > header + div { margin-top: 0 !important; }
div[data-testid="stAppViewContainer"] > section > div:first-child { padding-top: 0 !important; }
</style>
""", unsafe_allow_html=True)

OUNCE_TO_GRAM = 31.1035
KARAT_FACTORS = {'24K': 1.000, '21K': 0.875, '18K': 0.750}
KARAT_COLORS  = {'24K': '#FFF9C4', '21K': '#FFD700', '18K': '#CD7F32'}

CRISIS_EVENTS = {
    "2020-03-15": ("🦠 COVID-19",           "#FF6B6B", "rgba(255,107,107,0.06)"),
    "2022-02-24": ("🇺🇦 روسيا-أوكرانيا",  "#FF9F43", "rgba(255,159,67,0.06)"),
    "2022-03-21": ("📉 تعويم 1",            "#EF476F", "rgba(239,71,111,0.07)"),
    "2022-10-27": ("📉 تعويم 2",            "#EF476F", "rgba(239,71,111,0.07)"),
    "2023-10-07": ("⚔️ حرب غزة",           "#FF6B6B", "rgba(255,107,107,0.07)"),
    "2024-03-06": ("🔓 تعويم الجنيه",      "#06D6A0", "rgba(6,214,160,0.07)"),
    "2024-04-01": ("📈 ذهب 2265$",          "#FFD700", "rgba(255,215,0,0.05)"),
    "2024-09-18": ("✂️ Fed خفض الفائدة",   "#4CC9F0", "rgba(76,201,240,0.06)"),
    "2025-01-19": ("🕊️ وقف إطلاق النار",  "#06D6A0", "rgba(6,214,160,0.06)"),
    "2025-04-02": ("🔥 رسوم ترامب",        "#FF9F43", "rgba(255,159,67,0.07)"),
    "2025-04-22": ("🏆 ذهب 3500$",          "#FFD700", "rgba(255,215,0,0.06)"),
    "2025-06-13": ("💥 ضربة إيران",         "#EF476F", "rgba(239,71,111,0.08)"),
}

def _scrape_gold_usd():
    try:
        r = requests.get("https://data-asg.goldprice.org/dbXRates/USD",
                         headers=_HEADERS, timeout=10)
        return float(r.json()["items"][0]["xauPrice"])
    except Exception:
        return None

def _scrape_gold_usd_yf():
    try:
        df = yf.download("GC=F", period="5d", progress=False, auto_adjust=False)
        if df.empty: return None
        if isinstance(df.columns, pd.MultiIndex): df.columns = df.columns.droplevel(1)
        col = "Adj Close" if "Adj Close" in df.columns else "Close"
        return float(df[col].dropna().iloc[-1])
    except Exception:
        return None

def _scrape_usd_egp():
    try:
        r = requests.get("https://api.exchangerate-api.com/v4/latest/USD",
                         headers=_HEADERS, timeout=10)
        return float(r.json()["rates"]["EGP"])
    except Exception:
        return None

def _scrape_usd_egp_backup():
    try:
        r = requests.get("https://api.frankfurter.app/latest?from=USD&to=EGP",
                         headers=_HEADERS, timeout=10)
        return float(r.json()["rates"]["EGP"])
    except Exception:
        return None

def _scrape_usd_egp_yf():
    try:
        df = yf.download("EGP=X", period="5d", progress=False, auto_adjust=False)
        if df.empty: return None
        if isinstance(df.columns, pd.MultiIndex): df.columns = df.columns.droplevel(1)
        col = "Adj Close" if "Adj Close" in df.columns else "Close"
        return float(df[col].dropna().iloc[-1])
    except Exception:
        return None

def _scrape_others():
    result = {}
    for name, ticker in [("Crude_Oil","CL=F"),("US_10Y_Treasury","^TNX"),("SP500","^GSPC")]:
        try:
            df = yf.download(ticker, period="5d", progress=False, auto_adjust=False)
            if df.empty: continue
            if isinstance(df.columns, pd.MultiIndex): df.columns = df.columns.droplevel(1)
            col = "Adj Close" if "Adj Close" in df.columns else "Close"
            result[name] = float(df[col].dropna().iloc[-1])
        except Exception:
            pass
    return result

def _load_historical(start="2020-01-01"):
    tickers = {
        "Gold_USD_Ounce":   "GC=F",
        "USD_EGP_Official": "EGP=X",
        "Crude_Oil":        "CL=F",
        "US_10Y_Treasury":  "^TNX",
        "SP500":            "^GSPC",
    }
    frames = []
    yesterday = (datetime.today() - timedelta(days=1)).strftime("%Y-%m-%d")
    for name, ticker in tickers.items():
        for attempt in range(3):
            try:
                df = yf.download(ticker, start=start, end=yesterday,
                                 progress=False, auto_adjust=False)
                if df.empty: break
                if isinstance(df.columns, pd.MultiIndex): df.columns = df.columns.droplevel(1)
                col = "Adj Close" if "Adj Close" in df.columns else "Close"
                frames.append(df[[col]].rename(columns={col: name}))
                break
            except Exception:
                if attempt < 2: time.sleep(2)
    if not frames: return pd.DataFrame()
    data = pd.concat(frames, axis=1, sort=True)
    data.index = pd.to_datetime(data.index)
    data.ffill(inplace=True)
    data.dropna(inplace=True)
    return data

def run_scraper():
    gold_usd = _scrape_gold_usd() or _scrape_gold_usd_yf()
    usd_egp  = _scrape_usd_egp() or _scrape_usd_egp_backup() or _scrape_usd_egp_yf()
    others   = _scrape_others()

    if os.path.exists(CSV_PATH):
        try:
            hist = pd.read_csv(CSV_PATH, index_col="Date", parse_dates=True)
        except Exception:
            hist = _load_historical()
    else:
        hist = _load_historical()

    if hist.empty:
        return False

    if gold_usd and usd_egp:
        today = datetime.today().replace(hour=0, minute=0, second=0, microsecond=0)
        row = {
            "Gold_USD_Ounce":   gold_usd,
            "USD_EGP_Official": usd_egp,
            "Crude_Oil":        others.get("Crude_Oil",        float("nan")),
            "US_10Y_Treasury":  others.get("US_10Y_Treasury",  float("nan")),
            "SP500":            others.get("SP500",             float("nan")),
        }
        today_df = pd.DataFrame([row], index=[today])
        hist = hist[hist.index.date != today.date()]
        hist = pd.concat([hist, today_df], sort=False)

    hist.ffill(inplace=True)
    hist.dropna(how="all", inplace=True)
    hist.sort_index(inplace=True)
    hist.index.name = "Date"
    hist.to_csv(CSV_PATH)
    return True

_BASE = dict(
    template="plotly_dark",
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(family="Cairo, DM Mono", color="#8D99AE", size=11),
    hovermode="x unified",
    autosize=True,
    margin=dict(l=30, r=30, t=90, b=30),
    hoverlabel=dict(bgcolor="#0C1830", font_size=12, font_family="Cairo",
                    bordercolor="#1E3A5F", namelength=-1),
    modebar=dict(bgcolor="rgba(0,0,0,0)", color="#3A4A65", activecolor="#FFD700"),
)

def _legend_clean(**kw):
    d = dict(
        orientation="h",
        y=1.15,
        yanchor="top",
        x=0.5,
        xanchor="center",
        bgcolor="rgba(0,0,0,0)",
        borderwidth=0,
        font=dict(size=10, family="Cairo"),
        itemsizing="constant"
    )
    d.update(kw)
    return d

def _xax(**kw):
    d = dict(showgrid=True, gridcolor="rgba(19,34,56,0.8)", gridwidth=1,
             showline=True, linecolor="#132238", zeroline=False,
             rangeslider=dict(visible=False),
             rangeselector=dict(
                 x=0,
                 xanchor="left",
                 y=1.12,
                 yanchor="top", bgcolor="#0A1525",
                 bordercolor="#132238", borderwidth=1, activecolor="#1E3A5F",
                 font=dict(size=9.5, color="#8D99AE"),
                 buttons=[
                     dict(count=3,  label="3M",  step="month", stepmode="backward"),
                     dict(count=6,  label="6M",  step="month", stepmode="backward"),
                     dict(count=1,  label="1Y",  step="year",  stepmode="backward"),
                     dict(count=2,  label="2Y",  step="year",  stepmode="backward"),
                     dict(label="الكل", step="all"),
                 ]
             ),
             tickfont=dict(size=9.5, color="#3A4A65"), tickformat="%b %Y")
    d.update(kw)
    return d

def _yax(**kw):
    d = dict(showgrid=True, gridcolor="rgba(19,34,56,0.8)", gridwidth=1,
             showline=True, linecolor="#132238", zeroline=False,
             tickfont=dict(size=9.5, color="#3A4A65"))
    d.update(kw)
    return d

def plot_layout(height=440, show_legend=True, title_text="", **extra):
    lyt = dict(**_BASE, height=height)
    lyt['legend'] = _legend_clean()
    lyt['xaxis']  = _xax(range=["2020-01-01", None])
    lyt['yaxis']  = _yax()
    if not show_legend:
        lyt['showlegend'] = False
    if title_text:
        lyt['title'] = dict(
            text=title_text,
            font=dict(size=13, color="#FFD700", family="Cairo"),
            x=0.5,
            xanchor="center",
            y=0.96,
            yanchor="top",
        )
    for k, v in extra.items():
        if k in ('xaxis','yaxis','legend') and isinstance(v, dict):
            lyt[k].update(v)
        else:
            lyt[k] = v
    return lyt

@st.cache_data(ttl=60, show_spinner=False)
def load_data(csv_path: str, mtime: float) -> pd.DataFrame:
    data = pd.read_csv(csv_path, index_col="Date", parse_dates=True)
    data.ffill(inplace=True)
    data.dropna(inplace=True)
    data['Theoretical_24K'] = (data['Gold_USD_Ounce'] / OUNCE_TO_GRAM) * data['USD_EGP_Official']

    for karat, factor in KARAT_FACTORS.items():
        p = data['Theoretical_24K'] * factor
        data[f'Price_{karat}']       = p
        data[f'ValueDriven_{karat}'] = (data['Gold_USD_Ounce'] / OUNCE_TO_GRAM) * factor * 15.7
        data[f'InflPrem_{karat}']    = p - data[f'ValueDriven_{karat}']
        data[f'PremPct_{karat}']     = (data[f'InflPrem_{karat}'] / p) * 100
        data[f'SMA50_{karat}']       = p.rolling(50, min_periods=1).mean()
        data[f'SMA200_{karat}']      = p.rolling(200, min_periods=1).mean()
        ema12 = p.ewm(span=12, adjust=False).mean()
        ema26 = p.ewm(span=26, adjust=False).mean()
        data[f'MACD_{karat}']        = ema12 - ema26
        data[f'MACDSig_{karat}']     = data[f'MACD_{karat}'].ewm(span=9, adjust=False).mean()
        data[f'MACDHist_{karat}']    = data[f'MACD_{karat}'] - data[f'MACDSig_{karat}']
        delta = p.diff()
        gain  = delta.where(delta > 0, 0).rolling(14).mean()
        loss  = (-delta.where(delta < 0, 0)).rolling(14).mean()
        rs    = gain / loss.replace(0, np.nan)
        data[f'RSI_{karat}']    = 100 - (100 / (1 + rs))
        data[f'BB_mid_{karat}'] = p.rolling(20).mean()
        bb_std = p.rolling(20).std()
        data[f'BB_up_{karat}']  = data[f'BB_mid_{karat}'] + 2 * bb_std
        data[f'BB_dn_{karat}']  = data[f'BB_mid_{karat}'] - 2 * bb_std
        buy  = (data[f'RSI_{karat}'] < 30) | (
                    (data[f'MACD_{karat}'] > data[f'MACDSig_{karat}']) &
                    (data[f'MACD_{karat}'].shift(1) <= data[f'MACDSig_{karat}'].shift(1)))
        sell = (data[f'RSI_{karat}'] > 70) | (
                    (data[f'MACD_{karat}'] < data[f'MACDSig_{karat}']) &
                    (data[f'MACD_{karat}'].shift(1) >= data[f'MACDSig_{karat}'].shift(1)))
        data[f'Signal_{karat}'] = np.select([buy, sell], ['BUY','SELL'], default='HOLD')

    cap = 100_000
    for karat in KARAT_FACTORS:
        grams = cap / data[f'Price_{karat}'].iloc[0]
        data[f'Port_{karat}'] = grams * data[f'Price_{karat}']
        rm = data[f'Port_{karat}'].cummax()
        data[f'DD_{karat}']   = (data[f'Port_{karat}'] / rm - 1) * 100
        data[f'Norm_{karat}'] = data[f'Price_{karat}'] / data[f'Price_{karat}'].iloc[0] * 100

    usd0 = data['USD_EGP_Official'].iloc[0]
    data['Port_USD']  = (cap / usd0) * data['USD_EGP_Official']
    data['Port_Cash'] = cap
    data['Norm_USD']  = data['Port_USD'] / cap * 100
    data['Norm_Cash'] = 100.0
    return data

def add_events(fig, data, rows=None, y_ann=0.98):
    sorted_events = sorted(CRISIS_EVENTS.items(), key=lambda x: x[0])
    for date_str, (label, color, fill) in sorted_events:
        dt = pd.to_datetime(date_str)
        if dt < data.index[0]: continue

        x1 = (dt + timedelta(days=15)).strftime('%Y-%m-%d')
        rect_kw = dict(x0=date_str, x1=x1, fillcolor=fill,
                       opacity=1, layer="below", line_width=0)
        if rows:
            for r in rows:
                fig.add_vrect(**rect_kw, row=r, col=1)
        else:
            fig.add_vrect(**rect_kw)

        fig.add_vline(
            x=pd.to_datetime(date_str).timestamp() * 1000,
            line=dict(color=color, width=0.8, dash="dot"),
            opacity=0.55,
        )

        fig.add_annotation(
            x=date_str,
            y=y_ann,
            yref="paper",
            xref="x",
            text=label,
            showarrow=False,
            font=dict(size=7.5, color=color, family="Cairo"),
            textangle=-90,
            xanchor="left",
            yanchor="top",
            bgcolor="rgba(3,6,15,0.55)",
            borderpad=2,
        )

def section(icon, title, sub=""):
    import re
    safe_title = re.sub(r'(\d+K)', r'<bdi>\1</bdi>', title)

    if isinstance(sub, list):
        sub_html = "".join(
            f'<div style="direction:{d};text-align:{"right" if d=="rtl" else "left"};'
            f'font-size:0.76rem;color:var(--text-faint);margin:0 0 2px 0;">{t}</div>'
            for t, d in sub
        )
    elif sub:
        sub_html = f'<div class="section-sub">{sub}</div>'
    else:
        sub_html = ""
    st.markdown(f"""
    <div class="section-wrap" style="animation-delay:0.1s">
      <div class="section-title">
        <span class="section-text">{safe_title}</span>
        <span class="section-icon">{icon}</span>
      </div>
      <div class="section-line"></div>
      {sub_html}
    </div>""", unsafe_allow_html=True)

def spacer(h=16):
    st.markdown(f"<div style='height:{h}px'></div>", unsafe_allow_html=True)

def kpi_html(value, label, color, delay="0s"):
    return f"""<div class="kpi-card" style="animation-delay:{delay}">
        <div class="kpi-value" style="color:{color}">{value}</div>
        <div class="kpi-label">{label}</div>
    </div>"""

def insight(html):
    st.markdown(f'<div class="insight-box">{html}</div>', unsafe_allow_html=True)

def compute_metrics(data, karat):
    col = f'Port_{karat}'
    ret = data[col].pct_change().dropna()
    total  = (data[col].iloc[-1] / 100_000 - 1) * 100
    ann_r  = ret.mean() * 252
    ann_v  = ret.std()  * np.sqrt(252)
    sharpe = ann_r / ann_v if ann_v else 0
    max_dd = data[f'DD_{karat}'].min()
    var95  = ret.quantile(0.05) * 100
    return dict(total=total, sharpe=sharpe, max_dd=max_dd, var95=var95,
                final=data[col].iloc[-1], ann_ret=ann_r*100, ann_vol=ann_v*100)

_need_scrape = False
if not os.path.exists(CSV_PATH):
    _need_scrape = True
else:
    _age_hours = (time.time() - os.path.getmtime(CSV_PATH)) / 3600
    if _age_hours > 6:
        _need_scrape = True

if _need_scrape:
    with st.spinner("⏳ جاري جلب بيانات الذهب... (مرة واحدة فقط)"):
        run_scraper()

with st.sidebar:
    st.markdown("""
    <div class="sb-logo">
      <div class="sb-logo-icon">🥇</div>
      <div class="sb-logo-text">GOLD EGYPT</div>
      <div class="sb-logo-sub">أداة التحليل المالي · منذ 2020</div>
    </div>""", unsafe_allow_html=True)

    pages = {
        "home": "🏠  الرئيسية",
        "analysis": "📊  تحليل الأسعار",
        "compare": "⚖️  مقارنة العيارات",
        "investment": "💼  محاكاة الاستثمار",
        "technical": "📡  المؤشرات التقنية",
        "forecast": "🔮  التوقعات",
    }

    query = st.query_params
    default_key = query.get("page", "home")

    if default_key not in pages:
        default_key = "home"

    page_labels = list(pages.values())
    page_keys = list(pages.keys())

    default_index = page_keys.index(default_key)

    page_label = st.radio(
        "",
        page_labels,
        index=default_index,
        label_visibility="collapsed"
    )

    selected_key = page_keys[page_labels.index(page_label)]

    st.query_params["page"] = selected_key

    page = page_label

    st.markdown('<div class="gold-divider"></div>', unsafe_allow_html=True)

    st.markdown('<div style="color:#8D99AE;font-size:0.78rem;direction:rtl;text-align:right;margin-bottom:4px;">العيار الرئيسي</div>', unsafe_allow_html=True)
    selected_karat = st.selectbox("k", ["18K","21K","24K"], index=1, label_visibility="collapsed")

    spacer(6)
    show_events = st.toggle("أحداث الأزمات", value=True)

    if show_events:
        st.markdown("""
        <div style="font-size:0.6rem;color:#3A4A65;direction:rtl;text-align:right;
                    line-height:2;padding:4px 0;margin-top:2px;">
          <span style="color:#FF6B6B">●</span> كوفيد · غزة &nbsp;
          <span style="color:#FF9F43">●</span> أوكرانيا · ترامب<br>
          <span style="color:#EF476F">●</span> تعويم الجنيه &nbsp;
          <span style="color:#4CC9F0">●</span> الفيد · فائدة<br>
          <span style="color:#06D6A0">●</span> تعويم 2024 · وقف نار &nbsp;
          <span style="color:#FFD700">●</span> قياسيات ذهب
        </div>""", unsafe_allow_html=True)

    st.markdown('<div class="gold-divider"></div>', unsafe_allow_html=True)

    if st.button("🔄 تحديث البيانات الآن", use_container_width=True):
        with st.spinner("⏳ جاري التحديث..."):
            run_scraper()
        st.cache_data.clear()
        st.rerun()

    if os.path.exists(CSV_PATH):
        _mt  = datetime.fromtimestamp(os.path.getmtime(CSV_PATH)).strftime("%Y-%m-%d %H:%M")
        _sc  = "#06D6A0"
        _stx = f"✅ آخر تحديث:<br>{_mt}"
    else:
        _sc  = "#EF476F"
        _stx = "⏳ جاري تهيئة البيانات..."

    st.markdown(
        f'<div style="text-align:center;font-size:0.62rem;color:{_sc};'
        f'font-family:DM Mono,monospace;margin-top:6px;line-height:1.8;">{_stx}</div>',
        unsafe_allow_html=True)

    st.markdown('<div class="gold-divider"></div>', unsafe_allow_html=True)

    st.markdown("""
    <div class="sb-src">
      <div class="sb-src-head">مصادر البيانات</div>
      <div class="sb-src-val">goldprice.org · exchangerate-api · yfinance</div>
      <div class="sb-src-val">GC=F · EGP=X · CL=F · ^TNX · ^GSPC</div>
    </div>
    <div style="height:10px"></div>
    <div class="sb-src">
      <div class="sb-src-head">منحة رواد مصر الرقمية</div>
      <div class="sb-src-val">DEPI Final Project · 2026</div>
    </div>""", unsafe_allow_html=True)

if not os.path.exists(CSV_PATH):
    st.error("❌ فشل تحميل البيانات - تحقق من الاتصال بالإنترنت")
    st.stop()

_mtime_key = os.path.getmtime(CSV_PATH)

with st.spinner(""):
    data = load_data(CSV_PATH, _mtime_key)

if data.empty:
    st.error("❌ فشل قراءة البيانات"); st.stop()

last_date   = data.index[-1]
last_date_f = last_date.strftime('%d %b %Y')
last_price  = data[f'Price_{selected_karat}'].iloc[-1]
last_usd    = data['USD_EGP_Official'].iloc[-1]
last_gold   = data['Gold_USD_Ounce'].iloc[-1]

st.markdown('<div class="page-content">', unsafe_allow_html=True)

st.markdown("""
<script>
  const el = window.parent.document.querySelector('.main .block-container');
  if (el) el.style.paddingTop = '0px';
</script>
""", unsafe_allow_html=True)

if page == "🏠  الرئيسية":

    m = compute_metrics(data, selected_karat)

    st.markdown(f"""
    <div class="hero-wrap">
      <div class="hero-eyebrow">GOLD EGYPT · FINANCIAL INTELLIGENCE PLATFORM</div>
      <div class="hero-title">🥇 الذهب كأداة مالية في مصر</div>
      <div class="hero-sub">
        تحليل شامل لأداء الذهب بالعيارات
        <span style="font-family:'DM Mono',monospace; direction:ltr; display:inline;"> 18K · 21K · 24K </span>
        كأداة للحفاظ على القيمة في مواجهة التضخم وانخفاض الجنيه
      </div>
      <div class="hero-date">
        <span class="dot"></span>
        LIVE · Jan 2020 - {last_date_f}
      </div>
      <div class="hero-badges">
        <span class="hero-badge">DEPI 2026</span>
        <span class="hero-badge">منحة رواد مصر الرقمية</span>
      </div>
    </div>""", unsafe_allow_html=True)

    clr24 = '#06D6A0' if m['total'] > 0 else '#EF476F'
    cards_html = (
        kpi_html(f"{last_price:,.0f}", f"جنيه/جرام {selected_karat}", "#FFD700", "0.05s") +
        kpi_html(f"{last_usd:.2f}", "جنيه / دولار", "#4CC9F0", "0.10s") +
        kpi_html(f"${last_gold:,.0f}", "أونصة عالمياً", "#06D6A0", "0.15s") +
        kpi_html(f"{m['total']:+.0f}%", f"عائد الذهب {selected_karat} من 2020", clr24, "0.20s") +
        kpi_html(f"{m['sharpe']:.2f}", "Sharpe Ratio", "#A855F7", "0.25s")
    )
    st.markdown(f'<div class="kpi-grid">{cards_html}</div>', unsafe_allow_html=True)

    spacer(24)

    section("📈", "مسار سعر الذهب", "")

    st.markdown(f"""
    <div class="section-sub" style="display:flex;justify-content:space-between;align-items:center;margin-bottom:10px;">

    <div style="direction:rtl">
    سعر جرام {selected_karat} بالجنيه المصري
    </div>
    
    <div style="direction:ltr">
    Jan 2020 - {last_date_f}
    </div>

    </div>
    """, unsafe_allow_html=True)

    pc = f'Price_{selected_karat}'
    clr = KARAT_COLORS[selected_karat]
    fill_map = {'24K':'rgba(255,249,196,0.07)','21K':'rgba(255,215,0,0.07)','18K':'rgba(205,127,50,0.07)'}
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=data.index, y=data[pc], name=f'{selected_karat} سعر جرام',
        line=dict(color=clr, width=2), fill='tozeroy', fillcolor=fill_map[selected_karat],
        hovertemplate="<b>%{x|%d %b %Y}</b><br>%{y:,.0f} جنيه<extra></extra>"))
    fig.add_trace(go.Scatter(x=data.index, y=data[f'SMA50_{selected_karat}'],
        name='SMA 50', line=dict(color='#FF9F43', width=1.2, dash='dot'),
        hovertemplate="SMA50: %{y:,.0f}<extra></extra>"))
    fig.add_trace(go.Scatter(x=data.index, y=data[f'SMA200_{selected_karat}'],
        name='SMA 200', line=dict(color='#A855F7', width=1.2, dash='dot'),
        hovertemplate="SMA200: %{y:,.0f}<extra></extra>"))
    if show_events: add_events(fig, data)
    fig.update_layout(**plot_layout(height=420))
    st.plotly_chart(fig, use_container_width=True, config=dict(displayModeBar=True, displaylogo=False, responsive=True))

    spacer()

    price_chg = (data[pc].iloc[-1]/data[pc].iloc[0]-1)*100
    peak_p    = data[pc].max()
    peak_d    = data[pc].idxmax().strftime('%b %Y')
    usd_chg   = (data['USD_EGP_Official'].iloc[-1]/data['USD_EGP_Official'].iloc[0]-1)*100

    c1, c2 = st.columns(2)
    with c1:
        insight(f"📌 <b>الأداء الإجمالي:</b> ارتفع الذهب {selected_karat} بنسبة <span class='num'>{price_chg:.0f}%</span> منذ يناير 2020، مقارنةً بالدولار الذي ارتفع <span class='num'>{usd_chg:.0f}%</span> فقط خلال نفس الفترة.")
    with c2:
        insight(f"🏔️ <b>القمة التاريخية:</b> <span class='num'>{peak_p:,.0f} جنيه</span> لجرام {selected_karat} في <b>{peak_d}</b> - مدفوعاً بتراجع الجنيه وارتفاع الأسعار العالمية.")

    spacer(24)

    section("🗓️", "أبرز الأحداث المؤثرة على سعر الذهب", "2020 – 2025")
    events_cards = {
        "2020-03-15": ("🦠", "COVID-19", "مارس 2020", "انهيار الأسواق العالمية - الذهب يرتفع كملاذ آمن", "#FF6B6B"),
        "2022-02-24": ("🇺🇦", "روسيا-أوكرانيا", "فبراير 2022", "الغزو الروسي وارتفاع الطاقة والذهب عالمياً", "#FF9F43"),
        "2022-03-21": ("📉", "تعويم 1", "مارس 2022", "أول تعويم للجنيه يرفع الذهب المحلي بشكل حاد", "#EF476F"),
        "2023-10-07": ("⚔️", "حرب غزة", "أكتوبر 2023", "اندلاع المواجهة يرفع الطلب على الذهب كملاذ", "#FF6B6B"),
        "2024-03-06": ("🔓", "تعويم 2024", "مارس 2024", "تعويم شامل للجنيه: الدولار يقفز من 30 إلى 50 جنيهاً", "#06D6A0"),
        "2024-09-18": ("✂️", "خفض الفائدة", "سبتمبر 2024", "الفيدرالي يبدأ دورة خفض الفائدة - دعم قوي للذهب", "#4CC9F0"),
        "2025-01-19": ("🕊️", "وقف إطلاق النار", "يناير 2025", "اتفاق غزة يُهدئ مؤقتاً - الذهب يتراجع طفيفاً", "#06D6A0"),
        "2025-04-02": ("🔥", "رسوم ترامب", "أبريل 2025", "إعلان الرسوم الجمركية الشاملة يدفع الذهب لـ 3500$", "#FF9F43"),
        "2025-04-22": ("🏆", "قياسي 3500$", "أبريل 2025", "الذهب يكسر 3500$ لأول مرة في التاريخ", "#FFD700"),
        "2025-06-13": ("💥", "ضربة إيران", "يونيو 2025", "الضربة الإسرائيلية-الأمريكية على إيران ترفع الذهب فوراً", "#EF476F"),
    }
    cols_ev = st.columns(3)
    for idx, (date_str, (icon, title, date_lbl, desc, color)) in enumerate(events_cards.items()):
        with cols_ev[idx % 3]:
            st.markdown(f"""
            <div style="background:linear-gradient(145deg,#0A1525,#0D1E36);
                        border:1px solid #132238;border-radius:12px;padding:14px 14px;
                        margin-bottom:10px;border-top:2px solid {color};
                        transition:border-color 0.3s;">
              <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:6px;">
                <span style="font-size:1.3rem">{icon}</span>
                <span style="font-family:'DM Mono',monospace;font-size:0.6rem;color:#3A4A65">{date_lbl}</span>
              </div>
              <div style="color:{color};font-weight:700;font-size:0.82rem;direction:rtl;margin-bottom:4px">{title}</div>
              <div style="color:#6B7A99;font-size:0.72rem;direction:rtl;line-height:1.6">{desc}</div>
            </div>""", unsafe_allow_html=True)

    spacer(24)

    c1, c2 = st.columns([1.2, 1])
    with c1:
        section("🔗", "مصفوفة الارتباط", "")

        st.markdown("""
        <div class="section-sub" style="display:flex;justify-content:space-between;align-items:center;margin-bottom:10px;">
        <div style="direction:rtl">قوة العلاقة بين الذهب والمتغيرات الاقتصادية الكلية</div>
        <div style="direction:ltr">Correlation Matrix · Heatmap</div>
        </div>
        """, unsafe_allow_html=True)
        cols_ = ['Gold_USD_Ounce','USD_EGP_Official','Crude_Oil','US_10Y_Treasury','SP500']
        names = ['ذهب عالمي','دولار/جنيه','نفط','سندات أمريكية','S&P 500']
        cd = data[cols_].dropna().corr()
        cd.columns = names; cd.index = names
        fc = px.imshow(cd, text_auto=".2f",
            color_continuous_scale=[[0,'#EF476F'],[0.5,'#060C18'],[1,'#06D6A0']],
            zmin=-1, zmax=1)
        cl = plot_layout(height=420, show_legend=False)
        cl['margin'] = dict(l=8, r=8, t=30, b=50)
        cl['coloraxis_showscale'] = False
        fc.update_layout(**cl)
        fc.update_traces(textfont=dict(size=12, family="DM Mono"))
        st.plotly_chart(fc, use_container_width=True, config=dict(displaylogo=False, responsive=True))

    with c2:
        section("💱", "مسار الدولار", "")

        st.markdown("""
        <div class="section-sub" style="display:flex;justify-content:space-between;align-items:center;margin-bottom:10px;">
        
        <div style="direction:rtl">
        صعود الدولار يعني ارتفاعاً مباشراً في الذهب
        </div>
        
        <div style="direction:ltr">
        USD / EGP
        </div>

        </div>
        """, unsafe_allow_html=True)
        fu = go.Figure()
        fu.add_trace(go.Scatter(x=data.index, y=data['USD_EGP_Official'],
            line=dict(color='#4CC9F0', width=2), fill='tozeroy',
            fillcolor='rgba(76,201,240,0.06)',
            hovertemplate="%{x|%d %b %Y}<br><b>%{y:.2f} جنيه</b><extra></extra>"))
        if show_events: add_events(fu, data)
        fu.update_layout(**plot_layout(height=420, show_legend=False))
        st.plotly_chart(fu, use_container_width=True, config=dict(displaylogo=False, responsive=True))

elif page == "📊  تحليل الأسعار":

    section("📊", "تشريح السعر - قيمة حقيقية أم تضخم؟", "")

    st.markdown("""
    <div class="section-sub" style="display:flex;justify-content:space-between;align-items:center;margin-bottom:10px;">
    <div style="direction:rtl">كم من السعر يعكس ارتفاع الذهب عالمياً، وكم يعكس انهيار قيمة الجنيه؟</div>
    <div style="direction:ltr">Stacked Area · 24K · 21K · 18K</div>
    </div>
    """, unsafe_allow_html=True)

    fig = make_subplots(
        rows=3,
        cols=1,
        shared_xaxes=True,
        row_heights=[0.34,0.33,0.33],
        vertical_spacing=0.10,
        subplot_titles=["24K","21K","18K"]
    )

    KFILL = {'24K':'rgba(255,249,196,0.65)','21K':'rgba(255,215,0,0.65)','18K':'rgba(205,127,50,0.65)'}
    KROW  = {'24K':1,'21K':2,'18K':3}

    for karat in ['24K','21K','18K']:
        row = KROW[karat]
        fig.add_trace(go.Scatter(x=data.index, y=data[f'ValueDriven_{karat}'],
            name='قيمة عالمية', stackgroup=f'g{row}', mode='lines',
            line=dict(width=0), fillcolor=KFILL[karat],
            showlegend=(row==1), legendgroup='gv',
            hovertemplate=f"{karat} - قيمة: %{{y:,.0f}}<extra></extra>"), row=row, col=1)
        fig.add_trace(go.Scatter(x=data.index, y=data[f'InflPrem_{karat}'],
            name='علاوة تضخم', stackgroup=f'g{row}', mode='lines',
            line=dict(width=0), fillcolor='rgba(239,71,111,0.50)',
            showlegend=(row==1), legendgroup='gi',
            hovertemplate=f"{karat} - علاوة: %{{y:,.0f}}<extra></extra>"), row=row, col=1)

    if show_events: add_events(fig, data, rows=[1,2,3])
    lyt = plot_layout(height=800)
    lyt['margin'] = dict(l=8, r=8, t=160, b=8)
    lyt['legend'] = dict(orientation="h", y=1.12, x=0.5, xanchor="center",
        bgcolor="rgba(0,0,0,0)", borderwidth=0,
        font=dict(size=10, family="Cairo"), itemsizing="constant")
    lyt['xaxis']['rangeselector']['y'] = 1.06
    lyt['title'] = dict(text="تشريح السعر: القيمة الحقيقية مقابل علاوة التضخم",
        font=dict(size=13, color="#FFD700", family="Cairo"), x=0.5, xanchor='center', y=0.98)
    fig.update_layout(**lyt)
    fig.update_xaxes(tickfont=dict(family="Cairo", size=10, color="#4A6A8A"),gridcolor="rgba(255, 255, 255, 0.05)",range=["2020-01-01", data.index.max()])
    event_labels = {v[0] for v in CRISIS_EVENTS.values()}
    for ann in fig.layout.annotations:
        if ann.text not in event_labels:
            ann.update(x=0.98, xanchor='right', font=dict(color='#B8960C', size=10.5, family='Cairo'))
    for r in [1,2,3]: fig.update_yaxes(tickfont=dict(family="Cairo",size=11, color="#4A6A8A"),title_text="جنيه", title_font=dict(size=9), row=r, col=1)
    st.plotly_chart(fig, use_container_width=True, config=dict(displaylogo=False, responsive=True))

    spacer(24)
    section("📐", "نسبة علاوة التضخم %", "")

    st.markdown("""
    <div class="section-sub" style="display:flex;justify-content:space-between;align-items:center;margin-bottom:10px;">
    <div style="direction:rtl">النسبة المئوية من السعر ناتجة عن ضعف الجنيه - كلما ارتفعت، كلما كان الذهب وقاية أكبر</div>
    <div style="direction:ltr">Inflation Premium %</div>
    </div>
    """, unsafe_allow_html=True)

    fig2 = go.Figure()
    for karat, color in KARAT_COLORS.items():
        fig2.add_trace(go.Scatter(x=data.index, y=data[f'PremPct_{karat}'],
            name=karat, line=dict(color=color, width=2),
            hovertemplate=f"{karat}: %{{y:.1f}}%<extra></extra>"))
    fig2.add_hline(y=0, line_dash="dot", line_color="#1E3A5F", opacity=0.8)
    if show_events: add_events(fig2, data)
    fig2.update_layout(**plot_layout(height=340, yaxis=dict(title_text="علاوة %")))
    st.plotly_chart(fig2, use_container_width=True, config=dict(displaylogo=False, responsive=True))

    spacer()
    cols = st.columns(3)
    for col, karat in zip(cols, KARAT_FACTORS):
        ap = data[f'PremPct_{karat}'].mean()
        mx = data[f'PremPct_{karat}'].max()
        with col:
            insight(f"<b style='color:{KARAT_COLORS[karat]}'>{karat}</b><br>متوسط العلاوة: <span class='num'>{ap:.1f}%</span><br>الذروة التاريخية: <span class='num-red'>{mx:.1f}%</span>")

elif page == "⚖️  مقارنة العيارات":

    section("⚖️", "مقارنة العيارات", "")

    st.markdown("""
    <div class="section-sub" style="display:flex;justify-content:space-between;align-items:center;margin-bottom:10px;">

    <div style="direction:rtl">
    كل الأصول تبدأ من نقطة واحدة - أيها حقق أفضل أداء؟
    </div>
    
    <div style="direction:ltr">
    Base 100 · يناير 2020 = 100
    </div>

    </div>
    """, unsafe_allow_html=True)
    fig = go.Figure()
    for karat, color in KARAT_COLORS.items():
        fig.add_trace(go.Scatter(x=data.index, y=data[f'Norm_{karat}'],
            name=f'{karat} ذهب', line=dict(color=color, width=2.5),
            hovertemplate=f"<b>{karat}</b>: %{{y:.1f}}<extra></extra>"))
    fig.add_trace(go.Scatter(x=data.index, y=data['Norm_USD'],
        name='دولار 💵', line=dict(color='#4CC9F0', width=1.6, dash='dot'),
        hovertemplate="دولار: %{y:.1f}<extra></extra>"))
    fig.add_trace(go.Scatter(x=data.index, y=data['Norm_Cash'],
        name='كاش 💸', line=dict(color='#1E3A5F', width=1.2, dash='dot'),
        hovertemplate="كاش: %{y:.1f}<extra></extra>"))
    if show_events: add_events(fig, data)
    lyt_kc = plot_layout(height=460, yaxis=dict(title_text="مؤشر (يناير 2020 = 100)"))
    lyt_kc['title'] = dict(text="المقارنة الموحدة لكل الأصول منذ 2020",
        font=dict(size=13, color="#FFD700", family="Cairo"), x=0.5, xanchor='center', y=0.97)
    fig.update_layout(**lyt_kc)
    st.plotly_chart(fig, use_container_width=True, config=dict(displaylogo=False, responsive=True))

    spacer(24)
    c1, c2 = st.columns([1.15, 1])

    with c1:
        section("📋", "جدول المقاييس المالية", "")

        st.markdown("""
        <div class="section-sub" style="display:flex;justify-content:space-between;align-items:center;margin-bottom:10px;">
        <div style="direction:rtl">مقارنة شاملة لكل عيار وأصل</div>
        <div style="direction:ltr">Sharpe · Max DD · VaR 95%</div>
        </div>
        """, unsafe_allow_html=True)
        rows = []
        for karat in KARAT_FACTORS:
            m = compute_metrics(data, karat)
            rows.append({"العيار":karat, "العائد الكلي":f"{m['total']:+.1f}%",
                         "Sharpe":f"{m['sharpe']:.2f}", "Max DD":f"{m['max_dd']:.1f}%",
                         "VaR 95%":f"{m['var95']:.2f}%", "القيمة النهائية":f"{m['final']:,.0f}"})
        usd_ret = (data['Port_USD'].iloc[-1]/100_000-1)*100
        rows.append({"العيار":"دولار 💵","العائد الكلي":f"{usd_ret:+.1f}%",
                     "Sharpe":"-","Max DD":"-","VaR 95%":"-",
                     "القيمة النهائية":f"{data['Port_USD'].iloc[-1]:,.0f}"})
        st.dataframe(pd.DataFrame(rows).set_index("العيار"), use_container_width=True)

    with c2:
        section("📊", "مقارنة العوائد", "")

        st.markdown("""
        <div class="section-sub" style="display:flex;justify-content:space-between;align-items:center;margin-bottom:10px;">
        <div style="direction:rtl">100,000 جنيه · يناير 2020</div>
        <div style="direction:ltr">Total Return % · Bar Chart</div>
        </div>
        """, unsafe_allow_html=True)
        bv = [compute_metrics(data,'18K')['total'], compute_metrics(data,'21K')['total'],
              compute_metrics(data,'24K')['total'], usd_ret, 0]
        fb = go.Figure(go.Bar(x=['18K','21K','24K','USD','Cash'], y=bv,
            marker_color=['#CD7F32','#FFD700','#FFF9C4','#4CC9F0','#132238'],
            text=[f"{v:+.0f}%" for v in bv], textposition='outside',
            textfont=dict(size=11.5, color='white', family="DM Mono"),
            hovertemplate="%{x}: %{y:+.1f}%<extra></extra>"))
        fb.update_layout(**plot_layout(height=360, show_legend=False,
            yaxis=dict(title_text="العائد الكلي %")))
        st.plotly_chart(fb, use_container_width=True, config=dict(displaylogo=False, responsive=True))

elif page == "💼  محاكاة الاستثمار":

    section("💼", "محاكاة الاستثمار", "")

    st.markdown("""
    <div class="section-sub" style="display:flex;justify-content:space-between;align-items:center;margin-bottom:10px;">
    <div style="direction:rtl">لو استثمرت 100,000 جنيه في يناير 2020 - كم تساوي اليوم؟</div>
    <div style="direction:ltr">Portfolio Simulation · EGP 100K</div>
    </div>
    """, unsafe_allow_html=True)

    fig = go.Figure()
    for karat, color in KARAT_COLORS.items():
        fig.add_trace(go.Scatter(x=data.index, y=data[f'Port_{karat}'],
            name=f'{karat} ذهب', line=dict(color=color, width=2.2),
            hovertemplate=f"<b>{karat}</b>: %{{y:,.0f}} جنيه<extra></extra>"))
    fig.add_trace(go.Scatter(x=data.index, y=data['Port_USD'],
        name='دولار', line=dict(color='#4CC9F0', width=1.6, dash='dot'),
        hovertemplate="دولار: %{y:,.0f} جنيه<extra></extra>"))
    fig.add_trace(go.Scatter(x=data.index, y=data['Port_Cash'],
        name='كاش', line=dict(color='#1E3A5F', width=1.2, dash='dot'),
        hovertemplate="كاش: %{y:,.0f} جنيه<extra></extra>"))
    if show_events: add_events(fig, data)
    lyt_inv = plot_layout(height=440, yaxis=dict(title_text="القيمة (جنيه)"))
    lyt_inv['title'] = dict(text="نمو محفظة 100,000 جنيه منذ يناير 2020",
        font=dict(size=13, color="#FFD700", family="Cairo"), x=0.5, xanchor='center', y=0.97)
    fig.update_layout(**lyt_inv)
    st.plotly_chart(fig, use_container_width=True, config=dict(displaylogo=False, responsive=True))

    spacer()

    cols = st.columns(3)
    for col, karat in zip(cols, KARAT_FACTORS):
        m = compute_metrics(data, karat)
        tc = '#06D6A0' if m['total']>0 else '#EF476F'
        with col:
            st.markdown(f"""
            <div class="metric-card">
              <div class="metric-card-title" style="color:{KARAT_COLORS[karat]}">{karat} ذهب</div>
              <div class="metric-row"><span class="metric-label">العائد الكلي</span><span class="metric-val" style="color:{tc}">{m['total']:+.1f}%</span></div>
              <div class="metric-row"><span class="metric-label">Sharpe Ratio</span><span class="metric-val" style="color:#4CC9F0">{m['sharpe']:.2f}</span></div>
              <div class="metric-row"><span class="metric-label">Max Drawdown</span><span class="metric-val" style="color:#EF476F">{m['max_dd']:.1f}%</span></div>
              <div class="metric-row"><span class="metric-label">VaR 95% يومي</span><span class="metric-val" style="color:#FF9F43">{m['var95']:.2f}%</span></div>
              <div class="metric-row"><span class="metric-label">العائد السنوي</span><span class="metric-val" style="color:#A855F7">{m['ann_ret']:.1f}%</span></div>
              <div class="metric-row"><span class="metric-label">القيمة النهائية</span><span class="metric-val" style="color:#FFD700">{m['final']:,.0f} ج</span></div>
            </div>""", unsafe_allow_html=True)

    spacer(24)
    section("📉", "Max Drawdown", "")

    st.markdown("""
    <div class="section-sub" style="display:flex;justify-content:space-between;align-items:center;margin-bottom:10px;">
    <div style="direction:rtl">الانخفاض عن القمة - يقيس الخسارة في أسوأ الأوقات</div>
    <div style="direction:ltr">Peak-to-Trough Drawdown %</div>
    </div>
    """, unsafe_allow_html=True)

    fdd = go.Figure()
    for karat, color in KARAT_COLORS.items():
        fc_map = {'24K':'rgba(255,249,196,0.09)','21K':'rgba(255,215,0,0.09)','18K':'rgba(205,127,50,0.09)'}
        fdd.add_trace(go.Scatter(x=data.index, y=data[f'DD_{karat}'],
            name=karat, line=dict(color=color, width=1.8),
            fill='tozeroy', fillcolor=fc_map[karat],
            hovertemplate=f"{karat}: %{{y:.1f}}%<extra></extra>"))
    for date_str, (label, color, fill) in CRISIS_EVENTS.items():
        dt = pd.to_datetime(date_str)
        if dt < data.index[0]: continue
        x1 = (dt + timedelta(days=20)).strftime('%Y-%m-%d')
        fdd.add_vrect(x0=date_str, x1=x1, fillcolor=fill, opacity=1, layer="below", line_width=0)
        fdd.add_annotation(x=date_str, y=0.04, yref="paper", text=label, showarrow=False,
            font=dict(size=8, color=color), textangle=-90, xanchor="left", yanchor="bottom")
    fdd.update_layout(**plot_layout(height=300))
    fdd.update_yaxes(title_text="Drawdown %")
    st.plotly_chart(fdd, use_container_width=True, config=dict(displaylogo=False, responsive=True))

elif page == "📡  المؤشرات التقنية":

    k = selected_karat
    section("📡", f"التحليل التقني - {k}", "")

    st.markdown("""
    <div class="section-sub" style="display:flex;justify-content:space-between;align-items:center;margin-bottom:10px;">

    <div style="direction:rtl">
    إشارات الشراء والبيع الآلية
    </div>
    
    <div style="direction:ltr">
    Bollinger Bands · RSI-14 · MACD
    </div>

    </div>
    """, unsafe_allow_html=True)

    fig = make_subplots(rows=3, cols=1, shared_xaxes=True,
        row_heights=[0.55,0.25,0.20], vertical_spacing=0.07,
        subplot_titles=[f"السعر + Bollinger Bands ({k})", "MACD - زخم الاتجاه", "RSI-14 - مستوى التشبع"])

    fig.add_trace(go.Scatter(x=data.index, y=data[f'BB_up_{k}'],
        line=dict(width=0), showlegend=False), row=1, col=1)
    fig.add_trace(go.Scatter(x=data.index, y=data[f'BB_dn_{k}'],
        fill='tonexty', fillcolor='rgba(180,180,255,0.04)',
        line=dict(width=0), name='Bollinger Bands'), row=1, col=1)
    fig.add_trace(go.Scatter(x=data.index, y=data[f'Price_{k}'],
        name='السعر', line=dict(color='#D8E4F0', width=1.8),
        hovertemplate="%{x|%d %b %Y} - %{y:,.0f} جنيه<extra></extra>"), row=1, col=1)
    fig.add_trace(go.Scatter(x=data.index, y=data[f'SMA50_{k}'],
        name='SMA 50', line=dict(color='#FF9F43', width=1.1, dash='dot')), row=1, col=1)
    fig.add_trace(go.Scatter(x=data.index, y=data[f'SMA200_{k}'],
        name='SMA 200', line=dict(color='#A855F7', width=1.1, dash='dot')), row=1, col=1)
    buys  = data[data[f'Signal_{k}']=='BUY']
    sells = data[data[f'Signal_{k}']=='SELL']
    fig.add_trace(go.Scatter(x=buys.index, y=buys[f'Price_{k}'], mode='markers',
        name='BUY ▲', marker=dict(symbol='triangle-up', color='#06D6A0', size=7,
                                   line=dict(width=1, color='white'))), row=1, col=1)
    fig.add_trace(go.Scatter(x=sells.index, y=sells[f'Price_{k}'], mode='markers',
        name='SELL ▼', marker=dict(symbol='triangle-down', color='#EF476F', size=7,
                                    line=dict(width=1, color='white'))), row=1, col=1)

    hc = ['#06D6A0' if v>=0 else '#EF476F' for v in data[f'MACDHist_{k}']]
    fig.add_trace(go.Bar(x=data.index, y=data[f'MACDHist_{k}'],
        name='Histogram', marker_color=hc, opacity=0.7), row=2, col=1)
    fig.add_trace(go.Scatter(x=data.index, y=data[f'MACD_{k}'],
        name='MACD', line=dict(color='#4CC9F0', width=1.5)), row=2, col=1)
    fig.add_trace(go.Scatter(x=data.index, y=data[f'MACDSig_{k}'],
        name='Signal Line', line=dict(color='#FF9F43', width=1.5)), row=2, col=1)

    fig.add_trace(go.Scatter(x=data.index, y=data[f'RSI_{k}'],
        name='RSI-14', line=dict(color='#A855F7', width=1.7)), row=3, col=1)
    fig.add_hline(y=70, line_dash='dot', line_color='#EF476F', opacity=0.4, row=3, col=1)
    fig.add_hline(y=30, line_dash='dot', line_color='#06D6A0', opacity=0.4, row=3, col=1)
    fig.add_hrect(y0=70, y1=100, fillcolor='rgba(239,71,111,0.04)', line_width=0, row=3, col=1)
    fig.add_hrect(y0=0,  y1=30,  fillcolor='rgba(6,214,160,0.04)',  line_width=0, row=3, col=1)

    if show_events: add_events(fig, data, rows=[1,2,3], y_ann=0.93)

    lyt = plot_layout(height=900)
    lyt['margin'] = dict(l=8, r=8, t=160, b=8)
    lyt['legend'] = dict(orientation="h", y=1.12, x=0.5, xanchor="center",
        bgcolor="rgba(0,0,0,0)", borderwidth=0,
        font=dict(size=9.5, family="Cairo"), itemsizing="constant", tracegroupgap=3)
    lyt['xaxis']['rangeselector']['y'] = 1.06
    fig.update_layout(**lyt)
    fig.update_xaxes(tickfont=dict(family="Cairo", size=10, color="#3A4A65"),gridcolor="rgba(255, 255, 255, 0.05)",range=["2020-01-01", data.index.max()])
    event_labels = {v[0] for v in CRISIS_EVENTS.values()}
    for ann in fig.layout.annotations:
        if ann.text not in event_labels:
            ann.update(x=0.98, xanchor='right',
                       font=dict(color='#FFD700', size=11, family='Cairo'))
    fig.update_yaxes(title_text="السعر (جنيه)", title_font=dict(size=9, color="#3A4A65"), row=1, col=1)
    fig.update_yaxes(title_text="MACD",tickfont=dict(family="Cairo",size=9, color="#3A4A65"),title_font=dict(size=9, color="#3A4A65"), row=2, col=1)
    fig.update_yaxes(title_text="RSI", range=[0, 100],tickfont=dict(family="Cairo",size=9, color="#3A4A65"),
                     title_font=dict(size=9, color="#3A4A65"), row=3, col=1)
    st.plotly_chart(fig, use_container_width=True, config=dict(displaylogo=False, responsive=True))

    spacer()
    sig   = data[f'Signal_{k}'].iloc[-1]
    rsi   = data[f'RSI_{k}'].iloc[-1]
    macd  = data[f'MACD_{k}'].iloc[-1]
    sc    = {'BUY':'sig-buy','SELL':'sig-sell','HOLD':'sig-hold'}.get(sig,'sig-hold')
    sa    = {'BUY':'شراء 📈','SELL':'بيع 📉','HOLD':'انتظار ⏸'}.get(sig,'انتظار')
    bbu   = data[f'BB_up_{k}'].iloc[-1]
    bbl   = data[f'BB_dn_{k}'].iloc[-1]
    lp    = data[f'Price_{k}'].iloc[-1]
    bbp   = "عند الحد الأعلى ⚠️" if lp>bbu*0.98 else "عند الحد الأدنى ✅" if lp<bbl*1.02 else "داخل النطاق"
    insight(f"""
    <div style="display:flex;flex-wrap:wrap;gap:18px;align-items:center;direction:ltr;justify-content:center;font-family:'DM Mono',monospace;font-size:0.82rem;">
      <div><b style="color:#FFD700;font-family:Cairo">الإشارة ({k}):</b>&nbsp;<span class="{sc}">{sa}</span></div>
      <div style="color:#1E3A5F">│</div>
      <div><b style="color:#A855F7">RSI</b>&nbsp;{rsi:.1f}{"&nbsp;<span style='color:#EF476F;font-size:0.72rem'>تشبع شراء</span>" if rsi>70 else "&nbsp;<span style='color:#06D6A0;font-size:0.72rem'>تشبع بيع</span>" if rsi<30 else ""}</div>
      <div style="color:#1E3A5F">│</div>
      <div><b style="color:#4CC9F0">MACD</b>&nbsp;{macd:,.1f}</div>
      <div style="color:#1E3A5F">│</div>
      <div><b style="color:#FF9F43">BB</b>&nbsp;{bbp}</div>
    </div>""")

elif page == "🔮  التوقعات":

    section("🔮", f"توقعات الأسعار - {selected_karat}", "")

    st.markdown("""
    <div class="section-sub" style="display:flex;justify-content:space-between;align-items:center;margin-bottom:10px;">

    <div style="direction:ltr">
    Prophet Model · Regressors: USD + OIL
    </div>

    <div style="direction:rtl">
    نموذج التنبؤ مع متغيرات الدولار والنفط
    </div>

    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="fc-label">أفق التوقع (أيام)</div>', unsafe_allow_html=True)
    forecast_days = st.slider("d", 30, 365, 180, 30, label_visibility="collapsed")

    with st.spinner("⏳ جاري تدريب نموذج Prophet..."):
        try:
            from prophet import Prophet
            k      = selected_karat
            fv_col = f'Price_{k}'
            train  = data.reset_index()[['Date', fv_col, 'USD_EGP_Official', 'Crude_Oil']].copy()
            train.columns = ['ds','y','USD','OIL']

            def fc_reg(col, days):
                df = data.reset_index()[['Date',col]].rename(columns={'Date':'ds',col:'y'})
                mr = Prophet(yearly_seasonality=True, daily_seasonality=False)
                mr.fit(df)
                return mr.predict(mr.make_future_dataframe(periods=days))['yhat'].tail(days).reset_index(drop=True)

            usd_fc = fc_reg('USD_EGP_Official', forecast_days)
            oil_fc = fc_reg('Crude_Oil', forecast_days)
            pm = Prophet(daily_seasonality=True, yearly_seasonality=True)
            pm.add_regressor('USD'); pm.add_regressor('OIL')
            pm.fit(train)
            future = pm.make_future_dataframe(periods=forecast_days)
            future['USD'] = pd.concat([data['USD_EGP_Official'].reset_index(drop=True), usd_fc], ignore_index=True).iloc[:len(future)].values
            future['OIL'] = pd.concat([data['Crude_Oil'].reset_index(drop=True), oil_fc], ignore_index=True).iloc[:len(future)].values
            future.ffill(inplace=True)
            fc     = pm.predict(future)
            fc_out = fc.tail(forecast_days)
            n      = len(data)
            mae    = abs(train['y'].values - fc.iloc[:n]['yhat'].values).mean()
            rmse   = np.sqrt(((train['y'].values - fc.iloc[:n]['yhat'].values)**2).mean())

            title_chart = f"توقعات ذهب \u2066{k}\u2069 - {forecast_days} يوم قادماً"
            fig = go.Figure()
            hw = data[fv_col].resample('W').last()
            fig.add_trace(go.Scatter(x=hw.index, y=hw, name='السعر الفعلي',
                line=dict(color='#4A6A8A', width=1.5),
                hovertemplate="%{x|%d %b %Y}<br>%{y:,.0f} جنيه<extra></extra>"))
            fig.add_trace(go.Scatter(x=fc_out['ds'], y=fc_out['yhat_upper'],
                line=dict(width=0), showlegend=False))
            fig.add_trace(go.Scatter(x=fc_out['ds'], y=fc_out['yhat_lower'],
                fill='tonexty', fillcolor='rgba(76,201,240,0.10)',
                line=dict(width=0), name='نطاق الثقة 95%'))
            fig.add_trace(go.Scatter(x=fc_out['ds'], y=fc_out['yhat'],
                name='توقع Prophet', line=dict(color='#4CC9F0', width=2.5),
                hovertemplate="%{x|%d %b %Y}<br><b>%{y:,.0f} جنيه</b><extra></extra>"))
            fig.add_vline(x=datetime.today().timestamp()*1000, line_dash='dash',
                line_color='#FFD700', opacity=0.5,
                annotation_text='اليوم', annotation_font=dict(color='#FFD700', size=9.5),
                annotation_position="top right")
            if show_events: add_events(fig, data)
            lyt_fc = plot_layout(height=500, yaxis=dict(title_text="السعر (جنيه)"))
            lyt_fc['title'] = dict(text=title_chart,
                font=dict(size=13, color="#FFD700", family="Cairo"), x=0.5, xanchor='center', y=0.97)
            fig.update_layout(**lyt_fc)
            st.plotly_chart(fig, use_container_width=True, config=dict(displaylogo=False, responsive=True))

            spacer()
            la  = data[fv_col].iloc[-1]
            fe  = fc_out['yhat'].iloc[-1]
            cp  = (fe/la-1)*100
            cc  = '#06D6A0' if cp>=0 else '#EF476F'
            cards_html = (
                kpi_html(f"{la:,.0f}", "السعر الحالي (جنيه)", "#FFD700", "0.05s") +
                kpi_html(f"{fe:,.0f}", f"التوقع ({forecast_days}ي)", "#4CC9F0", "0.10s") +
                kpi_html(f"{cp:+.1f}%", "التغيير المتوقع", cc, "0.15s") +
                kpi_html(f"{rmse:,.0f}", "RMSE النموذج", "#A855F7", "0.20s")
            )
            st.markdown(f'<div class="kpi-grid" style="grid-template-columns:repeat(4,1fr)">{cards_html}</div>',
                        unsafe_allow_html=True)

            spacer()
            insight(f"""
            🤖 <b>ملخص التوقع:</b> يتوقع نموذج Prophet أن يصل سعر جرام {k} إلى
            <span class="{'num' if cp>=0 else 'num-red'}">{fe:,.0f} جنيه</span>
            خلال {forecast_days} يوم القادمة - تغيير
            <span class="{'num' if cp>=0 else 'num-red'}">{cp:+.1f}%</span>
            عن السعر الحالي.<br>
            <span style="direction:rtl; display:block; margin-top:6px;">
            دقة النموذج -
            <span style="font-family:'DM Mono',monospace; direction:ltr; display:inline-block; unicode-bidi:embed;">MAE = {mae:,.0f} جنيه</span>
            &nbsp;|&nbsp;
            <span style="font-family:'DM Mono',monospace; direction:ltr; display:inline-block; unicode-bidi:embed;">RMSE = {rmse:,.0f} جنيه</span>
            &nbsp;- كلما قل الرقم كلما كان النموذج أدق.
            </span>
            """)

        except ImportError:
            st.error("⚠️ مكتبة Prophet غير مثبتة - pip install prophet")
        except Exception as e:
            st.error(f"خطأ: {e}")

st.markdown('</div>', unsafe_allow_html=True)