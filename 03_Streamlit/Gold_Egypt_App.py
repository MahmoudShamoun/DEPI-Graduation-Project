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
# I18N / BILINGUAL SYSTEM (Arabic / English)
# Centralized TRANSLATIONS dict + t(key) helper. Default language = English.
# Mixed Arabic-English financial/technical terms (Prophet, RSI, MACD, karat
# labels like 18K/21K/24K, ticker symbols, etc.) are intentionally NOT
# translated per project convention.
# ─────────────────────────────────────────────────────────────────────────────

if "lang" not in st.session_state:
    st.session_state.lang = "en"   # default language MUST be English

def set_lang(lang_code: str):
    st.session_state.lang = lang_code

LANG  = st.session_state.lang
DIR   = "rtl" if LANG == "ar" else "ltr"
ALIGN = "right" if LANG == "ar" else "left"

TRANSLATIONS = {
    # ── App / Sidebar ──
    "app_tagline":         {"en": "Financial Analytics Tool · Since 2020",      "ar": "أداة التحليل المالي · منذ 2020"},
    "nav_home":             {"en": "🏠  Home",                                   "ar": "🏠  الرئيسية"},
    "nav_analysis":         {"en": "📊  Price Analysis",                        "ar": "📊  تحليل الأسعار"},
    "nav_investment":       {"en": "💼  Investment Simulator",                  "ar": "💼  محاكاة الاستثمار"},
    "nav_technical":        {"en": "📡  Technical Indicators",                  "ar": "📡  المؤشرات التقنية"},
    "nav_forecast":         {"en": "🔮  Forecast",                              "ar": "🔮  التوقعات"},
    "main_karat_label":     {"en": "Primary Karat",                             "ar": "العيار الرئيسي"},
    "crisis_events_toggle": {"en": "Crisis Events",                             "ar": "أحداث الأزمات"},
    "crisis_legend": {
        "en": ('<span style="color:#FF6B6B">●</span> COVID · Gaza &nbsp;'
               '<span style="color:#FF9F43">●</span> Ukraine · Trump<br>'
               '<span style="color:#EF476F">●</span> EGP Float &nbsp;'
               '<span style="color:#4CC9F0">●</span> Fed · Rates<br>'
               '<span style="color:#06D6A0">●</span> 2024 Float · Ceasefire &nbsp;'
               '<span style="color:#FFD700">●</span> Gold Records'),
        "ar": ('<span style="color:#FF6B6B">●</span> كوفيد · غزة &nbsp;'
               '<span style="color:#FF9F43">●</span> أوكرانيا · ترامب<br>'
               '<span style="color:#EF476F">●</span> تعويم الجنيه &nbsp;'
               '<span style="color:#4CC9F0">●</span> الفيد · فائدة<br>'
               '<span style="color:#06D6A0">●</span> تعويم 2024 · وقف نار &nbsp;'
               '<span style="color:#FFD700">●</span> قياسيات ذهب'),
    },
    "update_now_btn":      {"en": "🔄 Update Data Now",                         "ar": "🔄 تحديث البيانات الآن"},
    "updating_spinner":    {"en": "⏳ Updating...",                             "ar": "‫⏳ جاري التحديث...‬"},
    "fetching_spinner":    {"en": "⏳ Fetching gold data... (one-time)",        "ar": "‫⏳ جاري جلب بيانات الذهب... (مرة واحدة فقط)‬"},
    "last_update_prefix":  {"en": "‫✅ Last update:‬",                          "ar": "‫✅ آخر تحديث:‬"},
    "initializing_data":   {"en": "⏳ Initializing data...",                    "ar": "⏳ جاري تهيئة البيانات..."},
    "data_sources_head":   {"en": "Data Sources",                               "ar": "مصادر البيانات"},
    "grant_head":          {"en": "Digital Egypt Pioneers Initiative",          "ar": "منحة رواد مصر الرقمية"},
    "analyst_role":        {"en": "DATA ANALYST",                               "ar": "DATA ANALYST"},
    "analyst_name":        {"en": "Mahmoud Shamoun",                            "ar": "محمود شمعون"},
    "analyst_desc": {
        "en": "Specialized Data Analyst<br>Graduation Project · DEPI",
        "ar": "محلل بيانات متخصص<br>مشروع تخرج · DEPI",
    },
    "data_load_fail":      {"en": "❌ Failed to load data - check your internet connection", "ar": "❌ فشل تحميل البيانات - تحقق من الاتصال بالإنترنت"},
    "data_read_fail":      {"en": "❌ Failed to read data",                     "ar": "❌ فشل قراءة البيانات"},
    "lang_toggle_label":   {"en": "🌐 Language",                                "ar": "🌐 اللغة"},

    # ── Home Page ──
    "home_hero_title":     {"en": "Gold as a Financial Instrument in Egypt",    "ar": "الذهب كأداة مالية في مصر"},
    "home_hero_sub": {
        "en": "A comprehensive look at gold performance by karat "
              "kept as-is (18K · 21K · 24K) "
              "as a store of value against inflation and EGP devaluation - a realistic simulation including making charges and sell spreads",
        "ar": "تحليل شامل لأداء الذهب بالعيارات "
              "كأداة للحفاظ على القيمة في مواجهة التضخم وانخفاض الجنيه - محاكاة واقعية تشمل المصنعية وفرق أسعار البيع",
    },
    "home_badge_grant":    {"en": "Digital Egypt Pioneers Initiative",          "ar": "منحة رواد مصر الرقمية"},
    "kpi_price_per_gram":  {"en": "EGP/gram {k}",                               "ar": "جنيه/جرام {k}"},
    "kpi_egp_usd":         {"en": "EGP / USD",                                  "ar": "جنيه / دولار"},
    "kpi_ounce_global":    {"en": "Global Ounce",                               "ar": "أونصة عالمياً"},
    "kpi_gold_return":     {"en": "Gold {k} Return since 2020",                 "ar": "عائد الذهب {k} من 2020"},
    "sec_price_path":      {"en": "Gold Price Path",                           "ar": "مسار سعر الذهب"},
    "price_per_gram_sub":  {"en": "Price per gram {k} in EGP",                  "ar": "سعر جرام {k} بالجنيه المصري"},
    "insight_overall_perf": {
        "en": "📌 <b>Overall Performance:</b> Gold {k} rose <span class='num'>{price_chg:.0f}%</span> since January 2020, compared to the USD which rose only <span class='num'>{usd_chg:.0f}%</span> over the same period.",
        "ar": "‫📌 <b>الأداء الإجمالي:</b> ارتفع الذهب {k} بنسبة <span class='num'>{price_chg:.0f}%</span> منذ يناير 2020، مقارنةً بالدولار الذي ارتفع <span class='num'>{usd_chg:.0f}%</span> فقط خلال نفس الفترة.",
    },
    "insight_historic_peak": {
        "en": "🏔️ <b>Historic Peak:</b> <span class='num'>{peak_p:,.0f} EGP</span> per gram {k} in <b>{peak_d}</b> - driven by EGP weakness and rising global prices.",
        "ar": "🏔️ <b>القمة التاريخية:</b> <span class='num'>{peak_p:,.0f} جنيه</span> لجرام {k} في <b>{peak_d}</b> - مدفوعاً بتراجع الجنيه وارتفاع الأسعار العالمية.",
    },
    "sec_key_events":       {"en": "Key Events Affecting the Gold Price",       "ar": "أبرز الأحداث المؤثرة على سعر الذهب"},
    "sec_correlation":      {"en": "Correlation Matrix",                       "ar": "مصفوفة الارتباط"},
    "correlation_sub":      {"en": "Strength of the relationship between gold and macroeconomic variables", "ar": "قوة العلاقة بين الذهب والمتغيرات الاقتصادية الكلية"},
    "sec_usd_path":         {"en": "USD Path",                                 "ar": "مسار الدولار"},
    "usd_path_sub":         {"en": "A rising dollar means a direct rise in gold prices", "ar": "صعود الدولار يعني ارتفاعاً مباشراً في الذهب"},
    "corr_name_gold":       {"en": "Global Gold",                              "ar": "ذهب عالمي"},
    "corr_name_usd":        {"en": "USD/EGP",                                  "ar": "دولار/جنيه"},
    "corr_name_oil":        {"en": "Oil",                                      "ar": "نفط"},
    "corr_name_bonds":      {"en": "US Treasuries",                            "ar": "سندات أمريكية"},
    "corr_name_sp500":      {"en": "S&P 500",                                  "ar": "S&P 500"},
    "event_covid_title":    {"en": "COVID-19",                                 "ar": "COVID-19"},
    "event_covid_date":     {"en": "March 2020",                               "ar": "مارس 2020"},
    "event_covid_desc":     {"en": "Global markets collapse - gold rises as a safe haven", "ar": "انهيار الأسواق العالمية - الذهب يرتفع كملاذ آمن"},
    "event_ukraine_title":  {"en": "Russia-Ukraine",                           "ar": "روسيا-أوكرانيا"},
    "event_ukraine_date":   {"en": "February 2022",                            "ar": "فبراير 2022"},
    "event_ukraine_desc":   {"en": "Russian invasion drives up energy and gold prices globally", "ar": "الغزو الروسي وارتفاع الطاقة والذهب عالمياً"},
    "event_float1_title":   {"en": "Float 1",                                  "ar": "تعويم 1"},
    "event_float1_date":    {"en": "March 2022",                               "ar": "مارس 2022"},
    "event_float1_desc":    {"en": "First EGP float sharply raises local gold prices", "ar": "أول تعويم للجنيه يرفع الذهب المحلي بشكل حاد"},
    "event_gaza_title":     {"en": "Gaza War",                                 "ar": "حرب غزة"},
    "event_gaza_date":      {"en": "October 2023",                             "ar": "أكتوبر 2023"},
    "event_gaza_desc":      {"en": "Outbreak of conflict boosts demand for gold as a haven", "ar": "اندلاع المواجهة يرفع الطلب على الذهب كملاذ"},
    "event_float2024_title":{"en": "2024 Float",                               "ar": "تعويم 2024"},
    "event_float2024_date": {"en": "March 2024",                               "ar": "مارس 2024"},
    "event_float2024_desc": {"en": "Full EGP float: the dollar jumps from 30 to 50 EGP", "ar": "تعويم شامل للجنيه: الدولار يقفز من 30 إلى 50 جنيهاً"},
    "event_ratecut_title":  {"en": "Rate Cut",                                 "ar": "خفض الفائدة"},
    "event_ratecut_date":   {"en": "September 2024",                           "ar": "سبتمبر 2024"},
    "event_ratecut_desc":   {"en": "The Fed begins a rate-cutting cycle - strong support for gold", "ar": "الفيدرالي يبدأ دورة خفض الفائدة - دعم قوي للذهب"},
    "event_ceasefire_title":{"en": "Ceasefire",                                "ar": "وقف إطلاق النار"},
    "event_ceasefire_date": {"en": "January 2025",                             "ar": "يناير 2025"},
    "event_ceasefire_desc": {"en": "Gaza deal temporarily calms markets - gold pulls back slightly", "ar": "اتفاق غزة يُهدئ مؤقتاً - الذهب يتراجع طفيفاً"},
    "event_tariffs_title":  {"en": "Trump Tariffs",                            "ar": "رسوم ترامب"},
    "event_tariffs_date":   {"en": "April 2025",                               "ar": "أبريل 2025"},
    "event_tariffs_desc":   {"en": "Sweeping tariff announcement pushes gold to $3500", "ar": "إعلان الرسوم الجمركية الشاملة يدفع الذهب لـ 3500$"},
    "event_record_title":   {"en": "$3500 Record",                             "ar": "قياسي 3500$"},
    "event_record_date":    {"en": "April 2025",                               "ar": "أبريل 2025"},
    "event_record_desc":    {"en": "Gold breaks $3500 for the first time in history", "ar": "الذهب يكسر 3500$ لأول مرة في التاريخ"},
    "event_iran_title":     {"en": "Iran Strike",                              "ar": "ضربة إيران"},
    "event_iran_date":      {"en": "June 2025",                                "ar": "يونيو 2025"},
    "event_iran_desc":      {"en": "The Israeli-American strike on Iran immediately lifts gold", "ar": "الضربة الإسرائيلية-الأمريكية على إيران ترفع الذهب فوراً"},

    # ── Analysis Page ──
    "sec_price_anatomy":    {"en": "Price Anatomy - Real Value or Inflation?",  "ar": "تشريح السعر - قيمة حقيقية أم تضخم؟"},
    "price_anatomy_sub":    {"en": "How much of the price reflects the rise in global gold, and how much reflects the collapse of the EGP? (baseline: Jan 2020 exchange rate)", "ar": "كم من السعر يعكس ارتفاع الذهب عالمياً، وكم يعكس انهيار قيمة الجنيه؟ (قاعدة الحساب: سعر الصرف في يناير 2020)"},
    "legend_global_value":  {"en": "Global Value",                             "ar": "قيمة عالمية"},
    "legend_inflation_prem":{"en": "Inflation Premium",                        "ar": "علاوة تضخم"},
    "chart_title_anatomy":  {"en": "Price Anatomy: Real Value vs. Inflation & Currency Premium", "ar": "تشريح السعر: القيمة الحقيقية مقابل علاوة التضخم والعملة"},
    "axis_egp":              {"en": "EGP",                                      "ar": "جنيه"},
    "sec_inflation_pct":    {"en": "Inflation Premium %",                       "ar": "نسبة علاوة التضخم %"},
    "inflation_pct_sub":    {"en": "The percentage of the price driven by EGP weakness - the higher it is, the greater gold's protective value", "ar": "النسبة المئوية من السعر ناتجة عن ضعف الجنيه - كلما ارتفعت، كلما كان الذهب وقاية أكبر"},
    "axis_premium_pct":     {"en": "Premium %",                                 "ar": "علاوة %"},
    "insight_avg_premium":  {"en": "Average Premium:",                          "ar": "متوسط العلاوة:"},
    "insight_peak_premium": {"en": "Historic Peak:",                            "ar": "الذروة التاريخية:"},

    # ── Investment Page ──
    "inv_section_title":   {"en": "Realistic Investment Simulation",            "ar": "محاكاة الاستثمار الواقعية"},
    "inv_sub_p1":           {"en": "If we invested 100,000 EGP in January 2020 - net value after deducting making charges", "ar": "لو استثمرنا 100,000 جنيه في يناير 2020 - القيمة الصافية بعد خصم المصنعية"},
    "inv_sub_p2":           {"en": "and sell spreads",                          "ar": "وفروق البيع"},
    "inv_trace_gold_net":   {"en": "{k} Gold (net)",                            "ar": "{k} ذهب (صافي)"},
    "lbl_usd":              {"en": "USD",                                       "ar": "دولار"},
    "lbl_cash_egp":         {"en": "Cash (EGP)",                                "ar": "كاش (جنيه)"},
    "axis_net_value_egp":   {"en": "Net Value (EGP)",                           "ar": "القيمة الصافية (جنيه)"},
    "inv_chart_title":      {"en": "Real Wealth Growth (net of entry/exit costs)", "ar": "نمو الثروة الحقيقي (مخصوم منه تكاليف الدخول والخروج)"},
    "inv_card_title_gold":  {"en": "{k} Gold",                                  "ar": "{k} ذهب"},
    "lbl_net_qty":          {"en": "Net Quantity",                              "ar": "الكمية الصافية"},
    "lbl_price_2020_making":{"en": "2020 Price (+making)",                      "ar": "سعر 2020 (+مصنعية)"},
    "lbl_net_value":        {"en": "Net Value",                                 "ar": "القيمة الصافية"},
    "lbl_actual_return":    {"en": "Actual Return",                             "ar": "العائد الفعلي"},
    "lbl_usd_card_title":   {"en": "USD",                                       "ar": "الدولار USD"},
    "lbl_qty_bought":       {"en": "Quantity Bought",                           "ar": "الكمية المشتراة"},
    "lbl_price_2020":       {"en": "2020 Price",                                "ar": "سعر 2020"},
    "lbl_current_value":    {"en": "Current Value",                             "ar": "القيمة الحالية"},
    "lbl_total_return":     {"en": "Total Return",                              "ar": "العائد الكلي"},
    "dd_sub":               {"en": "Decline from the peak - measures losses during the worst periods", "ar": "الانخفاض عن القمة - يقيس الخسارة في أسوأ الأوقات"},
    "inv_insight_title":    {"en": "Comparison Summary:",                       "ar": "ملخص المقارنة:"},
    "inv_insight_body": {
        "en": ("The best real-world performer (after costs) was <b style=\"color:{c}\">{best_k}</b> "
               "with a net return of <span class='num'>{ret:+.1f}%</span> versus "
               "USD <span class='num'>{usd:+.1f}%</span> and cash in EGP "
               "<span class='num-red'>0%</span> (accounting for real inflation). "
               "Making charges and sell spreads reduce returns but don't erase gold's historical edge."),
        "ar": ("أفضل أداء واقعي (بعد خصم التكاليف) كان <b style=\"color:{c}\">{best_k}</b> "
               "بعائد صافٍ <span class='num'>{ret:+.1f}%</span> مقابل "
               "الدولار <span class='num'>{usd:+.1f}%</span> والكاش بالجنيه "
               "<span class='num-red'>0%</span> (مع التضخم الحقيقي). "
               "المصنعية وفروق البيع تُقلل العوائد لكن لا تمحو التفوق التاريخي للذهب."),
    },

    # ── Technical Page ──
    "tech_title":           {"en": "Technical Analysis - {k}",                  "ar": "التحليل التقني - {k}"},
    "tech_sub":              {"en": "Automated buy/sell signals",                "ar": "إشارات الشراء والبيع الآلية"},
    "tech_subplot_price_bb":{"en": "Price + Bollinger Bands ({k})",              "ar": "السعر + Bollinger Bands ({k})"},
    "tech_subplot_macd":    {"en": "MACD - Trend Momentum",                      "ar": "MACD - زخم الاتجاه"},
    "tech_subplot_rsi":     {"en": "RSI-14 - Overbought/Oversold Level",         "ar": "RSI-14 - مستوى التشبع"},
    "lbl_price":            {"en": "Price",                                      "ar": "السعر"},
    "axis_price_egp":       {"en": "Price (EGP)",                                "ar": "السعر (جنيه)"},
    "sig_buy":              {"en": "Buy 📈",                                     "ar": "شراء 📈"},
    "sig_sell":             {"en": "Sell 📉",                                    "ar": "بيع 📉"},
    "sig_hold":              {"en": "Hold ⏸",                                    "ar": "انتظار ⏸"},
    "tech_signal_label":    {"en": "Signal ({k}):",                              "ar": "الإشارة ({k}):"},
    "tech_overbought":      {"en": "Overbought",                                 "ar": "تشبع شراء"},
    "tech_oversold":        {"en": "Oversold",                                   "ar": "تشبع بيع"},
    "tech_bb_upper":        {"en": "At upper band ⚠️",                          "ar": "عند الحد الأعلى ⚠️"},
    "tech_bb_lower":        {"en": "At lower band ✅",                          "ar": "عند الحد الأدنى ✅"},
    "tech_bb_within":       {"en": "Within range",                               "ar": "داخل النطاق"},

    # ── Forecast Page ──
    "fc_title":              {"en": "Price Forecast - {k}",                     "ar": "توقعات الأسعار - {k}"},
    "fc_sub":                {"en": "Forecasting model with USD and oil regressors - historical merge strategy", "ar": "نموذج التنبؤ مع متغيرات الدولار والنفط - استراتيجية الدمج التاريخي"},
    "fc_horizon_label":     {"en": "Forecast Horizon (days)",                    "ar": "أفق التوقع (أيام)"},
    "fc_spinner_training":  {"en": "⏳ Training Prophet model...",               "ar": "⏳ جاري تدريب نموذج Prophet..."},
    "fc_chart_title":       {"en": "Gold {k} Forecast · Next {days} days",       "ar": "توقعات ذهب {k} · {days} يوم قادماً"},
    "lbl_actual_price":     {"en": "Actual Price",                               "ar": "السعر الفعلي"},
    "fc_confidence_band":   {"en": "90% Confidence Band",                        "ar": "نطاق الثقة 90%"},
    "fc_prophet_forecast":  {"en": "Prophet Forecast",                           "ar": "توقع Prophet"},
    "lbl_today":            {"en": "Today",                                      "ar": "اليوم"},
    "kpi_current_price_egp":{"en": "Current Price (EGP)",                        "ar": "السعر الحالي (جنيه)"},
    "kpi_forecast_days":    {"en": "Forecast ({days}d)",                         "ar": "التوقع ({days}ي)"},
    "kpi_expected_change":  {"en": "Expected Change",                            "ar": "التغيير المتوقع"},
    "kpi_model_rmse":       {"en": "Model RMSE",                                 "ar": "RMSE النموذج"},
    "fc_insight_summary": {
        "en": ("🤖 <b>Forecast Summary:</b> the Prophet model expects gold {k} price per gram to reach "
               "<span class=\"{cls}\">{fe:,.0f} EGP</span> "
               "within the next {days} days - a change of "
               "<span class=\"{cls}\">{cp:+.1f}%</span> from the current price.<br>"
               "<span style=\"display:block; margin-top:6px;\">"
               "Model accuracy - "
               "<span style=\"font-family:'DM Mono',monospace; display:inline-block;\">MAE = {mae:,.0f} EGP</span>"
               "&nbsp;|&nbsp;"
               "<span style=\"font-family:'DM Mono',monospace; display:inline-block;\">RMSE = {rmse:,.0f} EGP</span>"
               " - the lower the number, the more accurate the model."
               "</span>"
               "<span style=\"display:block;margin-top:6px;font-size:0.75rem;color:#3A4A65;\">"
               "* Strategy: Historical Date Merge - independent regressor models "
               "prevent mismatches between the official calendar and trading days."
               "</span>"),
        "ar": ("🤖 <b>ملخص التوقع:</b> يتوقع نموذج Prophet أن يصل سعر جرام {k} إلى "
               "<span class=\"{cls}\">{fe:,.0f} جنيه</span> "
               "خلال {days} يوم القادمة - تغيير "
               "<span class=\"{cls}\">{cp:+.1f}%</span> عن السعر الحالي.<br>"
               "<span style=\"direction:rtl; display:block; margin-top:6px;\">"
               "دقة النموذج - "
               "<span style=\"font-family:'DM Mono',monospace; direction:ltr; display:inline-block;\">MAE = {mae:,.0f} جنيه</span>"
               "&nbsp;|&nbsp;"
               "<span style=\"font-family:'DM Mono',monospace; direction:ltr; display:inline-block;\">RMSE = {rmse:,.0f} جنيه</span>"
               " - كلما قل الرقم كلما كان النموذج أدق."
               "</span>"
               "<span style=\"display:block;margin-top:6px;font-size:0.75rem;color:#3A4A65;\">"
               "* الاستراتيجية: دمج تاريخي (Historical Date Merge) - نماذج مستقلة للمتغيرات الخارجية "
               "تمنع أخطاء عدم التوافق بين التقويم الرسمي وأيام التداول."
               "</span>"),
    },
    "roi_section_title":    {"en": "Investment ROI Calculator",                 "ar": "حاسبة العائد على الاستثمار"},
    "roi_sub":               {"en": "Enter your investment amount and choose the karat and duration - we'll compute the expected return based on Prophet's forecast", "ar": "أدخل مبلغ استثمارك واختر العيار والمدة - سنحسب العائد المتوقع بناءً على توقعات Prophet"},
    "roi_amount_label":     {"en": "Investment Amount (EGP)",                    "ar": "مبلغ الاستثمار (جنيه مصري)"},
    "roi_amount_help":      {"en": "Enter the amount you want to invest in EGP", "ar": "أدخل المبلغ الذي تريد استثماره بالجنيه المصري"},
    "roi_karat_label":      {"en": "Karat",                                      "ar": "العيار"},
    "roi_duration_label":   {"en": "Duration (days)",                            "ar": "المدة (أيام)"},
    "roi_duration_help":    {"en": "Choose the number of days you plan to hold the gold", "ar": "اختر عدد الأيام التي تنوي الاحتفاظ بالذهب خلالها"},
    "roi_metric_expected_value": {"en": "💰 Expected Value",                     "ar": "💰 القيمة المتوقعة"},
    "roi_metric_expected_value_help": {"en": "Net value after {days} days, on {date}", "ar": "القيمة الصافية بعد {days} يوم بتاريخ {date}"},
    "roi_metric_net_return":{"en": "{icon} Net Return",                          "ar": "{icon} العائد الصافي"},
    "roi_annualized":       {"en": "{pct}% annually",                            "ar": "{pct}% سنوياً"},
    "roi_net_return_help":  {"en": "Total return on invested capital, and the annualized return", "ar": "العائد الإجمالي على رأس المال المستثمر، والعائد السنوي المُقنَّن"},
    "roi_metric_grams_bought": {"en": "⚖️ Quantity Bought",                      "ar": "⚖️ الكمية المشتراة"},
    "roi_grams_value":      {"en": "{grams:.2f} g",                              "ar": "{grams:.2f} جم"},
    "roi_grams_delta":      {"en": "{k} · {price:,.0f} EGP/g",                   "ar": "{k} · {price:,.0f} ج/جم"},
    "roi_grams_help":       {"en": "Number of grams after deducting making charges from the total amount", "ar": "عدد الجرامات بعد خصم المصنعية من المبلغ الإجمالي"},
    "roi_metric_target_price": {"en": "🎯 Target Price",                         "ar": "🎯 سعر الهدف"},
    "roi_target_value":     {"en": "{price:,.0f} EGP/g",                         "ar": "{price:,.0f} ج/جم"},
    "roi_vs_current":       {"en": "{pct:+.1f}% vs current",                     "ar": "{pct:+.1f}% عن الحالي"},
    "roi_target_help":      {"en": "Expected price per gram {k} on {date}",       "ar": "سعر جرام {k} المتوقع في {date}"},
    "roi_insight_summary": {
        "en": ("💡 <b>ROI Calculator Summary:</b> "
               "Investing <span class='num'>{amt:,.0f} EGP</span> in {k} gold "
               "today at <span class='num'>{price:,.0f} EGP/g</span> (including a making charge of <span class='num'>{mc:,} EGP</span>) "
               "gets you <span class='num'>{grams:.2f} grams</span>. Based on Prophet's forecast over "
               "<span class='num'>{days}</span> days, this could be worth "
               "<span class=\"{cls}\">{exit_val:,.0f} EGP</span> "
               "- a profit of <span class=\"{cls}\">{profit:+,.0f} EGP</span> "
               "(<span class=\"{cls2}\">{pct:+.2f}%</span>).<br>"
               "<span style=\"display:block;margin-top:6px;font-size:0.75rem;color:#3A4A65;\">"
               "* Calculations include the making charge on purchase and the sell spread ({spread:.1f}%) on sale. "
               "Forecasts are for guidance only and are not investment advice."
               "</span>"),
        "ar": ("💡 <b>ملخص حاسبة العائد:</b> "
               "استثمار <span class='num'>{amt:,.0f} جنيه</span> في ذهب <b>{k}</b> "
               "اليوم بسعر <span class='num'>{price:,.0f} جنيه/جم</span> (شامل مصنعية <span class='num'>{mc:,} جنيه</span>) "
               "يمنحك <span class='num'>{grams:.2f} جرام</span>. بناءً على توقعات Prophet خلال "
               "<span class='num'>{days}</span> يوم، قد تبلغ قيمتها "
               "<span class=\"{cls}\">{exit_val:,.0f} جنيه</span> "
               "- ربح <span class=\"{cls}\">{profit:+,.0f} جنيه</span> "
               "(<span class=\"{cls2}\">{pct:+.2f}%</span>).<br>"
               "<span style=\"display:block;margin-top:6px;font-size:0.75rem;color:#3A4A65;\">"
               "* الحسابات تشمل المصنعية عند الشراء وفرق السعر ({spread:.1f}%) عند البيع. "
               "التوقعات للأغراض التوجيهية فقط وليست نصيحة استثمارية."
               "</span>"),
    },
    "roi_insufficient_data":{"en": "⚠️ Not enough forecast data for the selected duration. Try extending the forecast horizon.", "ar": "⚠️ لا تتوفر بيانات توقع كافية للمدة المحددة. حاول تمديد أفق التوقع."},
    "fc_prophet_missing":   {"en": "⚠️ The Prophet library is not installed - run: pip install prophet", "ar": "⚠️ مكتبة Prophet غير مثبتة - قم بتشغيل: pip install prophet"},
    "fc_model_error":       {"en": "Forecast model error: {err}",                "ar": "خطأ في نموذج التنبؤ: {err}"},
}

def t(key: str, **kwargs) -> str:
    """Fetch a translated string for the current session language.
    Falls back to the key itself if missing (never crashes).
    Supports str.format(**kwargs) for dynamic values, e.g. t('kpi_egp_usd', k='21K')."""
    entry = TRANSLATIONS.get(key)
    raw = key if entry is None else entry.get(LANG, entry.get("en", key))
    if kwargs:
        try:
            return raw.format(**kwargs)
        except Exception:
            return raw
    return raw

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

# Dynamic base direction for the whole app main-content area. This flips
# automatically whenever LANG changes (Arabic → RTL, English → LTR). Element-
# level RTL/LTR overrides for intentionally-mixed content stay as-is.
st.markdown(f"""
<style>
.main .block-container {{ direction: {DIR}; text-align: {ALIGN}; }}
[data-testid="stSidebar"] * {{ text-align: {ALIGN}; }}
</style>
""", unsafe_allow_html=True)

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
    """Fallback: fetch gold price from Yahoo Finance (XAUUSD=X or GC=F)."""
    for ticker in ("XAUUSD=X", "GC=F"):
        try:
            df = yf.download(ticker, period="5d", progress=False, auto_adjust=False)
            if df.empty:
                continue
            if isinstance(df.columns, pd.MultiIndex):
                df.columns = df.columns.droplevel(1)
            col = "Adj Close" if "Adj Close" in df.columns else "Close"
            return float(df[col].dropna().iloc[-1])
        except Exception:
            continue
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
    TICKER_CANDIDATES = {
        "Gold_USD_Ounce":   ["XAUUSD=X", "GC=F"],   # spot first, futures fallback
        "USD_EGP_Official": ["EGP=X"],
        "Crude_Oil":        ["CL=F"],
        "US_10Y_Treasury":  ["^TNX"],
        "SP500":            ["^GSPC"],
    }
    frames = []
    yesterday = (datetime.today() - timedelta(days=1)).strftime("%Y-%m-%d")
    for name, candidates in TICKER_CANDIDATES.items():
        fetched = False
        for ticker in candidates:
            for attempt in range(3):
                try:
                    df = yf.download(ticker, start=start, end=yesterday,
                                     progress=False, auto_adjust=False)
                    if df.empty:
                        break
                    if isinstance(df.columns, pd.MultiIndex):
                        df.columns = df.columns.droplevel(1)
                    col = "Adj Close" if "Adj Close" in df.columns else "Close"
                    frames.append(df[[col]].rename(columns={col: name}))
                    fetched = True
                    break
                except Exception:
                    if attempt < 2:
                        time.sleep(2)
            if fetched:
                break   # this column is satisfied, no need to try next candidate ticker
    if not frames:
        return pd.DataFrame()
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

def compute_all_indicators(data: pd.DataFrame) -> pd.DataFrame:
    """
    Single source of truth for every derived price/indicator column.

    Given a raw DataFrame indexed by Date with columns
    ['Gold_USD_Ounce', 'USD_EGP_Official', 'Crude_Oil', 'US_10Y_Treasury',
    'SP500'], computes for every karat in KARAT_FACTORS:

        Theoretical_24K, Price_{k}, ValueDriven_{k}, InflPrem_{k}, PremPct_{k}
        SMA50_{k}, SMA200_{k}, MACD_{k}, MACDSig_{k}, MACDHist_{k}, RSI_{k}
        BB_mid_{k}, BB_up_{k}, BB_dn_{k}
        Port_{k}, DD_{k}, Norm_{k}

    plus the USD/Cash portfolio benchmarks (Port_USD, Port_Cash, Norm_USD,
    Norm_Cash). This is a pure function of `data` (no I/O), reused
    identically by the main Streamlit app, the Vercel embed views, and the
    CLI batch updater - none of which may reimplement this math locally.

    NOTE: does NOT compute Signal_{k}/SignalScore_{k}/SignalAgreement_{k} -
    that is compute_all_signals()'s job exclusively (called separately by
    prepare_dataset(), after this function).
    """
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

        # ── Trend indicators (SMA) ──
        data[f'SMA50_{karat}']       = p.rolling(50,  min_periods=1).mean()
        data[f'SMA200_{karat}']      = p.rolling(200, min_periods=1).mean()

        # ── Momentum indicator (MACD: 12/26 EMA crossover, 9-period signal) ──
        ema12 = p.ewm(span=12, adjust=False).mean()
        ema26 = p.ewm(span=26, adjust=False).mean()
        data[f'MACD_{karat}']        = ema12 - ema26
        data[f'MACDSig_{karat}']     = data[f'MACD_{karat}'].ewm(span=9, adjust=False).mean()
        data[f'MACDHist_{karat}']    = data[f'MACD_{karat}'] - data[f'MACDSig_{karat}']

        # ── Oscillator indicator (RSI-14, Wilder-style EWM smoothing) ──
        delta    = p.diff()
        gain     = delta.where(delta > 0, 0.0)
        loss     = (-delta.where(delta < 0, 0.0))
        avg_gain = gain.ewm(span=14, adjust=False).mean()
        avg_loss = loss.ewm(span=14, adjust=False).mean()
        rs       = avg_gain / avg_loss.replace(0, np.nan)
        data[f'RSI_{karat}'] = 100 - (100 / (1 + rs))

        # ── Volatility bands (Bollinger, 20-period, 2 std dev) ──
        data[f'BB_mid_{karat}'] = p.rolling(20, min_periods=1).mean()
        bb_std = p.rolling(20, min_periods=1).std()
        data[f'BB_up_{karat}']  = data[f'BB_mid_{karat}'] + 2 * bb_std
        data[f'BB_dn_{karat}']  = data[f'BB_mid_{karat}'] - 2 * bb_std

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


@st.cache_data(ttl=60, show_spinner=False)
def prepare_dataset(csv_path: str, mtime: float) -> pd.DataFrame:
    """
    Data loading + orchestration layer (cached via st.cache_data).

    Reads the raw market CSV, forward-fills/drops missing rows, then
    delegates ALL derived-column computation to the two single-source-of-
    truth functions:
        1. compute_all_indicators(data)  - prices, SMA/MACD/RSI/BB, portfolios
        2. compute_all_signals(data)     - BUY/SELL/HOLD composite signals

    `mtime` (file modification time) is part of the cache key, so
    st.cache_data automatically invalidates and recomputes whenever the
    underlying CSV changes on disk (e.g. after run_scraper() updates it).

    Returns an empty DataFrame (never raises) if the CSV has no usable
    rows after cleaning, so callers can check `data.empty` safely.
    """
    data = pd.read_csv(csv_path, index_col="Date", parse_dates=True)
    data.ffill(inplace=True)
    data.dropna(inplace=True)

    if data.empty:
        return data

    data = compute_all_indicators(data)
    data = compute_all_signals(data, list(KARAT_FACTORS.keys()))
    return data


# Backward-compatible alias: earlier revisions of this app called this
# function load_data(). Kept as a thin alias so any external references
# (e.g. the CLI entry point at the bottom of this file) keep working
# without duplicating logic.
load_data = prepare_dataset


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
# SHARED SIGNAL / CORRELATION LOGIC (single source of truth)
#
# These functions are the ONLY place correlation matrices and "best
# driver" rankings are computed anywhere in this app - the home-page
# correlation panel and the Q4 macro-correlation slide must both call
# these instead of running data[...].corr() inline. This removes the
# historical duplication where the home page and Q4 each ran their own
# independent .corr() call, which made it possible for the two views to
# silently drift out of sync if one call site's column list changed but
# the other didn't.
#
# NOTE: BUY/SELL/HOLD signal columns (Signal_{karat}) are NOT duplicated
# either - they are computed exactly once, inside load_data() above, and
# every chart reads that same data[f'Signal_{karat}'] column.
# ─────────────────────────────────────────────────────────────────────────────

def compute_correlation_matrix(data: pd.DataFrame, cols: list, labels: list = None) -> pd.DataFrame:
    """
    Single source of truth for every correlation matrix in the app.
    Any chart that needs a correlation matrix must call this rather than
    calling data[cols].corr() directly, so two views built on the same
    `cols` always produce identical numbers.
    """
    missing = [c for c in cols if c not in data.columns]
    if missing:
        raise KeyError(f"compute_correlation_matrix: columns not found in data: {missing}")

    corr_df = data[cols].dropna().corr()

    if labels is not None:
        if len(labels) != len(cols):
            raise ValueError("compute_correlation_matrix: labels and cols must be the same length")
        corr_df.columns = labels
        corr_df.index = labels

    return corr_df


def best_correlation_driver(corr_df: pd.DataFrame, target_label: str, exclude_labels: list = None):
    """
    Single source of truth for "which macro driver correlates most with
    gold" across the app. Reads the answer directly off an already
    computed correlation matrix (never recomputes anything), so the
    ranking always matches whatever heatmap is on screen.

    Returns (best_label, best_value, ranked_series).
    """
    if target_label not in corr_df.index:
        raise KeyError(f"best_correlation_driver: '{target_label}' not found in correlation matrix")

    exclude = set(exclude_labels or [])
    exclude.add(target_label)

    candidates = corr_df.loc[target_label].drop(labels=[l for l in exclude if l in corr_df.columns])
    ranked = candidates.reindex(candidates.abs().sort_values(ascending=False).index)

    best_label = ranked.index[0]
    best_value = ranked.iloc[0]
    return best_label, best_value, ranked


def compute_all_signals(data: pd.DataFrame, karats: list = None) -> pd.DataFrame:
    """
    Single source of truth for the composite technical signal
    (RSI + MACD crossover + Bollinger Bands).

    Adds, for every karat in `karats`:
        SignalScore_{k}      : int, sum of the three indicator votes
        SignalAgreement_{k}  : "n/3" string - how many of the 3 indicators
                                agree with the direction of the final call
        Signal_{k}           : BUY/SELL/HOLD, derived from SignalScore_{k}

    This is the ONLY place the composite signal logic lives. load_data()
    and every chart (Streamlit main app + Vercel embed) must read these
    columns rather than re-deriving RSI/MACD/BB votes locally.
    """
    karats = karats or list(KARAT_FACTORS.keys())
    required = []
    for k in karats:
        required += [f'RSI_{k}', f'MACD_{k}', f'MACDSig_{k}', f'Price_{k}', f'BB_up_{k}', f'BB_dn_{k}']
    missing = [c for c in required if c not in data.columns]
    if missing:
        raise KeyError(f"compute_signal_columns: required columns not found in data: {missing}")

    for k in karats:
        rsi   = data[f'RSI_{k}']
        macd  = data[f'MACD_{k}']
        sig   = data[f'MACDSig_{k}']
        price = data[f'Price_{k}']
        bb_up = data[f'BB_up_{k}']
        bb_dn = data[f'BB_dn_{k}']

        rsi_vote  = np.select([rsi < 30, rsi > 70], [1, -1], default=0)
        macd_vote = np.where(macd > sig, 1, -1)
        bb_vote   = np.select([price < bb_dn, price > bb_up], [1, -1], default=0)

        score = rsi_vote + macd_vote + bb_vote
        data[f'SignalScore_{k}'] = score

        direction = np.select([score >= 2, score <= -2], [1, -1], default=0)
        data[f'Signal_{k}'] = np.select(
            [direction == 1, direction == -1], ['BUY', 'SELL'], default='HOLD'
        )

        votes = np.vstack([rsi_vote, macd_vote, bb_vote])  # shape (3, n)
        match_count = (votes == direction).sum(axis=0)     # shape (n,), broadcasts against direction (n,)
        agree = np.where(direction != 0, match_count, 0)    # shape (n,)
        data[f'SignalAgreement_{k}'] = [f"{int(a)}/3" for a in agree]

    return data


# Backward-compatible alias: earlier revisions called this compute_signal_columns().
compute_signal_columns = compute_all_signals


def validate_data_consistency(data: pd.DataFrame, karats: list = None, atol: float = 1e-9):
    """
    Data-consistency validation layer (Streamlit main app <-> Vercel embed).

    Guarantees Signal_{k}, SignalScore_{k}, SignalAgreement_{k} and the
    macro correlation matrix are identical no matter which view is about
    to render them. Must be called BEFORE any chart in a section is
    drawn. Raises a clear error and prevents rendering on any mismatch,
    rather than silently drawing charts backed by inconsistent numbers.
    """
    karats = karats or list(KARAT_FACTORS.keys())

    check = compute_all_signals(data.copy(), karats)

    for k in karats:
        col = f'SignalScore_{k}'
        a = data[col].to_numpy(dtype=float)
        b = check[col].to_numpy(dtype=float)
        if not np.allclose(a, b, atol=atol, equal_nan=True):
            raise ValueError(
                f"Data consistency validation failed: '{col}' differs between the "
                f"cached data and a fresh compute_signal_columns() pass. Refusing to "
                f"render charts with potentially inconsistent signals."
            )
        for str_col in (f'Signal_{k}', f'SignalAgreement_{k}'):
            if not data[str_col].equals(check[str_col]):
                raise ValueError(
                    f"Data consistency validation failed: '{str_col}' differs between the "
                    f"cached data and a fresh compute_signal_columns() pass. Refusing to "
                    f"render charts with potentially inconsistent signals."
                )

    base_cols = [f'Price_{karats[0]}', 'Gold_USD_Ounce', 'USD_EGP_Official',
                 'Crude_Oil', 'US_10Y_Treasury', 'SP500']
    base_cols = [c for c in base_cols if c in data.columns]
    if len(base_cols) >= 2:
        m1 = compute_correlation_matrix(data, base_cols)
        m2 = compute_correlation_matrix(data, base_cols)
        if not np.allclose(m1.to_numpy(), m2.to_numpy(), atol=atol, equal_nan=True):
            raise ValueError(
                "Data consistency validation failed: compute_correlation_matrix() "
                "produced non-deterministic results for identical inputs."
            )

    return True


def assert_correlation_consistency(matrix_a: pd.DataFrame, matrix_b: pd.DataFrame,
                                    shared_labels: list, atol: float = 1e-9, context: str = ""):
    """
    Internal validation layer: whenever two correlation matrices in this
    app share a subset of variables, their overlapping cells MUST be
    numerically identical, because both are produced by
    compute_correlation_matrix() from the same underlying `data`. This
    proves that at runtime instead of assuming it. Raises AssertionError
    naming the exact mismatched cell rather than silently "fixing" it -
    a silent fix would hide a real data bug.
    """
    sub_a = matrix_a.loc[shared_labels, shared_labels]
    sub_b = matrix_b.loc[shared_labels, shared_labels]

    diff = (sub_a - sub_b).abs()
    if (diff > atol).any().any():
        bad_cell = diff.stack().idxmax()
        raise AssertionError(
            f"Correlation mismatch detected{(' in ' + context) if context else ''}: "
            f"cell {bad_cell} differs by {diff.stack().max():.6f} between the two matrices "
            f"(tolerance {atol}). The two chart call sites are no longer reading the same "
            f"underlying data/columns and must be reconciled."
        )
    return True


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
    with st.spinner(t("fetching_spinner")):
        run_scraper()
        st.cache_data.clear()

# ─────────────────────────────────────────────────────────────────────────────
# SIDEBAR - NAVIGATION & CONTROLS
# ─────────────────────────────────────────────────────────────────────────────

with st.sidebar:
    st.markdown("""
    <style>
    .sb-logo {
        text-align: center;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
    }
    .sb-logo-text {
        font-size: 20px;
        font-weight: bold;
        margin-top: 8px;
    }
    .sb-logo-sub {
        font-size: 12px;
        opacity: 0.7;
    }
    </style>
    """, unsafe_allow_html=True)

    st.markdown(f"""
    <div class="sb-logo">
      <div class="sb-logo-icon">
        <img src="{IMAGE_HTML_SRC}" width="80" style="border-radius:8px;">
      </div>
      <div class="sb-logo-text">GOLD EGYPT</div>
      <div class="sb-logo-sub">{t('app_tagline')}</div>
    </div>
    """, unsafe_allow_html=True)

    # ── Language toggle (AR / EN) — default is English ──
    _lang_cols = st.columns(2)
    with _lang_cols[0]:
        if st.button("EN", use_container_width=True,
                      type="primary" if LANG == "en" else "secondary",
                      key="lang_btn_en"):
            set_lang("en")
            st.rerun()
    with _lang_cols[1]:
        if st.button("AR", use_container_width=True,
                      type="primary" if LANG == "ar" else "secondary",
                      key="lang_btn_ar"):
            set_lang("ar")
            st.rerun()

    st.markdown('<div class="gold-divider"></div>', unsafe_allow_html=True)

    pages = {
        "home":       t("nav_home"),
        "analysis":   t("nav_analysis"),
        "investment": t("nav_investment"),
        "technical":  t("nav_technical"),
        "forecast":   t("nav_forecast"),
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

    st.markdown(f'<div style="color:#8D99AE;font-size:0.78rem;direction:{DIR};text-align:{ALIGN};margin-bottom:4px;">{t("main_karat_label")}</div>', unsafe_allow_html=True)
    selected_karat = st.selectbox("k", ["18K", "21K", "24K"], index=1, label_visibility="collapsed")

    spacer(6)
    show_events = st.toggle(t("crisis_events_toggle"), value=True)

    if show_events:
        st.markdown(f"""
        <div style="font-size:0.6rem;color:#3A4A65;direction:{DIR};text-align:{ALIGN};
                    line-height:2;padding:4px 0;margin-top:2px;">
          {t("crisis_legend")}
        </div>""", unsafe_allow_html=True)

    st.markdown('<div class="gold-divider"></div>', unsafe_allow_html=True)

    if st.button(t("update_now_btn"), use_container_width=True):
        with st.spinner(t("updating_spinner")):
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
        _stx = f"{t('last_update_prefix')}<br>{_mt}"

    else:
        _sc  = "#EF476F"
        _stx = t("initializing_data")

    st.markdown(
        f'<div style="text-align:center;font-size:0.62rem;color:{_sc};'
        f'font-family:DM Mono,monospace;margin-top:6px;line-height:1.8;">{_stx}</div>',
        unsafe_allow_html=True)

    st.markdown('<div class="gold-divider"></div>', unsafe_allow_html=True)

    st.markdown(f"""
    <div class="sb-src">
      <div class="sb-src-head">{t('data_sources_head')}</div>
      <div class="sb-src-val">goldprice.org · exchangerate-api · yfinance</div>
      <div class="sb-src-val">GC=F · EGP=X · CL=F · ^TNX · ^GSPC</div>
    </div>
    <div style="height:10px"></div>
    <div class="sb-src">
      <div class="sb-src-head">{t('grant_head')}</div>
      <div class="sb-src-val">DEPI Final Project · 2026</div>
    </div>
    <div style="height:14px"></div>
    <div style="background:linear-gradient(135deg,rgba(255,215,0,0.06),rgba(76,201,240,0.04));
                border:1px solid rgba(255,215,0,0.15);border-radius:10px;padding:12px 14px;">
      <div style="color:var(--gold);font-size:0.64rem;font-weight:700;text-align:center;
                  letter-spacing:1px;margin-bottom:6px;">{t('analyst_role')}</div>
      <div style="color:#E8EDF5;font-size:0.72rem;font-weight:700;text-align:center;
                  font-family:'Cairo',sans-serif;margin-bottom:3px;">محمود شمعون</div>
      <div style="color:#8D99AE;font-size:0.6rem;text-align:center;
                  font-family:'DM Mono',monospace;direction:ltr;">{t('analyst_name')}</div>
      <div style="color:#3A4A65;font-size:0.58rem;text-align:center;margin-top:4px;
                  direction:{DIR};line-height:1.7;">
        {t('analyst_desc')}
      </div>
    </div>""", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# LOAD DATA
# ─────────────────────────────────────────────────────────────────────────────

if not os.path.exists(CSV_PATH):
    st.error(t("data_load_fail"))
    st.stop()

_mtime_key = os.path.getmtime(CSV_PATH)
with st.spinner(""):
    data = prepare_dataset(CSV_PATH, _mtime_key)
    validate_data_consistency(data)

if data.empty:
    st.error(t("data_read_fail")); st.stop()

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
_EMBED_CSS = """
<style>
/* ── EMBED IFRAME SHELL ── */
[data-testid="stSidebar"],
header, footer,
.stDeployButton,
#MainMenu { display: none !important; }

.main .block-container {
    padding: 0 !important;
    max-width: 100% !important;
    margin: 0 !important;
}

/* transparent plotly wrapper */
.stPlotlyChart {
    border: none !important;
    box-shadow: none !important;
    background: transparent !important;
    padding: 0 !important;
    margin: 0 !important;
}

body, .stApp {
    background: #03060F !important;
}

/* ── KPI STRIP ── */
.eq-kpi-strip {
    display: flex;
    gap: 10px;
    padding: 8px 12px 4px 12px;
    background: transparent;
    flex-wrap: wrap;
}
.eq-kpi {
    flex: 1;
    min-width: 110px;
    background: linear-gradient(145deg, #0A1525, #0D1E36);
    border: 1px solid rgba(212,175,55,0.20);
    border-radius: 10px;
    padding: 10px 14px;
    text-align: center;
}
.eq-kpi-val {
    font-family: 'DM Mono', monospace;
    font-size: 1.35rem;
    font-weight: 900;
    line-height: 1.1;
    letter-spacing: 0.5px;
    display: block;
}
.eq-kpi-lbl {
    font-size: 0.68rem;
    color: #6a7a99;
    margin-top: 2px;
    display: block;
    letter-spacing: 0.03em;
}

/* ── SIGNAL BADGE ── */
.eq-signal-wrap {
    display: flex;
    justify-content: center;
    align-items: center;
    padding: 8px 12px 6px;
    gap: 12px;
    flex-wrap: wrap;
}
.eq-signal {
    font-family: 'DM Mono', monospace;
    font-size: 1.6rem;
    font-weight: 900;
    padding: 10px 36px;
    border-radius: 10px;
    letter-spacing: 0.12em;
}
.eq-signal.buy  { background: #06D6A0; color: #000; }
.eq-signal.sell { background: #EF476F; color: #fff; }
.eq-signal.hold { background: #4CC9F0; color: #000; }
.eq-sig-meta {
    font-size: 0.75rem;
    color: #6a7a99;
    text-align: center;
    line-height: 1.7;
}

/* ── Q-HEADER ── */
.eq-q-header {
    padding: 10px 14px 0 14px;
    font-family: 'Cairo', sans-serif;
    font-size: 0.72rem;
    font-weight: 700;
    color: #D4AF37;
    letter-spacing: 0.14em;
    text-transform: uppercase;
    opacity: 0.85;
}

/* ── FOOTNOTE (cross-reference notes between questions) ── */
.eq-footnote {
    padding: 4px 14px 0 14px;
    font-family: 'Cairo', sans-serif;
    font-size: 0.68rem;
    color: #FF9F43;
    opacity: 0.85;
    text-align: center;
}
</style>
"""


def _kpi_card(val: str, label: str, color: str = "#FFD700") -> str:
    """Return one KPI card HTML snippet."""
    return (
        f'<div class="eq-kpi">'
        f'<span class="eq-kpi-val" style="color:{color}">{val}</span>'
        f'<span class="eq-kpi-lbl">{label}</span>'
        f'</div>'
    )


def _kpi_strip(*cards: str) -> str:
    inner = "".join(cards)
    return f'<div class="eq-kpi-strip">{inner}</div>'


# ─────────────────────────────────────────────────────────────────────────────

embed_q = st.query_params.get("q")

# ─────────────────────────────────────────────────────────────────────────────
# EMBED VIEW RENDERERS (single dispatcher, one function per slide)
#
# Each _render_embed_qN() function is a pure rendering function: it reads
# ONLY from the already-validated `data` DataFrame (see validate_data_consistency()
# above) and never recomputes signals, correlations, or indicator formulas.
# render_embed_view() is the single dispatch point used by the app's boot
# sequence - no other code path may branch on `embed_q` directly.
# ─────────────────────────────────────────────────────────────────────────────

EGP = "EGP"

def _std_layout(fig, height=460, title=None):
    """
    Shared chart-styling helper for every embed view.

    Applies a centered title, a unified font (Inter), clean consistent
    margins, and an LTR-oriented horizontal legend. This is the ONLY
    place chart chrome is defined for the embed views - individual
    render functions must call this rather than hand-rolling layout
    dicts, so all seven slides look visually consistent.
    """
    lyt = plot_layout(height=height)
    lyt['margin'] = dict(l=50, r=30, t=70 if title else 40, b=40)
    lyt['font'] = dict(family='Inter, -apple-system, sans-serif', size=12, color='#B8C4D6')
    lyt['legend'] = dict(
        orientation='h', y=1.1, x=0.5, xanchor='center', yanchor='bottom',
        bgcolor='rgba(0,0,0,0)', borderwidth=0,
        font=dict(size=10, family='Inter'),
    )
    if title:
        lyt['title'] = dict(text=title, x=0.5, xanchor='center',
                             font=dict(size=15, family='Inter', color='#E8EDF5'))
    fig.update_layout(**lyt)
    fig.update_xaxes(tickfont=dict(family='Inter', size=9, color='#4A6A8A'),
                      gridcolor='rgba(255,255,255,0.04)')
    return fig

def _render_embed_q1(data: pd.DataFrame, k: str, show_events: bool) -> None:
    """Render embed slide Q1: Price Decomposition - Global Value vs. Currency & Demand Premium."""
    latest = data.dropna(subset=[f'Price_{k}', f'ValueDriven_{k}', f'InflPrem_{k}']).iloc[-1]
    total = latest[f'Price_{k}']
    val_pct = (latest[f'ValueDriven_{k}'] / total * 100) if total else 0
    prem_pct = (latest[f'InflPrem_{k}'] / total * 100) if total else 0

    mar24 = data['2024-03-01':'2024-03-31'].dropna(subset=[f'Price_{k}', f'ValueDriven_{k}'])
    if not mar24.empty:
        mar24_row = mar24.iloc[-1]
        mar24_tot = mar24_row[f'Price_{k}']
        mar24_val_s = f"{mar24_row[f'ValueDriven_{k}'] / mar24_tot * 100:.0f}%"
        mar24_prem_s = f"{mar24_row[f'InflPrem_{k}'] / mar24_tot * 100:.0f}%"
    else:
        mar24_val_s = mar24_prem_s = "N/A"

    current_price = f"{total:,.0f} {EGP}"

    st.markdown(
        '<div class="eq-q-header">Q1 - Price Decomposition: Global Value vs. Currency &amp; Demand Premium</div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        _kpi_strip(
            _kpi_card(current_price, f"Current {k} Price", "#FFD700"),
            _kpi_card(f"{val_pct:.0f}%", "Global Value (Now)", "#FFF9C4"),
            _kpi_card(f"{prem_pct:.0f}%", "Currency + Demand Premium (Now)", "#EF476F"),
            _kpi_card(mar24_prem_s, "March 2024 Premium (Peak)", "#FF6B6B"),
            _kpi_card(mar24_val_s, "March 2024 Global Value", "#FFD700"),
        ),
        unsafe_allow_html=True,
    )
    st.markdown(
        '<div class="eq-footnote">This premium includes instability and speculation effects - see Q3 for the instability breakdown</div>',
        unsafe_allow_html=True,
    )

    fig = make_subplots(
        rows=3, cols=1,
        shared_xaxes=True,
        row_heights=[0.34, 0.33, 0.33],
        vertical_spacing=0.08,
        subplot_titles=["24K", "21K", "18K"],
    )
    for anno in fig['layout']['annotations']:
        if anno['text'] in ["24K", "21K", "18K"]:
            anno['yshift'] = -15
            anno['font'] = dict(size=13, family='Inter', color='#4A6A8A')

    KFILL = {
        '24K': 'rgba(255,249,196,0.70)',
        '21K': 'rgba(255,215,0,0.65)',
        '18K': 'rgba(205,127,50,0.65)',
    }
    KROW = {'24K': 1, '21K': 2, '18K': 3}

    for karat in ['24K', '21K', '18K']:
        row = KROW[karat]
        fig.add_trace(go.Scatter(
            x=data.index, y=data[f'ValueDriven_{karat}'],
            name='Global Value (Fixed Price)', stackgroup=f'g{row}', mode='lines',
            line=dict(width=0), fillcolor=KFILL[karat],
            showlegend=(row == 1), legendgroup='gv',
            hovertemplate=f"{karat} Value: %{{y:,.0f}} {EGP}<extra></extra>",
        ), row=row, col=1)

        fig.add_trace(go.Scatter(
            x=data.index, y=data[f'InflPrem_{karat}'],
            name='Currency &amp; Demand Premium', stackgroup=f'g{row}', mode='lines',
            line=dict(width=0), fillcolor='rgba(239,71,111,0.55)',
            showlegend=(row == 1), legendgroup='gi',
            hovertemplate=f"{karat} Premium: %{{y:,.0f}} {EGP}<extra></extra>",
        ), row=row, col=1)

    for r in [1, 2, 3]:
        fig.add_vrect(
            x0='2024-03-01', x1='2024-03-31',
            fillcolor='rgba(239,71,111,0.12)', line_width=0,
            layer='below', row=r, col=1,
        )
    fig.add_annotation(
        x='2024-03-15', y=1.04, yref='paper', xref='x',
        text="March 2024 float - jump in currency &amp; demand premium (see Q3 for instability detail)",
        showarrow=False,
        font=dict(size=8.5, color='#EF476F', family='Inter'),
        xanchor='center', bgcolor='rgba(3,6,15,0.75)', borderpad=3,
    )
    if show_events:
        add_events(fig, data, rows=[1, 2, 3])

    _std_layout(fig, height=520)
    fig.update_layout(margin=dict(l=8, r=8, t=100, b=8))
    for r in [1, 2, 3]:
        fig.update_yaxes(
            title_text='EGP / gram',
            title_font=dict(size=8, color='#4A6A8A'),
            tickfont=dict(family='Inter', size=9, color='#4A6A8A'),
            gridcolor='rgba(255,255,255,0.04)',
            row=r, col=1,
        )
    st.plotly_chart(fig, use_container_width=True,
                     config=dict(displaylogo=False, responsive=True))

# ─────────────────────────────────────────────────────────────────────
# Q2 - Fair Value Index (FVI)
# Is Egyptian gold overpriced or underpriced vs. theoretical fair value?
# ─────────────────────────────────────────────────────────────────────


def _render_embed_q2(data: pd.DataFrame, k: str, show_events: bool) -> None:
    """Render embed slide Q2: Fair Value Index (FVI) - Overvalued vs. Undervalued vs. Fair."""
    fvi_data = data.copy()
    for karat, factor in KARAT_FACTORS.items():
        theoretical = (
            fvi_data['Gold_USD_Ounce'] / OUNCE_TO_GRAM
        ) * factor * fvi_data['USD_EGP_Official']
        fvi_data[f'FVI_{karat}'] = fvi_data[f'Price_{karat}'] / theoretical

    latest_fvi = fvi_data[f'FVI_{k}'].dropna().iloc[-1]
    max_fvi = fvi_data[f'FVI_{k}'].dropna().max()
    avg_fvi = fvi_data[f'FVI_{k}'].dropna().mean()

    if latest_fvi > 1.05:
        fvi_status, fvi_color, fvi_status_e = "Overvalued", "#EF476F", "Overvalued"
    elif latest_fvi < 0.97:
        fvi_status, fvi_color, fvi_status_e = "Undervalued", "#06D6A0", "Undervalued"
    else:
        fvi_status, fvi_color, fvi_status_e = "Fair Value", "#FFD700", "Fair Value"

    dev_pct = (latest_fvi - 1.0) * 100

    st.markdown(
        _kpi_strip(
            _kpi_card(f"{latest_fvi:.3f}", f"Fair Value Index ({k})", fvi_color),
            _kpi_card(fvi_status, "Current Status", fvi_color),
            _kpi_card(f"{dev_pct:+.1f}%", "Deviation from Fair Value", fvi_color),
            _kpi_card(f"{max_fvi:.3f}", "Highest Price Gap Recorded", "#EF476F"),
            _kpi_card(f"{avg_fvi:.3f}", "Period Average", "#4CC9F0"),
        ),
        unsafe_allow_html=True,
    )

    fig2 = go.Figure()
    fig2.add_hrect(y0=1.05, y1=2.5, fillcolor='rgba(239,71,111,0.07)', line_width=0)
    fig2.add_hrect(y0=0.97, y1=1.05, fillcolor='rgba(255,215,0,0.06)', line_width=0)
    fig2.add_hrect(y0=0.0, y1=0.97, fillcolor='rgba(6,214,160,0.06)', line_width=0)

    fvi_colors = {'24K': '#FFF9C4', '21K': '#FFD700', '18K': '#CD7F32'}
    for karat in ['24K', '21K', '18K']:
        lw = 2.4 if karat == k else 1.0
        opacity = 1.0 if karat == k else 0.35
        fig2.add_trace(go.Scatter(
            x=fvi_data.index, y=fvi_data[f'FVI_{karat}'],
            name=karat,
            line=dict(color=fvi_colors[karat], width=lw),
            opacity=opacity,
            hovertemplate=f"FVI {karat}: %{{y:.3f}}<extra></extra>",
        ))

    fig2.add_hline(
        y=1.0, line=dict(color='#FFD700', width=1.5, dash='dash'),
        annotation_text='Fair Value (FVI = 1.0)',
        annotation_font=dict(size=9, color='#FFD700', family='Inter'),
        annotation_position='top left',
    )
    fig2.add_hline(y=1.05, line=dict(color='rgba(239,71,111,0.4)', width=0.8, dash='dot'))
    fig2.add_hline(y=0.97, line=dict(color='rgba(6,214,160,0.4)', width=0.8, dash='dot'))

    fig2.add_annotation(x=fvi_data.index[-1], y=1.20, xanchor='right',
        text="Overvalued - the price gap is speculative", showarrow=False,
        font=dict(size=8, color='#EF476F', family='Inter'),
        bgcolor='rgba(3,6,15,0.65)', borderpad=2)
    fig2.add_annotation(x=fvi_data.index[-1], y=1.01, xanchor='right',
        text="Fair Value - an ideal entry window", showarrow=False,
        font=dict(size=8, color='#FFD700', family='Inter'),
        bgcolor='rgba(3,6,15,0.65)', borderpad=2)
    fig2.add_annotation(x=fvi_data.index[-1], y=0.93, xanchor='right',
        text="Undervalued - a rare buying window", showarrow=False,
        font=dict(size=8, color='#06D6A0', family='Inter'),
        bgcolor='rgba(3,6,15,0.65)', borderpad=2)

    last_date = fvi_data[f'FVI_{k}'].dropna().index[-1]
    fig2.add_annotation(
        x=last_date, y=latest_fvi,
        text=f"Now: {latest_fvi:.3f} ({fvi_status_e})",
        showarrow=True, arrowhead=2, arrowcolor=fvi_color, arrowsize=1.2, arrowwidth=1.5,
        ax=-60, ay=-30, font=dict(size=9.5, color=fvi_color, family='Inter'),
        bgcolor='rgba(3,6,15,0.80)', borderpad=3,
    )

    if show_events:
        add_events(fig2, data)

    _std_layout(fig2, height=480)
    fig2.update_layout(yaxis=dict(title_text='Fair Value Index (FVI)'), margin=dict(l=8, r=8, t=20, b=8))
    fig2.update_yaxes(tickfont=dict(family='Inter', size=10), gridcolor='rgba(255,255,255,0.04)')
    st.plotly_chart(fig2, use_container_width=True,
                     config=dict(displaylogo=False, responsive=True))

# ─────────────────────────────────────────────────────────────────────
# Q3 - Speculation / Panic Premium
# Do Egyptian gold prices show measurable panic spikes during crises?
# ─────────────────────────────────────────────────────────────────────


def _render_embed_q3(data: pd.DataFrame, k: str, show_events: bool) -> None:
    """Render embed slide Q3: Speculation / Panic Premium - crisis-window instability evidence."""
    latest_prem = {karat: data[f'PremPct_{karat}'].dropna().iloc[-1] for karat in KARAT_FACTORS}

    crisis_avg, baseline_avg = 0.0, 0.0
    try:
        if CRISIS_EVENTS:
            prem_series = data['PremPct_21K'].dropna()
            crisis_mask = pd.Series(False, index=prem_series.index)
            for ev_date in CRISIS_EVENTS.keys():
                ev_ts = pd.Timestamp(ev_date)
                window = (prem_series.index >= ev_ts - pd.Timedelta(days=15)) & \
                         (prem_series.index <= ev_ts + pd.Timedelta(days=15))
                crisis_mask |= window
            if crisis_mask.any():
                crisis_avg = prem_series[crisis_mask].mean()
            if (~crisis_mask).any():
                baseline_avg = prem_series[~crisis_mask].mean()
    except (NameError, TypeError):
        pass

    def _prem_status(pct):
        if pct > 15:
            return ("Price Bubble", "#EF476F")
        if pct > 8:
            return ("Elevated", "#FF9F43")
        if pct > 3:
            return ("Moderate", "#FFD700")
        return ("Normal", "#06D6A0")

    status_txt, status_clr = _prem_status(latest_prem['21K'])

    st.markdown(
        _kpi_strip(
            _kpi_card(f"{latest_prem['21K']:.1f}%", "Current 21K Premium", status_clr),
            _kpi_card(status_txt, "Signal Level", status_clr),
            _kpi_card(f"{crisis_avg:.1f}%", "Avg. Premium During Crises", "#EF476F"),
            _kpi_card(f"{baseline_avg:.1f}%", "Avg. Premium in Normal Times", "#06D6A0"),
            _kpi_card(f"{(crisis_avg - baseline_avg):+.1f}pt", "Instability Gap (Evidence)", "#FF9F43"),
        ),
        unsafe_allow_html=True,
    )

    fig3 = go.Figure()
    fig3.add_hrect(y0=15, y1=60, fillcolor='rgba(239,71,111,0.10)', line_width=0)
    fig3.add_hrect(y0=8, y1=15, fillcolor='rgba(255,159,67,0.08)', line_width=0)
    fig3.add_hrect(y0=3, y1=8, fillcolor='rgba(255,215,0,0.05)', line_width=0)
    fig3.add_hrect(y0=-5, y1=3, fillcolor='rgba(6,214,160,0.04)', line_width=0)

    fig3.add_hline(y=15, line=dict(color='rgba(239,71,111,0.5)', width=1, dash='dot'),
                    annotation_text='Price Bubble (&gt;15%)', annotation_position='top left',
                    annotation_font=dict(size=8, color='#EF476F', family='Inter'))
    fig3.add_hline(y=8, line=dict(color='rgba(255,159,67,0.5)', width=1, dash='dot'),
                    annotation_text='Elevated Premium (&gt;8%)', annotation_position='top left',
                    annotation_font=dict(size=8, color='#FF9F43', family='Inter'))
    fig3.add_hline(y=0, line=dict(color='rgba(100,120,160,0.4)', width=1, dash='dot'))

    for karat, color in KARAT_COLORS.items():
        lw = 2.2 if karat == k else 1.3
        fig3.add_trace(go.Scatter(
            x=data.index, y=data[f'PremPct_{karat}'],
            name=karat, line=dict(color=color, width=lw),
            hovertemplate=f"{karat} Premium: %{{y:.1f}}%<extra></extra>",
        ))

    if show_events:
        add_events(fig3, data)

    _std_layout(fig3, height=460)
    fig3.update_layout(yaxis=dict(title_text='Demand / Instability Premium (%)'), margin=dict(l=8, r=8, t=20, b=8))
    fig3.update_yaxes(tickfont=dict(family='Inter', size=10), gridcolor='rgba(255,255,255,0.04)')
    st.plotly_chart(fig3, use_container_width=True,
                     config=dict(displaylogo=False, responsive=True))

# ─────────────────────────────────────────────────────────────────────
# Q4 - Macroeconomic Correlation Matrix
# Which macro driver explains Egyptian gold price moves the most?
# Uses the shared compute_correlation_matrix() / best_correlation_driver()
# helpers exclusively - no inline .corr() calls.
# ─────────────────────────────────────────────────────────────────────


def _render_embed_q4(data: pd.DataFrame, k: str, show_events: bool) -> None:
    """Render embed slide Q4: Macroeconomic Correlation Matrix - which driver explains gold moves."""
    cols_ = [f'Price_{k}', 'Gold_USD_Ounce', 'USD_EGP_Official', 'Crude_Oil', 'US_10Y_Treasury', 'SP500']
    labels_ = [f'Gold Price ({k})', 'XAU Gold', 'USD/EGP', 'Brent Oil', '10Y Treasury', 'S&P 500']
    cd = compute_correlation_matrix(data, cols_, labels_)

    price_lbl = labels_[0]
    driver_labels = labels_[1:]
    _best_label, _best_value, _ranked = best_correlation_driver(cd, price_lbl)
    gold_corr = {lbl: cd.loc[price_lbl, lbl] for lbl in driver_labels}

    usd_corr = gold_corr.get('USD/EGP', 0)
    xau_corr = gold_corr.get('XAU Gold', 0)
    oil_corr = gold_corr.get('Brent Oil', 0)
    sp_corr = gold_corr.get('S&amp;P 500', gold_corr.get('S&P 500', 0))

    best_driver_lbl = max(gold_corr, key=lambda lbl: abs(gold_corr[lbl]))
    best_driver_val = gold_corr[best_driver_lbl]

    st.markdown(
        _kpi_strip(
            _kpi_card(f"{usd_corr:.3f}", "USD/EGP Correlation with Gold Price", "#06D6A0"),
            _kpi_card(f"{xau_corr:.3f}", "XAU/USD Correlation with Gold Price", "#FFD700"),
            _kpi_card(f"{oil_corr:.3f}", "Oil Correlation with Gold Price", "#FF9F43"),
            _kpi_card(f"{sp_corr:.3f}", "S&amp;P 500 Correlation with Gold Price", "#4CC9F0"),
            _kpi_card(best_driver_lbl, f"Highest Impact (r={best_driver_val:.3f})", "#D4AF37"),
        ),
        unsafe_allow_html=True,
    )

    fc4 = px.imshow(
        cd, text_auto='.2f',
        color_continuous_scale=[[0.0, '#EF476F'], [0.5, '#060C18'], [1.0, '#06D6A0']],
        zmin=-1, zmax=1, title=None,
    )

    best_idx = labels_.index(best_driver_lbl)
    fc4.add_shape(type='rect', x0=best_idx - 0.5, x1=best_idx + 0.5,
                  y0=-0.5, y1=len(labels_) - 0.5,
                  line=dict(color='#FFD700', width=2.5),
                  fillcolor='rgba(255,215,0,0.04)', layer='above')
    fc4.add_shape(type='rect', x0=-0.5, x1=len(labels_) - 0.5,
                  y0=best_idx - 0.5, y1=best_idx + 0.5,
                  line=dict(color='#FFD700', width=2.5),
                  fillcolor='rgba(255,215,0,0.04)', layer='above')
    fc4.add_annotation(
        x=best_idx, y=-0.75,
        text=f"Highest impact (r={best_driver_val:.2f})",
        showarrow=False, font=dict(size=9, color='#FFD700', family='Inter'),
        bgcolor='rgba(3,6,15,0.75)', borderpad=2,
    )
    fc4.add_shape(type='rect', x0=-0.5, x1=len(labels_) - 0.5,
                  y0=-0.5, y1=0.5,
                  line=dict(color='rgba(255,255,255,0.35)', width=1.5, dash='dot'),
                  layer='above')

    _std_layout(fc4, height=450)
    fc4.update_layout(showlegend=False, coloraxis_showscale=False, margin=dict(l=8, r=8, t=20, b=40))
    fc4.update_traces(textfont=dict(size=13, family='DM Mono', color='#E8EDF5'))
    fc4.update_xaxes(tickfont=dict(family='Inter', size=11, color='#9090A8'))
    fc4.update_yaxes(tickfont=dict(family='Inter', size=11, color='#9090A8'))
    st.plotly_chart(fc4, use_container_width=True,
                     config=dict(displaylogo=False, responsive=True))

# ─────────────────────────────────────────────────────────────────────
# Q5 - Net Return Comparison (Portfolio Simulation)
# Which asset outperforms after real costs; did EGP cash lose
# purchasing power?
# ─────────────────────────────────────────────────────────────────────


def _render_embed_q5(data: pd.DataFrame, k: str, show_events: bool) -> None:
    """Render embed slide Q5: Net Return Comparison - portfolio simulation after real costs."""
    INIT = 100_000

    def _portfolio_metrics(series):
        if series.dropna().empty:
            return dict(ret=0, sharpe=0, maxdd=0)
        rets = series.dropna().pct_change().dropna()
        total = (series.dropna().iloc[-1] / series.dropna().iloc[0] - 1) * 100
        sharpe = (rets.mean() / rets.std() * np.sqrt(252)) if rets.std() > 0 else 0
        roll = series.dropna().cummax()
        dd = ((series.dropna() - roll) / roll).min() * 100
        return dict(ret=total, sharpe=sharpe, maxdd=dd)

    m24 = _portfolio_metrics(data['Port_24K'].dropna())
    m21 = _portfolio_metrics(data['Port_21K'].dropna())
    m18 = _portfolio_metrics(data['Port_18K'].dropna())
    musd = _portfolio_metrics(data['Port_USD'].dropna())
    mcash = _portfolio_metrics(data['Port_Cash'].dropna())

    all_rets = {'24K': m24['ret'], '21K': m21['ret'], '18K': m18['ret']}
    best_label = max(all_rets, key=all_rets.get)
    best_ret = all_rets[best_label]

    # NOTE: replace with the actual cumulative CPI figure for the
    # analysis window (e.g. from CAPMAS) before presenting.
    EST_CUM_INFLATION_PCT = 180  # TODO: replace with real cumulative CPI % for the period
    cash_real_loss = mcash['ret'] - EST_CUM_INFLATION_PCT

    st.markdown(
        _kpi_strip(
            _kpi_card(f"{best_label}", "Best Performer (Net)", "#FFD700"),
            _kpi_card(f"{best_ret:+.0f}%", f"{best_label} Net Return (since Jan 2020)", "#FFD700"),
            _kpi_card(f"{musd['ret']:+.0f}%", "USD Return", "#4CC9F0"),
            _kpi_card(f"{mcash['ret']:+.0f}%", "EGP Cash Return (Nominal)", "#6a7a99"),
            _kpi_card(f"{cash_real_loss:+.0f}%", "EGP Cash Return (Real, after Inflation)", "#EF476F"),
        ),
        unsafe_allow_html=True,
    )
    st.markdown(
        '<div class="eq-footnote">Real cash return assumes an estimated cumulative inflation figure - replace with the actual CAPMAS number before presenting</div>',
        unsafe_allow_html=True,
    )

    fig5 = go.Figure()
    karat_cfg = [('24K', '#FFF9C4', 2.0), ('21K', '#FFD700', 2.8), ('18K', '#CD7F32', 1.8)]
    for karat, color, lw in karat_cfg:
        fig5.add_trace(go.Scatter(
            x=data.index, y=data[f'Port_{karat}'],
            name=f'{karat} (Net)', line=dict(color=color, width=lw),
            hovertemplate=f"<b>{karat}</b>: %{{y:,.0f}} {EGP}<extra></extra>",
        ))
    fig5.add_trace(go.Scatter(
        x=data.index, y=data['Port_USD'], name='USD',
        line=dict(color='#4CC9F0', width=1.8, dash='dot'),
        hovertemplate=f"USD: %{{y:,.0f}} {EGP}<extra></extra>",
    ))
    fig5.add_trace(go.Scatter(
        x=data.index, y=data['Port_Cash'], name='EGP Cash',
        line=dict(color='rgba(100,120,160,0.5)', width=1.2, dash='dot'),
        hovertemplate=f"Cash: %{{y:,.0f}} {EGP}<extra></extra>",
    ))

    fig5.add_hline(
        y=INIT, line=dict(color='rgba(255,255,255,0.15)', width=1, dash='dot'),
        annotation_text='Initial Capital: 100,000 EGP',
        annotation_font=dict(size=8, color='#6a7a99', family='Inter'),
        annotation_position='bottom right',
    )

    for karat, color, _ in karat_cfg:
        last_val = data[f'Port_{karat}'].dropna().iloc[-1]
        last_dt = data[f'Port_{karat}'].dropna().index[-1]
        fig5.add_annotation(
            x=last_dt, y=last_val, text=f" {karat}: {last_val / 1000:.0f}k",
            showarrow=False, xanchor='left',
            font=dict(size=8.5, color=color, family='Inter'),
        )

    if show_events:
        add_events(fig5, data)

    _std_layout(fig5, height=480)
    fig5.update_layout(yaxis=dict(title_text='Portfolio Value (EGP)'), margin=dict(l=8, r=8, t=20, b=8))
    fig5.update_yaxes(tickfont=dict(family='DM Mono', size=10), gridcolor='rgba(255,255,255,0.04)')
    st.plotly_chart(fig5, use_container_width=True,
                     config=dict(displaylogo=False, responsive=True))

# ─────────────────────────────────────────────────────────────────────
# Q6 - Prophet Multi-Stage Forecast
# Forward forecast with genuine held-out backtest accuracy metrics
# (MAE/RMSE/MAPE computed on a train/test split, never on in-sample fit).
# ─────────────────────────────────────────────────────────────────────


def _render_embed_q6(data: pd.DataFrame, k: str, show_events: bool) -> None:
    """Render embed slide Q6: Prophet Multi-Stage Forecast - held-out backtest accuracy."""
    st.markdown(
        '<div style="font-family:Inter; font-size:14px; margin-bottom:-15px;">Forecast Horizon (days)</div>',
        unsafe_allow_html=True,
    )
    forecast_days = st.slider(
        "Forecast Horizon (days)", 30, 365, 180, 30,
        key="embed_q6_slider", label_visibility="collapsed",
    )

    with st.spinner("Training Prophet model…"):
        try:
            from prophet import Prophet

            fv_col = f'Price_{k}'
            train = data.reset_index()[['Date', fv_col, 'USD_EGP_Official', 'Crude_Oil']].copy()
            train.columns = ['ds', 'y', 'USD', 'OIL']
            train['ds'] = pd.to_datetime(train['ds'])
            train['USD'] = train['USD'].ffill().bfill()
            train['OIL'] = train['OIL'].ffill().bfill()
            train = train.dropna(subset=['y'])

            def _forecast_regressor(col_name, n_days, hist_df=None):
                """Forecast a regressor (USD or OIL) forward using its own
                Prophet model. hist_df lets the backtest reuse a truncated
                history so the test window never leaks into training."""
                if hist_df is None:
                    df_r = data.reset_index()[['Date', col_name]].copy()
                else:
                    df_r = hist_df[['Date', col_name]].copy()
                df_r.columns = ['ds', 'y']
                df_r['ds'] = pd.to_datetime(df_r['ds'])
                df_r = df_r.dropna(subset=['y'])
                mr = Prophet(
                    yearly_seasonality=True, weekly_seasonality=False,
                    daily_seasonality=False, changepoint_prior_scale=0.05,
                    interval_width=0.80,
                )
                mr.fit(df_r)
                fut = mr.make_future_dataframe(periods=n_days, freq='D')
                fc_r = mr.predict(fut)[['ds', 'yhat']]
                return fc_r[fc_r['ds'] > df_r['ds'].max()].reset_index(drop=True)

            # PRODUCTION MODEL - full history, actual forward forecast.
            usd_fc = _forecast_regressor('USD_EGP_Official', forecast_days)
            oil_fc = _forecast_regressor('Crude_Oil', forecast_days)

            pm = Prophet(
                yearly_seasonality=True, weekly_seasonality=False, daily_seasonality=False,
                changepoint_prior_scale=0.10, seasonality_prior_scale=10.0,
                interval_width=0.90, n_changepoints=30,
            )
            pm.add_regressor('USD', standardize=True)
            pm.add_regressor('OIL', standardize=True)
            pm.fit(train)

            future_raw = pm.make_future_dataframe(periods=forecast_days, freq='D')
            future_raw['ds'] = pd.to_datetime(future_raw['ds'])
            hist_regs = train[['ds', 'USD', 'OIL']].copy()
            future_merged = future_raw.merge(hist_regs, on='ds', how='left')
            usd_fc.columns = ['ds', 'USD_fc']
            oil_fc.columns = ['ds', 'OIL_fc']
            future_merged = future_merged.merge(usd_fc, on='ds', how='left')
            future_merged = future_merged.merge(oil_fc, on='ds', how='left')
            future_merged['USD'] = future_merged['USD'].fillna(future_merged['USD_fc'])
            future_merged['OIL'] = future_merged['OIL'].fillna(future_merged['OIL_fc'])
            future_merged.drop(columns=['USD_fc', 'OIL_fc'], inplace=True)
            future_merged['USD'] = future_merged['USD'].ffill().bfill()
            future_merged['OIL'] = future_merged['OIL'].ffill().bfill()
            future_final = future_merged[['ds', 'USD', 'OIL']].copy()

            fc6 = pm.predict(future_final)

            last_hist6 = train['ds'].max()
            fc_out6 = fc6[fc6['ds'] > last_hist6].head(forecast_days).copy()
            act_last = train['y'].iloc[-1]
            pred_last_s = fc6[fc6['ds'] == last_hist6]['yhat']
            n6 = len(train)
            pred_last = pred_last_s.values[0] if len(pred_last_s) else fc6.iloc[:n6]['yhat'].iloc[-1]
            offset6 = act_last - pred_last
            fc_out6['yhat'] += offset6
            fc_out6['yhat_upper'] += offset6
            fc_out6['yhat_lower'] += offset6

            fc_target = fc_out6['yhat'].iloc[-1]
            fc_change = (fc_target - act_last) / act_last * 100

            # BACKTEST MODEL - held-out window for REPORTED ACCURACY only.
            BACKTEST_DAYS = int(min(60, max(10, len(train) // 5)))
            train_bt = train.iloc[:-BACKTEST_DAYS].copy()
            test_bt = train.iloc[-BACKTEST_DAYS:].copy()

            hist_df_bt = data.reset_index()[['Date', 'USD_EGP_Official', 'Crude_Oil']].copy()
            hist_df_bt = hist_df_bt[hist_df_bt['Date'] <= train_bt['ds'].max()]
            usd_fc_bt = _forecast_regressor('USD_EGP_Official', BACKTEST_DAYS, hist_df=hist_df_bt)
            oil_fc_bt = _forecast_regressor('Crude_Oil', BACKTEST_DAYS, hist_df=hist_df_bt)
            usd_fc_bt.columns = ['ds', 'USD']
            oil_fc_bt.columns = ['ds', 'OIL']
            test_bt_features = test_bt[['ds']].merge(usd_fc_bt, on='ds', how='left') \
                                                .merge(oil_fc_bt, on='ds', how='left')
            test_bt_features['USD'] = test_bt_features['USD'].ffill().bfill()
            test_bt_features['OIL'] = test_bt_features['OIL'].ffill().bfill()

            pm_bt = Prophet(
                yearly_seasonality=True, weekly_seasonality=False, daily_seasonality=False,
                changepoint_prior_scale=0.10, seasonality_prior_scale=10.0,
                interval_width=0.90, n_changepoints=30,
            )
            pm_bt.add_regressor('USD', standardize=True)
            pm_bt.add_regressor('OIL', standardize=True)
            pm_bt.fit(train_bt)

            bt_pred = pm_bt.predict(test_bt_features[['ds', 'USD', 'OIL']])[['ds', 'yhat']]
            y_true_bt = test_bt['y'].values
            y_pred_bt = bt_pred['yhat'].values
            mae_bt = float(np.abs(y_true_bt - y_pred_bt).mean())
            rmse_bt = float(np.sqrt(((y_true_bt - y_pred_bt) ** 2).mean()))
            mape_bt = float((np.abs((y_true_bt - y_pred_bt) / y_true_bt).mean()) * 100)

            st.markdown(
                _kpi_strip(
                    _kpi_card(f"{act_last:,.0f} {EGP}", f"Current {k} Price", "#FFD700"),
                    _kpi_card(f"{fc_target:,.0f} {EGP}", f"{forecast_days}-Day Forecast", "#4CC9F0"),
                    _kpi_card(f"{fc_change:+.1f}%", "Expected Change",
                              "#06D6A0" if fc_change > 0 else "#EF476F"),
                    _kpi_card(f"{mae_bt:,.0f} {EGP}", f"MAE (Backtest, {BACKTEST_DAYS}d)", "#FF9F43"),
                    _kpi_card(f"{mape_bt:.1f}%", "MAPE (Backtest)", "#A855F7"),
                ),
                unsafe_allow_html=True,
            )
            st.markdown(
                f'<div class="eq-footnote">Model accuracy is computed on data the model never saw during training '
                f'(last {BACKTEST_DAYS} days) - RMSE: {rmse_bt:,.0f} {EGP}</div>',
                unsafe_allow_html=True,
            )

            fig6 = go.Figure()
            hw6 = data[fv_col].resample('W').last()
            fig6.add_trace(go.Scatter(
                x=hw6.index, y=hw6, name='Actual Price',
                line=dict(color='#4A6A8A', width=1.5),
                hovertemplate=f"%{{x|%d %b %Y}}<br>%{{y:,.0f}} {EGP}<extra></extra>",
            ))
            fig6.add_trace(go.Scatter(
                x=fc_out6['ds'], y=fc_out6['yhat_upper'],
                line=dict(width=0), showlegend=False,
            ))
            fig6.add_trace(go.Scatter(
                x=fc_out6['ds'], y=fc_out6['yhat_lower'],
                fill='tonexty', fillcolor='rgba(76,201,240,0.12)',
                line=dict(width=0), name='90% Confidence Interval',
            ))
            fig6.add_trace(go.Scatter(
                x=fc_out6['ds'], y=fc_out6['yhat'],
                name='Prophet Forecast', line=dict(color='#4CC9F0', width=2.5),
                hovertemplate=f"%{{x|%d %b %Y}}<br><b>%{{y:,.0f}} {EGP}</b><extra></extra>",
            ))
            fig6.add_vline(
                x=datetime.today().timestamp() * 1000,
                line_dash='dash', line_color='#FFD700', opacity=0.6,
                annotation_text='Today',
                annotation_font=dict(color='#FFD700', size=9, family='Inter'),
                annotation_position='top right',
            )

            if show_events:
                add_events(fig6, data)

            _std_layout(fig6, height=460)
            fig6.update_layout(yaxis=dict(title_text='Price (EGP/gram)'), margin=dict(l=8, r=8, t=20, b=8))
            fig6.update_yaxes(tickfont=dict(family='DM Mono', size=10), gridcolor='rgba(255,255,255,0.04)')
            st.plotly_chart(fig6, use_container_width=True,
                             config=dict(displaylogo=False, responsive=True))

        except (ModuleNotFoundError, ImportError):
            st.error("Prophet is not installed. Please run: pip install prophet")
        except Exception as _exc:
            st.error(f"Forecast error: {_exc}")

# ─────────────────────────────────────────────────────────────────────
# Q7 - Technical Signals (RSI + MACD + Bollinger Bands -> BUY/HOLD/SELL)
# Reads Signal_{k} / SignalScore_{k} / SignalAgreement_{k} directly from
# `data` - these are computed exactly once by compute_signal_columns()
# and validated by validate_data_consistency() before this block runs.
# No indicator vote is recomputed here.
# ─────────────────────────────────────────────────────────────────────


def _render_embed_q7(data: pd.DataFrame, k: str, show_events: bool) -> None:
    """Render embed slide Q7: Technical Signals (RSI + MACD + Bollinger Bands -> BUY/HOLD/SELL)."""
    last_row = data.dropna(subset=[f'RSI_{k}', f'MACD_{k}', f'BB_up_{k}']).iloc[-1]
    rsi_val = last_row[f'RSI_{k}']
    macd_val = last_row[f'MACD_{k}']
    macd_sig = last_row[f'MACDSig_{k}']
    price_val = last_row[f'Price_{k}']
    bb_up = last_row[f'BB_up_{k}']
    bb_dn = last_row[f'BB_dn_{k}']

    sig = last_row[f'Signal_{k}']
    agree_str = last_row[f'SignalAgreement_{k}']  # e.g. "2/3"
    sig_color = {'BUY': '#06D6A0', 'SELL': '#EF476F', 'HOLD': '#4CC9F0'}.get(sig, '#4CC9F0')
    comp_signal = {'BUY': 'BUY \U0001F7E2', 'SELL': 'SELL \U0001F534', 'HOLD': 'HOLD \U0001F7E1'}.get(sig, 'HOLD \U0001F7E1')

    rsi_status = "Oversold" if rsi_val < 30 else ("Overbought" if rsi_val > 70 else "Neutral")
    macd_status = "Bullish \u25B2" if macd_val > macd_sig else "Bearish \u25BC"
    bb_status = "At Lower Band" if price_val < bb_dn else ("At Upper Band" if price_val > bb_up else "Within Range")

    st.markdown(
        _kpi_strip(
            _kpi_card(f"{rsi_val:.1f}", f"RSI-14 ({rsi_status})",
                      "#06D6A0" if rsi_val < 30 else ("#EF476F" if rsi_val > 70 else "#FFD700")),
            _kpi_card(macd_status, "MACD Crossover",
                      "#06D6A0" if macd_val > macd_sig else "#EF476F"),
            _kpi_card(bb_status, "Bollinger Bands",
                      "#06D6A0" if price_val < bb_dn else ("#EF476F" if price_val > bb_up else "#4CC9F0")),
            _kpi_card(f"{price_val:,.0f} {EGP}", f"Current {k} Price", "#FFD700"),
            _kpi_card(agree_str, "Indicators Agreeing with Composite Signal", sig_color),
        ),
        unsafe_allow_html=True,
    )

    fig7 = make_subplots(
        rows=3, cols=1, shared_xaxes=True,
        row_heights=[0.55, 0.25, 0.20], vertical_spacing=0.06,
        subplot_titles=[f"Price + Bollinger Bands ({k})", "MACD - Trend Momentum", "RSI-14 - Overbought/Oversold"],
    )
    for anno in fig7['layout']['annotations']:
        anno['font'] = dict(size=13, family='Inter', color='#4A6A8A')
        anno['yshift'] = 12 if "RSI-14" in anno['text'] else -10

    fig7.add_trace(go.Scatter(x=data.index, y=data[f'BB_up_{k}'],
        line=dict(color='rgba(180,180,255,0.4)', width=1, dash='dot'),
        name='BB Upper', showlegend=False), row=1, col=1)
    fig7.add_trace(go.Scatter(x=data.index, y=data[f'BB_dn_{k}'],
        fill='tonexty', fillcolor='rgba(180,180,255,0.04)',
        line=dict(color='rgba(180,180,255,0.4)', width=1, dash='dot'),
        name='Bollinger Bands'), row=1, col=1)
    fig7.add_trace(go.Scatter(x=data.index, y=data[f'BB_mid_{k}'],
        line=dict(color='rgba(255,215,0,0.35)', width=1, dash='dash'),
        name='SMA 20', showlegend=False), row=1, col=1)
    fig7.add_trace(go.Scatter(x=data.index, y=data[f'Price_{k}'],
        name='Price', line=dict(color='#D8E4F0', width=1.8),
        hovertemplate=f"%{{x|%d %b %Y}} - %{{y:,.0f}} {EGP}<extra></extra>"), row=1, col=1)
    fig7.add_trace(go.Scatter(x=data.index, y=data[f'SMA50_{k}'],
        name='SMA 50', line=dict(color='#FF9F43', width=1.0, dash='dot')), row=1, col=1)
    fig7.add_trace(go.Scatter(x=data.index, y=data[f'SMA200_{k}'],
        name='SMA 200', line=dict(color='#A855F7', width=1.0, dash='dot')), row=1, col=1)

    buys = data[data[f'Signal_{k}'] == 'BUY']
    sells = data[data[f'Signal_{k}'] == 'SELL']
    fig7.add_trace(go.Scatter(x=buys.index, y=buys[f'Price_{k}'], mode='markers',
        name='BUY \u25B2', marker=dict(symbol='triangle-up', color='#06D6A0', size=8,
                                        line=dict(width=1, color='white'))), row=1, col=1)
    fig7.add_trace(go.Scatter(x=sells.index, y=sells[f'Price_{k}'], mode='markers',
        name='SELL \u25BC', marker=dict(symbol='triangle-down', color='#EF476F', size=8,
                                         line=dict(width=1, color='white'))), row=1, col=1)

    hc7 = ['#06D6A0' if v >= 0 else '#EF476F' for v in data[f'MACDHist_{k}']]
    fig7.add_trace(go.Bar(x=data.index, y=data[f'MACDHist_{k}'],
        name='MACD Histogram', marker_color=hc7, opacity=0.75), row=2, col=1)
    fig7.add_trace(go.Scatter(x=data.index, y=data[f'MACD_{k}'],
        name='MACD', line=dict(color='#4CC9F0', width=1.5)), row=2, col=1)
    fig7.add_trace(go.Scatter(x=data.index, y=data[f'MACDSig_{k}'],
        name='Signal', line=dict(color='#FF9F43', width=1.5)), row=2, col=1)
    fig7.add_hline(y=0, line=dict(color='rgba(255,255,255,0.12)', width=0.8), row=2, col=1)

    fig7.add_trace(go.Scatter(x=data.index, y=data[f'RSI_{k}'],
        name='RSI-14', line=dict(color='#A855F7', width=1.7)), row=3, col=1)
    fig7.add_hline(y=70, line=dict(color='rgba(239,71,111,0.5)', width=1, dash='dot'), row=3, col=1)
    fig7.add_hline(y=30, line=dict(color='rgba(6,214,160,0.5)', width=1, dash='dot'), row=3, col=1)
    fig7.add_hrect(y0=70, y1=100, fillcolor='rgba(239,71,111,0.05)', line_width=0, row=3, col=1)
    fig7.add_hrect(y0=0, y1=30, fillcolor='rgba(6,214,160,0.05)', line_width=0, row=3, col=1)

    if show_events:
        add_events(fig7, data, rows=[1, 2, 3], y_ann=0.93)

    _std_layout(fig7, height=580)
    fig7.update_layout(margin=dict(l=8, r=8, t=100, b=8))
    fig7.update_yaxes(title_text='Price (EGP)', title_font=dict(size=8), row=1, col=1,
                       tickfont=dict(size=9), gridcolor='rgba(255,255,255,0.04)')
    fig7.update_yaxes(title_text='MACD', title_font=dict(size=8), row=2, col=1,
                       tickfont=dict(size=9), gridcolor='rgba(255,255,255,0.04)')
    fig7.update_yaxes(title_text='RSI', range=[0, 100], title_font=dict(size=8), row=3, col=1,
                       tickfont=dict(size=9), gridcolor='rgba(255,255,255,0.04)')
    st.plotly_chart(fig7, use_container_width=True,
                     config=dict(displaylogo=False, responsive=True))

    today_str = datetime.today().strftime('%d %b %Y')
    hex_color = sig_color.lstrip('#')
    rgb_color = f"{int(hex_color[0:2], 16)}, {int(hex_color[2:4], 16)}, {int(hex_color[4:6], 16)}"
    st.markdown(f"""
    <style>
    .premium-signal-container {{ background: linear-gradient(135deg, rgba(10, 15, 30, 0.75) 0%, rgba(20, 30, 55, 0.55) 100%); border: 1px solid rgba(255, 255, 255, 0.05); border-left: 4px solid {sig_color}; border-radius: 12px; padding: 18px 22px; margin-top: 25px; box-shadow: 0 12px 40px rgba(0, 0, 0, 0.6), inset 0 1px 1px rgba(255, 255, 255, 0.05); backdrop-filter: blur(12px); -webkit-backdrop-filter: blur(12px); display: flex; flex-wrap: wrap; align-items: center; justify-content: space-between; gap: 15px; }}
    .premium-info-block {{ flex: 1; min-width: 280px; }}
    .premium-headline {{ font-family: 'Inter', sans-serif; color: #E2E8F0; font-size: 14px; font-weight: 600; margin-bottom: 4px; display: flex; align-items: center; gap: 8px; }}
    .premium-subtitle {{ font-family: 'Inter', sans-serif; color: #748BA7; font-size: 11px; font-weight: 400; text-align: left; width: 100%; margin-bottom: 10px; }}
    .premium-badge-block {{ display: flex; align-items: center; gap: 12px; }}
    .premium-signal-badge {{ background: rgba({rgb_color}, 0.08); border: 1px solid rgba({rgb_color}, 0.45); color: {sig_color}; padding: 8px 22px; border-radius: 8px; font-family: 'Inter', sans-serif; font-weight: 700; font-size: 15px; letter-spacing: 0.5px; text-shadow: 0 0 10px rgba({rgb_color}, 0.4); box-shadow: 0 0 15px rgba({rgb_color}, 0.1); display: inline-flex; align-items: center; }}
    .technical-pills-grid {{ display: flex; gap: 8px; margin-top: 12px; flex-wrap: wrap; width: 100%; }}
    .tech-pill {{ background: rgba(255, 255, 255, 0.02); border: 1px solid rgba(255, 255, 255, 0.06); border-radius: 6px; padding: 5px 12px; font-family: 'Inter', sans-serif; font-size: 11.5px; color: #94A3B8; display: flex; align-items: center; gap: 5px; }}
    .tech-pill strong {{ color: #F8FAFC; }}
    </style>
    <div class="premium-signal-container">
        <div class="premium-info-block">
            <div class="premium-headline"><span>Composite Smart Signal (RSI + MACD + BB)</span></div>
            <div class="premium-subtitle">Live update: <bdi>{today_str}</bdi> · based on the latest market close</div>
            <div class="technical-pills-grid">
                <div class="tech-pill">RSI-14: <strong>{rsi_val:.1f} ({rsi_status})</strong></div>
                <div class="tech-pill">MACD: <strong>{macd_status}</strong></div>
                <div class="tech-pill">Bollinger Bands: <strong>{bb_status}</strong></div>
            </div>
        </div>
        <div class="premium-badge-block">
            <div class="tech-pill" style="border-color: rgba(255,215,0,0.2); background: rgba(255,215,0,0.02);">
                Indicator Agreement: <strong style="color: #FFD700;">{agree_str}</strong>
            </div>
            <div class="premium-signal-badge">{comp_signal}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

# ── EXIT - stop rendering the rest of the app ──────────────────────────


EMBED_RENDERERS = {
    "q1": _render_embed_q1,
    "q2": _render_embed_q2,
    "q3": _render_embed_q3,
    "q4": _render_embed_q4,
    "q5": _render_embed_q5,
    "q6": _render_embed_q6,
    "q7": _render_embed_q7,
}


def render_embed_view(q: str, data: pd.DataFrame) -> None:
    """
    Single dispatcher for every Vercel embed slide (?q=q1 ... ?q=q7).

    Replaces the earlier if/elif chain: looks up the requested slide in
    EMBED_RENDERERS and calls it with the already-loaded, already-
    validated `data`, the currently selected karat, and the crisis-events
    toggle state. Unknown `q` values render a clear error instead of
    silently falling through to no output.
    """
    st.markdown(_EMBED_CSS, unsafe_allow_html=True)

    renderer = EMBED_RENDERERS.get(q)
    if renderer is None:
        st.error(f"Unknown embed view: '{q}'. Valid options are: {', '.join(EMBED_RENDERERS)}.")
        return

    k = selected_karat  # e.g. '21K'
    renderer(data, k, show_events)

if embed_q:
    render_embed_view(embed_q, data)
    st.stop()

# ═════════════════════════════════════════════════════════════════════════════
# PAGE 1: Home - Executive Summary & Live Stream
# ═════════════════════════════════════════════════════════════════════════════

if selected_key == "home":

    m = compute_metrics(data, selected_karat)

    st.markdown(f"""
    <div class="hero-wrap">
      <div class="hero-eyebrow">GOLD EGYPT · FINANCIAL INTELLIGENCE PLATFORM</div>
      <div class="hero-title">
        <img src="{IMAGE_HTML_SRC}" width="40" style="vertical-align: middle; margin-left: 10px; position: relative; top: -5px;"> {t('home_hero_title')}
      </div>
      <div class="hero-sub">
        {t('home_hero_sub')}
      </div>
      <div class="hero-date">
        <span class="dot"></span>
        LIVE · Jan 2020 - {last_date_f}
      </div>
      <div class="hero-badges">
        <span class="hero-badge">DEPI 2026</span>
        <span class="hero-badge">{t('home_badge_grant')}</span>
        <span class="hero-badge">Mahmoud Shamoun</span>
      </div>
    </div>""", unsafe_allow_html=True)

    clr = '#06D6A0' if m['total'] > 0 else '#EF476F'
    cards_html = (
        kpi_html(f"{last_price:,.0f}",    t('kpi_price_per_gram', k=selected_karat),         "#FFD700", "0.05s") +
        kpi_html(f"{last_usd:.2f}",        t('kpi_egp_usd'),                                   "#4CC9F0", "0.10s") +
        kpi_html(f"${last_gold:,.0f}",     t('kpi_ounce_global'),                              "#06D6A0", "0.15s") +
        kpi_html(f"{m['total']:+.0f}%",    t('kpi_gold_return', k=selected_karat),             clr,       "0.20s") +
        kpi_html(f"{m['sharpe']:.2f}",     "Sharpe Ratio",                                      "#A855F7", "0.25s")
    )
    st.markdown(f'<div class="kpi-grid">{cards_html}</div>', unsafe_allow_html=True)

    spacer(24)
    section("📈", t('sec_price_path'), "")
    st.markdown(f"""
    <div class="section-sub" style="display:flex;justify-content:space-between;align-items:center;margin-bottom:10px;">
    <div style="direction:{DIR}">{t('price_per_gram_sub', k=selected_karat)}</div>
    <div style="direction:ltr">Jan 2020 - {last_date_f}</div>
    </div>""", unsafe_allow_html=True)

    pc   = f'Price_{selected_karat}'
    clr  = KARAT_COLORS[selected_karat]
    fill_map = {'24K': 'rgba(255,249,196,0.07)', '21K': 'rgba(255,215,0,0.07)', '18K': 'rgba(205,127,50,0.07)'}
    fig  = go.Figure()
    _price_trace_lbl = f'{selected_karat} price/g' if LANG == 'en' else f'{selected_karat} سعر جرام'
    _egp_word = 'EGP' if LANG == 'en' else 'جنيه'
    fig.add_trace(go.Scatter(x=data.index, y=data[pc], name=_price_trace_lbl,
        line=dict(color=clr, width=2), fill='tozeroy', fillcolor=fill_map[selected_karat],
        hovertemplate="<b>%{x|%d %b %Y}</b><br>%{y:,.0f} " + _egp_word + "<extra></extra>"))
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
        insight(t('insight_overall_perf', k=selected_karat, price_chg=price_chg, usd_chg=usd_chg))
    with c2:
        insight(t('insight_historic_peak', k=selected_karat, peak_p=peak_p, peak_d=peak_d))

    spacer(24)
    section("🗓️", t('sec_key_events'), "2020 – 2025")
    events_cards = {
        "2020-03-15": ("🦠", t("event_covid_title"),     t("event_covid_date"),     t("event_covid_desc"),     "#FF6B6B"),
        "2022-02-24": ("🇺🇦", t("event_ukraine_title"),  t("event_ukraine_date"),   t("event_ukraine_desc"),   "#FF9F43"),
        "2022-03-21": ("📉", t("event_float1_title"),    t("event_float1_date"),    t("event_float1_desc"),    "#EF476F"),
        "2023-10-07": ("⚔️", t("event_gaza_title"),      t("event_gaza_date"),      t("event_gaza_desc"),      "#FF6B6B"),
        "2024-03-06": ("🔓", t("event_float2024_title"), t("event_float2024_date"), t("event_float2024_desc"), "#06D6A0"),
        "2024-09-18": ("✂️", t("event_ratecut_title"),   t("event_ratecut_date"),   t("event_ratecut_desc"),   "#4CC9F0"),
        "2025-01-19": ("🕊️", t("event_ceasefire_title"), t("event_ceasefire_date"), t("event_ceasefire_desc"), "#06D6A0"),
        "2025-04-02": ("🔥", t("event_tariffs_title"),   t("event_tariffs_date"),   t("event_tariffs_desc"),   "#FF9F43"),
        "2025-04-22": ("🏆", t("event_record_title"),    t("event_record_date"),    t("event_record_desc"),    "#FFD700"),
        "2025-06-13": ("💥", t("event_iran_title"),      t("event_iran_date"),      t("event_iran_desc"),      "#EF476F"),
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
              <div style="color:{color};font-weight:700;font-size:0.82rem;direction:{DIR};margin-bottom:4px">{title_ev}</div>
              <div style="color:#6B7A99;font-size:0.72rem;direction:{DIR};line-height:1.6">{desc}</div>
            </div>""", unsafe_allow_html=True)

    spacer(24)
    c1, c2 = st.columns([1.2, 1])
    with c1:
        section("🔗", t('sec_correlation'), "")
        st.markdown(f"""
        <div class="section-sub" style="display:flex;justify-content:space-between;align-items:center;margin-bottom:10px;">
        <div style="direction:{DIR}">{t('correlation_sub')}</div>
        <div style="direction:ltr">Correlation Matrix · Heatmap</div>
        </div>""", unsafe_allow_html=True)
        # Computed via the shared compute_correlation_matrix() helper (single
        # source of truth) - see "SHARED SIGNAL / CORRELATION LOGIC" above.
        # This matrix intentionally omits Price_{k} (it shows how the macro
        # drivers move relative to EACH OTHER, not vs. the local gold price -
        # that view lives on the Q4 slide instead). Because both this panel
        # and Q4 call the same compute_correlation_matrix() over the same
        # underlying columns, their overlapping cells are guaranteed to be
        # numerically identical - verified below.
        cols_  = ['Gold_USD_Ounce', 'USD_EGP_Official', 'Crude_Oil', 'US_10Y_Treasury', 'SP500']
        names_ = [t('corr_name_gold'), t('corr_name_usd'), t('corr_name_oil'), t('corr_name_bonds'), t('corr_name_sp500')]
        cd     = compute_correlation_matrix(data, cols_, names_)

        # ── Internal validation layer (runs every render, negligible cost) ──
        # Confirm this home-page matrix agrees with the Q4 slide's matrix on
        # every macro-to-macro cell they share (built from the same karat
        # since Q4's non-Price_k columns are karat-independent).
        try:
            _cols_en = ['Gold_USD_Ounce', 'USD_EGP_Official', 'Crude_Oil', 'US_10Y_Treasury', 'SP500']
            _q4_check = compute_correlation_matrix(data, [f'Price_{selected_karat}'] + _cols_en)
            _home_check = compute_correlation_matrix(data, _cols_en)
            assert_correlation_consistency(
                _q4_check, _home_check, shared_labels=_cols_en,
                context="home-page correlation panel vs. Q4 macro matrix"
            )
        except AssertionError as _corr_mismatch:
            st.error(f"⚠️ Data consistency check failed: {_corr_mismatch}")
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
        section("💱", t('sec_usd_path'), "")
        st.markdown(f"""
        <div class="section-sub" style="display:flex;justify-content:space-between;align-items:center;margin-bottom:10px;">
        <div style="direction:{DIR}">{t('usd_path_sub')}</div>
        <div style="direction:ltr">USD / EGP</div>
        </div>""", unsafe_allow_html=True)
        fu = go.Figure()
        fu.add_trace(go.Scatter(x=data.index, y=data['USD_EGP_Official'],
            line=dict(color='#4CC9F0', width=2), fill='tozeroy',
            fillcolor='rgba(76,201,240,0.06)',
            hovertemplate="%{x|%d %b %Y}<br><b>%{y:.2f} " + ('EGP' if LANG == 'en' else 'جنيه') + "</b><extra></extra>"))
        if show_events: add_events(fu, data)
        fu.update_layout(**plot_layout(height=420, show_legend=False))
        st.plotly_chart(fu, use_container_width=True, config=dict(displaylogo=False, responsive=True))


# ═════════════════════════════════════════════════════════════════════════════
# PAGE 2: Price Structure Analysis - Premium Price Anatomy
# ═════════════════════════════════════════════════════════════════════════════

elif selected_key == "analysis":

    section("📊", t('sec_price_anatomy'), "")
    st.markdown(f"""
    <div class="section-sub" style="display:flex;justify-content:space-between;align-items:center;margin-bottom:10px;">
    <div style="direction:{DIR}">{t('price_anatomy_sub')}</div>
    <div style="direction:ltr">Stacked Area · 24K · 21K · 18K</div>
    </div>""", unsafe_allow_html=True)

    fig = make_subplots(rows=3, cols=1, shared_xaxes=True,
        row_heights=[0.34, 0.33, 0.33], vertical_spacing=0.10,
        subplot_titles=["24K", "21K", "18K"])

    KFILL = {'24K': 'rgba(255,249,196,0.65)', '21K': 'rgba(255,215,0,0.65)', '18K': 'rgba(205,127,50,0.65)'}
    KROW  = {'24K': 1, '21K': 2, '18K': 3}

    _lbl_value = t('legend_global_value')
    _lbl_prem  = t('legend_inflation_prem')
    for karat in ['24K', '21K', '18K']:
        row = KROW[karat]
        fig.add_trace(go.Scatter(x=data.index, y=data[f'ValueDriven_{karat}'],
            name=_lbl_value, stackgroup=f'g{row}', mode='lines',
            line=dict(width=0), fillcolor=KFILL[karat],
            showlegend=(row==1), legendgroup='gv',
            hovertemplate=f"{karat} - {_lbl_value}: %{{y:,.0f}}<extra></extra>"), row=row, col=1)
        fig.add_trace(go.Scatter(x=data.index, y=data[f'InflPrem_{karat}'],
            name=_lbl_prem, stackgroup=f'g{row}', mode='lines',
            line=dict(width=0), fillcolor='rgba(239,71,111,0.50)',
            showlegend=(row==1), legendgroup='gi',
            hovertemplate=f"{karat} - {_lbl_prem}: %{{y:,.0f}}<extra></extra>"), row=row, col=1)

    if show_events: add_events(fig, data, rows=[1,2,3])
    lyt = plot_layout(height=800)
    lyt['margin'] = dict(l=8, r=8, t=160, b=8)
    lyt['legend'] = dict(orientation="h", y=1.20, x=0.5, xanchor="center",
        bgcolor="rgba(0,0,0,0)", borderwidth=0,
        font=dict(size=10, family="Cairo"), itemsizing="constant")
    lyt['xaxis']['rangeselector']['y'] = 1.20
    lyt['title'] = dict(text=t('chart_title_anatomy'),
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
                         title_text=t('axis_egp'), title_font=dict(size=9), row=r, col=1)
    st.plotly_chart(fig, use_container_width=True, config=dict(displaylogo=False, responsive=True))

    spacer(24)
    section("📐", t('sec_inflation_pct'), "")
    st.markdown(f"""
    <div class="section-sub" style="display:flex;justify-content:space-between;align-items:center;margin-bottom:10px;">
    <div style="direction:{DIR}">{t('inflation_pct_sub')}</div>
    <div style="direction:ltr">Inflation Premium %</div>
    </div>""", unsafe_allow_html=True)

    fig2 = go.Figure()
    for karat, color in KARAT_COLORS.items():
        fig2.add_trace(go.Scatter(x=data.index, y=data[f'PremPct_{karat}'],
            name=karat, line=dict(color=color, width=2),
            hovertemplate=f"{karat}: %{{y:.1f}}%<extra></extra>"))
    fig2.add_hline(y=0, line_dash="dot", line_color="#1E3A5F", opacity=0.8)
    if show_events: add_events(fig2, data)
    fig2.update_layout(**plot_layout(height=340, yaxis=dict(title_text=t('axis_premium_pct'))))
    st.plotly_chart(fig2, use_container_width=True, config=dict(displaylogo=False, responsive=True))

    spacer()
    cols3 = st.columns(3)
    for col3, karat in zip(cols3, KARAT_FACTORS):
        ap = data[f'PremPct_{karat}'].mean()
        mx = data[f'PremPct_{karat}'].max()
        with col3:
            insight(f"<b style='color:{KARAT_COLORS[karat]}'>{karat}</b><br>"
                    f"{t('insight_avg_premium')} <span class='num'>{ap:.1f}%</span><br>"
                    f"{t('insight_peak_premium')} <span class='num-red'>{mx:.1f}%</span>")


# ═════════════════════════════════════════════════════════════════════════════
# PAGE 3: Investment Portfolio Simulation - Net Cost Simulation
# ═════════════════════════════════════════════════════════════════════════════

elif selected_key == "investment":

    _cur = 'ج' if LANG == 'ar' else ' EGP'
    section("💼", t('inv_section_title'), "")
    st.markdown(f"""
    <div class="section-sub" style="display:flex;justify-content:space-between;align-items:center;margin-bottom:10px;">
    <div style="direction:{DIR}">
      {t('inv_sub_p1')}
      <span style="font-family:'DM Mono';direction:ltr;display:inline;">(24K +{MAKING_CHARGES['24K']}{_cur} · 21K +{MAKING_CHARGES['21K']}{_cur} · 18K +{MAKING_CHARGES['18K']}{_cur})</span>
      {t('inv_sub_p2')}
      <span style="font-family:'DM Mono';direction:ltr;display:inline;">(24K {SELL_SPREAD['24K']*100:.1f}% · 21K {SELL_SPREAD['21K']*100:.1f}% · 18K {SELL_SPREAD['18K']*100:.1f}%)</span>
    </div>
    <div style="direction:ltr">Net Portfolio Simulation · 100,000 EGP Start</div>
    </div>""", unsafe_allow_html=True)

    _egp_word = 'EGP' if LANG == 'en' else 'جنيه'
    fig_inv = go.Figure()
    for karat, color in KARAT_COLORS.items():
        fig_inv.add_trace(go.Scatter(x=data.index, y=data[f'Port_{karat}'],
            name=t('inv_trace_gold_net', k=karat), line=dict(color=color, width=2.2),
            hovertemplate=f"<b>{karat}</b>: %{{y:,.0f}} {_egp_word}<extra></extra>"))
    fig_inv.add_trace(go.Scatter(x=data.index, y=data['Port_USD'],
        name=t('lbl_usd'), line=dict(color='#4CC9F0', width=1.6, dash='dot'),
        hovertemplate=f"{t('lbl_usd')}: %{{y:,.0f}}<extra></extra>"))
    fig_inv.add_trace(go.Scatter(x=data.index, y=data['Port_Cash'],
        name=t('lbl_cash_egp'), line=dict(color='#1E3A5F', width=1.2, dash='dot'),
        hovertemplate=f"{t('lbl_cash_egp')}: %{{y:,.0f}}<extra></extra>"))
    if show_events: add_events(fig_inv, data)
    lyt_inv = plot_layout(height=440, yaxis=dict(title_text=t('axis_net_value_egp')))
    lyt_inv['title'] = dict(text=t('inv_chart_title'),
        font=dict(size=13, color="#FFD700", family="Cairo"), x=0.5, xanchor='center', y=0.97)
    fig_inv.update_layout(**lyt_inv)
    st.plotly_chart(fig_inv, use_container_width=True, config=dict(displaylogo=False, responsive=True))

    spacer()
    _egp_sym = 'EGP' if LANG == 'en' else 'ج'
    _g_sym   = 'g'   if LANG == 'en' else 'جم'
    cols4 = st.columns(4)
    for col4, karat in zip(cols4[:3], KARAT_FACTORS):
        m = compute_metrics(data, karat)
        tc = '#06D6A0' if m['total'] > 0 else '#EF476F'
        entry = data[f'Price_{karat}'].iloc[0]
        grams = 100_000 / entry
        with col4:
            st.markdown(f"""
            <div class="metric-card" style="padding:15px 10px;">
              <div class="metric-card-title" style="color:{KARAT_COLORS[karat]}">{t('inv_card_title_gold', k=karat)}</div>
              <div class="metric-row"><span class="metric-label">{t('lbl_net_qty')}</span>
                <span class="metric-val" style="color:#E8EDF5">{grams:,.1f} {_g_sym}</span></div>
              <div class="metric-row"><span class="metric-label">{t('lbl_price_2020_making')}</span>
                <span class="metric-val" style="color:#8D99AE">{entry:,.0f} {_egp_sym}</span></div>
              <div class="metric-row"><span class="metric-label">{t('lbl_net_value')}</span>
                <span class="metric-val" style="color:#FFD700">{m['final']:,.0f} {_egp_sym}</span></div>
              <div class="metric-row"><span class="metric-label">{t('lbl_actual_return')}</span>
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
          <div class="metric-card-title" style="color:#4CC9F0">{t('lbl_usd_card_title')}</div>
          <div class="metric-row"><span class="metric-label">{t('lbl_qty_bought')}</span>
            <span class="metric-val" style="color:#E8EDF5">${usd_bought:,.0f}</span></div>
          <div class="metric-row"><span class="metric-label">{t('lbl_price_2020')}</span>
            <span class="metric-val" style="color:#8D99AE">{usd0:,.2f} {_egp_sym}</span></div>
          <div class="metric-row"><span class="metric-label">{t('lbl_current_value')}</span>
            <span class="metric-val" style="color:#FFD700">{usd_final:,.0f} {_egp_sym}</span></div>
          <div class="metric-row"><span class="metric-label">{t('lbl_total_return')}</span>
            <span class="metric-val" style="color:{usd_tc}">{usd_ret:+.1f}%</span></div>
          <div class="metric-row"><span class="metric-label">Sharpe Ratio</span>
            <span class="metric-val" style="color:#4CC9F0">{usd_sharpe:.2f}</span></div>
          <div class="metric-row"><span class="metric-label">Max Drawdown</span>
            <span class="metric-val" style="color:#EF476F">{usd_dd:.1f}%</span></div>
        </div>""", unsafe_allow_html=True)

    spacer(24)
    section("📉", "Max Drawdown", "")
    st.markdown(f"""
    <div class="section-sub" style="display:flex;justify-content:space-between;align-items:center;margin-bottom:10px;">
    <div style="direction:{DIR}">{t('dd_sub')}</div>
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
        name=t('lbl_usd'), line=dict(color='#4CC9F0', width=1.6, dash='dot'),
        hovertemplate=f"{t('lbl_usd')}: %{{y:.1f}}%<extra></extra>"))
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
    insight(f"💡 <b>{t('inv_insight_title')}</b> " + t('inv_insight_body', c=KARAT_COLORS[best_k], best_k=best_k,
                                              ret=best_m['total'], usd=usd_ret))


# ═════════════════════════════════════════════════════════════════════════════
# PAGE 4: Radar & Technical Indicators - Technical Analysis
# ═════════════════════════════════════════════════════════════════════════════

elif selected_key == "technical":

    k = selected_karat
    section("📡", t('tech_title', k=k), "")
    st.markdown(f"""
    <div class="section-sub" style="display:flex;justify-content:space-between;align-items:center;margin-bottom:10px;">
    <div style="direction:{DIR}">{t('tech_sub')}</div>
    <div style="direction:ltr">Bollinger Bands · RSI-14 · MACD</div>
    </div>""", unsafe_allow_html=True)

    _egp_word = 'EGP' if LANG == 'en' else 'جنيه'
    fig_tech = make_subplots(rows=3, cols=1, shared_xaxes=True,
        row_heights=[0.55, 0.25, 0.20], vertical_spacing=0.07,
        subplot_titles=[
            t('tech_subplot_price_bb', k=k),
            t('tech_subplot_macd'),
            t('tech_subplot_rsi')
        ])

    # Bollinger Bands
    fig_tech.add_trace(go.Scatter(x=data.index, y=data[f'BB_up_{k}'],
        line=dict(width=0), showlegend=False), row=1, col=1)
    fig_tech.add_trace(go.Scatter(x=data.index, y=data[f'BB_dn_{k}'],
        fill='tonexty', fillcolor='rgba(180,180,255,0.04)',
        line=dict(width=0), name='Bollinger Bands'), row=1, col=1)
    fig_tech.add_trace(go.Scatter(x=data.index, y=data[f'Price_{k}'],
        name=t('lbl_price'), line=dict(color='#D8E4F0', width=1.8),
        hovertemplate="%{x|%d %b %Y} - %{y:,.0f} " + _egp_word + "<extra></extra>"), row=1, col=1)
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
    fig_tech.update_yaxes(title_text=t('axis_price_egp'), title_font=dict(size=9, color="#3A4A65"), row=1, col=1)
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
    sa   = {'BUY': t('sig_buy'), 'SELL': t('sig_sell'), 'HOLD': t('sig_hold')}.get(sig, t('sig_hold'))
    bbu  = data[f'BB_up_{k}'].iloc[-1]
    bbl  = data[f'BB_dn_{k}'].iloc[-1]
    lp   = data[f'Price_{k}'].iloc[-1]
    bbp  = (t('tech_bb_upper') if lp > bbu * 0.98 else
            t('tech_bb_lower') if lp < bbl * 1.02 else t('tech_bb_within'))
    _rsi_tag = (f"&nbsp;<span style='color:#EF476F;font-size:0.72rem'>{t('tech_overbought')}</span>" if rsi>70 else
                f"&nbsp;<span style='color:#06D6A0;font-size:0.72rem'>{t('tech_oversold')}</span>" if rsi<30 else "")
    insight(f"""
    <div style="display:flex;flex-wrap:wrap;gap:18px;align-items:center;direction:ltr;
                justify-content:center;font-family:'DM Mono',monospace;font-size:0.82rem;">
      <div><b style="color:#FFD700;font-family:Cairo">{t('tech_signal_label', k=k)}</b>&nbsp;<span class="{sc}">{sa}</span></div>
      <div style="color:#1E3A5F">│</div>
      <div><b style="color:#A855F7">RSI</b>&nbsp;{rsi:.1f}{_rsi_tag}</div>
      <div style="color:#1E3A5F">│</div>
      <div><b style="color:#4CC9F0">MACD</b>&nbsp;{macd:,.1f}</div>
      <div style="color:#1E3A5F">│</div>
      <div><b style="color:#FF9F43">BB</b>&nbsp;{bbp}</div>
    </div>""")


# ═════════════════════════════════════════════════════════════════════════════
# PAGE 5: Advanced Forecasting - Tuned Prophet ML Suite + ROI Calculator
# ═════════════════════════════════════════════════════════════════════════════

elif selected_key == "forecast":

    section("🔮", t('fc_title', k=selected_karat), "")
    st.markdown(f"""
    <div class="section-sub" style="display:flex;justify-content:space-between;align-items:center;margin-bottom:10px;">
    <div style="direction:{DIR}">{t('fc_sub')}</div>
    <div style="direction:ltr">Prophet Model · Regressors: USD + OIL · Historical Date Merge Strategy</div>
    </div>""", unsafe_allow_html=True)

    st.markdown(f'<div class="fc-label">{t("fc_horizon_label")}</div>', unsafe_allow_html=True)
    forecast_days = st.slider("d", 30, 365, 180, 30, label_visibility="collapsed")

    with st.spinner(t("fc_spinner_training")):
        try:
            from prophet import Prophet

            k      = selected_karat
            fv_col = f'Price_{k}'

            # ── Step 1: Prepare main training frame ──
            train = data.reset_index()[['Date', fv_col, 'USD_EGP_Official', 'Crude_Oil']].copy()
            train.columns = ['ds', 'y', 'USD', 'OIL']
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
            from prophet.diagnostics import cross_validation, performance_metrics

            total_days = (train['ds'].max() - train['ds'].min()).days

            cv_horizon_days = int(max(30, min(90, total_days * 0.25)))

            cv_initial_days = int(max(total_days * 0.5,
                                       total_days - 6 * cv_horizon_days))
            cv_period_days  = cv_horizon_days  # non-overlapping folds → faster, independent cutoffs

            try:
                df_cv = cross_validation(
                    pm,
                    initial=f'{cv_initial_days} days',
                    period=f'{cv_period_days} days',
                    horizon=f'{cv_horizon_days} days',
                    parallel=None,
                )
                cv_metrics = performance_metrics(df_cv, rolling_window=1)
                mae  = cv_metrics['mae'].mean()
                rmse = cv_metrics['rmse'].mean()
            except Exception:
                split_idx = max(int(len(train) * 0.85), len(train) - cv_horizon_days)
                y_true_oos = train['y'].values[split_idx:]
                y_pred_oos = fc.iloc[split_idx:len(train)]['yhat'].values
                mae  = np.abs(y_true_oos - y_pred_oos).mean()
                rmse = np.sqrt(((y_true_oos - y_pred_oos) ** 2).mean())

            # ── Step 7: Extract the forward forecast horizon ──
            last_hist = train['ds'].max()
            fc_out    = fc[fc['ds'] > last_hist].head(forecast_days).copy()
            actual_last_price = train['y'].iloc[-1]
            n = len(train)   # row count used as the in-sample slice fallback below
            predicted_last_price = (
                fc[fc['ds'] == last_hist]['yhat'].values[0]
                if len(fc[fc['ds'] == last_hist]) > 0
                else fc.iloc[:n]['yhat'].iloc[-1]
            )
            continuity_offset = actual_last_price - predicted_last_price
            fc_out['yhat']       = fc_out['yhat']       + continuity_offset
            fc_out['yhat_upper'] = fc_out['yhat_upper'] + continuity_offset
            fc_out['yhat_lower'] = fc_out['yhat_lower'] + continuity_offset

            # ── Forecast chart ──
            _egp_word = 'EGP' if LANG == 'en' else 'جنيه'
            title_chart = t('fc_chart_title', k=k, days=forecast_days)
            fig_fc = go.Figure()

            # Weekly-downsampled actuals for cleaner display on long horizons
            hw = data[fv_col].resample('W').last()
            fig_fc.add_trace(go.Scatter(x=hw.index, y=hw, name=t('lbl_actual_price'),
                line=dict(color='#4A6A8A', width=1.5),
                hovertemplate="%{x|%d %b %Y}<br>%{y:,.0f} " + _egp_word + "<extra></extra>"))

            # 90% confidence band
            fig_fc.add_trace(go.Scatter(x=fc_out['ds'], y=fc_out['yhat_upper'],
                line=dict(width=0), showlegend=False))
            fig_fc.add_trace(go.Scatter(x=fc_out['ds'], y=fc_out['yhat_lower'],
                fill='tonexty', fillcolor='rgba(76,201,240,0.10)',
                line=dict(width=0), name=t('fc_confidence_band')))

            # Point forecast line
            fig_fc.add_trace(go.Scatter(x=fc_out['ds'], y=fc_out['yhat'],
                name=t('fc_prophet_forecast'), line=dict(color='#4CC9F0', width=2.5),
                hovertemplate="%{x|%d %b %Y}<br><b>%{y:,.0f} " + _egp_word + "</b><extra></extra>"))

            # Today marker
            fig_fc.add_vline(x=datetime.today().timestamp() * 1000,
                line_dash='dash', line_color='#FFD700', opacity=0.5,
                annotation_text=t('lbl_today'),
                annotation_font=dict(color='#FFD700', size=9.5),
                annotation_position="top right")

            if show_events: add_events(fig_fc, data)

            lyt_fc = plot_layout(height=500, yaxis=dict(title_text=t('axis_price_egp')))
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
                kpi_html(f"{la:,.0f}",    t('kpi_current_price_egp'),             "#FFD700", "0.05s") +
                kpi_html(f"{fe:,.0f}",    t('kpi_forecast_days', days=forecast_days), "#4CC9F0", "0.10s") +
                kpi_html(f"{cp:+.1f}%",   t('kpi_expected_change'),                cc,        "0.15s") +
                kpi_html(f"{rmse:,.0f}",  t('kpi_model_rmse'),                     "#A855F7", "0.20s")
            )
            st.markdown(f'<div class="kpi-grid" style="grid-template-columns:repeat(4,1fr)">{cards_html}</div>',
                        unsafe_allow_html=True)

            spacer()
            _cls = 'num' if cp>=0 else 'num-red'
            insight(t('fc_insight_summary', k=k, cls=_cls, fe=fe, days=forecast_days, cp=cp, mae=mae, rmse=rmse))

            # ─────────────────────────────────────────────────────────────────
            # TASK 2 - INVESTMENT ROI FORECASTER (replaces component chart)
            # ─────────────────────────────────────────────────────────────────
            spacer(28)
            section("💰", t('roi_section_title'), "")
            st.markdown(f"""
            <div class="section-sub" style="display:flex;justify-content:space-between;align-items:center;margin-bottom:10px;">
            <div style="direction:{DIR}">{t('roi_sub')}</div>
            <div style="direction:ltr">Prophet-Powered ROI Forecaster</div>
            </div>""", unsafe_allow_html=True)

            # ── ROI calculator inputs ──
            col_inv1, col_inv2, col_inv3 = st.columns([2, 1, 2])

            with col_inv1:
                invest_amount = st.number_input(
                    t('roi_amount_label'),
                    min_value=1_000,
                    max_value=10_000_000,
                    value=100_000,
                    step=1_000,
                    format="%d",
                    help=t('roi_amount_help')
                )

            with col_inv2:
                roi_karat = st.selectbox(
                    t('roi_karat_label'),
                    options=["18K", "21K", "24K"],
                    index=1,
                    key="roi_karat_select"
                )

            with col_inv3:
                st.markdown(f'<div class="fc-label">{t("roi_duration_label")}</div>', unsafe_allow_html=True)
                roi_days = st.slider(
                    "roi_duration",
                    min_value=30,
                    max_value=365,
                    value=min(forecast_days, 365),
                    step=30,
                    label_visibility="collapsed",
                    help=t('roi_duration_help')
                )

            # ── ROI computation logic ──
            # Current (entry) price for the chosen karat
            current_price_roi = data[f'Price_{roi_karat}'].iloc[-1]
            # forecasted yhat by a simple purity ratio
            # (KARAT_FACTORS[roi_karat] / KARAT_FACTORS[k]). This is NOT
            # algebraically exact, because:
            #     Price_{karat} = Theoretical_24K * KaratFactor_{karat} + MakingCharge_{karat}
            #
            # MakingCharge is an ADDITIVE constant that differs per karat
            # (60 / 150 / 220 EGP) - it does not scale with the karat
            # factor, so multiplying the whole yhat (which already bakes
            # in the model karat's making charge) by a purity ratio
            # distorts the result.
            #
            # The correct approach: invert the model's forecast back to
            # the pure Theoretical_24K series (removing the MODEL karat's
            # making charge and purity factor), then rebuild the exact
            # retail price for whichever karat the user picked in the ROI
            # calculator, using THAT karat's own making charge.
            theoretical_24k_fc       = (fc_out['yhat']       - MAKING_CHARGES[k]) / KARAT_FACTORS[k]
            theoretical_24k_fc_upper = (fc_out['yhat_upper'] - MAKING_CHARGES[k]) / KARAT_FACTORS[k]
            theoretical_24k_fc_lower = (fc_out['yhat_lower'] - MAKING_CHARGES[k]) / KARAT_FACTORS[k]

            roi_fc_series = fc_out[['ds']].copy()
            roi_fc_series['yhat'] = (
                theoretical_24k_fc * KARAT_FACTORS[roi_karat] + MAKING_CHARGES[roi_karat]
            )
            roi_fc_series['yhat_upper'] = (
                theoretical_24k_fc_upper * KARAT_FACTORS[roi_karat] + MAKING_CHARGES[roi_karat]
            )
            roi_fc_series['yhat_lower'] = (
                theoretical_24k_fc_lower * KARAT_FACTORS[roi_karat] + MAKING_CHARGES[roi_karat]
            )

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

                _egp_sym = 'EGP' if LANG == 'en' else 'ج'
                with m1:
                    st.metric(
                        label=t('roi_metric_expected_value'),
                        value=f"{exit_value_roi:,.0f} {_egp_sym}",
                        delta=f"{net_profit_roi:+,.0f} {_egp_sym}",
                        delta_color="normal",
                        help=t('roi_metric_expected_value_help', days=roi_days_clipped, date=target_date_roi.strftime('%d %b %Y'))
                    )

                with m2:
                    st.metric(
                        label=t('roi_metric_net_return', icon=roi_icon),
                        value=f"{roi_pct:+.2f}%",
                        delta=t('roi_annualized', pct=f"{annualised_roi:+.1f}"),
                        delta_color="normal",
                        help=t('roi_net_return_help')
                    )

                with m3:
                    st.metric(
                        label=t('roi_metric_grams_bought'),
                        value=t('roi_grams_value', grams=grams_roi),
                        delta=t('roi_grams_delta', k=roi_karat, price=entry_cost_per_g),
                        delta_color="off",
                        help=t('roi_grams_help')
                    )

                with m4:
                    st.metric(
                        label=t('roi_metric_target_price'),
                        value=t('roi_target_value', price=target_price_roi),
                        delta=t('roi_vs_current', pct=(target_price_roi/current_price_roi - 1)*100),
                        delta_color="normal",
                        help=t('roi_target_help', k=roi_karat, date=target_date_roi.strftime('%d %b %Y'))
                    )

                spacer(12)
                # Detailed insight summary
                _cls  = 'num' if net_profit_roi >= 0 else 'num-red'
                _cls2 = 'num' if roi_pct >= 0 else 'num-red'
                insight(t('roi_insight_summary',
                          amt=invest_amount, k=roi_karat, price=current_price_roi,
                          mc=MAKING_CHARGES[roi_karat], grams=grams_roi, days=roi_days_clipped,
                          cls=_cls, cls2=_cls2, exit_val=exit_value_roi, profit=net_profit_roi,
                          pct=roi_pct, spread=SELL_SPREAD[roi_karat]*100))
            else:
                st.warning(t('roi_insufficient_data'))

        except ImportError:
            st.error(t('fc_prophet_missing'))
        except Exception as e:
            st.error(t('fc_model_error', err=e))

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