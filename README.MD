# 15-Year Multi-Timeframe Quantitative Backtesting System
### NASDAQ 100 (QQQ) & S&P 500 (SPY) | 2011 – 2026 Audit

An institutional-grade algorithmic backtesting engine that simulates and verifies a **Multi-Timeframe Support/Resistance & Flag Breakout-and-Retest Strategy** across 15 full years (3,772 daily trading sessions).

---

## Executive Summary: What It Actually Does

In simple terms, this software proves whether a pure price-action strategy—trading **Support & Resistance** and **Bull/Bear Flags** with a **strict 3-touch rule** and a **30-minute breakout-and-retest confirmation**—is consistently profitable over 15 years on the world's most liquid index markets (NASDAQ and S&P 500).

```
+----------------------------------------------------------------------------------------------------+
|                                    STRATEGY EXECUTION PIPELINE                                     |
|                                                                                                    |
|  [ 1. DAILY REGIME ]   ----->  Reads 1D Trend (200 EMA): Is market BULLISH or BEARISH?             |
|                                      |                                                             |
|  [ 2. 4H ZONE DETECTION ] --->  Marks S/R & Flags: Counts touches (EXACT / WITHIN 3 TAPS ONLY)     |
|                                 * If tapped > 3 times -> REJECTS as sideways chop / NO TRADE       |
|                                      |                                                             |
|  [ 3. 30M BREAKOUT ]   ----->  Waits for price to close cleanly outside the 4H zone/flag           |
|                                      |                                                             |
|  [ 4. 30M RETEST ]     ----->  Waits for price to PULL BACK / RETEST the broken S/R zone           |
|                                      |                                                             |
|  [ 5. CONFIRMATION ]   ----->  Detects Bull/Bear candlestick patterns (Hammer, Engulfing, etc.)    |
|                                      |                                                             |
|  [ 6. EXECUTION ]      ----->  Enters position with strict 1:1 Risk-to-Reward (RR)                 |
|                                      |                                                             |
|  [ 7. FILTERS ]        ----->  New York Session ONLY (09:30-16:00 ET) | Skips NFP, CPI, FOMC, GDP  |
+----------------------------------------------------------------------------------------------------+
```

---

##  How the Strategy Works (Step-by-Step)

### Step 1: 1-Day (1D) Timeframe — Higher-Timeframe Market Bias
The algorithm first reads the overarching market direction on the daily chart:
* **Bullish Market Regime**: Daily Close $\ge$ 200 EMA. The engine will **ONLY look for LONG setups** (Bull Flags, Resistance Breakout-and-Retests, Support Bounces).
* **Bearish Market Regime**: Daily Close < 200 EMA. The engine will **ONLY look for SHORT setups** (Bear Flags, Support Breakdown-and-Retests, Resistance Rejections).
* *Purpose*: Prevents counter-trend trades and ensures trading strictly with institutional flow.

### Step 2: 4-Hour (4H) Timeframe — Support, Resistance & Flag Zone Identification
The engine analyzes intermediate 4H price action and identifies key levels and slanted flags:
* **The Strict 3-Taps Rule**: The zone must have been tapped **within/exactly 3 times** ($2 \le \text{taps} \le 3$).
* **The Sideways Filter**: If price touches the zone **more than 3 times** ($\text{taps} > 3$), the system marks the market as **Sideways / Range-Bound Chop** and **REJECTS the trade completely**.
* **Slanted Flags & Dynamic Trendlines**: Support and resistance are not limited to flat horizontal lines:
  * **Bull Flag**: Sharp upward pole followed by a downward-slanted parallel channel with 3 boundary taps.
  * **Bear Flag**: Sharp downward pole followed by an upward-slanted parallel channel with 3 boundary taps.

### Step 3: 30-Minute (30M) Timeframe — Breakout, Retest & Pattern Confirmation
Once a 4H zone with 3 taps is validated, the system zooms into the 30-minute execution timeframe:
1. **The Breakout**: Price must close cleanly outside the 4H zone or flag boundary. (If price retreats back into the zone without breaking, it is skipped).
2. **The Retest (Pullback)**: The algorithm does **not** chase the initial breakout. It patiently waits for price to pull back and retest the broken level:
   * Broken Resistance becomes new **Support**.
   * Broken Support becomes new **Resistance**.
3. **The Confirmation Pattern**: Price must print a recognized reversal/continuation pattern at the retest area:
   * **Bullish Retests**: Hammer / Pin Bar rejecting support, Bullish Engulfing candle, Bullish Retest Bounce candle, Three White Soldiers.
   * **Bearish Retests**: Shooting Star / Pin Bar rejecting resistance, Bearish Engulfing candle, Bearish Retest Rejection candle, Three Black Crows.

### Step 4: Position Sizing & Fixed 1:1 Risk-to-Reward (RR)
* **Risk (1R)**: Stop Loss is placed just beyond the retest swing extreme or broken zone boundary ($1.0\%$ account risk).
* **Reward (1R)**: Take Profit is set at **exactly 1.0x the Stop Loss distance** ($1:1\text{ RR}$).
* *Mathematics*: With a 1:1 RR, any win rate above $50.0\%$ generates a permanent mathematical edge.

---

## Strict Execution Guardrails & Filters

1. **New York Session Isolation ONLY**:
   * All trade entries must occur during regular US cash market hours: **09:30 AM to 16:00 PM Eastern Time**.
   * Trades during Asian session, London session, and pre-market overlap hours are **strictly skipped** to eliminate illiquid wicks and erratic overnight spreads.

2. **Macroeconomic News Filter**:
   * The system automatically scans the calendar and **skips trades** on days containing high-impact macroeconomic announcements:
     * **Non-Farm Payrolls (NFP)**: First Friday of every month.
     * **Consumer Price Index (CPI)**: Mid-month inflation release window.
     * **FOMC Interest Rate Decisions**: 8 scheduled Federal Reserve Wednesdays per year.
     * **Advance GDP**: Quarterly Advance economic output releases.

---

## 15-Year Backtest Results (2011 – 2026)

Across 15 full years, 3,772 daily cash sessions, and ~98,000 thirty-minute bars, the engine recorded:

```
  =============================================================================
                          15-YEAR STRATEGY PERFORMANCE AUDIT
  =============================================================================
  Initial Starting Capital     : $100,000.00 (Anchored Baseline)
  Final Net Capital            : $145,890.31
  Total Net Profit             : +$45,890.31 (+45.89% Net Return)
  -----------------------------------------------------------------------------
  Total Completed Trades       : 647 Trades (SPY: 253 | QQQ: 394)
  Winning Trades               : 344 Wins
  Losing Trades                : 303 Losses
  Overall Win Rate             : 53.17% (Positive Expectancy on 1:1 RR)
  Profit Factor                : 1.14
  Max Peak-to-Trough Drawdown  : 23.20%
  =============================================================================
```

### Annual Performance Breakdown

| Calendar Year | Total Trades | Wins | Losses | Win Rate % | Annual P&L ($) | Annual Return % | Market Regime Context |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: | :--- |
| **2011** | 49 | 24 | 25 | **49.0%** | -$1,203.98 | -1.20% | US Debt Downgrade / Chop |
| **2012** | 51 | 22 | 29 | **43.1%** | -$6,744.81 | -6.74% | European Debt Crisis |
| **2013** | 26 | 16 | 10 | **61.5%** | **+$5,771.20** | **+5.77%** | Taper Tantrum Bull Market |
| **2014** | 31 | 17 | 14 | **54.8%** | **+$2,787.94** | **+2.79%** | Steady Growth Cycle |
| **2015** | 39 | 22 | 17 | **56.4%** | **+$4,747.68** | **+4.75%** | China Devaluation Volatility |
| **2016** | 41 | 21 | 20 | **51.2%** | **+$874.84** | **+0.87%** | Brexit & US Election |
| **2017** | 17 | 10 | 7 | **58.8%** | **+$2,909.32** | **+2.91%** | Low-Volatility Bull Trend |
| **2018** | 49 | 31 | 18 | **63.3%** | **+$13,786.46** | **+13.79%** | Fed QT Volatility Squeeze |
| **2019** | 29 | 13 | 16 | **44.8%** | -$3,315.97 | -3.32% | Trade War Tariff Noise |
| **2020** | 56 | 26 | 30 | **46.4%** | -$3,453.19 | -3.45% | Global Pandemic Shock |
| **2021** | 40 | 21 | 19 | **52.5%** | **+$2,822.22** | **+2.82%** | Post-Pandemic Liquidity Boom |
| **2022** | 87 | 41 | 46 | **47.1%** | -$3,892.56 | -3.89% | Tech Bear Market / Fed Hikes |
| **2023** | 48 | 28 | 20 | **58.3%** | **+$8,570.07** | **+8.57%** | AI Infrastructure Expansion |
| **2024** | 40 | 27 | 13 | **67.5%** | **+$15,623.17** | **+15.62%** | High-Momentum Tech Rally |
| **2025** | 44 | 25 | 19 | **56.8%** | **+$6,604.61** | **+6.60%** | Trend Continuation |

---

## Web Dashboard & UI Features

The dashboard at [`ui/index.html`](file:///C:/Users/zakiy/backtest_system/ui/index.html) provides an institutional visual interface:

1. **Split-Color Equity Curve Anchored at $100,000**:
   * The baseline starts at **$100,000** (initial capital).
   * **Green Profit Shading (> $100k)**: Whenever account equity is in profit, the curve transitions to vibrant emerald green (`#3fb950`).
   * **Red Drawdown Shading (< $100k)**: If equity drops into drawdown below the initial $100k, the curve transitions to crimson red (`#f85149`).
   * **Chart Height**: Set to a massive **560px** for clear inspection.

2. **Enlarged High-Resolution Pattern Charts**:
   * Saved at **16 × 9.2 inches @ 180 DPI** in [`screenshots/`](file:///C:/Users/zakiy/backtest_system/screenshots).
   * **Clear 4H S/R Shading**: Bold colored zones with hatched texture.
   * **Explicit 3-Tap Badges**: Labeled **`TAP 1`**, **`TAP 2`**, and **`TAP 3`** on the swing wicks.
   * **Step-by-Step Flow**:
     - `1. 30M BREAKOUT OUTSIDE ZONE` (Purple arrow)
     - `2. RETEST / PULLBACK INTO S/R ZONE` (Gold arrow)
     - `3. PATTERN CONFIRMATION & ENTRY` (Blue arrow)
   * **1:1 RR Shading**: Green Take Profit zone (+1R) and Red Stop Loss zone (-1R).

3. **Lightbox Modal**:
   * Click any chart in the gallery to open a full-screen, high-res image modal for pixel-perfect inspection.

---

## System Architecture & Directory Tree

```
backtest_system/
├── core/
│   ├── data_loader.py       # Downloads & reconstructs 15Y 1D, 4H, and 30M multi-timeframe bars
│   ├── news_filter.py       # Avoids high-impact news days (NFP, CPI, FOMC, GDP)
│   ├── patterns.py          # Candlestick pattern detector (Hammers, Engulfing, Soldiers, etc.)
│   ├── visualizer.py        # 16:9 180-DPI chart renderer with 3-tap & retest annotations
│   └── strategy_engine.py   # Multi-timeframe Breakout & Retest simulation engine
│
├── data/                    # Cached historical datasets (SPY & QQQ 1D, 4H, 30M)
├── reports/
│   ├── 15_Year_Macro_Backtest_Report.docx  # Formal Word audit document with styled tables
│   ├── 15_Year_Macro_Backtest_Report.md    # Complete Markdown audit report
│   ├── trades_15y_log.csv                  # Complete 647-trade CSV log
│   └── analytics_15y.json                  # Machine-readable analytics dataset
│
├── screenshots/             # 60+ enlarged high-resolution trade charts (.png)
├── ui/
│   └── index.html           # Interactive dashboard with 560px split equity curve & gallery
├── README.md                # System documentation (this file)
└── run_15y_backtest.py      # Main end-to-end execution script
```

---

## How to Run & Inspect

### 1. Re-Run the Backtest Suite
To re-run the entire 15-year simulation from scratch:
```powershell
python C:\Users\zakiy\backtest_system\run_15y_backtest.py
```

### 2. Open the Dashboard UI
To open the interactive dashboard in your browser:
```powershell
Start-Process "C:\Users\zakiy\backtest_system\ui\index.html"
```

### 3. Open the Formal Word Report
```powershell
Start-Process "C:\Users\zakiy\backtest_system\reports\15_Year_Macro_Backtest_Report.docx"
```
