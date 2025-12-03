import streamlit as st
import pandas as pd
import numpy as np
import altair as alt

# =========================================================
# PAGE CONFIG
# =========================================================
st.set_page_config(
    page_title="WAVES Intelligence™ — Institutional Wave Console",
    layout="wide",
)

# =========================================================
# THEME / STYLING
# =========================================================
DARK_BG = "#020617"   # almost black
CARD_BG = "#020818"
TEXT_MAIN = "#E5E7EB"
TEXT_MUTED = "#9CA3AF"
ACCENT = "#22C55E"
ACCENT_SOFT = "#38BDF8"
BORDER = "#1F2937"

CUSTOM_CSS = f"""
<style>
    .stApp {{
        background-color: {DARK_BG} !important;
    }}
    .block-container {{
        padding-top: 1.5rem;
        padding-bottom: 2rem;
    }}
    h1, h2, h3, h4, h5, h6, p, span, label {{
        color: {TEXT_MAIN} !important;
        font-family: system-ui, -apple-system, BlinkMacSystemFont, "SF Pro Text", sans-serif;
    }}
    .metric-card {{
        background: radial-gradient(circle at top left, #0F172A, #020617);
        border-radius: 14px;
        padding: 1rem 1.25rem;
        border: 1px solid {BORDER};
        box-shadow: 0 18px 40px rgba(0,0,0,0.60);
    }}
    .metric-label {{
        font-size: 0.72rem;
        letter-spacing: .16em;
        text-transform: uppercase;
        color: {TEXT_MUTED};
    }}
    .metric-value {{
        font-size: 1.6rem;
        font-weight: 600;
        margin-top: 2px;
    }}
    .metric-sub {{
        font-size: 0.72rem;
        color: {TEXT_MUTED};
    }}
    .section-card {{
        background: {CARD_BG};
        border-radius: 14px;
        padding: 1rem 1.25rem 1.1rem 1.25rem;
        border: 1px solid {BORDER};
    }}
    .section-title {{
        font-size: 0.95rem;
        font-weight: 600;
        margin-bottom: 0.3rem;
    }}
    .section-caption {{
        font-size: 0.75rem;
        color: {TEXT_MUTED};
        margin-bottom: 0.6rem;
    }}
    .sidebar-title {{
        font-size: 0.9rem;
        font-weight: 600;
        margin-bottom: 0.3rem;
    }}
</style>
"""
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

# =========================================================
# WAVE DEFINITIONS (15 WAVES)
# =========================================================
WAVES = {
    "sp500": {
        "label": "S&P 500 Wave (LIVE Demo)",
        "benchmark": "S&P 500 Index",
        "csv_hint": "SP500_PORTFOLIO_FINAL.csv export",
        "wave_type": "AI-Managed Wave",
    },
    "us_growth": {
        "label": "US Growth Wave",
        "benchmark": "Russell 1000 Growth",
        "csv_hint": "US_GROWTH_WAVE.csv",
        "wave_type": "AI-Managed Wave",
    },
    "us_value": {
        "label": "US Value Wave",
        "benchmark": "Russell 1000 Value",
        "csv_hint": "US_VALUE_WAVE.csv",
        "wave_type": "AI-Managed Wave",
    },
    "smcap_growth": {
        "label": "Small Cap Growth Wave",
        "benchmark": "Russell 2000 Growth",
        "csv_hint": "SMALL_CAP_GROWTH_WAVE.csv",
        "wave_type": "AI-Managed Wave",
    },
    "sm_mid_growth": {
        "label": "Small-Mid Cap Growth Wave",
        "benchmark": "SMID Growth Composite",
        "csv_hint": "SMID_GROWTH_WAVE.csv",
        "wave_type": "AI-Managed Wave",
    },
    "income": {
        "label": "Equity Income Wave",
        "benchmark": "US Dividend Composite",
        "csv_hint": "EQUITY_INCOME_WAVE.csv",
        "wave_type": "Income Wave",
    },
    "future_power": {
        "label": "Future Power & Energy Wave",
        "benchmark": "Clean Energy / Infrastructure",
        "csv_hint": "FUTURE_POWER_WAVE.csv",
        "wave_type": "Thematic Wave",
    },
    "tech_leaders": {
        "label": "Tech Leaders Wave",
        "benchmark": "NASDAQ 100",
        "csv_hint": "TECH_LEADERS_WAVE.csv",
        "wave_type": "AI-Managed Wave",
    },
    "ai_wave": {
        "label": "AI & Automation Wave",
        "benchmark": "AI / Robotics Composite",
        "csv_hint": "AI_WAVE.csv",
        "wave_type": "Thematic Wave",
    },
    "quality_core": {
        "label": "Quality Core Wave",
        "benchmark": "Global Quality Composite",
        "csv_hint": "QUALITY_CORE_WAVE.csv",
        "wave_type": "Core Wave",
    },
    "diversified_us": {
        "label": "US Core Equity Wave",
        "benchmark": "Total US Market",
        "