<div align="center">

![Gold Egypt · Investment Decision Framework](cover.png)

<br/>

<img src="https://readme-typing-svg.demolab.com?font=Fira+Code&weight=700&size=20&pause=1000&color=FFD700&center=true&vCenter=true&width=600&lines=%F0%9F%A5%87+GOLD+EGYPT+%C2%B7+Financial+Intelligence" alt="Typing SVG" />

<br/>

<p>
  <img src="https://img.shields.io/badge/Python-3.10+-FFD700?style=for-the-badge&logo=python&logoColor=black" />
  <img src="https://img.shields.io/badge/Streamlit-App-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white" />
  <img src="https://img.shields.io/badge/Plotly-Interactive-3F4F75?style=for-the-badge&logo=plotly&logoColor=white" />
  <img src="https://img.shields.io/badge/Prophet-Forecasting-4CC9F0?style=for-the-badge&logo=meta&logoColor=white" />
  <img src="https://img.shields.io/badge/DEPI-2026-06D6A0?style=for-the-badge" />
</p>

</div>

---

## Project Name

**Gold Egypt** - Gold as a Financial Instrument in Egypt
*Fair Value Decomposition · Crisis Analysis · Retail Investor Decision Framework*

---

## Project Idea

> **Is gold's rise in Egypt real wealth - or just a reflection of the Egyptian pound's collapse?**

**Gold Egypt** is a full-stack financial data science project that uncovers the truth behind gold price movements in Egypt since January 2020 - through COVID-19, the Russia–Ukraine war, currency floatation events, and beyond.

The project decomposes the local gold price into three measurable components:

```
Local Gold Price  =  Global Value Component
                   + Exchange Rate Component
                   + Local Market Premium (Bubble)
```

It delivers an interactive, premium dark-mode dashboard with live **BUY / HOLD / SELL** signals powered by statistical and machine-learning models.

**Central Research Question:**
```
Can we decompose Egyptian gold price movements into global value,
currency impact, and local premium components - and build a
data-driven model that supports retail investors in distinguishing
fair value from panic-driven pricing?
```

| Info | Details |
|---|---|
| **Program** | Digital Egypt Pioneers Initiative (DEPI) |
| **Track** | Data Analysis |
| **Project Type** | Financial Data Science Project |
| **Year** | 2026 |
| **Data Period** | January 2020 – Present |
| **Tools** | Python · Streamlit · Plotly · Prophet · yfinance · pandas · numpy · statsmodels |

---

## Team Members

1. `[Team Member Name 1]`
2. `[Team Member Name 2]`
3. `[Team Member Name 3]`

---

## Project Plan

1. **Research & Analysis**
   - Audience personas - Retail investors, students, financial analysts
   - Literature review - Gold as hedge vs. safe haven (Baur & Lucey, 2010)
   - Data collection - Yahoo Finance API (`GC=F`, `EGP=X`, `CL=F`, `^TNX`, `^GSPC`)

2. **Visual Identity**
   - Logo design - Dark-gold luxury fintech aesthetic
   - Color system - `#FFD700` Gold · `#1A1A2E` Dark · `#06D6A0` Emerald
   - Typography - Cairo · Bebas Neue (Display) · DM Mono (Data)

3. **Main Designs**
   - Poster - A2 print-ready project summary
   - Dashboard UI - 6-page Streamlit app with premium CSS
   - Chart system - Plotly dark-mode (price, correlation, decomposition)

4. **Complementary Products**
   - Academic report - Fair Value Decomposition methodology paper
   - Clean dataset - Publication-ready financial CSV (Jan 2020 – Present)
   - Econometric report - Regression results & crisis window analysis

5. **Review & Finalization**
   - Model accuracy evaluation - MAE / RMSE benchmarking
   - Dashboard testing - Mobile-first responsive validation
   - Peer review & mentor feedback integration

6. **Final Presentation**
   - Live dashboard demo - Streamlit deployment
   - DEPI cohort presentation - Slides + poster
   - GitHub repository - Open-source release with full documentation

---

## Roles & Responsibilities

- **[Member 1]** - Data Engineering & Econometric Analysis
- **[Member 2]** - Dashboard Development & UI/UX (Streamlit + Plotly)
- **[Member 3]** - Forecasting Models (Prophet) & Academic Report Writing

---

## KPIs (Key Performance Indicators)

Metrics for project success:

- **Forecast Accuracy** - MAE < 500 EGP · RMSE < 800 EGP on held-out test set
- **Model Coverage** - R² > 0.85 for multiple regression on gold price drivers
- **Dashboard Performance** - All 6 pages load under 3 seconds · fully functional
- **Data Completeness** - < 2% missing values across all time series (Jan 2020–Present)
- **Signal Quality** - BUY / SELL signals backtested against historical returns
- **User Adoption** - Tested with at least 5 target-audience users (retail investors)

---

## Instructor

`[Instructor Name]`

---

## Project Files

You can find the full project files here:

- **GitHub:** `https://github.com/your-username/gold-egypt`
- **Live App:** `https://your-app.streamlit.app`

---
---

## ✨ Dashboard Pages

| Page | Description |
|---|---|
| 🏠 **Home** | Live KPIs · Gold price chart · USD/EGP trend · Correlation matrix |
| 📊 **Price Analysis** | Fair value decomposition for 18K / 21K / 24K · Inflation premium % |
| ⚖️ **Karat Comparison** | Normalized returns vs. USD & Cash · Sharpe / VaR metrics table |
| 💼 **Investment Simulation** | 100,000 EGP invested in Jan 2020 · Max Drawdown · Full risk metrics |
| 📡 **Technical Analysis** | Bollinger Bands · MACD · RSI-14 · Auto BUY / SELL / HOLD signals |
| 🔮 **Forecasting** | Prophet model with USD + Oil regressors · MAE/RMSE · 95% confidence interval |

---

## 🧮 Core Decomposition Formula

```python
# Theoretical gold price per gram in EGP
Theoretical_Price (EGP/gram) = (Global_Gold_USD_oz × USD_EGP_Rate) / 31.1035

# Local market premium (bubble component)
Local_Premium = Actual_Local_Price - Theoretical_Price

# Premium percentage
Premium_Pct (%) = (Local_Premium / Actual_Local_Price) * 100
```

> When `Premium_Pct` is **high** → the market is pricing in fear, not value.
> When it's **near zero** → the price closely reflects global fundamentals.

---

## 🛠️ Tech Stack

```
📦 Data Layer
├── yfinance          →  Yahoo Finance API  (GC=F · EGP=X · CL=F · ^TNX · ^GSPC)
├── pandas            →  Data wrangling, time-series alignment, resampling
└── numpy             →  Vectorized computations, feature engineering

📐 Analytics Layer
├── statsmodels       →  Econometric modeling & multiple linear regression
├── scikit-learn      →  Statistical analysis utilities
├── Prophet           →  Time-series forecasting with external regressors
└── Custom            →  RSI-14 · MACD · Bollinger Bands · Sharpe Ratio · VaR

🖥️ Application Layer
├── Streamlit         →  Multi-page interactive web dashboard
├── Plotly            →  Area, scatter, heatmap, and multi-panel charts
└── Custom CSS        →  Luxury dark-mode UI (Cairo · Bebas Neue · DM Mono fonts)
```

---

## ⚡ Quick Start

### 1. Clone the repository
```bash
git clone https://github.com/your-username/gold-egypt.git
cd gold-egypt
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Run the app
```bash
streamlit run app_2.py
```

> The app will open automatically at `http://localhost:8501` 🚀

---

## 📋 Requirements

```txt
streamlit>=1.32
pandas>=2.0
numpy>=1.24
plotly>=5.18
yfinance>=0.2
prophet>=1.1
scikit-learn>=1.3
statsmodels>=0.14
```

---

## 📊 Data Sources

| Source | Ticker | Variable | Purpose |
|---|---|---|---|
| Yahoo Finance | `GC=F` | Global Gold Futures | International gold benchmark |
| Yahoo Finance | `EGP=X` | USD/EGP Exchange Rate | Currency impact analysis |
| Yahoo Finance | `CL=F` | Crude Oil (WTI) | Macro indicator |
| Yahoo Finance | `^TNX` | US 10Y Treasury Yield | Safe-haven comparison |
| Yahoo Finance | `^GSPC` | S&P 500 Index | Risk-on / risk-off proxy |
| CBE / IMF | - | Inflation & Interest Rates | Econometric modeling |
| Market Data | - | 18K / 21K / 24K Local Prices | Local price tracking |

> All data is **daily frequency** · January 2020 → Present

---

## 🗂️ Project Structure

```
gold-egypt/
│
├── app_2.py               # 🚀  Main Streamlit application (all 6 pages)
├── requirements.txt       # 📦  Python dependencies
├── Proposal.docx          # 📄  Academic project proposal (DEPI)
└── README.md              # 📖  This file
```

---

## 🔬 Methodology

```
Phase 1 ── Data Engineering & Preprocessing
           Data cleaning · missing value handling · outlier detection
           Time-series alignment · feature engineering (returns, volatility,
           rolling averages, RSI, MACD, Bollinger Bands)

Phase 2 ── Fair Value Decomposition
           Compute Theoretical Price = (Global Gold × USD/EGP) / 31.1
           Calculate Local Premium = Actual − Theoretical
           Separate global / currency / local distortion components

Phase 3 ── Econometric & Crisis Analysis
           Correlation matrix · trend & volatility analysis
           Multiple linear regression · crisis window comparative analysis

Phase 4 ── Investment Performance Simulation
           Simulate 100,000 EGP invested in Gold 21K/24K/18K, USD, and Cash
           Compute nominal/real return · volatility · Max Drawdown · Sharpe · VaR

Phase 5 ── Forecasting Models
           Moving Average · ARIMA · Prophet with external regressors
           Evaluate with MAE and RMSE · 6-month and 1-year horizons

Phase 6 ── Decision Support Framework
           Fair Value Index · RSI & MACD crossover signals
           Output: BUY / HOLD / OVERPRICED / HIGH RISK signal
```

---

## 📈 Crisis Events Tracked

| Date | Event | Market Impact |
|---|---|---|
| Mar 2020 | 🦠 COVID-19 Pandemic | Global shock · flight to safety |
| Feb 2022 | 🇺🇦 Russia–Ukraine War | Commodity surge · geopolitical risk |
| Mar 2022 | 📉 EGP Floatation I | Sharp EGP depreciation · gold spike |
| Oct 2022 | 📉 EGP Floatation II | Continued currency pressure |
| Mar 2024 | 🔓 Major EGP Floatation | Structural reform · CBE + IMF deal |

---

## 📐 Financial Metrics Computed

| Metric | Formula / Method |
|---|---|
| **Total Return** | `(Final Value / Initial − 1) × 100` |
| **Annualized Return** | `mean(daily_returns) × 252` |
| **Sharpe Ratio** | `Annualized Return / Annualized Volatility` |
| **Max Drawdown** | `min((Price / cummax(Price)) − 1) × 100` |
| **VaR 95%** | `5th percentile of daily returns` |
| **RSI-14** | Wilder's Relative Strength Index (14-day) |
| **MACD** | `EMA(12) − EMA(26)` with signal line `EMA(9)` |
| **Bollinger Bands** | `SMA(20) ± 2 × STD(20)` |
| **Fair Value Index** | `Actual Price / Theoretical Price` |

---

## 🎓 Academic & Social Value

- Provides the **first quantitative decomposition** of Egyptian gold price drivers into global, exchange-rate, and local components
- Distinguishes **real value appreciation** from **exchange-rate-driven distortions** in local pricing
- Evaluates gold empirically as a **hedge against Egyptian inflation** and currency depreciation
- Delivers a **practical, data-driven decision-support tool** accessible to small retail investors
- Bridges **financial economics with applied data science** in the Egyptian market context
- Contributes an **open, clean financial dataset** for future academic research

---

## 📚 References

- Baur, D. G., & Lucey, B. M. (2010). *Is Gold a Hedge or a Safe Haven? An Analysis of Stocks, Bonds and Gold.* - Journal of Financial Economics.
- World Gold Council - Annual and Quarterly Gold Demand Trends Reports.
- Yahoo Finance - Historical Market Data (`GC=F`, `EGP=X`, `S&P500`, `Oil`, `Treasuries`).
- International Monetary Fund (IMF) - Egypt Economic Outlook Reports, 2020–2024.
- Central Bank of Egypt (CBE) - Monetary Policy Statements and Exchange Rate History.
- Prophet Documentation - [Facebook/Meta Open Source Forecasting Library](https://facebook.github.io/prophet/)

---

<div align="center">

**Built with ❤️ + 🥇 in Egypt**

<sub>DEPI Final Project · 2026 · Gold as a Financial Instrument in Egypt</sub>

<br/>

<img src="https://img.shields.io/badge/%F0%9F%A5%87%20Gold%20Egypt-DEPI%202026-FFD700?style=for-the-badge" />

</div>

---

## ⚖️ License

Copyright (c) 2026 Mahmoud Shamoun

All rights reserved.

This project is shared for **portfolio and demonstration purposes only**.

No one is allowed to copy, modify, distribute, reuse, or sell any part of this code or project without explicit written permission from the author.

Unauthorized use of this code is strictly prohibited.
