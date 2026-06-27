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
from PIL import Image
import base64
def get_img_as_base64(file_path):
    try:
        with open(file_path, "rb") as f:
            data = f.read()
        return base64.b64encode(data).decode()
    except Exception:
        return ""
base_path = os.path.dirname(os.path.abspath(__file__))
image_path = os.path.join(base_path, "logo.png")
icon_img = Image.open(image_path)
img_base64 = get_img_as_base64(image_path) 
IMAGE_HTML_SRC = f"data:image/png;base64,{img_base64}"

# ─────────────────────────────────────────────────────────────────────────────
# PATHS & CONSTANTS
# ─────────────────────────────────────────────────────────────────────────────
CSV_PATH           = os.path.abspath(os.path.join(base_path, "..", "02_Dataset", "Gold_Egypt.csv"))
CSV_PROCESSED_PATH = os.path.abspath(os.path.join(base_path, "..", "02_Dataset", "Gold_Egypt_Processed.csv"))

_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/122.0.0.0 Safari/537.36",
    "Accept-Language": "ar,en;q=0.9",
}

OUNCE_TO_GRAM   = 31.1035
KARAT_FACTORS   = {'24K': 1.000, '21K': 0.875, '18K': 0.750}
KARAT_COLORS    = {'24K': '#FFF9C4', '21K': '#FFD700', '18K': '#CD7F32'}

# Making charges per gram in EGP (fabrication/workmanship fee)
MAKING_CHARGES  = {'24K': 60, '21K': 150, '18K': 220}
# Bid-ask spread applied at liquidation
SELL_SPREAD     = {'24K': 0.005, '21K': 0.010, '18K': 0.015}

# Baseline EGP/USD used for the value-driven component (pre-devaluation anchor: Jan 2020 ~15.7)
VALUE_BASELINE_USD_EGP = 15.70

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

# ─────────────────────────────────────────────────────────────────────────────
# TASK 1 - SAFE AUTO-REFRESH (every 5 minutes during market hours UTC 13–21)
# Falls back silently if streamlit-autorefresh is not installed. A 300-second
# interval prevents aggressive polling that could trigger IP blocks or API
# rate limits on gold/FX data providers.
# ─────────────────────────────────────────────────────────────────────────────
try:
    from streamlit_autorefresh import st_autorefresh
    st_autorefresh(interval=300_000, key="market_refresh")   
except ImportError:
    pass   # streamlit-autorefresh not installed - app continues without auto-refresh

# ─────────────────────────────────────────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="GOLD EGYPT · ذهب مصر",
    page_icon=icon_img,
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────────────────────────────────────
# PREMIUM CSS - CYBERPUNK / LUXURY DARK THEME
# ─────────────────────────────────────────────────────────────────────────────
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

/* ── Keyframes ── */
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
@keyframes blink {
  0%, 100% { opacity: 1; }
  50%       { opacity: 0.3; }
}

/* ── Main container ── */
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

[data-testid="stSidebar"] .stSelectbox label,
[data-testid="stSidebar"] .stToggle label {
  direction: rtl !important; text-align: right !important;
  width: 100%; color: var(--text-muted) !important; font-size: 0.8rem !important;
}

/* ── HERO BANNER ── */
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

/* ── KPI CARDS ── */
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

/* ── ROI CALCULATOR CARD ── */
.roi-card {
  background: linear-gradient(145deg, #080F1F, #0C1A30);
  border: 1px solid var(--border-glow);
  border-radius: var(--radius);
  padding: 24px 20px;
  margin-top: 8px;
}
.roi-card-title {
  font-size: 0.88rem; font-weight: 700; color: var(--gold);
  text-align: right; direction: rtl; margin-bottom: 16px;
  letter-spacing: 0.3px;
}

/* ── PAGE TRANSITION ── */
.page-content { animation: pageIn 0.4s cubic-bezier(0.4,0,0.2,1) both; }

/* ── Streamlit slider - TradingView style ── */
[data-testid="stSlider"] > div > div > div {
  background: linear-gradient(90deg, #ff4d4d 0%, #ff7a7a 25%, #ffb347 60%, var(--gold) 100%) !important;
  height: 4px !important;
  border-radius: 10px !important;
}
[data-testid="stSlider"] [role="slider"] {
  background: var(--gold) !important;
  border: 2px solid #fff !important;
  width: 14px !important; height: 14px !important;
  border-radius: 50% !important;
  box-shadow: 0 0 6px rgba(255,215,0,0.8), 0 0 14px rgba(255,215,0,0.35);
}
[data-baseweb="slider"] [role="tooltip"] {
  background: transparent !important; color: var(--gold) !important;
  border: none !important; box-shadow: none !important;
  font-weight: 600; padding: 0 !important;
}
[data-baseweb="slider"] [role="tooltip"]::before,
[data-baseweb="slider"] [role="tooltip"]::after { display: none !important; }
[data-testid="stSlider"] [role="slider"]:hover { transform: scale(1.2); }

/* ── Streamlit toggle ── */
[data-testid="stToggle"] input:checked + div { background-color: var(--gold-dim) !important; }

/* ── st.metric styling override for ROI cards ── */
[data-testid="stMetric"] {
  background: linear-gradient(145deg, var(--bg-card), var(--bg-card2));
  border: 1px solid var(--border);
  border-radius: var(--radius);
  padding: 16px 18px !important;
  transition: border-color var(--transition);
}
[data-testid="stMetric"]:hover { border-color: rgba(255,215,0,0.25); }
[data-testid="stMetricLabel"] { font-size: 0.72rem !important; color: var(--text-faint) !important; direction: rtl; }
[data-testid="stMetricValue"] { font-family: 'Bebas Neue', 'DM Mono', monospace !important; font-size: 1.6rem !important; }
[data-testid="stMetricDelta"] { font-family: 'DM Mono', monospace !important; font-size: 0.8rem !important; }

/* ── Mobile responsive ── */
@media (max-width: 768px) {
  .main .block-container { padding: 0 0.4rem 0.5rem !important; }
  .hero-wrap { padding: 16px 14px; margin-bottom: 16px; }
  .hero-title { font-size: 1.25rem; }
  .kpi-grid { grid-template-columns: repeat(2, 1fr); gap: 8px; }
  .kpi-value { font-size: 1.35rem; }
  .kpi-card { padding: 14px 10px; }
  .insight-box { font-size: 0.78rem; padding: 11px 14px 11px 10px; }
}
@media (max-width: 480px) {
  .kpi-grid { grid-template-columns: repeat(2, 1fr); gap: 6px; }
  .hero-title { font-size: 1.05rem; line-height: 1.25; }
}

/* ── Hide clutter ── */
#MainMenu, footer, .stDeployButton { display: none !important; }
header { visibility: visible !important; background: transparent !important; }
[data-testid="collapsedControl"] {
  visibility: visible !important; background: #07101F !important;
  border-right: 1px solid rgba(255,215,0,0.15) !important;
}
[data-testid="collapsedControl"] svg { fill: var(--gold) !important; }

/* ── Scrollbar ── */
::-webkit-scrollbar { width: 4px; }
::-webkit-scrollbar-track { background: var(--bg-void); }
::-webkit-scrollbar-thumb { background: #1E3A5F; border-radius: 4px; }
::-webkit-scrollbar-thumb:hover { background: var(--gold-dim); }

/* ── Chart glass wrapper ── */
.stPlotlyChart {
  background: linear-gradient(145deg, rgba(10,21,37,0.7), rgba(13,30,54,0.5));
  border: 1px solid var(--border);
  border-radius: var(--radius);
  padding: 4px;
  box-shadow: 0 4px 40px rgba(0,0,0,0.4);
  margin-bottom: 4px;
}

/* ── Remove top gap ── */
.stApp > header + div { margin-top: 0 !important; }
div[data-testid="stAppViewContainer"] > section > div:first-child { padding-top: 0 !important; }
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# DATA SCRAPING & ENGINEERING
# ─────────────────────────────────────────────────────────────────────────────

def _scrape_gold_usd():
    """Fetch live gold spot price (USD/oz) from goldprice.org data feed."""
    try:
        r = requests.get("https://data-asg.goldprice.org/dbXRates/USD",
                         headers=_HEADERS, timeout=10)
        return float(r.json()["items"][0]["xauPrice"])
    except Exception:
        return None

def _scrape_gold_usd_yf():
    """Fallback: fetch gold spot price from Yahoo Finance (GC=F futures)."""
    try:
        df = yf.download("GC=F", period="5d", progress=False, auto_adjust=False)
        if df.empty: return None
        if isinstance(df.columns, pd.MultiIndex): df.columns = df.columns.droplevel(1)
        col = "Adj Close" if "Adj Close" in df.columns else "Close"
        return float(df[col].dropna().iloc[-1])
    except Exception:
        return None

def _scrape_usd_egp():
    """Fetch USD/EGP exchange rate from exchangerate-api (primary)."""
    try:
        r = requests.get("https://api.exchangerate-api.com/v4/latest/USD",
                         headers=_HEADERS, timeout=10)
        return float(r.json()["rates"]["EGP"])
    except Exception:
        return None

def _scrape_usd_egp_backup():
    """Fallback: fetch USD/EGP from frankfurter.app."""
    try:
        r = requests.get("https://api.frankfurter.app/latest?from=USD&to=EGP",
                         headers=_HEADERS, timeout=10)
        return float(r.json()["rates"]["EGP"])
    except Exception:
        return None

def _scrape_usd_egp_yf():
    """Second fallback: fetch USD/EGP from Yahoo Finance (EGP=X ticker)."""
    try:
        df = yf.download("EGP=X", period="5d", progress=False, auto_adjust=False)
        if df.empty: return None
        if isinstance(df.columns, pd.MultiIndex): df.columns = df.columns.droplevel(1)
        col = "Adj Close" if "Adj Close" in df.columns else "Close"
        return float(df[col].dropna().iloc[-1])
    except Exception:
        return None

def _scrape_others():
    """Fetch auxiliary market data: crude oil, 10Y treasury, and S&P 500."""
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
    """
    Pull historical OHLC data from Yahoo Finance for all required tickers.
    Returns a forward-filled, aligned DataFrame indexed by date.
    """
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
    """Fetch live data, append to historical CSV, handle overlapping dates."""
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
        # Remove any existing row for today before appending to avoid duplicates
        hist = hist[hist.index.date != today.date()]
        hist = pd.concat([hist, today_df], sort=False)

    hist.ffill(inplace=True)
    hist.dropna(how="all", inplace=True)
    hist.sort_index(inplace=True)
    hist.index.name = "Date"
    hist.to_csv(CSV_PATH)
    return True


# ─────────────────────────────────────────────────────────────────────────────
# PLOTLY LAYOUT HELPERS
# ─────────────────────────────────────────────────────────────────────────────

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
    d = dict(orientation="h", y=1.10, yanchor="top", x=0.5, xanchor="center",
             bgcolor="rgba(0,0,0,0)", borderwidth=0,
             font=dict(size=10, family="Cairo"), itemsizing="constant")
    d.update(kw)
    return d

def _xax(**kw):
    d = dict(showgrid=True, gridcolor="rgba(19,34,56,0.8)", gridwidth=1,
             showline=True, linecolor="#132238", zeroline=False,
             rangeslider=dict(visible=False),
             rangeselector=dict(
                 x=0, xanchor="left", y=1.10, yanchor="top",
                 bgcolor="#0A1525", bordercolor="#132238", borderwidth=1,
                 activecolor="#1E3A5F", font=dict(size=9.5, color="#8D99AE"),
                 buttons=[
                     dict(count=3,  label="3M",  step="month", stepmode="backward"),
                     dict(count=6,  label="6M",  step="month", stepmode="backward"),
                     dict(count=1,  label="1Y",  step="year",  stepmode="backward"),
                     dict(count=2,  label="2Y",  step="year",  stepmode="backward"),
                     dict(label="الكل", step="all"),
                 ]),
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
        lyt['title'] = dict(text=title_text,
            font=dict(size=13, color="#FFD700", family="Cairo"),
            x=0.5, xanchor="center", y=0.96, yanchor="top")
    for k, v in extra.items():
        if k in ('xaxis', 'yaxis', 'legend') and isinstance(v, dict):
            lyt[k].update(v)
        else:
            lyt[k] = v
    return lyt


# ─────────────────────────────────────────────────────────────────────────────
# DATA LOADING & FEATURE ENGINEERING
# ─────────────────────────────────────────────────────────────────────────────

@st.cache_data(ttl=60, show_spinner=False)
def load_data(csv_path: str, mtime: float) -> pd.DataFrame:
    data = pd.read_csv(csv_path, index_col="Date", parse_dates=True)
    data.ffill(inplace=True)
    data.dropna(inplace=True)

    # Core spot price: convert global gold (USD/oz) to EGP/gram using live FX rate
    data['Theoretical_24K'] = (data['Gold_USD_Ounce'] / OUNCE_TO_GRAM) * data['USD_EGP_Official']

    for karat, factor in KARAT_FACTORS.items():
        # p = pure spot price (USD/oz → EGP/gram at live FX, no retail fees)
        # Used for all technical indicators & value decomposition to avoid distorting signals
        p = data['Theoretical_24K'] * factor

        # Price_{karat} = retail BUY price a customer actually pays in the Egyptian market
        # = spot price + making charge (fabrication/workmanship fee per gram)
        # For 24K: Price_24K > Theoretical_24K by exactly MAKING_CHARGES['24K'] = 60 EGP
        data[f'Price_{karat}'] = p + MAKING_CHARGES[karat]

        # Value-driven component: gram price at a stable pre-devaluation EGP/USD rate
        # (VALUE_BASELINE_USD_EGP = 15.70, Jan 2020 anchor - reflects intrinsic gold value)
        data[f'ValueDriven_{karat}'] = (data['Gold_USD_Ounce'] / OUNCE_TO_GRAM) * factor * VALUE_BASELINE_USD_EGP
        # Inflation & currency premium: residual reflecting local EGP weakness relative to baseline
        data[f'InflPrem_{karat}']    = p - data[f'ValueDriven_{karat}']
        data[f'PremPct_{karat}']     = (data[f'InflPrem_{karat}'] / p) * 100

        # ── Technical indicators ──
        data[f'SMA50_{karat}']       = p.rolling(50,  min_periods=1).mean()
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

        # ── Automated trading signals ──
        buy  = (data[f'RSI_{karat}'] < 30) | (
                    (data[f'MACD_{karat}'] > data[f'MACDSig_{karat}']) &
                    (data[f'MACD_{karat}'].shift(1) <= data[f'MACDSig_{karat}'].shift(1)))
        sell = (data[f'RSI_{karat}'] > 70) | (
                    (data[f'MACD_{karat}'] < data[f'MACDSig_{karat}']) &
                    (data[f'MACD_{karat}'].shift(1) >= data[f'MACDSig_{karat}'].shift(1)))
        data[f'Signal_{karat}'] = np.select([buy, sell], ['BUY', 'SELL'], default='HOLD')

        # ── Realistic portfolio simulation ──
        # Entry cost: Price_{karat} already includes making charge (fabrication fee)
        entry_price  = data[f'Price_{karat}'].iloc[0]
        grams_bought = 100_000 / entry_price
        # Net liquidation value: sell at spot price less bid-ask spread (no making charge on exit)
        net_series   = (p * grams_bought) * (1 - SELL_SPREAD[karat])
        data[f'Port_{karat}'] = net_series
        rm = data[f'Port_{karat}'].cummax()
        data[f'DD_{karat}']   = (data[f'Port_{karat}'] / rm - 1) * 100
        data[f'Norm_{karat}'] = data[f'Port_{karat}'] / 100_000 * 100

    # ── USD and Cash benchmarks ──
    usd0 = data['USD_EGP_Official'].iloc[0]
    data['Port_USD']  = (100_000 / usd0) * data['USD_EGP_Official']
    data['Port_Cash'] = 100_000.0
    data['Norm_USD']  = data['Port_USD']  / 100_000 * 100
    data['Norm_Cash'] = 100.0
    return data


def add_events(fig, data, rows=None, y_ann=0.98):
    """Add crisis event vertical bands and annotations to a Plotly figure."""
    for date_str, (label, color, fill) in sorted(CRISIS_EVENTS.items()):
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
            line=dict(color=color, width=0.8, dash="dot"), opacity=0.55)
        fig.add_annotation(
            x=date_str, y=y_ann, yref="paper", xref="x",
            text=label, showarrow=False,
            font=dict(size=7.5, color=color, family="Cairo"),
            textangle=-90, xanchor="left", yanchor="top",
            bgcolor="rgba(3,6,15,0.55)", borderpad=2)


# ─────────────────────────────────────────────────────────────────────────────
# UI HELPERS
# ─────────────────────────────────────────────────────────────────────────────

def section(icon, title, sub=""):
    import re
    safe_title = re.sub(r'(\d+K)', r'<bdi>\1</bdi>', title)
    if isinstance(sub, list):
        sub_html = "".join(
            f'<div style="direction:{d};text-align:{"right" if d=="rtl" else "left"};'
            f'font-size:0.76rem;color:var(--text-faint);margin:0 0 2px 0;">{t}</div>'
            for t, d in sub)
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
    """Compute investment performance metrics using net (realistic) portfolio values."""
    col = f'Port_{karat}'
    ret    = data[col].pct_change().dropna()
    total  = (data[col].iloc[-1] / 100_000 - 1) * 100
    ann_r  = ret.mean() * 252
    ann_v  = ret.std()  * np.sqrt(252)
    sharpe = ann_r / ann_v if ann_v else 0
    max_dd = data[f'DD_{karat}'].min()
    var95  = ret.quantile(0.05) * 100
    return dict(total=total, sharpe=sharpe, max_dd=max_dd, var95=var95,
                final=data[col].iloc[-1], ann_ret=ann_r * 100, ann_vol=ann_v * 100)


# ─────────────────────────────────────────────────────────────────────────────
# BOOT: auto-scrape if CSV is missing or stale (> 6 hours old)
# ─────────────────────────────────────────────────────────────────────────────

_need_scrape = False
if not os.path.exists(CSV_PATH):
    _need_scrape = True
else:
    _age_minutes = (time.time() - os.path.getmtime(CSV_PATH)) / 60
    if _age_minutes >= 5:
        _need_scrape = True

if _need_scrape:
    with st.spinner("‫⏳ جاري جلب بيانات الذهب... (مرة واحدة فقط)‬"):
        run_scraper()
        st.cache_data.clear()

# ─────────────────────────────────────────────────────────────────────────────
# SIDEBAR - NAVIGATION & CONTROLS
# ─────────────────────────────────────────────────────────────────────────────

with st.sidebar:
    st.markdown(f"""
    <div class="sb-logo">
      <div class="sb-logo-icon"><img src="{IMAGE_HTML_SRC}" width="80" style="border-radius:8px;"></div>
      <div class="sb-logo-text">GOLD EGYPT</div>
      <div class="sb-logo-sub">أداة التحليل المالي · منذ 2020</div>
    </div>""", unsafe_allow_html=True)

    pages = {
        "home":       "🏠  الرئيسية",
        "analysis":   "📊  تحليل الأسعار",
        "investment": "💼  محاكاة الاستثمار",
        "technical":  "📡  المؤشرات التقنية",
        "forecast":   "🔮  التوقعات",
    }
    query         = st.query_params
    default_key   = query.get("page", "home")
    if default_key not in pages:
        default_key = "home"
    page_labels   = list(pages.values())
    page_keys     = list(pages.keys())
    default_index = page_keys.index(default_key)
    page_label    = st.radio("", page_labels, index=default_index, label_visibility="collapsed")
    selected_key  = page_keys[page_labels.index(page_label)]
    st.query_params["page"] = selected_key
    page = page_label

    st.markdown('<div class="gold-divider"></div>', unsafe_allow_html=True)

    st.markdown('<div style="color:#8D99AE;font-size:0.78rem;direction:rtl;text-align:right;margin-bottom:4px;">العيار الرئيسي</div>', unsafe_allow_html=True)
    selected_karat = st.selectbox("k", ["18K", "21K", "24K"], index=1, label_visibility="collapsed")

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
        with st.spinner("‫⏳ جاري التحديث...‬"):
            run_scraper()
        st.cache_data.clear()
        st.rerun()

    if os.path.exists(CSV_PATH):
        import pytz

        ts = os.path.getmtime(CSV_PATH)
        _mt = datetime.utcfromtimestamp(ts).replace(tzinfo=pytz.utc).astimezone(
            pytz.timezone("Africa/Cairo")
        ).strftime("%Y-%m-%d %H:%M")

        _sc  = "#06D6A0"
        _stx = f"‫✅ آخر تحديث:‬<br>{_mt}"

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
    </div>
    <div style="height:14px"></div>
    <div style="background:linear-gradient(135deg,rgba(255,215,0,0.06),rgba(76,201,240,0.04));
                border:1px solid rgba(255,215,0,0.15);border-radius:10px;padding:12px 14px;">
      <div style="color:var(--gold);font-size:0.64rem;font-weight:700;text-align:center;
                  letter-spacing:1px;margin-bottom:6px;">DATA ANALYST</div>
      <div style="color:#E8EDF5;font-size:0.72rem;font-weight:700;text-align:center;
                  font-family:'Cairo',sans-serif;margin-bottom:3px;">محمود شمعون</div>
      <div style="color:#8D99AE;font-size:0.6rem;text-align:center;
                  font-family:'DM Mono',monospace;direction:ltr;">Mahmoud Shamoun</div>
      <div style="color:#3A4A65;font-size:0.58rem;text-align:center;margin-top:4px;
                  direction:rtl;line-height:1.7;">
        محلل بيانات متخصص<br>مشروع تخرج · DEPI
      </div>
    </div>""", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# LOAD DATA
# ─────────────────────────────────────────────────────────────────────────────

if not os.path.exists(CSV_PATH):
    st.error("❌ فشل تحميل البيانات - تحقق من الاتصال بالإنترنت")
    st.stop()

_mtime_key = os.path.getmtime(CSV_PATH)
with st.spinner(""):
    data = load_data(CSV_PATH, _mtime_key)

if data.empty:
    st.error("❌ فشل قراءة البيانات"); st.stop()

# Export the fully processed DataFrame (all engineered columns) to CSV.
# Includes fair values, technical indicators, signals, and portfolio metrics
# for all three karats. Non-fatal: UI continues even if export fails.
try:
    data.to_csv(CSV_PROCESSED_PATH, index=True, index_label="Date")
except Exception:
    pass

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
# ─────────────────────────────────────────────────────────────────────────────
# PREMIUM EMBED ROUTER (For Vercel HTML Slides Integration)
# ─────────────────────────────────────────────────────────────────────────────
embed_q = st.query_params.get("q")
if embed_q:
    # إخفاء عناصر التحكم كلياً لضمان تجربة SaaS انسيابية داخل الـ Iframe
    st.markdown("""
    <style>
        [data-testid="stSidebar"], header, footer, .stDeployButton {display: none !important;}
        .main .block-container {padding: 0 !important; max-width: 100% !important; margin: 0 !important;}
        .stPlotlyChart {border: none !important; box-shadow: none !important; background: transparent !important;}
        body {background-color: transparent !important;}
    </style>
    """, unsafe_allow_html=True)

    k = selected_karat

    # Q1: تفكيك السعر (Price Decomposition)
    if embed_q == "q1":
        fig = make_subplots(rows=1, cols=1)
        fig.add_trace(go.Scatter(x=data.index, y=data[f'ValueDriven_{k}'], name='قيمة عالمية عادلة', fill='tozeroy', line=dict(color='#FFF9C4')))
        fig.add_trace(go.Scatter(x=data.index, y=data[f'InflPrem_{k}'], name='علاوة تضخم وتحوط', fill='tonexty', line=dict(color='#EF476F')))
        fig.update_layout(**plot_layout(height=460))
        st.plotly_chart(fig, use_container_width=True)

    # Q2: فجوة السعر العادل (Fair Value Gap)
    elif embed_q == "q2":
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=data.index, y=data[f'Price_{k}'], name='السعر الفعلي بمصر', line=dict(color='#FFD700', width=2)))
        fig.add_trace(go.Scatter(x=data.index, y=data[f'ValueDriven_{k}'], name='السعر العادل نظرياً', line=dict(color='#06D6A0', dash='dash')))
        fig.update_layout(**plot_layout(height=460))
        st.plotly_chart(fig, use_container_width=True)

    # Q3: نسبة النوازل والعلاوة التاريخية (Premium % Timeline)
    elif embed_q == "q3":
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=data.index, y=data[f'PremPct_{k}'], name=f'علاوة عيار {k}', line=dict(color='#FFD700')))
        fig.update_layout(**plot_layout(height=460, yaxis=dict(title_text="نسبة العلاوة %")))
        st.plotly_chart(fig, use_container_width=True)

    # Q4: مصفوفة الارتباط العالمي (Global Correlation Matrix)
    elif embed_q == "q4":
        cols_ = ['Gold_USD_Ounce', 'USD_EGP_Official', 'Crude_Oil', 'US_10Y_Treasury', 'SP500']
        names_ = ['ذهب عالمي', 'دولار رسمي', 'نفط برنت', 'سندات أمريكا', 'S&P 500']
        valid_cols = [c for c in cols_ if c in data.columns]
        valid_names = [names_[cols_.index(c)] for c in valid_cols]
        if valid_cols:
            cd = data[valid_cols].dropna().corr()
            cd.columns = valid_names; cd.index = valid_names
            fig = px.imshow(cd, text_auto=".2f", color_continuous_scale=[[0,'#EF476F'],[0.5,'#060C18'],[1,'#06D6A0']], zmin=-1, zmax=1)
            fig.update_layout(**plot_layout(height=460))
            st.plotly_chart(fig, use_container_width=True)

    # Q5: محاكاة المحفظة الاستثمارية (Portfolio Net Returns)
    elif embed_q == "q5":
        fig = go.Figure()
        for karat, color in KARAT_COLORS.items():
            if f'Port_{karat}' in data.columns:
                fig.add_trace(go.Scatter(x=data.index, y=data[f'Port_{karat}'], name=f'صافي عائد {karat}', line=dict(color=color)))
        if 'Port_USD' in data.columns:
            fig.add_trace(go.Scatter(x=data.index, y=data['Port_USD'], name='استثمار الدولار', line=dict(color='#4CC9F0', dash='dot')))
        fig.update_layout(**plot_layout(height=460))
        st.plotly_chart(fig, use_container_width=True)

    # Q6: التنبؤ المستقبلي (Prophet Forecasting Time Series)
    elif embed_q == "q6":
        fig = go.Figure()
        # عرض البيانات التاريخية الفعلية مع خط التنبؤ المستقبلي الممتد
        fig.add_trace(go.Scatter(x=data.index, y=data[f'Price_{k}'], name='السعر التاريخي', line=dict(color='#FFD700')))
        if 'Forecast_Upper' in data.columns and 'Forecast_Lower' in data.columns:
            fig.add_trace(go.Scatter(x=data.index, y=data['Forecast_Upper'], name='الحد الأعلى المتوقع', line=dict(color='rgba(239,71,111,0.2)', width=0)))
            fig.add_trace(go.Scatter(x=data.index, y=data['Forecast_Lower'], name='الحد الأدنى المتوقع', fill='tonexty', line=dict(color='rgba(239,71,111,0.2)', width=0)))
        fig.update_layout(**plot_layout(height=460))
        st.plotly_chart(fig, use_container_width=True)

    # Q7: المؤشرات الفنية للزخم (Technical Indicators: RSI & MACD)
    elif embed_q == "q7":
        fig = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.06, row_heights=[0.5, 0.5])
        if f'RSI_{k}' in data.columns:
            fig.add_trace(go.Scatter(x=data.index, y=data[f'RSI_{k}'], name='RSI (مؤشر القوة النسبية)', line=dict(color='#E63946')), row=1, col=1)
        if f'MACD_{k}' in data.columns and f'Signal_{k}' in data.columns:
            fig.add_trace(go.Scatter(x=data.index, y=data[f'MACD_{k}'], name='MACD Line', line=dict(color='#4CC9F0')), row=2, col=1)
            fig.add_trace(go.Scatter(x=data.index, y=data[f'Signal_{k}'], name='Signal Line', line=dict(color='#FFD700')), row=2, col=1)
        fig.update_layout(**plot_layout(height=460))
        st.plotly_chart(fig, use_container_width=True)

    # إيقاف التنفيذ الفوري بعد رسم الشارت المطلوبة لمنع تحميل بقية الـ DOM
    st.stop()

# ═════════════════════════════════════════════════════════════════════════════
# PAGE 1: Home - Executive Summary & Live Stream
# ═════════════════════════════════════════════════════════════════════════════

if page == "🏠  الرئيسية":

    m = compute_metrics(data, selected_karat)

    st.markdown(f"""
    <div class="hero-wrap">
      <div class="hero-eyebrow">GOLD EGYPT · FINANCIAL INTELLIGENCE PLATFORM</div>
      <div class="hero-title">
        <img src="{IMAGE_HTML_SRC}" width="40" style="vertical-align: middle; margin-left: 10px; position: relative; top: -5px;"> الذهب كأداة مالية في مصر
      </div>
      <div class="hero-sub">
        تحليل شامل لأداء الذهب بالعيارات
        <span style="font-family:'DM Mono',monospace; direction:ltr; display:inline;"> 18K · 21K · 24K </span>
        كأداة للحفاظ على القيمة في مواجهة التضخم وانخفاض الجنيه - محاكاة واقعية تشمل المصنعية وفرق أسعار البيع
      </div>
      <div class="hero-date">
        <span class="dot"></span>
        LIVE · Jan 2020 - {last_date_f}
      </div>
      <div class="hero-badges">
        <span class="hero-badge">DEPI 2026</span>
        <span class="hero-badge">منحة رواد مصر الرقمية</span>
        <span class="hero-badge">Mahmoud Shamoun</span>
      </div>
    </div>""", unsafe_allow_html=True)

    clr = '#06D6A0' if m['total'] > 0 else '#EF476F'
    cards_html = (
        kpi_html(f"{last_price:,.0f}",    f"جنيه/جرام {selected_karat}",         "#FFD700", "0.05s") +
        kpi_html(f"{last_usd:.2f}",        "جنيه / دولار",                         "#4CC9F0", "0.10s") +
        kpi_html(f"${last_gold:,.0f}",     "أونصة عالمياً",                        "#06D6A0", "0.15s") +
        kpi_html(f"{m['total']:+.0f}%",    f"عائد الذهب {selected_karat} من 2020", clr,       "0.20s") +
        kpi_html(f"{m['sharpe']:.2f}",     "Sharpe Ratio",                         "#A855F7", "0.25s")
    )
    st.markdown(f'<div class="kpi-grid">{cards_html}</div>', unsafe_allow_html=True)

    spacer(24)
    section("📈", "مسار سعر الذهب", "")
    st.markdown(f"""
    <div class="section-sub" style="display:flex;justify-content:space-between;align-items:center;margin-bottom:10px;">
    <div style="direction:rtl">سعر جرام {selected_karat} بالجنيه المصري</div>
    <div style="direction:ltr">Jan 2020 - {last_date_f}</div>
    </div>""", unsafe_allow_html=True)

    pc   = f'Price_{selected_karat}'
    clr  = KARAT_COLORS[selected_karat]
    fill_map = {'24K': 'rgba(255,249,196,0.07)', '21K': 'rgba(255,215,0,0.07)', '18K': 'rgba(205,127,50,0.07)'}
    fig  = go.Figure()
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
    price_chg = (data[pc].iloc[-1] / data[pc].iloc[0] - 1) * 100
    peak_p    = data[pc].max()
    peak_d    = data[pc].idxmax().strftime('%b %Y')
    usd_chg   = (data['USD_EGP_Official'].iloc[-1] / data['USD_EGP_Official'].iloc[0] - 1) * 100
    c1, c2    = st.columns(2)
    with c1:
        insight(f"‫📌 <b>الأداء الإجمالي:</b> ارتفع الذهب {selected_karat} بنسبة <span class='num'>{price_chg:.0f}%</span> منذ يناير 2020، مقارنةً بالدولار الذي ارتفع <span class='num'>{usd_chg:.0f}%</span> فقط خلال نفس الفترة.")
    with c2:
        insight(f"🏔️ <b>القمة التاريخية:</b> <span class='num'>{peak_p:,.0f} جنيه</span> لجرام {selected_karat} في <b>{peak_d}</b> - مدفوعاً بتراجع الجنيه وارتفاع الأسعار العالمية.")

    spacer(24)
    section("🗓️", "أبرز الأحداث المؤثرة على سعر الذهب", "2020 – 2025")
    events_cards = {
        "2020-03-15": ("🦠", "COVID-19",       "مارس 2020",    "انهيار الأسواق العالمية - الذهب يرتفع كملاذ آمن",            "#FF6B6B"),
        "2022-02-24": ("🇺🇦","روسيا-أوكرانيا","فبراير 2022",  "الغزو الروسي وارتفاع الطاقة والذهب عالمياً",                "#FF9F43"),
        "2022-03-21": ("📉", "تعويم 1",         "مارس 2022",    "أول تعويم للجنيه يرفع الذهب المحلي بشكل حاد",              "#EF476F"),
        "2023-10-07": ("⚔️","حرب غزة",          "أكتوبر 2023",  "اندلاع المواجهة يرفع الطلب على الذهب كملاذ",               "#FF6B6B"),
        "2024-03-06": ("🔓","تعويم 2024",        "مارس 2024",    "تعويم شامل للجنيه: الدولار يقفز من 30 إلى 50 جنيهاً",      "#06D6A0"),
        "2024-09-18": ("✂️","خفض الفائدة",       "سبتمبر 2024",  "الفيدرالي يبدأ دورة خفض الفائدة - دعم قوي للذهب",          "#4CC9F0"),
        "2025-01-19": ("🕊️","وقف إطلاق النار",  "يناير 2025",   "اتفاق غزة يُهدئ مؤقتاً - الذهب يتراجع طفيفاً",             "#06D6A0"),
        "2025-04-02": ("🔥","رسوم ترامب",        "أبريل 2025",   "إعلان الرسوم الجمركية الشاملة يدفع الذهب لـ 3500$",         "#FF9F43"),
        "2025-04-22": ("🏆","قياسي 3500$",        "أبريل 2025",   "الذهب يكسر 3500$ لأول مرة في التاريخ",                     "#FFD700"),
        "2025-06-13": ("💥","ضربة إيران",         "يونيو 2025",   "الضربة الإسرائيلية-الأمريكية على إيران ترفع الذهب فوراً", "#EF476F"),
    }
    cols_ev = st.columns(3)
    for idx, (date_str, (icon, title_ev, date_lbl, desc, color)) in enumerate(events_cards.items()):
        with cols_ev[idx % 3]:
            st.markdown(f"""
            <div style="background:linear-gradient(145deg,#0A1525,#0D1E36);
                        border:1px solid #132238;border-radius:12px;padding:14px;
                        margin-bottom:10px;border-top:2px solid {color};">
              <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:6px;">
                <span style="font-size:1.3rem">{icon}</span>
                <span style="font-family:'DM Mono',monospace;font-size:0.6rem;color:#3A4A65">{date_lbl}</span>
              </div>
              <div style="color:{color};font-weight:700;font-size:0.82rem;direction:rtl;margin-bottom:4px">{title_ev}</div>
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
        </div>""", unsafe_allow_html=True)
        cols_  = ['Gold_USD_Ounce', 'USD_EGP_Official', 'Crude_Oil', 'US_10Y_Treasury', 'SP500']
        names_ = ['ذهب عالمي', 'دولار/جنيه', 'نفط', 'سندات أمريكية', 'S&P 500']
        cd     = data[cols_].dropna().corr()
        cd.columns = names_; cd.index = names_
        fc  = px.imshow(cd, text_auto=".2f",
            color_continuous_scale=[[0,'#EF476F'],[0.5,'#060C18'],[1,'#06D6A0']],
            zmin=-1, zmax=1)
        cl  = plot_layout(height=420, show_legend=False)
        cl['margin'] = dict(l=8, r=8, t=30, b=50)
        cl['coloraxis_showscale'] = False
        fc.update_layout(**cl)
        fc.update_traces(textfont=dict(size=12, family="DM Mono"))
        st.plotly_chart(fc, use_container_width=True, config=dict(displaylogo=False, responsive=True))

    with c2:
        section("💱", "مسار الدولار", "")
        st.markdown("""
        <div class="section-sub" style="display:flex;justify-content:space-between;align-items:center;margin-bottom:10px;">
        <div style="direction:rtl">صعود الدولار يعني ارتفاعاً مباشراً في الذهب</div>
        <div style="direction:ltr">USD / EGP</div>
        </div>""", unsafe_allow_html=True)
        fu = go.Figure()
        fu.add_trace(go.Scatter(x=data.index, y=data['USD_EGP_Official'],
            line=dict(color='#4CC9F0', width=2), fill='tozeroy',
            fillcolor='rgba(76,201,240,0.06)',
            hovertemplate="%{x|%d %b %Y}<br><b>%{y:.2f} جنيه</b><extra></extra>"))
        if show_events: add_events(fu, data)
        fu.update_layout(**plot_layout(height=420, show_legend=False))
        st.plotly_chart(fu, use_container_width=True, config=dict(displaylogo=False, responsive=True))


# ═════════════════════════════════════════════════════════════════════════════
# PAGE 2: Price Structure Analysis - Premium Price Anatomy
# ═════════════════════════════════════════════════════════════════════════════

elif page == "📊  تحليل الأسعار":

    section("📊", "تشريح السعر - قيمة حقيقية أم تضخم؟", "")
    st.markdown("""
    <div class="section-sub" style="display:flex;justify-content:space-between;align-items:center;margin-bottom:10px;">
    <div style="direction:rtl">كم من السعر يعكس ارتفاع الذهب عالمياً، وكم يعكس انهيار قيمة الجنيه؟ (قاعدة الحساب: سعر الصرف في يناير 2020)</div>
    <div style="direction:ltr">Stacked Area · 24K · 21K · 18K</div>
    </div>""", unsafe_allow_html=True)

    fig = make_subplots(rows=3, cols=1, shared_xaxes=True,
        row_heights=[0.34, 0.33, 0.33], vertical_spacing=0.10,
        subplot_titles=["24K", "21K", "18K"])

    KFILL = {'24K': 'rgba(255,249,196,0.65)', '21K': 'rgba(255,215,0,0.65)', '18K': 'rgba(205,127,50,0.65)'}
    KROW  = {'24K': 1, '21K': 2, '18K': 3}

    for karat in ['24K', '21K', '18K']:
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
    lyt['legend'] = dict(orientation="h", y=1.20, x=0.5, xanchor="center",
        bgcolor="rgba(0,0,0,0)", borderwidth=0,
        font=dict(size=10, family="Cairo"), itemsizing="constant")
    lyt['xaxis']['rangeselector']['y'] = 1.20
    lyt['title'] = dict(text="تشريح السعر: القيمة الحقيقية مقابل علاوة التضخم والعملة",
        font=dict(size=13, color="#FFD700", family="Cairo"), x=0.5, xanchor='center', y=0.98)
    fig.update_layout(**lyt)
    fig.update_xaxes(tickfont=dict(family="Cairo", size=10, color="#4A6A8A"),
                     gridcolor="rgba(255,255,255,0.05)",
                     range=["2020-01-01", data.index.max()])
    event_labels = {v[0] for v in CRISIS_EVENTS.values()}
    for ann in fig.layout.annotations:
        if ann.text not in event_labels:
            ann.update(x=0.98, xanchor='right', font=dict(color='#B8960C', size=10.5, family='Cairo'))
    for r in [1,2,3]:
        fig.update_yaxes(tickfont=dict(family="Cairo", size=11, color="#4A6A8A"),
                         title_text="جنيه", title_font=dict(size=9), row=r, col=1)
    st.plotly_chart(fig, use_container_width=True, config=dict(displaylogo=False, responsive=True))

    spacer(24)
    section("📐", "نسبة علاوة التضخم %", "")
    st.markdown("""
    <div class="section-sub" style="display:flex;justify-content:space-between;align-items:center;margin-bottom:10px;">
    <div style="direction:rtl">النسبة المئوية من السعر ناتجة عن ضعف الجنيه - كلما ارتفعت، كلما كان الذهب وقاية أكبر</div>
    <div style="direction:ltr">Inflation Premium %</div>
    </div>""", unsafe_allow_html=True)

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
    cols3 = st.columns(3)
    for col3, karat in zip(cols3, KARAT_FACTORS):
        ap = data[f'PremPct_{karat}'].mean()
        mx = data[f'PremPct_{karat}'].max()
        with col3:
            insight(f"<b style='color:{KARAT_COLORS[karat]}'>{karat}</b><br>"
                    f"متوسط العلاوة: <span class='num'>{ap:.1f}%</span><br>"
                    f"الذروة التاريخية: <span class='num-red'>{mx:.1f}%</span>")


# ═════════════════════════════════════════════════════════════════════════════
# PAGE 3: Investment Portfolio Simulation - Net Cost Simulation
# ═════════════════════════════════════════════════════════════════════════════

elif page == "💼  محاكاة الاستثمار":

    section("💼", "محاكاة الاستثمار الواقعية", "")
    st.markdown(f"""
    <div class="section-sub" style="display:flex;justify-content:space-between;align-items:center;margin-bottom:10px;">
    <div style="direction:rtl">
      لو استثمرنا 100,000 جنيه في يناير 2020 - القيمة الصافية بعد خصم المصنعية
      <span style="font-family:'DM Mono';direction:ltr;display:inline;">(24K +{MAKING_CHARGES['24K']}ج · 21K +{MAKING_CHARGES['21K']}ج · 18K +{MAKING_CHARGES['18K']}ج)</span>
      وفروق البيع
      <span style="font-family:'DM Mono';direction:ltr;display:inline;">(24K {SELL_SPREAD['24K']*100:.1f}% · 21K {SELL_SPREAD['21K']*100:.1f}% · 18K {SELL_SPREAD['18K']*100:.1f}%)</span>
    </div>
    <div style="direction:ltr">Net Portfolio Simulation · 100,000 EGP Start</div>
    </div>""", unsafe_allow_html=True)

    fig_inv = go.Figure()
    for karat, color in KARAT_COLORS.items():
        fig_inv.add_trace(go.Scatter(x=data.index, y=data[f'Port_{karat}'],
            name=f'{karat} ذهب (صافي)', line=dict(color=color, width=2.2),
            hovertemplate=f"<b>{karat}</b>: %{{y:,.0f}} جنيه<extra></extra>"))
    fig_inv.add_trace(go.Scatter(x=data.index, y=data['Port_USD'],
        name='دولار', line=dict(color='#4CC9F0', width=1.6, dash='dot'),
        hovertemplate="دولار: %{y:,.0f}<extra></extra>"))
    fig_inv.add_trace(go.Scatter(x=data.index, y=data['Port_Cash'],
        name='كاش (جنيه)', line=dict(color='#1E3A5F', width=1.2, dash='dot'),
        hovertemplate="كاش: %{y:,.0f}<extra></extra>"))
    if show_events: add_events(fig_inv, data)
    lyt_inv = plot_layout(height=440, yaxis=dict(title_text="القيمة الصافية (جنيه)"))
    lyt_inv['title'] = dict(text="نمو الثروة الحقيقي (مخصوم منه تكاليف الدخول والخروج)",
        font=dict(size=13, color="#FFD700", family="Cairo"), x=0.5, xanchor='center', y=0.97)
    fig_inv.update_layout(**lyt_inv)
    st.plotly_chart(fig_inv, use_container_width=True, config=dict(displaylogo=False, responsive=True))

    spacer()
    cols4 = st.columns(4)
    for col4, karat in zip(cols4[:3], KARAT_FACTORS):
        m = compute_metrics(data, karat)
        tc = '#06D6A0' if m['total'] > 0 else '#EF476F'
        entry = data[f'Price_{karat}'].iloc[0]
        grams = 100_000 / entry
        with col4:
            st.markdown(f"""
            <div class="metric-card" style="padding:15px 10px;">
              <div class="metric-card-title" style="color:{KARAT_COLORS[karat]}">{karat} ذهب</div>
              <div class="metric-row"><span class="metric-label">الكمية الصافية</span>
                <span class="metric-val" style="color:#E8EDF5">{grams:,.1f} جم</span></div>
              <div class="metric-row"><span class="metric-label">سعر 2020 (+مصنعية)</span>
                <span class="metric-val" style="color:#8D99AE">{entry:,.0f} ج</span></div>
              <div class="metric-row"><span class="metric-label">القيمة الصافية</span>
                <span class="metric-val" style="color:#FFD700">{m['final']:,.0f} ج</span></div>
              <div class="metric-row"><span class="metric-label">العائد الفعلي</span>
                <span class="metric-val" style="color:{tc}">{m['total']:+.1f}%</span></div>
              <div class="metric-row"><span class="metric-label">Sharpe Ratio</span>
                <span class="metric-val" style="color:#4CC9F0">{m['sharpe']:.2f}</span></div>
              <div class="metric-row"><span class="metric-label">Max Drawdown</span>
                <span class="metric-val" style="color:#EF476F">{m['max_dd']:.1f}%</span></div>
              <div class="metric-row"><span class="metric-label">VaR 95%</span>
                <span class="metric-val" style="color:#FF9F43">{m['var95']:.2f}%</span></div>
            </div>""", unsafe_allow_html=True)

    # USD benchmark card
    usd0        = data['USD_EGP_Official'].iloc[0]
    usd_bought  = 100_000 / usd0
    usd_final   = data['Port_USD'].iloc[-1]
    usd_ret     = (usd_final / 100_000 - 1) * 100
    usd_dd_s    = (data['Port_USD'] / data['Port_USD'].cummax() - 1) * 100
    usd_dd      = usd_dd_s.min()
    usd_r_d     = data['Port_USD'].pct_change().dropna()
    usd_ann_r   = usd_r_d.mean() * 252
    usd_ann_v   = usd_r_d.std() * np.sqrt(252)
    usd_sharpe  = usd_ann_r / usd_ann_v if usd_ann_v else 0
    usd_tc      = '#06D6A0' if usd_ret > 0 else '#EF476F'

    with cols4[3]:
        st.markdown(f"""
        <div class="metric-card" style="padding:15px 10px;">
          <div class="metric-card-title" style="color:#4CC9F0">الدولار USD</div>
          <div class="metric-row"><span class="metric-label">الكمية المشتراة</span>
            <span class="metric-val" style="color:#E8EDF5">${usd_bought:,.0f}</span></div>
          <div class="metric-row"><span class="metric-label">سعر 2020</span>
            <span class="metric-val" style="color:#8D99AE">{usd0:,.2f} ج</span></div>
          <div class="metric-row"><span class="metric-label">القيمة الحالية</span>
            <span class="metric-val" style="color:#FFD700">{usd_final:,.0f} ج</span></div>
          <div class="metric-row"><span class="metric-label">العائد الكلي</span>
            <span class="metric-val" style="color:{usd_tc}">{usd_ret:+.1f}%</span></div>
          <div class="metric-row"><span class="metric-label">Sharpe Ratio</span>
            <span class="metric-val" style="color:#4CC9F0">{usd_sharpe:.2f}</span></div>
          <div class="metric-row"><span class="metric-label">Max Drawdown</span>
            <span class="metric-val" style="color:#EF476F">{usd_dd:.1f}%</span></div>
        </div>""", unsafe_allow_html=True)

    spacer(24)
    section("📉", "Max Drawdown", "")
    st.markdown("""
    <div class="section-sub" style="display:flex;justify-content:space-between;align-items:center;margin-bottom:10px;">
    <div style="direction:rtl">الانخفاض عن القمة - يقيس الخسارة في أسوأ الأوقات</div>
    <div style="direction:ltr">Peak-to-Trough Drawdown %</div>
    </div>""", unsafe_allow_html=True)

    fdd = go.Figure()
    fc_map = {'24K': 'rgba(255,249,196,0.09)', '21K': 'rgba(255,215,0,0.09)', '18K': 'rgba(205,127,50,0.09)'}
    for karat, color in KARAT_COLORS.items():
        fdd.add_trace(go.Scatter(x=data.index, y=data[f'DD_{karat}'],
            name=karat, line=dict(color=color, width=1.8),
            fill='tozeroy', fillcolor=fc_map.get(karat,'rgba(255,255,255,0.1)'),
            hovertemplate=f"{karat}: %{{y:.1f}}%<extra></extra>"))
    fdd.add_trace(go.Scatter(x=data.index, y=usd_dd_s,
        name='دولار', line=dict(color='#4CC9F0', width=1.6, dash='dot'),
        hovertemplate="دولار: %{y:.1f}%<extra></extra>"))
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

    spacer()
    best_k  = max(KARAT_FACTORS.keys(), key=lambda k: compute_metrics(data,k)['total'])
    best_m  = compute_metrics(data, best_k)
    insight(f"""💡 <b>ملخص المقارنة:</b>
    أفضل أداء واقعي (بعد خصم التكاليف) كان <b style="color:{KARAT_COLORS[best_k]}">{best_k}</b>
    بعائد صافٍ <span class="num">{best_m['total']:+.1f}%</span> مقابل
    الدولار <span class="num">{usd_ret:+.1f}%</span> والكاش بالجنيه
    <span class="num-red">0%</span> (مع التضخم الحقيقي).
    المصنعية وفروق البيع تُقلل العوائد لكن لا تمحو التفوق التاريخي للذهب.
    """)


# ═════════════════════════════════════════════════════════════════════════════
# PAGE 4: Radar & Technical Indicators - Technical Analysis
# ═════════════════════════════════════════════════════════════════════════════

elif page == "📡  المؤشرات التقنية":

    k = selected_karat
    section("📡", f"التحليل التقني - {k}", "")
    st.markdown("""
    <div class="section-sub" style="display:flex;justify-content:space-between;align-items:center;margin-bottom:10px;">
    <div style="direction:rtl">إشارات الشراء والبيع الآلية</div>
    <div style="direction:ltr">Bollinger Bands · RSI-14 · MACD</div>
    </div>""", unsafe_allow_html=True)

    fig_tech = make_subplots(rows=3, cols=1, shared_xaxes=True,
        row_heights=[0.55, 0.25, 0.20], vertical_spacing=0.07,
        subplot_titles=[
            f"السعر + Bollinger Bands ({k})",
            "MACD - زخم الاتجاه",
            "RSI-14 - مستوى التشبع"
        ])

    # Bollinger Bands
    fig_tech.add_trace(go.Scatter(x=data.index, y=data[f'BB_up_{k}'],
        line=dict(width=0), showlegend=False), row=1, col=1)
    fig_tech.add_trace(go.Scatter(x=data.index, y=data[f'BB_dn_{k}'],
        fill='tonexty', fillcolor='rgba(180,180,255,0.04)',
        line=dict(width=0), name='Bollinger Bands'), row=1, col=1)
    fig_tech.add_trace(go.Scatter(x=data.index, y=data[f'Price_{k}'],
        name='السعر', line=dict(color='#D8E4F0', width=1.8),
        hovertemplate="%{x|%d %b %Y} - %{y:,.0f} جنيه<extra></extra>"), row=1, col=1)
    fig_tech.add_trace(go.Scatter(x=data.index, y=data[f'SMA50_{k}'],
        name='SMA 50', line=dict(color='#FF9F43', width=1.1, dash='dot')), row=1, col=1)
    fig_tech.add_trace(go.Scatter(x=data.index, y=data[f'SMA200_{k}'],
        name='SMA 200', line=dict(color='#A855F7', width=1.1, dash='dot')), row=1, col=1)

    # BUY / SELL signal markers overlaid on price chart
    buys  = data[data[f'Signal_{k}'] == 'BUY']
    sells = data[data[f'Signal_{k}'] == 'SELL']
    fig_tech.add_trace(go.Scatter(x=buys.index, y=buys[f'Price_{k}'], mode='markers',
        name='BUY ▲', marker=dict(symbol='triangle-up', color='#06D6A0', size=7,
                                   line=dict(width=1, color='white'))), row=1, col=1)
    fig_tech.add_trace(go.Scatter(x=sells.index, y=sells[f'Price_{k}'], mode='markers',
        name='SELL ▼', marker=dict(symbol='triangle-down', color='#EF476F', size=7,
                                    line=dict(width=1, color='white'))), row=1, col=1)

    # MACD histogram and signal line
    hc = ['#06D6A0' if v >= 0 else '#EF476F' for v in data[f'MACDHist_{k}']]
    fig_tech.add_trace(go.Bar(x=data.index, y=data[f'MACDHist_{k}'],
        name='Histogram', marker_color=hc, opacity=0.7), row=2, col=1)
    fig_tech.add_trace(go.Scatter(x=data.index, y=data[f'MACD_{k}'],
        name='MACD', line=dict(color='#4CC9F0', width=1.5)), row=2, col=1)
    fig_tech.add_trace(go.Scatter(x=data.index, y=data[f'MACDSig_{k}'],
        name='Signal Line', line=dict(color='#FF9F43', width=1.5)), row=2, col=1)

    # RSI-14 with overbought/oversold reference bands
    fig_tech.add_trace(go.Scatter(x=data.index, y=data[f'RSI_{k}'],
        name='RSI-14', line=dict(color='#A855F7', width=1.7)), row=3, col=1)
    fig_tech.add_hline(y=70, line_dash='dot', line_color='#EF476F', opacity=0.4, row=3, col=1)
    fig_tech.add_hline(y=30, line_dash='dot', line_color='#06D6A0', opacity=0.4, row=3, col=1)
    fig_tech.add_hrect(y0=70, y1=100, fillcolor='rgba(239,71,111,0.04)', line_width=0, row=3, col=1)
    fig_tech.add_hrect(y0=0,  y1=30,  fillcolor='rgba(6,214,160,0.04)',  line_width=0, row=3, col=1)

    if show_events: add_events(fig_tech, data, rows=[1,2,3], y_ann=0.93)

    lyt_tech = plot_layout(height=900)
    lyt_tech['margin'] = dict(l=8, r=8, t=160, b=8)
    lyt_tech['legend'] = dict(orientation="h", y=1.12, x=0.5, xanchor="center",
        bgcolor="rgba(0,0,0,0)", borderwidth=0,
        font=dict(size=9.5, family="Cairo"), itemsizing="constant", tracegroupgap=3)
    lyt_tech['xaxis']['rangeselector']['y'] = 1.06
    fig_tech.update_layout(**lyt_tech)
    fig_tech.update_xaxes(tickfont=dict(family="Cairo", size=10, color="#3A4A65"),
                          gridcolor="rgba(255,255,255,0.05)",
                          range=["2020-01-01", data.index.max()])
    event_labels = {v[0] for v in CRISIS_EVENTS.values()}
    for ann in fig_tech.layout.annotations:
        if ann.text not in event_labels:
            ann.update(x=0.98, xanchor='right',
                       font=dict(color='#FFD700', size=11, family='Cairo'))
    fig_tech.update_yaxes(title_text="السعر (جنيه)", title_font=dict(size=9, color="#3A4A65"), row=1, col=1)
    fig_tech.update_yaxes(title_text="MACD", tickfont=dict(family="Cairo", size=9, color="#3A4A65"),
                          title_font=dict(size=9, color="#3A4A65"), row=2, col=1)
    fig_tech.update_yaxes(title_text="RSI", range=[0, 100],
                          tickfont=dict(family="Cairo", size=9, color="#3A4A65"),
                          title_font=dict(size=9, color="#3A4A65"), row=3, col=1)
    st.plotly_chart(fig_tech, use_container_width=True, config=dict(displaylogo=False, responsive=True))

    spacer()
    sig  = data[f'Signal_{k}'].iloc[-1]
    rsi  = data[f'RSI_{k}'].iloc[-1]
    macd = data[f'MACD_{k}'].iloc[-1]
    sc   = {'BUY': 'sig-buy', 'SELL': 'sig-sell', 'HOLD': 'sig-hold'}.get(sig, 'sig-hold')
    sa   = {'BUY': 'شراء 📈', 'SELL': 'بيع 📉', 'HOLD': 'انتظار ⏸'}.get(sig, 'انتظار')
    bbu  = data[f'BB_up_{k}'].iloc[-1]
    bbl  = data[f'BB_dn_{k}'].iloc[-1]
    lp   = data[f'Price_{k}'].iloc[-1]
    bbp  = ("عند الحد الأعلى ⚠️" if lp > bbu * 0.98 else
            "عند الحد الأدنى ✅" if lp < bbl * 1.02 else "داخل النطاق")
    insight(f"""
    <div style="display:flex;flex-wrap:wrap;gap:18px;align-items:center;direction:ltr;
                justify-content:center;font-family:'DM Mono',monospace;font-size:0.82rem;">
      <div><b style="color:#FFD700;font-family:Cairo">الإشارة ({k}):</b>&nbsp;<span class="{sc}">{sa}</span></div>
      <div style="color:#1E3A5F">│</div>
      <div><b style="color:#A855F7">RSI</b>&nbsp;{rsi:.1f}{"&nbsp;<span style='color:#EF476F;font-size:0.72rem'>تشبع شراء</span>" if rsi>70 else "&nbsp;<span style='color:#06D6A0;font-size:0.72rem'>تشبع بيع</span>" if rsi<30 else ""}</div>
      <div style="color:#1E3A5F">│</div>
      <div><b style="color:#4CC9F0">MACD</b>&nbsp;{macd:,.1f}</div>
      <div style="color:#1E3A5F">│</div>
      <div><b style="color:#FF9F43">BB</b>&nbsp;{bbp}</div>
    </div>""")


# ═════════════════════════════════════════════════════════════════════════════
# PAGE 5: Advanced Forecasting - Tuned Prophet ML Suite + ROI Calculator
# ═════════════════════════════════════════════════════════════════════════════

elif page == "🔮  التوقعات":

    section("🔮", f"توقعات الأسعار - {selected_karat}", "")
    st.markdown("""
    <div class="section-sub" style="display:flex;justify-content:space-between;align-items:center;margin-bottom:10px;">
    <div style="direction:rtl">نموذج التنبؤ مع متغيرات الدولار والنفط - استراتيجية الدمج التاريخي</div>
    <div style="direction:ltr">Prophet Model · Regressors: USD + OIL · Historical Date Merge Strategy</div>
    </div>""", unsafe_allow_html=True)

    st.markdown('<div class="fc-label">أفق التوقع (أيام)</div>', unsafe_allow_html=True)
    forecast_days = st.slider("d", 30, 365, 180, 30, label_visibility="collapsed")

    with st.spinner("⏳ جاري تدريب نموذج Prophet..."):
        try:
            from prophet import Prophet

            k      = selected_karat
            fv_col = f'Price_{k}'

            # ── Step 1: Prepare main training frame ──
            train = data.reset_index()[['Date', fv_col, 'USD_EGP_Official', 'Crude_Oil']].copy()
            train.columns = ['ds', 'y', 'USD', 'OIL']
            train['ds'] = pd.to_datetime(train['ds'])
            train['ds'] = pd.to_datetime(train['ds'])
            
            # Forward fill and backward fill regressors so we don't lose rows
            train['USD'] = train['USD'].ffill().bfill()
            train['OIL'] = train['OIL'].ffill().bfill()
            
            # Drop rows ONLY where the target 'y' (Gold Price) is missing
            train = train.dropna(subset=['y'])

            # ── Step 2: Train independent regressor models and project N days forward ──
            def forecast_regressor(col_name: str, n_days: int) -> pd.DataFrame:
                """
                Train a lightweight Prophet model on a single regressor series and
                return a future DataFrame [ds, yhat] covering the next n_days.
                Changepoint scale is conservative (0.05) to avoid overfitting.
                """
                df_reg = data.reset_index()[['Date', col_name]].copy()
                df_reg.columns = ['ds', 'y']
                df_reg['ds'] = pd.to_datetime(df_reg['ds'])
                
                # Explicitly drop missing values in the target 'y' before fitting
                df_reg = df_reg.dropna(subset=['y'])
                mr = Prophet(
                    yearly_seasonality=True,
                    weekly_seasonality=False,    # FX and oil have no intra-week cycle
                    daily_seasonality=False,
                    changepoint_prior_scale=0.05, # conservative - macro series trend slowly
                    interval_width=0.80
                )
                mr.fit(df_reg)
                fut   = mr.make_future_dataframe(periods=n_days, freq='D')
                fc_r  = mr.predict(fut)[['ds', 'yhat']]
                # Return only the future (post-training) slice
                last_hist_date = df_reg['ds'].max()
                return fc_r[fc_r['ds'] > last_hist_date].reset_index(drop=True)

            usd_future_df = forecast_regressor('USD_EGP_Official', forecast_days)
            oil_future_df = forecast_regressor('Crude_Oil',         forecast_days)

            # ── Step 3: Fit the main gold Prophet model with tuned parameters ──
            # TASK 3 - Financial time-series best practices applied:
            #   • changepoint_prior_scale=0.10  - moderate flexibility; prevents overfitting to
            #     short-term spikes while still capturing structural breaks (devaluations).
            #   • yearly_seasonality=True        - gold has an annual demand cycle (festive seasons).
            #   • weekly_seasonality=False       - gold markets are 5-day (Mon–Fri) without a
            #     meaningful intra-week price pattern in EGP terms.
            #   • interval_width=0.90            - wider confidence band acknowledges high gold
            #     price volatility; 95% was too wide and obscured the point forecast visually.
            #   • n_changepoints=30 (default 25) - slightly more change-points for a 5-year series
            #     that has experienced multiple structural regime shifts.
            pm = Prophet(
                yearly_seasonality=True,
                weekly_seasonality=False,
                daily_seasonality=False,
                changepoint_prior_scale=0.10,   # tuned: less aggressive than 0.15 to avoid overfitting
                seasonality_prior_scale=10.0,   # allow seasonal components to fit gold's amplitude
                interval_width=0.90,            # 90% CI - realistic for commodity price volatility
                n_changepoints=30,              # extra change-points for a regime-heavy series
            )
            pm.add_regressor('USD', standardize=True)  # standardize regressors for numerical stability
            pm.add_regressor('OIL', standardize=True)
            pm.fit(train)

            # ── Step 4: Build future dataframe using HISTORICAL DATE MERGE STRATEGY ──
            # make_future_dataframe adds rows into the future (calendar days).
            future_raw = pm.make_future_dataframe(periods=forecast_days, freq='D')
            future_raw['ds'] = pd.to_datetime(future_raw['ds'])

            # 4a. Attach historical regressors via left-join on ds
            hist_regs = train[['ds', 'USD', 'OIL']].copy()
            future_merged = future_raw.merge(hist_regs, on='ds', how='left')

            # 4b. For days beyond historical range, merge forecasted regressor values
            usd_future_df.columns = ['ds', 'USD_fc']
            oil_future_df.columns = ['ds', 'OIL_fc']
            future_merged = future_merged.merge(usd_future_df, on='ds', how='left')
            future_merged = future_merged.merge(oil_future_df, on='ds', how='left')

            # 4c. Fill missing historical USD/OIL with forecasted values (weekend/holiday gaps)
            future_merged['USD'] = future_merged['USD'].fillna(future_merged['USD_fc'])
            future_merged['OIL'] = future_merged['OIL'].fillna(future_merged['OIL_fc'])
            future_merged.drop(columns=['USD_fc', 'OIL_fc'], inplace=True)

            # 4d. Safety: forward-fill then back-fill any remaining NaNs
            future_merged['USD'] = future_merged['USD'].ffill().bfill()
            future_merged['OIL'] = future_merged['OIL'].ffill().bfill()

            future_final = future_merged[['ds', 'USD', 'OIL']].copy()

            # ── Step 5: Generate predictions ──
            fc = pm.predict(future_final)

            # ── Step 6: In-sample evaluation on historical training data ──
            n        = len(train)
            y_true   = train['y'].values
            y_pred   = fc.iloc[:n]['yhat'].values
            mae      = np.abs(y_true - y_pred).mean()
            rmse     = np.sqrt(((y_true - y_pred) ** 2).mean())

            # ── Step 7: Extract the forward forecast horizon ──
            last_hist = train['ds'].max()
            fc_out    = fc[fc['ds'] > last_hist].head(forecast_days).copy()
            actual_last_price = train['y'].iloc[-1]
            predicted_last_price = fc[fc['ds'] == last_hist]['yhat'].values[0] if len(fc[fc['ds'] == last_hist]) > 0 else fc.iloc[:n]['yhat'].iloc[-1]
            continuity_offest = actual_last_price - predicted_last_price
            fc_out['yhat'] = fc_out['yhat'] + continuity_offest  # adjust forecast to ensure smooth transition from historical to forecasted values
            fc_out['yhat_upper'] = fc_out['yhat_upper'] + continuity_offest
            fc_out['yhat_lower'] = fc_out['yhat_lower'] + continuity_offest 

            # ── Forecast chart ──
            title_chart = f"توقعات ذهب \u2066{k}\u2069 · {forecast_days} يوم قادماً"
            fig_fc = go.Figure()

            # Weekly-downsampled actuals for cleaner display on long horizons
            hw = data[fv_col].resample('W').last()
            fig_fc.add_trace(go.Scatter(x=hw.index, y=hw, name='السعر الفعلي',
                line=dict(color='#4A6A8A', width=1.5),
                hovertemplate="%{x|%d %b %Y}<br>%{y:,.0f} جنيه<extra></extra>"))

            # 90% confidence band
            fig_fc.add_trace(go.Scatter(x=fc_out['ds'], y=fc_out['yhat_upper'],
                line=dict(width=0), showlegend=False))
            fig_fc.add_trace(go.Scatter(x=fc_out['ds'], y=fc_out['yhat_lower'],
                fill='tonexty', fillcolor='rgba(76,201,240,0.10)',
                line=dict(width=0), name='‫نطاق الثقة 90%‬'))

            # Point forecast line
            fig_fc.add_trace(go.Scatter(x=fc_out['ds'], y=fc_out['yhat'],
                name='‫توقع Prophet‬', line=dict(color='#4CC9F0', width=2.5),
                hovertemplate="%{x|%d %b %Y}<br><b>%{y:,.0f} جنيه</b><extra></extra>"))

            # Today marker
            fig_fc.add_vline(x=datetime.today().timestamp() * 1000,
                line_dash='dash', line_color='#FFD700', opacity=0.5,
                annotation_text='اليوم',
                annotation_font=dict(color='#FFD700', size=9.5),
                annotation_position="top right")

            if show_events: add_events(fig_fc, data)

            lyt_fc = plot_layout(height=500, yaxis=dict(title_text="السعر (جنيه)"))
            lyt_fc['title'] = dict(text=title_chart,
                font=dict(size=13, color="#FFD700", family="Cairo"),
                x=0.5, xanchor='center', y=0.97)
            fig_fc.update_layout(**lyt_fc)
            st.plotly_chart(fig_fc, use_container_width=True, config=dict(displaylogo=False, responsive=True))

            spacer()
            la  = data[fv_col].iloc[-1]
            fe  = fc_out['yhat'].iloc[-1]
            cp  = (fe / la - 1) * 100
            cc  = '#06D6A0' if cp >= 0 else '#EF476F'
            cards_html = (
                kpi_html(f"{la:,.0f}",    "السعر الحالي (جنيه)",        "#FFD700", "0.05s") +
                kpi_html(f"{fe:,.0f}",    f"التوقع ({forecast_days}ي)",  "#4CC9F0", "0.10s") +
                kpi_html(f"{cp:+.1f}%",   "التغيير المتوقع",              cc,        "0.15s") +
                kpi_html(f"{rmse:,.0f}",  "RMSE النموذج",                "#A855F7", "0.20s")
            )
            st.markdown(f'<div class="kpi-grid" style="grid-template-columns:repeat(4,1fr)">{cards_html}</div>',
                        unsafe_allow_html=True)

            spacer()
            insight(f"""
            🤖 <b>ملخص التوقع:</b> يتوقع نموذج Prophet أن يصل سعر جرام {k} إلى
            <span class="{'num' if cp>=0 else 'num-red'}">{fe:,.0f} جنيه</span>
            خلال {forecast_days} يوم القادمة - تغيير
            <span class="{'num' if cp>=0 else 'num-red'}">{cp:+.1f}%</span> عن السعر الحالي.<br>
            <span style="direction:rtl; display:block; margin-top:6px;">
            دقة النموذج -
            <span style="font-family:'DM Mono',monospace; direction:ltr; display:inline-block;">MAE = {mae:,.0f} جنيه</span>
            &nbsp;|&nbsp;
            <span style="font-family:'DM Mono',monospace; direction:ltr; display:inline-block;">RMSE = {rmse:,.0f} جنيه</span>
            - كلما قل الرقم كلما كان النموذج أدق.
            </span>
            <span style="display:block;margin-top:6px;font-size:0.75rem;color:#3A4A65;">
            * الاستراتيجية: دمج تاريخي (Historical Date Merge) - نماذج مستقلة للمتغيرات الخارجية
            تمنع أخطاء عدم التوافق بين التقويم الرسمي وأيام التداول.
            </span>""")

            # ─────────────────────────────────────────────────────────────────
            # TASK 2 - INVESTMENT ROI FORECASTER (replaces component chart)
            # ─────────────────────────────────────────────────────────────────
            spacer(28)
            section("💰", "حاسبة العائد على الاستثمار", "")
            st.markdown("""
            <div class="section-sub" style="display:flex;justify-content:space-between;align-items:center;margin-bottom:10px;">
            <div style="direction:rtl">أدخل مبلغ استثمارك واختر العيار والمدة - سنحسب العائد المتوقع بناءً على توقعات Prophet</div>
            <div style="direction:ltr">Prophet-Powered ROI Forecaster</div>
            </div>""", unsafe_allow_html=True)

            # ── ROI calculator inputs ──
            col_inv1, col_inv2, col_inv3 = st.columns([2, 1, 2])

            with col_inv1:
                invest_amount = st.number_input(
                    "مبلغ الاستثمار (جنيه مصري)",
                    min_value=1_000,
                    max_value=10_000_000,
                    value=100_000,
                    step=1_000,
                    format="%d",
                    help="أدخل المبلغ الذي تريد استثماره بالجنيه المصري"
                )

            with col_inv2:
                roi_karat = st.selectbox(
                    "العيار",
                    options=["18K", "21K", "24K"],
                    index=1,
                    key="roi_karat_select"
                )

            with col_inv3:
                st.markdown('<div class="fc-label">المدة (أيام)</div>', unsafe_allow_html=True)
                roi_days = st.slider(
                    "roi_duration",
                    min_value=30,
                    max_value=365,
                    value=min(forecast_days, 365),
                    step=30,
                    label_visibility="collapsed",
                    help="اختر عدد الأيام التي تنوي الاحتفاظ بالذهب خلالها"
                )

            # ── ROI computation logic ──
            # Current (entry) price for the chosen karat
            current_price_roi = data[f'Price_{roi_karat}'].iloc[-1]

            # If the selected ROI karat differs from the model karat (k), we must
            # derive the forecasted price by applying the karat factor ratio.
            # This avoids re-training Prophet and is algebraically exact because all
            # karat prices share the same underlying USD/oz × EGP/USD driver.
            if roi_karat == k:
                # Use the already-trained model's forecast directly
                roi_fc_series = fc_out.copy()
            else:
                # Scale the existing forecast using the ratio of karat purity factors
                scale = KARAT_FACTORS[roi_karat] / KARAT_FACTORS[k]
                roi_fc_series = fc_out.copy()
                for col_fc in ['yhat', 'yhat_upper', 'yhat_lower']:
                    roi_fc_series[col_fc] = roi_fc_series[col_fc] * scale

            # Clip roi_days to available forecast rows to prevent index errors
            roi_days_clipped = min(roi_days, len(roi_fc_series))

            if roi_days_clipped > 0:
                forecast_row      = roi_fc_series.iloc[roi_days_clipped - 1]
                target_price_roi  = max(forecast_row['yhat'], 0.01)   # guard against negative yhat
                target_date_roi   = forecast_row['ds']

                # Entry: invest amount buys N grams at current retail price (already includes making charge)
                entry_cost_per_g  = current_price_roi
                grams_roi         = invest_amount / entry_cost_per_g

                # Exit: sell at forecasted price less bid-ask spread
                exit_value_roi    = grams_roi * target_price_roi * (1 - SELL_SPREAD[roi_karat])
                net_profit_roi    = exit_value_roi - invest_amount
                roi_pct           = (net_profit_roi / invest_amount) * 100
                annualised_roi    = roi_pct * (365 / roi_days_clipped)

                # Color coding: green for gain, red for loss
                profit_color      = "#06D6A0" if net_profit_roi >= 0 else "#EF476F"
                roi_icon          = "📈" if net_profit_roi >= 0 else "📉"

                # ── Display ROI metric cards using st.metric ──
                spacer(8)
                m1, m2, m3, m4 = st.columns(4)

                with m1:
                    st.metric(
                        label="‫💰 القيمة المتوقعة‬",
                        value=f"{exit_value_roi:,.0f} ج",
                        delta=f"{net_profit_roi:+,.0f} ج",
                        delta_color="normal",
                        help=f"القيمة الصافية بعد {roi_days_clipped} يوم بتاريخ {target_date_roi.strftime('%d %b %Y')}"
                    )

                with m2:
                    st.metric(
                        label=f"{roi_icon} العائد الصافي",
                        value=f"{roi_pct:+.2f}%",
                        delta=f"{annualised_roi:+.1f}% سنوياً",
                        delta_color="normal",
                        help="العائد الإجمالي على رأس المال المستثمر، والعائد السنوي المُقنَّن"
                    )

                with m3:
                    st.metric(
                        label="⚖️ الكمية المشتراة",
                        value=f"{grams_roi:.2f} جم",
                        delta=f"{roi_karat} · {entry_cost_per_g:,.0f} ج/جم",
                        delta_color="off",
                        help="عدد الجرامات بعد خصم المصنعية من المبلغ الإجمالي"
                    )

                with m4:
                    st.metric(
                        label="🎯 سعر الهدف",
                        value=f"{target_price_roi:,.0f} ج/جم",
                        delta=f"{(target_price_roi/current_price_roi - 1)*100:+.1f}% عن الحالي",
                        delta_color="normal",
                        help=f"سعر جرام {roi_karat} المتوقع في {target_date_roi.strftime('%d %b %Y')}"
                    )

                spacer(12)
                # Detailed insight summary
                insight(f"""
                💡 <b>ملخص حاسبة العائد:</b>
                استثمار <span class="num">{invest_amount:,.0f} جنيه</span> في ذهب <b>{roi_karat}</b>
                اليوم بسعر <span class="num">{current_price_roi:,.0f} جنيه/جم</span> (شامل مصنعية <span class="num">{MAKING_CHARGES[roi_karat]:,} جنيه</span>)
                يمنحك <span class="num">{grams_roi:.2f} جرام</span>. بناءً على توقعات Prophet خلال
                <span class="num">{roi_days_clipped}</span> يوم، قد تبلغ قيمتها
                <span class="{'num' if net_profit_roi >= 0 else 'num-red'}">{exit_value_roi:,.0f} جنيه</span>
                - ربح <span class="{'num' if net_profit_roi >= 0 else 'num-red'}">{net_profit_roi:+,.0f} جنيه</span>
                (<span class="{'num' if roi_pct >= 0 else 'num-red'}">{roi_pct:+.2f}%</span>).<br>
                <span style="display:block;margin-top:6px;font-size:0.75rem;color:#3A4A65;">
                * الحسابات تشمل المصنعية عند الشراء وفرق السعر ({SELL_SPREAD[roi_karat]*100:.1f}%) عند البيع.
                التوقعات للأغراض التوجيهية فقط وليست نصيحة استثمارية.
                </span>""")
            else:
                st.warning("⚠️ لا تتوفر بيانات توقع كافية للمدة المحددة. حاول تمديد أفق التوقع.")

        except ImportError:
            st.error("⚠️ مكتبة Prophet غير مثبتة - قم بتشغيل: pip install prophet")
        except Exception as e:
            st.error(f"خطأ في نموذج التنبؤ: {e}")

# ─────────────────────────────────────────────────────────────────────────────

st.markdown('</div>', unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# CLI ENTRY POINT (background updater)
# ─────────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import sys
    if "--update" in sys.argv:
        print("⏳ Starting background data update...")
        success = run_scraper()
        if success:
            print("⚙️ Scraper succeeded. Generating Processed CSV...")
            try:
                _mt = os.path.getmtime(CSV_PATH)
                df_proc = load_data(CSV_PATH, _mt)
                df_proc.to_csv(CSV_PROCESSED_PATH, index=True, index_label="Date")
                print("✅ Both Gold_Egypt.csv & Processed.csv updated!")
            except Exception as e:
                print(f"⚠️ Processed generation failed: {e}")
                sys.exit(1) 
        else:
            print("❌ Failed to update spot/fx data")
            sys.exit(1)